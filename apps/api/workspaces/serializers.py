from rest_framework import serializers
from workspaces.models import Workspace, WorkspaceMember
from users.serializers import UserLiteSerializer


class WorkspaceLiteSerializer(serializers.ModelSerializer):
    """
    Lightweight workspace serializer
    """
    class Meta:
        model = Workspace
        fields = [
            'id', 'name', 'slug', 'logo', 'total_members',
            'total_projects', 'total_pages', 'created_at'
        ]
        read_only_fields = fields


class WorkspaceSerializer(serializers.ModelSerializer):
    """
    Full workspace serializer
    """
    owner_detail = UserLiteSerializer(source='owner', read_only=True)
    total_members = serializers.IntegerField(read_only=True)
    total_projects = serializers.IntegerField(read_only=True)
    total_pages = serializers.IntegerField(read_only=True)

    class Meta:
        model = Workspace
        fields = '__all__'
        read_only_fields = [
            'id', 'owner', 'created_at', 'updated_at',
            'total_members', 'total_projects', 'total_pages'
        ]

    def validate_slug(self, value):
        """Validate slug is unique"""
        if Workspace.objects.filter(slug=value).exists():
            # Allow if updating same workspace
            if self.instance and self.instance.slug == value:
                return value
            raise serializers.ValidationError("Workspace with this slug already exists")
        return value


class WorkspaceMemberSerializer(serializers.ModelSerializer):
    """
    Workspace member serializer
    """
    member_detail = UserLiteSerializer(source='member', read_only=True)

    class Meta:
        model = WorkspaceMember
        fields = '__all__'
        read_only_fields = ['id', 'workspace', 'created_at']

    def validate_role(self, value):
        """Validate role is valid"""
        valid_roles = [role[0] for role in WorkspaceMember.ROLE_CHOICES]
        if value not in valid_roles:
            raise serializers.ValidationError(f"Role must be one of {valid_roles}")
        return value
