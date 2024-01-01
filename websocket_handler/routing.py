from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path('ws/online-users/', consumers.OnlineConsumer.as_asgi()),
]
