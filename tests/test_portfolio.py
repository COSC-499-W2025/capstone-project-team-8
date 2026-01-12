"""
Comprehensive Portfolio Tests

Tests portfolio CRUD, project management, aggregation, public access, and upload integration.
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
from django.contrib.auth import get_user_model

from app.models import (
    Portfolio, PortfolioProject, Project, 
    ProgrammingLanguage, ProjectLanguage, Framework, ProjectFramework,
    Contributor, ProjectContribution
)

User = get_user_model()


class PortfolioModelTests(TestCase):
    """Tests for Portfolio and PortfolioProject models."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.project = Project.objects.create(
            user=self.user,
            name='Test Project',
            classification_type='coding',
            resume_bullet_points=['Built feature A', 'Implemented feature B']
        )
    
    def test_portfolio_auto_generates_slug(self):
        """Slug should be auto-generated from name."""
        portfolio = Portfolio.objects.create(user=self.user, name='My Web Portfolio')
        self.assertIsNotNone(portfolio.slug)
        self.assertTrue(portfolio.slug.startswith('my-web-portfolio-'))
    
    def test_portfolio_slug_is_unique(self):
        """Each portfolio should have a unique slug."""
        p1 = Portfolio.objects.create(user=self.user, name='Same Name')
        p2 = Portfolio.objects.create(user=self.user, name='Same Name')
        self.assertNotEqual(p1.slug, p2.slug)
    
    def test_portfolio_project_get_display_title(self):
        """Should return custom title if set, otherwise project name."""
        portfolio = Portfolio.objects.create(user=self.user, name='Portfolio')
        pp = PortfolioProject.objects.create(portfolio=portfolio, project=self.project)
        
        # No custom title - use project name
        self.assertEqual(pp.get_display_title(), 'Test Project')
        
        # With custom title
        pp.custom_title = 'Custom Title'
        pp.save()
        self.assertEqual(pp.get_display_title(), 'Custom Title')
    
    def test_portfolio_project_get_bullet_points(self):
        """Should return custom bullets if enabled, otherwise project bullets."""
        portfolio = Portfolio.objects.create(user=self.user, name='Portfolio')
        pp = PortfolioProject.objects.create(portfolio=portfolio, project=self.project)
        
        # Default - use project bullets
        self.assertEqual(pp.get_bullet_points(), ['Built feature A', 'Implemented feature B'])
        
        # With custom bullets enabled
        pp.custom_bullet_points = ['Custom bullet 1', 'Custom bullet 2']
        pp.use_custom_bullets = True
        pp.save()
        self.assertEqual(pp.get_bullet_points(), ['Custom bullet 1', 'Custom bullet 2'])
    
    def test_portfolio_project_unique_constraint(self):
        """Cannot add same project to same portfolio twice."""
        portfolio = Portfolio.objects.create(user=self.user, name='Portfolio')
        PortfolioProject.objects.create(portfolio=portfolio, project=self.project)
        
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            PortfolioProject.objects.create(portfolio=portfolio, project=self.project)


