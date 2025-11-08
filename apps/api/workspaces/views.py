from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import models

from workspaces.models import Workspace, WorkspaceMember
from workspaces.serializers import (
    WorkspaceSerializer,
    WorkspaceLiteSerializer,
    WorkspaceMemberSerializer
)


class WorkspaceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Workspace CRUD operations
    """
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'

    def get_queryset(self):
        """Return workspaces where user is a member or owner"""
        user = self.request.user
        return Workspace.objects.filter(
            models.Q(owner=user) | models.Q(members__member=user, members__is_active=True)
        ).distinct()

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return WorkspaceLiteSerializer
        return WorkspaceSerializer

    def perform_create(self, serializer):
        """Set owner when creating workspace"""
        workspace = serializer.save(owner=self.request.user)
        # Automatically add owner as workspace member with Owner role
        WorkspaceMember.objects.create(
            workspace=workspace,
            member=self.request.user,
            role=20  # Owner role
        )

    @action(detail=True, methods=['get'])
    def members(self, request, slug=None):
        """List all members of a workspace"""
        workspace = self.get_object()
        members = workspace.members.filter(is_active=True)
        serializer = WorkspaceMemberSerializer(members, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_member(self, request, slug=None):
        """Add a member to workspace"""
        workspace = self.get_object()
        serializer = WorkspaceMemberSerializer(data={
            **request.data,
            'workspace': workspace.id
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='members/(?P<member_id>[^/.]+)')
    def update_member(self, request, slug=None, member_id=None):
        """Update a workspace member's role"""
        workspace = self.get_object()
        member = get_object_or_404(WorkspaceMember, workspace=workspace, id=member_id)
        serializer = WorkspaceMemberSerializer(member, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['delete'], url_path='members/(?P<member_id>[^/.]+)')
    def remove_member(self, request, slug=None, member_id=None):
        """Remove a member from workspace"""
        workspace = self.get_object()
        member = get_object_or_404(WorkspaceMember, workspace=workspace, id=member_id)
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WorkspaceMemberViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for WorkspaceMember read operations
    """
    serializer_class = WorkspaceMemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return workspace members for workspaces user belongs to"""
        user = self.request.user
        return WorkspaceMember.objects.filter(
            workspace__owner=user
        ) | WorkspaceMember.objects.filter(
            workspace__members__member=user,
            workspace__members__is_active=True
        )
