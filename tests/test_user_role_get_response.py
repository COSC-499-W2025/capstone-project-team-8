"""
TDD Cycle 5 – user_role is present in GET responses.

Tests cover:
- /api/projects/         (list)  → each project object contains user_role
- /api/projects/<id>/   (detail) → response contains user_role
- Correct value is returned in both endpoints
"""
import os
import sys
import django

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
django.setup()

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from app.models import Project
from django.contrib.auth import get_user_model

User = get_user_model()


class GetUserRoleResponseTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='getuser', email='get@test.com', password='pass'
        )
        self.project = Project.objects.create(
            user=self.user,
            name='GET Role Project',
            classification_type='coding',
            classification_confidence=0.9,
            user_role='lead_developer',
        )
        self.list_url   = reverse('projects-list')
        self.detail_url = reverse('projects-detail', args=[self.project.id])

    # ------------------------------------------------------------------ #
    # List endpoint
    # ------------------------------------------------------------------ #

    def test_list_response_contains_user_role_key(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, 200)
        project_data = resp.json()['projects'][0]
        self.assertIn('user_role', project_data)

    def test_list_response_user_role_has_correct_value(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(self.list_url)
        project_data = resp.json()['projects'][0]
        self.assertEqual(project_data['user_role'], 'lead_developer')

    def test_list_response_user_role_updates_after_patch(self):
        """After patching, the list should reflect the new role."""
        self.client.force_authenticate(user=self.user)
        self.client.patch(self.detail_url, data={'user_role': 'contributor'}, format='json')
        resp = self.client.get(self.list_url)
        project_data = resp.json()['projects'][0]
        self.assertEqual(project_data['user_role'], 'contributor')

    # ------------------------------------------------------------------ #
    # Detail endpoint
    # ------------------------------------------------------------------ #

    def test_detail_response_contains_user_role_key(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(self.detail_url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('user_role', resp.json())

    def test_detail_response_user_role_has_correct_value(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(self.detail_url)
        self.assertEqual(resp.json()['user_role'], 'lead_developer')

    def test_detail_response_user_role_default_is_other(self):
        """A project with no explicit role set should return 'other'."""
        plain = Project.objects.create(
            user=self.user,
            name='No Role Project',
            classification_type='coding',
        )
        url = reverse('projects-detail', args=[plain.id])
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(url)
        self.assertEqual(resp.json()['user_role'], 'other')
