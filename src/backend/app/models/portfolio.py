
from django.db import models
from django.db.models import Sum, Count
from django.utils import timezone
from app.models.user import User


class Portfolio(models.Model):
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
	
	# Cached statistics fields
	total_projects = models.IntegerField(default=0)
	total_files = models.IntegerField(default=0)
	code_files_count = models.IntegerField(default=0)
	text_files_count = models.IntegerField(default=0)
	image_files_count = models.IntegerField(default=0)
	total_lines_of_code = models.IntegerField(default=0)
	total_commits = models.IntegerField(default=0)
	total_contributors = models.IntegerField(default=0)
	languages_stats = models.JSONField(default=list, blank=True)  # [{"language": str, "lines_of_code": int, "file_count": int}]
	frameworks_stats = models.JSONField(default=list, blank=True)  # [{"framework": str, "project_count": int}]
	date_range_start = models.DateTimeField(null=True, blank=True)
	date_range_end = models.DateTimeField(null=True, blank=True)
	stats_updated_at = models.DateTimeField(null=True, blank=True)

	class Meta:
		db_table = 'portfolios'
		ordering = ['-created_at']
		indexes = [
			models.Index(fields=['user', '-created_at']),
			models.Index(fields=['is_public', '-created_at']),
		]

	def __str__(self):
		return f"{self.user.username} - {self.title}"
	
	def update_cached_stats(self):
		"""
		Recalculate and cache all portfolio statistics from projects.
		Called when projects are added/removed or on first stats access.
		"""
		from app.models.project import ProjectFile, ProjectFramework, ProjectContribution
		
		projects = self.projects.all()
		project_ids = list(projects.values_list('id', flat=True))
		
		# Basic project counts
		self.total_projects = len(project_ids)
		
		if not project_ids:
			# Empty portfolio - reset all stats
			self.total_files = 0
			self.code_files_count = 0
			self.text_files_count = 0
			self.image_files_count = 0
			self.total_lines_of_code = 0
			self.total_commits = 0
			self.total_contributors = 0
			self.languages_stats = []
			self.frameworks_stats = []
			self.date_range_start = None
			self.date_range_end = None
			self.stats_updated_at = timezone.now()
			self.save()
			return
		
		# Aggregate file counts from projects
		file_totals = projects.aggregate(
			total_files=Sum('total_files'),
			code_files=Sum('code_files_count'),
			text_files=Sum('text_files_count'),
			image_files=Sum('image_files_count'),
		)
		
		self.total_files = file_totals.get('total_files') or 0
		self.code_files_count = file_totals.get('code_files') or 0
		self.text_files_count = file_totals.get('text_files') or 0
		self.image_files_count = file_totals.get('image_files') or 0
		
		# Calculate lines of code per language from ProjectFile
		language_stats = (
			ProjectFile.objects
			.filter(
				project_id__in=project_ids,
				file_type='code',
				detected_language__isnull=False,
				line_count__isnull=False,
			)
			.values('detected_language__name')
			.annotate(
				lines_of_code=Sum('line_count'),
				file_count=Count('id'),
			)
			.order_by('-lines_of_code')
		)
		
		self.languages_stats = [
			{
				'language': stat['detected_language__name'],
				'lines_of_code': stat['lines_of_code'] or 0,
				'file_count': stat['file_count'] or 0,
			}
			for stat in language_stats
		]
		
		# Calculate total lines of code
		self.total_lines_of_code = sum(lang['lines_of_code'] for lang in self.languages_stats)
		
		# Aggregate frameworks
		framework_stats = (
			ProjectFramework.objects
			.filter(project_id__in=project_ids)
			.values('framework__name')
			.annotate(project_count=Count('project', distinct=True))
			.order_by('-project_count')
		)
		
		self.frameworks_stats = [
			{
				'framework': stat['framework__name'],
				'project_count': stat['project_count'] or 0,
			}
			for stat in framework_stats
		]
		
		# Calculate contribution stats
		contribution_stats = (
			ProjectContribution.objects
			.filter(project_id__in=project_ids)
			.aggregate(
				total_commits=Sum('commit_count'),
				unique_contributors=Count('contributor', distinct=True),
			)
		)
		
		self.total_commits = contribution_stats.get('total_commits') or 0
		self.total_contributors = contribution_stats.get('unique_contributors') or 0
		
		# Calculate date range from project first_commit_date and created_at
		date_stats = projects.aggregate(
			earliest_date=models.Min('first_commit_date'),
			latest_date=models.Max('created_at'),
		)
		
		self.date_range_start = date_stats.get('earliest_date')
		self.date_range_end = date_stats.get('latest_date')
		
		self.stats_updated_at = timezone.now()
		self.save()



class PortfolioProject(models.Model):
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
