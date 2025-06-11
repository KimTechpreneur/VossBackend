from django.contrib import admin
from .models import Office, OfficeFolder, OfficeTransfer

@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = [
        'office_name', 'office_code', 'office_type', 
        'head_of_office', 'staff_count', 'status', 
        'location', 'created_date'
    ]
    list_filter = ['office_type', 'status', 'created_date']
    search_fields = ['office_name', 'office_code', 'head_of_office__full_name']
    readonly_fields = ['created_date', 'last_updated_date', 'ongoing_transfers']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('office_name', 'office_code', 'office_type', 'status')
        }),
        ('Management', {
            'fields': ('head_of_office', 'staff_count')
        }),
        ('Details', {
            'fields': ('location', 'description')
        }),
        ('Metadata', {
            'fields': ('created_date', 'last_updated_date', 'updated_by', 'ongoing_transfers'),
            'classes': ('collapse',)
        }),
    )

@admin.register(OfficeFolder)
class OfficeFolderAdmin(admin.ModelAdmin):
    list_display = ['folder_id', 'title', 'office', 'status', 'date', 'initiated_by']
    list_filter = ['status', 'office', 'date']
    search_fields = ['folder_id', 'title', 'office__office_name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(OfficeTransfer)
class OfficeTransferAdmin(admin.ModelAdmin):
    list_display = ['transfer_id', 'subject', 'office', 'party', 'status', 'date']
    list_filter = ['status', 'office', 'date']
    search_fields = ['transfer_id', 'subject', 'office__office_name', 'party']
    readonly_fields = ['created_at', 'updated_at']
