from django.contrib import admin
from .models import (
    InternalOffice, OfficeFolder, OfficeTransfer,
    OfficeStaffMember
)

@admin.register(InternalOffice)
class InternalOfficeAdmin(admin.ModelAdmin):
    list_display = ('office_name', 'office_type', 'office_code', 'status', 'created_date', 'last_updated_date')
    list_filter = ('office_type', 'status')
    search_fields = ('office_name', 'office_code', 'description')
    readonly_fields = ('created_date', 'last_updated_date')
    ordering = ('office_name',)
    
    fieldsets = (
        (None, {'fields': ('office_name', 'office_type', 'office_code', 'head_of_office', 'staff_count', 'status', 'location', 'description')}),
        ('Important dates', {'fields': ('created_date', 'last_updated_date', 'updated_by')}),
    )

@admin.register(OfficeFolder)
class OfficeFolderAdmin(admin.ModelAdmin):
    list_display = ('folder_id', 'title', 'status', 'date', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('folder_id', 'title')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-date',)
    
    fieldsets = (
        (None, {'fields': ('office', 'folder_id', 'title', 'status', 'date', 'initiated_by')}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(OfficeTransfer)
class OfficeTransferAdmin(admin.ModelAdmin):
    list_display = ('transfer_id', 'party', 'status', 'date', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('transfer_id', 'subject', 'party')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-date',)
    
    fieldsets = (
        (None, {'fields': ('office', 'transfer_id', 'date', 'party', 'status', 'subject')}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(OfficeStaffMember)
class OfficeStaffMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'office', 'role', 'status', 'assigned_date', 'updated_at')
    list_filter = ('status', 'role')
    search_fields = ('user__email', 'office__office_name')
    readonly_fields = ('assigned_date', 'updated_at')
    ordering = ('-assigned_date',)
    
    fieldsets = (
        (None, {'fields': ('office', 'user', 'role', 'status')}),
        ('Important dates', {'fields': ('assigned_date', 'updated_at')}),
    )
