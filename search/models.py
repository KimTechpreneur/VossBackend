from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class SearchResultItem(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
        ('in_review', 'In Review'),
        ('awaiting_pickup', 'Awaiting Pickup'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    folder = models.ForeignKey(
        'folders.Folder',
        on_delete=models.CASCADE,
        related_name='search_results'
    )
    file = models.ForeignKey(
        'folders.FolderFile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='search_results'
    )
    current_office = models.ForeignKey(
        'offices.Office',
        on_delete=models.SET_NULL,
        null=True,
        related_name='search_results'
    )
    current_status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.file:
            return f"{self.folder.folder_id} - {self.file.original_filename}"
        return f"{self.folder.folder_id}"

    class Meta:
        ordering = ['-last_activity']

class SearchFilters(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    search_term = models.CharField(max_length=255)
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    destination_unit = models.ForeignKey(
        'offices.Office',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='destination_search_filters'
    )
    office = models.ForeignKey(
        'offices.Office',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='office_search_filters'
    )
    file_type = models.CharField(max_length=50, null=True, blank=True)
    current_status = models.CharField(
        max_length=20,
        choices=SearchResultItem.STATUS_CHOICES,
        null=True,
        blank=True
    )
    agent = models.ForeignKey(
        'agents.Agent',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='search_filters'
    )
    treatment_folder_id = models.CharField(max_length=50, null=True, blank=True)
    specific_file_id = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Search Filters - {self.search_term}"

    class Meta:
        verbose_name_plural = 'Search Filters'

class TransferPathStep(models.Model):
    STATUS_CHOICES = (
        ('received', 'Received'),
        ('processed', 'Processed'),
        ('sent', 'Sent'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    folder = models.ForeignKey(
        'folders.Folder',
        on_delete=models.CASCADE,
        related_name='transfer_path_steps'
    )
    office = models.ForeignKey(
        'offices.Office',
        on_delete=models.SET_NULL,
        null=True,
        related_name='transfer_path_steps'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.folder.folder_id} - {self.office} - {self.status}"

    class Meta:
        ordering = ['timestamp']

class AgentActivity(models.Model):
    STATUS_CHOICES = (
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transfer = models.ForeignKey(
        'folders.FolderTransfer',
        on_delete=models.CASCADE,
        related_name='agent_activities'
    )
    agent = models.ForeignKey(
        'agents.Agent',
        on_delete=models.SET_NULL,
        null=True,
        related_name='activities'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.agent} - {self.status} - {self.transfer}"

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Agent Activities'

class TransferTrail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    folder = models.OneToOneField(
        'folders.Folder',
        on_delete=models.CASCADE,
        related_name='transfer_trail'
    )
    current_position = models.JSONField(
        help_text="Current position information: {'office': str, 'status': str}"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transfer Trail - {self.folder.folder_id}"

    class Meta:
        ordering = ['-updated_at']

class SearchHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='search_history'
    )
    search_term = models.CharField(max_length=255)
    filters = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.search_term}"

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Search History'

class SearchResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    search_history = models.ForeignKey(
        SearchHistory,
        on_delete=models.CASCADE,
        related_name='results'
    )
    result_type = models.CharField(max_length=50)
    result_id = models.UUIDField()
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.search_history.search_term} - {self.result_type}"

    class Meta:
        ordering = ['-created_at']
