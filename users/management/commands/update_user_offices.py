from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import User
from offices.models import Office

class Command(BaseCommand):
    help = 'Updates user-office relationships based on unit assignments'

    def handle(self, *args, **options):
        self.stdout.write('Starting user-office relationship update...')
        
        try:
            with transaction.atomic():
                # Get all users with units
                users_with_unit = User.objects.exclude(unit__isnull=True)
                self.stdout.write(f'Found {users_with_unit.count()} users with units')

                for user in users_with_unit:
                    # Get all offices in the user's unit
                    unit_offices = Office.objects.filter(unit=user.unit)
                    
                    # If user is head of any office in their unit, keep that relationship
                    headed_offices = unit_offices.filter(head_of_office=user)
                    
                    # Log the assignments
                    if headed_offices.exists():
                        for office in headed_offices:
                            self.stdout.write(f'User {user.email} remains head of office {office.office_name}')
                    
                    # Update user's unit count in offices
                    for office in unit_offices:
                        office.staff_count = User.objects.filter(unit=office.unit).count()
                        office.save()
                        self.stdout.write(f'Updated staff count for office {office.office_name}: {office.staff_count}')

                self.stdout.write(self.style.SUCCESS('Successfully updated user-office relationships'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during update: {str(e)}'))
            raise 