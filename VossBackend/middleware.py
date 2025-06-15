from channels.middleware import BaseMiddleware
from channels.auth import AuthMiddlewareStack
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class WebSocketAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Get the token from query string
        query_string = scope.get('query_string', b'').decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        logger.info(f"[WebSocket] Received connection attempt with token: {token[:20] if token else 'None'}...")

        if token:
            try:
                # Verify the token and get the user
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                logger.info(f"[WebSocket] Token validated for user_id: {user_id}")
                
                user = await self.get_user(user_id)
                if isinstance(user, AnonymousUser):
                    logger.warning(f"[WebSocket] User {user_id} not found in database")
                else:
                    logger.info(f"[WebSocket] User {user_id} authenticated successfully")
                
                scope['user'] = user
            except Exception as e:
                logger.error(f"[WebSocket] Token validation failed: {str(e)}")
                scope['user'] = AnonymousUser()
        else:
            logger.warning("[WebSocket] No token provided in connection attempt")
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)

    @staticmethod
    async def get_user(user_id):
        try:
            user = await User.objects.aget(id=user_id)
            logger.info(f"[WebSocket] Retrieved user {user_id} from database")
            return user
        except User.DoesNotExist:
            logger.warning(f"[WebSocket] User {user_id} not found in database")
            return AnonymousUser() 