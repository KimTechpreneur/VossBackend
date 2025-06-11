from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class Office(models.Model):
    OFFICE_TYPES = (
        ('Faculty-Level', 'Faculty-Level'),
        ('Departmental', 'Departmental'),
        ('Support Office', 'Support Office'),
        ('Record Storage', 'Record Storage'),
    )
    
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    office_name = models.CharField(max_length=255)
    office_type = models.CharField(max_length=50, choices=OFFICE_TYPES)
    office_code = models.CharField(max_length=50, unique=True)
    head_of_office = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_offices'
    )
    staff_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    location = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    last_updated_date = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='updated_offices'
    )

    def __str__(self):
        return f"{self.office_name} ({self.office_code})"

    @property
    def ongoing_transfers(self):
        return self.transfers.filter(status__in=['In Transit', 'Pending']).count()

    class Meta:
        ordering = ['office_name']

class OfficeFolder(models.Model):
    STATUS_CHOICES = (
        ('Completed', 'Completed'),
        ('In Progress', 'In Progress'),
        ('Pending', 'Pending'),
        ('Archived', 'Archived'),
        ('Overdue', 'Overdue'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name='folders')
    folder_id = models.CharField(max_length=50, unique=True)  # e.g., VOSS-2023-0047
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    date = models.DateTimeField()
    initiated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.folder_id} - {self.title}"

    class Meta:
        ordering = ['-date']

class OfficeTransfer(models.Model):
    STATUS_CHOICES = (
        ('Received', 'Received'),
        ('Delivered', 'Delivered'),
        ('In Transit', 'In Transit'),
        ('Pending', 'Pending'),
        ('Overdue', 'Overdue'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    office = models.ForeignKey(Office, on_delete=models.CASCADE, related_name='transfers')
    transfer_id = models.CharField(max_length=50, unique=True)  # e.g., VOSS-2023-0051
    date = models.DateTimeField()
    party = models.CharField(max_length=255)  # e.g., "From: Dean's Office" or "To: Faculty Archives"
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    subject = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.transfer_id} - {self.subject}"

    class Meta:
        ordering = ['-date']
