import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Workspace(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_workspaces')
    logo = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workspaces'
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name

    @property
    def total_members(self):
        return self.members.filter(is_active=True).count()

    @property
    def total_projects(self):
        return self.projects.filter(archived_at__isnull=True).count()

    @property
    def total_pages(self):
        return self.pages.filter(deleted_at__isnull=True).count()

class WorkspaceMember(models.Model):
    ROLE_CHOICES = [
        (20, 'Owner'),
        (15, 'Admin'),
        (10, 'Member'),
        (5, 'Guest'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='members')
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workspace_memberships')
    role = models.IntegerField(choices=ROLE_CHOICES, default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'workspace_members'
        unique_together = ['workspace', 'member']
        indexes = [
            models.Index(fields=['workspace', 'member']),
        ]

    def __str__(self):
        return f"{self.member.email} in {self.workspace.name}"