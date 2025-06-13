from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Role, Permission, PasswordReset

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('name',)}),
        ('Important dates', {'fields': ('created_at',)}),
    )

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'module', 'created_at', 'updated_at')
    list_filter = ('module',)
    search_fields = ('name', 'module')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('module', 'name')

@admin.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_used', 'expires_at', 'created_at')
    list_filter = ('is_used',)
    search_fields = ('user__email', 'user__full_name')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'first_name', 'last_name', 'role', 'status', 'unit', 'last_login')
    list_filter = ('status', 'unit', 'role')
    search_fields = ('first_name', 'last_name', 'email', 'voss_id')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('email', 'first_name', 'last_name', 'phone')
        }),
        ('Work Information', {
            'fields': ('role', 'status', 'unit', 'office_location', 'notes', 'voss_id')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role', 'unit', 'office_location')}),
    )
