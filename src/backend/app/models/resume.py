from django.db import models
from app.models.user import User


class Resume(models.Model):
	user = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name='resumes',
		help_text="The user who owns this resume"
	)
	name = models.CharField(
		max_length=255,
		blank=True,
		default="",
		help_text="Optional name/title for this resume"
	)
	content = models.JSONField(
		default=dict,
		blank=True,
		help_text="Resume content stored as JSON (skills, projects, education, etc.)"
	)
	theme = models.CharField(
		max_length=64,
		blank=True,
		default="classic",
		help_text="RenderCV theme used when generating saved resume exports"
	)
	rendercv_yaml = models.TextField(
		blank=True,
		default="",
		help_text="Saved RenderCV YAML generated from the resume content"
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = 'resumes'
		ordering = ['-updated_at']
		indexes = [
			models.Index(fields=['user', '-updated_at']),
		]

	def __str__(self):
		name_display = self.name or f"Resume {self.id}"
		return f"{name_display} ({self.user.username})"


"""Resume and ResumeItem models."""
