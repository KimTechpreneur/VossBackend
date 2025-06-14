from users.models import User
from .models import NotificationHistoryItem
from .serializers import NotificationHistoryItemSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json
from uuid import UUID

def create_and_send_notification(user: User, title: str, message: str, notification_type: str, reference_id: str):
    """
    Helper function to create a notification history item and send it via WebSocket.
    """
    if not isinstance(user, User):
        print(f"Warning: Recipient '{user}' is not a valid User object. Skipping notification.")
        return

    # Create the in-app notification
    history_item = NotificationHistoryItem.objects.create(
        user=user,
        title=title,
        message=message,
        type=notification_type,
        reference_id=reference_id
    )

    # Send via WebSocket
    channel_layer = get_channel_layer()
    user_channel_group = f"notifications_{user.id}"
    serializer = NotificationHistoryItemSerializer(history_item)
    
    async_to_sync(channel_layer.group_send)(
        user_channel_group,
        {
            'type': 'send_notification',
            'message': json.dumps(serializer.data)
        }
    )
    print(f"Sent notification '{title}' to {user.email}")

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)

def json_encode(data):
    """
    Safely encode data to JSON, handling UUID objects.
    """
    return json.dumps(data, cls=UUIDEncoder) 