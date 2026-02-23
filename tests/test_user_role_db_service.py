"""
TDD Cycle 3 – user_role is auto-inferred during project creation
via ProjectDatabaseService.

Tests verify that after save_project_analysis() completes,
the resulting Project objects have a user_role that matches
the expected inference from roles service.
"""
import os
import sys
import django

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model

from app.models import Project
from app.services.database_service import ProjectDatabaseService

User = get_user_model()


def _make_user(username='dbuser', email='dbuser@test.com'):
    return User.objects.create_user(
        username=username, email=email,
        password='pass', github_email=email
    )


def _solo_analysis(name='solo-project', classification='coding', languages=None):
    """Minimal analysis payload – no contributors → non-collaborative."""
    return {
        'projects': [{
            'id': 0,
            'root': name,
            'collaborative': False,
            'classification': {
                'type': classification,
                'confidence': 0.9,
                'languages': languages or [],
                'frameworks': [],
            },
            'files': {'code': [], 'content': [], 'image': [], 'unknown': []},
            'contributors': [],
        }],
        'overall': {
            'classification': classification,
            'confidence': 0.9,
        },
    }


def _collab_analysis(name='collab-project', classification='coding',
                     languages=None, user_email='dbuser@test.com',
                     user_commits=80, other_commits=20):
    """Analysis payload with two contributors – collaborative project."""
    total = user_commits + other_commits
    user_pct   = (user_commits / total) * 100 if total else 0
    other_pct  = (other_commits / total) * 100 if total else 0
    return {
        'projects': [{
            'id': 1,
            'root': name,
            'collaborative': True,
            'classification': {
                'type': classification,
                'confidence': 0.85,
                'languages': languages or [],
                'frameworks': [],
            },
            'files': {'code': [], 'content': [], 'image': [], 'unknown': []},
            'contributors': [
                {
                    'name': 'Test User',
                    'email': user_email,
                    'commits': user_commits,
                    'percent_commits': user_pct,
                    'lines_added': 500,
                    'lines_deleted': 100,
                },
                {
                    'name': 'Other Dev',
                    'email': 'other@example.com',
                    'commits': other_commits,
                    'percent_commits': other_pct,
                    'lines_added': 100,
                    'lines_deleted': 20,
                },
            ],
        }],
        'overall': {
            'classification': classification,
            'confidence': 0.85,
        },
    }


class DatabaseServiceAutoInferRoleTest(TestCase):
    """ProjectDatabaseService must populate user_role on created projects."""

    def setUp(self):
        self.service = ProjectDatabaseService()
        self.user = _make_user()

    # ------------------------------------------------------------------ #
    # Solo projects
    # ------------------------------------------------------------------ #

    def test_solo_coding_project_gets_solo_developer_role(self):
        analysis = _solo_analysis(classification='coding')
        projects = self.service.save_project_analysis(self.user, analysis)
        self.assertEqual(projects[0].user_role, 'solo_developer')

    def test_solo_writing_project_gets_writer_role(self):
        analysis = _solo_analysis(classification='writing')
        projects = self.service.save_project_analysis(self.user, analysis)
        self.assertEqual(projects[0].user_role, 'writer')

    def test_solo_art_project_gets_designer_role(self):
        analysis = _solo_analysis(classification='art')
        projects = self.service.save_project_analysis(self.user, analysis)
        self.assertEqual(projects[0].user_role, 'designer')

    # ------------------------------------------------------------------ #
    # Collaborative – lead
    # ------------------------------------------------------------------ #

    def test_collab_coding_lead_gets_lead_developer_role(self):
        """User has 80 % of commits → lead_developer."""
        analysis = _collab_analysis(
            user_email=self.user.email, user_commits=80, other_commits=20
        )
        projects = self.service.save_project_analysis(self.user, analysis)
        self.assertEqual(projects[0].user_role, 'lead_developer')

    # ------------------------------------------------------------------ #
    # Collaborative – contributor
    # ------------------------------------------------------------------ #

    def test_collab_coding_contributor_gets_contributor_role(self):
        """User has 20 % of commits and no language hints → contributor."""
        analysis = _collab_analysis(
            user_email=self.user.email, user_commits=20, other_commits=80,
            languages=[],
        )
        projects = self.service.save_project_analysis(self.user, analysis)
        self.assertEqual(projects[0].user_role, 'contributor')

    def test_collab_coding_frontend_contributor_gets_frontend_role(self):
        """Low-contribution user with JS/CSS/HTML → frontend_developer."""
        analysis = _collab_analysis(
            user_email=self.user.email, user_commits=15, other_commits=85,
            languages=['JavaScript', 'CSS', 'HTML'],
        )
        projects = self.service.save_project_analysis(self.user, analysis)
        self.assertEqual(projects[0].user_role, 'frontend_developer')

    def test_collab_coding_backend_contributor_gets_backend_role(self):
        """Low-contribution user with Python/SQL → backend_developer."""
        analysis = _collab_analysis(
            user_email=self.user.email, user_commits=10, other_commits=90,
            languages=['Python', 'SQL'],
        )
        projects = self.service.save_project_analysis(self.user, analysis)
        self.assertEqual(projects[0].user_role, 'backend_developer')

    # ------------------------------------------------------------------ #
    # Persisted value
    # ------------------------------------------------------------------ #

    def test_user_role_is_persisted_to_database(self):
        """The inferred role must survive a DB round-trip."""
        analysis = _solo_analysis(classification='coding')
        projects = self.service.save_project_analysis(self.user, analysis)
        refreshed = Project.objects.get(pk=projects[0].pk)
        self.assertEqual(refreshed.user_role, 'solo_developer')
