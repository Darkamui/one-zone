from rest_framework import serializers
from projects.models import Project, ProjectMember
from users.serializers import UserLiteSerializer


class ProjectLiteSerializer(serializers.ModelSerializer):
    """
    Lightweight project serializer
    """
    is_favorite = serializers.SerializerMethodField()
    total_pages = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'workspace', 'name', 'identifier', 'emoji',
            'icon_prop', 'cover_image', 'is_favorite', 'total_pages',
            'created_at'
        ]

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Check if ProjectFavorite model exists and use it
            # For now, return False as a placeholder
            return False
        return False

    def get_total_pages(self, obj):
        return obj.pages.count()


class ProjectSerializer(serializers.ModelSerializer):
    """
    Full project serializer
    """
    created_by_detail = UserLiteSerializer(source='created_by', read_only=True)
    is_favorite = serializers.SerializerMethodField()
    total_pages = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = [
            'id', 'workspace', 'created_at',
            'updated_at', 'created_by'
        ]

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Check if ProjectFavorite model exists and use it
            # For now, return False as a placeholder
            return False
        return False

    def get_total_pages(self, obj):
        return obj.pages.count()


class ProjectMemberSerializer(serializers.ModelSerializer):
    """
    Project member serializer
    """
    member_detail = UserLiteSerializer(source='member', read_only=True)

    class Meta:
        model = ProjectMember
        fields = '__all__'
        read_only_fields = ['id', 'project', 'created_at']
