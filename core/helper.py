from django.utils import timezone
from django.conf import settings
from django.urls import reverse

def get_breadcrumbs(node):
    """
    Recursively build the breadcrumb trail for the given node.
    """
    if node is None:
        return []

    breadcrumbs = []
    if node.parent_node:
        breadcrumbs = get_breadcrumbs(node.parent_node)
    elif node.parent_forum:
        forum_url = reverse('view-forum-page', kwargs={'forum_slug': node.parent_forum.slug})
        breadcrumbs = [{'name': node.parent_forum.name, 'url': forum_url}]

    node_url = reverse('view-node-page', kwargs={'node_slug': node.slug})
    breadcrumbs.append({'name': node.name, 'url': node_url})
    return breadcrumbs

def convert_to_localtime(date, format="%B %d, %Y - %I:%M %p"):
    return timezone.localtime(date).strftime(format)

def get_online_users():
    from .models import Profile
    from django.utils import timezone
    return Profile.objects.filter(last_activity__gte=timezone.now()-timezone.timedelta(minutes=settings.OFFLINE_TRESHOLD_MINUTES))

def update_user_activity(request):
    from .models import Profile
    from django.utils import timezone
    Profile.objects.filter(user=request.user).update(last_activity=timezone.now())

def format_number(num):
    if num >= 1000000000:
        return f'{num / 1000000000:.1f}B'
    elif num >= 1000000:
        return f'{num / 1000000:.1f}M'
    elif num >= 1000:
        return f'{num / 1000:.1f}K'
    else:
        return str(num)

def get_weekday_name(date):
    return date.strftime("%A")

def pages_count(object, per_page=8):
    return float(object.count() / per_page)