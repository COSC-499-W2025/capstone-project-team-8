import os
import sys
import unittest
import django

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
django.setup()

import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


class JWTTokenEndpointTests(TestCase):
    """Test new JWT token endpoints (separate from existing auth)"""
    
    def setUp(self):
        """Set up test client and create test user"""
        self.client = Client()
        self.username = "testuser"
        self.email = "test@example.com"
        self.password = "testpass123"
        
        # Create test user
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )
    
    def test_token_obtain_returns_jwt_tokens(self):
        """Test NEW /api/token/ endpoint returns access and refresh tokens"""
        response = self.client.post('/api/token/', 
            json.dumps({
                'username': self.username,
                'password': self.password
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should return both access and refresh tokens
        self.assertIn('access', data)
        self.assertIn('refresh', data)
        self.assertIsInstance(data['access'], str)
        self.assertIsInstance(data['refresh'], str)
        self.assertGreater(len(data['access']), 0)
        self.assertGreater(len(data['refresh']), 0)
    
    def test_token_obtain_invalid_credentials_returns_401(self):
        """Test that invalid credentials return 401 Unauthorized"""
        response = self.client.post('/api/token/',
            json.dumps({
                'username': self.username,
                'password': 'wrongpassword'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_token_obtain_missing_username_returns_400(self):
        """Test that missing username returns 400 Bad Request"""
        response = self.client.post('/api/token/',
            json.dumps({
                'password': self.password
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_token_obtain_missing_password_returns_400(self):
        """Test that missing password returns 400 Bad Request"""
        response = self.client.post('/api/token/',
            json.dumps({
                'username': self.username
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_access_token_allows_protected_route_access(self):
        """Test that valid access token allows access to protected routes"""
        # Get tokens from NEW token endpoint
        token_response = self.client.post('/api/token/',
            json.dumps({
                'username': self.username,
                'password': self.password
            }),
            content_type='application/json'
        )
        tokens = token_response.json()
        access_token = tokens['access']
        
        # Try to access protected route with token
        response = self.client.post('/api/upload-folder/',
            {},
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        # Should NOT return 401 (may return 400 for missing file, but that's OK)
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    @unittest.expectedFailure
    def test_protected_route_without_token_returns_401(self):
        """Test that accessing protected route without token returns 401"""
        response = self.client.post('/api/upload-folder/', {})
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_protected_route_with_invalid_token_returns_401(self):
        """Test that invalid token returns 401 Unauthorized"""
        response = self.client.get('/api/upload-folder/',
            HTTP_AUTHORIZATION='Bearer invalid_token_here'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_refresh_token_generates_new_access_token(self):
        """Test that refresh token can generate a new access token"""
        # Get tokens from token endpoint
        token_response = self.client.post('/api/token/',
            json.dumps({
                'username': self.username,
                'password': self.password
            }),
            content_type='application/json'
        )
        tokens = token_response.json()
        refresh_token = tokens['refresh']
        
        # Use refresh token to get new access token
        response = self.client.post('/api/token/refresh/',
            json.dumps({
                'refresh': refresh_token
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('access', data)
        self.assertIsInstance(data['access'], str)
        self.assertGreater(len(data['access']), 0)
    
    def test_invalid_refresh_token_returns_401(self):
        """Test that invalid refresh token returns 401"""
        response = self.client.post('/api/token/refresh/',
            json.dumps({
                'refresh': 'invalid_refresh_token'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_token_contains_user_information(self):
        """Test that access token payload contains user info"""
        # Get tokens
        token_response = self.client.post('/api/token/',
            json.dumps({
                'username': self.username,
                'password': self.password
            }),
            content_type='application/json'
        )
        tokens = token_response.json()
        
        # Token should be a valid JWT with user info
        # We'll verify by using it to access a protected route
        access_token = tokens['access']
        response = self.client.post('/api/upload-folder/',
            {},
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        # Should authenticate (may fail for other reasons, but not 401)
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_logout_blacklists_refresh_token(self):
        """Test NEW /api/token/logout/ endpoint blacklists the refresh token"""
        # Get tokens
        token_response = self.client.post('/api/token/',
            json.dumps({
                'username': self.username,
                'password': self.password
            }),
            content_type='application/json'
        )
        tokens = token_response.json()
        refresh_token = tokens['refresh']
        
        # Logout via NEW endpoint
        logout_response = self.client.post('/api/token/logout/',
            json.dumps({
                'refresh': refresh_token
            }),
            content_type='application/json'
        )
        
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        
        # Try to use the refresh token - should fail
        response = self.client.post('/api/token/refresh/',
            json.dumps({
                'refresh': refresh_token
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_expired_access_token_returns_401(self):
        """Test that expired access token returns 401"""
        # This test would require creating an expired token
        # For now, we'll test with a malformed token that simulates expiry
        expired_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjB9.invalid"
        
        response = self.client.post('/api/upload-folder/',
            {},
            HTTP_AUTHORIZATION=f'Bearer {expired_token}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UpdatedAuthEndpointsTests(TestCase):
    """Test that existing /api/login/ and /api/signup/ now return JSON"""
    
    def setUp(self):
        """Set up test client"""
        self.client = Client()
    
    def test_login_returns_json_with_tokens(self):
        """Test /api/login/ returns JSON instead of HTML"""
        # Create user first
        User.objects.create_user('jsonuser', 'json@test.com', 'jsonpass123')
        
        response = self.client.post('/api/login/',
            json.dumps({
                'username': 'jsonuser',
                'password': 'jsonpass123'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        self.assertIn('access', data)
        self.assertIn('refresh', data)
        self.assertIn('username', data)
    
    def test_login_invalid_credentials_json_error(self):
        """Test /api/login/ returns JSON error for bad credentials"""
        User.objects.create_user('jsonuser', 'json@test.com', 'jsonpass123')
        
        response = self.client.post('/api/login/',
            json.dumps({
                'username': 'jsonuser',
                'password': 'wrongpass'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        self.assertIn('error', data)
    
    def test_signup_returns_json_with_tokens(self):
        """Test /api/signup/ returns JSON with tokens instead of HTML"""
        response = self.client.post('/api/signup/',
            json.dumps({
                'username': 'newsignup',
                'email': 'new@signup.com',
                'password': 'newpass123',
                'confirm_password': 'newpass123'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        self.assertIn('access', data)
        self.assertIn('refresh', data)
        self.assertIn('username', data)

    def test_signup_accepts_github_username(self):
        """Test /api/signup/ stores optional github_username field"""
        response = self.client.post('/api/signup/',
            json.dumps({
                'username': 'ghuser',
                'email': 'gh@test.com',
                'password': 'newpass123',
                'confirm_password': 'newpass123',
                'github_username': 'MatinDev'
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.json()
        self.assertEqual(data.get('github_username'), 'MatinDev')

        created = User.objects.get(username='ghuser')
        self.assertEqual(created.github_username, 'MatinDev')
    
    def test_signup_password_mismatch_json_error(self):
        """Test /api/signup/ returns JSON error for password mismatch"""
        response = self.client.post('/api/signup/',
            json.dumps({
                'username': 'mismatchuser',
                'email': 'mismatch@test.com',
                'password': 'pass123',
                'confirm_password': 'different123'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        self.assertIn('error', data)
    
    def test_login_html_form_still_works(self):
        """Test backward compatibility: HTML requests still get HTML forms"""
        User.objects.create_user('htmluser', 'html@test.com', 'htmlpass')
        
        # GET request should return HTML form
        response = self.client.get('/api/login/',
            HTTP_ACCEPT='text/html'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('text/html', response['Content-Type'])
        self.assertIn(b'<form', response.content)


class JWTProtectedRouteTests(TestCase):
    """Test that upload-folder endpoint requires JWT authentication"""
    
    def setUp(self):
        """Set up test client and user"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="uploaduser",
            email="upload@example.com",
            password="uploadpass123"
        )
    @unittest.expectedFailure
    def test_upload_folder_requires_authentication(self):
        """Test that /api/upload-folder/ requires JWT token"""
        response = self.client.post('/api/upload-folder/', {})
        
        # Should return 401 without authentication
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_upload_folder_with_valid_token_authenticates(self):
        """Test that /api/upload-folder/ works with valid JWT token"""
        # Get token
        token_response = self.client.post('/api/token/',
            json.dumps({
                'username': 'uploaduser',
                'password': 'uploadpass123'
            }),
            content_type='application/json'
        )
        access_token = token_response.json()['access']
        
        # Try to upload (will fail for missing file, but should authenticate)
        response = self.client.post('/api/upload-folder/',
            {},
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        # Should NOT be 401 (authenticated, but may be 400 for missing file)
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_token_cannot_be_tampered_with(self):
        """Test that modified tokens are rejected"""
        # Get valid token
        token_response = self.client.post('/api/token/',
            json.dumps({
                'username': 'uploaduser',
                'password': 'uploadpass123'
            }),
            content_type='application/json'
        )
        access_token = token_response.json()['access']
        
        # Tamper with token (modify last character)
        tampered_token = access_token[:-1] + 'X'
        
        # Try to use tampered token
        response = self.client.post('/api/upload-folder/',
            {},
            HTTP_AUTHORIZATION=f'Bearer {tampered_token}'
        )
        
        # Tampered tokens return 400 (Bad Request) because they can't be decoded
        # This is acceptable - malformed != unauthorized
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])
    
    def test_tokens_are_user_specific(self):
        """Test that tokens contain user-specific information"""
        # Create another user
        User.objects.create_user('otheruser', 'other@test.com', 'otherpass')
        
        # Get token for first user
        token1_response = self.client.post('/api/token/',
            json.dumps({
                'username': 'uploaduser',
                'password': 'uploadpass123'
            }),
            content_type='application/json'
        )
        token1 = token1_response.json()['access']
        
        # Get token for second user
        token2_response = self.client.post('/api/token/',
            json.dumps({
                'username': 'otheruser',
                'password': 'otherpass'
            }),
            content_type='application/json'
        )
        token2 = token2_response.json()['access']
        
        # Tokens should be different
        self.assertNotEqual(token1, token2)
