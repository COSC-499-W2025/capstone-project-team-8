import os
import sys
import django

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
django.setup()

from django.test import TestCase
from django.contrib.auth import authenticate
from django.db import IntegrityError
from app.models import User


class CustomUserModelTest(TestCase):
    """Test custom User model matches auth.py requirements"""
    
    def test_create_user_with_username_email_password(self):
        """Test User.objects.create_user() works like auth.py expects (line 23)"""
        # This is exactly how auth.py creates users
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Verify user was created
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        
        # Verify password is hashed (not plain text)
        self.assertNotEqual(user.password, 'testpass123')
        self.assertTrue(user.password.startswith('pbkdf2_sha256'))  # Django's hash format
    
    def test_username_is_unique(self):
        """Test IntegrityError raised for duplicate username (auth.py line 24)"""
        User.objects.create_user(
            username='duplicate',
            email='first@example.com',
            password='pass1'
        )
        
        # Attempting to create another user with same username should fail
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='duplicate',
                email='different@example.com',
                password='pass2'
            )
    
    def test_authenticate_with_username_and_password(self):
        """Test authenticate() works like LoginView expects (auth.py line 89)"""
        # Create user
        User.objects.create_user(
            username='authuser',
            email='auth@example.com',
            password='correctpass'
        )
        
        # Test successful authentication
        user = authenticate(username='authuser', password='correctpass')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'authuser')
        
        # Test failed authentication
        failed_user = authenticate(username='authuser', password='wrongpass')
        self.assertIsNone(failed_user)
    
    def test_user_has_username_attribute(self):
        """Test user.username exists for session storage (auth.py line 30)"""
        user = User.objects.create_user(
            username='sessionuser',
            email='session@example.com',
            password='pass123'
        )
        
        # auth.py stores: request.session['username'] = username
        # So user must have accessible username attribute
        self.assertTrue(hasattr(user, 'username'))
        self.assertEqual(user.username, 'sessionuser')
    
    def test_user_string_representation(self):
        """Test __str__ returns username for display"""
        user = User.objects.create_user(
            username='displayuser',
            email='display@example.com',
            password='pass123'
        )
        
        self.assertEqual(str(user), 'displayuser')
    
    def test_email_is_normalized(self):
        """Test email domain is lowercased"""
        user = User.objects.create_user(
            username='emailtest',
            email='Test@EXAMPLE.COM',
            password='pass123'
        )
        
        # Domain should be normalized to lowercase
        self.assertEqual(user.email, 'Test@example.com')
    
    def test_create_user_without_username_fails(self):
        """Test that username is required"""
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(
                username='',
                email='test@example.com',
                password='pass123'
            )
        
        self.assertIn('username', str(context.exception).lower())
    
    def test_create_user_without_email_fails(self):
        """Test that email is required"""
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(
                username='testuser',
                email='',
                password='pass123'
            )
        
        self.assertIn('email', str(context.exception).lower())
    
    def test_create_superuser(self):
        """Test creating admin user for Django admin"""
        superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass'
        )
        
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)
    
    def test_user_can_be_retrieved_from_database(self):
        """Test user persistence in MySQL"""
        user = User.objects.create_user(
            username='persistent',
            email='persist@example.com',
            password='pass123'
        )
        
        # Retrieve from database
        retrieved_user = User.objects.get(username='persistent')
        self.assertEqual(retrieved_user.id, user.id)
        self.assertEqual(retrieved_user.email, 'persist@example.com')
    
    def test_multiple_users_can_exist(self):
        """Test multiple users in database"""
        User.objects.create_user('user1', 'user1@test.com', 'pass1')
        User.objects.create_user('user2', 'user2@test.com', 'pass2')
        User.objects.create_user('user3', 'user3@test.com', 'pass3')
        
        self.assertEqual(User.objects.count(), 3)
        self.assertTrue(User.objects.filter(username='user1').exists())
        self.assertTrue(User.objects.filter(username='user2').exists())
        self.assertTrue(User.objects.filter(username='user3').exists())
