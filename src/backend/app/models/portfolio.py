from django.db import models
from app.models.user import User


	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
	title = models.CharField(max_length=255)
	slug = models.SlugField(max_length=100, unique=True, db_index=True)
	description = models.TextField(blank=True)
	summary = models.TextField(blank=True)
	summary_generated_at = models.DateTimeField(null=True, blank=True)
	is_public = models.BooleanField(default=False)
	target_audience = models.CharField(max_length=100, blank=True)
	tone = models.CharField(
		max_length=20,
		choices=[
			('professional', 'Professional'),
			('casual', 'Casual'),
			('technical', 'Technical'),
			('creative', 'Creative'),
		],
		default='professional'
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	projects = models.ManyToManyField(
		'Project',  # String reference to avoid circular import
		through='PortfolioProject',
		related_name='portfolios'
	)
	class Meta:
		db_table = 'portfolios'
		ordering = ['-created_at']
		indexes = [
			models.Index(fields=['user', '-created_at']),
			models.Index(fields=['is_public', '-created_at']),
		]
	def __str__(self):
		return f"{self.user.username} - {self.title}"

	portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='portfolio_projects')
	project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='portfolio_entries')  # String reference
	order = models.PositiveIntegerField(default=0)
	notes = models.TextField(blank=True)
	featured = models.BooleanField(default=False)
	added_at = models.DateTimeField(auto_now_add=True)
	class Meta:
		db_table = 'portfolio_projects'
		unique_together = ['portfolio', 'project']
		ordering = ['order', '-added_at']
		indexes = [
			models.Index(fields=['portfolio', 'order']),
		]
	def __str__(self):
		return f"{self.portfolio.title} - {self.project.name} (order: {self.order})"
"""Portfolio and PortfolioProject models."""
