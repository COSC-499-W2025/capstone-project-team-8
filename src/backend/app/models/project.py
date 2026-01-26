from django.db import models
from django.utils import timezone

from app.models.user import User
from app.models.language import ProgrammingLanguage, Framework

class Project(models.Model):
	# Relationships
	languages = models.ManyToManyField(
		ProgrammingLanguage,
		through='ProjectLanguage',
		related_name='projects'
	)
	frameworks = models.ManyToManyField(
		Framework,
		through='ProjectFramework',
		related_name='projects'
	)
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
	name = models.CharField(max_length=255)
	description = models.TextField(blank=True)
	thumbnail = models.ImageField(upload_to='project_thumbnails/', null=True, blank=True)
	classification_type = models.CharField(
		max_length=50,
		choices=[
			('coding', 'Coding'),
			('writing', 'Writing'),
			('art', 'Art/Design'),
			('mixed:coding+writing', 'Mixed: Coding + Writing'),
			('mixed:coding+art', 'Mixed: Coding + Art'),
			('mixed:writing+art', 'Mixed: Writing + Art'),
			('unknown', 'Unknown')
		],
		default='unknown'
	)
	classification_confidence = models.FloatField(default=0.0)
	project_root_path = models.CharField(max_length=500, blank=True)
	project_tag = models.IntegerField(null=True, blank=True)
	total_files = models.IntegerField(default=0)
	code_files_count = models.IntegerField(default=0)
	text_files_count = models.IntegerField(default=0)
	image_files_count = models.IntegerField(default=0)
	git_repository = models.BooleanField(default=False)
	first_commit_date = models.DateTimeField(null=True, blank=True)
	resume_bullet_points = models.JSONField(default=list, blank=True)
	upload_source = models.CharField(max_length=50, default='zip_file')
	original_zip_name = models.CharField(max_length=255, blank=True)
	created_at = models.DateTimeField(null=True, blank=True, default=timezone.now)
	updated_at = models.DateTimeField(null=True, blank=True)
	ai_summary = models.TextField(blank=True)
	ai_summary_generated_at = models.DateTimeField(null=True, blank=True)
	llm_consent = models.BooleanField(default=False)
	class Meta:
		db_table = 'projects'
		ordering = ['-created_at']
		indexes = [
			models.Index(fields=['user', '-created_at']),
			models.Index(fields=['classification_type']),
			models.Index(fields=['git_repository']),
		]
	def __str__(self):
		return f"{self.user.username} - {self.name}"

class ProjectFile(models.Model):
	project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
	file_path = models.CharField(max_length=1000)
	filename = models.CharField(max_length=255)
	file_extension = models.CharField(max_length=20, blank=True)
	content_hash = models.CharField(max_length=64, blank=True, db_index=True)
	is_duplicate = models.BooleanField(default=False)
	original_file = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='duplicates')
	file_type = models.CharField(
		max_length=20,
		choices=[
			('code', 'Code'),
			('content', 'Content/Text'),
			('image', 'Image'),
			('unknown', 'Unknown')
		]
	)
	file_size_bytes = models.BigIntegerField(null=True, blank=True)
	line_count = models.IntegerField(null=True, blank=True)
	character_count = models.IntegerField(null=True, blank=True)
	content_preview = models.TextField(blank=True, max_length=10000)
	is_content_truncated = models.BooleanField(default=False)
	detected_language = models.ForeignKey(
		'ProgrammingLanguage',
		on_delete=models.SET_NULL,
		null=True,
		blank=True
	)
	created_at = models.DateTimeField(auto_now_add=True)
	class Meta:
		db_table = 'project_files'
		indexes = [
			models.Index(fields=['project', 'file_type']),
			models.Index(fields=['file_extension']),
		]
	def __str__(self):
		return f"{self.project.name} - {self.filename}"

class ProjectLanguage(models.Model):
	project = models.ForeignKey(Project, on_delete=models.CASCADE)
	language = models.ForeignKey('ProgrammingLanguage', on_delete=models.CASCADE)
	file_count = models.IntegerField(default=0)
	is_primary = models.BooleanField(default=False)
	class Meta:
		db_table = 'project_languages'
		unique_together = ['project', 'language']

class ProjectFramework(models.Model):
	project = models.ForeignKey(Project, on_delete=models.CASCADE)
	framework = models.ForeignKey('Framework', on_delete=models.CASCADE)
	detected_from = models.CharField(
		max_length=50,
		choices=[
			('dependencies', 'Dependency Files'),
			('imports', 'Code Imports'),
			('config', 'Configuration Files'),
			('filenames', 'File Names')
		],
		default='dependencies'
	)
	class Meta:
		db_table = 'project_frameworks'
		unique_together = ['project', 'framework']

class Contributor(models.Model):
	name = models.CharField(max_length=255)
	email = models.EmailField(max_length=255, blank=True)
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='contributor_profiles')
	email_domain = models.CharField(max_length=255, blank=True)
	normalized_name = models.CharField(max_length=255, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	class Meta:
		db_table = 'contributors'
		unique_together = ['name', 'email']
		indexes = [
			models.Index(fields=['email']),
			models.Index(fields=['normalized_name']),
		]
	def save(self, *args, **kwargs):
		if self.email:
			self.email_domain = self.email.split('@')[-1] if '@' in self.email else ''
		self.normalized_name = self.name.lower().replace(' ', '')
		super().save(*args, **kwargs)
	def __str__(self):
		return f"{self.name} ({self.email})" if self.email else self.name

class ProjectContribution(models.Model):
	project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='contributions')
	contributor = models.ForeignKey(Contributor, on_delete=models.CASCADE, related_name='contributions')
	commit_count = models.IntegerField(default=0)
	lines_added = models.IntegerField(default=0)
	lines_deleted = models.IntegerField(default=0)
	percent_of_commits = models.FloatField(default=0.0)
	net_lines = models.IntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	class Meta:
		db_table = 'project_contributions'
		unique_together = ['project', 'contributor']
		indexes = [
			models.Index(fields=['project', '-commit_count']),
			models.Index(fields=['contributor', '-commit_count']),
		]
	def save(self, *args, **kwargs):
		self.net_lines = self.lines_added - self.lines_deleted
		super().save(*args, **kwargs)
	def __str__(self):
		return f"{self.contributor.name} -> {self.project.name} ({self.commit_count} commits)"
"""Project and File models."""
