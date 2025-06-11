from django.core.management.base import BaseCommand
from users.models import Role, Permission

class Command(BaseCommand):
    help = 'Create default roles for the application'

    def handle(self, *args, **options):
        roles_data = [
            {
                'name': 'Global Admin',
                'description': 'Full system access and administration rights',
                'type': 'system',
                'color': '#ef4444'
            },
            {
                'name': 'Unit Head',
                'description': 'Department/unit management rights',
                'type': 'custom',
                'color': '#3b82f6'
            },
            {
                'name': 'Staff',
                'description': 'Standard staff member access',
                'type': 'custom',
                'color': '#10b981'
            },
            {
                'name': 'Agent',
                'description': 'Field agent access rights',
                'type': 'custom',
                'color': '#f59e0b'
            },
            {
                'name': 'Auditor',
                'description': 'Audit and review access rights',
                'type': 'custom',
                'color': '#8b5cf6'
            },
        ]

        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults=role_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created role: {role.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Role already exists: {role.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully created/verified all default roles')
        ) 