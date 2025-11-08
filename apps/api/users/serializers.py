from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


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


class UserSerializer(serializers.ModelSerializer):
    """
    Standard user serializer for user management
    """
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'avatar', 'display_name', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
