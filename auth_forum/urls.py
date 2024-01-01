from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('login/', views.login_page, name='login-page'),
    path('logout/', views.logout_page, name='logout-page'),
]