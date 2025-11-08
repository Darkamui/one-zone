from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, F
from django.utils import timezone
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

from pages.models import Page, PageVersion, PageComment, PageReaction, PageActivity, PageFavorite
from pages.serializers import (
    PageSerializer, PageLiteSerializer, PageVersionSerializer,
    PageCommentSerializer, PageReactionSerializer, PageActivitySerializer
)
from onezone_api.permissions import WorkspaceEntityPermission
from onezone_api.utils.paginator import CustomPaginator


class PageViewSet(viewsets.ModelViewSet):
    """
    Complete CRUD operations for Pages

    Endpoints:
    - GET /api/v1/workspaces/{workspace_slug}/pages/ - List all pages
    - POST /api/v1/workspaces/{workspace_slug}/pages/ - Create page
    - GET /api/v1/workspaces/{workspace_slug}/pages/{page_id}/ - Get page detail
    - PATCH /api/v1/workspaces/{workspace_slug}/pages/{page_id}/ - Update page
    - DELETE /api/v1/workspaces/{workspace_slug}/pages/{page_id}/ - Delete page

    Custom actions:
    - POST /{page_id}/lock/ - Lock page for editing
    - POST /{page_id}/unlock/ - Unlock page
    - POST /{page_id}/publish/ - Publish page publicly
    - POST /{page_id}/unpublish/ - Unpublish page
    - POST /{page_id}/favorite/ - Add to favorites
    - DELETE /{page_id}/favorite/ - Remove from favorites
    - POST /{page_id}/archive/ - Archive page
    - POST /{page_id}/restore/ - Restore archived page
    - GET /{page_id}/versions/ - Get version history
    - POST /{page_id}/versions/{version_id}/restore/ - Restore version
    """

    permission_classes = [IsAuthenticated, WorkspaceEntityPermission]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description_stripped']
    ordering_fields = ['name', 'created_at', 'updated_at', 'view_count']
    ordering = ['-created_at']

    def get_queryset(self):
        workspace_slug = self.kwargs.get('workspace_slug')
        project_id = self.request.query_params.get('project_id')

        queryset = Page.objects.filter(
            workspace__slug=workspace_slug,
            deleted_at__isnull=True
        ).select_related(
            'created_by', 'updated_by', 'locked_by'
        ).prefetch_related('favorites')

        # Filter by project
        if project_id:
            queryset = queryset.filter(project_id=project_id)

        # Filter by access level based on user permissions
        user = self.request.user
        queryset = queryset.filter(
            Q(created_by=user) |  # User's own pages
            Q(access=2) |  # Workspace-level pages
            Q(access=1, project__members__member=user)  # Project pages where user is member
        ).distinct()

        # Filter archived
        archived = self.request.query_params.get('archived')
        if archived == 'true':
            queryset = queryset.filter(archived_at__isnull=False)
        else:
            queryset = queryset.filter(archived_at__isnull=True)

        # Filter favorites
        favorites = self.request.query_params.get('favorites')
        if favorites == 'true':
            queryset = queryset.filter(favorites__user=user)

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return PageLiteSerializer
        return PageSerializer

    def perform_create(self, serializer):
        from workspaces.models import Workspace
        workspace_slug = self.kwargs.get('workspace_slug')
        workspace = Workspace.objects.get(slug=workspace_slug)

        serializer.save(
            workspace=workspace,
            created_by=self.request.user,
            updated_by=self.request.user
        )

        # Create initial version
        page = serializer.instance
        PageVersion.objects.create(
            page=page,
            version_number=1,
            name=page.name,
            content=page.content,
            content_html=page.content_html,
            created_by=self.request.user,
            change_summary="Initial version"
        )

        # Log activity
        PageActivity.objects.create(
            workspace=page.workspace,
            project=page.project,
            page=page,
            actor=self.request.user,
            verb='created'
        )

    def perform_update(self, serializer):
        page = self.get_object()
        old_name = page.name
        old_content = page.content

        serializer.save(updated_by=self.request.user)

        # Create version snapshot if content changed
        if serializer.validated_data.get('content') != old_content:
            latest_version = PageVersion.objects.filter(page=page).order_by('-version_number').first()
            next_version = latest_version.version_number + 1 if latest_version else 1

            PageVersion.objects.create(
                page=page,
                version_number=next_version,
                name=page.name,
                content=page.content,
                content_html=page.content_html,
                created_by=self.request.user,
                change_summary=f"Updated by {self.request.user.display_name}"
            )

        # Log activity
        PageActivity.objects.create(
            workspace=page.workspace,
            project=page.project,
            page=page,
            actor=self.request.user,
            verb='updated',
            field='name' if old_name != page.name else 'content'
        )

    def perform_destroy(self, instance):
        """Soft delete"""
        instance.deleted_at = timezone.now()
        instance.save(update_fields=['deleted_at'])

        # Log activity
        PageActivity.objects.create(
            workspace=instance.workspace,
            project=instance.project,
            page=instance,
            actor=self.request.user,
            verb='deleted'
        )

    @action(detail=True, methods=['post'])
    def lock(self, request, workspace_slug=None, pk=None):
        """Lock page for editing"""
        page = self.get_object()

        if page.is_locked and page.locked_by != request.user:
            return Response(
                {'error': f'Page is locked by {page.locked_by.display_name}'},
                status=status.HTTP_409_CONFLICT
            )

        page.is_locked = True
        page.locked_by = request.user
        page.locked_at = timezone.now()
        page.save(update_fields=['is_locked', 'locked_by', 'locked_at'])

        serializer = self.get_serializer(page)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def unlock(self, request, workspace_slug=None, pk=None):
        """Unlock page"""
        page = self.get_object()

        if page.is_locked and page.locked_by != request.user:
            return Response(
                {'error': 'You cannot unlock a page locked by another user'},
                status=status.HTTP_403_FORBIDDEN
            )

        page.is_locked = False
        page.locked_by = None
        page.locked_at = None
        page.save(update_fields=['is_locked', 'locked_by', 'locked_at'])

        serializer = self.get_serializer(page)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def publish(self, request, workspace_slug=None, pk=None):
        """Publish page publicly"""
        page = self.get_object()
        public_slug = request.data.get('public_slug')

        if not public_slug:
            return Response(
                {'error': 'public_slug is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check slug uniqueness
        if Page.objects.filter(public_slug=public_slug).exclude(id=page.id).exists():
            return Response(
                {'error': 'This slug is already taken'},
                status=status.HTTP_400_BAD_REQUEST
            )

        page.is_published = True
        page.published_at = timezone.now()
        page.public_slug = public_slug
        page.save(update_fields=['is_published', 'published_at', 'public_slug'])

        # Log activity
        PageActivity.objects.create(
            workspace=page.workspace,
            project=page.project,
            page=page,
            actor=request.user,
            verb='published'
        )

        serializer = self.get_serializer(page)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def unpublish(self, request, workspace_slug=None, pk=None):
        """Unpublish page"""
        page = self.get_object()

        page.is_published = False
        page.save(update_fields=['is_published'])

        serializer = self.get_serializer(page)
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, workspace_slug=None, pk=None):
        """Add/remove page from favorites"""
        page = self.get_object()

        if request.method == 'POST':
            page.favorites.get_or_create(user=request.user)
            favorited = True
        else:  # DELETE
            page.favorites.filter(user=request.user).delete()
            favorited = False

        return Response({'favorited': favorited})

    @action(detail=True, methods=['post'])
    def archive(self, request, workspace_slug=None, pk=None):
        """Archive page"""
        page = self.get_object()

        page.archived_at = timezone.now()
        page.save(update_fields=['archived_at'])

        # Log activity
        PageActivity.objects.create(
            workspace=page.workspace,
            project=page.project,
            page=page,
            actor=request.user,
            verb='archived'
        )

        serializer = self.get_serializer(page)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def restore(self, request, workspace_slug=None, pk=None):
        """Restore archived page"""
        page = self.get_object()

        page.archived_at = None
        page.save(update_fields=['archived_at'])

        serializer = self.get_serializer(page)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def versions(self, request, workspace_slug=None, pk=None):
        """Get version history"""
        page = self.get_object()
        versions = PageVersion.objects.filter(page=page).order_by('-version_number')

        paginator = CustomPaginator()
        paginated_versions = paginator.paginate_queryset(versions, request)

        serializer = PageVersionSerializer(paginated_versions, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'], url_path='versions/(?P<version_id>[^/.]+)/restore')
    def restore_version(self, request, workspace_slug=None, pk=None, version_id=None):
        """Restore a previous version"""
        page = self.get_object()
        version = PageVersion.objects.get(id=version_id, page=page)

        # Create new version from current state first
        latest_version = PageVersion.objects.filter(page=page).order_by('-version_number').first()
        next_version = latest_version.version_number + 1

        PageVersion.objects.create(
            page=page,
            version_number=next_version,
            name=page.name,
            content=page.content,
            content_html=page.content_html,
            created_by=request.user,
            change_summary=f"Before restoring version {version.version_number}"
        )

        # Restore the version
        page.name = version.name
        page.content = version.content
        page.content_html = version.content_html
        page.updated_by = request.user
        page.save()

        # Create new version for the restore
        PageVersion.objects.create(
            page=page,
            version_number=next_version + 1,
            name=page.name,
            content=page.content,
            content_html=page.content_html,
            created_by=request.user,
            change_summary=f"Restored version {version.version_number}"
        )

        serializer = self.get_serializer(page)
        return Response(serializer.data)


class PageCommentViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for page comments
    """
    serializer_class = PageCommentSerializer
    permission_classes = [IsAuthenticated, WorkspaceEntityPermission]

    def get_queryset(self):
        workspace_slug = self.kwargs.get('workspace_slug')
        page_id = self.kwargs.get('page_id')

        return PageComment.objects.filter(
            workspace__slug=workspace_slug,
            page_id=page_id
        ).select_related('created_by').order_by('created_at')

    def perform_create(self, serializer):
        page_id = self.kwargs.get('page_id')
        page = Page.objects.get(id=page_id)

        serializer.save(
            page=page,
            workspace=page.workspace,
            created_by=self.request.user
        )

        # Increment comment count
        page.comment_count = F('comment_count') + 1
        page.save(update_fields=['comment_count'])

        # Log activity
        PageActivity.objects.create(
            workspace=page.workspace,
            project=page.project,
            page=page,
            actor=self.request.user,
            verb='commented'
        )


class PageReactionViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for page reactions
    """
    serializer_class = PageReactionSerializer
    permission_classes = [IsAuthenticated, WorkspaceEntityPermission]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        workspace_slug = self.kwargs.get('workspace_slug')
        page_id = self.kwargs.get('page_id')

        return PageReaction.objects.filter(
            workspace__slug=workspace_slug,
            page_id=page_id
        ).select_related('actor')

    def perform_create(self, serializer):
        page_id = self.kwargs.get('page_id')
        page = Page.objects.get(id=page_id)

        # Remove existing reaction if any
        PageReaction.objects.filter(
            page=page,
            actor=self.request.user
        ).delete()

        serializer.save(
            page=page,
            workspace=page.workspace,
            actor=self.request.user
        )

        # Update reaction count
        page.reaction_count = page.reactions.count()
        page.save(update_fields=['reaction_count'])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_pages(request, workspace_slug):
    """
    Full-text search for pages

    GET /api/v1/workspaces/{workspace_slug}/search/?q=search+term
    """
    query = request.query_params.get('q', '').strip()

    if not query:
        return Response({'results': []})

    # Get accessible pages for user
    user = request.user
    pages = Page.objects.filter(
        workspace__slug=workspace_slug,
        deleted_at__isnull=True,
        archived_at__isnull=True
    ).filter(
        Q(created_by=user) |
        Q(access=2) |
        Q(access=1, project__members__member=user)
    ).distinct()

    # Full-text search
    search_query = SearchQuery(query)
    search_vector = SearchVector('name', weight='A') + SearchVector('description_stripped', weight='B')

    results = pages.annotate(
        rank=SearchRank(search_vector, search_query)
    ).filter(
        rank__gte=0.01
    ).order_by('-rank')[:20]

    serializer = PageLiteSerializer(results, many=True, context={'request': request})
    return Response({'results': serializer.data, 'count': results.count()})