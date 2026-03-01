"""
TDD Cycle 4 – PATCH /api/projects/<id>/ accepts and validates user_role.

Tests cover:
- PATCHing user_role to a valid value succeeds (200) and persists
- PATCHing with an invalid role is rejected with 400
- PATCHing user_role on another user's project returns 404
- user_role can be changed alongside name/description in one request
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
from django.utils import timezone

from app.models import Project
from django.contrib.auth import get_user_model

User = get_user_model()

VALID_ROLES = [
    'solo_developer', 'lead_developer', 'contributor',
    'frontend_developer', 'backend_developer', 'full_stack_developer',
    'designer', 'writer', 'architect', 'other',
]


class PatchUserRoleEndpointTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='patchuser', email='patch@test.com', password='pass'
        )
        self.other = User.objects.create_user(
            username='otheruser', email='other@test.com', password='pass'
        )
        self.project = Project.objects.create(
            user=self.user,
            name='Patch Test Project',
            classification_type='coding',
            classification_confidence=0.9,
            user_role='other',
        )
        self.url = reverse('projects-detail', args=[self.project.id])

    # ------------------------------------------------------------------ #
    # Happy path – valid roles
    # ------------------------------------------------------------------ #

    def test_patch_valid_role_returns_200(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.patch(self.url, data={'user_role': 'lead_developer'}, format='json')
        self.assertEqual(resp.status_code, 200)

    def test_patch_valid_role_persists_to_db(self):
        self.client.force_authenticate(user=self.user)
        self.client.patch(self.url, data={'user_role': 'frontend_developer'}, format='json')
        self.project.refresh_from_db()
        self.assertEqual(self.project.user_role, 'frontend_developer')

    def test_patch_response_includes_ok_true(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.patch(self.url, data={'user_role': 'contributor'}, format='json')
        self.assertEqual(resp.json().get('ok'), True)

    def test_patch_all_valid_roles_are_accepted(self):
        self.client.force_authenticate(user=self.user)
        for role in VALID_ROLES:
            with self.subTest(role=role):
                resp = self.client.patch(self.url, data={'user_role': role}, format='json')
                self.assertEqual(resp.status_code, 200, f"Role '{role}' was rejected")

    # ------------------------------------------------------------------ #
    # Validation – invalid role
    # ------------------------------------------------------------------ #

    def test_patch_invalid_role_returns_400(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.patch(self.url, data={'user_role': 'galaxy_brain'}, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_patch_invalid_role_does_not_change_existing_role(self):
        self.project.user_role = 'architect'
        self.project.save()
        self.client.force_authenticate(user=self.user)
        self.client.patch(self.url, data={'user_role': 'not_real'}, format='json')
        self.project.refresh_from_db()
        self.assertEqual(self.project.user_role, 'architect')

    # ------------------------------------------------------------------ #
    # Authorisation
    # ------------------------------------------------------------------ #

    def test_patch_other_users_project_returns_404(self):
        self.client.force_authenticate(user=self.other)
        resp = self.client.patch(self.url, data={'user_role': 'contributor'}, format='json')
        self.assertEqual(resp.status_code, 404)

    # ------------------------------------------------------------------ #
    # Combined update
    # ------------------------------------------------------------------ #

    def test_patch_role_and_name_together(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.patch(
            self.url,
            data={'user_role': 'backend_developer', 'name': 'Renamed Project'},
            format='json',
        )
        self.assertEqual(resp.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.user_role, 'backend_developer')
        self.assertEqual(self.project.name, 'Renamed Project')
