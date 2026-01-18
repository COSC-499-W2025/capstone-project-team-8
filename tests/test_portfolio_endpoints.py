"""
Portfolio API endpoint tests.
Tests CRUD operations, project curation, permissions, and AI summary generation.
AI-related tests skip (not fail) when LLM service is unavailable.
"""

import os
import sys
import requests

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
from django.urls import reverse
from rest_framework.test import APIClient
from django.utils import timezone
from unittest import skipIf

from app.models import Project, Portfolio, PortfolioProject
from django.contrib.auth import get_user_model

User = get_user_model()


def is_llm_service_available():
    """Check if LLM service is available for AI summary tests."""
    try:
        from app.services.llm import ai_analyze
        # Try a simple call to verify service is responsive
        ai_analyze("test", system_message="test")
        return True
    except Exception:
        return False


# Cache the result at module load time
LLM_AVAILABLE = False
try:
    LLM_AVAILABLE = is_llm_service_available()
except Exception:
    LLM_AVAILABLE = False


class PortfolioEndpointsTests(TestCase):
    """Test portfolio CRUD operations and permissions."""
    
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username="alice", email="alice@example.com", password="pass123"
        )
        self.user2 = User.objects.create_user(
            username="bob", email="bob@example.com", password="pass123"
        )
        
        now = timezone.now()
        
        # Create projects for user1
        self.project1 = Project.objects.create(
            user=self.user1,
            name="Alice Project 1",
            description="A coding project",
            project_tag=1,
            classification_type="coding",
            total_files=10,
            code_files_count=8,
            created_at=now,
        )
        self.project2 = Project.objects.create(
            user=self.user1,
            name="Alice Project 2",
            description="Another project",
            project_tag=2,
            classification_type="mixed:coding+writing",
            total_files=5,
            code_files_count=3,
            created_at=now,
        )
        
        # Create project for user2
        self.project_bob = Project.objects.create(
            user=self.user2,
            name="Bob Project",
            description="Bob's project",
            project_tag=3,
            classification_type="writing",
            total_files=3,
            created_at=now,
        )
    
    # ==================== Authentication Tests ====================
    
    def test_portfolio_list_requires_auth(self):
        """Unauthenticated requests to list portfolios should be rejected."""
        url = reverse("portfolio-list")
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (401, 403))
    
    def test_portfolio_generate_requires_auth(self):
        """Unauthenticated requests to generate portfolio should be rejected."""
        url = reverse("portfolio-generate")
        resp = self.client.post(url, data={"title": "Test"}, format="json")
        self.assertIn(resp.status_code, (401, 403))
    
    # ==================== Portfolio Generation Tests ====================
    
    def test_generate_portfolio_basic(self):
        """Create a basic portfolio without AI summary."""
        self.client.force_authenticate(user=self.user1)
        url = reverse("portfolio-generate")
        
        resp = self.client.post(url, data={
            "title": "My Portfolio",
            "description": "A showcase of my work",
            "project_ids": [self.project1.id, self.project2.id],
            "is_public": True,
            "generate_summary": False,  # Skip AI summary
        }, format="json")
        
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertIn("portfolio", data)
        
        portfolio = data["portfolio"]
        self.assertEqual(portfolio["title"], "My Portfolio")
        self.assertEqual(portfolio["description"], "A showcase of my work")
        self.assertTrue(portfolio["is_public"])
        self.assertEqual(portfolio["project_count"], 2)
        self.assertEqual(len(portfolio["projects"]), 2)
    
    def test_generate_portfolio_auto_slug(self):
        """Portfolio slug is auto-generated from title if not provided."""
        self.client.force_authenticate(user=self.user1)
        url = reverse("portfolio-generate")
        
        resp = self.client.post(url, data={
            "title": "My Awesome Portfolio",
            "generate_summary": False,
        }, format="json")
        
        self.assertEqual(resp.status_code, 201)
        portfolio = resp.json()["portfolio"]
        self.assertEqual(portfolio["slug"], "my-awesome-portfolio")
    
    def test_generate_portfolio_unique_slug_enforcement(self):
        """Duplicate slugs are auto-incremented."""
        self.client.force_authenticate(user=self.user1)
        url = reverse("portfolio-generate")
        
        # Create first portfolio
        resp1 = self.client.post(url, data={
            "title": "Test Portfolio",
            "slug": "test-slug",
            "generate_summary": False,
        }, format="json")
        self.assertEqual(resp1.status_code, 201)
        
        # Create second with same slug - should get incremented
        resp2 = self.client.post(url, data={
            "title": "Another Portfolio",
            "slug": "test-slug",
            "generate_summary": False,
        }, format="json")
        self.assertEqual(resp2.status_code, 201)
        self.assertEqual(resp2.json()["portfolio"]["slug"], "test-slug-1")
    
    def test_generate_portfolio_invalid_project_ids(self):
        """Cannot add projects that don't belong to user."""
        self.client.force_authenticate(user=self.user1)
        url = reverse("portfolio-generate")
        
        resp = self.client.post(url, data={
            "title": "Test",
            "project_ids": [self.project_bob.id],  # Bob's project
            "generate_summary": False,
        }, format="json")
        
        self.assertEqual(resp.status_code, 400)
        self.assertIn("error", resp.json())
    
    # ==================== Portfolio Retrieve Tests ====================
    
    def test_retrieve_own_private_portfolio(self):
        """User can retrieve their own private portfolio."""
        portfolio = Portfolio.objects.create(
            user=self.user1,
            title="Private Portfolio",
            slug="private-portfolio",
            is_public=False,
        )
        
        self.client.force_authenticate(user=self.user1)
        url = reverse("portfolio-detail", args=[portfolio.id])
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["title"], "Private Portfolio")
    
    def test_cannot_retrieve_others_private_portfolio(self):
        """User cannot retrieve another user's private portfolio."""
        portfolio = Portfolio.objects.create(
            user=self.user1,
            title="Private Portfolio",
            slug="private-portfolio-2",
            is_public=False,
        )
        
        self.client.force_authenticate(user=self.user2)
        url = reverse("portfolio-detail", args=[portfolio.id])
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 404)
    
    def test_public_portfolio_accessible_without_auth(self):
        """Public portfolios can be viewed without authentication."""
        portfolio = Portfolio.objects.create(
            user=self.user1,
            title="Public Portfolio",
            slug="public-portfolio",
            is_public=True,
        )
        
        # No authentication
        url = reverse("portfolio-detail", args=[portfolio.id])
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["title"], "Public Portfolio")
    
    # ==================== Portfolio Edit Tests ====================
    
    def test_edit_portfolio_fields(self):
        """Edit portfolio fields via POST /portfolio/{id}/edit."""
        portfolio = Portfolio.objects.create(
            user=self.user1,
            title="Original Title",
            slug="edit-test",
            description="Original description",
            is_public=False,
        )
        
        self.client.force_authenticate(user=self.user1)
        url = reverse("portfolio-edit", args=[portfolio.id])
        
        resp = self.client.post(url, data={
            "title": "Updated Title",
            "description": "Updated description",
            "is_public": True,
        }, format="json")
        
        self.assertEqual(resp.status_code, 200)
        portfolio.refresh_from_db()
        self.assertEqual(portfolio.title, "Updated Title")
        self.assertEqual(portfolio.description, "Updated description")
        self.assertTrue(portfolio.is_public)
    
    def test_cannot_edit_others_portfolio(self):
        """User cannot edit another user's portfolio."""
        portfolio = Portfolio.objects.create(
            user=self.user1,
            title="Alice's Portfolio",
            slug="alice-portfolio",
        )
        
        self.client.force_authenticate(user=self.user2)
        url = reverse("portfolio-edit", args=[portfolio.id])
        
        resp = self.client.post(url, data={"title": "Hacked"}, format="json")
        self.assertEqual(resp.status_code, 404)
    
    # ==================== Portfolio Delete Tests ====================
    
    def test_delete_own_portfolio(self):
        """User can delete their own portfolio."""
        portfolio = Portfolio.objects.create(
            user=self.user1,
            title="Delete Me",
            slug="delete-me",
        )
        
        self.client.force_authenticate(user=self.user1)
        url = reverse("portfolio-detail", args=[portfolio.id])
        
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Portfolio.objects.filter(id=portfolio.id).exists())
    
    def test_cannot_delete_others_portfolio(self):
        """User cannot delete another user's portfolio."""
        portfolio = Portfolio.objects.create(
            user=self.user1,
            title="Protected",
            slug="protected",
        )
        
        self.client.force_authenticate(user=self.user2)
        url = reverse("portfolio-detail", args=[portfolio.id])
        
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(Portfolio.objects.filter(id=portfolio.id).exists())
    
    # ==================== Portfolio List Tests ====================
    
    def test_list_own_portfolios(self):
        """User sees only their own portfolios in list."""
        Portfolio.objects.create(user=self.user1, title="Alice's 1", slug="alice-1")
        Portfolio.objects.create(user=self.user1, title="Alice's 2", slug="alice-2")
        Portfolio.objects.create(user=self.user2, title="Bob's 1", slug="bob-1")
        
        self.client.force_authenticate(user=self.user1)
        url = reverse("portfolio-list")
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 200)
        portfolios = resp.json()["portfolios"]
        self.assertEqual(len(portfolios), 2)
        titles = [p["title"] for p in portfolios]
        self.assertIn("Alice's 1", titles)
        self.assertIn("Alice's 2", titles)
        self.assertNotIn("Bob's 1", titles)


