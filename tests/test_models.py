import os
import sys
import django

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
django.setup()

from django.test import TestCase
from django.contrib.auth.models import User


class UserModelTest(TestCase):
    """Test suite for User model functionality"""
    
    def test_create_user(self):
        """Test creating a user with username, email, and password"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_user_string_representation(self):
        """Test the string representation of a user"""
        user = User.objects.create_user(
            username='john_doe',
            email='john@example.com',
            password='password123'
        )
        
        self.assertEqual(str(user), 'john_doe')
    
    def test_user_email_is_optional(self):
        """Test creating a user without an email"""
        user = User.objects.create_user(
            username='noemailuser',
            password='testpass123'
        )
        
        self.assertEqual(user.username, 'noemailuser')
        self.assertEqual(user.email, '')
    
    def test_create_superuser(self):
        """Test creating a superuser for admin access"""
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.assertEqual(superuser.username, 'admin')
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)
