from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter

# Import ViewSets from app folders
from workspaces.views import WorkspaceViewSet, WorkspaceMemberViewSet
from projects.views import ProjectViewSet, ProjectMemberViewSet
from pages.views import PageViewSet, search_pages
from users.views import UserViewSet

# Import authentication views
from authentication.views import sign_in, sign_up, sign_out, profile, csrf_token

# Create main router
router = DefaultRouter()

# Register top-level routes
router.register(r'workspaces', WorkspaceViewSet, basename='workspace')
router.register(r'users', UserViewSet, basename='user')

# Create nested routers for workspace resources
# This requires rest_framework_nested, but for now let's use a simpler approach with explicit paths

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API v1 routes
    path('api/v1/', include(router.urls)),

    # Nested workspace routes for projects
    path('api/v1/workspaces/<str:workspace_slug>/projects/',
         ProjectViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='workspace-projects'),
    path('api/v1/workspaces/<str:workspace_slug>/projects/<uuid:pk>/',
         ProjectViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='workspace-project-detail'),

    # Nested workspace routes for pages - List and Create
    path('api/v1/workspaces/<str:workspace_slug>/pages/',
         PageViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='workspace-pages'),

    # Page detail - Retrieve, Update, Delete
    path('api/v1/workspaces/<str:workspace_slug>/pages/<uuid:pk>/',
         PageViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='workspace-page-detail'),

    # Page custom actions
    path('api/v1/workspaces/<str:workspace_slug>/pages/<uuid:pk>/lock/',
         PageViewSet.as_view({'post': 'lock'}),
         name='page-lock'),
    path('api/v1/workspaces/<str:workspace_slug>/pages/<uuid:pk>/unlock/',
         PageViewSet.as_view({'post': 'unlock'}),
         name='page-unlock'),
    path('api/v1/workspaces/<str:workspace_slug>/pages/<uuid:pk>/publish/',
         PageViewSet.as_view({'post': 'publish'}),
         name='page-publish'),
    path('api/v1/workspaces/<str:workspace_slug>/pages/<uuid:pk>/unpublish/',
         PageViewSet.as_view({'post': 'unpublish'}),
         name='page-unpublish'),
    path('api/v1/workspaces/<str:workspace_slug>/pages/<uuid:pk>/favorite/',
         PageViewSet.as_view({'post': 'favorite', 'delete': 'favorite'}),
         name='page-favorite'),
    path('api/v1/workspaces/<str:workspace_slug>/pages/<uuid:pk>/archive/',
         PageViewSet.as_view({'post': 'archive'}),
         name='page-archive'),
    path('api/v1/workspaces/<str:workspace_slug>/pages/<uuid:pk>/restore/',
         PageViewSet.as_view({'post': 'restore'}),
         name='page-restore'),
    path('api/v1/workspaces/<str:workspace_slug>/pages/<uuid:pk>/versions/',
         PageViewSet.as_view({'get': 'versions'}),
         name='page-versions'),

    # Search endpoint
    path('api/v1/workspaces/<str:workspace_slug>/search/',
         search_pages,
         name='workspace-search'),

    # Authentication endpoints
    path('api/v1/auth/sign-in/', sign_in, name='sign-in'),
    path('api/v1/auth/sign-up/', sign_up, name='sign-up'),
    path('api/v1/auth/sign-out/', sign_out, name='sign-out'),
    path('api/v1/auth/profile/', profile, name='profile'),
    path('api/v1/auth/csrf/', csrf_token, name='csrf-token'),
]
