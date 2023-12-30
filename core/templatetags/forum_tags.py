from django import template

register = template.Library()

@register.simple_tag
def is_post_liked(post, profile):
    return post.is_liked_by_user(profile)

@register.simple_tag
def is_reply_liked(reply, profile):
    return reply.is_reply_liked(profile)

@register.simple_tag
def is_new_post_in_node(node, profile):
    return node.new_post_alert(profile)