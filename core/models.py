from django.db import models
from django.utils import timezone
from colorfield.fields import ColorField
from django.utils.text import slugify
from django.utils.safestring import mark_safe as safe
from django.db.models import Max
from django.conf import settings

import datetime

from .helper import *

class WelcomeMessages(models.Model):
    message = models.TextField(help_text="Use 'USER' in the message, and it will be replaced with the user's name.")
    event = models.CharField(max_length=200)
    image = models.ImageField(upload_to='welcome/', null=True, blank=True, help_text="Recommended size: 1920x1080")
    announcement_url = models.URLField(null=True, blank=True)
    url_format = models.TextField(max_length=200, null=True, blank=True, help_text="Use 'ANNOUNCEMENT_URL' in the format, and it will be replaced with the actual link (Word: 'here').")
    position = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)

    login_required = models.BooleanField(default=False)

    is_centered = models.BooleanField(default=False, help_text="Center the message on the page if needed such as short message.")

    def dynamic_message_text(self, user_profile):
        if self.message:
            return self.message.replace('USER', user_profile.name)

    def dynamic_url_text(self):
        if self.url_format:
            anchor_tag = f"<a class='link no-underline text-primary font-semibold tooltip mx-auto' href='{self.announcement_url}' target='_blank'>here</a>"
            return self.url_format.replace('ANNOUNCEMENT_URL', anchor_tag)
        return f"Click <a class='link no-underline text-primary font-semibold tooltip mx-auto' href='{self.announcement_url}' target='_blank'>here</a> to visit our announcement"

    def save(self, *args, **kwargs):
        if not self.pk:
            max_position = WelcomeMessages.objects.aggregate(Max('position'))['position__max']
            if max_position is None:
                max_position = 0
            self.position = max_position + 1

        super(WelcomeMessages, self).save(*args, **kwargs)

    def __str__(self):
        return self.message

    class Meta:
        verbose_name = 'Welcome Message'
        verbose_name_plural = 'Welcome Messages'
        ordering = ['position']

class UserGroup(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    color = ColorField(default='#FF0000')
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    is_bold = models.BooleanField(default=False)
    is_italic = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    def get_ug_style(self):
        """
        Returns a style string with the background color set to the usergroups's color
        and the text color set to either black or white for contrast.
        """

        def get_contrast_yiq(hexcolor):
            hexcolor = hexcolor.lstrip('#')
            r, g, b = tuple(int(hexcolor[i:i+2], 16) for i in (0, 2, 4))
            yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000
            return 'black' if yiq >= 128 else 'white'

        text_color = get_contrast_yiq(self.color)

        return f'color: {self.color};'

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'User Group'
        verbose_name_plural = 'User Groups'

class Profile(models.Model):

    THEME_CHOICES = [
        ('dark', 'Dark'),
        ('light', 'Light'),
    ]


    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    phone = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='profile/', null=True, blank=True)

    user_group = models.ManyToManyField(UserGroup, through='GroupMembership', blank=True)

    last_activity = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    is_verified = models.BooleanField(default=False)

    # settings
    hide_welcome_message = models.BooleanField(default=False)
    # and more to come

    @classmethod
    def get_latest_member(cls):
        return cls.objects.order_by('-user__date_joined').first()

    def is_user_online(self):
        return timezone.now() - self.last_activity < timezone.timedelta(minutes=settings.OFFLINE_TRESHOLD_MINUTES)

    def get_color(self):
        membership = self.groupmembership_set.filter(user_group__is_active=True).order_by('position').first()
        if membership:
            return membership.user_group.color
        return '#FFFFFF'

    def get_formatted_name(self):
        membership = self.groupmembership_set.filter(user_group__is_active=True).order_by('position').first()
        if membership:
            color = membership.user_group.color
            bold = 'font-weight: bold;' if membership.user_group.is_bold else ''
            italic = 'font-style: italic;' if membership.user_group.is_italic else ''
            verified = f'<span style="color: #1DA1F2" class="ml-1 text-xs tooltip tooltip-warning" data-tip="{self.name} is verified">✓</span>' if self.is_verified else ''
            return safe(f'<span class="tooltip tooltip-warning" data-tip="{self.name}" style="color: {color}; {bold} {italic}">{self.name}</span>{verified}')
        return safe(f'<span class="tooltip tooltip-warning" data-tip="{self.name}" style="color: #FFFFFF;">{self.name}</span>')

    def get_first_membership(self):
        membership = self.groupmembership_set.filter(user_group__is_active=True).order_by('position').first()
        if membership:
            return membership.user_group.name
        return 'Noob'

    def get_total_likes(self):
        return self.post_likes.count() + self.reply_likes.count()

    def get_total_messages(self):
        return self.message_set.count() + self.reply_set.count() + self.post_set.count()

    def __str__(self):
        return self.name

