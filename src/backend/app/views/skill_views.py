"""
Skills API Views

Provides endpoints for aggregating and retrieving skills (languages and frameworks)
from a user's projects.
"""
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Count
from drf_spectacular.utils import extend_schema, OpenApiResponse

from app.models import Project, ProgrammingLanguage, Framework
from app.serializers import ErrorResponseSerializer


@method_decorator(csrf_exempt, name="dispatch")
class SkillsView(APIView):
    """
    GET /api/skills/
    
    Aggregate and return all skills (programming languages and frameworks)
    from the authenticated user's projects, sorted by usage frequency.
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        responses={
            200: OpenApiResponse(
                description="Aggregated skills from user's projects",
                response={
                    "type": "object",
                    "properties": {
                        "languages": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "project_count": {"type": "integer"}
                                }
                            }
                        },
                        "frameworks": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "project_count": {"type": "integer"}
                                }
                            }
                        },
                        "total_projects": {"type": "integer"}
                    }
                }
            ),
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
        description="Get aggregated skills (languages and frameworks) from authenticated user's projects. Skills are sorted by usage frequency (most used first).",
        tags=["Skills"],
    )
    def get(self, request):
        """
        Get aggregated skills from user's projects.
        
        Returns:
            - languages: List of programming languages with project counts
            - frameworks: List of frameworks with project counts
            - total_projects: Total number of user's projects
        """
        user = request.user
        
        # Aggregate languages from user's projects
        # Uses the ProjectLanguage through model to count distinct projects
        languages = ProgrammingLanguage.objects.filter(
            projects__user=user
        ).annotate(
            project_count=Count('projects', distinct=True)
        ).order_by('-project_count', 'name')
        
        # Aggregate frameworks from user's projects
        # Uses the ProjectFramework through model to count distinct projects
        frameworks = Framework.objects.filter(
            projects__user=user
        ).annotate(
            project_count=Count('projects', distinct=True)
        ).order_by('-project_count', 'name')
        
        # Get total project count for context
        total_projects = Project.objects.filter(user=user).count()
        
        return JsonResponse({
            'languages': [
                {
                    'name': lang.name,
                    'project_count': lang.project_count
                }
                for lang in languages
            ],
            'frameworks': [
                {
                    'name': fw.name,
                    'project_count': fw.project_count
                }
                for fw in frameworks
            ],
            'total_projects': total_projects
        })
