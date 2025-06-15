from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import uuid
from django.conf import settings

User = get_user_model()

class RoutingStep(models.Model):
    """Represents a step in the transfer's routing process."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
    ]

    transfer = models.ForeignKey('Transfer', on_delete=models.CASCADE, related_name='routing_steps')
    step_number = models.PositiveIntegerField()
    unit_office = models.ForeignKey('offices.Office', on_delete=models.PROTECT, related_name='routing_steps')
    responsible_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='routing_steps')
    due_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    completed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='completed_steps'
    )

    class Meta:
        ordering = ['step_number']
        unique_together = ['transfer', 'step_number']

    def __str__(self):
        return f"Step {self.step_number} - {self.unit_office.name}"

class Transfer(models.Model):
    """Core model representing a transfer."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('recalled', 'Recalled'),
        ('escalated', 'Escalated'),
        ('returned', 'Returned'),
        ('return_approved', 'Return Approved'),
        ('return_rejected', 'Return Rejected'),
        ('revision_requested', 'Revision Requested'),
        ('force_returned', 'Force Returned'),
    ]

    DELIVERY_METHOD_CHOICES = [
        ('self', 'Self Delivery'),
        ('agent', 'Agent Delivery'),
    ]

    PRIORITY_CHOICES = [
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
        ('immediate', 'Immediate'),
    ]

    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    folder = models.ForeignKey('folders.Folder', on_delete=models.PROTECT, related_name='transfers')
    source_office = models.ForeignKey(
        'offices.Office', 
        on_delete=models.PROTECT, 
        related_name='outgoing_transfers'
    )
    destination_office = models.ForeignKey(
        'offices.Office', 
        on_delete=models.PROTECT, 
        related_name='incoming_transfers'
    )

    # Delivery Information
    delivery_method = models.CharField(max_length=10, choices=DELIVERY_METHOD_CHOICES)
    agent = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_transfers'
    )
    agent_notes = models.TextField(blank=True)

    # Transfer Details
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    tags = models.JSONField(default=list)
    notifications = models.JSONField(default=dict)  # {inApp: bool, email: bool, sms: bool}
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='created_transfers'
    )
    submitted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)

    # Return Information
    return_reason = models.TextField(blank=True)
    return_notes = models.TextField(blank=True)
    returned_at = models.DateTimeField(null=True, blank=True)
    returned_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='returned_transfers'
    )

    # History tracking
    history = models.JSONField(default=list)  # List of status changes and actions

    # Collection Information
    collected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    collected_at = models.DateTimeField(null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.id} - {self.folder.title}"

    def save(self, *args, **kwargs):
        # Track status changes in history
        if not self._state.adding:
            try:
                old_instance = Transfer.objects.get(pk=self.pk)
                if old_instance.status != self.status:
                    self.history.append({
                        'timestamp': timezone.now().isoformat(),
                        'old_status': old_instance.status,
                        'new_status': self.status,
                        'changed_by': self._current_user.id if hasattr(self, '_current_user') else None
                    })
            except Transfer.DoesNotExist:
                # This can happen in some edge cases, so we just skip history tracking
                pass
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        if self.due_date and self.status in ['in_transit', 'submitted']:
            return timezone.now() > self.due_date
        return False

    @property
    def current_step(self):
        return self.routing_steps.filter(status__in=['pending', 'in_progress']).first()

    @property
    def next_step(self):
        current_step = self.current_step
        if current_step:
            return self.routing_steps.filter(step_number__gt=current_step.step_number).first()
        return None

    def can_be_recalled(self):
        return self.status in ['submitted', 'in_transit']

    def can_be_escalated(self):
        return self.is_overdue and self.status in ['in_transit', 'submitted']

    def can_be_returned(self):
        return self.status in ['in_transit', 'submitted']

    def can_be_approved(self):
        return self.status == 'returned'

    def can_be_rejected(self):
        return self.status == 'returned'

class TransferComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transfer = models.ForeignKey(Transfer, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='transfer_comments'
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
    comment_type = models.CharField(
        max_length=20,
        choices=(
            ('general', 'General Comment'),
            ('escalation', 'Escalation Note'),
            ('return', 'Return Note'),
            ('rejection', 'Rejection Note'),
            ('revision', 'Revision Request'),
            ('agent', 'Agent Note'),
        ),
        default='general'
    )

    def __str__(self):
        return f"Comment by {self.user} on Transfer {self.transfer.id}"

    class Meta:
        ordering = ['-created_at']
