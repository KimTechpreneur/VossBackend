from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from offices.models import Office
from django.utils import timezone
import uuid

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample offices for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample offices...'))
        
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

        # Sample offices data
        offices_data = [
            {
                'office_name': 'Dean\'s Office',
                'office_code': 'DEAN-001',
                'office_type': 'Faculty-Level',
                'staff_count': 15,
                'status': 'Active',
                'location': 'Main Building, 3rd Floor',
                'description': 'Main administrative office for the faculty',
                'head_of_office': test_user
            },
            {
                'office_name': 'Computer Science Department',
                'office_code': 'CS-002',
                'office_type': 'Departmental',
                'staff_count': 25,
                'status': 'Active',
                'location': 'Technology Building, 2nd Floor',
                'description': 'Computer Science academic department',
                'head_of_office': test_user
            },
            {
                'office_name': 'Engineering Department',
                'office_code': 'ENG-003',
                'office_type': 'Departmental',
                'staff_count': 30,
                'status': 'Active',
                'location': 'Engineering Building, 1st Floor',
                'description': 'Engineering academic department'
            },
            {
                'office_name': 'Student Affairs',
                'office_code': 'SA-004',
                'office_type': 'Support Office',
                'staff_count': 12,
                'status': 'Active',
                'location': 'Student Center, Ground Floor',
                'description': 'Student support and services office'
            },
            {
                'office_name': 'Records Archive',
                'office_code': 'ARCH-005',
                'office_type': 'Record Storage',
                'staff_count': 5,
                'status': 'Active',
                'location': 'Basement, Building A',
                'description': 'Central records storage and archival facility'
            },
            {
                'office_name': 'Business Department',
                'office_code': 'BUS-006',
                'office_type': 'Departmental',
                'staff_count': 20,
                'status': 'Inactive',
                'location': 'Business Building, 2nd Floor',
                'description': 'Business and management academic department'
            }
        ]

        # Create offices
        created_count = 0
        for office_data in offices_data:
            office, created = Office.objects.get_or_create(
                office_code=office_data['office_code'],
                defaults={
                    **office_data,
                    'updated_by': test_user
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created office: {office.office_name}')
            else:
                self.stdout.write(f'Office already exists: {office.office_name}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new offices')
        ) 