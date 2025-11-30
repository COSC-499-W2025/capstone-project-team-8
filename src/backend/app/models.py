from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import URLValidator
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom manager for User model"""
    
    def create_user(self, username, email, password=None, **extra_fields):
        """
        Create and return a regular user with username, email and password.
        This method is called by auth.py: User.objects.create_user()
        """
        if not username:
            raise ValueError('Username is required')
        if not email:
            raise ValueError('Email is required')
        
        # Normalize email (lowercase the domain part)
        email = self.normalize_email(email)
        
        # Create user instance
        user = self.model(username=username, email=email, **extra_fields)
        
        # Hash the password (never store plain text!)
        user.set_password(password)
        
        # Save to database
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        """
        Create and return a superuser for Django admin.
        Used by: python manage.py createsuperuser
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model for the capstone project.
    Uses username for authentication (to match existing auth.py implementation).
    Extended with social links and profile information.
    """
    # Core fields required by auth.py
    username = models.CharField(max_length=150, unique=True, db_index=True)
    email = models.EmailField(max_length=255, unique=True)
    
    # Profile fields
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    
    # Social media links
    github_username = models.CharField(max_length=100, blank=True, db_index=True)
    github_email = models.EmailField(max_length=255, blank=True)
    linkedin_url = models.URLField(max_length=255, blank=True)
    portfolio_url = models.URLField(max_length=255, blank=True)
    twitter_username = models.CharField(max_length=100, blank=True)
    
    # Profile image
    profile_image_url = models.URLField(max_length=500, blank=True)
    
    # Permission fields (required for admin and authentication)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # Timestamps
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    profile_updated_at = models.DateTimeField(auto_now=True)
    
    # Attach the custom manager
    objects = UserManager()
    
    # Tell Django to use 'username' for authentication
    # This matches auth.py: authenticate(username=username, password=password)
    USERNAME_FIELD = 'username'
    
    # Required fields when creating superuser
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        """String representation - used in admin and logging"""
        return self.username
    
    def get_full_name(self):
        """Return full name if available, otherwise username"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def get_short_name(self):
        """Return first name if available, otherwise username"""
        return self.first_name if self.first_name else self.username
    
    @property
    def display_name(self):
        """Best name to display for this user"""
        return self.get_full_name()


