from django.contrib import admin
from .models import Agent, AgentDelivery

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'base_office', 'employment_type', 'joined_date', 'last_activity', 'deliveries_today', 'success_rate']
    list_filter = ['status', 'base_office', 'employment_type']
    search_fields = ['user__full_name', 'user__email', 'agent_id', 'base_office__name']
    ordering = ['-last_activity']
    
    fieldsets = (
        (None, {'fields': ('user', 'agent_id', 'status')}),
        ('Vehicle Information', {'fields': ('vehicle_number', 'vehicle_type', 'license_number', 'license_expiry', 'insurance_number', 'insurance_expiry')}),
        ('Additional Info', {'fields': ('notes',)}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(AgentDelivery)
class AgentDeliveryAdmin(admin.ModelAdmin):
    list_display = ['id', 'agent', 'status', 'date', 'time_taken', 'confirmation_type']
    list_filter = ['status', 'confirmation_type']
    search_fields = ['delivery_id', 'from_location', 'to_location']
    ordering = ['-date']
    
    fieldsets = (
        (None, {'fields': ('agent', 'delivery_id', 'status')}),
        ('Location Info', {'fields': ('pickup_location', 'delivery_location')}),
        ('Timing', {'fields': ('pickup_time', 'delivery_time')}),
        ('Additional Info', {'fields': ('notes',)}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )
