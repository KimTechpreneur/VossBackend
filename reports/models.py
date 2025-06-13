from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class ReportTemplate(models.Model):
    """Template for generating reports"""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    query = models.TextField(help_text=_("SQL query or data source configuration"))
    parameters = models.JSONField(default=dict, help_text=_("Template parameters"))
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class Report(models.Model):
    """Generated report instance"""
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
    ]

    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='reports', null=True, blank=True)
    name = models.CharField(max_length=255)
    parameters = models.JSONField(default=dict, help_text=_("Report parameters"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result = models.JSONField(null=True, blank=True, help_text=_("Report results"))
    file = models.FileField(upload_to='reports/', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='generated_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
