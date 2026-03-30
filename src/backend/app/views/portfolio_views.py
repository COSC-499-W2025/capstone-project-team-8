"""
Portfolio API views for creating, managing, and showcasing user portfolios.

Endpoints:
- GET    /portfolio/           - List user's portfolios
- POST   /portfolio/generate   - Create new portfolio with optional AI summary
- GET    /portfolio/{slug}/    - Retrieve portfolio details
- POST   /portfolio/{id}/edit  - Update portfolio and optionally regenerate summary
- DELETE /portfolio/id/{id}/   - Delete portfolio

Project curation:
- POST   /portfolio/{id}/projects/add       - Add project to portfolio
- DELETE /portfolio/{id}/projects/{pid}     - Remove project from portfolio
- POST   /portfolio/{id}/projects/reorder   - Reorder projects in portfolio
"""

from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, F, Q
from django.db.models.functions import TruncDate, Cast
from django.db.models import DateTimeField
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import datetime, timedelta
from collections import defaultdict
import logging
import secrets
import string

from app.models import Portfolio, PortfolioProject, Project, Resume, ProjectFile, ProjectContribution
from app.serializers import (
    PortfolioSerializer,
    PortfolioGenerateSerializer,
    PortfolioEditSerializer,
    AddProjectSerializer,
    ReorderProjectsSerializer,
)

logger = logging.getLogger(__name__)


def generate_random_portfolio_slug(length=10):
    """Generate an opaque, URL-safe slug for public sharing."""
    alphabet = string.ascii_lowercase + string.digits
    token = ''.join(secrets.choice(alphabet) for _ in range(length))
    return f"pf-{token}"


def generate_unique_portfolio_slug(max_attempts=10):
    """Generate a globally unique slug with retry protection against rare collisions."""
    for _ in range(max_attempts):
        slug = generate_random_portfolio_slug()
        if not Portfolio.objects.filter(slug=slug).exists():
            return slug

    # Fallback: longer token if collisions keep occurring.
    while True:
        slug = generate_random_portfolio_slug(length=14)
        if not Portfolio.objects.filter(slug=slug).exists():
            return slug


def generate_portfolio_summary(portfolio, projects):
    """
    Generate AI summary for portfolio based on included projects.
    Returns (summary_text, success_bool).
    """
    try:
        from app.services.llm import LLMFactory
    except ImportError:
        logger.warning("LLM service not available for portfolio summary generation")
        return "", False
    
    if not projects:
        return "", True
    
    # Build context from projects (prefer project-level AI summaries when available)
    project_descriptions = []
    ai_summary_fragments = []
    for p in projects:
        desc = f"- {p.name}"
        if p.ai_summary:
            desc += f" | AI Summary: {p.ai_summary.strip()}"
            ai_summary_fragments.append(f"{p.name}: {p.ai_summary.strip()}")
        if p.description:
            desc += f": {p.description}"
        if p.classification_type and p.classification_type != 'unknown':
            desc += f" (Type: {p.classification_type})"
        if p.resume_bullet_points:
            bullets = "; ".join(p.resume_bullet_points[:3])
            desc += f" | Highlights: {bullets}"
        project_descriptions.append(desc)
    
    projects_text = "\n".join(project_descriptions)
    
    # Build prompt
    tone = portfolio.tone or 'professional'
    audience = portfolio.target_audience or 'general audience'
    
    prompt = f"""Generate a concise, compelling portfolio summary for a developer showcasing these projects:

Portfolio Title: {portfolio.title}
{f'Description: {portfolio.description}' if portfolio.description else ''}
Target Audience: {audience}
Tone: {tone}

Projects:
{projects_text}

Write a 2-3 paragraph summary that:
1. Highlights the developer's key skills and expertise based on the projects
2. Emphasizes notable achievements and technologies used
3. Is written in a {tone} tone appropriate for {audience}

Return ONLY the summary text, no headers or formatting."""

    system_message = """You are an expert career coach and technical writer who creates compelling portfolio summaries for software developers. Your summaries are concise, impactful, and tailored to the target audience. Focus on skills, achievements, and the value the developer brings."""

    try:
        summary = LLMFactory.get_provider().analyze(prompt, system_message=system_message)
        return summary.strip(), True
    except Exception as e:
        logger.error(f"Error generating portfolio summary: {e}")
        # Fallback: if project-level summaries exist, build a concise combined summary
        # so users still see meaningful content on the portfolio page.
        if ai_summary_fragments:
            fallback = " ".join(ai_summary_fragments[:3]).strip()
            return fallback, True
        return "", False


