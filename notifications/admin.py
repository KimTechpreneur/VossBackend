from django.contrib import admin
from .models import (
    NotificationPreference, NotificationChannel, UserNotificationPreference,
    UserNotificationChannel, PersonalNotificationSettings, NotificationHistoryItem,
    SystemNotificationRule, NotificationTemplate, Notification, NotificationLog
)

@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'notification_type', 'is_active', 'created_at')
    list_filter = ('notification_type', 'is_active')
    search_fields = ('name', 'subject', 'body')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'notification_type', 'is_active')
        }),
        ('Email Content', {
            'fields': ('subject', 'body'),
            'description': 'Use {variable_name} for dynamic content. Available variables: user, title, message, reference_id, timestamp'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_enabled', 'created_at')
    list_filter = ('is_enabled',)
    search_fields = ('title', 'description')

@admin.register(NotificationChannel)
class NotificationChannelAdmin(admin.ModelAdmin):
    list_display = ('label', 'is_enabled', 'created_at')
    list_filter = ('is_enabled',)

class UserNotificationPreferenceInline(admin.TabularInline):
    model = UserNotificationPreference
    extra = 1

class UserNotificationChannelInline(admin.TabularInline):
    model = UserNotificationChannel
    extra = 1

@admin.register(PersonalNotificationSettings)
class PersonalNotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'digest_frequency', 'created_at')
    list_filter = ('digest_frequency',)
    search_fields = ('user__email', 'user__username')
    inlines = [UserNotificationPreferenceInline, UserNotificationChannelInline]

@admin.register(NotificationHistoryItem)
class NotificationHistoryItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'type', 'status', 'created_at')
    list_filter = ('type', 'status')
    search_fields = ('title', 'message', 'user__email')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(SystemNotificationRule)
class SystemNotificationRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'trigger_type', 'is_enabled', 'created_at')
    list_filter = ('trigger_type', 'is_enabled')
    search_fields = ('name', 'message_template')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('notification_type', 'recipient', 'subject', 'priority', 'is_read', 'created_at')
    list_filter = ('notification_type', 'priority', 'is_read')
    search_fields = ('subject', 'message', 'recipient__email')
    readonly_fields = ('created_at', 'updated_at', 'read_at')

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('notification', 'delivery_method', 'status', 'created_at')
    list_filter = ('delivery_method', 'status')
    search_fields = ('notification__subject', 'error_message')
    readonly_fields = ('created_at',)

# Add default email templates
def create_default_templates():
    templates = [
        {
            'name': 'Transfer Created',
            'notification_type': 'transfer',
            'subject': '[VOSS] New Transfer: {title}',
            'body': '''
                <h2>New Transfer Created</h2>
                <p>Hello {user.first_name},</p>
                <p>A new transfer has been created:</p>
                <ul>
                    <li><strong>Title:</strong> {title}</li>
                    <li><strong>Message:</strong> {message}</li>
                    <li><strong>Reference ID:</strong> {reference_id}</li>
                </ul>
                <p><a href="{settings.FRONTEND_URL}/transfers/{reference_id}">View Transfer</a></p>
                <p>Thank you,<br>The VOSS Team</p>
            ''',
            'is_active': True
        },
        {
            'name': 'Transfer Status Update',
            'notification_type': 'transfer',
            'subject': '[VOSS] Transfer Update: {title}',
            'body': '''
                <h2>Transfer Status Update</h2>
                <p>Hello {user.first_name},</p>
                <p>Your transfer has been updated:</p>
                <ul>
                    <li><strong>Title:</strong> {title}</li>
                    <li><strong>Status:</strong> {message}</li>
                    <li><strong>Reference ID:</strong> {reference_id}</li>
                </ul>
                <p><a href="{settings.FRONTEND_URL}/transfers/{reference_id}">View Transfer</a></p>
                <p>Thank you,<br>The VOSS Team</p>
            ''',
            'is_active': True
        },
        {
            'name': 'Folder Created',
            'notification_type': 'folder',
            'subject': '[VOSS] New Folder: {title}',
            'body': '''
                <h2>New Folder Created</h2>
                <p>Hello {user.first_name},</p>
                <p>A new folder has been created:</p>
                <ul>
                    <li><strong>Title:</strong> {title}</li>
                    <li><strong>Message:</strong> {message}</li>
                    <li><strong>Reference ID:</strong> {reference_id}</li>
                </ul>
                <p><a href="{settings.FRONTEND_URL}/folders/{reference_id}">View Folder</a></p>
                <p>Thank you,<br>The VOSS Team</p>
            ''',
            'is_active': True
        }
    ]

    for template_data in templates:
        NotificationTemplate.objects.get_or_create(
            name=template_data['name'],
            defaults=template_data
        )

# Create default templates when Django starts
from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_default_templates_handler(sender, **kwargs):
    create_default_templates()

class NotificationsConfig(AppConfig):
    name = 'notifications'

    def ready(self):
        post_migrate.connect(create_default_templates_handler, sender=self)
