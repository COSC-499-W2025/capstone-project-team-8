from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.utils import timezone

from app.models import Project
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