class GroupMembership(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    user_group = models.ForeignKey(UserGroup, on_delete=models.CASCADE)
    position = models.IntegerField()

    class Meta:
        ordering = ['position']

    def __str__(self):
        return f'{self.profile.name} - {self.user_group.name}'

class Message(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    viewer = models.ManyToManyField(Profile, related_name='viewer', blank=True)

    is_active = models.BooleanField(default=True)

    replies = models.ManyToManyField('Reply', blank=True)
    reactions = models.ManyToManyField('Reaction', blank=True)

    slug = models.SlugField(null=True, blank=True, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        is_new = self._state.adding

        super(Message, self).save(*args, **kwargs)

        if is_new and not self.slug:
            self.slug = slugify(f'{self.name} {self.id}')
            super(Message, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

class Forum(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    access = models.ManyToManyField(UserGroup, blank=True)

    is_active = models.BooleanField(default=True)

    feather_icon = models.CharField(max_length=200, null=True, blank=True, default='folder')

    position = models.IntegerField(default=0)

    slug = models.SlugField(null=True, blank=True, unique=True)

    login_required = models.BooleanField(default=False)

    def upper_title(self):
        return self.name.upper()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:
            max_position = Forum.objects.aggregate(Max('position'))['position__max']
            if max_position is None:
                max_position = 0
            self.position = max_position + 1

        is_new = self._state.adding

        super(Forum, self).save(*args, **kwargs)

        if is_new and not self.slug:
            self.slug = slugify(f'{self.name} {self.id}')
            super(Forum, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Forum'
        verbose_name_plural = 'Forums'
        ordering = ['position']

class Node(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    parent_node = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children_nodes')
    parent_forum = models.ForeignKey(Forum, on_delete=models.CASCADE, null=True, blank=True)

    access = models.ManyToManyField(UserGroup, blank=True)

    slug = models.SlugField(null=True, blank=True, unique=True)

    display_description = models.BooleanField(default=True)

    position = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)

    login_required = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def total_posts(self):
        count = self.post_set.filter(is_active=True).count()

        for child_node in self.children_nodes.all():
            count += child_node.post_set.filter(is_active=True).count()

        return format_number(count)

    def total_replies(self):
        count = Reply.objects.filter(post__node=self, is_active=True).count()

        for child_node in self.children_nodes.all():
            count += Reply.objects.filter(post__node=child_node, is_active=True).count()

        return format_number(count)
    
    def get_latest_post(self):
        return self.post_set.filter(is_active=True).order_by('-created_at').first()
    
    def get_latest_reply(self):
        return Reply.objects.filter(post__node=self, is_active=True).order_by('-created_at').first()

    def get_latest_post_or_reply(self):
        latest_post = self.post_set.filter(is_active=True).order_by('-created_at').first()
        latest_reply = Reply.objects.filter(post__node=self, is_active=True).order_by('-created_at').first()

        if latest_post and latest_reply:
            return latest_reply if latest_reply.created_at > latest_post.created_at else latest_post
        elif latest_post:
            return latest_post
        elif latest_reply:
            return latest_reply
        else:
            return None
        
    def new_post_alert(self, user_profile):
        all_posts = self.post_set.all()

        for post in all_posts:
            try:
                post_view = PostView.objects.get(user=user_profile, post=post)

                if post.updated_at > post_view.last_viewed:
                    return True

                new_replies = Reply.objects.filter(post=post, created_at__gt=post_view.last_viewed, is_active=True)
                if new_replies.exists():
                    return True

            except PostView.DoesNotExist:
                return True

        return False

    def save(self, *args, **kwargs):
        if not self.pk:
            max_position = Forum.objects.aggregate(Max('position'))['position__max']
            if max_position is None:
                max_position = 0
            self.position = max_position + 1

        is_new = self._state.adding

        super(Node, self).save(*args, **kwargs)

        if is_new and not self.slug:
            self.slug = slugify(f'{self.name} {self.id}')
            super(Node, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Node'
        verbose_name_plural = 'Nodes'
        ordering = ['position']

class Prefix(models.Model):
    name = models.CharField(max_length=200)
    color = ColorField(default='#FF0000')
    description = models.TextField()
    node = models.ForeignKey(Node, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def get_prefix_style(self):
        """
        Returns a style string with the background color set to the prefix's color
        and the text color set to either black or white for contrast.
        """

        def get_contrast_yiq(hexcolor):
            hexcolor = hexcolor.lstrip('#')
            r, g, b = tuple(int(hexcolor[i:i+2], 16) for i in (0, 2, 4))
            yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000
            return 'black' if yiq >= 128 else 'white'

        text_color = get_contrast_yiq(self.color)

        return f'background: {self.color}; color: {text_color};font-weight: 700;'

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Prefix'
        verbose_name_plural = 'Prefixes'

class Post(models.Model):
    title = models.CharField(max_length=200)
    prefix = models.ForeignKey(Prefix, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)

    is_active = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)

    reactions = models.ManyToManyField('Reaction', blank=True)

    likes = models.ManyToManyField(Profile, related_name='post_likes', blank=True)

    views = models.ManyToManyField(Profile, related_name='views', blank=True)

    node = models.ForeignKey(Node, on_delete=models.CASCADE, null=True, blank=True)

    slug = models.SlugField(null=True, blank=True, unique=True)

    login_required = models.BooleanField(default=False)

    def is_liked_by_user(self, profile):
        return self.likes.filter(id=profile.id).exists()

    def total_replies(self):
        count = Reply.objects.filter(post=self, is_active=True).count()
        return format_number(count)

    def total_views(self):
        if self.views.count() > 0:
            return format_number(self.views.count())

        return 0

    def get_latest_reply_author(self):
        reply = Reply.objects.filter(post=self, is_active=True).order_by('-created_at').first()
        if reply:
            return reply.author
        else:
            return self.author

    def get_latest_reply(self):
        reply = Reply.objects.filter(post=self, is_active=True).order_by('-created_at').first()
        if reply:
            return reply
        else:
            return self

    def formatted_updated_at(self):
        now = timezone.localtime()
        updated_at_local = timezone.localtime(self.updated_at)

        if updated_at_local.date() == now.date():
            return "Today at " + convert_to_localtime(self.updated_at, "%I:%M %p")
        elif updated_at_local.date() == now.date() - datetime.timedelta(days=1):
            return "Yesterday at " + convert_to_localtime(self.updated_at, "%I:%M %p")
        elif updated_at_local.date() > now.date() - datetime.timedelta(days=7):
            return get_weekday_name(updated_at_local) + " at " + convert_to_localtime(self.updated_at, "%I:%M %p")
        else:
            return convert_to_localtime(self.updated_at, "%B %d, %Y at %I:%M %p")

    def formatted_created_at(self):
        now = timezone.localtime()
        created_at_local = timezone.localtime(self.created_at)

        if created_at_local.date() == now.date():
            return "Today at " + convert_to_localtime(self.created_at, "%I:%M %p")
        elif created_at_local.date() == now.date() - datetime.timedelta(days=1):
            return "Yesterday at " + convert_to_localtime(self.created_at, "%I:%M %p")
        elif created_at_local.date() > now.date() - datetime.timedelta(days=7):
            return get_weekday_name(created_at_local) + " at " + convert_to_localtime(self.created_at, "%I:%M %p")
        else:
            return convert_to_localtime(self.created_at, "%B %d, %Y at %I:%M %p")

    def is_current_user_viewed(self, profile):
        try:
            post_view = PostView.objects.get(post=self, user=profile)
            return self.updated_at <= post_view.last_viewed
        except PostView.DoesNotExist:
            return False

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        is_new = self._state.adding

        super(Post, self).save(*args, **kwargs)

        if is_new and not self.slug:
            self.slug = slugify(f'{self.title} {self.id}')
            super(Post, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

class PostView(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    last_viewed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'post')

class Reply(models.Model):
    content = models.TextField()
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    likes = models.ManyToManyField(Profile, related_name="reply_likes", blank=True)

    reactions = models.ManyToManyField('Reaction', blank=True)

    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)

    def is_reply_liked(self, user):
        return self.likes.filter(id=user.id).exists()

    def formatted_updated_at(self):
        now = timezone.localtime()
        updated_at_local = timezone.localtime(self.updated_at)

        if updated_at_local.date() == now.date():
            return "Today at " + convert_to_localtime(self.updated_at, "%I:%M %p")
        elif updated_at_local.date() == now.date() - datetime.timedelta(days=1):
            return "Yesterday at " + convert_to_localtime(self.updated_at, "%I:%M %p")
        elif updated_at_local.date() > now.date() - datetime.timedelta(days=7):
            return get_weekday_name(updated_at_local) + " at " + convert_to_localtime(self.updated_at, "%I:%M %p")
        else:
            return convert_to_localtime(self.updated_at, "%B %d, %Y at %I:%M %p")

    def formatted_created_at(self):
        now = timezone.localtime()
        created_at_local = timezone.localtime(self.created_at)

        if created_at_local.date() == now.date():
            return "Today at " + convert_to_localtime(self.created_at, "%I:%M %p")
        elif created_at_local.date() == now.date() - datetime.timedelta(days=1):
            return "Yesterday at " + convert_to_localtime(self.created_at, "%I:%M %p")
        elif created_at_local.date() > now.date() - datetime.timedelta(days=7):
            return get_weekday_name(created_at_local) + " at " + convert_to_localtime(self.created_at, "%I:%M %p")
        else:
            return convert_to_localtime(self.created_at, "%B %d, %Y at %I:%M %p")

    def __str__(self):
        return f'Reply by {self.author.name}'

    class Meta:
        verbose_name = 'Reply'
        verbose_name_plural = 'Replies'

class Reaction(models.Model):
    LIKE = 'LIKE'
    LOVE = 'LOVE'
    CARE = 'CARE'
    HAHA = 'HAHA'
    WOW = 'WOW'
    SAD = 'SAD'
    ANGRY = 'ANGRY'

    REACTION_CHOICES = [
        (LIKE, 'Like'),
        (LOVE, 'Love'),
        (CARE, 'Care'),
        (HAHA, 'Haha'),
        (WOW, 'Wow'),
        (SAD, 'Sad'),
        (ANGRY, 'Angry'),
    ]

    reaction = models.CharField(max_length=5, choices=REACTION_CHOICES, default=LIKE)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return self.reaction + ' by ' + self.author.name

    class Meta:
        verbose_name = 'Reaction'
        verbose_name_plural = 'Reactions'

class Status(models.Model):
    content = models.TextField()
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    is_active = models.BooleanField(default=True)

    def formatted_created_at(self):
        self.created_at = timezone.localtime(self.created_at)
        if self.created_at.date() == timezone.localtime().date():
            return "Today at " + convert_to_localtime(self.created_at, "%I:%M %p")
        else:
            return convert_to_localtime(self.created_at, "%B %d, %Y at %I:%M %p")

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = 'Status'
        verbose_name_plural = 'Statuses'
        ordering = ['-created_at']