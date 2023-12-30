from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('forum/', views.forum, name='forum-page'),
    path('image-upload/', views.image_upload, name='image-upload'),
    path('forum/view-post/<slug:title_slug>/', views.view_post, name='view-post-page'),
    path('forum/submit-reply/<int:post_id>/', views.submit_reply, name='submit-reply-page'),
    path('forum/get-post-content/', views.get_post_content, name='get-post-content-page'),
    path('forum/like-post/', views.like_post, name='like-post-page'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)