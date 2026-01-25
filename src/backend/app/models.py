from django.db import models

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
    
    # Project thumbnail image
    thumbnail = models.ImageField(upload_to='project_thumbnails/', null=True, blank=True)
    
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

    def get_full_name(self):
