from rest_framework import serializers
from plane.db.models import Project, ProjectMember
from .user import UserLiteSerializer


class ProjectLiteSerializer(serializers.ModelSerializer):
    """
    Lightweight project serializer
    """
    class Meta:
        model = Project
        fields = [
            'id', 'workspace', 'name', 'identifier', 'emoji',
            'icon_prop', 'cover_image', 'is_favorite', 'total_pages',
            'created_at'
        ]


class ProjectSerializer(serializers.ModelSerializer):
    """
    Full project serializer
    """
    created_by_detail = UserLiteSerializer(source='created_by', read_only=True)

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = [
            'id', 'workspace', 'identifier', 'created_at',
            'updated_at', 'created_by', 'total_pages'
        ]


class ProjectMemberSerializer(serializers.ModelSerializer):
    """
    Project member serializer
    """
    member_detail = UserLiteSerializer(source='member', read_only=True)

    class Meta:
        model = ProjectMember
        fields = '__all__'
        read_only_fields = ['id', 'project', 'created_at']