from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token

from django.contrib.auth import get_user_model
from users.serializers import UserDetailSerializer

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def sign_in(request):
    """
    Session-based authentication login

    POST /api/v1/auth/sign-in/
    Body: { "email": "user@example.com", "password": "password" }
    """
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {'error': 'Email and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(request, username=email, password=password)

    if user is None:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        return Response(
            {'error': 'Account is disabled'},
            status=status.HTTP_403_FORBIDDEN
        )

    login(request, user)

    serializer = UserDetailSerializer(user)
    return Response({
        'user': serializer.data,
        'message': 'Signed in successfully'
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def sign_up(request):
    """
    User registration

    POST /api/v1/auth/sign-up/
    Body: { "email": "user@example.com", "username": "username", "password": "password" }
    """
    email = request.data.get('email')
    username = request.data.get('username')
    password = request.data.get('password')

    if not all([email, username, password]):
        return Response(
            {'error': 'Email, username, and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {'error': 'User with this email already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username is already taken'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create_user(
        email=email,
        username=username,
        password=password
    )

    login(request, user)

    serializer = UserDetailSerializer(user)
    return Response({
        'user': serializer.data,
        'message': 'Account created successfully'
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sign_out(request):
    """
    Logout user

    POST /api/v1/auth/sign-out/
    """
    logout(request)
    return Response({'message': 'Signed out successfully'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    """
    Get current user profile

    GET /api/v1/auth/profile/
    """
    serializer = UserDetailSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def csrf_token(request):
    """
    Get CSRF token for session-based auth

    GET /api/v1/auth/csrf/
    """
    return Response({'csrfToken': get_token(request)})