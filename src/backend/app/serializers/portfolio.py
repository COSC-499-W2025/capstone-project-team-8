"""Portfolio serializers for creating, managing, and organizing portfolios."""

from rest_framework import serializers
from django.utils.text import slugify

from app.models import Portfolio, PortfolioProject, Project


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
        required=True,
        help_text="Ordered list of project IDs"
    )
