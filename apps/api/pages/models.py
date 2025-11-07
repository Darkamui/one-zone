import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex

User = get_user_model()

class Page(models.Model):
    """
    Main feature: Collaborative notes/documentation
    """
    ACCESS_CHOICES = [
        (0, 'Private'),
        (1, 'Project'),
        (2, 'Workspace'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey('workspaces.Workspace', on_delete=models.CASCADE, related_name='pages')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, null=True, blank=True, related_name='pages')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    # Content
    name = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    description_html = models.TextField(blank=True)
    description_stripped = models.TextField(blank=True)

    # TipTap editor content
    content = models.JSONField(default=dict)
    content_html = models.TextField(blank=True)

    # Metadata
    emoji = models.CharField(max_length=10, blank=True)
    icon_prop = models.JSONField(null=True, blank=True)
    cover_image = models.URLField(blank=True, null=True)

    # Access control
    access = models.IntegerField(choices=ACCESS_CHOICES, default=1)

    # Locking (for collaborative editing)
    is_locked = models.BooleanField(default=False)
    locked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='locked_pages')
    locked_at = models.DateTimeField(null=True, blank=True)

    # Organization
    is_favorite = models.BooleanField(default=False)
    sort_order = models.FloatField(default=65535)

    # Publishing
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    public_slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)

    # Metrics
    view_count = models.IntegerField(default=0)

    # Soft delete
    archived_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_pages')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_pages')

    # Full-text search
    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:
        db_table = 'pages'
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['workspace', 'project', 'deleted_at']),
            models.Index(fields=['parent', 'sort_order']),
            models.Index(fields=['is_published', 'public_slug']),
            GinIndex(fields=['search_vector']),
        ]

    def __str__(self):
        return self.name

    @property
    def comment_count(self):
        return self.comments.count()

    @property
    def reaction_count(self):
        return self.reactions.count()

class PageVersion(models.Model):
    """
    Version history for pages
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()

    # Snapshot of content
    name = models.CharField(max_length=500)
    content = models.JSONField(default=dict)
    content_html = models.TextField(blank=True)

    change_summary = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='page_versions')

    class Meta:
        db_table = 'page_versions'
        ordering = ['-version_number']
        unique_together = ['page', 'version_number']
        indexes = [
            models.Index(fields=['page', '-version_number']),
        ]

class PageComment(models.Model):
    """
    Comments on pages
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey('workspaces.Workspace', on_delete=models.CASCADE)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, null=True, blank=True)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='page_comments')

    # Comment content (TipTap JSON for rich text)
    comment = models.JSONField(default=dict)
    comment_html = models.TextField(blank=True)
    comment_stripped = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'page_comments'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['page', 'created_at']),
        ]

class PageReaction(models.Model):
    """
    Reactions on pages or comments
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey('workspaces.Workspace', on_delete=models.CASCADE)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, null=True, blank=True, related_name='reactions')
    comment = models.ForeignKey(PageComment, on_delete=models.CASCADE, null=True, blank=True, related_name='reactions')

    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='page_reactions')
    reaction = models.CharField(max_length=20)  # Emoji

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'page_reactions'
        indexes = [
            models.Index(fields=['page', 'actor']),
            models.Index(fields=['comment', 'actor']),
        ]

class PageActivity(models.Model):
    """
    Activity log for pages
    """
    VERB_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
        ('published', 'Published'),
        ('archived', 'Archived'),
        ('commented', 'Commented'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey('workspaces.Workspace', on_delete=models.CASCADE)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, null=True, blank=True)
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='activities')
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='page_activities')

    verb = models.CharField(max_length=20, choices=VERB_CHOICES)
    field = models.CharField(max_length=255, blank=True)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'page_activities'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['page', '-created_at']),
        ]