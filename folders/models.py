from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid
import os

class FolderService(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class FolderCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Folder Categories'

class RetentionClass(models.Model):
    CLASS_CHOICES = (
        ('a', 'Class A'),
        ('b', 'Class B'),
        ('c', 'Class C'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=1, choices=CLASS_CHOICES, unique=True)
    description = models.TextField()
    retention_period = models.DurationField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Class {self.get_name_display()}"

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Retention Classes'

class Folder(models.Model):
    STATUS_CHOICES = (
        ('Not Started', 'Not Started'),
        ('In Transit', 'In Transit'),
        ('Delivered', 'Delivered'),
        ('Overdue', 'Overdue'),
        ('Pending', 'Pending'),
        ('Cancelled', 'Cancelled'),
    )
    
    PRIORITY_CHOICES = (
        ('urgent', 'Urgent'),
        ('normal', 'Normal'),
        ('low', 'Low'),
        ('confidential', 'Confidential'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    folder_id = models.CharField(max_length=50, unique=True)  # e.g., VOSS-2023-0047
    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not Started')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    service = models.ForeignKey(FolderService, on_delete=models.SET_NULL, null=True, blank=True, related_name='folders')
    category = models.ForeignKey(FolderCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='folders')
    retention_class = models.ForeignKey(RetentionClass, on_delete=models.SET_NULL, null=True, blank=True, related_name='folders')
    source_office = models.ForeignKey(
        'offices.Office',
        on_delete=models.SET_NULL,
        null=True,
        related_name='source_folders'
    )
    destination_office = models.ForeignKey(
        'offices.Office',
        on_delete=models.SET_NULL,
        null=True,
        related_name='destination_folders'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_folders'
    )
    assigned_agent = models.ForeignKey(
        'agents.Agent',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_folders'
    )
    requires_signature = models.BooleanField(default=False)
    is_signed = models.BooleanField(default=False)
    forwarding_comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    current_office = models.ForeignKey(
        'offices.Office',
        on_delete=models.SET_NULL,
        null=True,
        related_name='current_folders'
    )
    last_modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='modified_folders'
    )
    auto_generate_file_numbers = models.BooleanField(default=True)
    tags = models.JSONField(default=list, blank=True)
    notifications = models.JSONField(
        default=dict,
        blank=True,
        help_text="Notification preferences: {'inApp': bool, 'email': bool, 'sms': bool}"
    )
    collected_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    collected_at = models.DateTimeField(null=True)

    def __str__(self):
        return f"{self.folder_id} - {self.title}"

    @property
    def is_overdue(self):
        if self.due_date and self.status not in ['Delivered', 'Cancelled']:
            return timezone.now() > self.due_date
        return False

    @property
    def file_count(self):
        return self.files.count()

    @property
    def current_location(self):
        return self.current_office.office_name if self.current_office else 'Unknown'

    @property
    def status_flags(self):
        return {
            'inTransit': self.status == 'In Transit',
            'overdue': self.is_overdue,
            'requiresSignature': self.requires_signature,
            'isSigned': self.is_signed
        }

    class Meta:
        ordering = ['-created_at']

def get_file_path(instance, filename):
    # Generate a unique path for the file
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('folder_files', str(instance.folder.id), filename)

class FolderFile(models.Model):
    folder = models.ForeignKey('Folder', on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to=get_file_path)
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100)
    file_size = models.BigIntegerField()  # Size in bytes
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deleted_folder_files'
    )
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    archived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='archived_folder_files'
    )

    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['folder', 'uploaded_at']),
            models.Index(fields=['file_type']),
        ]

    def __str__(self):
        return f"{self.original_filename} ({self.folder.name})"

    def delete(self, *args, **kwargs):
        # Soft delete
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self, *args, **kwargs):
        # Actually delete the file and record
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)

class FolderTransfer(models.Model):
    STATUS_CHOICES = (
        ('Not Started', 'Not Started'),
        ('Pending', 'Pending'),
        ('In Transit', 'In Transit'),
        ('Delivered', 'Delivered'),
        ('Returned', 'Returned'),
        ('Cancelled', 'Cancelled'),
        ('Overdue', 'Overdue'),
        ('Draft', 'Draft'),
        ('Submitted', 'Submitted'),
    )

    DELIVERY_METHOD_CHOICES = (
        ('self', 'Self Delivery'),
        ('agent', 'Agent Delivery'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='folder_transfers')
    from_office = models.ForeignKey(
        'offices.Office',
        on_delete=models.SET_NULL,
        null=True,
        related_name='folder_outgoing_transfers'
    )
    to_office = models.ForeignKey(
        'offices.Office',
        on_delete=models.SET_NULL,
        null=True,
        related_name='folder_incoming_transfers'
    )
    agent = models.ForeignKey(
        'agents.Agent',
        on_delete=models.SET_NULL,
        null=True,
        related_name='folder_transfers'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Not Started')
    transfer_date = models.DateTimeField()
    delivered_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmation_type = models.CharField(
        max_length=20,
        choices=(
            ('signature', 'Signature'),
            ('qr_scan', 'QR Scan'),
        ),
        null=True,
        blank=True
    )
    time_taken = models.DurationField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_folder_transfers'
    )
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='received_transfers'
    )
    delivery_method = models.CharField(
        max_length=10,
        choices=DELIVERY_METHOD_CHOICES,
        default='agent'
    )
    agent_notes = models.TextField(null=True, blank=True)
    priority = models.CharField(
        max_length=20,
        choices=Folder.PRIORITY_CHOICES,
        default='normal'
    )
    tags = models.JSONField(default=list, blank=True)
    notifications = models.JSONField(
        default=dict,
        blank=True,
        help_text="Notification preferences: {'inApp': bool, 'email': bool, 'sms': bool}"
    )
    submitted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Transfer {self.id} - {self.folder.folder_id}"

    class Meta:
        ordering = ['-transfer_date']

class FolderSignature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='signatures')
    signed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='folder_signatures'
    )
    signature_type = models.CharField(max_length=50)  # e.g., 'digital', 'physical'
    signature_data = models.TextField()  # Store signature data or reference
    signed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='verified_signatures'
    )

    def __str__(self):
        return f"Signature for {self.folder.folder_id} by {self.signed_by}"

    class Meta:
        ordering = ['-signed_at']

class FolderWorkflowStep(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in-progress', 'In Progress'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='workflow_steps')
    office = models.ForeignKey(
        'offices.Office',
        on_delete=models.SET_NULL,
        null=True,
        related_name='workflow_steps'
    )
    step_number = models.PositiveIntegerField()
    total_steps = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='completed_workflow_steps'
    )
    is_required = models.BooleanField(default=True)
    estimated_duration = models.DurationField(null=True, blank=True)
    actual_duration = models.DurationField(null=True, blank=True)
    responsible_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='responsible_workflow_steps'
    )
    due_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Step {self.step_number} of {self.total_steps} for {self.folder.folder_id}"

    class Meta:
        ordering = ['step_number']
        unique_together = ['folder', 'step_number']

class FolderComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='folder_comments'
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_internal = models.BooleanField(default=False)  # For internal notes vs. visible comments
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    def __str__(self):
        return f"Comment by {self.user} on {self.folder.folder_id}"

    class Meta:
        ordering = ['-created_at']
