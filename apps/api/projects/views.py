from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from projects.models import Project, ProjectMember
from projects.serializers import (
    ProjectSerializer,
    ProjectLiteSerializer,
    ProjectMemberSerializer
)
from workspaces.models import Workspace


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Project CRUD operations
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return projects where user has access"""
        user = self.request.user
        workspace_slug = self.kwargs.get('workspace_slug')

        if workspace_slug:
            return Project.objects.filter(
                workspace__slug=workspace_slug,
                workspace__members__member=user,
                workspace__members__is_active=True,
                archived_at__isnull=True
            ).distinct()

        return Project.objects.filter(
            workspace__members__member=user,
            workspace__members__is_active=True,
            archived_at__isnull=True
        ).distinct()

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return ProjectLiteSerializer
        return ProjectSerializer

    def perform_create(self, serializer):
        """Set workspace and creator when creating project"""
        workspace_slug = self.kwargs.get('workspace_slug')
        workspace = get_object_or_404(Workspace, slug=workspace_slug)

        project = serializer.save(
            workspace=workspace,
            created_by=self.request.user
        )

        # Automatically add creator as project member with Admin role
        ProjectMember.objects.create(
            project=project,
            member=self.request.user,
            role=20  # Admin role
        )

    def perform_destroy(self, instance):
        """Soft delete using archived_at"""
        from django.utils import timezone
        instance.archived_at = timezone.now()
        instance.save(update_fields=['archived_at'])

    @action(detail=True, methods=['get'])
    def members(self, request, workspace_slug=None, pk=None):
        """List all members of a project"""
        project = self.get_object()
        members = project.members.all()
        serializer = ProjectMemberSerializer(members, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_member(self, request, workspace_slug=None, pk=None):
        """Add a member to project"""
        project = self.get_object()
        serializer = ProjectMemberSerializer(data={
            **request.data,
            'project': project.id
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='members/(?P<member_id>[^/.]+)')
    def update_member(self, request, workspace_slug=None, pk=None, member_id=None):
        """Update a project member's role"""
        project = self.get_object()
        member = get_object_or_404(ProjectMember, project=project, id=member_id)
        serializer = ProjectMemberSerializer(member, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['delete'], url_path='members/(?P<member_id>[^/.]+)')
    def remove_member(self, request, workspace_slug=None, pk=None, member_id=None):
        """Remove a member from project"""
        project = self.get_object()
        member = get_object_or_404(ProjectMember, project=project, id=member_id)
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def archive(self, request, workspace_slug=None, pk=None):
        """Archive a project"""
        from django.utils import timezone
        project = self.get_object()
        project.archived_at = timezone.now()
        project.save()
        return Response({'message': 'Project archived successfully'})

    @action(detail=True, methods=['post'])
    def restore(self, request, workspace_slug=None, pk=None):
        """Restore an archived project"""
        project = self.get_object()
        project.archived_at = None
        project.save()
        return Response({'message': 'Project restored successfully'})


class ProjectMemberViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for ProjectMember read operations
    """
    serializer_class = ProjectMemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return project members for projects user has access to"""
        user = self.request.user
        return ProjectMember.objects.filter(
            project__workspace__members__member=user,
            project__workspace__members__is_active=True
        ).distinct()
