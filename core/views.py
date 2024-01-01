from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core import serializers
from django.core.paginator import Paginator
from django.utils import timezone

import datetime
import uuid

from .models import *
from .helper import *

def home(request):
    prefixes = Prefix.objects.filter(is_active=True)

    context = { 'prefixes': prefixes }

    return render(request, 'home.html', context)

def forum(request):
    five_latest_posts = Post.objects.filter(is_active=True).order_by('-updated_at')[:5]

    forums = Forum.objects.filter(is_active=True)

    statuses = Status.objects.filter(is_active=True)[:10]

    online_users = get_online_users()

    update_user_activity(request)

    total_posts = Post.objects.all().count()
    total_replies = Reply.objects.all().count()
    total_members = Profile.objects.all().count()
    latest_member_profile = Profile.get_latest_member()

    context = { 'five_latest_posts': five_latest_posts, 'forums': forums, 'statuses': statuses, 'online_users': online_users, 'total_posts': total_posts, 'total_replies': total_replies, 'total_members': total_members, 'latest_member': latest_member_profile }

    return render(request, 'forum.html', context)

def view_forum(request, forum_slug):
    nodes = Node.objects.filter(parent_forum__slug=forum_slug, is_active=True)
    forum = get_object_or_404(Forum, slug=forum_slug)

    all_posts = Post.objects.filter(node__parent_forum__slug=forum_slug, is_active=True).order_by('-updated_at')

    paginator = Paginator(all_posts, 8)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    page_numbers = pages_count(all_posts)

    context = {'nodes': nodes, 'parent_forum': forum, 'posts': posts, 'all_posts_count': all_posts.count(), 'page_numbers': page_numbers}
    return render(request, 'view_forum.html', context)

def view_node(request, node_slug):
    all_posts = Post.objects.filter(node__slug=node_slug, is_active=True).order_by('-updated_at')
    node = get_object_or_404(Node, slug=node_slug)
    
    breadcrumbs = get_breadcrumbs(node)

    paginator = Paginator(all_posts, 8)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    page_numbers = pages_count(all_posts)

    context = { 'posts': posts, 'parent_node': node, 'breadcrumbs': breadcrumbs, 'all_posts_count': all_posts.count(), 'page_numbers': page_numbers }
    return render(request, 'nodes/view_node.html', context)

def view_post(request, title_slug):
    post = get_object_or_404(Post, slug=title_slug)

    post.created_at_formatted = convert_to_localtime(post.created_at)

    all_replies = Reply.objects.filter(post=post).order_by('created_at')

    for replies in all_replies:
        replies.created_at_formatted = convert_to_localtime(replies.created_at)

    paginator = Paginator(all_replies, 5) 
    page_number = request.GET.get('page', 1)
    replies = paginator.get_page(page_number)
    replies_json = serializers.serialize('json', replies)

    node = post.node
    breadcrumbs = get_breadcrumbs(node)

    post.views.add(request.user.profile)

    post_view, created = PostView.objects.get_or_create(user=request.user.profile, post=post)
    post_view.save()

    page_numbers = pages_count(all_replies, 5)

    context = {
        'post': post,
        'replies': replies,
        'breadcrumbs': breadcrumbs,
        'replies_json': replies_json,
        'all_replies_count': all_replies.count(),
        'page_numbers': page_numbers,
    }

    return render(request, 'posts/view_post.html', context)

@csrf_exempt 
def image_upload(request):
    if request.method == 'POST':
        image = request.FILES['upload']
        image_name = default_storage.save(image.name, image)
        image_url = default_storage.url(image_name)
        return JsonResponse({'url': image_url})
    return JsonResponse({'error': 'POST request required.'})

def submit_reply(request, post_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST request required.'})

    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'You must be logged in to reply.'})

    if request.POST['content'] == '':
        return JsonResponse({'success': False, 'message': 'Reply cannot be empty.'})

    post = get_object_or_404(Post, pk=post_id)

    if post.is_locked:
        return JsonResponse({'success': False, 'message': 'This post is locked.'})

    if not post.is_active:
        return JsonResponse({'success': False, 'message': 'This post has been deleted.'})

    reply = Reply(content=request.POST['content'], author=request.user.profile, post=post)
    reply.save()
    
    post.updated_at = timezone.now()
    post.save()
    
    post_view, created = PostView.objects.get_or_create(user=request.user.profile, post=post)
    post_view.save()

    memberships = reply.author.groupmembership_set.all()
    serialized_memberships = [
        {
            'name': membership.user_group.name,
            'style': membership.user_group.get_ug_style(),
        }
        for membership in memberships
    ]

    reply_data = {
        'id': reply.id,
        'content': reply.content,
        'author': {
            'name': reply.author.name,
            'name_with_color': reply.author.get_formatted_name(),
            'color': reply.author.get_color(),
            'profile_pic': reply.author.image.url,
            'memberships': serialized_memberships,
        },
        'created_at': reply.formatted_created_at(),
    }

    return JsonResponse({'success': True, 'reply': reply_data})

def get_post_content(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'GET request required.'})

    type = request.GET['entity_type']
    id = request.GET['entity_id']

    if type == 'post':
        post = get_object_or_404(Post, pk=id)
        return JsonResponse({'success': True, 'content': post.content})
    elif type == 'reply':
        reply = get_object_or_404(Reply, pk=id)
        return JsonResponse({'success': True, 'content': reply.content})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid entity type.'})

def like_post(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required.'})

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'You must be logged in to like a post.'})

    type = request.POST['entity_type']
    id = request.POST['entity_id']

    if type == 'post':
        post = get_object_or_404(Post, pk=id)
        if request.user.profile in post.likes.all():
            post.likes.remove(request.user.profile)
            return JsonResponse({'success': True, 'is_liked': False, 'like_count': post.likes.count()})
        else:
            post.likes.add(request.user.profile)
            return JsonResponse({'success': True, 'is_liked': True, 'like_count': post.likes.count()})
    elif type == 'reply':
        reply = get_object_or_404(Reply, pk=id)
        if request.user.profile in reply.likes.all():
            reply.likes.remove(request.user.profile)
            return JsonResponse({'success': True, 'is_liked': False, 'like_count': reply.likes.count()})
        else:
            reply.likes.add(request.user.profile)
            return JsonResponse({'success': True, 'is_liked': True, 'like_count': reply.likes.count()})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid entity type.'})