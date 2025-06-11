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

def check_database_state():
    print("=== DATABASE STATE CHECK ===")
    
    # Check if Agent role exists
    try:
        agent_role = Role.objects.get(name='Agent')
        print(f"✓ Agent role exists: {agent_role.name}")
    except Role.DoesNotExist:
        print("✗ Agent role does not exist")
        print("Creating Agent role...")
        agent_role = Role.objects.create(
            name='Agent',
            description='Agent role for delivery agents',
            type='system'
        )
        print(f"✓ Created Agent role: {agent_role.name}")
    
    # Check users with Agent role
    users_with_agent_role = User.objects.filter(role=agent_role)
    print(f"\nUsers with Agent role: {users_with_agent_role.count()}")
    
    for user in users_with_agent_role:
        has_profile = hasattr(user, 'agent')
        print(f"- {user.first_name} {user.last_name} ({user.email}) - Has agent profile: {has_profile}")
    
    # Check agent profiles
    agents = Agent.objects.all()
    print(f"\nTotal agent profiles: {agents.count()}")
    
    for agent in agents:
        print(f"- {agent.user.first_name} {agent.user.last_name} ({agent.user.email}) - Status: {agent.status}")
    
    # Check all users
    all_users = User.objects.all()
    print(f"\nTotal users: {all_users.count()}")
    
    for user in all_users:
        role_name = user.role.name if user.role else "No role"
        print(f"- {user.first_name} {user.last_name} ({user.email}) - Role: {role_name}")

if __name__ == "__main__":
    check_database_state() 