class PortfolioProjectCurationTests(TestCase):
    """Test adding, removing, and reordering projects in portfolios."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass123"
        )
        
        # Create projects
        self.project1 = Project.objects.create(
            user=self.user, name="Project 1", project_tag=1, created_at=timezone.now()
        )
        self.project2 = Project.objects.create(
            user=self.user, name="Project 2", project_tag=2, created_at=timezone.now()
        )
        self.project3 = Project.objects.create(
            user=self.user, name="Project 3", project_tag=3, created_at=timezone.now()
        )
        
        # Create portfolio
        self.portfolio = Portfolio.objects.create(
            user=self.user,
            title="Test Portfolio",
            slug="test-portfolio",
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_add_project_to_portfolio(self):
        """Add a project to portfolio."""
        url = reverse("portfolio-add-project", args=[self.portfolio.id])
        
        resp = self.client.post(url, data={
            "project_id": self.project1.id,
            "notes": "My favorite project",
            "featured": True,
        }, format="json")
        
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(
            PortfolioProject.objects.filter(
                portfolio=self.portfolio, project=self.project1
            ).exists()
        )
        
        pp = PortfolioProject.objects.get(portfolio=self.portfolio, project=self.project1)
        self.assertEqual(pp.notes, "My favorite project")
        self.assertTrue(pp.featured)
    
    def test_add_project_auto_order(self):
        """Projects are auto-ordered when added."""
        url = reverse("portfolio-add-project", args=[self.portfolio.id])
        
        # Add first project
        self.client.post(url, data={"project_id": self.project1.id}, format="json")
        # Add second project
        self.client.post(url, data={"project_id": self.project2.id}, format="json")
        
        pp1 = PortfolioProject.objects.get(portfolio=self.portfolio, project=self.project1)
        pp2 = PortfolioProject.objects.get(portfolio=self.portfolio, project=self.project2)
        
        self.assertEqual(pp1.order, 0)
        self.assertEqual(pp2.order, 1)
    
    def test_cannot_add_duplicate_project(self):
        """Cannot add the same project twice."""
        PortfolioProject.objects.create(
            portfolio=self.portfolio, project=self.project1, order=0
        )
        
        url = reverse("portfolio-add-project", args=[self.portfolio.id])
        resp = self.client.post(url, data={"project_id": self.project1.id}, format="json")
        
        self.assertEqual(resp.status_code, 400)
        self.assertIn("already in portfolio", resp.json()["error"])
    
    def test_remove_project_from_portfolio(self):
        """Remove a project from portfolio."""
        PortfolioProject.objects.create(
            portfolio=self.portfolio, project=self.project1, order=0
        )
        
        url = reverse("portfolio-remove-project", args=[self.portfolio.id, self.project1.id])
        resp = self.client.delete(url)
        
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(
            PortfolioProject.objects.filter(
                portfolio=self.portfolio, project=self.project1
            ).exists()
        )
    
    def test_reorder_projects(self):
        """Reorder projects in portfolio."""
        PortfolioProject.objects.create(portfolio=self.portfolio, project=self.project1, order=0)
        PortfolioProject.objects.create(portfolio=self.portfolio, project=self.project2, order=1)
        PortfolioProject.objects.create(portfolio=self.portfolio, project=self.project3, order=2)
        
        url = reverse("portfolio-reorder-projects", args=[self.portfolio.id])
        
        # Reverse the order
        resp = self.client.post(url, data={
            "project_ids": [self.project3.id, self.project2.id, self.project1.id]
        }, format="json")
        
        self.assertEqual(resp.status_code, 200)
        
        # Verify new order
        pp1 = PortfolioProject.objects.get(portfolio=self.portfolio, project=self.project1)
        pp2 = PortfolioProject.objects.get(portfolio=self.portfolio, project=self.project2)
        pp3 = PortfolioProject.objects.get(portfolio=self.portfolio, project=self.project3)
        
        self.assertEqual(pp3.order, 0)
        self.assertEqual(pp2.order, 1)
        self.assertEqual(pp1.order, 2)
    
    def test_reorder_requires_all_project_ids(self):
        """Reorder fails if not all project IDs are provided."""
        PortfolioProject.objects.create(portfolio=self.portfolio, project=self.project1, order=0)
        PortfolioProject.objects.create(portfolio=self.portfolio, project=self.project2, order=1)
        
        url = reverse("portfolio-reorder-projects", args=[self.portfolio.id])
        
        # Missing project2
        resp = self.client.post(url, data={
            "project_ids": [self.project1.id]
        }, format="json")
        
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Missing", resp.json()["error"])


class PortfolioAISummaryTests(TestCase):
    """Test AI summary generation for portfolios.
    These tests SKIP (not fail) if LLM service is unavailable.
    """
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="aiuser", email="ai@example.com", password="pass123"
        )
        
        self.project = Project.objects.create(
            user=self.user,
            name="AI Test Project",
            description="A project for testing AI summaries",
            project_tag=1,
            classification_type="coding",
            resume_bullet_points=[
                "Built a REST API with Django",
                "Implemented JWT authentication",
            ],
            created_at=timezone.now(),
        )
        
        self.client.force_authenticate(user=self.user)
    
    @skipIf(not LLM_AVAILABLE, "LLM service unavailable - skipping AI summary test")
    def test_generate_portfolio_with_ai_summary(self):
        """Generate portfolio with AI summary when LLM available."""
        url = reverse("portfolio-generate")
        
        resp = self.client.post(url, data={
            "title": "AI Summary Portfolio",
            "project_ids": [self.project.id],
            "generate_summary": True,
            "tone": "professional",
            "target_audience": "recruiters",
        }, format="json")
        
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        
        # Summary should be generated
        self.assertTrue(data.get("summary_generated", False))
        portfolio = data["portfolio"]
        self.assertTrue(len(portfolio["summary"]) > 0)
        self.assertIsNotNone(portfolio["summary_generated_at"])
    
    @skipIf(not LLM_AVAILABLE, "LLM service unavailable - skipping AI summary test")
    def test_edit_portfolio_regenerate_summary(self):
        """Regenerate AI summary via edit endpoint when LLM available."""
        # Create portfolio without summary
        portfolio = Portfolio.objects.create(
            user=self.user,
            title="Edit Summary Test",
            slug="edit-summary-test",
            tone="technical",
        )
        PortfolioProject.objects.create(
            portfolio=portfolio, project=self.project, order=0
        )
        
        url = reverse("portfolio-edit", args=[portfolio.id])
        
        resp = self.client.post(url, data={
            "regenerate_summary": True,
        }, format="json")
        
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        self.assertTrue(data.get("summary_regenerated", False))
        portfolio.refresh_from_db()
        self.assertTrue(len(portfolio.summary) > 0)
    
    def test_generate_portfolio_without_summary_succeeds(self):
        """Portfolio creation works even when AI summary is disabled."""
        url = reverse("portfolio-generate")
        
        resp = self.client.post(url, data={
            "title": "No Summary Portfolio",
            "project_ids": [self.project.id],
            "generate_summary": False,
        }, format="json")
        
        self.assertEqual(resp.status_code, 201)
        portfolio = resp.json()["portfolio"]
        self.assertEqual(portfolio["summary"], "")


class PortfolioModelTests(TestCase):
    """Test Portfolio model constraints and behavior."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="modeluser", email="model@example.com", password="pass123"
        )
    
    def test_portfolio_slug_uniqueness(self):
        """Slug must be globally unique."""
        Portfolio.objects.create(
            user=self.user, title="First", slug="unique-slug"
        )
        
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Portfolio.objects.create(
                user=self.user, title="Second", slug="unique-slug"
            )
    
    def test_portfolio_project_ordering(self):
        """PortfolioProject default ordering is by order, then added_at."""
        portfolio = Portfolio.objects.create(
            user=self.user, title="Order Test", slug="order-test"
        )
        
        p1 = Project.objects.create(user=self.user, name="P1", project_tag=1, created_at=timezone.now())
        p2 = Project.objects.create(user=self.user, name="P2", project_tag=2, created_at=timezone.now())
        p3 = Project.objects.create(user=self.user, name="P3", project_tag=3, created_at=timezone.now())
        
        PortfolioProject.objects.create(portfolio=portfolio, project=p3, order=0)
        PortfolioProject.objects.create(portfolio=portfolio, project=p1, order=2)
        PortfolioProject.objects.create(portfolio=portfolio, project=p2, order=1)
        
        ordered = list(portfolio.portfolio_projects.all())
        self.assertEqual(ordered[0].project.name, "P3")
        self.assertEqual(ordered[1].project.name, "P2")
        self.assertEqual(ordered[2].project.name, "P1")
    
    def test_cascade_delete_user(self):
        """Deleting user cascades to portfolios."""
        portfolio = Portfolio.objects.create(
            user=self.user, title="Cascade Test", slug="cascade-test"
        )
        portfolio_id = portfolio.id
        
        self.user.delete()
        
        self.assertFalse(Portfolio.objects.filter(id=portfolio_id).exists())
    
    def test_cascade_delete_project(self):
        """Deleting project removes it from portfolios but keeps portfolio."""
        portfolio = Portfolio.objects.create(
            user=self.user, title="Project Cascade", slug="project-cascade"
        )
        project = Project.objects.create(
            user=self.user, name="ToDelete", project_tag=1, created_at=timezone.now()
        )
        PortfolioProject.objects.create(portfolio=portfolio, project=project, order=0)
        
        project.delete()
        
        self.assertTrue(Portfolio.objects.filter(id=portfolio.id).exists())
        self.assertEqual(portfolio.portfolio_projects.count(), 0)
