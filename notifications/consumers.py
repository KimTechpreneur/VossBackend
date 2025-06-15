import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        logger.info(f"[WebSocket] Connection attempt from user: {self.user}")

        if not self.user.is_authenticated:
            logger.warning(f"[WebSocket] Rejecting connection - user not authenticated")
            await self.close()
            return

        # Each user joins a group named after their ID.
        # This ensures notifications are sent only to the correct user.
        self.room_group_name = f'notifications_{self.user.id}'
        logger.info(f"[WebSocket] User {self.user.id} joining group: {self.room_group_name}")

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        logger.info(f"[WebSocket] User {self.user.id} connected successfully")

    async def disconnect(self, close_code):
        logger.info(f"[WebSocket] User {self.user.id} disconnecting with code: {close_code}")
        # Only attempt to discard the channel from the group if it was successfully added
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"[WebSocket] User {self.user.id} removed from group: {self.room_group_name}")
        logger.info(f"[WebSocket] User {self.user.id} disconnected")

    # This method is called when a message is sent to the group.
    async def send_notification(self, event):
        message = event['message']
        logger.info(f"[WebSocket] Sending notification to user {self.user.id}: {message}")
        
        # Send message to WebSocket
        await self.send(text_data=message)
        logger.info(f"[WebSocket] Notification sent successfully to user {self.user.id}")

    async def send_toast(self, event):
        """Send a lightweight toast notification payload to the client."""
        payload = {
            "type": "toast",
            "title": event.get("title"),
            "message": event.get("message"),
        }
        logger.info("[WebSocket] Sending toast to user %s: %s", self.user.id, payload)
        await self.send(text_data=json.dumps(payload))

    async def receive(self, text_data):
        """Handle incoming messages from the client.
        Currently we only expect heartbeat `ping` frames from the React front-end.
        When we receive a `{ "type": "ping" }` payload we immediately reply
        with `{ "type": "pong" }` so the client knows the connection is still
        alive.  Any other payloads are ignored for now but logged for future
        use.  This keeps the socket open and prevents the front-end from
        closing the connection prematurely (which triggered the endless
        reconnect attempts you saw in the log).
        """
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            logger.warning(
                "[WebSocket] Received non-JSON payload from user %s: %s", self.user.id, text_data
            )
            return

        msg_type = data.get("type")

        # Heartbeat handling
        if msg_type == "ping":
            await self.send(json.dumps({"type": "pong"}))
            logger.debug("[WebSocket] Pong sent to user %s", self.user.id)
            return

        # Placeholder for future message types coming from client
        logger.info("[WebSocket] Received message from user %s: %s", self.user.id, data)