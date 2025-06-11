#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VossBackend.settings')
django.setup()

from users.models import User, Role
from agents.models import Agent
from offices.models import Office

def create_test_data():
    print("=== CREATING TEST DATA ===")
    
    # Create Agent role if it doesn't exist
    agent_role, created = Role.objects.get_or_create(
        name='Agent',
        defaults={
            'description': 'Agent role for delivery agents',
            'type': 'system'
        }
    )
    if created:
        print(f"✓ Created Agent role: {agent_role.name}")
    else:
        print(f"✓ Agent role already exists: {agent_role.name}")
    
    # Create offices using the main Office model
    offices_data = [
        {
            'office_name': 'Main Campus Office',
            'office_type': 'Faculty-Level',
            'office_code': 'MCO-001',
            'status': 'Active',
            'location': 'Main Campus Building A'
        },
        {
            'office_name': 'East Wing Office',
            'office_type': 'Departmental',
            'office_code': 'EWO-002',
            'status': 'Active',
            'location': 'East Wing Building B'
        },
        {
            'office_name': 'West Wing Office',
            'office_type': 'Departmental',
            'office_code': 'WWO-003',
            'status': 'Active',
            'location': 'West Wing Building C'
        },
        {
            'office_name': 'Admin Building Office',
            'office_type': 'Support Office',
            'office_code': 'ABO-004',
            'status': 'Active',
            'location': 'Administration Building'
        },
    ]
    
    for office_data in offices_data:
        office, created = Office.objects.get_or_create(
            office_code=office_data['office_code'],
            defaults=office_data
        )
        if created:
            print(f"✓ Created office: {office.office_name}")
        else:
            print(f"✓ Office already exists: {office.office_name}")
    
    # Create test users with Agent role (but no agent profiles)
    test_users = [
        {
            'email': 'john.agent@voss.com',
            'first_name': 'John',
            'last_name': 'Agent',
            'password': 'testpass123'
        },
        {
            'email': 'jane.delivery@voss.com',
            'first_name': 'Jane',
            'last_name': 'Delivery',
            'password': 'testpass123'
        },
        {
            'email': 'mike.courier@voss.com',
            'first_name': 'Mike',
            'last_name': 'Courier',
            'password': 'testpass123'
        }
    ]
    
    for user_data in test_users:
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults={
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'role': agent_role,
                'department': 'IT Department'
            }
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
            print(f"✓ Created user with Agent role: {user.first_name} {user.last_name} ({user.email})")
        else:
            # Update role if user exists but doesn't have Agent role
            if user.role != agent_role:
                user.role = agent_role
                user.save()
                print(f"✓ Updated user role to Agent: {user.first_name} {user.last_name} ({user.email})")
            else:
                print(f"✓ User already exists with Agent role: {user.first_name} {user.last_name} ({user.email})")
    
    # Create one full agent profile as an example
    main_office = Office.objects.get(office_code='MCO-001')
    test_user = User.objects.get(email='john.agent@voss.com')
    
    if not hasattr(test_user, 'agent'):
        agent = Agent.objects.create(
            user=test_user,
            base_office=main_office,
            status='available',
            employment_type='Full Time',
            notes='Test agent with full profile'
        )
        print(f"✓ Created full agent profile for: {test_user.first_name} {test_user.last_name}")
    else:
        print(f"✓ Agent profile already exists for: {test_user.first_name} {test_user.last_name}")
    
    print("\n=== TEST DATA CREATION COMPLETE ===")
    print("You should now see:")
    print("- 3 users with Agent role")
    print("- 1 user with full agent profile (John Agent)")
    print("- 2 users with Agent role but no profile (Jane Delivery, Mike Courier)")
    print("- 4 offices in the main office system")
    print("- Offices have proper UUIDs and can be selected in agent creation")

if __name__ == "__main__":
    create_test_data() 