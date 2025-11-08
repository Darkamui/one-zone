from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from workspaces.models import Workspace, WorkspaceMember
from projects.models import Project

User = get_user_model()


class ProjectAPITestCase(TestCase):
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

        # Create workspace for user1
        self.workspace = Workspace.objects.create(
            name='Test Workspace',
            slug='test-workspace',
            owner=self.user1
        )
        WorkspaceMember.objects.create(
            workspace=self.workspace,
            member=self.user1,
            role=20
        )

    def test_create_project(self):
        """Test creating a new project within workspace"""
        self.client.force_authenticate(user=self.user1)

        url = f'/api/v1/workspaces/{self.workspace.slug}/projects/'
        data = {
            'name': 'Test Project',
            'identifier': 'TEST',
            'description': 'A test project'
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Test Project')
        self.assertEqual(response.data['identifier'], 'TEST')
        self.assertTrue(Project.objects.filter(identifier='TEST').exists())

    def test_list_projects(self):
        """Test listing projects in workspace"""
        # Create project
        Project.objects.create(
            workspace=self.workspace,
            name='Project 1',
            identifier='PROJ1',
            created_by=self.user1
        )

        self.client.force_authenticate(user=self.user1)
        url = f'/api/v1/workspaces/{self.workspace.slug}/projects/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_update_project(self):
        """Test updating a project"""
        project = Project.objects.create(
            workspace=self.workspace,
            name='Original Name',
            identifier='ORIG',
            created_by=self.user1
        )

        self.client.force_authenticate(user=self.user1)
        url = f'/api/v1/workspaces/{self.workspace.slug}/projects/{project.id}/'
        data = {'name': 'Updated Name'}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Name')

    def test_project_access_control(self):
        """Test users not in workspace cannot access projects"""
        project = Project.objects.create(
            workspace=self.workspace,
            name='Test Project',
            identifier='TEST',
            created_by=self.user1
        )

        # User2 tries to access project (not a workspace member)
        self.client.force_authenticate(user=self.user2)
        url = f'/api/v1/workspaces/{self.workspace.slug}/projects/{project.id}/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_project(self):
        """Test deleting a project (soft delete via archived_at)"""
        project = Project.objects.create(
            workspace=self.workspace,
            name='To Delete',
            identifier='DEL',
            created_by=self.user1
        )

        self.client.force_authenticate(user=self.user1)
        url = f'/api/v1/workspaces/{self.workspace.slug}/projects/{project.id}/'
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        project.refresh_from_db()
        self.assertIsNotNone(project.archived_at)
