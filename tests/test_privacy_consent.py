from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from app.models.project import Project

User = get_user_model()

class PrivacyConsentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        self.other_user = User.objects.create_user(username='otheruser', email='other@example.com', password='password123')
        
        self.project = Project.objects.create(
            user=self.user,
            name="Test Project",
            llm_consent=False
        )
        
        self.client = APIClient()

    def test_update_consent_success(self):
        """Test that a user can update consent for their project."""
        self.client.force_authenticate(user=self.user)
        data = {
            "project_id": self.project.id,
            "consent": True
        }
        response = self.client.post('/api/privacy-consent/llm/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Refresh from DB
        self.project.refresh_from_db()
        self.assertTrue(self.project.llm_consent)
        
        # Test toggling back to false
        data["consent"] = False
        response = self.client.post('/api/privacy-consent/llm/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertFalse(self.project.llm_consent)

    def test_update_consent_invalid_project(self):
        """Test updating a non-existent project."""
        self.client.force_authenticate(user=self.user)
        data = {
            "project_id": 99999,
            "consent": True
        }
        response = self.client.post('/api/privacy-consent/llm/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_consent_unauthorized_project(self):
        """Test updating a project belonging to another user."""
        self.client.force_authenticate(user=self.other_user)
        data = {
            "project_id": self.project.id,
            "consent": True
        }
        response = self.client.post('/api/privacy-consent/llm/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_access(self):
        """Test unauthenticated access."""
        data = {
            "project_id": self.project.id,
            "consent": True
        }
        response = self.client.post('/api/privacy-consent/llm/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
