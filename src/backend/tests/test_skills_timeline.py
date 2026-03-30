"""
Tests for Skills Timeline Endpoint

Tests the GET /api/skills/timeline/ endpoint that determines
the chronological inception of skills across a user's projects.
"""
import os
import sys

# Add the backend directory to the Python path if not already there
backend_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Setup Django settings only if not already configured
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
    import django
    django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta

from app.models import (
    Project, 
    ProgrammingLanguage, 
    Framework, 
    ProjectLanguage, 
    ProjectFramework,
    Portfolio,
    PortfolioProject
)

User = get_user_model()


class SkillsTimelineTests(TestCase):
    """Test suite for the skills timeline endpoint"""
    
    def setUp(self):
        """Set up test client and user"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='timeline_user',
            email='timeline@example.com',
            password='pass123'
        )
        self.url = '/api/skills/timeline/'
        
        # Setup base time to ensure chronological stability
        self.base_time = timezone.now()
        
    def test_endpoint_requires_authentication(self):
        """Unauthenticated requests should be rejected"""
        response = self.client.get(self.url)
        self.assertIn(response.status_code, [401, 403])

    def test_empty_timeline_for_new_user(self):
        """A user with no projects should receive an empty timeline"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('timeline', data)
        self.assertEqual(data['timeline'], [])

    def test_timeline_returns_earliest_dates_chronologically(self):
        """Skills should be sorted by absolute earliest occurrence across all projects"""
        self.client.force_authenticate(user=self.user)
        
        # Create Skills
        python = ProgrammingLanguage.objects.create(name='Python')
        js = ProgrammingLanguage.objects.create(name='JavaScript')
        django_fw = Framework.objects.create(name='Django')
        react = Framework.objects.create(name='React')
        
        # Create projects with staggered timelines
        # Project 1: Oldest
        p1 = Project.objects.create(
            user=self.user,
            name='First Project',
            classification_type='coding',
            first_commit_date=self.base_time - timedelta(days=365) # 1 year ago
        )
        # Project 2: Middle
        p2 = Project.objects.create(
            user=self.user,
            name='Second Project',
            classification_type='coding',
            first_commit_date=self.base_time - timedelta(days=180) # 6 months ago
        )
        # Project 3: Newest
        p3 = Project.objects.create(
            user=self.user,
            name='Latest Project',
            classification_type='coding',
            first_commit_date=self.base_time - timedelta(days=30) # 1 month ago
        )

        # Associate Skills
        # Python appears 1 year ago
        ProjectLanguage.objects.create(project=p1, language=python, file_count=5)
        # Python appears AGAIN 1 month ago
        ProjectLanguage.objects.create(project=p3, language=python, file_count=10)
        
        # Django appears 6 months ago
        ProjectFramework.objects.create(project=p2, framework=django_fw)
        
        # JS and React appear 1 month ago
        ProjectLanguage.objects.create(project=p3, language=js, file_count=8)
        ProjectFramework.objects.create(project=p3, framework=react)
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        
        timeline = response.json().get('timeline', [])
        self.assertEqual(len(timeline), 4)

        # Chronological Order verification
        self.assertEqual(timeline[0]['skill'], 'Python')
        self.assertEqual(timeline[1]['skill'], 'Django')
        
        # JS and React share the same timestamp (P3's date)
        # Order among identical timestamps isn't strictly defined by the requirements,
        # but both should be last.
        latest_skills = [timeline[2]['skill'], timeline[3]['skill']]
        self.assertIn('JavaScript', latest_skills)
        self.assertIn('React', latest_skills)
        
        # Verify type classifications
        python_node = next(s for s in timeline if s['skill'] == 'Python')
        django_node = next(s for s in timeline if s['skill'] == 'Django')
        self.assertEqual(python_node['type'], 'language')
        self.assertEqual(django_node['type'], 'framework')

    def test_timeline_filters_by_portfolio_id(self):
        """Timeline should strictly isolate skills present inside a requested portfolio"""
        self.client.force_authenticate(user=self.user)
        
        # Create Skills
        cpp = ProgrammingLanguage.objects.create(name='C++')
        rust = ProgrammingLanguage.objects.create(name='Rust')
        
        # Create projects
        p_portfolio = Project.objects.create(
            user=self.user,
            name='Portfolio Target',
            classification_type='coding',
            first_commit_date=self.base_time - timedelta(days=100)
        )
        p_other = Project.objects.create(
            user=self.user,
            name='Ignored Project',
            classification_type='coding',
            first_commit_date=self.base_time - timedelta(days=200)
        )
        
        # Portfolio target has C++
        ProjectLanguage.objects.create(project=p_portfolio, language=cpp, file_count=5)
        # Ignored project has Rust
        ProjectLanguage.objects.create(project=p_other, language=rust, file_count=5)
        
        # Create Portfolio mapping
        portfolio = Portfolio.objects.create(
            user=self.user,
            title='Subset Portfolio',
            slug='subset-portfolio'
        )
        PortfolioProject.objects.create(portfolio=portfolio, project=p_portfolio, order=0)
        
        # Call global endpoint (Expects both C++ and Rust)
        response_global = self.client.get(self.url)
        self.assertEqual(len(response_global.json()['timeline']), 2)
        
        # Call portfolio filtered endpoint
        response_filtered = self.client.get(f"{self.url}?portfolio_id={portfolio.id}")
        self.assertEqual(response_filtered.status_code, 200)
        
        timeline = response_filtered.json()['timeline']
        # Expects only C++
        self.assertEqual(len(timeline), 1)
        self.assertEqual(timeline[0]['skill'], 'C++')

    def test_fallback_to_created_at(self):
        """Projects without commit history should fallback to creation date"""
        self.client.force_authenticate(user=self.user)
        
        ruby = ProgrammingLanguage.objects.create(name='Ruby')
        
        p = Project.objects.create(
            user=self.user,
            name='No Commits Project',
            classification_type='coding',
            created_at=self.base_time - timedelta(days=50),
            first_commit_date=None
        )
        ProjectLanguage.objects.create(project=p, language=ruby, file_count=2)
        
        response = self.client.get(self.url)
        timeline = response.json()['timeline']
        
        self.assertEqual(len(timeline), 1)
        self.assertEqual(timeline[0]['skill'], 'Ruby')
        # Dates are returned in ISO 8601, ensuring it didn't crash on None
        self.assertTrue(timeline[0]['date'].startswith((self.base_time - timedelta(days=50)).strftime('%Y-%m-%d')))
