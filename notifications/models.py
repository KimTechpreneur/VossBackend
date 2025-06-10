from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()

class NotificationPreference(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    description = models.TextField()
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']

class NotificationChannel(models.Model):
    CHANNEL_CHOICES = (
        ('in_app', 'In-App'),
        ('email', 'Email'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=50)
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.label

    class Meta:
        ordering = ['label']

class PersonalNotificationSettings(models.Model):
    DIGEST_FREQUENCY_CHOICES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('none', 'None'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_settings'
    )
    preferences = models.ManyToManyField(NotificationPreference, through='UserNotificationPreference')
    channels = models.ManyToManyField(NotificationChannel, through='UserNotificationChannel')
    digest_frequency = models.CharField(
        max_length=10,
        choices=DIGEST_FREQUENCY_CHOICES,
        default='none'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Notification settings for {self.user}"

class UserNotificationPreference(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_settings = models.ForeignKey(PersonalNotificationSettings, on_delete=models.CASCADE)
    preference = models.ForeignKey(NotificationPreference, on_delete=models.CASCADE)
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user_settings', 'preference']

class UserNotificationChannel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_settings = models.ForeignKey(PersonalNotificationSettings, on_delete=models.CASCADE)
    channel = models.ForeignKey(NotificationChannel, on_delete=models.CASCADE)
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user_settings', 'channel']

class NotificationHistoryItem(models.Model):
    TYPE_CHOICES = (
        ('system', 'System'),
        ('transfer', 'Transfer'),
        ('escalation', 'Escalation'),
        ('agent', 'Agent'),
        ('task', 'Task'),
    )

    STATUS_CHOICES = (
        ('read', 'Read'),
        ('unread', 'Unread'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_history'
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unread')
    reference_id = models.CharField(max_length=50, null=True, blank=True)
    file_link = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.user}"

    class Meta:
        ordering = ['-created_at']

class SystemNotificationRule(models.Model):
    TRIGGER_TYPE_CHOICES = (
        ('file_inactive', 'File Inactive'),
        ('agent_delay', 'Agent Delay'),
        ('file_rejected_returned', 'File Rejected/Returned'),
        ('no_action_taken', 'No Action Taken'),
        ('weekly_digest', 'Weekly Digest'),
    )

    RECIPIENT_CHOICES = (
        ('file_sender', 'File Sender'),
        ('file_recipient', 'File Recipient'),
        ('office_admin', 'Office Admin'),
        ('agent_supervisor', 'Agent Supervisor'),
        ('office_heads', 'Office Heads'),
        ('global_admin', 'Global Admin'),
    )

    CHANNEL_CHOICES = (
        ('in_app', 'In-App'),
        ('email', 'Email'),
    )

    THRESHOLD_UNIT_CHOICES = (
        ('minutes', 'Minutes'),
        ('hours', 'Hours'),
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('instant', 'Instant'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    trigger_type = models.CharField(max_length=50, choices=TRIGGER_TYPE_CHOICES)
    recipients = models.JSONField(help_text="Array of recipient roles/types")
    threshold_value = models.PositiveIntegerField(null=True, blank=True)
    threshold_unit = models.CharField(
        max_length=10,
        choices=THRESHOLD_UNIT_CHOICES,
        null=True,
        blank=True
    )
    notification_channels = models.JSONField(help_text="Array of notification channels")
    message_template = models.TextField(null=True, blank=True)
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class NotificationTemplate(models.Model):
    """Template for system notifications."""
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    notification_type = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Notification(models.Model):
    """System notification sent to users."""
    NOTIFICATION_TYPES = [
        ('system', 'System'),
        ('transfer', 'Transfer'),
        ('folder', 'Folder'),
        ('office', 'Office'),
        ('user', 'User'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    template = models.ForeignKey(NotificationTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type} - {self.subject}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

class NotificationLog(models.Model):
    """Log of notification delivery attempts."""
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='delivery_logs')
    delivery_method = models.CharField(max_length=20)  # email, in_app, sms
    status = models.CharField(max_length=20)  # sent, failed, pending
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.notification} - {self.delivery_method} - {self.status}"
