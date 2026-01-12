"""
Portfolio Views

Provides endpoints for managing portfolios and aggregating project data.
Returns comprehensive summaries similar to upload-folder response format.
"""

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Sum
from typing import Dict, Any
import logging

from app.models import Portfolio, PortfolioProject, Project

logger = logging.getLogger(__name__)


def aggregate_portfolio_data(portfolio: Portfolio) -> Dict[str, Any]:
    """
    Aggregate all data from portfolio projects, similar to upload-folder response.
    
    Returns structure matching upload-folder format with:
    - projects: list of project summaries
    - overall: aggregated classification/stats
    - skill_analysis: aggregated languages/frameworks
    - git_contributions: aggregated contributor stats
    """
    portfolio_projects = PortfolioProject.objects.filter(
        portfolio=portfolio
    ).select_related('project').prefetch_related(
        'project__projectlanguage_set__language',
        'project__projectframework_set__framework',
        'project__files',
        'project__contributions__contributor'
    ).order_by('display_order', '-added_at')
    
    # Aggregate data structures
    all_projects = []
    all_languages = {}  # {name: count}
    all_frameworks = {}  # {name: count}
    all_contributors = {}  # {name: {commits, lines_added, lines_deleted, email}}
    
    total_code_files = 0
    total_content_files = 0
    total_image_files = 0
    total_files = 0
    
    classification_counts = {}  # {type: count}
    
    for pp in portfolio_projects:
        project = pp.project
        
        # Build project entry similar to upload-folder format
        project_entry = {
            'portfolio_project_id': pp.id,
            'id': project.project_tag or project.id,
            'project_id': project.id,
            'name': pp.get_display_title(),
            'original_name': project.name,
            'root': project.project_root_path or '.',
            'description': pp.custom_description or project.description,
            'classification': {
                'type': project.classification_type,
                'confidence': project.classification_confidence
            },
            'highlight': pp.highlight,
            'include_in_resume': pp.include_in_resume,
            'display_order': pp.display_order,
            'git_repository': project.git_repository,
            'created_at': int(project.created_at.timestamp()) if project.created_at else None,
            'updated_at': int(project.updated_at.timestamp()) if project.updated_at else None,
        }
        
        # Get files breakdown
        files_by_type = {
            'code': [],
            'content': [],
            'image': [],
            'unknown': []
        }
        
        code_count = 0
        content_count = 0
        image_count = 0
        
        for pf in project.files.all():
            file_entry = {'path': pf.filename}
            if pf.file_type == 'code':
                if pf.line_count:
                    file_entry['lines'] = pf.line_count
                files_by_type['code'].append(file_entry)
                code_count += 1
            elif pf.file_type == 'content':
                if pf.character_count:
                    file_entry['length'] = pf.character_count
                files_by_type['content'].append(file_entry)
                content_count += 1
            elif pf.file_type == 'image':
                files_by_type['image'].append(file_entry)
                image_count += 1
            else:
                files_by_type['unknown'].append(pf.filename)
        
        project_entry['files'] = files_by_type
        total_files += project.total_files
        total_code_files += code_count
        total_content_files += content_count
        total_image_files += image_count
        
        # Get languages
        languages = []
        for pl in project.projectlanguage_set.all():
            lang_name = pl.language.name
            languages.append(lang_name)
            all_languages[lang_name] = all_languages.get(lang_name, 0) + 1
        project_entry['languages'] = languages
        
        # Get frameworks
        frameworks = []
        for pf in project.projectframework_set.all():
            fw_name = pf.framework.name
            frameworks.append(fw_name)
            all_frameworks[fw_name] = all_frameworks.get(fw_name, 0) + 1
        project_entry['frameworks'] = frameworks
        
        # Get contributors
        contributors = []
        for pc in project.contributions.all():
            contributor_data = {
                'name': pc.contributor.name,
                'email': pc.contributor.email or '',
                'commits': pc.commit_count,
                'lines_added': pc.lines_added,
                'lines_deleted': pc.lines_deleted,
            }
            contributors.append(contributor_data)
            
            # Aggregate to portfolio level
            contrib_key = pc.contributor.name
            if contrib_key not in all_contributors:
                all_contributors[contrib_key] = {
                    'name': pc.contributor.name,
                    'email': pc.contributor.email or '',
                    'commits': 0,
                    'lines_added': 0,
                    'lines_deleted': 0
                }
            all_contributors[contrib_key]['commits'] += pc.commit_count
            all_contributors[contrib_key]['lines_added'] += pc.lines_added
            all_contributors[contrib_key]['lines_deleted'] += pc.lines_deleted
        
        project_entry['contributors'] = contributors
        
        # Get bullet points
        project_entry['bullet_points'] = pp.get_bullet_points()
        
        # Track classifications
        classification_counts[project.classification_type] = \
            classification_counts.get(project.classification_type, 0) + 1
        
        all_projects.append(project_entry)
    
    # Determine overall classification
    if classification_counts:
        overall_classification = max(classification_counts.items(), key=lambda x: x[1])[0]
        if len(classification_counts) > 1:
            # Multiple types - check if should use mixed
            types = sorted([k for k in classification_counts.keys() if k != 'unknown'])[:2]
            if len(types) >= 2:
                overall_classification = f"mixed:{'+'.join(types)}"
    else:
        overall_classification = 'unknown'
    
    # Build response similar to upload-folder
    return {
        'portfolio_id': portfolio.id,
        'portfolio_name': portfolio.name,
        'portfolio_description': portfolio.description,
        'portfolio_slug': portfolio.slug,
        'portfolio_cover_image': portfolio.cover_image_url or None,
        'is_public': portfolio.is_public,
        'display_order': portfolio.display_order,
        'created_at': int(portfolio.created_at.timestamp()),
        'updated_at': int(portfolio.updated_at.timestamp()),
        
        'source': 'portfolio',
        'projects': all_projects,
        
        'overall': {
            'classification': overall_classification,
            'total_projects': len(all_projects),
            'total_files': total_files,
            'code_files': total_code_files,
            'content_files': total_content_files,
            'image_files': total_image_files,
        },
        
        'skill_analysis': {
            'languages': sorted([
                {'name': name, 'project_count': count}
                for name, count in all_languages.items()
            ], key=lambda x: x['project_count'], reverse=True),
            'frameworks': sorted([
                {'name': name, 'project_count': count}
                for name, count in all_frameworks.items()
            ], key=lambda x: x['project_count'], reverse=True),
        },
        
        'git_contributions': {
            'contributors': list(all_contributors.values()),
            'total_commits': sum(c['commits'] for c in all_contributors.values()),
            'total_lines_added': sum(c['lines_added'] for c in all_contributors.values()),
            'total_lines_deleted': sum(c['lines_deleted'] for c in all_contributors.values()),
        }
    }


@method_decorator(csrf_exempt, name="dispatch")
class PortfolioListView(APIView):
    """List all portfolios for authenticated user or create new portfolio."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """List all user's portfolios (summary only)."""
        portfolios = Portfolio.objects.filter(user=request.user).prefetch_related('portfolio_projects')
        
        result = []
        for portfolio in portfolios:
            result.append({
                'id': portfolio.id,
                'name': portfolio.name,
                'description': portfolio.description,
                'cover_image_url': portfolio.cover_image_url or None,
                'is_public': portfolio.is_public,
                'slug': portfolio.slug,
                'display_order': portfolio.display_order,
                'project_count': portfolio.portfolio_projects.count(),
                'created_at': int(portfolio.created_at.timestamp()),
                'updated_at': int(portfolio.updated_at.timestamp()),
            })
        
        return JsonResponse({'portfolios': result})
    
    def post(self, request):
        """Create a new portfolio."""
        name = request.data.get('name', '').strip()
        if not name:
            return JsonResponse({'error': 'Portfolio name is required'}, status=400)
        
        description = request.data.get('description', '').strip()
        is_public = request.data.get('is_public', False)
        display_order = request.data.get('display_order', 'manual')
        
        # Validate display_order
        valid_orders = ['manual', 'contribution', 'date', 'name']
        if display_order not in valid_orders:
            display_order = 'manual'
        
        portfolio = Portfolio.objects.create(
            user=request.user,
            name=name,
            description=description,
            is_public=bool(is_public),
            display_order=display_order
        )
        
        return JsonResponse({
            'id': portfolio.id,
            'name': portfolio.name,
            'description': portfolio.description,
            'cover_image_url': portfolio.cover_image_url or None,
            'is_public': portfolio.is_public,
            'slug': portfolio.slug,
            'display_order': portfolio.display_order,
            'project_count': 0,
            'created_at': int(portfolio.created_at.timestamp()),
            'updated_at': int(portfolio.updated_at.timestamp()),
        }, status=201)


@method_decorator(csrf_exempt, name="dispatch")
class PortfolioDetailView(APIView):
    """Get, update, or delete a specific portfolio."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, portfolio_id):
        """Get portfolio details with full aggregated summary."""
        portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
        return JsonResponse(aggregate_portfolio_data(portfolio))
    
    def patch(self, request, portfolio_id):
        """Update portfolio metadata."""
        portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
        
        if 'name' in request.data:
            name = request.data['name'].strip()
            if not name:
                return JsonResponse({'error': 'Portfolio name cannot be empty'}, status=400)
            portfolio.name = name
        
        if 'description' in request.data:
            portfolio.description = request.data['description'].strip()
        
        if 'is_public' in request.data:
            portfolio.is_public = bool(request.data['is_public'])
        
        if 'display_order' in request.data:
            valid_orders = ['manual', 'contribution', 'date', 'name']
            if request.data['display_order'] in valid_orders:
                portfolio.display_order = request.data['display_order']
        
        if 'cover_image_url' in request.data:
            portfolio.cover_image_url = request.data['cover_image_url'].strip()
        
        portfolio.save()
        
        return JsonResponse({
            'id': portfolio.id,
            'name': portfolio.name,
            'description': portfolio.description,
            'cover_image_url': portfolio.cover_image_url or None,
            'is_public': portfolio.is_public,
            'slug': portfolio.slug,
            'display_order': portfolio.display_order,
            'updated_at': int(portfolio.updated_at.timestamp()),
        })
    
    def delete(self, request, portfolio_id):
        """Delete a portfolio (projects remain in user account)."""
        portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
        portfolio.delete()
        return JsonResponse({'message': 'Portfolio deleted successfully'})


@method_decorator(csrf_exempt, name="dispatch")
class PortfolioCoverUploadView(APIView):
    """Placeholder for future image upload functionality."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, portfolio_id):
        """Image upload endpoint - returns NOT IMPLEMENTED for now."""
        # Verify portfolio exists and belongs to user
        get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
        
        return JsonResponse({
            'error': 'Image upload not yet implemented',
            'message': 'This endpoint is reserved for future image upload functionality. '
                       'For now, use the cover_image_url field with external URLs via PATCH /api/portfolios/{id}/'
        }, status=501)


