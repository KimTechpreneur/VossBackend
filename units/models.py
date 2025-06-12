from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class Unit(models.Model):
    UNIT_TYPE_CHOICES = (
        ('central_admin', 'Central Administration'),
        ('academic_faculty', 'Academic Faculty'),
        ('support_service', 'Support Service'),
        ('health_services', 'Health Services'),
        ('finance_division', 'Finance Division'),
        ('audit_unit', 'Audit Unit'),
        ('library', 'Library'),
        ('student_affairs', 'Student Affairs'),
        ('human_resources', 'Human Resources'),
        ('it_services', 'IT Services'),
        ('security', 'Security'),
        ('maintenance', 'Maintenance'),
        ('other', 'Other'),
    )

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    unit_type = models.CharField(max_length=50, choices=UNIT_TYPE_CHOICES)
    unit_code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    head_of_unit = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='headed_units'
    )
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    description = models.TextField(null=True, blank=True)
    staff_count = models.IntegerField(default=0)
    ongoing_transfers = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.unit_code})"

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['unit_type']),
            models.Index(fields=['status']),
            models.Index(fields=['unit_code']),
        ]

    def update_staff_count(self):
        """Update the staff count for this unit."""
        from users.models import User
        self.staff_count = User.objects.filter(unit=self).count()
        self.save(update_fields=['staff_count'])

    def update_ongoing_transfers(self):
        """Update the count of ongoing transfers for this unit."""
        from folders.models import FolderTransfer
        self.ongoing_transfers = FolderTransfer.objects.filter(
            current_office=self,
            status__in=['in_transit', 'awaiting_pickup']
        ).count()
        self.save(update_fields=['ongoing_transfers'])
