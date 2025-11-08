from rest_framework import serializers
from plane.db.models import Page, PageVersion, PageComment, PageReaction, PageActivity
from .user import UserLiteSerializer
from .project import ProjectLiteSerializer


class PageSerializer(serializers.ModelSerializer):
    """
    Full page serializer with all fields
    """
    created_by_detail = UserLiteSerializer(source='created_by', read_only=True)
    updated_by_detail = UserLiteSerializer(source='updated_by', read_only=True)
    locked_by_detail = UserLiteSerializer(source='locked_by', read_only=True)

    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = '__all__'
        read_only_fields = [
            'id', 'workspace', 'created_at', 'updated_at',
            'created_by', 'view_count', 'comment_count', 'reaction_count'
        ]

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorites.filter(user=request.user).exists()
        return False

    def validate_access(self, value):
        """Validate access level"""
        if value not in [0, 1, 2]:
            raise serializers.ValidationError("Access must be 0 (private), 1 (project), or 2 (workspace)")
        return value

    def validate(self, attrs):
        """Cross-field validation"""
        # If access is project-level, project must be set
        if attrs.get('access') == 1 and not attrs.get('project'):
            raise serializers.ValidationError({
                'project': 'Project is required for project-level access'
            })

        # If publishing, validate slug is unique
        if attrs.get('is_published') and not attrs.get('public_slug'):
            raise serializers.ValidationError({
                'public_slug': 'Public slug is required when publishing'
            })

        return attrs


class PageLiteSerializer(serializers.ModelSerializer):
    """
    Lightweight page serializer for lists
    """
    created_by_detail = UserLiteSerializer(source='created_by', read_only=True)
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = [
            'id', 'workspace', 'project', 'parent',
            'name', 'emoji', 'icon_prop', 'access',
            'is_favorite', 'is_locked', 'locked_by_detail',
            'is_published', 'view_count', 'comment_count',
            'sort_order', 'archived_at', 'created_at',
            'updated_at', 'created_by_detail'
        ]

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorites.filter(user=request.user).exists()
        return False


class PageVersionSerializer(serializers.ModelSerializer):
    """
    Page version history serializer
    """
    created_by_detail = UserLiteSerializer(source='created_by', read_only=True)

    class Meta:
        model = PageVersion
        fields = '__all__'
        read_only_fields = ['id', 'page', 'version_number', 'created_at', 'created_by']


class PageCommentSerializer(serializers.ModelSerializer):
    """
    Page comment serializer with nested user and reactions
    """
    created_by_detail = UserLiteSerializer(source='created_by', read_only=True)
    reaction_count = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()

    class Meta:
        model = PageComment
        fields = '__all__'
        read_only_fields = ['id', 'page', 'workspace', 'created_at', 'updated_at', 'created_by']

    def get_reaction_count(self, obj):
        return obj.reactions.count()

    def get_user_reaction(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            reaction = obj.reactions.filter(actor=request.user).first()
            return reaction.reaction if reaction else None
        return None


class PageReactionSerializer(serializers.ModelSerializer):
    """
    Page reaction serializer
    """
    actor_detail = UserLiteSerializer(source='actor', read_only=True)

    class Meta:
        model = PageReaction
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'actor']


class PageActivitySerializer(serializers.ModelSerializer):
    """
    Page activity log serializer
    """
    actor_detail = UserLiteSerializer(source='actor', read_only=True)

    class Meta:
        model = PageActivity
        fields = '__all__'
        read_only_fields = ['id', 'workspace', 'project', 'page', 'actor', 'created_at']