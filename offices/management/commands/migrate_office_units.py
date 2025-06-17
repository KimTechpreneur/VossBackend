from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from offices.models import Office
from units.models import Unit
from users.models import User
from django.db.models import Count

class Command(BaseCommand):
    help = 'Reviews and updates office-unit relationships based on user assignments'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run in dry-run mode (no changes will be made)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if office already has a unit',
        )
        parser.add_argument(
            '--unit',
            type=str,
            help='Specify a unit ID to only process offices for that unit',
        )

    def get_unit_by_code_prefix(self, office_code, units):
        """Try to find a unit based on office code prefix."""
        # Extract prefix (e.g., 'ENG' from 'ENG-CS-001')
        prefix = office_code.split('-')[0] if '-' in office_code else office_code[:3]
        
        # Map common prefixes to unit types
        prefix_map = {
            'ENG': 'academic_faculty',  # Engineering
            'CS': 'academic_faculty',   # Computer Science
            'IT': 'it_services',        # IT Services
            'FIN': 'finance_division',  # Finance
            'VC': 'central_admin',      # Vice Chancellor
            'HC': 'health_services',    # Health Center
            'LIB': 'library',          # Library
            'SA': 'student_affairs',   # Student Affairs
            'HR': 'human_resources',   # Human Resources
            'SEC': 'security',         # Security
            'MAINT': 'maintenance',    # Maintenance
        }

        if prefix in prefix_map:
            matching_units = units.filter(unit_type=prefix_map[prefix])
            if matching_units.exists():
                return matching_units.first(), f"Matched office code prefix {prefix} to unit type {prefix_map[prefix]}"

        return None, None

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        specific_unit = options['unit']
        
        self.stdout.write('Starting office-unit relationship review...')
        if dry_run:
            self.stdout.write('DRY RUN MODE - No changes will be made')
        
        try:
            with transaction.atomic():
                # Get all units for reference
                units = Unit.objects.all()
                self.stdout.write(f'Found {units.count()} units in the system')
                for unit in units:
                    self.stdout.write(f'  - {unit.name} ({unit.unit_code})')

                # Get offices to process
                if specific_unit:
                    offices = Office.objects.filter(unit_id=specific_unit)
                    self.stdout.write(f'\nProcessing only offices for unit: {specific_unit}')
                else:
                    offices = Office.objects.all()
                
                # Count current state
                offices_with_unit = offices.exclude(unit__isnull=True).count()
                offices_without_unit = offices.filter(unit__isnull=True).count()
                self.stdout.write(f'\nCurrent state:')
                self.stdout.write(f'  Offices with unit: {offices_with_unit}')
                self.stdout.write(f'  Offices without unit: {offices_without_unit}')

                # Process each office
                for office in offices:
                    self.stdout.write(f'\nProcessing office: {office.office_name} ({office.office_code})')
                    
                    if office.unit and not force:
                        self.stdout.write(f'  Already assigned to unit: {office.unit.name}')
                        continue

                    # Try to find the best unit match
                    suggested_unit = None
                    reason = None

                    # 1. Try head of office's unit
                    if office.head_of_office and office.head_of_office.unit:
                        suggested_unit = office.head_of_office.unit
                        reason = f"Head of office ({office.head_of_office.email}) belongs to this unit"

                    # 2. Try office code prefix matching
                    if not suggested_unit:
                        suggested_unit, code_reason = self.get_unit_by_code_prefix(office.office_code, units)
                        if suggested_unit:
                            reason = code_reason

                    # 3. Try users in the office
                    if not suggested_unit:
                        users_in_office = User.objects.filter(headed_offices=office)
                        unit_counts = {}
                        for user in users_in_office:
                            if user.unit:
                                unit_counts[user.unit] = unit_counts.get(user.unit, 0) + 1
                        
                        if unit_counts:
                            suggested_unit = max(unit_counts.items(), key=lambda x: x[1])[0]
                            reason = f"Most common unit among {len(users_in_office)} office users"

                    # 4. Try office type matching
                    if not suggested_unit:
                        # Map office types to unit types
                        office_to_unit_type = {
                            'Faculty-Level': 'academic_faculty',
                            'Support Office': 'support_service',
                            'Record Storage': 'central_admin',
                            'Departmental': 'academic_faculty'
                        }
                        matching_unit_type = office_to_unit_type.get(office.office_type)
                        if matching_unit_type:
                            matching_units = Unit.objects.filter(unit_type=matching_unit_type)
                            if matching_units.exists():
                                suggested_unit = matching_units.first()
                                reason = f"Matched office type {office.office_type} to unit type {matching_unit_type}"

                    # Report findings
                    if suggested_unit:
                        if office.unit and office.unit != suggested_unit:
                            self.stdout.write(f'  Current unit: {office.unit.name}')
                            self.stdout.write(f'  Suggested unit: {suggested_unit.name} ({reason})')
                            if not dry_run and force:
                                office.unit = suggested_unit
                                office.save()
                                self.stdout.write(self.style.SUCCESS(f'  Updated unit assignment'))
                        elif not office.unit:
                            self.stdout.write(f'  Suggested unit: {suggested_unit.name} ({reason})')
                            if not dry_run:
                                office.unit = suggested_unit
                                office.save()
                                self.stdout.write(self.style.SUCCESS(f'  Assigned to unit'))
                    else:
                        self.stdout.write(self.style.WARNING(f'  No suitable unit found'))

                # Final count
                if not dry_run:
                    final_with_unit = Office.objects.exclude(unit__isnull=True).count()
                    final_without_unit = Office.objects.filter(unit__isnull=True).count()
                    self.stdout.write(f'\nFinal state:')
                    self.stdout.write(f'  Offices with unit: {final_with_unit}')
                    self.stdout.write(f'  Offices without unit: {final_without_unit}')
                else:
                    self.stdout.write(self.style.SUCCESS('\nDry run completed. No changes were made.'))

                if dry_run:
                    # Always rollback in dry-run mode
                    raise CommandError('Rolling back due to dry-run mode')

        except CommandError as e:
            if 'Rolling back due to dry-run mode' in str(e):
                self.stdout.write(self.style.SUCCESS('Successfully rolled back dry-run'))
            else:
                raise
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during migration: {str(e)}'))
            raise 