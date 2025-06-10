import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if isinstance(self.scope["user"], AnonymousUser):
            await self.close()
            return

        # Add the user to their personal notification group
        user_id = str(self.scope["user"].id)
        await self.channel_layer.group_add(
            f"user_{user_id}_notifications",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        if not isinstance(self.scope["user"], AnonymousUser):
            user_id = str(self.scope["user"].id)
            await self.channel_layer.group_discard(
                f"user_{user_id}_notifications",
                self.channel_name
            )

    async def receive(self, text_data):
        if isinstance(self.scope["user"], AnonymousUser):
            await self.close()
            return

        data = json.loads(text_data)
        # Handle any incoming messages if needed
        pass

    async def notification_message(self, event):
        # Send notification to WebSocket
        await self.send(text_data=json.dumps(event['data'])) 