@method_decorator(csrf_exempt, name="dispatch")
class PortfolioListView(APIView):
    """List all portfolios for the authenticated user."""
    permission_classes = [IsAuthenticated]
    serializer_class = PortfolioSerializer

    def get(self, request):
        portfolios = Portfolio.objects.filter(user=request.user).prefetch_related('portfolio_projects__project')
        serializer = PortfolioSerializer(portfolios, many=True, context={'request': request})
        return JsonResponse({"portfolios": serializer.data})


@method_decorator(csrf_exempt, name="dispatch")
class PortfolioGenerateView(APIView):
    """
    Create a new portfolio with optional AI summary generation.
    POST /portfolio/generate
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PortfolioGenerateSerializer

    def post(self, request):
        serializer = PortfolioGenerateSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            # Format errors as readable message
            error_messages = []
            for field, errors in serializer.errors.items():
                if isinstance(errors, list):
                    error_messages.extend([str(err) for err in errors])
                else:
                    error_messages.append(str(errors))
            error_msg = '; '.join(error_messages) or 'Invalid portfolio data'
            return JsonResponse({"error": error_msg}, status=400)
        
        data = serializer.validated_data
        
        # Always generate pseudorandom share slug (input slug is ignored for immutability/privacy).
        slug = generate_unique_portfolio_slug()
        
        with transaction.atomic():
            # Create portfolio
            portfolio = Portfolio.objects.create(
                user=request.user,
                title=data['title'],
                slug=slug,
                description=data.get('description', ''),
                is_public=data.get('is_public', False),
                target_audience=data.get('target_audience', ''),
                tone=data.get('tone', 'professional'),
            )
            
            # Add projects
            project_ids = data.get('project_ids', [])
            projects = []
            for order, project_id in enumerate(project_ids):
                project = Project.objects.get(id=project_id, user=request.user)
                PortfolioProject.objects.create(
                    portfolio=portfolio,
                    project=project,
                    order=order
                )
                projects.append(project)
            
            # Generate AI summary if requested
            summary_generated = False
            if data.get('generate_summary', True) and projects:
                summary, success = generate_portfolio_summary(portfolio, projects)
                if success and summary:
                    portfolio.summary = summary
                    portfolio.summary_generated_at = timezone.now()
                    portfolio.save()
                    summary_generated = True
        
        response_serializer = PortfolioSerializer(portfolio, context={'request': request})
        return JsonResponse({
            "portfolio": response_serializer.data,
            "summary_generated": summary_generated
        }, status=201)


@method_decorator(csrf_exempt, name="dispatch")
class PortfolioDetailView(APIView):
    """
    Retrieve portfolio details.
    GET /portfolio/{slug}/
    Public portfolios can be accessed without authentication.
    """
    permission_classes = [AllowAny]
    serializer_class = PortfolioSerializer

    def get_portfolio(self, *, slug=None, pk=None, user=None):
        """Get portfolio, respecting visibility rules.
        Returns (portfolio, status) where status is 'ok', 'private', or 'not_found'.
        """
        if slug is None and pk is None:
            return None, 'not_found'

        try:
            query = {'slug': slug} if slug is not None else {'pk': pk}
            portfolio = Portfolio.objects.prefetch_related('portfolio_projects__project').get(**query)
            # Allow access if public or if user is owner
            if portfolio.is_public or (user and user.is_authenticated and portfolio.user == user):
                return portfolio, 'ok'
            return portfolio, 'private'
        except Portfolio.DoesNotExist:
            return None, 'not_found'

    def get(self, request, slug=None, pk=None):
        portfolio, status = self.get_portfolio(slug=slug, pk=pk, user=request.user)
        if status == 'not_found':
            return JsonResponse({"error": "Portfolio not found"}, status=404)
        if status == 'private':
            return JsonResponse({
                "error": "This portfolio is private",
                "is_private": True,
                "portfolio_title": portfolio.title,
                "owner": portfolio.user.username if portfolio.user else None,
            }, status=403)
        
        serializer = PortfolioSerializer(portfolio, context={'request': request})
        return JsonResponse(serializer.data)

    def delete(self, request, slug=None, pk=None):
        if pk is None:
            return JsonResponse({"error": "Delete is only available on ID routes"}, status=405)

        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)
        
        try:
            portfolio = Portfolio.objects.get(pk=pk, user=request.user)
        except Portfolio.DoesNotExist:
            return JsonResponse({"error": "Portfolio not found"}, status=404)
        
        portfolio_id = portfolio.id
        portfolio.delete()
        return JsonResponse({"ok": True, "deleted_id": portfolio_id})


@method_decorator(csrf_exempt, name="dispatch")
class PortfolioEditView(APIView):
    """
    Update portfolio and optionally regenerate AI summary.
    POST /portfolio/{id}/edit
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PortfolioEditSerializer

    def post(self, request, pk):
        try:
            portfolio = Portfolio.objects.prefetch_related('portfolio_projects__project').get(pk=pk, user=request.user)
        except Portfolio.DoesNotExist:
            return JsonResponse({"error": "Portfolio not found"}, status=404)

        if 'slug' in request.data:
            return JsonResponse({"error": "Portfolio slug is immutable after creation"}, status=400)
        
        serializer = PortfolioEditSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse({"error": serializer.errors}, status=400)
        
        data = serializer.validated_data
        
        # Update fields
        if 'title' in data:
            portfolio.title = data['title']
        if 'description' in data:
            portfolio.description = data['description']
        if 'is_public' in data:
            portfolio.is_public = data['is_public']
        if 'target_audience' in data:
            portfolio.target_audience = data['target_audience']
        if 'tone' in data:
            portfolio.tone = data['tone']
        
        # Regenerate summary if requested
        summary_regenerated = False
        if data.get('regenerate_summary', False):
            projects = [pp.project for pp in portfolio.portfolio_projects.select_related('project').all()]
            summary, success = generate_portfolio_summary(portfolio, projects)
            if success and summary:
                portfolio.summary = summary
                portfolio.summary_generated_at = timezone.now()
                summary_regenerated = True
        
        portfolio.save()
        
        response_serializer = PortfolioSerializer(portfolio, context={'request': request})
        return JsonResponse({
            "portfolio": response_serializer.data,
            "summary_regenerated": summary_regenerated
        })


