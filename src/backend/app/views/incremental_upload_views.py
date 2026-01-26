"""
API views for incremental uploads - adding files to existing portfolios/projects.
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, OpenApiResponse
import tempfile
import os
import logging

from app.models import Portfolio, Project
from app.services.incremental_upload_service import IncrementalUploadService
from app.serializers import ErrorResponseSerializer


class IncrementalUploadSerializer:
    """Serializer documentation for incremental uploads."""
    pass


@method_decorator(csrf_exempt, name="dispatch")
class IncrementalUploadView(APIView):
    """
    Handle incremental uploads that add new files to existing portfolios or projects.
    
    POST /api/incremental-upload/
    - Upload ZIP file with additional project files
    - Automatically deduplicate files and merge with existing projects
    - Can target specific portfolio or project, or create new standalone projects
    """
    
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {'type': 'string', 'format': 'binary'},
                    'target_portfolio_id': {'type': 'integer', 'required': False},
                    'target_project_id': {'type': 'integer', 'required': False},
                    'github_username': {'type': 'string', 'required': False},
                    'consent_send_llm': {'type': 'boolean', 'default': False}
                },
                'required': ['file']
            }
        },
        responses={
            200: OpenApiResponse(description="Incremental upload processed successfully"),
            400: ErrorResponseSerializer,
        },
        description="Upload additional files to existing portfolio/project or create new projects with incremental versioning support.",
        tags=["Incremental Upload"],
    )
    def post(self, request):
        """Process incremental upload."""
        upload_file = request.FILES.get("file")
        if not upload_file:
            return JsonResponse({"error": "No file provided. Use 'file' form field."}, status=400)
        
        # Parse request parameters from multipart form data
        target_portfolio_id = request.POST.get("target_portfolio_id")
        target_project_id = request.POST.get("target_project_id")
        github_username = request.POST.get("github_username")
        send_to_llm = request.POST.get("consent_send_llm", False) in ['1', 'true', 'True', True]
        
        # Convert string IDs to integers
        try:
            if target_portfolio_id:
                target_portfolio_id = int(target_portfolio_id)
            if target_project_id:
                target_project_id = int(target_project_id)
        except (ValueError, TypeError):
            return JsonResponse({"error": "Invalid portfolio or project ID"}, status=400)
        
        # Validate portfolio/project ownership
        if target_portfolio_id:
            try:
                Portfolio.objects.get(id=target_portfolio_id, user=request.user)
            except Portfolio.DoesNotExist:
                return JsonResponse({"error": "Portfolio not found or not owned by user"}, status=404)
        
        if target_project_id:
            try:
                Project.objects.get(id=target_project_id, user=request.user)
            except Project.DoesNotExist:
                return JsonResponse({"error": "Project not found or not owned by user"}, status=404)
        
        try:
            # Process the incremental upload
            service = IncrementalUploadService()
            result = service.process_incremental_upload(
                user=request.user,
                upload_file=upload_file,
                target_portfolio_id=target_portfolio_id,
                target_project_id=target_project_id,
                github_username=github_username,
                send_to_llm=send_to_llm
            )
            
            # Build response
            response_data = {
                "success": True,
                "session_id": result["session_id"],
                "merge_strategy": result["merge_strategy"],
                "projects_processed": len(result["processed_projects"]),
                "files_added": result["files_added"],
                "files_deduplicated": result["files_deduplicated"],
                "projects": [
                    {
                        "id": project.id,
                        "name": project.name,
                        "is_incremental": getattr(project, 'is_incremental_update', False),
                        "version_number": getattr(project, 'version_number', 1),
                        "base_project_id": project.base_project.id if getattr(project, 'base_project', None) else None,
                        "total_files": project.total_files,
                        "classification": project.classification_type
                    } for project in result["processed_projects"]
                ]
            }
            
            # Add target information to response
            if target_portfolio_id:
                response_data["target_portfolio_id"] = target_portfolio_id
            if target_project_id:
                response_data["target_project_id"] = target_project_id
            
            return JsonResponse(response_data)
            
        except Exception as e:
            import traceback
            logger = logging.getLogger(__name__)
            logger.error(f"Incremental upload failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return JsonResponse({"error": f"Processing failed: {str(e)}"}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class ProjectHistoryView(APIView):
    """
    Get the complete version history of a project including all incremental updates.
    
    GET /api/projects/{id}/history/
    """
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        responses={
            200: {
                "type": "object",
                "properties": {
                    "base_project": {"type": "object"},
                    "versions": {"type": "array"},
                    "total_versions": {"type": "integer"}
                }
            },
            404: ErrorResponseSerializer,
        },
        description="Get complete version history for a project including incremental updates.",
        tags=["Projects"],
    )
    def get(self, request, project_id):
        """Get project version history."""
        try:
            project = Project.objects.get(id=project_id, user=request.user)
        except Project.DoesNotExist:
            return JsonResponse({"error": "Project not found"}, status=404)
        
        # Find the base project (could be this project or its base)
        base_project = getattr(project, 'base_project', None) or project
        
        # Get complete history using the service
        service = IncrementalUploadService()
        history = service.get_project_history(base_project)
        
        return JsonResponse({
            "base_project": {
                "id": base_project.id,
                "name": base_project.name,
                "created_at": base_project.created_at,
                "classification": base_project.classification_type
            },
            "versions": history,
            "total_versions": len(history),
            "requested_project_id": project_id
        })


@method_decorator(csrf_exempt, name="dispatch")
class PortfolioIncrementalStatsView(APIView):
    """
    Get statistics about incremental uploads for a portfolio.
    
    GET /api/portfolio/{id}/incremental-stats/
    """
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        responses={
            200: {
                "type": "object",
                "properties": {
                    "portfolio": {"type": "object"},
                    "incremental_uploads": {"type": "integer"},
                    "total_versions": {"type": "integer"},
                    "last_incremental_upload": {"type": "string"},
                    "projects_with_versions": {"type": "array"}
                }
            },
            404: ErrorResponseSerializer,
        },
        description="Get incremental upload statistics for a portfolio.",
        tags=["Portfolio"],
    )
    def get(self, request, portfolio_id):
        """Get portfolio incremental upload stats."""
        try:
            portfolio = Portfolio.objects.get(id=portfolio_id, user=request.user)
        except Portfolio.DoesNotExist:
            return JsonResponse({"error": "Portfolio not found"}, status=404)
        
        # Get all projects in portfolio
        portfolio_projects = Project.objects.filter(
            portfolios=portfolio, user=request.user
        ).distinct()
        
        # Count incremental versions
        incremental_sessions = set()
        projects_with_versions = []
        total_versions = 0
        
        for project in portfolio_projects:
            # Count versions for this project
            if hasattr(project, 'incremental_versions'):
                versions = project.incremental_versions.all()
                version_count = versions.count() + 1  # +1 for base project
            else:
                versions = Project.objects.filter(base_project=project)
                version_count = versions.count() + 1
            
            if version_count > 1:
                projects_with_versions.append({
                    "project_id": project.id,
                    "project_name": project.name,
                    "version_count": version_count,
                    "latest_version": max([getattr(v, 'version_number', 1) for v in versions] + [1])
                })
            
            total_versions += version_count
            
            # Collect session IDs
            for version in versions:
                if hasattr(version, 'incremental_upload_session') and version.incremental_upload_session:
                    incremental_sessions.add(version.incremental_upload_session)
        
        return JsonResponse({
            "portfolio": {
                "id": portfolio.id,
                "title": portfolio.title,
                "supports_incremental_updates": getattr(portfolio, 'supports_incremental_updates', True)
            },
            "incremental_uploads": len(incremental_sessions),
            "total_versions": total_versions,
            "projects_with_versions": projects_with_versions,
            "last_incremental_upload": portfolio.last_incremental_upload.isoformat() if getattr(portfolio, 'last_incremental_upload', None) else None,
            "portfolio_projects_count": portfolio_projects.count()
        })