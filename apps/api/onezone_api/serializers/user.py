from rest_framework import serializers
from plane.db.models import User


class UserLiteSerializer(serializers.ModelSerializer):
    """
    Lightweight user serializer for nested relationships
    """
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'avatar', 'display_name', 'is_active'
        ]
        read_only_fields = fields


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Full user profile serializer
    """
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'avatar', 'cover_image', 'display_name', 'bio',
            'timezone', 'date_joined', 'last_login', 'is_active'
        ]
        read_only_fields = ['id', 'email', 'date_joined', 'last_login']