@method_decorator(csrf_exempt, name="dispatch")
class PortfolioAddProjectView(APIView):
    """
    Add a project to portfolio.
    POST /portfolio/{id}/projects/add
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AddProjectSerializer

    def post(self, request, pk):
        try:
            portfolio = Portfolio.objects.get(pk=pk, user=request.user)
        except Portfolio.DoesNotExist:
            return JsonResponse({"error": "Portfolio not found"}, status=404)
        
        serializer = AddProjectSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse({"error": serializer.errors}, status=400)
        
        data = serializer.validated_data
        project_id = data['project_id']
        
        # Verify project belongs to user
        try:
            project = Project.objects.get(id=project_id, user=request.user)
        except Project.DoesNotExist:
            return JsonResponse({"error": "Project not found or does not belong to you"}, status=404)
        
        # Check if already in portfolio
        if PortfolioProject.objects.filter(portfolio=portfolio, project=project).exists():
            return JsonResponse({"error": "Project already in portfolio"}, status=400)
        
        # Determine order
        from django.db.models import Max
        max_order_result = portfolio.portfolio_projects.aggregate(
            max_order=Max('order')
        )['max_order']
        max_order = max_order_result if max_order_result is not None else -1
        order = data.get('order') if data.get('order') is not None else (max_order + 1)
        
        portfolio_project = PortfolioProject.objects.create(
            portfolio=portfolio,
            project=project,
            order=order,
            notes=data.get('notes', ''),
            featured=data.get('featured', False),
        )
        
        # Recalculate portfolio statistics
        portfolio.update_cached_stats()
        
        return JsonResponse({
            "ok": True,
            "portfolio_project_id": portfolio_project.id,
            "project_id": project.id,
            "order": order
        }, status=201)


@method_decorator(csrf_exempt, name="dispatch")
class PortfolioRemoveProjectView(APIView):
    """
    Remove a project from portfolio.
    DELETE /portfolio/{id}/projects/{project_id}
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AddProjectSerializer

    def delete(self, request, pk, project_id):
        try:
            portfolio = Portfolio.objects.get(pk=pk, user=request.user)
        except Portfolio.DoesNotExist:
            return JsonResponse({"error": "Portfolio not found"}, status=404)
        
        try:
            portfolio_project = PortfolioProject.objects.get(
                portfolio=portfolio, project_id=project_id
            )
        except PortfolioProject.DoesNotExist:
            return JsonResponse({"error": "Project not in portfolio"}, status=404)
        
        portfolio_project.delete()
        
        # Recalculate portfolio statistics
        portfolio.update_cached_stats()
        
        return JsonResponse({"ok": True, "removed_project_id": project_id})


