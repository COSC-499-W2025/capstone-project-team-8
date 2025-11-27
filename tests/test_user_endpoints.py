"""
Tests for the user profile API endpoints (/api/users/me/ and public user view)
"""

import os
import sys
import django
import json
import uuid

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


class UserApiTests(TestCase):
    """Simple tests for user API endpoints"""

    def setUp(self):
        self.client = Client()

        unique_id = str(uuid.uuid4())[:8]
        self.username = f"apiuser_{unique_id}"
        self.email = f"apiuser_{unique_id}@example.com"
        self.password = "testpass123"

        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password,
        )

        # Authenticate and set Bearer token header
        resp = self.client.post('/api/token/',
            json.dumps({'username': self.username, 'password': self.password}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        tokens = resp.json()
        self.access_token = tokens['access']
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {self.access_token}'

    def test_put_updates_github_username_and_bio(self):
        # Ensure initial values are empty
        u = User.objects.get(username=self.username)
        self.assertEqual(u.github_username, "")
        self.assertEqual(u.bio, "")

        payload = json.dumps({
            'user': {
                'github_username': 'testuser',
                'bio': 'New bio'
            }
        })

        response = self.client.put('/api/users/me/', payload, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertIn('user', data)
        returned = data['user']
        self.assertEqual(returned.get('github_username'), 'testuser')
        self.assertEqual(returned.get('bio'), 'New bio')

        # Confirm persisted to DB
        u.refresh_from_db()
        self.assertEqual(u.github_username, 'testuser')
        self.assertEqual(u.bio, 'New bio')

    def test_get_public_user_view(self):
        # Set some public fields then GET the public view
        self.user.bio = 'public bio'
        self.user.save()

        response = self.client.get(f'/api/users/{self.username}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('user', data)
        self.assertEqual(data['user']['username'], self.username)
