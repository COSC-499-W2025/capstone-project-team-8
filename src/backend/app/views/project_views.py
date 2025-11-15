"""
API Views for User Projects

Provides endpoints to retrieve and manage user's project data.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Count, Sum, Avg
from django.http import JsonResponse

from app.models import Project, ProgrammingLanguage, Framework, Contributor


class UserProjectsView(APIView):
    """
    API endpoint to retrieve user's projects with statistics.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get all projects for the authenticated user.
        
        Returns project list with basic info and statistics.
        """
        # For testing: show all projects if not authenticated
        if request.user.is_authenticated:
            user = request.user
            projects = user.projects.all().order_by('-created_at')
        else:
            # Show all projects for testing (remove this in production)
            from app.models import Project
            projects = Project.objects.all().order_by('-created_at')
        
        project_data = []
        for project in projects:
            # Get languages and frameworks
            languages = list(project.languages.values_list('name', flat=True))
            frameworks = list(project.frameworks.values_list('name', flat=True))
            
            # Get top contributors
            top_contributors = project.contributions.select_related('contributor').order_by('-commit_count')[:3]
            contributors = [
                {
                    'name': contrib.contributor.name,
                    'commits': contrib.commit_count,
                    'percent': contrib.percent_of_commits
                }
                for contrib in top_contributors
            ]
            
            project_info = {
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'classification': {
                    'type': project.classification_type,
                    'confidence': project.classification_confidence
                },
                'languages': languages,
                'frameworks': frameworks,
                'statistics': {
                    'total_files': project.total_files,
                    'code_files': project.code_files_count,
                    'text_files': project.text_files_count,
                    'image_files': project.image_files_count
                },
                'contributors': contributors,
                'git_repository': project.git_repository,
                'first_commit_date': project.first_commit_date,
                'created_at': project.created_at,
                'updated_at': project.updated_at
            }
            project_data.append(project_info)
        
        return Response({
            'projects': project_data,
            'total_count': len(project_data)
        })


class ProjectDetailView(APIView):
    """
    API endpoint to get detailed information about a specific project.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, project_id):
        """
        Get detailed information about a specific project.
        
        Args:
            project_id: ID of the project to retrieve
        """
        try:
            project = Project.objects.get(id=project_id, user=request.user)
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get detailed language information
        languages = []
        for proj_lang in project.projectlanguage_set.all().select_related('language'):
            languages.append({
                'name': proj_lang.language.name,
                'category': proj_lang.language.category,
                'file_count': proj_lang.file_count,
                'is_primary': proj_lang.is_primary
            })
        
        # Get detailed framework information
        frameworks = []
        for proj_framework in project.projectframework_set.all().select_related('framework'):
            frameworks.append({
                'name': proj_framework.framework.name,
                'category': proj_framework.framework.category,
                'detected_from': proj_framework.detected_from
            })
        
        # Get all contributors with full stats
        contributors = []
        for contrib in project.contributions.all().select_related('contributor'):
            contributors.append({
                'name': contrib.contributor.name,
                'email': contrib.contributor.email,
                'commits': contrib.commit_count,
                'lines_added': contrib.lines_added,
                'lines_deleted': contrib.lines_deleted,
                'net_lines': contrib.net_lines,
                'percent_commits': contrib.percent_of_commits,
                'is_registered_user': contrib.contributor.user is not None
            })
        
        # Get file breakdown by type
        files_by_type = {}
        for file_type in ['code', 'content', 'image', 'unknown']:
            files = project.files.filter(file_type=file_type)
            files_by_type[file_type] = {
                'count': files.count(),
                'files': [
                    {
                        'filename': f.filename,
                        'path': f.file_path,
                        'extension': f.file_extension,
                        'lines': f.line_count,
                        'characters': f.character_count,
                        'size_bytes': f.file_size_bytes,
                        'language': f.detected_language.name if f.detected_language else None
                    }
                    for f in files[:20]  # Limit to first 20 files per type
                ]
            }
        
        return Response({
            'project': {
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'classification': {
                    'type': project.classification_type,
                    'confidence': project.classification_confidence
                },
                'languages': languages,
                'frameworks': frameworks,
                'contributors': contributors,
                'files': files_by_type,
                'metadata': {
                    'project_root_path': project.project_root_path,
                    'project_tag': project.project_tag,
                    'git_repository': project.git_repository,
                    'first_commit_date': project.first_commit_date,
                    'upload_source': project.upload_source,
                    'original_zip_name': project.original_zip_name,
                    'created_at': project.created_at,
                    'updated_at': project.updated_at
                }
            }
        })


