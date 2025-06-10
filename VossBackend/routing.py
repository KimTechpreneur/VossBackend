from channels.routing import URLRouter
from django.urls import re_path
from transfers.routing import websocket_urlpatterns as transfers_websocket_urlpatterns
from folders.routing import websocket_urlpatterns as folders_websocket_urlpatterns
from notifications.routing import websocket_urlpatterns as notifications_websocket_urlpatterns

# Combine all WebSocket URL patterns
websocket_urlpatterns = (
    transfers_websocket_urlpatterns +
    folders_websocket_urlpatterns +
    notifications_websocket_urlpatterns
) 