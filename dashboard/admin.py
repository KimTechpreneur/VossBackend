from django.contrib import admin
from .models import (
    DashboardMetrics, NotificationItem, ActivityItem, OverdueUnit,
    AuditItem, HealthMetric, TransferVolumeData, ProcessingTimeData,
    AgentSuccessData
)

@admin.register(DashboardMetrics)
class DashboardMetricsAdmin(admin.ModelAdmin):
    list_display = ('total_active_transfers', 'pending_approvals', 'overdue_transfers', 'agent_performance', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('total_active_transfers', 'pending_approvals', 'overdue_transfers', 'agent_performance')}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(NotificationItem)
class NotificationItemAdmin(admin.ModelAdmin):
    list_display = ('type', 'title', 'message', 'timestamp', 'created_at', 'updated_at')
    list_filter = ('type',)
    search_fields = ('title', 'message')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-timestamp',)
    
    fieldsets = (
        (None, {'fields': ('type', 'title', 'message')}),
        ('Important dates', {'fields': ('timestamp', 'created_at', 'updated_at')}),
    )

@admin.register(ActivityItem)
class ActivityItemAdmin(admin.ModelAdmin):
    list_display = ('type', 'title', 'description', 'timestamp', 'created_at', 'updated_at')
    list_filter = ('type',)
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-timestamp',)
    
    fieldsets = (
        (None, {'fields': ('type', 'title', 'description')}),
        ('Important dates', {'fields': ('timestamp', 'created_at', 'updated_at')}),
    )

@admin.register(OverdueUnit)
class OverdueUnitAdmin(admin.ModelAdmin):
    list_display = ('name', 'overdue_count', 'avg_days', 'created_at', 'updated_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-overdue_count',)
    
    fieldsets = (
        (None, {'fields': ('name', 'overdue_count', 'avg_days')}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(AuditItem)
class AuditItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp', 'created_at', 'updated_at')
    search_fields = ('user__email', 'action')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-timestamp',)
    
    fieldsets = (
        (None, {'fields': ('user', 'action')}),
        ('Important dates', {'fields': ('timestamp', 'created_at', 'updated_at')}),
    )

@admin.register(HealthMetric)
class HealthMetricAdmin(admin.ModelAdmin):
    list_display = ('title', 'value', 'percentage', 'color', 'created_at', 'updated_at')
    list_filter = ('color',)
    search_fields = ('title',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('title',)
    
    fieldsets = (
        (None, {'fields': ('title', 'value', 'percentage', 'color')}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(TransferVolumeData)
class TransferVolumeDataAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('labels', 'datasets')}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(ProcessingTimeData)
class ProcessingTimeDataAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('labels', 'datasets')}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(AgentSuccessData)
class AgentSuccessDataAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('labels', 'datasets')}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )
