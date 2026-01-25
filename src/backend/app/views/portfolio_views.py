"""
Portfolio API views for creating, managing, and showcasing user portfolios.

Endpoints:
- GET    /portfolio/           - List user's portfolios
- POST   /portfolio/generate   - Create new portfolio with optional AI summary
- GET    /portfolio/{id}/      - Retrieve portfolio details
- POST   /portfolio/{id}/edit  - Update portfolio and optionally regenerate summary
- DELETE /portfolio/{id}/      - Delete portfolio

Project curation:
- POST   /portfolio/{id}/projects/add       - Add project to portfolio
- DELETE /portfolio/{id}/projects/{pid}     - Remove project from portfolio
- POST   /portfolio/{id}/projects/reorder   - Reorder projects in portfolio
"""

from django.http import JsonResponse
from django.utils import timezone
from django.utils.text import slugify
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging

from app.models import Portfolio, PortfolioProject, Project
from app.serializers import (
    PortfolioSerializer,
    PortfolioGenerateSerializer,
    PortfolioEditSerializer,
    AddProjectSerializer,
    ReorderProjectsSerializer,
)

logger = logging.getLogger(__name__)


def generate_portfolio_summary(portfolio, projects):
    """
    Generate AI summary for portfolio based on included projects.
    Returns (summary_text, success_bool).
    """
    try:
        from app.services.llm import ai_analyze
    except ImportError:
        logger.warning("LLM service not available for portfolio summary generation")
        return "", False
    
    if not projects:
        return "", True
    
    # Build context from projects
    project_descriptions = []
    for p in projects:
        desc = f"- {p.name}"
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
        summary = ai_analyze(prompt, system_message=system_message)
        return summary.strip(), True
    except Exception as e:
        logger.error(f"Error generating portfolio summary: {e}")
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
            return JsonResponse({"error": serializer.errors}, status=400)
        
        data = serializer.validated_data
        
        # Auto-generate slug if not provided
        slug = data.get('slug') or slugify(data['title'])
        
        # Ensure unique slug
        base_slug = slug
        counter = 1
        while Portfolio.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
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
    GET /portfolio/{id}/
    Public portfolios can be accessed without authentication.
    """
    permission_classes = [AllowAny]
    serializer_class = PortfolioSerializer

    def get_portfolio(self, pk, user=None):
        """Get portfolio, respecting visibility rules."""
        try:
            portfolio = Portfolio.objects.prefetch_related('portfolio_projects__project').get(pk=pk)
            # Allow access if public or if user is owner
            if portfolio.is_public or (user and user.is_authenticated and portfolio.user == user):
                return portfolio
            return None
        except Portfolio.DoesNotExist:
            return None

    def get(self, request, pk):
        portfolio = self.get_portfolio(pk, request.user)
        if not portfolio:
            return JsonResponse({"error": "Portfolio not found"}, status=404)
        
        serializer = PortfolioSerializer(portfolio, context={'request': request})
        return JsonResponse(serializer.data)

    def delete(self, request, pk):
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
