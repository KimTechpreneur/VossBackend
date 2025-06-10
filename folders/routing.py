from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/folders/$', consumers.FolderConsumer.as_asgi()),
] 