import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Project(models.Model):
    NETWORK_CHOICES = [
        (0, 'Private'),
        (1, 'Internal'),
        (2, 'Public'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey('workspaces.Workspace', on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255)
    identifier = models.CharField(max_length=10)  # e.g., "DOCS"
    description = models.TextField(blank=True)
    description_html = models.TextField(blank=True)

    emoji = models.CharField(max_length=10, blank=True)
    icon_prop = models.JSONField(null=True, blank=True)
    cover_image = models.URLField(blank=True, null=True)

    network = models.IntegerField(choices=NETWORK_CHOICES, default=1)
    timezone = models.CharField(max_length=50, default='UTC')

    # Feature toggle (simplified - only pages)
    page_view = models.BooleanField(default=True)

    archived_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')

    class Meta:
        db_table = 'projects'
        unique_together = ['workspace', 'identifier']
        indexes = [
            models.Index(fields=['workspace', 'archived_at']),
        ]

    def __str__(self):
        return f"{self.identifier} - {self.name}"

    @property
    def total_members(self):
        return self.members.count()

    @property
    def total_pages(self):
        return self.pages.filter(deleted_at__isnull=True).count()

class ProjectMember(models.Model):
    ROLE_CHOICES = [
        (20, 'Admin'),
        (10, 'Member'),
        (5, 'Viewer'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_memberships')
    role = models.IntegerField(choices=ROLE_CHOICES, default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'project_members'
        unique_together = ['project', 'member']