# Programming Languages and Frameworks
class ProgrammingLanguage(models.Model):
    """
    Model to store programming languages detected in projects.
    Normalized to avoid duplicates and enable aggregation.
    """
    name = models.CharField(max_length=50, unique=True)
    category = models.CharField(
        max_length=20,
        choices=[
            ('general', 'General Purpose'),
            ('web', 'Web Development'),
            ('data', 'Data Science'),
            ('mobile', 'Mobile'),
            ('system', 'System Programming'),
            ('other', 'Other')
        ],
        default='general'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'programming_languages'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Framework(models.Model):
    """
    Model to store frameworks and libraries detected in projects.
    """
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(
        max_length=30,
        choices=[
            ('web_frontend', 'Web Frontend'),
            ('web_backend', 'Web Backend'),
            ('mobile', 'Mobile'),
            ('data_science', 'Data Science'),
            ('testing', 'Testing'),
            ('ui_library', 'UI Library'),
            ('build_tool', 'Build Tool'),
            ('database', 'Database/ORM'),
            ('other', 'Other')
        ],
        default='other'
    )
    language = models.ForeignKey(
        ProgrammingLanguage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='frameworks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'frameworks'
        ordering = ['name']
    
    def __str__(self):
        return self.name


# Project Models
class Project(models.Model):
    """
    Model to represent a project uploaded by a user.
    Each project corresponds to a single git repository or folder structure.
    """
    # Core identification
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Project classification from AI analysis
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
    
    # Project metadata
    project_root_path = models.CharField(max_length=500, blank=True)  # Relative path in upload
    project_tag = models.IntegerField(null=True, blank=True)  # Original numeric tag from analysis
    
    # File statistics
    total_files = models.IntegerField(default=0)
    code_files_count = models.IntegerField(default=0)
    text_files_count = models.IntegerField(default=0)
    image_files_count = models.IntegerField(default=0)
    
    # Git information
    git_repository = models.BooleanField(default=False)
    first_commit_date = models.DateTimeField(null=True, blank=True)
    
    # Upload metadata
    upload_source = models.CharField(max_length=50, default='zip_file')
    original_zip_name = models.CharField(max_length=255, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
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

    # AI-generated summary (stored once during upload)
    ai_summary = models.TextField(blank=True)
    ai_summary_generated_at = models.DateTimeField(null=True, blank=True)
    llm_consent = models.BooleanField(default=False)  # Track if user consented to LLM
    
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


class ProjectLanguage(models.Model):
    """
    Through model to track which languages are used in which projects.
    Includes additional metadata like file count for that language.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    language = models.ForeignKey(ProgrammingLanguage, on_delete=models.CASCADE)
    file_count = models.IntegerField(default=0)
    is_primary = models.BooleanField(default=False)  # Most used language in project
    
    class Meta:
        db_table = 'project_languages'
        unique_together = ['project', 'language']


class ProjectFramework(models.Model):
    """
    Through model to track which frameworks are used in which projects.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE)
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


# File Analysis Models
class ProjectFile(models.Model):
    """
    Model to store individual file analysis results.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    
    # File identification
    file_path = models.CharField(max_length=1000)  # Relative path within project
    filename = models.CharField(max_length=255)
    file_extension = models.CharField(max_length=20, blank=True)
    
    # File classification
    file_type = models.CharField(
        max_length=20,
        choices=[
            ('code', 'Code'),
            ('content', 'Content/Text'),
            ('image', 'Image'),
            ('unknown', 'Unknown')
        ]
    )
    
    # File metrics (vary by type)
    file_size_bytes = models.BigIntegerField(null=True, blank=True)
    line_count = models.IntegerField(null=True, blank=True)  # For code files
    character_count = models.IntegerField(null=True, blank=True)  # For text files
    
    # Content preview (for small text files)
    content_preview = models.TextField(blank=True, max_length=10000)
    is_content_truncated = models.BooleanField(default=False)
    
    # Language detection (for code files)
    detected_language = models.ForeignKey(
        ProgrammingLanguage,
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


# Contributor Models
class Contributor(models.Model):
    """
    Model to represent a git contributor.
    This is separate from User to handle external contributors.
    """
    # Identity
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, blank=True)
    
    # Link to registered user (if they have an account)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='contributor_profiles'
    )
    
    # Auto-generated fields for matching
    email_domain = models.CharField(max_length=255, blank=True)
    normalized_name = models.CharField(max_length=255, blank=True)  # Lowercase, no spaces
    
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
        # Auto-populate computed fields
        if self.email:
            self.email_domain = self.email.split('@')[-1] if '@' in self.email else ''
        self.normalized_name = self.name.lower().replace(' ', '')
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({self.email})" if self.email else self.name


class ProjectContribution(models.Model):
    """
    Model to track contributor statistics for each project.
    Links contributors to projects with their contribution metrics.
    """
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='contributions')
    contributor = models.ForeignKey(Contributor, on_delete=models.CASCADE, related_name='contributions')
    
    # Git statistics
    commit_count = models.IntegerField(default=0)
    lines_added = models.IntegerField(default=0)
    lines_deleted = models.IntegerField(default=0)
    percent_of_commits = models.FloatField(default=0.0)
    
    # Derived metrics
    net_lines = models.IntegerField(default=0)  # lines_added - lines_deleted
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'project_contributions'
        unique_together = ['project', 'contributor']
        indexes = [
            models.Index(fields=['project', '-commit_count']),
            models.Index(fields=['contributor', '-commit_count']),
        ]
    
    def save(self, *args, **kwargs):
        # Auto-calculate derived metrics
        self.net_lines = self.lines_added - self.lines_deleted
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.contributor.name} -> {self.project.name} ({self.commit_count} commits)"