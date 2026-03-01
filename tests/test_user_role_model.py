"""
TDD Cycle 1 – user_role field on the Project model.

Tests cover:
- Field exists with the correct default
- All valid role choices are accepted
- The field is persisted and retrieved correctly
"""
import os
import sys
import django

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
django.setup()

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model

from app.models import Project

User = get_user_model()

VALID_ROLES = [
    'solo_developer',
    'lead_developer',
    'contributor',
    'frontend_developer',
    'backend_developer',
    'full_stack_developer',
    'designer',
    'writer',
    'architect',
    'other',
]


def _make_user(username='roleuser', email='roleuser@test.com'):
    return User.objects.create_user(username=username, email=email, password='pass')


def _make_project(user, **kwargs):
    defaults = dict(
        name='Test Project',
        classification_type='coding',
        classification_confidence=0.9,
    )
    defaults.update(kwargs)
    return Project.objects.create(user=user, **defaults)


class ProjectUserRoleFieldTest(TestCase):
    """The Project model must expose a user_role field."""

    def setUp(self):
        self.user = _make_user()

    # ------------------------------------------------------------------ #
    # Field existence & default
    # ------------------------------------------------------------------ #

    def test_project_has_user_role_field(self):
        """Project model must have a user_role attribute."""
        project = _make_project(self.user)
        self.assertTrue(
            hasattr(project, 'user_role'),
            "Project model is missing the 'user_role' field.",
        )

    def test_user_role_defaults_to_other(self):
        """When no role is supplied, user_role should default to 'other'."""
        project = _make_project(self.user)
        self.assertEqual(project.user_role, 'other')

    # ------------------------------------------------------------------ #
    # Persistence
    # ------------------------------------------------------------------ #

    def test_user_role_persists_to_database(self):
        """A set user_role must survive a round-trip to the database."""
        project = _make_project(self.user, user_role='lead_developer')
        refreshed = Project.objects.get(pk=project.pk)
        self.assertEqual(refreshed.user_role, 'lead_developer')

    def test_user_role_can_be_updated(self):
        """user_role must be updatable via .save()."""
        project = _make_project(self.user)
        project.user_role = 'contributor'
        project.save(update_fields=['user_role'])
        refreshed = Project.objects.get(pk=project.pk)
        self.assertEqual(refreshed.user_role, 'contributor')

    # ------------------------------------------------------------------ #
    # All valid roles round-trip
    # ------------------------------------------------------------------ #

    def test_all_valid_roles_are_accepted(self):
        """Every defined role choice must be storable and retrievable."""
        for role in VALID_ROLES:
            with self.subTest(role=role):
                project = _make_project(self.user, user_role=role)
                refreshed = Project.objects.get(pk=project.pk)
                self.assertEqual(refreshed.user_role, role)
                project.delete()

    # ------------------------------------------------------------------ #
    # Null / blank safety
    # ------------------------------------------------------------------ #

    def test_user_role_is_not_null_in_database(self):
        """user_role should never be NULL – default keeps it non-null."""
        project = _make_project(self.user)
        self.assertIsNotNone(project.user_role)
        self.assertNotEqual(project.user_role, '')
