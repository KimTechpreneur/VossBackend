from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import Permission

class Command(BaseCommand):
    help = 'Create comprehensive permissions for the role-based access control system'

    def handle(self, *args, **options):
        permissions_data = [
            # User Management
            {'name': 'View Users', 'module': 'User Management'},
            {'name': 'Create Users', 'module': 'User Management'},
            {'name': 'Edit Users', 'module': 'User Management'},
            {'name': 'Delete Users', 'module': 'User Management'},
            {'name': 'Deactivate Users', 'module': 'User Management'},
            {'name': 'Reset User Passwords', 'module': 'User Management'},
            {'name': 'Bulk User Operations', 'module': 'User Management'},
            {'name': 'View User Profiles', 'module': 'User Management'},
            {'name': 'Export User Data', 'module': 'User Management'},

            # Role & Permission Management
            {'name': 'View Roles', 'module': 'Role Management'},
            {'name': 'Create Roles', 'module': 'Role Management'},
            {'name': 'Edit Roles', 'module': 'Role Management'},
            {'name': 'Delete Roles', 'module': 'Role Management'},
            {'name': 'Assign Permissions', 'module': 'Role Management'},
            {'name': 'View Permissions', 'module': 'Role Management'},
            {'name': 'Manage System Roles', 'module': 'Role Management'},

            # Office Management
            {'name': 'View Offices', 'module': 'Office Management'},
            {'name': 'Create Offices', 'module': 'Office Management'},
            {'name': 'Edit Offices', 'module': 'Office Management'},
            {'name': 'Delete Offices', 'module': 'Office Management'},
            {'name': 'Manage Office Structure', 'module': 'Office Management'},

            # Agent Management
            {'name': 'View Agents', 'module': 'Agent Management'},
            {'name': 'Create Agents', 'module': 'Agent Management'},
            {'name': 'Edit Agents', 'module': 'Agent Management'},
            {'name': 'Delete Agents', 'module': 'Agent Management'},
            {'name': 'Assign Agent Tasks', 'module': 'Agent Management'},

            # Folder Management
            {'name': 'View Folders', 'module': 'Folder Management'},
            {'name': 'Create Folders', 'module': 'Folder Management'},
            {'name': 'Edit Folders', 'module': 'Folder Management'},
            {'name': 'Delete Folders', 'module': 'Folder Management'},
            {'name': 'Move Folders', 'module': 'Folder Management'},
            {'name': 'Archive Folders', 'module': 'Folder Management'},
            {'name': 'Restore Folders', 'module': 'Folder Management'},

            # Transfer Management
            {'name': 'View Transfers', 'module': 'Transfer Management'},
            {'name': 'Create Transfers', 'module': 'Transfer Management'},
            {'name': 'Edit Transfers', 'module': 'Transfer Management'},
            {'name': 'Cancel Transfers', 'module': 'Transfer Management'},
            {'name': 'Approve Transfers', 'module': 'Transfer Management'},
            {'name': 'Track Transfers', 'module': 'Transfer Management'},
            {'name': 'Bulk Transfer Operations', 'module': 'Transfer Management'},
            {'name': 'Confirm Transfer Delivery', 'module': 'Transfer Management'},

            # Dashboard & Analytics
            {'name': 'View Dashboard', 'module': 'Dashboard'},
            {'name': 'View Analytics', 'module': 'Dashboard'},
            {'name': 'View Reports', 'module': 'Dashboard'},
            {'name': 'Export Data', 'module': 'Dashboard'},
            {'name': 'View System Stats', 'module': 'Dashboard'},

            # Notifications
            {'name': 'View Notifications', 'module': 'Notifications'},
            {'name': 'Send Notifications', 'module': 'Notifications'},
            {'name': 'Manage Notification Settings', 'module': 'Notifications'},
            {'name': 'Bulk Notifications', 'module': 'Notifications'},

            # Search & Discovery
            {'name': 'Global Search', 'module': 'Search'},
            {'name': 'Advanced Search', 'module': 'Search'},
            {'name': 'Search All Records', 'module': 'Search'},
            {'name': 'Export Search Results', 'module': 'Search'},

            # Units Management
            {'name': 'View Units', 'module': 'Units'},
            {'name': 'Create Units', 'module': 'Units'},
            {'name': 'Edit Units', 'module': 'Units'},
            {'name': 'Delete Units', 'module': 'Units'},
            {'name': 'Manage Unit Hierarchy', 'module': 'Units'},

            # Reports & Analytics
            {'name': 'Generate Reports', 'module': 'Reports'},
            {'name': 'View Performance Reports', 'module': 'Reports'},
            {'name': 'Schedule Reports', 'module': 'Reports'},
            {'name': 'Custom Report Builder', 'module': 'Reports'},
            {'name': 'Export Reports', 'module': 'Reports'},

            # Ticket Management
            {'name': 'View Tickets', 'module': 'Ticket Management'},
            {'name': 'Create Tickets', 'module': 'Ticket Management'},
            {'name': 'Edit Tickets', 'module': 'Ticket Management'},
            {'name': 'Close Tickets', 'module': 'Ticket Management'},
            {'name': 'Assign Tickets', 'module': 'Ticket Management'},
            {'name': 'Escalate Tickets', 'module': 'Ticket Management'},

            # System Administration
            {'name': 'System Configuration', 'module': 'System Admin'},
            {'name': 'View System Logs', 'module': 'System Admin'},
            {'name': 'Backup & Restore', 'module': 'System Admin'},
            {'name': 'Manage Integrations', 'module': 'System Admin'},
            {'name': 'Security Settings', 'module': 'System Admin'},
            {'name': 'Audit Trail', 'module': 'System Admin'},

            # Profile Management
            {'name': 'View Own Profile', 'module': 'Profile'},
            {'name': 'Edit Own Profile', 'module': 'Profile'},
            {'name': 'Change Password', 'module': 'Profile'},
            {'name': 'Manage Account Settings', 'module': 'Profile'},
        ]

        created_count = 0
        updated_count = 0
        
        with transaction.atomic():
            for perm_data in permissions_data:
                permission, created = Permission.objects.get_or_create(
                    name=perm_data['name'],
                    module=perm_data['module'],
                    defaults=perm_data
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Created permission: {permission.name} ({permission.module})')
                    )
                else:
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Skipped existing permission: {permission.name} ({permission.module})')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Permission creation complete!\n'
                f'Created: {created_count} permissions\n'
                f'Skipped: {updated_count} existing permissions\n'
                f'Total: {Permission.objects.count()} permissions in database'
            )
        ) 