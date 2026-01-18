"""
Tests for the Resume model.
TDD: These tests are written before implementing the Resume model.
"""
import os
import sys
import django

# Ensure backend package is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


class ResumeModelTests(TestCase):
    """Tests for the Resume model."""

    def setUp(self):
        """Create a test user for resume tests."""
        self.user = User.objects.create_user(
            username="resume_test_user",
            email="resumetest@example.com",
            password="testpass123"
        )

    def test_resume_model_exists(self):
        """Test that Resume model can be imported."""
        from app.models import Resume
        self.assertIsNotNone(Resume)

    def test_create_resume_for_user(self):
        """Test creating a resume linked to a user."""
        from app.models import Resume
        
        resume = Resume.objects.create(
            user=self.user,
            name="My First Resume"
        )
        
        self.assertIsNotNone(resume.id)
        self.assertEqual(resume.user, self.user)
        self.assertEqual(resume.name, "My First Resume")

    def test_resume_has_timestamps(self):
        """Test that resume has created_at and updated_at timestamps."""
        from app.models import Resume
        
        resume = Resume.objects.create(
            user=self.user,
            name="Timestamped Resume"
        )
        
        self.assertIsNotNone(resume.created_at)
        self.assertIsNotNone(resume.updated_at)

    def test_resume_content_defaults_to_empty_dict(self):
        """Test that content field defaults to empty dict."""
        from app.models import Resume
        
        resume = Resume.objects.create(
            user=self.user,
            name="Content Test Resume"
        )
        
        self.assertEqual(resume.content, {})

    def test_resume_can_store_json_content(self):
        """Test that resume can store JSON content."""
        from app.models import Resume
        
        content = {
            "summary": "Experienced developer",
            "skills": ["Python", "Django", "React"],
            "projects": [
                {"name": "Project 1", "description": "A cool project"}
            ]
        }
        
        resume = Resume.objects.create(
            user=self.user,
            name="JSON Content Resume",
            content=content
        )
        
        # Reload from database
        resume.refresh_from_db()
        
        self.assertEqual(resume.content["summary"], "Experienced developer")
        self.assertEqual(len(resume.content["skills"]), 3)
        self.assertEqual(resume.content["projects"][0]["name"], "Project 1")

    def test_user_can_have_multiple_resumes(self):
        """Test that a user can have multiple resumes."""
        from app.models import Resume
        
        resume1 = Resume.objects.create(user=self.user, name="Resume 1")
        resume2 = Resume.objects.create(user=self.user, name="Resume 2")
        resume3 = Resume.objects.create(user=self.user, name="Resume 3")
        
        user_resumes = Resume.objects.filter(user=self.user)
        self.assertEqual(user_resumes.count(), 3)

    def test_resume_deleted_when_user_deleted(self):
        """Test that resumes are deleted when user is deleted (CASCADE)."""
        from app.models import Resume
        
        temp_user = User.objects.create_user(
            username="temp_user",
            email="temp@example.com",
            password="temppass"
        )
        
        Resume.objects.create(user=temp_user, name="Temp Resume")
        self.assertEqual(Resume.objects.filter(user=temp_user).count(), 1)
        
        temp_user.delete()
        self.assertEqual(Resume.objects.filter(user=temp_user).count(), 0)

    def test_resume_str_representation(self):
        """Test the string representation of a resume."""
        from app.models import Resume
        
        resume = Resume.objects.create(
            user=self.user,
            name="Developer Resume"
        )
        
        # Should include name and username
        str_repr = str(resume)
        self.assertIn("Developer Resume", str_repr)

    def test_resume_name_can_be_blank(self):
        """Test that resume name can be blank (will get auto-generated)."""
        from app.models import Resume
        
        resume = Resume.objects.create(
            user=self.user,
            name=""
        )
        
        self.assertIsNotNone(resume.id)
