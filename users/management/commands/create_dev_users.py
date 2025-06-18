from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from users.models import Role, Permission
from offices.models import Office
from units.models import Unit
from django.utils import timezone
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create comprehensive development test users with proper roles, permissions, and assignments'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing dev users and recreate them',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Creating development test users...'))
        
        # If reset flag is provided, delete existing dev users
        if options['reset']:
            self.stdout.write(self.style.WARNING('⚠️  Resetting existing development users...'))
            dev_emails = [
                'admin@example.com', 'agent@example.com', 'user@example.com',
                'staff@example.com', 'unithead@example.com', 'auditor@example.com'
            ]
            User.objects.filter(email__in=dev_emails, is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS('✅ Deleted existing development users'))

        # Get or create sample units and offices
        self.create_sample_data()
        
        # Create development users with proper roles
        self.create_dev_users()
        
        self.stdout.write(self.style.SUCCESS('🎉 Development users setup complete!'))

    @transaction.atomic
    def create_sample_data(self):
        """Create sample units and offices if they don't exist"""
        
        # Create sample units
        units_data = [
            {
                'name': 'Central Administration',
                'unit_type': 'central_admin',
                'unit_code': 'ADMIN-001',
                'location': 'Main Building',
                'description': 'Central administrative unit',
                'staff_count': 15
            },
            {
                'name': 'Faculty of Engineering',
                'unit_type': 'academic_faculty',
                'unit_code': 'ENG-001',
                'location': 'Engineering Building',
                'description': 'Engineering faculty',
                'staff_count': 45
            },
            {
                'name': 'IT Services',
                'unit_type': 'it_services',
                'unit_code': 'IT-001',
                'location': 'Technology Building',
                'description': 'IT support services',
                'staff_count': 20
            },
            {
                'name': 'Finance Department',
                'unit_type': 'finance_division',
                'unit_code': 'FIN-001',
                'location': 'Administrative Block',
                'description': 'Financial operations',
                'staff_count': 25
            }
        ]

        for unit_data in units_data:
            unit, created = Unit.objects.get_or_create(
                unit_code=unit_data['unit_code'],
                defaults=unit_data
            )
            if created:
                self.stdout.write(f'✅ Created unit: {unit.name}')

        # Create sample offices
        offices_data = [
            {
                'office_name': "Vice Chancellor's Office",
                'office_code': 'VC-001',
                'office_type': 'Faculty-Level',
                'location': 'Main Building, Floor 3',
                'description': 'Executive office',
                'staff_count': 8
            },
            {
                'office_name': 'Engineering Dean Office',
                'office_code': 'ENG-DEAN-001',
                'office_type': 'Faculty-Level',
                'location': 'Engineering Building, Floor 1',
                'description': 'Engineering faculty administration',
                'staff_count': 12
            },
            {
                'office_name': 'Computer Science Department',
                'office_code': 'CS-001',
                'office_type': 'Departmental',
                'location': 'Engineering Building, Floor 2',
                'description': 'CS department office',
                'staff_count': 18
            },
            {
                'office_name': 'IT Support Office',
                'office_code': 'IT-SUPPORT-001',
                'office_type': 'Support Office',
                'location': 'Technology Building, Floor 1',
                'description': 'IT help desk and support',
                'staff_count': 10
            },
            {
                'office_name': 'Finance Office',
                'office_code': 'FIN-001',
                'office_type': 'Support Office',
                'location': 'Administrative Block, Floor 2',
                'description': 'Financial services office',
                'staff_count': 15
            },
            {
                'office_name': 'Records Archive',
                'office_code': 'ARCHIVE-001',
                'office_type': 'Record Storage',
                'location': 'Basement, Main Building',
                'description': 'Central records storage',
                'staff_count': 6
            }
        ]

        for office_data in offices_data:
            office, created = Office.objects.get_or_create(
                office_code=office_data['office_code'],
                defaults=office_data
            )
            if created:
                self.stdout.write(f'✅ Created office: {office.office_name}')

    @transaction.atomic
    def create_dev_users(self):
        """Create comprehensive development test users"""
        
        # Get required objects
        units = list(Unit.objects.all())
        offices = list(Office.objects.all())
        
        if not units or not offices:
            self.stdout.write(self.style.ERROR('❌ No units or offices found. Please create sample data first.'))
            return

        # Development users data with comprehensive role assignments
        dev_users_data = [
            {
                'email': 'admin@example.com',
                'password': 'admin123',
                'first_name': 'Global',
                'last_name': 'Admin',
                'role_name': 'Global Admin',
                'unit': random.choice(units),
                'office': random.choice(offices),
                'is_superuser': True,
                'is_staff': True,
                'description': 'System administrator with full access'
            },
            {
                'email': 'unithead@example.com',
                'password': 'unit123',
                'first_name': 'Unit',
                'last_name': 'Head',
                'role_name': 'Unit Head',
                'unit': units[0] if units else None,
                'office': offices[0] if offices else None,
                'description': 'Unit head with management privileges'
            },
            {
                'email': 'staff@example.com',
                'password': 'staff123',
                'first_name': 'Staff',
                'last_name': 'Member',
                'role_name': 'Staff',
                'unit': units[1] if len(units) > 1 else units[0],
                'office': offices[1] if len(offices) > 1 else offices[0],
                'description': 'Regular staff member'
            },
            {
                'email': 'agent@example.com',
                'password': 'agent123',
                'first_name': 'Field',
                'last_name': 'Agent',
                'role_name': 'Agent',
                'unit': units[2] if len(units) > 2 else units[0],
                'office': offices[2] if len(offices) > 2 else offices[0],
                'description': 'Field agent for transfers and operations'
            },
            {
                'email': 'auditor@example.com',
                'password': 'audit123',
                'first_name': 'System',
                'last_name': 'Auditor',
                'role_name': 'Auditor',
                'unit': units[3] if len(units) > 3 else units[0],
                'office': offices[3] if len(offices) > 3 else offices[0],
                'description': 'System auditor with read-only access'
            },
            {
                'email': 'user@example.com',
                'password': 'user123',
                'first_name': 'Basic',
                'last_name': 'User',
                'role_name': 'Staff',  # Using Staff role for basic user
                'unit': units[4] if len(units) > 4 else units[0],
                'office': offices[4] if len(offices) > 4 else offices[0],
                'description': 'Basic user with limited access'
            }
        ]

        created_users = []
        for user_data in dev_users_data:
            # Get the role
            try:
                role = Role.objects.get(name=user_data['role_name'])
            except Role.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ Role "{user_data["role_name"]}" not found. Please create roles first.')
                )
                continue

            # Create or update user
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'role': role,
                    'unit': user_data['unit'],
                    'office_location': user_data['office'].office_name if user_data['office'] else None,
                    'notes': user_data['description'],
                    'is_superuser': user_data.get('is_superuser', False),
                    'is_staff': user_data.get('is_staff', True),
                    'is_active': True,
                    'phone': f'+1234567{random.randint(100, 999)}'
                }
            )

            if created:
                user.set_password(user_data['password'])
                user.save()
                created_users.append(user)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Created user: {user.email} | Role: {role.name} | Unit: {user.unit.name if user.unit else "None"}'
                    )
                )
            else:
                # Update existing user with latest data
                user.role = role
                user.unit = user_data['unit']
                user.office_location = user_data['office'].office_name if user_data['office'] else None
                user.notes = user_data['description']
                user.is_active = True
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  Updated existing user: {user.email} | Role: {role.name}'
                    )
                )

        # Display summary
        self.stdout.write(self.style.SUCCESS(f'\n📊 Development Users Summary:'))
        self.stdout.write(self.style.SUCCESS(f'Created: {len(created_users)} new users'))
        self.stdout.write(self.style.SUCCESS(f'Total dev users: {len(dev_users_data)}'))
        
        # Display login credentials
        self.stdout.write(self.style.SUCCESS(f'\n🔑 Development Login Credentials:'))
        for user_data in dev_users_data:
            role_name = user_data['role_name']
            self.stdout.write(
                self.style.SUCCESS(
                    f'  {role_name}: {user_data["email"]} / {user_data["password"]}'
                )
            )

        # Display role permissions summary
        self.stdout.write(self.style.SUCCESS(f'\n🛡️  Role Permissions Summary:'))
        for role in Role.objects.all():
            perm_count = role.permissions.count()
            self.stdout.write(
                self.style.SUCCESS(f'  {role.name}: {perm_count} permissions')
            )

        self.stdout.write(self.style.SUCCESS(f'\n🌟 Ready for comprehensive testing!'))
        self.stdout.write(self.style.SUCCESS(f'   • Use /dev-login for quick access'))
        self.stdout.write(self.style.SUCCESS(f'   • Each user has proper role-based permissions'))
        self.stdout.write(self.style.SUCCESS(f'   • Users are assigned to different units and offices'))
        self.stdout.write(self.style.SUCCESS(f'   • Test role-based access control across the system')) 