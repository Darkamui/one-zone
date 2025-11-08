from rest_framework import permissions
from workspaces.models import WorkspaceMember


class WorkspaceEntityPermission(permissions.BasePermission):
    """
    Permission class for workspace-based entities (pages, projects, etc.)

    Checks if user is an active member of the workspace that the entity belongs to.
    """

    def has_permission(self, request, view):
        """
        Check if user is authenticated
        """
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Check if user has permission to access the workspace entity

        - For read operations (GET, HEAD, OPTIONS): user must be workspace member
        - For write operations (POST, PUT, PATCH, DELETE): user must be workspace member
        """
        # Get the workspace from the object
        workspace = None
        if hasattr(obj, 'workspace'):
            workspace = obj.workspace
        elif hasattr(obj, 'page') and hasattr(obj.page, 'workspace'):
            workspace = obj.page.workspace
        elif hasattr(obj, 'project') and hasattr(obj.project, 'workspace'):
            workspace = obj.project.workspace

        if not workspace:
            return False

        # Check if user is an active member of the workspace
        is_member = WorkspaceMember.objects.filter(
            workspace=workspace,
            member=request.user,
            is_active=True
        ).exists()

        if not is_member:
            return False

        # For write operations, you might want to check role level
        # For now, any active member can perform operations
        return True


class WorkspaceAdminPermission(permissions.BasePermission):
    """
    Permission class that requires admin or owner role in workspace
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Check if user has admin/owner role in the workspace
        """
        workspace = None
        if hasattr(obj, 'workspace'):
            workspace = obj.workspace
        elif hasattr(obj, 'page') and hasattr(obj.page, 'workspace'):
            workspace = obj.page.workspace
        elif hasattr(obj, 'project') and hasattr(obj.project, 'workspace'):
            workspace = obj.project.workspace

        if not workspace:
            return False

        # Check if user is owner or admin (role >= 15)
        try:
            member = WorkspaceMember.objects.get(
                workspace=workspace,
                member=request.user,
                is_active=True
            )
            return member.role >= 15  # Admin or Owner
        except WorkspaceMember.DoesNotExist:
            return False
