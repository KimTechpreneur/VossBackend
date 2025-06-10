from django.contrib import admin
from .models import (
    NotificationPreference, NotificationChannel, UserNotificationPreference,
    UserNotificationChannel, PersonalNotificationSettings, NotificationHistoryItem,
    SystemNotificationRule
)

@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'updated_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('name',)}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(NotificationChannel)
class NotificationChannelAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'updated_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('name',)}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(UserNotificationPreference)
class UserNotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'updated_at')
    search_fields = ('user__email',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('user',)}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(UserNotificationChannel)
class UserNotificationChannelAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'updated_at')
    search_fields = ('user__email',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('user',)}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(PersonalNotificationSettings)
class PersonalNotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'updated_at')
    search_fields = ('notification_type',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('notification_type',)}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(NotificationHistoryItem)
class NotificationHistoryItemAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'updated_at')
    search_fields = ('notification_type',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('notification_type',)}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(SystemNotificationRule)
class SystemNotificationRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'trigger_type', 'is_enabled', 'created_at', 'updated_at')
    list_filter = ('trigger_type', 'is_enabled')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)
    
    fieldsets = (
        (None, {'fields': ('name', 'trigger_type', 'is_enabled')}),
        ('Configuration', {'fields': ('conditions', 'actions', 'description')}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )
