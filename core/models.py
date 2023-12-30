from django.db import models
from django.utils import timezone
from colorfield.fields import ColorField
from django.utils.text import slugify
from django.utils.safestring import mark_safe as safe
from django.db.models import Max

from .helper import *

class UserGroup(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    color = ColorField(default='#FF0000')
    date_created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

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
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)
    phone = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='profile/', null=True, blank=True)

    user_group = models.ManyToManyField(UserGroup, through='GroupMembership', blank=True)

    def get_color(self):
        membership = self.groupmembership_set.order_by('position').first()
        if membership:
            return membership.user_group.color
        return '#FFFFFF'

    def get_name_with_color(self):
        membership = self.groupmembership_set.order_by('position').first()
        if membership:
            color = membership.user_group.color
            return safe(f'<span style="color: {color};">{self.name}</span>')
        return safe(f'<span style="color: #FFFFFF;">{self.name}</span>')

    def get_first_membership(self):
        membership = self.groupmembership_set.order_by('position').first()
        if membership:
            return membership.user_group.name
        return 'Noob'

    def get_total_likes(self):
        return self.post_likes.count() + self.reply_likes.count()

    def get_total_messages(self):
        return self.message_set.count() + self.reply_set.count()

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

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

class Forum(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    access = models.ManyToManyField(UserGroup, blank=True)

    is_active = models.BooleanField(default=True)

    nodes = models.ManyToManyField('Node', blank=True)

    feather_icon = models.CharField(max_length=200, null=True, blank=True, default='folder')

    position = models.IntegerField(default=0)

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

        super(Forum, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Forum'
        verbose_name_plural = 'Forums'
        ordering = ['position']

class Node(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    access = models.ManyToManyField(UserGroup, blank=True)

    def __str__(self):
        return self.name

    def total_posts(self):
        return self.post_set.filter(is_active=True).count()

    def total_replies(self):
        return sum(post.replies.filter(is_active=True).count() for post in self.post_set.filter(is_active=True))
    
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
        latest_post = self.post_set.filter(is_active=True).order_by('-created_at').first()

        if latest_post:
            if user_profile not in latest_post.views.all():
                return True
        return False

    class Meta:
        verbose_name = 'Node'
        verbose_name_plural = 'Nodes'

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

        return f'background: {self.color}; color: {text_color};'

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

    replies = models.ManyToManyField('Reply', blank=True)
    reactions = models.ManyToManyField('Reaction', blank=True)

    likes = models.ManyToManyField(Profile, related_name='post_likes', blank=True)

    views = models.ManyToManyField(Profile, related_name='views', blank=True)

    node = models.ForeignKey(Node, on_delete=models.CASCADE, null=True, blank=True)

    slug = models.SlugField(null=True, blank=True, unique=True)

    def is_liked_by_user(self, profile):
        return self.likes.filter(id=profile.id).exists()

    def total_replies(self):
        if self.replies.count() > 0:
            return self.replies.count()

        return 0

    def total_views(self):
        if self.views.count() > 0:
            return self.views.count()

        return 0

    def get_latest_reply_author(self):
        if self.total_replies() > 0:
            return self.replies.last().author
        else:
            return self.author

    def get_latest_reply(self):
        if self.total_replies() > 0:
            return self.replies.last()
        else:
            return self

    def formatted_updated_at(self):
        self.updated_at = timezone.localtime(self.updated_at)
        if self.updated_at.date() == timezone.localtime().date():
            return "Today at " + convert_to_localtime(self.updated_at, "%I:%M %p")
        else:
            return convert_to_localtime(self.updated_at, "%B %d, %Y at %I:%M %p")

    def formatted_created_at(self):
        self.created_at = timezone.localtime(self.created_at)
        if self.created_at.date() == timezone.localtime().date():
            return "Today at " + convert_to_localtime(self.created_at, "%I:%M %p")
        else:
            return convert_to_localtime(self.created_at, "%B %d, %Y at %I:%M %p")

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

class Reply(models.Model):
    content = models.TextField()
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    likes = models.ManyToManyField(Profile, related_name="reply_likes", blank=True)

    reactions = models.ManyToManyField('Reaction', blank=True)

    def is_reply_liked(self, user):
        return self.likes.filter(id=user.id).exists()

    def formatted_updated_at(self):
        self.updated_at = timezone.localtime(self.updated_at)
        if self.updated_at.date() == timezone.localtime().date():
            return "Today at " + convert_to_localtime(self.updated_at, "%I:%M %p")
        else:
            return convert_to_localtime(self.updated_at, "%B %d, %Y at %I:%M %p")

    def formatted_created_at(self):
        self.created_at = timezone.localtime(self.created_at)
        if self.created_at.date() == timezone.localtime().date():
            return "Today at " + convert_to_localtime(self.created_at, "%I:%M %p")
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