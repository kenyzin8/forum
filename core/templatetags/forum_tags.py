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

@register.simple_tag
def is_user_viewed_post(post, profile):
    return post.is_current_user_viewed(profile)

@register.filter
def get_item(list, index):
    return list[index]

@register.simple_tag
def get_dynamic_message(wc_message, profile):
    return wc_message.dynamic_message_text(profile)