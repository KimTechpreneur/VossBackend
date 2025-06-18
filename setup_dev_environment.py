#!/usr/bin/env python
"""
Development Environment Setup Script for VOSS
This script sets up a complete development environment with:
- Database migrations
- Default roles and permissions
- Sample units and offices
- Comprehensive test users with proper role assignments
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VossBackend.settings')
    django.setup()

def run_command(command_list):
    """Run a Django management command"""
    print(f"\n🔄 Running: {' '.join(command_list)}")
    try:
        execute_from_command_line(['manage.py'] + command_list)
        print(f"✅ Successfully completed: {' '.join(command_list)}")
        return True
    except Exception as e:
        print(f"❌ Error running {' '.join(command_list)}: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up VOSS Development Environment")
    print("=" * 50)
    
    # Setup Django
    setup_django()
    
    # Commands to run in order
    setup_commands = [
        # Database setup
        ['migrate'],
        
        # Create permissions first
        ['create_permissions'],
        
        # Create default roles
        ['create_default_roles'],
        
        # Assign permissions to roles
        ['assign_role_permissions'],
        
        # Create sample units
        ['create_sample_units'],
        
        # Create sample offices
        ['create_sample_offices'],
        
        # Create comprehensive development users
        ['create_dev_users', '--reset'],
        
        # Collect static files (if needed)
        # ['collectstatic', '--noinput'],
    ]
    
    success_count = 0
    total_commands = len(setup_commands)
    
    for command in setup_commands:
        if run_command(command):
            success_count += 1
        else:
            print(f"\n⚠️  Command failed, but continuing with setup...")
    
    print("\n" + "=" * 50)
    print("🎉 Development Environment Setup Complete!")
    print(f"✅ {success_count}/{total_commands} commands completed successfully")
    
    if success_count == total_commands:
        print("\n🌟 Your development environment is ready!")
        print("\n📋 What's been set up:")
        print("   • Database migrations applied")
        print("   • Comprehensive permissions system")
        print("   • Role-based access control")
        print("   • Sample units and offices")
        print("   • Test users with proper role assignments")
        
        print("\n🔑 Development Login Credentials:")
        print("   • Global Admin: admin@example.com / admin123")
        print("   • Unit Head: unithead@example.com / unit123")
        print("   • Staff Member: staff@example.com / staff123")
        print("   • Field Agent: agent@example.com / agent123")
        print("   • System Auditor: auditor@example.com / audit123")
        print("   • Basic User: user@example.com / user123")
        
        print("\n🌐 Access your application:")
        print("   • Frontend: http://localhost:3000/dev-login")
        print("   • Backend Admin: http://localhost:8000/admin")
        print("   • API Docs: http://localhost:8000/api/docs/")
        
        print("\n🧪 Testing Instructions:")
        print("   1. Start your Django backend: python manage.py runserver")
        print("   2. Start your Next.js frontend: npm run dev")
        print("   3. Visit /dev-login for quick role-based testing")
        print("   4. Test different role permissions across the system")
        
    else:
        print(f"\n⚠️  Setup completed with {total_commands - success_count} errors")
        print("   Please check the error messages above and resolve any issues")
        print("   You may need to run individual commands manually")
    
    print("\n" + "=" * 50)

if __name__ == '__main__':
    main() 