from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import Role, Permission

class Command(BaseCommand):
    help = 'Assign permissions to default roles'

    def handle(self, *args, **options):
        # Define role-permission mappings
        role_permissions = {
            'Global Admin': [
                # All permissions for Global Admin
                'ALL'
            ],
            'Unit Head': [
                # Office Management
                'View Offices', 'Create Offices', 'Edit Offices', 'Manage Office Structure',
                # User Management (limited)
                'View Users', 'View User Profiles', 'Create Users', 'Edit Users',
                # Role Management (limited)
                'View Roles', 'View Permissions',
                # Folder Management
                'View Folders', 'Create Folders', 'Edit Folders', 'Move Folders', 'Archive Folders',
                # Transfer Management
                'View Transfers', 'Create Transfers', 'Edit Transfers', 'Approve Transfers', 'Track Transfers',
                'Handle Escalations', 'Manage Transfers',
                # Dashboard & Reports
                'View Dashboard', 'View Analytics', 'View Reports', 'Generate Reports', 'Export Data',
                # Agent Management
                'View Agents', 'Create Agents', 'Edit Agents', 'Assign Agent Tasks',
                # Units
                'View Units', 'Create Units', 'Edit Units', 'Manage Unit Hierarchy',
                # Profile
                'View Own Profile', 'Edit Own Profile', 'Change Password', 'Manage Account Settings',
            ],
            'Staff': [
                # Basic operations
                'View Offices', 'View Users', 'View User Profiles',
                'View Folders', 'Create Folders', 'Edit Folders',
                'View Transfers', 'Create Transfers', 'Track Transfers',
                'Handle Escalations', 'Manage Transfers',
                'View Dashboard', 'View Reports',
                'View Agents',
                'View Units',
                'View Notifications',
                'Global Search', 'Advanced Search',
                # Profile management
                'View Own Profile', 'Edit Own Profile', 'Change Password', 'Manage Account Settings',
            ],
            'Agent': [
                # Field agent specific
                'View Offices', 'View Folders', 'Edit Folders',
                'View Transfers', 'Create Transfers', 'Edit Transfers', 'Track Transfers',
                'View Dashboard',
                'View Agents',
                'View Notifications',
                'Global Search',
                # Profile management
                'View Own Profile', 'Edit Own Profile', 'Change Password', 'Manage Account Settings',
            ],
            'Auditor': [
                # Read-only access for auditing
                'View Offices', 'View Users', 'View User Profiles',
                'View Roles', 'View Permissions',
                'View Folders', 'View Transfers',
                'View Dashboard', 'View Analytics', 'View Reports', 'Generate Reports', 'Export Data',
                'View Agents', 'View Units',
                'View Notifications',
                'Global Search', 'Advanced Search', 'Search All Records', 'Export Search Results',
                'View System Logs', 'Audit Trail',
                # Profile management
                'View Own Profile', 'Edit Own Profile', 'Change Password', 'Manage Account Settings',
            ]
        }

        with transaction.atomic():
            for role_name, permission_names in role_permissions.items():
                try:
                    role = Role.objects.get(name=role_name)
                    
                    if permission_names == ['ALL']:
                        # Assign all permissions to Global Admin
                        all_permissions = Permission.objects.all()
                        role.permissions.set(all_permissions)
                        self.stdout.write(
                            self.style.SUCCESS(f'✅ Assigned ALL {all_permissions.count()} permissions to {role_name}')
                        )
                    else:
                        # Assign specific permissions
                        permissions = Permission.objects.filter(name__in=permission_names)
                        role.permissions.set(permissions)
                        self.stdout.write(
                            self.style.SUCCESS(f'✅ Assigned {permissions.count()} permissions to {role_name}')
                        )
                        
                        # Check for missing permissions
                        assigned_names = set(permissions.values_list('name', flat=True))
                        missing_permissions = set(permission_names) - assigned_names
                        if missing_permissions:
                            self.stdout.write(
                                self.style.WARNING(f'⚠️  Missing permissions for {role_name}: {missing_permissions}')
                            )
                
                except Role.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Role not found: {role_name}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Role-permission assignment complete!\n'
                f'All roles have been configured with appropriate permissions.'
            )
        )

        try:
            with transaction.atomic():
                # Get roles
                global_admin = Role.objects.get(name='Global Admin')
                unit_head = Role.objects.get(name='Unit Head')
                staff = Role.objects.get(name='Staff')
                agent = Role.objects.get(name='Agent')

                # Get the confirm delivery permission
                confirm_delivery_perm = Permission.objects.get(
                    name='Confirm Transfer Delivery',
                    module='Transfer Management'
                )

                # Assign the permission to appropriate roles
                for role in [global_admin, unit_head, staff]:
                    role.permissions.add(confirm_delivery_perm)
                    self.stdout.write(
                        self.style.SUCCESS(f'Added confirm delivery permission to {role.name}')
                    )

                self.stdout.write(
                    self.style.SUCCESS('Successfully assigned confirm delivery permission to roles')
                )

        except Role.DoesNotExist as e:
            self.stdout.write(
                self.style.ERROR(f'Role not found: {str(e)}')
            )
        except Permission.DoesNotExist as e:
            self.stdout.write(
                self.style.ERROR(f'Permission not found: {str(e)}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error assigning permissions: {str(e)}')
            )