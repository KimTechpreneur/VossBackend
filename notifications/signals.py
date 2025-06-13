from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json

# It's common to have a central place for business logic that determines who should be notified.
# For this example, let's assume you have a 'transfers' app with a 'FolderTransfer' model.
# You would need to import the actual models involved in the events.
# from transfers.models import FolderTransfer 

from .models import Notification, NotificationHistoryItem, User
from .serializers import NotificationHistoryItemSerializer

# This is a placeholder for your actual FolderTransfer model. 
# You should remove this and import your real model.
class FolderTransfer:
    pass

@receiver(post_save, sender=FolderTransfer)
def folder_transfer_notification_handler(sender, instance, created, **kwargs):
    """
    Listens for a new FolderTransfer and creates notifications.
    """
    if not created:
        # We are only interested in newly created transfers for this example.
        # You can add logic for updates here as well (e.g., if status changes).
        return

    # --- 1. Define the Notification Content ---
    # In a real app, this would be more dynamic, perhaps using NotificationTemplates.
    title = f"New Folder Transfer: {instance.id}"
    message = f"A new folder has been transferred from {instance.origin_office} to {instance.destination_office}."
    
    # --- 2. Determine Recipients ---
    # This is a critical step. You need to fetch the actual user objects who should be notified.
    # Example: Notifying all staff in the destination office.
    # This logic depends heavily on your User and Office models.
    # For this example, we'll just notify the creator (a placeholder).
    recipients = [instance.created_by] # Replace with your actual logic.
    
    # --- 3. Create and Broadcast Notifications ---
    for user in recipients:
        if not isinstance(user, User):
            print(f"Warning: Recipient '{user}' is not a valid User object. Skipping.")
            continue

        # Create the in-app notification history item that the user will see in their list.
        history_item = NotificationHistoryItem.objects.create(
            user=user,
            title=title,
            message=message,
            type='transfer', # Matches the frontend type
            reference_id=str(instance.id)
        )

        # The 'Notification' model could be used for more persistent, auditable notifications
        # or for queueing emails, but for real-time in-app, NotificationHistoryItem is sufficient.
        
        # --- 4. Send to WebSocket ---
        channel_layer = get_channel_layer()
        # Every user needs to be in a group named after their user ID.
        # Your consumer should handle adding users to this group on connection.
        user_channel_group = f"notifications_{user.id}"

        # Serialize the data that the frontend expects
        serializer = NotificationHistoryItemSerializer(history_item)
        
        async_to_sync(channel_layer.group_send)(
            user_channel_group,
            {
                'type': 'send_notification',
                'message': json.dumps(serializer.data)
            }
        )

    print(f"Notifications sent for FolderTransfer {instance.id}")


def connect_signals():
    """
    A function to connect all signals. Called in apps.py.
    """
    # Connect more signals here as you add more handlers.
    post_save.connect(folder_transfer_notification_handler, sender=FolderTransfer)
    print("Notification signals connected.")