@method_decorator(csrf_exempt, name="dispatch")
class PortfolioReorderProjectsView(APIView):
    """
    Reorder projects in portfolio.
    POST /portfolio/{id}/projects/reorder
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ReorderProjectsSerializer

    def post(self, request, pk):
        try:
            portfolio = Portfolio.objects.get(pk=pk, user=request.user)
        except Portfolio.DoesNotExist:
            return JsonResponse({"error": "Portfolio not found"}, status=404)
        
        serializer = ReorderProjectsSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse({"error": serializer.errors}, status=400)
        
        project_ids = serializer.validated_data['project_ids']
        
        # Verify all project_ids are in this portfolio
        existing_project_ids = set(
            portfolio.portfolio_projects.values_list('project_id', flat=True)
        )
        provided_ids = set(project_ids)
        
        if provided_ids != existing_project_ids:
            missing = existing_project_ids - provided_ids
            extra = provided_ids - existing_project_ids
            errors = []
            if missing:
                errors.append(f"Missing project IDs: {list(missing)}")
            if extra:
                errors.append(f"Unknown project IDs: {list(extra)}")
            return JsonResponse({"error": "; ".join(errors)}, status=400)
        
        # Update order
        with transaction.atomic():
            for order, project_id in enumerate(project_ids):
                PortfolioProject.objects.filter(
                    portfolio=portfolio, project_id=project_id
                ).update(order=order)
        
        return JsonResponse({"ok": True, "new_order": project_ids})


@method_decorator(csrf_exempt, name="dispatch")
class PortfolioStatsView(APIView):
    """
    Get portfolio statistics including lines of code per language.
    GET /portfolio/{slug}/stats/
    
    Statistics are cached and updated when projects are added/removed.
    On first access (lazy loading), stats are calculated and cached.
    Public portfolios can be accessed without authentication.
    """
    permission_classes = [AllowAny]

    def get(self, request, slug=None, pk=None):
        if slug is None and pk is None:
            return JsonResponse({"error": "Portfolio not found"}, status=404)

        try:
            query = {'slug': slug} if slug is not None else {'pk': pk}
            portfolio = Portfolio.objects.get(**query)
        except Portfolio.DoesNotExist:
            return JsonResponse({"error": "Portfolio not found"}, status=404)
        
        # Public portfolios: anyone can access
        # Private portfolios: require authentication (401), non-owners get 404
        if not portfolio.is_public:
            if not request.user.is_authenticated:
                return JsonResponse({"error": "Authentication required"}, status=401)
            if portfolio.user != request.user:
                return JsonResponse({"error": "Portfolio not found"}, status=404)
        
        # Lazy initialization: calculate stats if never computed
        if portfolio.stats_updated_at is None:
            portfolio.update_cached_stats()
            portfolio.refresh_from_db()
        
        return JsonResponse({
            "portfolio_id": portfolio.id,
            "total_projects": portfolio.total_projects,
            "total_files": portfolio.total_files,
            "code_files_count": portfolio.code_files_count,
            "text_files_count": portfolio.text_files_count,
            "image_files_count": portfolio.image_files_count,
            "total_lines_of_code": portfolio.total_lines_of_code,
            "total_commits": portfolio.total_commits,
            "total_contributors": portfolio.total_contributors,
            "languages": portfolio.languages_stats,
            "frameworks": portfolio.frameworks_stats,
            "date_range_start": portfolio.date_range_start.isoformat() if portfolio.date_range_start else None,
            "date_range_end": portfolio.date_range_end.isoformat() if portfolio.date_range_end else None,
            "stats_updated_at": portfolio.stats_updated_at.isoformat() if portfolio.stats_updated_at else None,
        })


@method_decorator(csrf_exempt, name="dispatch")
class PortfolioGenerateResumeView(APIView):
    """
    Generate a resume from portfolio data.
    POST /portfolio/{id}/generate-resume/
    
    Creates a new Resume object populated with:
    - User profile data (name, email, education)
    - Portfolio projects (ordered by PortfolioProject.order)
    - Skills extracted from portfolio languages/frameworks
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            portfolio = Portfolio.objects.prefetch_related(
                'portfolio_projects__project__languages',
                'portfolio_projects__project__frameworks'
            ).get(pk=pk, user=request.user)
        except Portfolio.DoesNotExist:
            return JsonResponse({"error": "Portfolio not found"}, status=404)
        
        user = request.user
        
        # Ensure portfolio stats are up-to-date
        if portfolio.stats_updated_at is None:
            portfolio.update_cached_stats()
            portfolio.refresh_from_db()
        
        # Build user profile info
        first_name = user.first_name or ''
        last_name = user.last_name or ''
        full_name = f"{first_name} {last_name}".strip() or user.username
        
        city = getattr(user, 'education_city', '') or getattr(user, 'city', '') or ''
        state = getattr(user, 'education_state', '') or getattr(user, 'state', '') or ''
        location = f"{city}, {state}" if city and state else city or state or ''
        
        # Build education from user profile
        education = []
        university = getattr(user, 'university', '')
        degree_major = getattr(user, 'degree_major', '')
        expected_graduation = getattr(user, 'expected_graduation', None)
        
        if university or degree_major:
            grad_str = ''
            if expected_graduation:
                grad_str = f"Graduating {expected_graduation.year}" if hasattr(expected_graduation, 'year') else f"Graduating {expected_graduation}"
            education.append({
                'id': 1,
                'title': university or 'University',
                'degree_type': '',
                'company': degree_major or '',
                'duration': grad_str,
                'content': '',
            })
        
        # Build projects from portfolio (ordered by PortfolioProject.order)
        resume_projects = []
        portfolio_projects = portfolio.portfolio_projects.select_related('project').order_by('order', '-added_at')
        
        for idx, pp in enumerate(portfolio_projects):
            project = pp.project
            
            # Get frameworks/technologies for the project
            frameworks = list(project.frameworks.values_list('name', flat=True)[:5])
            languages = list(project.languages.values_list('name', flat=True)[:3])
            tech_list = frameworks if frameworks else languages
            tech_str = ', '.join(tech_list) if tech_list else ''
            
            # Get date range for duration
            duration = ''
            if project.first_commit_date:
                start_date = project.first_commit_date.strftime('%b %Y')
                end_date = project.created_at.strftime('%b %Y') if project.created_at else 'Present'
                if start_date != end_date:
                    duration = f"{start_date} - {end_date}"
                else:
                    duration = start_date
            elif project.created_at:
                duration = project.created_at.strftime('%b %Y')
            
            # Use existing resume_bullet_points or generate from description
            bullet_points = project.resume_bullet_points or []
            if not bullet_points and project.description:
                bullet_points = [project.description[:200]]
            
            content = '\n'.join([f"• {bp}" for bp in bullet_points[:5]])
            
            resume_projects.append({
                'id': idx + 1,
                'title': project.name,
                'company': tech_str,
                'duration': duration,
                'content': content,
            })
        
        # Build skills from portfolio stats
        skills = []
        skill_id = 1
        
        # Add languages first
        for lang_stat in portfolio.languages_stats or []:
            skills.append({
                'id': skill_id,
                'title': lang_stat.get('language', ''),
            })
            skill_id += 1
        
        # Add frameworks
        for fw_stat in portfolio.frameworks_stats or []:
            skills.append({
                'id': skill_id,
                'title': fw_stat.get('framework', ''),
            })
            skill_id += 1
        
        # Build resume content
        resume_content = {
            'name': full_name,
            'email': user.email or '',
            'phone': getattr(user, 'phone', '') or '',
            'github_url': f"https://github.com/{user.github_username}" if getattr(user, 'github_username', '') else '',
            'portfolio_url': getattr(user, 'portfolio_url', '') or '',
            'linkedin_url': getattr(user, 'linkedin_url', '') or '',
            'location': location,
            'sections': {
                'summary': '',
                'education': education,
                'experience': [],  # User has no experience fields in model
                'projects': resume_projects,
                'skills': skills,
                'certifications': [],
            },
        }
        
        # Save the resume
        resume_name = f"{portfolio.title} Resume"
        resume = Resume.objects.create(
            user=user,
            name=resume_name,
            content=resume_content,
        )
        
        return JsonResponse({
            'resume_id': resume.id,
            'resume_name': resume.name,
            'content': resume_content,
            'portfolio_id': portfolio.id,
            'portfolio_title': portfolio.title,
        }, status=201)


