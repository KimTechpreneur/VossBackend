from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from .models import Office
from users.models import User, Unit

class OfficeViewSetTests(APITestCase):
    def setUp(self):
        # Create test units
        self.unit1 = Unit.objects.create(name='Test Unit 1')
        self.unit2 = Unit.objects.create(name='Test Unit 2')
        
        # Create test users
        self.admin_user = User.objects.create_user(
            email='admin@test.com',
            password='testpass123',
            is_staff=True
        )
        self.unit_admin = User.objects.create_user(
            email='unitadmin@test.com',
            password='testpass123',
            unit=self.unit1
        )
        self.regular_user = User.objects.create_user(
            email='user@test.com',
            password='testpass123',
            unit=self.unit1
        )
        
        # Create test offices
        self.office1 = Office.objects.create(
            office_name='Office 1',
            unit=self.unit1,
            head_of_office=self.unit_admin
        )
        self.office2 = Office.objects.create(
            office_name='Office 2',
            unit=self.unit1
        )
        self.office3 = Office.objects.create(
            office_name='Office 3',
            unit=self.unit2
        )
        
        # Add staff member to office
        self.office1.staff_members.add(self.regular_user)
        
        self.client = APIClient()
        
    def test_get_offices_by_unit(self):
        """Test getting offices by unit"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Test with unit1
        url = reverse('office-by-unit')
        response = self.client.get(url, {'unit_id': self.unit1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should return 2 offices
        
        # Test with unit2
        response = self.client.get(url, {'unit_id': self.unit2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Should return 1 office
        
        # Test without unit_id
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_get_offices_by_unit_with_user_filter(self):
        """Test getting offices by unit with user filtering"""
        self.client.force_authenticate(user=self.regular_user)
        
        url = reverse('office-by-unit')
        response = self.client.get(url, {
            'unit_id': self.unit1.id,
            'user_id': self.regular_user.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Should only return office1
        self.assertEqual(response.data[0]['office_name'], 'Office 1')
        
    def test_get_offices_by_unit_as_unit_admin(self):
        """Test getting offices by unit as unit admin"""
        self.client.force_authenticate(user=self.unit_admin)
        
        url = reverse('office-by-unit')
        response = self.client.get(url, {
            'unit_id': self.unit1.id,
            'user_id': self.unit_admin.id
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should return all offices in unit1
