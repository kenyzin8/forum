from django.contrib import admin
from .models import *

# Register your models here.
class ForumAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

class NodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

class GroupMembershipInline(admin.TabularInline):
    model = GroupMembership
    extra = 1 

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'address', 'description', 'image', 'last_activity')
    search_fields = ('name', 'email', 'phone', 'address', 'description')
    inlines = [GroupMembershipInline, ]  

class MessageAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'created_at', 'updated_at', 'author', 'is_active')
    search_fields = ('title', 'content')

class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'content', 'created_at', 'updated_at', 'author', 'is_active')
    search_fields = ('title', 'content')

class ReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'author', 'post', 'created_at', 'updated_at', 'is_active')
    search_fields = ('content', 'author')

class ReactionAdmin(admin.ModelAdmin):
    list_display = ('reaction', 'author')
    search_fields = ('reaction', 'author')

class PrefixAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'description', 'node')
    search_fields = ('name', 'color', 'description', 'node')

class UserGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

class StatusAdmin(admin.ModelAdmin):
    list_display = ('author', 'content')
    search_fields = ('author', 'content')

class PostViewAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'last_viewed')
    search_fields = ('user', 'post', 'last_viewed')

class WelcomeMessageAdmin(admin.ModelAdmin):
    list_display = ('message', 'event', 'is_active', 'position')
    search_fields = ('message', 'event')


admin.site.register(Forum, ForumAdmin)
admin.site.register(Node, NodeAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Reply, ReplyAdmin)
admin.site.register(Reaction, ReactionAdmin)
admin.site.register(Prefix, PrefixAdmin)
admin.site.register(UserGroup, UserGroupAdmin)
admin.site.register(Status, StatusAdmin)
admin.site.register(PostView, PostViewAdmin)
admin.site.register(WelcomeMessages, WelcomeMessageAdmin)