import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        # Each user joins a group named after their ID.
        # This ensures notifications are sent only to the correct user.
        self.room_group_name = f'notifications_{self.user.id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"User {self.user.id} connected to notification socket.")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"User {self.user.id} disconnected.")

    # This method is called when a message is sent to the group.
    async def send_notification(self, event):
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=message)
        print(f"Sent notification to {self.user.id}") 