class UserStatsView(APIView):
    """
    API endpoint to get user's overall project statistics.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get comprehensive statistics for the user's projects.
        """
        user = request.user
        projects = user.projects.all()
        
        # Basic project statistics
        total_projects = projects.count()
        git_projects = projects.filter(git_repository=True).count()
        
        # File statistics
        file_stats = projects.aggregate(
            total_files=Sum('total_files'),
            code_files=Sum('code_files_count'),
            text_files=Sum('text_files_count'),
            image_files=Sum('image_files_count')
        )
        
        # Language usage across all projects
        language_usage = (
            ProgrammingLanguage.objects
            .filter(projects__user=user)
            .annotate(
                project_count=Count('projects', distinct=True),
                total_files=Sum('projectlanguage__file_count')
            )
            .order_by('-project_count', '-total_files')[:10]
        )
        
        languages = [
            {
                'name': lang.name,
                'category': lang.category,
                'project_count': lang.project_count,
                'file_count': lang.total_files or 0
            }
            for lang in language_usage
        ]
        
        # Framework usage
        framework_usage = (
            Framework.objects
            .filter(projects__user=user)
            .annotate(project_count=Count('projects', distinct=True))
            .order_by('-project_count')[:10]
        )
        
        frameworks = [
            {
                'name': fw.name,
                'category': fw.category,
                'project_count': fw.project_count
            }
            for fw in framework_usage
        ]
        
        # Project classifications
        classifications = {}
        for project in projects:
            class_type = project.classification_type
            if class_type not in classifications:
                classifications[class_type] = {
                    'count': 0,
                    'avg_confidence': 0,
                    'confidences': []
                }
            classifications[class_type]['count'] += 1
            classifications[class_type]['confidences'].append(project.classification_confidence)
        
        # Calculate average confidence for each classification
        for class_type, data in classifications.items():
            if data['confidences']:
                data['avg_confidence'] = sum(data['confidences']) / len(data['confidences'])
            del data['confidences']  # Remove raw data
        
        # Contribution statistics (as a contributor)
        contribution_stats = user.contributor_profiles.aggregate(
            total_projects_contributed=Count('contributions', distinct=True),
            total_commits=Sum('contributions__commit_count'),
            total_lines_added=Sum('contributions__lines_added'),
            total_lines_deleted=Sum('contributions__lines_deleted')
        )
        
        return Response({
            'user': {
                'username': user.username,
                'github_username': user.github_username,
                'display_name': user.display_name
            },
            'project_statistics': {
                'total_projects': total_projects,
                'git_projects': git_projects,
                'non_git_projects': total_projects - git_projects,
                'classifications': classifications
            },
            'file_statistics': file_stats,
            'technology_usage': {
                'languages': languages,
                'frameworks': frameworks
            },
            'contribution_statistics': contribution_stats
        })


class TechnologyStatsView(APIView):
    """
    API endpoint for overall platform technology statistics.
    """
    
    def get(self, request):
        """
        Get platform-wide technology usage statistics.
        Public endpoint - no authentication required.
        """
        # Most popular languages
        popular_languages = (
            ProgrammingLanguage.objects
            .annotate(
                project_count=Count('projects', distinct=True),
                user_count=Count('projects__user', distinct=True)
            )
            .filter(project_count__gt=0)
            .order_by('-project_count')[:20]
        )
        
        # Most popular frameworks
        popular_frameworks = (
            Framework.objects
            .annotate(
                project_count=Count('projects', distinct=True),
                user_count=Count('projects__user', distinct=True)
            )
            .filter(project_count__gt=0)
            .order_by('-project_count')[:20]
        )
        
        # Platform statistics
        platform_stats = {
            'total_projects': Project.objects.count(),
            'total_users': Project.objects.values('user').distinct().count(),
            'total_languages': ProgrammingLanguage.objects.filter(projects__isnull=False).distinct().count(),
            'total_frameworks': Framework.objects.filter(projects__isnull=False).distinct().count()
        }
        
        return Response({
            'platform_statistics': platform_stats,
            'popular_languages': [
                {
                    'name': lang.name,
                    'category': lang.category,
                    'project_count': lang.project_count,
                    'user_count': lang.user_count
                }
                for lang in popular_languages
            ],
            'popular_frameworks': [
                {
                    'name': fw.name,
                    'category': fw.category,
                    'project_count': fw.project_count,
                    'user_count': fw.user_count
                }
                for fw in popular_frameworks
            ]
        })