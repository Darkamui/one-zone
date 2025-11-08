from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model

from users.serializers import UserSerializer, UserDetailSerializer, UserLiteSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User CRUD operations
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return users"""
        return User.objects.filter(is_active=True)

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'retrieve' or self.action == 'me':
            return UserDetailSerializer
        elif self.action == 'list':
            return UserLiteSerializer
        return UserSerializer

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user profile"""
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """Update current user profile"""
        serializer = UserDetailSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def deactivate(self, request, pk=None):
        """Deactivate a user account"""
        user = self.get_object()
        # Only allow users to deactivate their own account or admins
        if user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only deactivate your own account'},
                status=status.HTTP_403_FORBIDDEN
            )
        user.is_active = False
        user.save()
        return Response({'message': 'User account deactivated'})
