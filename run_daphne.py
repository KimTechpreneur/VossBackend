import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VossBackend.settings')
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from transfers.routing import websocket_urlpatterns as transfers_websocket_urlpatterns
from folders.routing import websocket_urlpatterns as folders_websocket_urlpatterns
from notifications.routing import websocket_urlpatterns as notifications_websocket_urlpatterns

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            transfers_websocket_urlpatterns + 
            folders_websocket_urlpatterns + 
            notifications_websocket_urlpatterns
        )
    ),
}) 