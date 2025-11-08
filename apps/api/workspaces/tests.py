from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from workspaces.models import Workspace, WorkspaceMember

User = get_user_model()


class WorkspaceAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create test users
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            username='user2',
            password='testpass123'
        )

    def test_create_workspace(self):
        """Test creating a new workspace"""
        self.client.force_authenticate(user=self.user1)

        url = '/api/v1/workspaces/'
        data = {
            'name': 'Test Workspace',
            'slug': 'test-workspace'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Test Workspace')
        self.assertTrue(Workspace.objects.filter(slug='test-workspace').exists())

        # Verify owner membership was created
        workspace = Workspace.objects.get(slug='test-workspace')
        self.assertTrue(
            WorkspaceMember.objects.filter(
                workspace=workspace,
                member=self.user1,
                role=20  # Owner role
            ).exists()
        )

    def test_list_workspaces(self):
        """Test listing workspaces shows only user's workspaces"""
        # Create workspace for user1
        workspace1 = Workspace.objects.create(
            name='User1 Workspace',
            slug='user1-workspace',
            owner=self.user1
        )
        WorkspaceMember.objects.create(
            workspace=workspace1,
            member=self.user1,
            role=20
        )

        # Create workspace for user2
        workspace2 = Workspace.objects.create(
            name='User2 Workspace',
            slug='user2-workspace',
            owner=self.user2
        )
        WorkspaceMember.objects.create(
            workspace=workspace2,
            member=self.user2,
            role=20
        )

        # User1 should only see their workspace
        self.client.force_authenticate(user=self.user1)
        url = '/api/v1/workspaces/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['slug'], 'user1-workspace')

    def test_workspace_access_control(self):
        """Test users cannot access workspaces they're not members of"""
        # Create workspace for user1
        workspace = Workspace.objects.create(
            name='User1 Workspace',
            slug='user1-workspace',
            owner=self.user1
        )
        WorkspaceMember.objects.create(
            workspace=workspace,
            member=self.user1,
            role=20
        )

        # User2 tries to access user1's workspace
        self.client.force_authenticate(user=self.user2)
        url = f'/api/v1/workspaces/{workspace.slug}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_workspace(self):
        """Test updating workspace"""
        workspace = Workspace.objects.create(
            name='Original Name',
            slug='test-workspace',
            owner=self.user1
        )
        WorkspaceMember.objects.create(
            workspace=workspace,
            member=self.user1,
            role=20
        )

        self.client.force_authenticate(user=self.user1)
        url = f'/api/v1/workspaces/{workspace.slug}/'
        data = {'name': 'Updated Name'}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Name')

    def test_unauthenticated_access(self):
        """Test unauthenticated users cannot access workspaces"""
        url = '/api/v1/workspaces/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
