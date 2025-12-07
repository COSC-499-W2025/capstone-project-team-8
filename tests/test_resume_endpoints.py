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