@method_decorator(csrf_exempt, name="dispatch")
class PortfolioProjectsView(APIView):
    """Add projects to a portfolio."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, portfolio_id):
        """Add a project to portfolio."""
        portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
        
        project_id = request.data.get('project_id')
        if not project_id:
            return JsonResponse({'error': 'project_id is required'}, status=400)
        
        project = get_object_or_404(Project, id=project_id, user=request.user)
        
        # Check if already exists
        if PortfolioProject.objects.filter(portfolio=portfolio, project=project).exists():
            return JsonResponse({'error': 'Project already in portfolio'}, status=400)
        
        # Get next display order
        max_order = PortfolioProject.objects.filter(portfolio=portfolio).count()
        
        portfolio_project = PortfolioProject.objects.create(
            portfolio=portfolio,
            project=project,
            display_order=max_order,
            custom_title=request.data.get('custom_title', ''),
            custom_description=request.data.get('custom_description', ''),
            highlight=bool(request.data.get('highlight', False)),
            include_in_resume=bool(request.data.get('include_in_resume', True)),
        )
        
        return JsonResponse({
            'portfolio_project_id': portfolio_project.id,
            'project_id': project.id,
            'display_order': portfolio_project.display_order,
            'message': 'Project added to portfolio'
        }, status=201)


@method_decorator(csrf_exempt, name="dispatch")
class PortfolioProjectDetailView(APIView):
    """Update or remove a project from portfolio."""
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, portfolio_id, portfolio_project_id):
        """Update portfolio project customization."""
        portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
        portfolio_project = get_object_or_404(
            PortfolioProject,
            id=portfolio_project_id,
            portfolio=portfolio
        )
        
        if 'custom_title' in request.data:
            portfolio_project.custom_title = request.data['custom_title'].strip()
        
        if 'custom_description' in request.data:
            portfolio_project.custom_description = request.data['custom_description'].strip()
        
        if 'display_order' in request.data:
            portfolio_project.display_order = int(request.data['display_order'])
        
        if 'highlight' in request.data:
            portfolio_project.highlight = bool(request.data['highlight'])
        
        if 'include_in_resume' in request.data:
            portfolio_project.include_in_resume = bool(request.data['include_in_resume'])
        
        if 'custom_bullet_points' in request.data:
            bullets = request.data['custom_bullet_points']
            if isinstance(bullets, list):
                portfolio_project.custom_bullet_points = bullets
        
        if 'use_custom_bullets' in request.data:
            portfolio_project.use_custom_bullets = bool(request.data['use_custom_bullets'])
        
        portfolio_project.save()
        
        return JsonResponse({
            'portfolio_project_id': portfolio_project.id,
            'custom_title': portfolio_project.custom_title,
            'custom_description': portfolio_project.custom_description,
            'display_order': portfolio_project.display_order,
            'highlight': portfolio_project.highlight,
            'include_in_resume': portfolio_project.include_in_resume,
            'use_custom_bullets': portfolio_project.use_custom_bullets,
            'message': 'Portfolio project updated'
        })
    
    def delete(self, request, portfolio_id, portfolio_project_id):
        """Remove a project from portfolio."""
        portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
        portfolio_project = get_object_or_404(
            PortfolioProject,
            id=portfolio_project_id,
            portfolio=portfolio
        )
        
        portfolio_project.delete()
        return JsonResponse({'message': 'Project removed from portfolio'})


@method_decorator(csrf_exempt, name="dispatch")
class PortfolioReorderView(APIView):
    """Reorder projects in a portfolio."""
    permission_classes = [IsAuthenticated]
    
    @transaction.atomic
    def post(self, request, portfolio_id):
        """Reorder projects based on array of portfolio_project_ids."""
        portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
        
        project_order = request.data.get('project_order', [])
        if not isinstance(project_order, list):
            return JsonResponse({'error': 'project_order must be an array'}, status=400)
        
        # Update display_order for each project
        for index, pp_id in enumerate(project_order):
            try:
                PortfolioProject.objects.filter(
                    id=int(pp_id),
                    portfolio=portfolio
                ).update(display_order=index)
            except (ValueError, TypeError):
                # Skip invalid IDs
                pass
        
        return JsonResponse({'message': 'Projects reordered successfully'})


@method_decorator(csrf_exempt, name="dispatch")
class PublicPortfolioView(APIView):
    """Public view of a portfolio (no authentication required)."""
    permission_classes = [AllowAny]
    
    def get(self, request, slug):
        """Get public portfolio by slug."""
        portfolio = get_object_or_404(Portfolio, slug=slug, is_public=True)
        
        # Get aggregated data
        data = aggregate_portfolio_data(portfolio)
        
        # Add user public info
        user = portfolio.user
        data['user'] = {
            'username': user.username,
            'full_name': user.get_full_name() or user.username,
            'github_username': user.github_username or '',
            'portfolio_url': user.portfolio_url or '',
        }
        
        return JsonResponse(data)
