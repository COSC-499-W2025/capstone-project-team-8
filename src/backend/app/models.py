

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
