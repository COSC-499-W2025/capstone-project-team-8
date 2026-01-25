# This is where we define our serializers for converting complex data types, 
# such as querysets and model instances, 
# into native Python datatypes that can then be easily rendered 
# into JSON, XML or other content types.

from rest_framework import serializers
from django.utils.text import slugify
from .models import Portfolio, PortfolioProject, Project


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, help_text="Unique username for the account")
    email = serializers.EmailField(required=True, help_text="User's email address")
    password = serializers.CharField(required=True, write_only=True, help_text="Password for the account")
    confirm_password = serializers.CharField(required=True, write_only=True, help_text="Password confirmation")
    github_username = serializers.CharField(required=False, allow_blank=True, help_text="Optional GitHub username")
    github_email = serializers.EmailField(required=False, allow_blank=True, help_text="Optional GitHub email")


class SignupResponseSerializer(serializers.Serializer):
    access = serializers.CharField(help_text="JWT access token")
    refresh = serializers.CharField(help_text="JWT refresh token")
    username = serializers.CharField(help_text="Username of the created account")
    github_username = serializers.CharField(help_text="GitHub username if provided")
    github_email = serializers.EmailField(help_text="GitHub email if provided")


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, help_text="Username")
    password = serializers.CharField(required=True, write_only=True, help_text="Password")


class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField(help_text="JWT access token")
    refresh = serializers.CharField(help_text="JWT refresh token")
    username = serializers.CharField(help_text="Authenticated username")


class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField(help_text="Error message describing what went wrong")


# User Serializers
class UserProfileSerializer(serializers.Serializer):
    username = serializers.CharField(help_text="Username")
    first_name = serializers.CharField(help_text="First name", allow_blank=True)
    last_name = serializers.CharField(help_text="Last name", allow_blank=True)
    email = serializers.EmailField(help_text="Email address")
    bio = serializers.CharField(help_text="User biography", allow_blank=True)
    github_username = serializers.CharField(help_text="GitHub username", allow_blank=True)
    linkedin_url = serializers.URLField(help_text="LinkedIn profile URL", allow_blank=True, required=False)
    portfolio_url = serializers.URLField(help_text="Portfolio website URL", allow_blank=True, required=False)
    twitter_username = serializers.CharField(help_text="Twitter username", allow_blank=True)
    profile_image_url = serializers.URLField(help_text="Profile image URL", allow_blank=True, required=False)
    university = serializers.CharField(help_text="University name", allow_blank=True)
    degree_major = serializers.CharField(help_text="Degree and major", allow_blank=True)
    education_city = serializers.CharField(help_text="Education city", allow_blank=True)
    education_state = serializers.CharField(help_text="Education state/province", allow_blank=True)
    expected_graduation = serializers.DateField(help_text="Expected graduation date", allow_null=True, required=False)
    date_joined = serializers.DateTimeField(help_text="Account creation date", required=False)


class UserUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    github_username = serializers.CharField(required=False, allow_blank=True)
    linkedin_url = serializers.URLField(required=False, allow_blank=True)
    portfolio_url = serializers.URLField(required=False, allow_blank=True)
    twitter_username = serializers.CharField(required=False, allow_blank=True)
    university = serializers.CharField(required=False, allow_blank=True)
    degree_major = serializers.CharField(required=False, allow_blank=True)
    education_city = serializers.CharField(required=False, allow_blank=True)
    education_state = serializers.CharField(required=False, allow_blank=True)
    expected_graduation = serializers.DateField(required=False, allow_null=True)


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True, write_only=True, help_text="Current password")
    new_password = serializers.CharField(required=True, write_only=True, help_text="New password")
    confirm_password = serializers.CharField(required=True, write_only=True, help_text="Confirm new password")


class PublicUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    first_name = serializers.CharField(allow_blank=True)
    last_name = serializers.CharField(allow_blank=True)
    bio = serializers.CharField(allow_blank=True)
    github_username = serializers.CharField(allow_blank=True)
    linkedin_url = serializers.URLField(allow_blank=True, required=False)
    portfolio_url = serializers.URLField(allow_blank=True, required=False)
    twitter_username = serializers.CharField(allow_blank=True)
    profile_image_url = serializers.URLField(allow_blank=True, required=False)
    university = serializers.CharField(allow_blank=True)
    degree_major = serializers.CharField(allow_blank=True)
    date_joined = serializers.DateTimeField(required=False)


# Project Serializers
class ProjectSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    classification = serializers.CharField()
    languages = serializers.ListField(child=serializers.CharField())
    frameworks = serializers.ListField(child=serializers.CharField())
    created_at = serializers.DateTimeField(read_only=True)
    last_updated = serializers.DateTimeField(read_only=True)
    thumbnail_url = serializers.URLField(allow_blank=True, required=False)


class ProjectDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    classification = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)
    last_updated = serializers.DateTimeField(read_only=True)
    thumbnail_url = serializers.URLField(allow_blank=True, required=False)
    contributors = serializers.ListField()
    languages = serializers.ListField()
    frameworks = serializers.ListField()
    files = serializers.ListField()


class ProjectUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    classification = serializers.CharField(required=False)


class ProjectStatsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    by_classification = serializers.DictField()


# Resume Serializers  
class ResumeTemplateSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()


class ResumeSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    template_id = serializers.CharField()
    content = serializers.DictField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class ResumeGenerateRequestSerializer(serializers.Serializer):
    template_id = serializers.CharField(required=True, help_text="Template ID to use")
    project_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="Optional list of project IDs to include"
    )