class PortfolioAPITests(TestCase):
    """Tests for Portfolio API endpoints."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='testpass123',
            github_username='testgithub'
        )
        self.other_user = User.objects.create_user(
            username='otheruser', 
            email='other@example.com', 
            password='testpass123'
        )
        
        # Create test projects with metadata
        self.project1 = Project.objects.create(
            user=self.user,
            name='Web App',
            description='A web application',
            classification_type='coding',
            classification_confidence=0.95,
            total_files=100,
            git_repository=True,
            resume_bullet_points=['Built REST API', 'Implemented auth']
        )
        self.project2 = Project.objects.create(
            user=self.user,
            name='Mobile App',
            classification_type='coding',
            total_files=50,
            resume_bullet_points=['Developed cross-platform app']
        )
        self.other_project = Project.objects.create(
            user=self.other_user,
            name='Other Project',
            classification_type='coding'
        )
        
        # Add languages and frameworks to project1
        self.python = ProgrammingLanguage.objects.create(name='Python')
        self.javascript = ProgrammingLanguage.objects.create(name='JavaScript')
        self.django = Framework.objects.create(name='Django')
        self.react = Framework.objects.create(name='React')
        
        ProjectLanguage.objects.create(project=self.project1, language=self.python)
        ProjectLanguage.objects.create(project=self.project1, language=self.javascript)
        ProjectFramework.objects.create(project=self.project1, framework=self.django)
        ProjectFramework.objects.create(project=self.project1, framework=self.react)
        
        # Add contributor
        self.contributor = Contributor.objects.create(name='John Doe', email='john@example.com')
        ProjectContribution.objects.create(
            project=self.project1,
            contributor=self.contributor,
            commit_count=45,
            lines_added=3456,
            lines_deleted=1234
        )
    
    def _auth(self, user=None):
        """Authenticate client with JWT."""
        user = user or self.user
        self.client.force_authenticate(user=user)
    
    # --- Portfolio CRUD Tests ---
    
    def test_create_portfolio(self):
        """POST /api/portfolios/ should create a portfolio."""
        self._auth()
        resp = self.client.post(reverse('portfolio-list'), {
            'name': 'My Portfolio',
            'description': 'Test description',
            'is_public': True,
            'display_order': 'contribution'
        }, format='json')
        
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data['name'], 'My Portfolio')
        self.assertEqual(data['description'], 'Test description')
        self.assertTrue(data['is_public'])
        self.assertEqual(data['display_order'], 'contribution')
        self.assertIn('slug', data)
        self.assertEqual(data['project_count'], 0)
    
    def test_create_portfolio_requires_name(self):
        """POST /api/portfolios/ should require name."""
        self._auth()
        resp = self.client.post(reverse('portfolio-list'), {'description': 'No name'}, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('error', resp.json())
    
    def test_create_portfolio_requires_auth(self):
        """POST /api/portfolios/ should require authentication."""
        resp = self.client.post(reverse('portfolio-list'), {'name': 'Test'}, format='json')
        self.assertEqual(resp.status_code, 401)
    
    def test_list_portfolios(self):
        """GET /api/portfolios/ should list user's portfolios only."""
        Portfolio.objects.create(user=self.user, name='Portfolio 1')
        Portfolio.objects.create(user=self.user, name='Portfolio 2')
        Portfolio.objects.create(user=self.other_user, name='Other Portfolio')
        
        self._auth()
        resp = self.client.get(reverse('portfolio-list'))
        
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data['portfolios']), 2)
        names = [p['name'] for p in data['portfolios']]
        self.assertIn('Portfolio 1', names)
        self.assertIn('Portfolio 2', names)
        self.assertNotIn('Other Portfolio', names)
    
    def test_get_portfolio_detail_with_aggregation(self):
        """GET /api/portfolios/{id}/ should return full aggregated data."""
        portfolio = Portfolio.objects.create(user=self.user, name='My Portfolio')
        PortfolioProject.objects.create(portfolio=portfolio, project=self.project1, highlight=True)
        PortfolioProject.objects.create(portfolio=portfolio, project=self.project2)
        
        self._auth()
        resp = self.client.get(reverse('portfolio-detail', args=[portfolio.id]))
        
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        # Portfolio metadata
        self.assertEqual(data['portfolio_name'], 'My Portfolio')
        self.assertEqual(data['source'], 'portfolio')
        
        # Projects array
        self.assertEqual(len(data['projects']), 2)
        self.assertTrue(any(p['highlight'] for p in data['projects']))
        
        # Overall stats
        self.assertEqual(data['overall']['total_projects'], 2)
        self.assertEqual(data['overall']['total_files'], 150)  # 100 + 50
        
        # Skill analysis
        languages = [l['name'] for l in data['skill_analysis']['languages']]
        self.assertIn('Python', languages)
        self.assertIn('JavaScript', languages)
        
        frameworks = [f['name'] for f in data['skill_analysis']['frameworks']]
        self.assertIn('Django', frameworks)
        self.assertIn('React', frameworks)
        
        # Git contributions
        self.assertEqual(data['git_contributions']['total_commits'], 45)
    
    def test_update_portfolio(self):
        """PATCH /api/portfolios/{id}/ should update portfolio."""
        portfolio = Portfolio.objects.create(user=self.user, name='Original')
        
        self._auth()
        resp = self.client.patch(reverse('portfolio-detail', args=[portfolio.id]), {
            'name': 'Updated',
            'is_public': True,
            'cover_image_url': 'https://example.com/image.jpg'
        }, format='json')
        
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['name'], 'Updated')
        self.assertTrue(data['is_public'])
        self.assertEqual(data['cover_image_url'], 'https://example.com/image.jpg')
    
    def test_delete_portfolio(self):
        """DELETE /api/portfolios/{id}/ should delete portfolio."""
        portfolio = Portfolio.objects.create(user=self.user, name='To Delete')
        PortfolioProject.objects.create(portfolio=portfolio, project=self.project1)
        
        self._auth()
        resp = self.client.delete(reverse('portfolio-detail', args=[portfolio.id]))
        
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Portfolio.objects.filter(id=portfolio.id).exists())
        # Project should still exist
        self.assertTrue(Project.objects.filter(id=self.project1.id).exists())
    
    def test_cannot_access_other_users_portfolio(self):
        """Should not be able to access another user's portfolio."""
        portfolio = Portfolio.objects.create(user=self.other_user, name='Private')
        
        self._auth()
        resp = self.client.get(reverse('portfolio-detail', args=[portfolio.id]))
        self.assertEqual(resp.status_code, 404)
    
    # --- Portfolio Project Management Tests ---
    
    def test_add_project_to_portfolio(self):
        """POST /api/portfolios/{id}/projects/ should add project."""
        portfolio = Portfolio.objects.create(user=self.user, name='Portfolio')
        
        self._auth()
        resp = self.client.post(reverse('portfolio-add-project', args=[portfolio.id]), {
            'project_id': self.project1.id,
            'highlight': True
        }, format='json')
        
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data['project_id'], self.project1.id)
        self.assertIn('portfolio_project_id', data)
        
        # Verify in database
        self.assertTrue(PortfolioProject.objects.filter(
            portfolio=portfolio, project=self.project1
        ).exists())
    
    def test_cannot_add_duplicate_project(self):
        """Should not add same project twice."""
        portfolio = Portfolio.objects.create(user=self.user, name='Portfolio')
        PortfolioProject.objects.create(portfolio=portfolio, project=self.project1)
        
        self._auth()
        resp = self.client.post(reverse('portfolio-add-project', args=[portfolio.id]), {
            'project_id': self.project1.id
        }, format='json')
        
        self.assertEqual(resp.status_code, 400)
        self.assertIn('already in portfolio', resp.json()['error'])
    
    def test_cannot_add_other_users_project(self):
        """Should not add another user's project."""
        portfolio = Portfolio.objects.create(user=self.user, name='Portfolio')
        
        self._auth()
        resp = self.client.post(reverse('portfolio-add-project', args=[portfolio.id]), {
            'project_id': self.other_project.id
        }, format='json')
        
        self.assertEqual(resp.status_code, 404)
    
    def test_update_portfolio_project(self):
        """PATCH /api/portfolios/{id}/projects/{pp_id}/ should update customization."""
        portfolio = Portfolio.objects.create(user=self.user, name='Portfolio')
        pp = PortfolioProject.objects.create(portfolio=portfolio, project=self.project1)
        
        self._auth()
        resp = self.client.patch(
            reverse('portfolio-project-detail', args=[portfolio.id, pp.id]),
            {
                'custom_title': 'Custom Title',
                'custom_description': 'Custom Desc',
                'highlight': True,
                'custom_bullet_points': ['Bullet 1', 'Bullet 2'],
                'use_custom_bullets': True
            },
            format='json'
        )
        
        self.assertEqual(resp.status_code, 200)
        
        pp.refresh_from_db()
        self.assertEqual(pp.custom_title, 'Custom Title')
        self.assertEqual(pp.custom_description, 'Custom Desc')
        self.assertTrue(pp.highlight)
        self.assertEqual(pp.custom_bullet_points, ['Bullet 1', 'Bullet 2'])
        self.assertTrue(pp.use_custom_bullets)
    
    def test_remove_project_from_portfolio(self):
        """DELETE /api/portfolios/{id}/projects/{pp_id}/ should remove project."""
        portfolio = Portfolio.objects.create(user=self.user, name='Portfolio')
        pp = PortfolioProject.objects.create(portfolio=portfolio, project=self.project1)
        
        self._auth()
        resp = self.client.delete(
            reverse('portfolio-project-detail', args=[portfolio.id, pp.id])
        )
        
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(PortfolioProject.objects.filter(id=pp.id).exists())
        # Project itself still exists
        self.assertTrue(Project.objects.filter(id=self.project1.id).exists())
    
    def test_reorder_projects(self):
        """POST /api/portfolios/{id}/reorder/ should update display order."""
        portfolio = Portfolio.objects.create(user=self.user, name='Portfolio')
        pp1 = PortfolioProject.objects.create(portfolio=portfolio, project=self.project1, display_order=0)
        pp2 = PortfolioProject.objects.create(portfolio=portfolio, project=self.project2, display_order=1)
        
        self._auth()
        resp = self.client.post(
            reverse('portfolio-reorder', args=[portfolio.id]),
            {'project_order': [pp2.id, pp1.id]},  # Reversed
            format='json'
        )
        
        self.assertEqual(resp.status_code, 200)
        
        pp1.refresh_from_db()
        pp2.refresh_from_db()
        self.assertEqual(pp2.display_order, 0)
        self.assertEqual(pp1.display_order, 1)
    
    # --- Public Portfolio Tests ---
    
    def test_public_portfolio_accessible_without_auth(self):
        """GET /api/portfolio/public/{slug}/ should work without auth."""
        portfolio = Portfolio.objects.create(
            user=self.user,
            name='Public Portfolio',
            is_public=True
        )
        PortfolioProject.objects.create(portfolio=portfolio, project=self.project1)
        
        # No authentication
        resp = self.client.get(reverse('portfolio-public', args=[portfolio.slug]))
        
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['portfolio_name'], 'Public Portfolio')
        self.assertIn('user', data)
        self.assertEqual(data['user']['username'], 'testuser')
        self.assertEqual(data['user']['github_username'], 'testgithub')
    
    def test_private_portfolio_not_accessible_publicly(self):
        """Private portfolios should return 404 on public endpoint."""
        portfolio = Portfolio.objects.create(
            user=self.user,
            name='Private Portfolio',
            is_public=False
        )
        
        resp = self.client.get(reverse('portfolio-public', args=[portfolio.slug]))
        self.assertEqual(resp.status_code, 404)
    
    # --- Cover Image Placeholder Test ---
    
    def test_cover_upload_returns_not_implemented(self):
        """POST /api/portfolios/{id}/upload-cover/ should return 501."""
        portfolio = Portfolio.objects.create(user=self.user, name='Portfolio')
        
        self._auth()
        resp = self.client.post(
            reverse('portfolio-upload-cover', args=[portfolio.id]),
            {'file': 'dummy'},
            format='multipart'
        )
        
        self.assertEqual(resp.status_code, 501)
        self.assertIn('not yet implemented', resp.json()['error'])


