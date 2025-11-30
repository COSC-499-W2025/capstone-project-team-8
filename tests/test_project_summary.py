import os
import sys
import django

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
django.setup()

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.utils import timezone
from unittest.mock import patch, MagicMock

from app.models import (
    Project, Contributor, ProjectContribution, ProjectFile,
    ProgrammingLanguage, Framework, ProjectLanguage, ProjectFramework
)
from django.contrib.auth import get_user_model

User = get_user_model()


class TopProjectsSummaryTests(TestCase):
    """Test suite for top 3 ranked projects with AI summaries"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", 
            email="test@example.com", 
            password="pass123"
        )
        
        # Create a contributor linked to the user
        self.contributor = Contributor.objects.create(
            name="Test User",
            email="test@example.com",
            user=self.user
        )
        
        # Create languages
        self.python = ProgrammingLanguage.objects.create(name="Python")
        self.javascript = ProgrammingLanguage.objects.create(name="JavaScript")
        self.typescript = ProgrammingLanguage.objects.create(name="TypeScript")
        
        # Create frameworks
        self.django = Framework.objects.create(name="Django")
        self.react = Framework.objects.create(name="React")
        self.postgres = Framework.objects.create(name="PostgreSQL")
        
        now = timezone.now()
        
        # Project 1: Highest contribution (60% commits, 80% lines)
        # Expected score: (60*0.4) + (80*0.6) = 24 + 48 = 72
        self.p1 = Project.objects.create(
            user=self.user,
            name="E-commerce Platform",
            project_tag=1,
            project_root_path="/ecommerce",
            classification_type="coding",
            classification_confidence=0.95,
            total_files=20,
            code_files_count=18,
            git_repository=True,
            first_commit_date=now,
            ai_summary="Led development of e-commerce platform using Django and React with 60% of commits.",
            llm_consent=True,
            ai_summary_generated_at=now
        )
        # Add files (1000 total lines)
        for i in range(10):
            ProjectFile.objects.create(
                project=self.p1,
                file_path=f"/ecommerce/file{i}.py",
                filename=f"file{i}.py",
                file_extension="py",
                file_type="code",
                line_count=100,
            )
        # User contribution: 800 lines out of 1000
        ProjectContribution.objects.create(
            project=self.p1,
            contributor=self.contributor,
            commit_count=30,
            lines_added=600,
            lines_deleted=200,
            percent_of_commits=60.0,
        )
        # Add languages and frameworks
        ProjectLanguage.objects.create(project=self.p1, language=self.python, file_count=8, is_primary=True)
        ProjectLanguage.objects.create(project=self.p1, language=self.javascript, file_count=5)
        ProjectFramework.objects.create(project=self.p1, framework=self.django)
        ProjectFramework.objects.create(project=self.p1, framework=self.react)
        
        # Project 2: Medium contribution (40% commits, 50% lines)
        # Expected score: (40*0.4) + (50*0.6) = 16 + 30 = 46
        self.p2 = Project.objects.create(
            user=self.user,
            name="Mobile Game",
            project_tag=2,
            project_root_path="/game",
            classification_type="coding",
            classification_confidence=0.85,
            total_files=15,
            code_files_count=12,
            git_repository=True,
            first_commit_date=now,
            ai_summary="Contributed to mobile game using TypeScript with focus on game mechanics.",
            llm_consent=True,
            ai_summary_generated_at=now
        )
        for i in range(8):
            ProjectFile.objects.create(
                project=self.p2,
                file_path=f"/game/file{i}.cs",
                filename=f"file{i}.cs",
                file_extension="cs",
                file_type="code",
                line_count=100,
            )
        ProjectContribution.objects.create(
            project=self.p2,
            contributor=self.contributor,
            commit_count=20,
            lines_added=300,
            lines_deleted=100,
            percent_of_commits=40.0,
        )
        ProjectLanguage.objects.create(project=self.p2, language=self.typescript, file_count=8, is_primary=True)
        
        # Project 3: Lower contribution (20% commits, 30% lines)
        # Expected score: (20*0.4) + (30*0.6) = 8 + 18 = 26
        self.p3 = Project.objects.create(
            user=self.user,
            name="Data Analysis Tool",
            project_tag=3,
            project_root_path="/data-tool",
            classification_type="coding",
            classification_confidence=0.80,
            total_files=10,
            code_files_count=8,
            git_repository=True,
            first_commit_date=now,
            ai_summary="",  # No summary - user didn't consent to LLM
            llm_consent=False
        )
        for i in range(5):
            ProjectFile.objects.create(
                project=self.p3,
                file_path=f"/data-tool/file{i}.py",
                filename=f"file{i}.py",
                file_extension="py",
                file_type="code",
                line_count=100,
            )
        ProjectContribution.objects.create(
            project=self.p3,
            contributor=self.contributor,
            commit_count=10,
            lines_added=120,
            lines_deleted=30,
            percent_of_commits=20.0,
        )
        ProjectLanguage.objects.create(project=self.p3, language=self.python, file_count=5, is_primary=True)
    
    def test_summary_endpoint_requires_auth(self):
        """Test that endpoint requires authentication"""
        url = reverse("projects-ranked-summary")
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (401, 403))
    
    def test_summary_returns_top_3_projects(self):
        """Test that endpoint returns exactly top 3 projects"""
        self.client.force_authenticate(user=self.user)
        url = reverse("projects-ranked-summary")
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        self.assertIn("top_projects", data)
        self.assertEqual(len(data["top_projects"]), 3)
    
    def test_projects_ranked_correctly(self):
        """Test that projects are returned in correct order by contribution score"""
        self.client.force_authenticate(user=self.user)
        url = reverse("projects-ranked-summary")
        resp = self.client.get(url)
        
        data = resp.json()
        projects = data["top_projects"]
        
        # Check order: p1 (72) > p2 (46) > p3 (26)
        self.assertEqual(projects[0]["name"], "E-commerce Platform")
        self.assertEqual(projects[1]["name"], "Mobile Game")
        self.assertEqual(projects[2]["name"], "Data Analysis Tool")
        
        # Verify scores are descending
        self.assertGreater(projects[0]["contribution_score"], projects[1]["contribution_score"])
        self.assertGreater(projects[1]["contribution_score"], projects[2]["contribution_score"])
    
    def test_includes_languages_and_frameworks(self):
        """Test that response includes languages and frameworks"""
        self.client.force_authenticate(user=self.user)
        url = reverse("projects-ranked-summary")
        resp = self.client.get(url)
        
        data = resp.json()
        project = data["top_projects"][0]  # E-commerce Platform
        
        self.assertIn("languages", project)
        self.assertIn("frameworks", project)
        self.assertIn("Python", project["languages"])
        self.assertIn("JavaScript", project["languages"])
        self.assertIn("Django", project["frameworks"])
        self.assertIn("React", project["frameworks"])
    
    def test_stored_summary_returned(self):
        """Test that pre-generated AI summary from database is returned"""
        self.client.force_authenticate(user=self.user)
        url = reverse("projects-ranked-summary")
        resp = self.client.get(url)
        
        data = resp.json()
        projects = data["top_projects"]
        
        # Check that summaries match what's stored in database
        self.assertEqual(
            projects[0]["summary"], 
            "Led development of e-commerce platform using Django and React with 60% of commits."
        )
        self.assertTrue(projects[0]["llm_consent"])
        
        self.assertEqual(
            projects[1]["summary"],
            "Contributed to mobile game using TypeScript with focus on game mechanics."
        )
        self.assertTrue(projects[1]["llm_consent"])
        
        # Project 3 has no summary (no consent)
        self.assertEqual(projects[2]["summary"], "No summary available")
        self.assertFalse(projects[2]["llm_consent"])
    
    def test_no_ai_calls_made(self):
        """Test that API does not call AI service (summaries are pre-generated)"""
        with patch('app.views.project_views.ai_analyze') as mock_ai:
            self.client.force_authenticate(user=self.user)
            url = reverse("projects-ranked-summary")
            resp = self.client.get(url)
            
            # AI should NOT be called since we're using stored summaries
            mock_ai.assert_not_called()
    
    def test_contribution_metrics_included(self):
        """Test that all contribution metrics are included"""
        self.client.force_authenticate(user=self.user)
        url = reverse("projects-ranked-summary")
        resp = self.client.get(url)
        
        data = resp.json()
        project = data["top_projects"][0]
        
        # Check all required fields
        required_fields = [
            'project_id', 'name', 'contribution_score', 'commit_percentage',
            'lines_changed_percentage', 'total_commits', 'total_lines_changed',
            'total_project_lines', 'classification_type', 'languages', 
            'frameworks', 'summary', 'llm_consent'
        ]
        
        for field in required_fields:
            self.assertIn(field, project, f"Missing field: {field}")
    
    def test_empty_projects_list(self):
        """Test behavior when user has no projects"""
        new_user = User.objects.create_user(
            username="newuser",
            email="newuser@example.com",
            password="pass123"
        )
        self.client.force_authenticate(user=new_user)
        url = reverse("projects-ranked-summary")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data["top_projects"]), 0)

    def test_user_isolation(self):
        """Test that users only see their own projects"""
        other_user = User.objects.create_user(
            username="otheruser",
            email="otheruser@example.com",
            password="pass123"
        )
        self.client.force_authenticate(user=other_user)
        url = reverse("projects-ranked-summary")
        resp = self.client.get(url)
        data = resp.json()
        self.assertEqual(len(data["top_projects"]), 0)

if __name__ == '__main__':
    import unittest
    unittest.main()
