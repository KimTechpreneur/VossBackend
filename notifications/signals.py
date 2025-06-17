from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

# It's common to have a central place for business logic that determines who should be notified.
# For this example, let's assume you have a 'transfers' app with a 'FolderTransfer' model.
# You would need to import the actual models involved in the events.
# from transfers.models import FolderTransfer 

from transfers.models import Transfer, RoutingStep, TransferComment
from folders.models import Folder
from .models import Notification, NotificationHistoryItem, User, NotificationTemplate
from .serializers import NotificationHistoryItemSerializer
from .utils import json_encode

# This is a placeholder for your actual FolderTransfer model. 
# You should remove this and import your real model.
class FolderTransfer:
    pass

def create_notification(user, title, message, notification_type, reference_id=None, priority='medium', channels=None):
    """Safely create and dispatch a notification. If *user* is None we silently
    abort to avoid database integrity errors (e.g. null user_id on
    NotificationHistoryItem)."""
    if user is None:
        # Nothing to do – we cannot associate a notification without a user.
        return
    """Helper function to create notifications across different channels"""
    # Normalise channels argument.
    if channels is None:
        channels = ['in_app', 'email']

    # Create in-app notification
    if 'in_app' in channels:
        history_item = NotificationHistoryItem.objects.create(
            user=user,
            title=title,
            message=message,
            type=notification_type,
            reference_id=reference_id
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

    # Toast (lightweight push) notification via WebSocket only.
    if 'toast' in channels:
        async_to_sync(channel_layer.group_send)(
            user_channel_group,
            {
                'type': 'send_toast',
                'title': title,
                'message': message,
            }
        )

    # Send email notification
    if 'email' in channels:
        try:
            template = NotificationTemplate.objects.filter(
                notification_type=notification_type,
                is_active=True
            ).first()

            if template:
                context = {
                    'user': user,
                    'title': title,
                    'message': message,
                    'reference_id': reference_id,
                    'timestamp': timezone.now()
                }
                
                subject = template.subject.format(**context)
                body = render_to_string(template.body, context)
                
                send_mail(
                    subject,
                    body,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                    html_message=body
                )
        except Exception as e:
            print(f"Failed to send email notification: {str(e)}")

@receiver(post_save, sender=Folder)
def folder_notification_handler(sender, instance, created, **kwargs):
    """Handle folder-related notifications"""
    if created:
        # Notify folder creator
        create_notification(
            user=instance.created_by,
            title="Folder Created",
            message=f"Folder '{instance.title}' has been created successfully.",
            notification_type='folder',
            reference_id=str(instance.id),
            channels=['in_app', 'toast']
        )
        
        # Notify watchers if any
        for watcher in instance.watchers.all():
            create_notification(
                user=watcher,
                title="New Folder Created",
                message=f"Folder '{instance.title}' has been created by {instance.created_by.get_full_name()}.",
                notification_type='folder',
                reference_id=str(instance.id),
                channels=['in_app']
            )

# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _office_admins(office):
    """Return a list of admin users for *office*.

    1. Tries the `admins` reverse-relation if present (ManyToMany / FK).
    2. Gracefully handles any object that provides `.all()` or is already
       an iterable of users.
    3. Falls back to the solitary `head_of_office` FK.
    """
    admins_attr = getattr(office, "admins", None)

    if admins_attr is not None:
        # It could be (a) a RelatedManager with .all(), (b) an actual list / queryset
        try:
            # RelatedManager / queryset path
            return [u for u in admins_attr.all() if u]
        except Exception:
            # Iterable path (list / set / tuple …) – ensure truthy users only
            try:
                return [u for u in admins_attr if u]
            except Exception:
                # Unexpected type → ignore
                pass

    head = getattr(office, "head_of_office", None)
    return [head] if head else []

# ---------------------------------------------------------------------------

@receiver(post_save, sender=Transfer)
def transfer_notification_handler(sender, instance, created, **kwargs):
    """Handle transfer-related notifications"""
    if created:
        # Notify creator (sender)
        create_notification(
            user=instance.created_by,
            title="Transfer Created",
            message=f"Transfer for folder '{instance.folder.title}' has been created.",
            notification_type='transfer',
            reference_id=str(instance.id),
            channels=['in_app', 'toast']
        )
        
        # Notify all users in routing steps
        for step in instance.routing_steps.all():
            # Notify the responsible user for this step
            create_notification(
                user=step.responsible_user,
                title="New Transfer Assignment",
                message=f"You have been assigned as responsible for a transfer of folder '{instance.folder.title}' from {instance.source_office.office_name}.",
                notification_type='transfer',
                reference_id=str(instance.id),
                channels=['in_app', 'email', 'toast']
            )

        # Notify assigned agent if any
        if instance.agent:
            create_notification(
                user=instance.agent.user,
                title="New Transfer Assignment",
                message=f"You have been assigned to handle the transfer of folder '{instance.folder.title}' from {instance.source_office.office_name} to {instance.destination_office.office_name}.",
                notification_type='transfer',
                reference_id=str(instance.id),
                channels=['in_app', 'email', 'toast']
            )
        
        # Notify receiving office admins
        for admin in _office_admins(instance.destination_office):
            create_notification(
                user=admin,
                title="New Transfer Received",
                message=f"New transfer from {instance.source_office.office_name} for folder '{instance.folder.title}'.",
                notification_type='transfer',
                reference_id=str(instance.id),
                channels=['in_app', 'email']
            )
    else:
        # Handle status changes
        if instance.status in ['completed', 'rejected', 'overdue']:
            # Collect all involved parties
            recipients = {
                instance.created_by,  # Sender
                *[step.responsible_user for step in instance.routing_steps.all()],  # All responsible users
                *_office_admins(instance.destination_office),  # Destination office admins
                *_office_admins(instance.source_office),  # Source office admins
            }
            
            # Add agent if assigned
            if instance.agent:
                recipients.add(instance.agent.user)
            
            status_message = {
                'completed': 'has been completed',
                'rejected': 'has been rejected',
                'overdue': 'is overdue'
            }[instance.status]
            
            for user in recipients:
                if user:  # Check if user exists
                    create_notification(
                        user=user,
                        title=f"Transfer {instance.status.title()}",
                        message=f"Transfer for folder '{instance.folder.title}' {status_message}. From: {instance.source_office.office_name} To: {instance.destination_office.office_name}",
                        notification_type='transfer',
                        reference_id=str(instance.id),
                        channels=['in_app', 'email']
                    )

@receiver(pre_save, sender=Transfer)
def transfer_cancellation_handler(sender, instance, **kwargs):
    """Handle transfer cancellation"""
    if instance.status == 'cancelled' and instance.pk:
        old_instance = Transfer.objects.get(pk=instance.pk)
        if old_instance.status != 'cancelled':
            # Notify all involved parties
            recipients = {
                instance.created_by,
                *_office_admins(instance.destination_office),
                *_office_admins(instance.source_office)
            }
            
            for user in recipients:
                create_notification(
                    user=user,
                    title="Transfer Cancelled",
                    message=f"Transfer for folder '{instance.folder.title}' has been cancelled.",
                    notification_type='transfer',
                    reference_id=str(instance.id),
                    priority='high',
                    channels=['in_app', 'email']
                )

@receiver(post_save, sender=TransferComment)
def comment_notification_handler(sender, instance, created, **kwargs):
    """Handle comment-related notifications"""
    if created:
        transfer = instance.transfer
        comment_type = instance.comment_type
        
        # Get all recipients who should be notified
        recipients = {
            transfer.created_by,  # Transfer creator
            instance.user,  # Comment author
            *[step.responsible_user for step in transfer.routing_steps.all()],  # All responsible users
            *_office_admins(transfer.destination_office),  # Destination office admins
            *_office_admins(transfer.source_office),  # Source office admins
        }
        
        # Add agent if assigned
        if transfer.agent:
            recipients.add(transfer.agent)
        
        # Add parent comment author if this is a reply
        if instance.parent_comment and instance.parent_comment.user:
            recipients.add(instance.parent_comment.user)
        
        # Remove the comment author from recipients
        recipients.discard(instance.user)
        
        # Prepare notification message based on comment type
        title_prefix = {
            'general': 'New Comment',
            'escalation': 'Transfer Escalation',
            'return': 'Transfer Return Request',
            'rejection': 'Transfer Rejection',
            'revision': 'Revision Request',
            'agent': 'Agent Note'
        }.get(comment_type, 'New Comment')
        
        message_prefix = {
            'general': 'commented on',
            'escalation': 'escalated',
            'return': 'requested return of',
            'rejection': 'rejected',
            'revision': 'requested revision for',
            'agent': 'added a note to'
        }.get(comment_type, 'commented on')
        
        # Send notifications to all recipients
        for user in recipients:
            if user:  # Check if user exists
                create_notification(
                    user=user,
                    title=f"{title_prefix} on Transfer",
                    message=f"{instance.user.get_full_name()} {message_prefix} transfer for folder '{transfer.folder.title}'.",
                    notification_type='transfer_comment',
                    reference_id=str(transfer.id),
                    channels=['in_app', 'email', 'toast']
                )

@receiver(pre_save, sender=Transfer)
def transfer_status_change_handler(sender, instance, **kwargs):
    """Handle notifications for transfer status changes"""
    try:
        # Get the old instance if it exists
        old_instance = Transfer.objects.get(pk=instance.pk)
        
        # If status has changed
        if old_instance.status != instance.status:
            # Handle delivery status
            if instance.status == 'delivered':
                # Notify source office users
                source_office_users = User.objects.filter(unit=instance.source_office.unit)
                for user in source_office_users:
                    create_notification(
                        user=user,
                        title=f'Transfer Delivered: {instance.id}',
                        message=f'Transfer {instance.id} has been delivered to {instance.destination_office.office_name}',
                        notification_type='transfer_delivery',
                        reference_id=str(instance.id),
                        channels=['in_app', 'email', 'toast']
                    )
                
                # Notify transfer creator
                if instance.created_by:
                    create_notification(
                        user=instance.created_by,
                        title=f'Transfer Delivered: {instance.id}',
                        message=f'Your transfer {instance.id} has been delivered to {instance.destination_office.office_name}',
                        notification_type='transfer_delivery',
                        reference_id=str(instance.id),
                        channels=['in_app', 'email', 'toast']
                    )

    except Transfer.DoesNotExist:
        # This is a new instance being created, ignore
        pass
    except Exception as e:
        print(f"Error in transfer_status_change_handler: {str(e)}")
        # Don't raise the exception to avoid blocking the save operation

def connect_signals():
    """Connect all notification signals"""
    post_save.connect(folder_notification_handler, sender=Folder)
    post_save.connect(transfer_notification_handler, sender=Transfer)
    pre_save.connect(transfer_cancellation_handler, sender=Transfer)
    post_save.connect(comment_notification_handler, sender=TransferComment)
    pre_save.connect(transfer_status_change_handler, sender=Transfer)
    print("Notification signals connected.")
