from django.contrib import admin
from .models import (
    FolderService, FolderCategory, RetentionClass, Folder,
    FolderFile, FolderTransfer, FolderSignature, FolderWorkflowStep,
    FolderComment
)

@admin.register(FolderService)
class FolderServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)
    
    fieldsets = (
        (None, {'fields': ('name', 'description')}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(FolderCategory)
class FolderCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)
    
    fieldsets = (
        (None, {'fields': ('name', 'description')}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(RetentionClass)
class RetentionClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'retention_period', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)
    
    fieldsets = (
        (None, {'fields': ('name', 'description', 'retention_period')}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ('folder_id', 'title', 'subject', 'status', 'priority', 'created_at', 'updated_at')
    list_filter = ('status', 'priority', 'service', 'category', 'retention_class')
    search_fields = ('folder_id', 'title', 'subject', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('folder_id', 'title', 'subject', 'description', 'status', 'priority')}),
        ('Relations', {'fields': ('service', 'category', 'retention_class', 'source_office', 'destination_office', 'created_by', 'assigned_agent', 'current_office', 'last_modified_by')}),
        ('Flags', {'fields': ('requires_signature', 'is_signed', 'auto_generate_file_numbers')}),
        ('Dates', {'fields': ('due_date', 'completed_at', 'created_at', 'updated_at')}),
        ('Additional Info', {'fields': ('forwarding_comment', 'tags', 'notifications')}),
    )

@admin.register(FolderFile)
class FolderFileAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'file_type', 'file_size', 'uploaded_by', 'uploaded_at')
    list_filter = ('file_type', 'is_archived')
    search_fields = ('original_filename', 'description', 'file_number')
    readonly_fields = ('uploaded_at',)
    ordering = ('-uploaded_at',)
    
    fieldsets = (
        (None, {'fields': ('folder', 'file', 'original_filename', 'file_type', 'file_size', 'uploaded_by', 'description', 'file_number')}),
        ('Archive Info', {'fields': ('is_archived', 'archived_at', 'archived_by')}),
        ('Important dates', {'fields': ('uploaded_at',)}),
    )

@admin.register(FolderTransfer)
class FolderTransferAdmin(admin.ModelAdmin):
    list_display = ('folder', 'from_office', 'to_office', 'status', 'transfer_date')
    list_filter = ('status', 'delivery_method', 'priority')
    search_fields = ('folder__folder_id', 'notes', 'agent_notes')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-transfer_date',)
    
    fieldsets = (
        (None, {'fields': ('folder', 'from_office', 'to_office', 'agent', 'status', 'transfer_date', 'delivered_at', 'notes', 'confirmation_type', 'time_taken', 'created_by', 'received_by', 'delivery_method', 'agent_notes', 'priority', 'tags', 'notifications', 'submitted_at')}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(FolderSignature)
class FolderSignatureAdmin(admin.ModelAdmin):
    list_display = ('folder', 'signed_by', 'signature_type', 'signed_at', 'is_verified')
    list_filter = ('signature_type', 'is_verified')
    search_fields = ('folder__folder_id', 'notes')
    readonly_fields = ('signed_at',)
    ordering = ('-signed_at',)
    
    fieldsets = (
        (None, {'fields': ('folder', 'signed_by', 'signature_type', 'signature_data', 'notes', 'is_verified', 'verified_at', 'verified_by')}),
        ('Important dates', {'fields': ('signed_at',)}),
    )

@admin.register(FolderWorkflowStep)
class FolderWorkflowStepAdmin(admin.ModelAdmin):
    list_display = ('folder', 'office', 'step_number', 'total_steps', 'status')
    list_filter = ('status', 'is_required')
    search_fields = ('folder__folder_id', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('step_number',)
    
    fieldsets = (
        (None, {'fields': ('folder', 'office', 'step_number', 'total_steps', 'status', 'completed_at', 'notes', 'completed_by', 'is_required', 'estimated_duration', 'actual_duration', 'responsible_user', 'due_date')}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(FolderComment)
class FolderCommentAdmin(admin.ModelAdmin):
    list_display = ('folder', 'user', 'comment', 'is_internal')
    list_filter = ('is_internal',)
    search_fields = ('folder__folder_id', 'comment')
    readonly_fields = ()
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('folder', 'user', 'comment', 'is_internal', 'parent_comment')}),
    )
