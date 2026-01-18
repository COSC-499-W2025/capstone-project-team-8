import os
import sys
import django

# Ensure backend package is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
django.setup()

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from app.models import Resume


User = get_user_model()


class ResumeEndpointsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="resume_user",
            email="resume@example.com",
            password="pass12345"
        )

    def test_templates_endpoint_requires_authentication(self):
        url = reverse("resume-templates")
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (401, 403))

    def test_templates_endpoint_returns_available_templates(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("resume-templates")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("templates", data)
        self.assertGreaterEqual(len(data["templates"]), 1)
        first_template = data["templates"][0]
        self.assertIn("id", first_template)
        self.assertIn("name", first_template)
        self.assertIn("ai_supported", first_template)

    def test_preview_endpoint_returns_context_for_template(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("resume-preview")
        resp = self.client.get(url, {"template_id": "classic"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("template", data)
        self.assertEqual(data["template"]["id"], "classic")
        self.assertIn("context", data)
        context = data["context"]
        self.assertIn("summary", context)
        self.assertIn("projects", context)
        self.assertIsInstance(context["projects"], list)


class ResumeDetailEndpointTests(TestCase):
    """Tests for GET /api/resume/{id}/ endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="detail_user",
            email="detail@example.com",
            password="pass12345"
        )
        self.other_user = User.objects.create_user(
            username="other_user",
            email="other@example.com",
            password="pass12345"
        )
        self.resume = Resume.objects.create(
            user=self.user,
            name="Test Resume",
            content={"summary": "Test summary", "skills": ["Python", "Django"]}
        )

    def test_get_resume_requires_authentication(self):
        """GET /api/resume/{id}/ requires auth."""
        url = reverse("resume-detail", kwargs={"pk": self.resume.id})
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (401, 403))

    def test_get_resume_returns_data(self):
        """Authenticated user can get their resume."""
        self.client.force_authenticate(user=self.user)
        url = reverse("resume-detail", kwargs={"pk": self.resume.id})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["id"], self.resume.id)
        self.assertEqual(data["name"], "Test Resume")
        self.assertEqual(data["content"]["summary"], "Test summary")

    def test_get_resume_404_for_nonexistent(self):
        """GET returns 404 for nonexistent resume."""
        self.client.force_authenticate(user=self.user)
        url = reverse("resume-detail", kwargs={"pk": 99999})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_get_resume_404_for_other_users_resume(self):
        """User cannot access another user's resume."""
        self.client.force_authenticate(user=self.other_user)
        url = reverse("resume-detail", kwargs={"pk": self.resume.id})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)


class ResumeGenerateEndpointTests(TestCase):
    """Tests for POST /api/resume/generate/ endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="generate_user",
            email="generate@example.com",
            password="pass12345"
        )

    def test_generate_resume_requires_authentication(self):
        """POST /api/resume/generate/ requires auth."""
        url = reverse("resume-generate")
        resp = self.client.post(url, {"name": "New Resume"})
        self.assertIn(resp.status_code, (401, 403))

    def test_generate_resume_creates_new_resume(self):
        """Authenticated user can generate a new resume."""
        self.client.force_authenticate(user=self.user)
        url = reverse("resume-generate")
        payload = {"name": "My Generated Resume"}
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertIn("id", data)
        self.assertEqual(data["name"], "My Generated Resume")
        # Verify it's saved in database
        resume = Resume.objects.get(id=data["id"])
        self.assertEqual(resume.user, self.user)

    def test_generate_resume_requires_name(self):
        """Name field is required."""
        self.client.force_authenticate(user=self.user)
        url = reverse("resume-generate")
        payload = {}
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, 400)


class ResumeEditEndpointTests(TestCase):
    """Tests for POST /api/resume/{id}/edit/ endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="edit_user",
            email="edit@example.com",
            password="pass12345"
        )
        self.other_user = User.objects.create_user(
            username="other_edit_user",
            email="other_edit@example.com",
            password="pass12345"
        )
        self.resume = Resume.objects.create(
            user=self.user,
            name="Original Name",
            content={"summary": "Original summary"}
        )

    def test_edit_resume_requires_authentication(self):
        """POST /api/resume/{id}/edit/ requires auth."""
        url = reverse("resume-edit", kwargs={"pk": self.resume.id})
        resp = self.client.post(url, {"name": "New Name"})
        self.assertIn(resp.status_code, (401, 403))

    def test_edit_resume_updates_name(self):
        """Authenticated user can update resume name."""
        self.client.force_authenticate(user=self.user)
        url = reverse("resume-edit", kwargs={"pk": self.resume.id})
        payload = {"name": "Updated Name"}
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["name"], "Updated Name")
        # Verify it's updated in database
        self.resume.refresh_from_db()
        self.assertEqual(self.resume.name, "Updated Name")

    def test_edit_resume_updates_content(self):
        """Authenticated user can update resume content."""
        self.client.force_authenticate(user=self.user)
        url = reverse("resume-edit", kwargs={"pk": self.resume.id})
        payload = {"content": {"summary": "Updated summary", "skills": ["Python"]}}
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["content"]["summary"], "Updated summary")
        self.resume.refresh_from_db()
        self.assertEqual(self.resume.content["summary"], "Updated summary")

    def test_edit_resume_404_for_nonexistent(self):
        """POST returns 404 for nonexistent resume."""
        self.client.force_authenticate(user=self.user)
        url = reverse("resume-edit", kwargs={"pk": 99999})
        resp = self.client.post(url, {"name": "Test"}, format="json")
        self.assertEqual(resp.status_code, 404)

    def test_edit_resume_404_for_other_users_resume(self):
        """User cannot edit another user's resume."""
        self.client.force_authenticate(user=self.other_user)
        url = reverse("resume-edit", kwargs={"pk": self.resume.id})
        resp = self.client.post(url, {"name": "Hacked"}, format="json")
        self.assertEqual(resp.status_code, 404)
