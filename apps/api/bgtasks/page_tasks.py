from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from pages.models import Page, PageVersion, PageActivity


@shared_task
def create_version_snapshot(page_id: str, user_id: str, change_summary: str = "Auto-save"):
    """
    Create automatic version snapshot for a page
    """
    try:
        page = Page.objects.get(id=page_id)

        # Check if content changed since last version
        latest_version = PageVersion.objects.filter(page=page).order_by('-version_number').first()

        if latest_version and latest_version.content == page.content:
            return {'status': 'skipped', 'reason': 'No changes detected'}

        # Create new version
        next_version = latest_version.version_number + 1 if latest_version else 1

        PageVersion.objects.create(
            page=page,
            version_number=next_version,
            name=page.name,
            content=page.content,
            content_html=page.content_html,
            created_by_id=user_id,
            change_summary=change_summary
        )

        return {'status': 'success', 'version': next_version}

    except Page.DoesNotExist:
        return {'status': 'error', 'reason': 'Page not found'}


@shared_task
def create_version_snapshots():
    """
    Periodic task to create version snapshots for all recently edited pages
    """
    one_hour_ago = timezone.now() - timedelta(hours=1)

    # Get pages edited in last hour
    pages = Page.objects.filter(
        updated_at__gte=one_hour_ago,
        deleted_at__isnull=True
    ).values_list('id', 'updated_by_id')

    results = []
    for page_id, user_id in pages:
        result = create_version_snapshot.delay(str(page_id), str(user_id), "Auto-save (hourly)")
        results.append(result)

    return {'task': 'create_version_snapshots', 'pages_processed': len(results)}


@shared_task
def cleanup_old_versions():
    """
    Cleanup old versions keeping only last 50 per page
    """
    pages = Page.objects.all()
    deleted_count = 0

    for page in pages:
        versions = PageVersion.objects.filter(page=page).order_by('-version_number')

        if versions.count() > 50:
            # Keep last 50, delete rest
            versions_to_delete = versions[50:]
            count = versions_to_delete.delete()[0]
            deleted_count += count

    return {'task': 'cleanup_old_versions', 'deleted': deleted_count}


@shared_task
def send_page_notification(page_id: str, actor_id: str, verb: str):
    """
    Send notifications for page activities
    """
    try:
        page = Page.objects.select_related('created_by', 'workspace').get(id=page_id)
        actor = page.workspace.members.get(id=actor_id)

        # Get all workspace members except actor
        members = page.workspace.members.exclude(id=actor_id)

        # Create notification logic here
        # (In production, you'd use a notification service or email)

        return {
            'status': 'success',
            'page': page.name,
            'verb': verb,
            'notified': members.count()
        }

    except Exception as e:
        return {'status': 'error', 'reason': str(e)}