import os
import sys
import django

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
django.setup()

from django.test import TestCase
from app.models import User  # Use custom User model


class UserDatabaseTest(TestCase):
    """Test that users can be created and saved to MySQL database"""
    
    def test_create_user_in_database(self):
        """Test creating a user and saving to MySQL"""
        # Create a user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Verify user was saved to database
        self.assertIsNotNone(user.id)  # Has database ID
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        
        # Verify we can retrieve it from database
        retrieved_user = User.objects.get(username='testuser')
        self.assertEqual(retrieved_user.id, user.id)
        self.assertEqual(retrieved_user.email, 'test@example.com')
    
    def test_create_multiple_users(self):
        """Test creating multiple users in MySQL"""
        # Create multiple users
        user1 = User.objects.create_user(username='user1', email='user1@test.com', password='pass1')
        user2 = User.objects.create_user(username='user2', email='user2@test.com', password='pass2')
        user3 = User.objects.create_user(username='user3', email='user3@test.com', password='pass3')
        
        # Verify count in database
        total_users = User.objects.count()
        self.assertEqual(total_users, 3)
        
        # Verify all users exist
        self.assertTrue(User.objects.filter(username='user1').exists())
        self.assertTrue(User.objects.filter(username='user2').exists())
        self.assertTrue(User.objects.filter(username='user3').exists())