@method_decorator(csrf_exempt, name="dispatch")
class PortfolioActivityHeatmapView(APIView):
    """
    Get activity heatmap data for all projects in a portfolio.
    GET /portfolio/{id}/activity-heatmap/
    
    Returns daily activity counts aggregated from:
    - File uploads (ProjectFile.created_at)
    - Project creation dates
    
    Response format:
    {
        "portfolio_id": int,
        "total_activity": int,
        "date_range": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD"},
        "activity_data": [
            {"date": "YYYY-MM-DD", "count": int, "projects": [{"id": int, "name": str, "count": int}]},
            ...
        ],
        "max_activity": int,
        "min_activity": int
    }
    """
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            portfolio = Portfolio.objects.get(pk=pk)
        except Portfolio.DoesNotExist:
            return JsonResponse({"error": "Portfolio not found"}, status=404)
        
        # Check permissions
        if not portfolio.is_public:
            if not request.user.is_authenticated:
                return JsonResponse({"error": "Authentication required"}, status=401)
            if portfolio.user != request.user:
                return JsonResponse({"error": "Portfolio not found"}, status=404)
        
        # Get all projects in the portfolio
        portfolio_projects = portfolio.portfolio_projects.select_related('project').prefetch_related('project__files')
        
        if not portfolio_projects.exists():
            return JsonResponse({
                "portfolio_id": portfolio.id,
                "total_activity": 0,
                "date_range": {"start": None, "end": None},
                "activity_data": [],
                "max_activity": 0,
                "min_activity": 0,
            })
        
        # Aggregate activity by date
        activity_by_date = defaultdict(lambda: {"count": 0, "projects": defaultdict(int)})
        
        all_dates = []
        
        # Collect file activity (ProjectFile.created_at)
        project_ids = [pp.project_id for pp in portfolio_projects]
        file_activity = ProjectFile.objects.filter(
            project_id__in=project_ids
        ).values('project_id', 'project__name').annotate(
            date=TruncDate('created_at')
        ).values('date', 'project_id', 'project__name').annotate(
            count=Count('id')
        )
        
        for entry in file_activity:
            date_str = entry['date'].isoformat() if entry['date'] else None
            if date_str:
                activity_by_date[date_str]["count"] += entry['count']
                activity_by_date[date_str]["projects"][entry['project__name']] += entry['count']
                all_dates.append(entry['date'])
        
        # Collect project creation activity (Project.created_at)
        project_activity = Project.objects.filter(
            id__in=project_ids
        ).values('id', 'name', 'created_at').annotate(
            date=TruncDate('created_at')
        ).values('date', 'id', 'name')
        
        for entry in project_activity:
            date_str = entry['date'].isoformat() if entry['date'] else None
            if date_str:
                activity_by_date[date_str]["count"] += 1
                activity_by_date[date_str]["projects"][entry['name']] += 1
                all_dates.append(entry['date'])
        
        # Determine date range
        if all_dates:
            min_date = min(all_dates)
            max_date = max(all_dates)
        else:
            min_date = None
            max_date = None
        
        # Fill in gaps with zero activity
        if min_date and max_date:
            current_date = min_date
            while current_date <= max_date:
                date_str = current_date.isoformat()
                if date_str not in activity_by_date:
                    activity_by_date[date_str] = {"count": 0, "projects": {}}
                current_date += timedelta(days=1)
        
        # Convert to list format
        activity_data = []
        total_activity = 0
        max_activity = 0
        min_activity = float('inf')
        
        for date_str in sorted(activity_by_date.keys()):
            entry = activity_by_date[date_str]
            count = entry["count"]
            
            # Build projects list
            projects_list = [
                {"name": name, "count": count}
                for name, count in sorted(entry["projects"].items(), key=lambda x: x[1], reverse=True)
            ]
            
            activity_data.append({
                "date": date_str,
                "count": count,
                "projects": projects_list,
            })
            
            total_activity += count
            max_activity = max(max_activity, count)
            if count > 0:
                min_activity = min(min_activity, count)
        
        if min_activity == float('inf'):
            min_activity = 0
        
        return JsonResponse({
            "portfolio_id": portfolio.id,
            "total_activity": total_activity,
            "date_range": {
                "start": min_date.isoformat() if min_date else None,
                "end": max_date.isoformat() if max_date else None,
            },
            "activity_data": activity_data,
            "max_activity": max_activity,
            "min_activity": min_activity,
        })
