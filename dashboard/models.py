from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class DashboardMetrics(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    total_active_transfers = models.PositiveIntegerField(default=0)
    pending_approvals = models.PositiveIntegerField(default=0)
    overdue_transfers = models.PositiveIntegerField(default=0)
    agent_performance = models.CharField(max_length=50)  # e.g., "28 min"
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Dashboard Metrics'

    def __str__(self):
        return f"Dashboard Metrics - {self.created_at}"

class NotificationItem(models.Model):
    TYPE_CHOICES = (
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('info', 'Info'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.type}"

    class Meta:
        ordering = ['-timestamp']

class ActivityItem(models.Model):
    TYPE_CHOICES = (
        ('folder_created', 'Folder Created'),
        ('transfer_initiated', 'Transfer Initiated'),
        ('staff_approval', 'Staff Approval'),
        ('delivery_confirmation', 'Delivery Confirmation'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.type}"

    class Meta:
        ordering = ['-timestamp']

class OverdueUnit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    overdue_count = models.PositiveIntegerField(default=0)
    avg_days = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.overdue_count} overdue"

    class Meta:
        ordering = ['-overdue_count']

class AuditItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_items'
    )
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.action}"

    class Meta:
        ordering = ['-timestamp']

class HealthMetric(models.Model):
    COLOR_CHOICES = (
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('red', 'Red'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    value = models.CharField(max_length=50)  # e.g., "99.98%"
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    color = models.CharField(max_length=10, choices=COLOR_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.value}"

    class Meta:
        ordering = ['title']

class TransferVolumeData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    labels = models.JSONField(help_text="Array of unit names")
    datasets = models.JSONField(help_text="Array of datasets for transfers sent and received")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transfer Volume Data - {self.created_at}"

    class Meta:
        verbose_name_plural = 'Transfer Volume Data'

class ProcessingTimeData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    labels = models.JSONField(help_text="Array of time labels")
    datasets = models.JSONField(help_text="Array of datasets for processing time")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Processing Time Data - {self.created_at}"

    class Meta:
        verbose_name_plural = 'Processing Time Data'

class AgentSuccessData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    labels = models.JSONField(help_text="Array of success categories")
    datasets = models.JSONField(help_text="Array of datasets for success rates")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Agent Success Data - {self.created_at}"

    class Meta:
        verbose_name_plural = 'Agent Success Data'
