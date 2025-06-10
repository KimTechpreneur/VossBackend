from django.contrib import admin
from .models import (
    TransferPathStep, AgentActivity, TransferTrail,
    SearchFilters, SearchResultItem
)

@admin.register(TransferPathStep)
class TransferPathStepAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'updated_at')
    search_fields = ('transfer__id',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('transfer',)}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(AgentActivity)
class AgentActivityAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'updated_at')
    search_fields = ('agent__email',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('agent',)}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(TransferTrail)
class TransferTrailAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'updated_at')
    search_fields = ('transfer__id',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('transfer',)}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(SearchFilters)
class SearchFiltersAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'updated_at')
    search_fields = ('user__email',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('user',)}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(SearchResultItem)
class SearchResultItemAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'updated_at')
    search_fields = ('search_session',)
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('search_session',)}),
        ('Important dates', {'fields': ('created_at', 'updated_at')}),
    )
