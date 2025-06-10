import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

class FolderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if isinstance(self.scope["user"], AnonymousUser):
            await self.close()
            return

        await self.channel_layer.group_add('folders', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('folders', self.channel_name)

    async def receive(self, text_data):
        if isinstance(self.scope["user"], AnonymousUser):
            await self.close()
            return

        data = json.loads(text_data)
        if data.get('action') == 'mark_collected':
            folder_id = data.get('folder_id')
            # Logic to mark folder as collected (e.g., call a service or update DB)
            # For now, we'll just broadcast the action
            await self.channel_layer.group_send(
                'folders',
                {
                    'type': 'folder_update',
                    'data': {
                        'id': folder_id,
                        'status': 'collected',
                        'action': 'mark_collected'
                    }
                }
            )

    async def folder_update(self, event):
        # Send real-time updates to the client
        await self.send(text_data=json.dumps(event['data'])) 