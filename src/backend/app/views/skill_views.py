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

from collections import Counter

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
                        "resume_skills": {
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
        description="Get aggregated skills (languages, frameworks, and resume skills) from authenticated user's projects. Skills are sorted by usage frequency (most used first).",
        tags=["Skills"],
    )
    def get(self, request):
        """
        Get aggregated skills from user's projects.
        
        Returns:
            - languages: List of programming languages with project counts
            - frameworks: List of frameworks with project counts
            - resume_skills: List of other skills (writing, art, etc.) with project counts
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

        # Aggregate resume_skills from the JSONField on each project
        # Count how many projects each skill appears in
        skill_counter = Counter()
        for skills_list in Project.objects.filter(user=user).values_list('resume_skills', flat=True):
            if skills_list:
                skill_counter.update(skills_list)

        resume_skills_list = [
            {'name': skill, 'project_count': count}
            for skill, count in skill_counter.most_common()
        ]

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
            'resume_skills': resume_skills_list,
            'total_projects': total_projects
        })

@method_decorator(csrf_exempt, name="dispatch")
class SkillsTimelineView(APIView):
    """
    GET /api/skills/timeline/
    
    Returns the chronological timeline of when skills first appeared.
    Optionally filter by portfolio using ?portfolio_id=123
    """
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        responses={
            200: OpenApiResponse(
                description="Chronological timeline of skills",
            ),
        },
        description="Get chronological timeline of when skills first appeared. Optionally takes ?portfolio_id=",
        tags=["Skills"],
    )
    def get(self, request):
        user = request.user
        portfolio_id = request.GET.get('portfolio_id')

        # Base project query
        projects = Project.objects.filter(user=user)
        if portfolio_id:
            projects = projects.filter(portfolios__id=portfolio_id)

        projects = projects.prefetch_related('languages', 'frameworks')
        
        skill_earliest_date = {}

        for p in projects:
            # Use first_commit_date, fallback to created_at
            p_date = p.first_commit_date or p.created_at
            if not p_date:
                continue
                
            for lang in p.languages.all():
                key = f"lang_{lang.name}"
                if key not in skill_earliest_date or p_date < skill_earliest_date[key]['date_obj']:
                    skill_earliest_date[key] = {
                        "skill": lang.name, 
                        "date_obj": p_date, 
                        "type": "language"
                    }
                    
            for fw in p.frameworks.all():
                key = f"fw_{fw.name}"
                if key not in skill_earliest_date or p_date < skill_earliest_date[key]['date_obj']:
                    skill_earliest_date[key] = {
                        "skill": fw.name, 
                        "date_obj": p_date, 
                        "type": "framework"
                    }

        # Convert to list and sort by date
        timeline = list(skill_earliest_date.values())
        timeline.sort(key=lambda x: x['date_obj'])

        # Format dates for JSON
        for item in timeline:
            item['date'] = item['date_obj'].isoformat()
            del item['date_obj']

        return JsonResponse({"timeline": timeline})