class PortfolioAggregationTests(TestCase):
    """Tests for portfolio data aggregation logic."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='test123')
        
        # Create projects with different classifications
        self.coding_project = Project.objects.create(
            user=self.user,
            name='Coding Project',
            classification_type='coding',
            classification_confidence=0.9,
            total_files=50
        )
        self.writing_project = Project.objects.create(
            user=self.user,
            name='Writing Project', 
            classification_type='writing',
            classification_confidence=0.85,
            total_files=20
        )
        
        # Languages
        self.python = ProgrammingLanguage.objects.create(name='Python')
        self.rust = ProgrammingLanguage.objects.create(name='Rust')
        ProjectLanguage.objects.create(project=self.coding_project, language=self.python)
        ProjectLanguage.objects.create(project=self.coding_project, language=self.rust)
    
    def test_aggregation_combines_languages(self):
        """Languages should be aggregated with counts across all projects."""
        from app.views.portfolio_views import aggregate_portfolio_data
        
        portfolio = Portfolio.objects.create(user=self.user, name='Portfolio')
        PortfolioProject.objects.create(portfolio=portfolio, project=self.coding_project)
        
        data = aggregate_portfolio_data(portfolio)
        
        languages = data['skill_analysis']['languages']
        lang_names = [l['name'] for l in languages]
        self.assertIn('Python', lang_names)
        self.assertIn('Rust', lang_names)
    
    def test_aggregation_determines_mixed_classification(self):
        """Mixed classification should be detected when multiple types present."""
        from app.views.portfolio_views import aggregate_portfolio_data
        
        portfolio = Portfolio.objects.create(user=self.user, name='Mixed Portfolio')
        PortfolioProject.objects.create(portfolio=portfolio, project=self.coding_project)
        PortfolioProject.objects.create(portfolio=portfolio, project=self.writing_project)
        
        data = aggregate_portfolio_data(portfolio)
        
        # Should be mixed since we have both coding and writing
        self.assertIn('mixed:', data['overall']['classification'])
    
    def test_aggregation_sums_file_counts(self):
        """Total files should be summed across all projects."""
        from app.views.portfolio_views import aggregate_portfolio_data
        
        portfolio = Portfolio.objects.create(user=self.user, name='Portfolio')
        PortfolioProject.objects.create(portfolio=portfolio, project=self.coding_project)
        PortfolioProject.objects.create(portfolio=portfolio, project=self.writing_project)
        
        data = aggregate_portfolio_data(portfolio)
        
        self.assertEqual(data['overall']['total_files'], 70)  # 50 + 20
        self.assertEqual(data['overall']['total_projects'], 2)


class ResumeServicePortfolioTests(TestCase):
    """Tests for resume service portfolio integration."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='test123',
            first_name='John',
            last_name='Doe'
        )
        self.project = Project.objects.create(
            user=self.user,
            name='Project',
            classification_type='coding',
            resume_bullet_points=['Bullet 1', 'Bullet 2']
        )
        
        self.python = ProgrammingLanguage.objects.create(name='Python')
        ProjectLanguage.objects.create(project=self.project, language=self.python)
    
    def test_build_resume_context_from_portfolio(self):
        """build_resume_context should aggregate from specified portfolio."""
        from app.services.resume_service import build_resume_context
        
        portfolio = Portfolio.objects.create(user=self.user, name='Resume Portfolio')
        PortfolioProject.objects.create(portfolio=portfolio, project=self.project, include_in_resume=True)
        
        context = build_resume_context(self.user, portfolio_id=portfolio.id)
        
        self.assertEqual(context['full_name'], 'John Doe')
        self.assertEqual(context['portfolio_name'], 'Resume Portfolio')
        self.assertEqual(context['portfolio_id'], portfolio.id)
        self.assertEqual(len(context['projects']), 1)
        self.assertIn('Python', context['languages'])
    
    def test_build_resume_context_respects_include_in_resume(self):
        """Projects with include_in_resume=False should be excluded."""
        from app.services.resume_service import build_resume_context
        
        other_project = Project.objects.create(user=self.user, name='Excluded', classification_type='coding')
        
        portfolio = Portfolio.objects.create(user=self.user, name='Portfolio')
        PortfolioProject.objects.create(portfolio=portfolio, project=self.project, include_in_resume=True)
        PortfolioProject.objects.create(portfolio=portfolio, project=other_project, include_in_resume=False)
        
        context = build_resume_context(self.user, portfolio_id=portfolio.id)
        
        self.assertEqual(len(context['projects']), 1)
        self.assertEqual(context['projects'][0]['name'], 'Project')
    
    def test_build_resume_context_without_portfolio(self):
        """Should return basic context when no portfolio specified."""
        from app.services.resume_service import build_resume_context
        
        context = build_resume_context(self.user)
        
        self.assertEqual(context['full_name'], 'John Doe')
        self.assertEqual(context['projects'], [])
        self.assertIsNone(context['portfolio_id'])


if __name__ == '__main__':
    import unittest
    unittest.main()
