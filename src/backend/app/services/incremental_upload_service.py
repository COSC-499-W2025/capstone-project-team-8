"""
Incremental Upload Service for handling additional ZIP files 
that add or update information in existing portfolios/projects.
"""

import os
import hashlib
import zipfile
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from django.db import transaction
from django.db import models
from django.db.models import Max
from django.utils import timezone
from django.contrib.auth.models import User

from app.models import Project, Portfolio, ProjectFile, PortfolioProject
from app.services.database_service import ProjectDatabaseService
from app.services.folder_upload import FolderUploadService


class IncrementalUploadService:
    """
    Service for handling incremental uploads that add new files 
    or update existing projects in a portfolio.
    """
    
    def __init__(self):
        self.folder_upload_service = FolderUploadService()
        self.db_service = ProjectDatabaseService()
    
    def process_incremental_upload(
        self,
        user: User,
        upload_file,
        target_portfolio_id: Optional[int] = None,
        target_project_id: Optional[int] = None,
        github_username: Optional[str] = None,
        send_to_llm: bool = False
    ) -> Dict[str, Any]:
        """
        Process an incremental upload that adds files to existing projects
        or creates new projects within an existing portfolio.
        
        Args:
            user: The authenticated user
            upload_file: The uploaded ZIP file
            target_portfolio_id: ID of portfolio to update (optional)
            target_project_id: ID of specific project to update (optional)
            github_username: Username for attribution
            send_to_llm: Whether to send analysis to LLM
            
        Returns:
            Dictionary with processing results and statistics
        """
        
        # Process the upload using existing folder upload service
        analysis_data = self.folder_upload_service.process_zip(
            upload=upload_file,
            github_username=github_username,
            send_to_llm=send_to_llm
        )
        
        # Create a session ID to track this incremental upload
        session_id = self._generate_session_id()
        
        # Analyze what we received and determine merge strategy
        merge_strategy = self._determine_merge_strategy(
            user, analysis_data, target_portfolio_id, target_project_id
        )
        
        with transaction.atomic():
            if merge_strategy['type'] == 'project_update':
                result = self._merge_into_existing_project(
                    user, analysis_data, merge_strategy['target_project'], session_id
                )
            elif merge_strategy['type'] == 'portfolio_expansion':
                result = self._add_to_existing_portfolio(
                    user, analysis_data, merge_strategy['target_portfolio'], session_id
                )
            else:  # 'new_standalone'
                result = self._create_new_projects(user, analysis_data, session_id)
            
            # Update portfolio last_incremental_upload timestamp
            if target_portfolio_id:
                try:
                    portfolio = Portfolio.objects.get(id=target_portfolio_id, user=user)
                    portfolio.last_incremental_upload = timezone.now()
                    portfolio.save(update_fields=['last_incremental_upload'])
                except Portfolio.DoesNotExist:
                    pass
        
        return {
            'session_id': session_id,
            'merge_strategy': merge_strategy['type'],
            'processed_projects': result.get('projects', []),
            'files_added': result.get('files_added', 0),
            'files_deduplicated': result.get('files_deduplicated', 0),
            'analysis_data': analysis_data,
            **result
        }
    
    def _determine_merge_strategy(
        self, 
        user: User, 
        analysis_data: Dict[str, Any],
        target_portfolio_id: Optional[int],
        target_project_id: Optional[int]
    ) -> Dict[str, Any]:
        """
        Determine how to merge the new upload with existing data.
        """
        projects_in_upload = analysis_data.get('projects', [])
        
        # If targeting a specific project
        if target_project_id:
            try:
                target_project = Project.objects.get(id=target_project_id, user=user)
                return {
                    'type': 'project_update',
                    'target_project': target_project,
                    'reason': f'Updating specific project {target_project.name}'
                }
            except Project.DoesNotExist:
                pass
        
        # If targeting a portfolio, try to match by project names/paths
        if target_portfolio_id:
            try:
                portfolio = Portfolio.objects.get(id=target_portfolio_id, user=user)
                existing_projects = Project.objects.filter(
                    portfolios=portfolio, user=user
                ).distinct()
                
                # Try to match uploaded projects to existing ones by name/path
                matched_projects = []
                for upload_project in projects_in_upload:
                    project_name = upload_project.get('root', '').strip('./').replace('/', ' - ')
                    project_root = upload_project.get('root', '')
                    
                    for existing_project in existing_projects:
                        if (existing_project.project_root_path == project_root or
                            project_name.lower() in existing_project.name.lower()):
                            matched_projects.append({
                                'upload_project': upload_project,
                                'existing_project': existing_project
                            })
                            break
                
                return {
                    'type': 'portfolio_expansion',
                    'target_portfolio': portfolio,
                    'matched_projects': matched_projects,
                    'reason': f'Expanding portfolio {portfolio.title}'
                }
            except Portfolio.DoesNotExist:
                pass
        
        return {
            'type': 'new_standalone',
            'reason': 'Creating new projects without specific targets'
        }
    
    def _merge_into_existing_project(
        self, 
        user: User, 
        analysis_data: Dict[str, Any], 
        target_project: Project,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Merge new files into an existing project as an incremental version.
        """
        projects_data = analysis_data.get('projects', [])
        if not projects_data:
            return {'projects': [], 'files_added': 0, 'files_deduplicated': 0}
        
        # Use the first project from upload (could be enhanced to merge multiple)
        upload_project = projects_data[0]
        
        # Create incremental version
        next_version = (Project.objects.filter(
            base_project=target_project
        ).count() + 2)  # +2 because base is v1, first increment is v2
        
        incremental_project = Project.objects.create(
            user=user,
            name=f"{target_project.name} (v{next_version})",
            description=target_project.description,
            classification_type=upload_project.get('classification', {}).get('type', target_project.classification_type),
            classification_confidence=upload_project.get('classification', {}).get('confidence', 0.0),
            project_root_path=upload_project.get('root', target_project.project_root_path),
            project_tag=upload_project.get('id'),
            base_project=target_project,
            version_number=next_version,
            is_incremental_update=True,
            incremental_upload_session=session_id,
            upload_source='incremental_zip',
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
        
        # Process files with deduplication against the base project
        files_added, files_deduplicated = self._process_incremental_files(
            incremental_project, upload_project, target_project
        )
        
        # Update file counts
        incremental_project.total_files = files_added
        incremental_project.save(update_fields=['total_files'])
        
        return {
            'projects': [incremental_project],
            'files_added': files_added,
            'files_deduplicated': files_deduplicated,
            'base_project': target_project
        }
    
    def _add_to_existing_portfolio(
        self, 
        user: User, 
        analysis_data: Dict[str, Any], 
        target_portfolio: Portfolio,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Add new projects to an existing portfolio or update existing projects.
        """
        projects_data = analysis_data.get('projects', [])
        created_projects = []
        total_files_added = 0
        total_files_deduplicated = 0
        
        for project_data in projects_data:
            # Check if this looks like an update to an existing project
            project_root = project_data.get('root', '')
            project_name = project_root.strip('./').replace('/', ' - ') if project_root else 'Uploaded Files'
            
            # Try to find matching existing project in portfolio
            existing_projects = Project.objects.filter(
                portfolios=target_portfolio, 
                user=user
            ).distinct()
            
            matched_project = None
            for existing_project in existing_projects:
                if (existing_project.project_root_path == project_root or
                    project_name.lower() in existing_project.name.lower()):
                    matched_project = existing_project
                    break
            
            if matched_project:
                # Create incremental version
                result = self._merge_into_existing_project(
                    user, {'projects': [project_data]}, matched_project, session_id
                )
                created_projects.extend(result['projects'])
                total_files_added += result['files_added']
                total_files_deduplicated += result['files_deduplicated']
            else:
                # Create new project and add to portfolio
                new_projects = self.db_service.save_project_analysis(
                    user=user,
                    analysis_data={'projects': [project_data], 'overall': analysis_data.get('overall', {})},
                    upload_filename=f'incremental_upload_{session_id}.zip'
                )
                
                for new_project in new_projects:
                    new_project.incremental_upload_session = session_id
                    new_project.save(update_fields=['incremental_upload_session'])
                    
                    # Add to portfolio
                    max_order = target_portfolio.portfolio_projects.aggregate(
                        max_order=Max('order')
                    )['max_order'] or 0
                    
                    PortfolioProject.objects.create(
                        portfolio=target_portfolio,
                        project=new_project,
                        order=max_order + 1,
                        notes=f'Added via incremental upload {session_id}'
                    )
                
                created_projects.extend(new_projects)
                total_files_added += new_project.total_files
        
        return {
            'projects': created_projects,
            'files_added': total_files_added,
            'files_deduplicated': total_files_deduplicated,
            'target_portfolio': target_portfolio
        }
    
    def _create_new_projects(
        self, 
        user: User, 
        analysis_data: Dict[str, Any],
        session_id: str
    ) -> Dict[str, Any]:
        """
        Create new standalone projects from the upload.
        """
        created_projects = self.db_service.save_project_analysis(
            user=user,
            analysis_data=analysis_data,
            upload_filename=f'incremental_upload_{session_id}.zip'
        )
        
        # Mark as part of this incremental upload session
        for project in created_projects:
            project.incremental_upload_session = session_id
            project.save(update_fields=['incremental_upload_session'])
        
        return {
            'projects': created_projects,
            'files_added': sum(p.total_files for p in created_projects),
            'files_deduplicated': 0
        }
    
    def _process_incremental_files(
        self, 
        incremental_project: Project, 
        upload_project_data: Dict[str, Any],
        base_project: Project
    ) -> Tuple[int, int]:
        """
        Process files for an incremental project with deduplication.
        
        Returns:
            Tuple of (files_added, files_deduplicated)
        """
        files_added = 0
        files_deduplicated = 0
        
        # Get existing file hashes from base project and all its versions
        existing_hashes = set(
            ProjectFile.objects.filter(
                project__in=[base_project] + list(base_project.incremental_versions.all())
            ).exclude(
                content_hash=''
            ).values_list('content_hash', flat=True)
        )
        
        files_data = upload_project_data.get('files', {})
        
        for file_type in ['code', 'content', 'image', 'unknown']:
            files_of_type = files_data.get(file_type, [])
            
            for file_data in files_of_type:
                # Handle both string and dictionary formats
                if isinstance(file_data, str):
                    # If file_data is just a string (filepath), convert to dict format
                    file_path = file_data
                    file_content = ''
                else:
                    # Normal dictionary format
                    file_path = file_data.get('path', '')
                    file_content = file_data.get('text', '') or file_data.get('content', '')
                
                # Calculate content hash
                content_hash = ''
                if file_content:
                    content_hash = hashlib.sha256(file_content.encode('utf-8')).hexdigest()
                
                # Check if file already exists
                if content_hash and content_hash in existing_hashes:
                    files_deduplicated += 1
                    # Still create a record but mark as duplicate
                    ProjectFile.objects.create(
                        project=incremental_project,
                        file_path=file_path,
                        filename=os.path.basename(file_path),
                        file_extension=os.path.splitext(file_path)[1].lower(),
                        content_hash=content_hash,
                        is_duplicate=True,
                        file_type=file_type,
                        content_preview=file_content[:1000] if file_content else '',
                        is_content_truncated=len(file_content) > 1000 if file_content else False
                    )
                else:
                    files_added += 1
                    existing_hashes.add(content_hash)  # Track for subsequent files
                    
                    ProjectFile.objects.create(
                        project=incremental_project,
                        file_path=file_path,
                        filename=os.path.basename(file_path),
                        file_extension=os.path.splitext(file_path)[1].lower(),
                        content_hash=content_hash,
                        is_duplicate=False,
                        file_type=file_type,
                        line_count=file_data.get('lines') if file_type == 'code' else None,
                        character_count=len(file_content) if file_content else None,
                        file_size_bytes=file_data.get('size') if file_type == 'image' else None,
                        content_preview=file_content[:1000] if file_content else '',
                        is_content_truncated=len(file_content) > 1000 if file_content else False
                    )
        
        return files_added, files_deduplicated
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID for this incremental upload."""
        return f"inc_{int(timezone.now().timestamp())}_{hashlib.md5(str(timezone.now()).encode()).hexdigest()[:8]}"
    
    def get_project_history(self, base_project: Project) -> List[Dict[str, Any]]:
        """
        Get the complete history of a project including all incremental versions.
        
        Args:
            base_project: The base project
            
        Returns:
            List of project versions with metadata
        """
        versions = [base_project]
        versions.extend(
            base_project.incremental_versions.all().order_by('version_number')
        )
        
        return [{
            'id': project.id,
            'version': project.version_number if hasattr(project, 'version_number') else 1,
            'name': project.name,
            'created_at': project.created_at,
            'updated_at': project.updated_at,
            'is_incremental': project.is_incremental_update if hasattr(project, 'is_incremental_update') else False,
            'session_id': project.incremental_upload_session if hasattr(project, 'incremental_upload_session') else None,
            'total_files': project.total_files,
            'classification': project.classification_type
        } for project in versions]