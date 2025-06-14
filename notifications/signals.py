from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.core.mail import send_mail

# It's common to have a central place for business logic that determines who should be notified.
# For this example, let's assume you have a 'transfers' app with a 'FolderTransfer' model.
# You would need to import the actual models involved in the events.
# from transfers.models import FolderTransfer 

from transfers.models import Transfer, RoutingStep
from .models import Notification, NotificationHistoryItem, User
from .serializers import NotificationHistoryItemSerializer
from .utils import json_encode

# This is a placeholder for your actual FolderTransfer model. 
# You should remove this and import your real model.
class FolderTransfer:
    pass

@receiver(post_save, sender=Transfer)
def transfer_notification_handler(sender, instance, created, **kwargs):
    """
    Listens for a new Transfer and creates notifications for relevant parties.
    """
    if not created:
        return

    # --- 1. Define the Notification Content ---
    title = f"New Transfer Created: {instance.folder.title}"
    message = f"A new transfer '{instance.folder.title}' from {instance.source_office.office_name} to {instance.destination_office.office_name} has been created by {instance.created_by.get_full_name()}."
    
    # --- 2. Determine Recipients ---
    # We will notify the creator and the user responsible for the first step.
    recipients = {instance.created_by}
    
    first_step = instance.routing_steps.order_by('step_number').first()
    if first_step and first_step.responsible_user:
        recipients.add(first_step.responsible_user)
    
    # --- 3. Create and Broadcast Notifications ---
    for user in recipients:
        if not isinstance(user, User):
            print(f"Warning: Recipient '{user}' is not a valid User object. Skipping.")
            continue

        # Create the in-app notification if enabled
        if instance.notifications.get('in_app', False):
            history_item = NotificationHistoryItem.objects.create(
                user=user,
                title=title,
                message=message,
                type='transfer',
                reference_id=str(instance.id)
            )
            
            # Send to WebSocket
            channel_layer = get_channel_layer()
            user_channel_group = f"notifications_{user.id}"
            serializer = NotificationHistoryItemSerializer(history_item)
            
            async_to_sync(channel_layer.group_send)(
                user_channel_group,
                {
                    'type': 'send_notification',
                    'message': json_encode(serializer.data)
                }
            )

        # Send email notification if enabled
        if instance.notifications.get('email', False):
            send_mail(
                'New VOSS Transfer Created',
                f"Hello {user.first_name},\n\n{message}\n\nYou have been assigned a role in this transfer. Please log in to VOSS for details.\n\nThank you,\nThe VOSS Team",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

    print(f"Notifications sent for Transfer {instance.id}")

def connect_signals():
    """
    A function to connect all signals. Called in apps.py.
    """
    post_save.connect(transfer_notification_handler, sender=Transfer)
    print("Transfer notification signals connected.")
