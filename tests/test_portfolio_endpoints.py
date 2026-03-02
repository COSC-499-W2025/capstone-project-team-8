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
        """Accessing another user's private portfolio returns 403 with is_private flag."""
        portfolio = Portfolio.objects.create(
            user=self.user1,
            title="Private Portfolio",
            slug="private-portfolio-2",
            is_public=False,
        )

        self.client.force_authenticate(user=self.user2)
        url = reverse("portfolio-detail", args=[portfolio.id])
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 403)
        data = resp.json()
        self.assertTrue(data.get("is_private"), "Response should include is_private=True")
        self.assertEqual(data.get("portfolio_title"), "Private Portfolio")
        self.assertEqual(data.get("owner"), "alice")

    def test_unauthenticated_cannot_retrieve_private_portfolio(self):
        """Unauthenticated access to a private portfolio returns 403 with is_private flag."""
        portfolio = Portfolio.objects.create(
            user=self.user1,
            title="Secret Portfolio",
            slug="secret-portfolio",
            is_public=False,
        )

        url = reverse("portfolio-detail", args=[portfolio.id])
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 403)
        data = resp.json()
        self.assertTrue(data.get("is_private"))
        self.assertEqual(data.get("portfolio_title"), "Secret Portfolio")
    
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


class PortfolioStatisticsTests(TestCase):
    """Test portfolio statistics calculation and caching."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="statsuser", email="stats@example.com", password="pass123"
        )
        
        # Import models needed for statistics
        from app.models import (
            ProjectFile, ProjectLanguage, ProjectFramework, 
            ProgrammingLanguage, Framework, Contributor, ProjectContribution
        )
        
        self.ProjectFile = ProjectFile
        self.ProjectLanguage = ProjectLanguage
        self.ProjectFramework = ProjectFramework
        self.ProgrammingLanguage = ProgrammingLanguage
        self.Framework = Framework
        self.Contributor = Contributor
        self.ProjectContribution = ProjectContribution
        
        # Create programming languages
        self.python = self.ProgrammingLanguage.objects.create(name="Python", category="general")
        self.javascript = self.ProgrammingLanguage.objects.create(name="JavaScript", category="web")
        self.typescript = self.ProgrammingLanguage.objects.create(name="TypeScript", category="web")
        
        # Create frameworks
        self.django = self.Framework.objects.create(name="Django", category="web_backend", language=self.python)
        self.react = self.Framework.objects.create(name="React", category="web_frontend", language=self.javascript)
        
        now = timezone.now()
        
        # Create project 1 - Python/Django project
        self.project1 = Project.objects.create(
            user=self.user,
            name="Python Backend",
            project_tag=1,
            classification_type="coding",
            total_files=10,
            code_files_count=8,
            text_files_count=2,
            image_files_count=0,
            git_repository=True,
            first_commit_date=now,
            created_at=now,
        )
        
        # Add files with line counts to project1
        self.ProjectFile.objects.create(
            project=self.project1,
            file_path="app/models.py",
            filename="models.py",
            file_extension=".py",
            file_type="code",
            line_count=150,
            detected_language=self.python,
        )
        self.ProjectFile.objects.create(
            project=self.project1,
            file_path="app/views.py",
            filename="views.py",
            file_extension=".py",
            file_type="code",
            line_count=200,
            detected_language=self.python,
        )
        self.ProjectFile.objects.create(
            project=self.project1,
            file_path="tests/test_api.py",
            filename="test_api.py",
            file_extension=".py",
            file_type="code",
            line_count=100,
            detected_language=self.python,
        )
        
        # Add ProjectLanguage for project1
        self.ProjectLanguage.objects.create(
            project=self.project1,
            language=self.python,
            file_count=3,
            is_primary=True,
        )
        
        # Add framework for project1
        self.ProjectFramework.objects.create(
            project=self.project1,
            framework=self.django,
            detected_from="dependencies",
        )
        
        # Add contributor for project1
        self.contributor1 = self.Contributor.objects.create(
            name="Stats User",
            email="stats@example.com",
            user=self.user,
        )
        self.ProjectContribution.objects.create(
            project=self.project1,
            contributor=self.contributor1,
            commit_count=25,
            lines_added=500,
            lines_deleted=100,
            percent_of_commits=100.0,
        )
        
        # Create project 2 - JavaScript/React project
        self.project2 = Project.objects.create(
            user=self.user,
            name="React Frontend",
            project_tag=2,
            classification_type="coding",
            total_files=15,
            code_files_count=12,
            text_files_count=3,
            image_files_count=0,
            git_repository=True,
            first_commit_date=now,
            created_at=now,
        )
        
        # Add files with line counts to project2
        self.ProjectFile.objects.create(
            project=self.project2,
            file_path="src/App.js",
            filename="App.js",
            file_extension=".js",
            file_type="code",
            line_count=80,
            detected_language=self.javascript,
        )
        self.ProjectFile.objects.create(
            project=self.project2,
            file_path="src/components/Header.tsx",
            filename="Header.tsx",
            file_extension=".tsx",
            file_type="code",
            line_count=120,
            detected_language=self.typescript,
        )
        
        # Add ProjectLanguage for project2
        self.ProjectLanguage.objects.create(
            project=self.project2,
            language=self.javascript,
            file_count=5,
            is_primary=True,
        )
        self.ProjectLanguage.objects.create(
            project=self.project2,
            language=self.typescript,
            file_count=7,
            is_primary=False,
        )
        
        # Add framework for project2
        self.ProjectFramework.objects.create(
            project=self.project2,
            framework=self.react,
            detected_from="dependencies",
        )
        
        # Add contributor for project2
        self.contributor2 = self.Contributor.objects.create(
            name="Another Dev",
            email="another@example.com",
        )
        self.ProjectContribution.objects.create(
            project=self.project2,
            contributor=self.contributor1,
            commit_count=15,
            lines_added=300,
            lines_deleted=50,
            percent_of_commits=60.0,
        )
        self.ProjectContribution.objects.create(
            project=self.project2,
            contributor=self.contributor2,
            commit_count=10,
            lines_added=200,
            lines_deleted=30,
            percent_of_commits=40.0,
        )
        
        # Create portfolio
        self.portfolio = Portfolio.objects.create(
            user=self.user,
            title="Stats Test Portfolio",
            slug="stats-test-portfolio",
        )
        
        self.client.force_authenticate(user=self.user)
    
    # ==================== Stats Endpoint Tests ====================
    
    def test_portfolio_stats_endpoint_exists(self):
        """Portfolio stats endpoint returns 200."""
        url = reverse("portfolio-stats", args=[self.portfolio.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
    
    def test_portfolio_stats_empty_portfolio(self):
        """Empty portfolio returns zero stats."""
        url = reverse("portfolio-stats", args=[self.portfolio.id])
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        self.assertEqual(data["total_projects"], 0)
        self.assertEqual(data["total_files"], 0)
        self.assertEqual(data["total_lines_of_code"], 0)
        self.assertEqual(data["languages"], [])
        self.assertEqual(data["frameworks"], [])
    
    def test_portfolio_stats_with_projects(self):
        """Portfolio stats aggregates data from all projects."""
        # Add both projects to portfolio
        PortfolioProject.objects.create(portfolio=self.portfolio, project=self.project1, order=0)
        PortfolioProject.objects.create(portfolio=self.portfolio, project=self.project2, order=1)
        
        url = reverse("portfolio-stats", args=[self.portfolio.id])
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        # Basic counts
        self.assertEqual(data["total_projects"], 2)
        self.assertEqual(data["total_files"], 25)  # 10 + 15
        self.assertEqual(data["code_files_count"], 20)  # 8 + 12
        self.assertEqual(data["text_files_count"], 5)  # 2 + 3
    
    def test_portfolio_stats_lines_per_language(self):
        """Stats include lines of code per programming language."""
        PortfolioProject.objects.create(portfolio=self.portfolio, project=self.project1, order=0)
        PortfolioProject.objects.create(portfolio=self.portfolio, project=self.project2, order=1)
        
        url = reverse("portfolio-stats", args=[self.portfolio.id])
        resp = self.client.get(url)
        
        data = resp.json()
        languages = data["languages"]
        
        # Should have 3 languages: Python, JavaScript, TypeScript
        self.assertEqual(len(languages), 3)
        
        # Convert to dict for easier assertions
        lang_dict = {l["language"]: l for l in languages}
        
        # Python: 150 + 200 + 100 = 450 lines
        self.assertIn("Python", lang_dict)
        self.assertEqual(lang_dict["Python"]["lines_of_code"], 450)
        self.assertEqual(lang_dict["Python"]["file_count"], 3)
        
        # JavaScript: 80 lines
        self.assertIn("JavaScript", lang_dict)
        self.assertEqual(lang_dict["JavaScript"]["lines_of_code"], 80)
        self.assertEqual(lang_dict["JavaScript"]["file_count"], 1)
        
        # TypeScript: 120 lines
        self.assertIn("TypeScript", lang_dict)
        self.assertEqual(lang_dict["TypeScript"]["lines_of_code"], 120)
        self.assertEqual(lang_dict["TypeScript"]["file_count"], 1)
    
    def test_portfolio_stats_total_lines(self):
        """Total lines of code sums all code files."""
        PortfolioProject.objects.create(portfolio=self.portfolio, project=self.project1, order=0)
        PortfolioProject.objects.create(portfolio=self.portfolio, project=self.project2, order=1)
        
        url = reverse("portfolio-stats", args=[self.portfolio.id])
        resp = self.client.get(url)
        
        data = resp.json()
        # 450 (Python) + 80 (JS) + 120 (TS) = 650
        self.assertEqual(data["total_lines_of_code"], 650)
    
    def test_portfolio_stats_frameworks(self):
        """Stats include frameworks with project counts."""
        PortfolioProject.objects.create(portfolio=self.portfolio, project=self.project1, order=0)
        PortfolioProject.objects.create(portfolio=self.portfolio, project=self.project2, order=1)
        
        url = reverse("portfolio-stats", args=[self.portfolio.id])
        resp = self.client.get(url)
        
        data = resp.json()
        frameworks = data["frameworks"]
        
        self.assertEqual(len(frameworks), 2)
        
        fw_dict = {f["framework"]: f for f in frameworks}
        
        self.assertIn("Django", fw_dict)
        self.assertEqual(fw_dict["Django"]["project_count"], 1)
        
        self.assertIn("React", fw_dict)
        self.assertEqual(fw_dict["React"]["project_count"], 1)
    
    def test_portfolio_stats_contributors(self):
        """Stats include total contributors and commits."""
        PortfolioProject.objects.create(portfolio=self.portfolio, project=self.project1, order=0)
        PortfolioProject.objects.create(portfolio=self.portfolio, project=self.project2, order=1)
        
        url = reverse("portfolio-stats", args=[self.portfolio.id])
        resp = self.client.get(url)
        
        data = resp.json()
        
        # 2 unique contributors (contributor1 appears in both, contributor2 in project2)
        self.assertEqual(data["total_contributors"], 2)
        
        # Total commits: 25 + 15 + 10 = 50
        self.assertEqual(data["total_commits"], 50)
    
    def test_portfolio_stats_date_range(self):
        """Stats include date range from project dates."""
        PortfolioProject.objects.create(portfolio=self.portfolio, project=self.project1, order=0)
        PortfolioProject.objects.create(portfolio=self.portfolio, project=self.project2, order=1)
        
        url = reverse("portfolio-stats", args=[self.portfolio.id])
        resp = self.client.get(url)
        
        data = resp.json()
        
        self.assertIn("date_range_start", data)
        self.assertIn("date_range_end", data)
    
    # ==================== Stats Caching Tests ====================
    
    def test_stats_cached_after_calculation(self):
        """Stats are cached in portfolio after first calculation."""
        PortfolioProject.objects.create(portfolio=self.portfolio, project=self.project1, order=0)
        
        # First request calculates stats
        url = reverse("portfolio-stats", args=[self.portfolio.id])
        self.client.get(url)
        
        # Refresh from DB and check cached values
        self.portfolio.refresh_from_db()
        self.assertIsNotNone(self.portfolio.stats_updated_at)
        self.assertEqual(self.portfolio.total_projects, 1)
    
    def test_stats_updated_on_add_project(self):
        """Stats are recalculated when project is added."""
        PortfolioProject.objects.create(portfolio=self.portfolio, project=self.project1, order=0)
        
        # Initial stats
        url = reverse("portfolio-stats", args=[self.portfolio.id])
        resp = self.client.get(url)
        initial_projects = resp.json()["total_projects"]
        
        # Add another project
        add_url = reverse("portfolio-add-project", args=[self.portfolio.id])
        self.client.post(add_url, data={"project_id": self.project2.id}, format="json")
        
        # Stats should be updated
        resp = self.client.get(url)
        self.assertEqual(resp.json()["total_projects"], initial_projects + 1)
    
    def test_stats_updated_on_remove_project(self):
        """Stats are recalculated when project is removed."""
        PortfolioProject.objects.create(portfolio=self.portfolio, project=self.project1, order=0)
        PortfolioProject.objects.create(portfolio=self.portfolio, project=self.project2, order=1)
        
        # Initial stats
        url = reverse("portfolio-stats", args=[self.portfolio.id])
        resp = self.client.get(url)
        self.assertEqual(resp.json()["total_projects"], 2)
        
        # Remove project
        remove_url = reverse("portfolio-remove-project", args=[self.portfolio.id, self.project1.id])
        self.client.delete(remove_url)
        
        # Stats should be updated
        resp = self.client.get(url)
        self.assertEqual(resp.json()["total_projects"], 1)
    
    # ==================== Permissions Tests ====================
    
    def test_stats_requires_auth(self):
        """Stats endpoint requires authentication."""
        self.client.logout()
        url = reverse("portfolio-stats", args=[self.portfolio.id])
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (401, 403))
    
    def test_stats_only_owner_can_access(self):
        """Only portfolio owner can access stats."""
        other_user = User.objects.create_user(
            username="other", email="other@example.com", password="pass123"
        )
        self.client.force_authenticate(user=other_user)
        
        url = reverse("portfolio-stats", args=[self.portfolio.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)
    
    def test_stats_languages_sorted_by_lines(self):
        """Languages are sorted by lines of code descending."""
        PortfolioProject.objects.create(portfolio=self.portfolio, project=self.project1, order=0)
        PortfolioProject.objects.create(portfolio=self.portfolio, project=self.project2, order=1)
        
        url = reverse("portfolio-stats", args=[self.portfolio.id])
        resp = self.client.get(url)
        
        languages = resp.json()["languages"]
        
        # Python (450) should be first, TypeScript (120) second, JavaScript (80) third
        self.assertEqual(languages[0]["language"], "Python")
        self.assertEqual(languages[1]["language"], "TypeScript")
        self.assertEqual(languages[2]["language"], "JavaScript")
