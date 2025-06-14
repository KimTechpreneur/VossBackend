from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from units.models import Unit
from offices.models import Office
from django.utils import timezone
import uuid

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample units and their offices for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample units and offices...'))
        
        # Create a test user if it doesn't exist
        test_user, created = User.objects.get_or_create(
            email='testuser@example.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
                'is_active': True,
            }
        )
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            self.stdout.write(f'Created test user: {test_user.email}')

        # Sample units and their offices data
        units_data = [
            {
                'name': "Vice Chancellor's Office",
                'unit_type': 'central_admin',
                'unit_code': 'VC-001',
                'head_of_unit': test_user,
                'location': 'Administrative Block, 1st Floor',
                'status': 'active',
                'description': 'Main administrative unit headed by the Vice Chancellor',
                'staff_count': 10,
                'offices': [
                    {
                        'office_name': "Vice Chancellor's Secretariat",
                        'office_type': 'Faculty-Level',
                        'office_code': 'VC-SEC-001',
                        'location': 'Administrative Block, 1st Floor',
                        'description': 'Main secretariat office of the Vice Chancellor',
                        'staff_count': 5
                    },
                    {
                        'office_name': 'Executive Records',
                        'office_type': 'Record Storage',
                        'office_code': 'VC-REC-001',
                        'location': 'Administrative Block, 1st Floor',
                        'description': 'Records storage for executive documents',
                        'staff_count': 3
                    }
                ]
            },
            {
                'name': 'Faculty of Engineering',
                'unit_type': 'academic_faculty',
                'unit_code': 'ENG-001',
                'head_of_unit': test_user,
                'location': 'Engineering Complex, Block A',
                'status': 'active',
                'description': 'Engineering faculty offering various engineering programs',
                'staff_count': 45,
                'offices': [
                    {
                        'office_name': "Dean's Office",
                        'office_type': 'Faculty-Level',
                        'office_code': 'ENG-DEAN-001',
                        'location': 'Engineering Complex, Block A, 1st Floor',
                        'description': "Dean's office for the Faculty of Engineering",
                        'staff_count': 8
                    },
                    {
                        'office_name': 'Computer Science Department',
                        'office_type': 'Departmental',
                        'office_code': 'ENG-CS-001',
                        'location': 'Engineering Complex, Block A, 2nd Floor',
                        'description': 'Computer Science Department',
                        'staff_count': 15
                    },
                    {
                        'office_name': 'Mechanical Engineering Department',
                        'office_type': 'Departmental',
                        'office_code': 'ENG-MECH-001',
                        'location': 'Engineering Complex, Block B, 1st Floor',
                        'description': 'Mechanical Engineering Department',
                        'staff_count': 12
                    }
                ]
            },
            {
                'name': 'Health Center',
                'unit_type': 'health_services',
                'unit_code': 'HC-001',
                'head_of_unit': test_user,
                'location': 'Medical Complex, Ground Floor',
                'status': 'active',
                'description': 'University health center providing medical services',
                'staff_count': 15,
                'offices': [
                    {
                        'office_name': 'Medical Records',
                        'office_type': 'Record Storage',
                        'office_code': 'HC-REC-001',
                        'location': 'Medical Complex, Ground Floor',
                        'description': 'Medical records storage and management',
                        'staff_count': 4
                    },
                    {
                        'office_name': 'Outpatient Department',
                        'office_type': 'Support Office',
                        'office_code': 'HC-OPD-001',
                        'location': 'Medical Complex, Ground Floor',
                        'description': 'Outpatient services and consultation',
                        'staff_count': 8
                    }
                ]
            },
            {
                'name': 'IT Support Services',
                'unit_type': 'it_services',
                'unit_code': 'IT-001',
                'head_of_unit': test_user,
                'location': 'Technology Building, 2nd Floor',
                'status': 'active',
                'description': 'Information Technology support and services',
                'staff_count': 20,
                'offices': [
                    {
                        'office_name': 'IT Help Desk',
                        'office_type': 'Support Office',
                        'office_code': 'IT-HELP-001',
                        'location': 'Technology Building, 2nd Floor',
                        'description': 'IT support and help desk services',
                        'staff_count': 8
                    },
                    {
                        'office_name': 'Network Operations',
                        'office_type': 'Support Office',
                        'office_code': 'IT-NET-001',
                        'location': 'Technology Building, 2nd Floor',
                        'description': 'Network infrastructure and operations',
                        'staff_count': 6
                    }
                ]
            },
            {
                'name': 'Finance Department',
                'unit_type': 'finance_division',
                'unit_code': 'FIN-001',
                'head_of_unit': test_user,
                'location': 'Administrative Block, 2nd Floor',
                'status': 'active',
                'description': 'Handles all financial matters of the university',
                'staff_count': 25,
                'offices': [
                    {
                        'office_name': 'Accounts Office',
                        'office_type': 'Support Office',
                        'office_code': 'FIN-ACC-001',
                        'location': 'Administrative Block, 2nd Floor',
                        'description': 'Financial accounts and bookkeeping',
                        'staff_count': 10
                    },
                    {
                        'office_name': 'Financial Records',
                        'office_type': 'Record Storage',
                        'office_code': 'FIN-REC-001',
                        'location': 'Administrative Block, 2nd Floor',
                        'description': 'Financial records and archives',
                        'staff_count': 5
                    }
                ]
            },
            # Additional demonstration units
            {
                'name': 'Library Services',
                'unit_type': 'library',
                'unit_code': 'LIB-001',
                'head_of_unit': test_user,
                'location': 'Central Library Building',
                'status': 'active',
                'description': 'Main university library and information services',
                'staff_count': 18,
                'offices': [
                    {
                        'office_name': 'Library Admin',
                        'office_type': 'Support Office',
                        'office_code': 'LIB-ADMIN-001',
                        'location': 'Central Library Building',
                        'description': 'Library administration office',
                        'staff_count': 6
                    },
                    {
                        'office_name': 'Library Records',
                        'office_type': 'Record Storage',
                        'office_code': 'LIB-REC-001',
                        'location': 'Central Library Building',
                        'description': 'Library records and archives',
                        'staff_count': 3
                    }
                ]
            },
            {
                'name': 'Student Affairs',
                'unit_type': 'student_affairs',
                'unit_code': 'SA-001',
                'head_of_unit': test_user,
                'location': 'Student Center, 1st Floor',
                'status': 'active',
                'description': 'Handles student welfare and activities',
                'staff_count': 12,
                'offices': [
                    {
                        'office_name': 'Student Support Office',
                        'office_type': 'Support Office',
                        'office_code': 'SA-SUP-001',
                        'location': 'Student Center, 1st Floor',
                        'description': 'Student support and services office',
                        'staff_count': 7
                    }
                ]
            }
        ]

        created_units = 0
        created_offices = 0
        for unit_data in units_data:
            offices_data = unit_data.pop('offices', [])
            unit, created = Unit.objects.get_or_create(
                unit_code=unit_data['unit_code'],
                defaults=unit_data
            )
            if created:
                created_units += 1
                self.stdout.write(f'Created unit: {unit.name}')
            else:
                self.stdout.write(f'Unit already exists: {unit.name}')

            # Create offices for this unit
            for office_data in offices_data:
                office, office_created = Office.objects.get_or_create(
                    office_code=office_data['office_code'],
                    defaults={
                        **office_data,
                        'unit': unit,
                        'head_of_office': test_user,
                        'updated_by': test_user
                    }
                )
                if office_created:
                    created_offices += 1
                    self.stdout.write(f'  Created office: {office.office_name}')
                else:
                    self.stdout.write(f'  Office already exists: {office.office_name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_units} new units and {created_offices} new offices'
            )
        ) 