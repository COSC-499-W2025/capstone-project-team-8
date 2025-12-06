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

from app.models import Project, Contributor, ProjectContribution, ProjectFile
from django.contrib.auth import get_user_model

User = get_user_model()


class ProjectEndpointsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username="alice", email="alice@example.com", password="pass123")
        self.user2 = User.objects.create_user(username="bob", email="bob@example.com", password="pass123")

        now = timezone.now()
        # Create projects for user1 and user2
        self.p1 = Project.objects.create(
            user=self.user1,
            name="Alice Project",
            project_tag=1,
            project_root_path="alice/root",
            classification_type="coding",
            classification_confidence=0.9,
            total_files=3,
            code_files_count=2,
            text_files_count=1,
            image_files_count=0,
            git_repository=True,
            first_commit_date=now,
            # created_at if present on model will be handled in assertions; creating record is sufficient
        )
        self.p2 = Project.objects.create(
            user=self.user2,
            name="Bob Project",
            project_tag=2,
            project_root_path="bob/root",
            classification_type="writing",
            classification_confidence=0.8,
            total_files=7,
            code_files_count=0,
            text_files_count=7,
            image_files_count=0,
            git_repository=False,
            first_commit_date=now,
        )

    def test_projects_list_requires_auth(self):
        url = reverse("projects-list")
        resp = self.client.get(url)
        # DRF typically returns 401 for unauthenticated requests
        self.assertIn(resp.status_code, (401, 403))

    def test_projects_list_returns_only_user_projects(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("projects-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("projects", data)
        # only Alice's project should be present
        self.assertEqual(len(data["projects"]), 1)
        proj = data["projects"][0]
        self.assertEqual(proj["name"], "Alice Project")
        self.assertEqual(int(proj.get("project_tag", 0)), 1)

    def test_project_detail_patch_and_delete(self):
        detail_url = reverse("projects-detail", args=[self.p1.id])

        # other user cannot access
        self.client.force_authenticate(user=self.user2)
        resp = self.client.get(detail_url)
        # Should be 404 because view limits to user's projects
        self.assertEqual(resp.status_code, 404)

        # owner can retrieve
        self.client.force_authenticate(user=self.user1)
        resp = self.client.get(detail_url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get("id"), self.p1.id)
        self.assertEqual(data.get("name"), "Alice Project")

        # patch name
        resp = self.client.patch(detail_url, data={"name": "Alice Renamed"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.p1.refresh_from_db()
        self.assertEqual(self.p1.name, "Alice Renamed")

        # delete
        resp = self.client.delete(detail_url)
        self.assertEqual(resp.status_code, 200)
        with self.assertRaises(Project.DoesNotExist):
            Project.objects.get(pk=self.p1.id)

    def test_stats_aggregation(self):
        self.client.force_authenticate(user=self.user1)
        # Create another project for user1 to test aggregation totals
        Project.objects.create(
            user=self.user1,
            name="Alice Project 2",
            project_tag=3,
            project_root_path="alice/root2",
            classification_type="coding",
            classification_confidence=0.7,
            total_files=5,
            code_files_count=3,
            text_files_count=2,
            image_files_count=0,
            git_repository=False,
            first_commit_date=timezone.now(),
        )

        url = reverse("projects-stats")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        # total_projects should be 2 for user1
        self.assertEqual(data.get("total_projects"), 2)
        # total_files should equal sum of total_files from both projects for user1 (3 + 5)
        self.assertEqual(int(data.get("total_files", 0)), 8)


class RankedProjectsTests(TestCase):
    """
    Test suite for project ranking by user contribution.
    Ranking formula: (commit_percent * 0.4) + (lines_changed_percent * 0.6)
    """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="pass123")
        
        # Create a contributor linked to the user
        self.contributor = Contributor.objects.create(
            name="Test User",
            email="test@example.com",
            user=self.user
        )
        
        now = timezone.now()
        
        # Project 1: High contribution (50% commits, 600/1000 lines = 60%)
        self.p1 = Project.objects.create(
            user=self.user,
            name="High Contribution Project",
            project_tag=1,
            project_root_path="/high",
            classification_type="coding",
            classification_confidence=0.9,
            total_files=5,
            code_files_count=5,
            git_repository=True,
            first_commit_date=now,
        )
        # Add files to get total line count of 1000
        for i in range(5):
            ProjectFile.objects.create(
                project=self.p1,
                file_path=f"/high/file{i}.py",
                filename=f"file{i}.py",
                file_extension="py",
                file_type="code",
                line_count=200,  # 5 files * 200 = 1000 lines
            )
        # User contributed 10 commits (50% of 20 total), 600 lines changed
        ProjectContribution.objects.create(
            project=self.p1,
            contributor=self.contributor,
            commit_count=10,
            lines_added=400,
            lines_deleted=200,
            percent_of_commits=50.0,
        )
        
        # Project 2: Medium contribution (30% commits, 300/2000 lines = 15%)
        self.p2 = Project.objects.create(
            user=self.user,
            name="Medium Contribution Project",
            project_tag=2,
            project_root_path="/medium",
            classification_type="coding",
            classification_confidence=0.85,
            total_files=10,
            code_files_count=10,
            git_repository=True,
            first_commit_date=now,
        )
        for i in range(10):
            ProjectFile.objects.create(
                project=self.p2,
                file_path=f"/medium/file{i}.py",
                filename=f"file{i}.py",
                file_extension="py",
                file_type="code",
                line_count=200,  # 10 files * 200 = 2000 lines
            )
        ProjectContribution.objects.create(
            project=self.p2,
            contributor=self.contributor,
            commit_count=6,
            lines_added=200,
            lines_deleted=100,
            percent_of_commits=30.0,
        )
        
        # Project 3: Low contribution (20% commits, 100/500 lines = 20%)
        self.p3 = Project.objects.create(
            user=self.user,
            name="Low Contribution Project",
            project_tag=3,
            project_root_path="/low",
            classification_type="coding",
            classification_confidence=0.8,
            total_files=2,
            code_files_count=2,
            git_repository=True,
            first_commit_date=now,
        )
        for i in range(2):
            ProjectFile.objects.create(
                project=self.p3,
                file_path=f"/low/file{i}.py",
                filename=f"file{i}.py",
                file_extension="py",
                file_type="code",
                line_count=250,  # 2 files * 250 = 500 lines
            )
        ProjectContribution.objects.create(
            project=self.p3,
            contributor=self.contributor,
            commit_count=4,
            lines_added=60,
            lines_deleted=40,
            percent_of_commits=20.0,
        )
        
        # Project 4: No contribution data (should be ranked last or excluded)
        self.p4 = Project.objects.create(
            user=self.user,
            name="No Contribution Project",
            project_tag=4,
            project_root_path="/none",
            classification_type="coding",
            classification_confidence=0.75,
            total_files=3,
            code_files_count=3,
            git_repository=False,  # Not a git repo
            first_commit_date=None,
        )

    def test_ranked_projects_requires_auth(self):
        """Test that the endpoint requires authentication"""
        url = reverse("projects-ranked")
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (401, 403))

    def test_ranked_projects_returns_correct_order(self):
        """
        Test projects are ranked correctly by contribution score.
        Expected order:
        1. High Contribution: (50*0.4) + (60*0.6) = 20 + 36 = 56
        2. Low Contribution: (20*0.4) + (20*0.6) = 8 + 12 = 20
        3. Medium Contribution: (30*0.4) + (15*0.6) = 12 + 9 = 21
        Actually: High > Medium > Low > No contribution
        """
        self.client.force_authenticate(user=self.user)
        url = reverse("projects-ranked")
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("projects", data)
        
        projects = data["projects"]
        # Should have 3 projects with git contributions
        self.assertGreaterEqual(len(projects), 3)
        
        # Verify High Contribution is first
        self.assertEqual(projects[0]["name"], "High Contribution Project")
        self.assertIn("contribution_score", projects[0])
        
        # Verify scores are in descending order
        for i in range(len(projects) - 1):
            score_current = projects[i].get("contribution_score", 0)
            score_next = projects[i + 1].get("contribution_score", 0)
            self.assertGreaterEqual(score_current, score_next)

    def test_ranked_projects_includes_contribution_metrics(self):
        """Test that each project includes contribution metrics"""
        self.client.force_authenticate(user=self.user)
        url = reverse("projects-ranked")
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        projects = data["projects"]
        
        # Check first project has all required fields
        first_project = projects[0]
        self.assertIn("id", first_project)
        self.assertIn("name", first_project)
        self.assertIn("contribution_score", first_project)
        self.assertIn("commit_percentage", first_project)
        self.assertIn("lines_changed_percentage", first_project)
        self.assertIn("total_commits", first_project)
        self.assertIn("total_lines_changed", first_project)
        self.assertIn("total_project_lines", first_project)

    def test_ranked_projects_excludes_non_git_projects(self):
        """Test that projects without git contributions are excluded or ranked last"""
        self.client.force_authenticate(user=self.user)
        url = reverse("projects-ranked")
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        projects = data["projects"]
        
        # No Contribution Project should either be excluded or have score of 0
        no_contrib_project = next(
            (p for p in projects if p["name"] == "No Contribution Project"),
            None
        )
        
        if no_contrib_project:
            # If included, should have score of 0
            self.assertEqual(no_contrib_project.get("contribution_score", 0), 0)

    def test_ranked_projects_user_isolation(self):
        """Test that ranking only shows the authenticated user's projects"""
        # Create another user with projects
        other_user = User.objects.create_user(username="other", email="other@example.com", password="pass123")
        other_contributor = Contributor.objects.create(
            name="Other User",
            email="other@example.com",
            user=other_user
        )
        
        other_project = Project.objects.create(
            user=other_user,
            name="Other User Project",
            project_tag=5,
            project_root_path="/other",
            classification_type="coding",
            classification_confidence=0.9,
            total_files=5,
            code_files_count=5,
            git_repository=True,
            first_commit_date=timezone.now(),
        )
        ProjectFile.objects.create(
            project=other_project,
            file_path="/other/file.py",
            filename="file.py",
            file_extension="py",
            file_type="code",
            line_count=1000,
        )
        ProjectContribution.objects.create(
            project=other_project,
            contributor=other_contributor,
            commit_count=50,
            lines_added=800,
            lines_deleted=200,
            percent_of_commits=100.0,
        )
        
        # Test user should only see their own projects
        self.client.force_authenticate(user=self.user)
        url = reverse("projects-ranked")
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        projects = data["projects"]
        
        # Should not include other user's project
        project_names = [p["name"] for p in projects]
        self.assertNotIn("Other User Project", project_names)

    def test_ranked_projects_correct_score_calculation(self):
        """Test that contribution scores are calculated correctly"""
        self.client.force_authenticate(user=self.user)
        url = reverse("projects-ranked")
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        projects = data["projects"]
        
        # Find High Contribution Project and verify calculation
        high_contrib = next(p for p in projects if p["name"] == "High Contribution Project")
        
        # Expected: (50*0.4) + (60*0.6) = 56
        expected_score = (50.0 * 0.4) + (60.0 * 0.6)
        actual_score = high_contrib["contribution_score"]
        
        self.assertAlmostEqual(actual_score, expected_score, places=1)
