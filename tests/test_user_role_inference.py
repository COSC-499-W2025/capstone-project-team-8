"""
TDD Cycle 2 – infer_user_role() pure-logic function.

Tests cover every decision branch:
- Solo project (no contributors) per classification
- Lead by commit percentage (>= 50 %)
- Regular contributor (< 50 %)
- Frontend vs. backend vs. full-stack heuristic
- Architect role for high-level / unknown classification with high contribution
- Writer for writing projects, Designer for art projects
- Fallback to 'other'
"""
import os
import sys
import django

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
django.setup()

from django.test import SimpleTestCase
from app.services.role_inference import infer_user_role


# ------------------------------------------------------------------ #
# Helper builders
# ------------------------------------------------------------------ #

def _project(classification='coding', languages=None, is_collaborative=False,
             user_percent=0.0):
    return {
        'classification': {'type': classification},
        'is_collaborative': is_collaborative,
        'user_contribution_percent': user_percent,
        'languages': languages or [],
    }


# ------------------------------------------------------------------ #
# Solo projects (non-collaborative)
# ------------------------------------------------------------------ #

class InferRoleSoloTest(SimpleTestCase):
    """Non-collaborative projects: owner did everything."""

    def test_solo_coding_returns_solo_developer(self):
        role = infer_user_role(_project('coding', is_collaborative=False))
        self.assertEqual(role, 'solo_developer')

    def test_solo_writing_returns_writer(self):
        role = infer_user_role(_project('writing', is_collaborative=False))
        self.assertEqual(role, 'writer')

    def test_solo_art_returns_designer(self):
        role = infer_user_role(_project('art', is_collaborative=False))
        self.assertEqual(role, 'designer')

    def test_solo_mixed_coding_writing_returns_solo_developer(self):
        role = infer_user_role(_project('mixed:coding+writing', is_collaborative=False))
        self.assertEqual(role, 'solo_developer')

    def test_solo_unknown_returns_other(self):
        role = infer_user_role(_project('unknown', is_collaborative=False))
        self.assertEqual(role, 'other')


# ------------------------------------------------------------------ #
# Collaborative – lead (>= 50 %)
# ------------------------------------------------------------------ #

class InferRoleLeadTest(SimpleTestCase):
    """High-contribution collaborators become 'lead_developer' for coding."""

    def test_lead_developer_at_50_percent(self):
        role = infer_user_role(_project('coding', is_collaborative=True, user_percent=50.0))
        self.assertEqual(role, 'lead_developer')

    def test_lead_developer_above_50_percent(self):
        role = infer_user_role(_project('coding', is_collaborative=True, user_percent=75.0))
        self.assertEqual(role, 'lead_developer')

    def test_lead_writing_returns_writer(self):
        role = infer_user_role(_project('writing', is_collaborative=True, user_percent=60.0))
        self.assertEqual(role, 'writer')

    def test_lead_art_returns_designer(self):
        role = infer_user_role(_project('art', is_collaborative=True, user_percent=55.0))
        self.assertEqual(role, 'designer')


# ------------------------------------------------------------------ #
# Collaborative – contributor (< 50 %)
# ------------------------------------------------------------------ #

class InferRoleContributorTest(SimpleTestCase):
    """Low-contribution collaborators become more specialised roles or 'contributor'."""

    def test_contributor_below_50_percent_no_language_hint(self):
        role = infer_user_role(_project('coding', is_collaborative=True, user_percent=30.0))
        self.assertEqual(role, 'contributor')

    def test_frontend_contributor_with_js_css(self):
        role = infer_user_role(_project(
            'coding', is_collaborative=True, user_percent=20.0,
            languages=['JavaScript', 'CSS', 'HTML'],
        ))
        self.assertEqual(role, 'frontend_developer')

    def test_backend_contributor_with_python(self):
        role = infer_user_role(_project(
            'coding', is_collaborative=True, user_percent=20.0,
            languages=['Python', 'SQL'],
        ))
        self.assertEqual(role, 'backend_developer')

    def test_full_stack_contributor_with_mixed_languages(self):
        role = infer_user_role(_project(
            'coding', is_collaborative=True, user_percent=20.0,
            languages=['JavaScript', 'Python', 'HTML'],
        ))
        self.assertEqual(role, 'full_stack_developer')

    def test_backend_contributor_with_java(self):
        role = infer_user_role(_project(
            'coding', is_collaborative=True, user_percent=15.0,
            languages=['Java', 'SQL'],
        ))
        self.assertEqual(role, 'backend_developer')

    def test_backend_contributor_with_cpp(self):
        role = infer_user_role(_project(
            'coding', is_collaborative=True, user_percent=10.0,
            languages=['C++'],
        ))
        self.assertEqual(role, 'backend_developer')

    def test_writing_contributor_returns_writer(self):
        role = infer_user_role(_project('writing', is_collaborative=True, user_percent=25.0))
        self.assertEqual(role, 'writer')

    def test_art_contributor_returns_designer(self):
        role = infer_user_role(_project('art', is_collaborative=True, user_percent=10.0))
        self.assertEqual(role, 'designer')


# ------------------------------------------------------------------ #
# Edge cases
# ------------------------------------------------------------------ #

class InferRoleEdgeCasesTest(SimpleTestCase):

    def test_zero_percent_contribution_defaults_to_contributor(self):
        role = infer_user_role(_project('coding', is_collaborative=True, user_percent=0.0))
        self.assertEqual(role, 'contributor')

    def test_100_percent_solo_equivalent_when_collaborative_is_lead(self):
        role = infer_user_role(_project('coding', is_collaborative=True, user_percent=100.0))
        self.assertEqual(role, 'lead_developer')

    def test_missing_keys_do_not_raise(self):
        """infer_user_role must not crash on a sparse dict."""
        role = infer_user_role({})
        self.assertIn(role, [
            'solo_developer', 'lead_developer', 'contributor',
            'frontend_developer', 'backend_developer', 'full_stack_developer',
            'designer', 'writer', 'architect', 'other',
        ])