# Upload Serializers
class UploadFolderSerializer(serializers.Serializer):
    file = serializers.FileField(required=True, help_text="ZIP file containing project folders")
    github_username = serializers.CharField(required=False, allow_blank=True, help_text="GitHub username for the projects")
    consent_scan = serializers.BooleanField(required=False, default=False, help_text="Consent to scan and analyze project files")
    consent_send_llm = serializers.BooleanField(required=False, default=False, help_text="Consent to send data to LLM for AI analysis")


# Portfolio Serializers
class PortfolioProjectSerializer(serializers.ModelSerializer):
    """Serializer for PortfolioProject through model with nested project info."""
    project_id = serializers.IntegerField(source='project.id', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    project_description = serializers.CharField(source='project.description', read_only=True)
    classification_type = serializers.CharField(source='project.classification_type', read_only=True)
    
    class Meta:
        model = PortfolioProject
        fields = [
            'id', 'project_id', 'project_name', 'project_description',
            'classification_type', 'order', 'notes', 'featured', 'added_at'
        ]
        read_only_fields = ['id', 'added_at']


class PortfolioSerializer(serializers.ModelSerializer):
    """Serializer for Portfolio with nested projects."""
    projects = PortfolioProjectSerializer(source='portfolio_projects', many=True, read_only=True)
    project_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of project IDs to add to portfolio"
    )
    user_username = serializers.CharField(source='user.username', read_only=True)
    project_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Portfolio
        fields = [
            'id', 'user_username', 'title', 'slug', 'description', 'summary',
            'summary_generated_at', 'is_public', 'target_audience', 'tone',
            'created_at', 'updated_at', 'projects', 'project_ids', 'project_count'
        ]
        read_only_fields = ['id', 'summary', 'summary_generated_at', 'created_at', 'updated_at']
    
    def get_project_count(self, obj):
        return obj.portfolio_projects.count()
    
    def validate_slug(self, value):
        """Ensure slug is URL-safe and unique."""
        slug = slugify(value)
        if not slug:
            raise serializers.ValidationError("Slug cannot be empty after sanitization.")
        
        # Check uniqueness (exclude current instance on update)
        qs = Portfolio.objects.filter(slug=slug)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A portfolio with this slug already exists.")
        return slug
    
    def validate_project_ids(self, value):
        """Validate that all project IDs belong to the requesting user."""
        if not value:
            return value
        
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("Authentication required.")
        
        user_project_ids = set(
            Project.objects.filter(user=request.user, id__in=value).values_list('id', flat=True)
        )
        invalid_ids = set(value) - user_project_ids
        if invalid_ids:
            raise serializers.ValidationError(
                f"Projects with IDs {list(invalid_ids)} not found or do not belong to you."
            )
        return value
    
    def create(self, validated_data):
        project_ids = validated_data.pop('project_ids', [])
        portfolio = Portfolio.objects.create(**validated_data)
        
        # Add projects with order
        for order, project_id in enumerate(project_ids):
            PortfolioProject.objects.create(
                portfolio=portfolio,
                project_id=project_id,
                order=order
            )
        return portfolio
    
    def update(self, instance, validated_data):
        # project_ids handling is done separately via dedicated endpoints
        validated_data.pop('project_ids', None)
        return super().update(instance, validated_data)


class PortfolioGenerateSerializer(serializers.Serializer):
    """Serializer for generating a new portfolio with AI summary."""
    title = serializers.CharField(max_length=255)
    slug = serializers.SlugField(max_length=100, required=False)
    description = serializers.CharField(required=False, allow_blank=True, default='')
    project_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list
    )
    is_public = serializers.BooleanField(default=False)
    target_audience = serializers.CharField(max_length=100, required=False, default='')
    tone = serializers.ChoiceField(
        choices=['professional', 'casual', 'technical', 'creative'],
        default='professional'
    )
    generate_summary = serializers.BooleanField(default=True)
    
    def validate_slug(self, value):
        # Just slugify; uniqueness is handled by the view with auto-increment
        return slugify(value) if value else None
    
    def validate_project_ids(self, value):
        if not value:
            return value
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("Authentication required.")
        
        user_project_ids = set(
            Project.objects.filter(user=request.user, id__in=value).values_list('id', flat=True)
        )
        invalid_ids = set(value) - user_project_ids
        if invalid_ids:
            raise serializers.ValidationError(
                f"Projects with IDs {list(invalid_ids)} not found or do not belong to you."
            )
        return value


class PortfolioEditSerializer(serializers.Serializer):
    """Serializer for editing portfolio and optionally regenerating summary."""
    title = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    is_public = serializers.BooleanField(required=False)
    target_audience = serializers.CharField(max_length=100, required=False)
    tone = serializers.ChoiceField(
        choices=['professional', 'casual', 'technical', 'creative'],
        required=False
    )
    regenerate_summary = serializers.BooleanField(default=False)


class AddProjectSerializer(serializers.Serializer):
    """Serializer for adding a project to portfolio."""
    project_id = serializers.IntegerField()
    notes = serializers.CharField(required=False, allow_blank=True, default='')
    featured = serializers.BooleanField(default=False)
    order = serializers.IntegerField(required=False, default=None)


class ReorderProjectsSerializer(serializers.Serializer):
    """Serializer for reordering projects in portfolio."""
    project_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="Ordered list of project IDs"
    )


class ReorderProjectsSerializer(serializers.Serializer):
    project_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        help_text="Ordered list of project IDs"
    )