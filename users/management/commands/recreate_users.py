from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import User, Role
import string
import random
from users.utils import generate_voss_id

class Command(BaseCommand):
    help = 'Deletes all non-superuser users and creates new users for each role.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting user recreation process...'))

        # 0. Ensure admin superuser exists
        admin_email = 'admin@example.com'
        admin_pass = 'admin123'
        if not User.objects.filter(email=admin_email, is_superuser=True).exists():
            User.objects.create_superuser(email=admin_email, password=admin_pass)
            self.stdout.write(self.style.SUCCESS(f'Admin superuser {admin_email} created.'))
        else:
            self.stdout.write(self.style.NOTICE(f'Admin superuser {admin_email} already exists.'))

        # 1. Delete all users who are not superusers
        admin_users = User.objects.filter(is_superuser=True)
        admin_emails = list(admin_users.values_list('email', flat=True))
        
        self.stdout.write(f"Found {admin_users.count()} admin user(s) to preserve: {', '.join(admin_emails)}")

        users_to_delete = User.objects.filter(is_superuser=False)
        count_to_delete = users_to_delete.count()
        users_to_delete.delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {count_to_delete} non-admin users.'))

        # 2. Get all available roles
        roles = Role.objects.all()
        if not roles.exists():
            self.stdout.write(self.style.ERROR('No roles found in the database. Please create roles first.'))
            self.stdout.write(self.style.NOTICE('You can use `python manage.py create_default_roles` to create them.'))
            return

        self.stdout.write(f'Found {roles.count()} roles. Creating 2 users per role.')

        # 3. Create 2 users for each role
        for role in roles:
            for i in range(2):
                first_name = f'{role.name.replace(" ", "")}{i+1}'
                last_name = 'User'
                email = f'{first_name.lower()}@voss.com'
                
                if User.objects.filter(email=email).exists():
                    self.stdout.write(self.style.WARNING(f'User with email {email} already exists. Skipping.'))
                    continue

                user = User.objects.create_user(
                    email=email,
                    password='Password123!',
                    first_name=first_name,
                    last_name=last_name,
                    role=role,
                    voss_id=generate_voss_id(),
                    department='IT Department', # Default department
                    force_password_change=True
                )
                self.stdout.write(self.style.SUCCESS(f'Created user: {user.email} with role {role.name} and VOSS ID {user.voss_id}'))

        self.stdout.write(self.style.SUCCESS('Successfully recreated users.')) 