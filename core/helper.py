from django.utils import timezone

def get_breadcrumbs(node):
    """
    Recursively build the breadcrumb trail for the given node.
    """
    if node is None:
        return []
    else:
        return get_breadcrumbs(node.parent) + [{'name': node.name, 'id': node.id}]

def convert_to_localtime(date, format="%B %d, %Y - %I:%M %p"):
    return timezone.localtime(date).strftime(format)