from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from workspaces.models import Workspace, WorkspaceMember
from projects.models import Project
from pages.models import Page

User = get_user_model()


class PageAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create test user
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )

        # Create workspace
        self.workspace = Workspace.objects.create(
            name='Test Workspace',
            slug='test-workspace',
            owner=self.user
        )

        # Add user as workspace member
        WorkspaceMember.objects.create(
            workspace=self.workspace,
            member=self.user,
            role=20  # Owner role
        )

        # Create project
        self.project = Project.objects.create(
            workspace=self.workspace,
            name='Test Project',
            identifier='TEST',
            created_by=self.user
        )

        # Login
        self.client.login(email='test@example.com', password='testpass123')

    def test_create_page(self):
        """Test creating a new page"""
        url = f'/api/v1/workspaces/{self.workspace.slug}/pages/'
        data = {
            'name': 'Test Page',
            'content': {'type': 'doc', 'content': []},
            'access': 2
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Test Page')
        self.assertTrue(Page.objects.filter(name='Test Page').exists())

    def test_list_pages(self):
        """Test listing pages"""
        # Create test pages
        Page.objects.create(
            workspace=self.workspace,
            name='Page 1',
            content={},
            access=2,
            created_by=self.user,
            updated_by=self.user
        )

        url = f'/api/v1/workspaces/{self.workspace.slug}/pages/'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_update_page(self):
        """Test updating a page"""
        page = Page.objects.create(
            workspace=self.workspace,
            name='Original Name',
            content={},
            access=2,
            created_by=self.user,
            updated_by=self.user
        )

        url = f'/api/v1/workspaces/{self.workspace.slug}/pages/{page.id}/'
        data = {'name': 'Updated Name'}

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Name')

    def test_delete_page(self):
        """Test deleting a page (soft delete)"""
        page = Page.objects.create(
            workspace=self.workspace,
            name='To Delete',
            content={},
            access=2,
            created_by=self.user,
            updated_by=self.user
        )

        url = f'/api/v1/workspaces/{self.workspace.slug}/pages/{page.id}/'
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        page.refresh_from_db()
        self.assertIsNotNone(page.deleted_at)

    def test_lock_page(self):
        """Test locking a page"""
        page = Page.objects.create(
            workspace=self.workspace,
            name='Lockable Page',
            content={},
            access=2,
            created_by=self.user,
            updated_by=self.user
        )

        url = f'/api/v1/workspaces/{self.workspace.slug}/pages/{page.id}/lock/'
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        page.refresh_from_db()
        self.assertTrue(page.is_locked)
        self.assertEqual(page.locked_by, self.user)


# Run tests:
# python manage.py test pages.tests