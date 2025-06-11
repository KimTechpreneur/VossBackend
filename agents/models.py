from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class BaseOffice(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Agent(models.Model):
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('in_transit', 'In Transit'),
        ('offline', 'Offline'),
        ('on_leave', 'On Leave'),
        ('suspended', 'Suspended'),
    )

    EMPLOYMENT_TYPE_CHOICES = (
        ('Full Time', 'Full Time'),
        ('Part Time', 'Part Time'),
        ('Contract', 'Contract'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    agent_id = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    base_office = models.ForeignKey('offices.Office', on_delete=models.PROTECT, related_name='agents')
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES)
    joined_date = models.DateTimeField(default=timezone.now)
    last_activity = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.agent_id})"

    @property
    def deliveries_today(self):
        today = timezone.now().date()
        return self.deliveries.filter(
            date__date=today,
            status='completed'
        ).count()

    @property
    def success_rate(self):
        total_deliveries = self.deliveries.count()
        if total_deliveries == 0:
            return 0
        successful_deliveries = self.deliveries.filter(status='completed').count()
        return round((successful_deliveries / total_deliveries) * 100)

    def save(self, *args, **kwargs):
        if not self.agent_id:
            # Generate agent ID if not provided
            self.agent_id = f"AGT-{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['agent_id']

class AgentDelivery(models.Model):
    STATUS_CHOICES = (
        ('completed', 'Completed'),
        ('exception', 'Exception'),
    )

    CONFIRMATION_TYPE_CHOICES = (
        ('signature', 'Signature'),
        ('qr_scan', 'QR Scan'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='deliveries')
    delivery_id = models.CharField(max_length=50, unique=True)
    date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    from_location = models.CharField(max_length=255)
    to_location = models.CharField(max_length=255)
    time_taken = models.DurationField()
    confirmation_type = models.CharField(max_length=20, choices=CONFIRMATION_TYPE_CHOICES, null=True, blank=True)
    exception = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.delivery_id} - {self.status}"

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Agent Deliveries'
