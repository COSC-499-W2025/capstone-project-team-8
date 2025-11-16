"""
Database Service for Processing Upload Results

This service handles converting the JSON response from project analysis
into structured database records using the Django models.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from django.db import transaction
from django.utils import timezone
import datetime as dt

from app.models import (
    User, Project, ProgrammingLanguage, Framework,
    ProjectLanguage, ProjectFramework, ProjectFile,
    Contributor, ProjectContribution
)


class ProjectDatabaseService:
    """
    Service for saving project analysis results to the database.
    
    Handles the complete workflow of converting JSON analysis results
    into normalized database records with proper relationships.
    """
    
    def save_project_analysis(
        self, 
        user: User, 
        analysis_data: Dict[str, Any], 
        upload_filename: str = "",
        project_name_override: str = ""
    ) -> List[Project]:
        """
        Save complete project analysis results to database.
        
        Args:
            user: The user who uploaded the project
            analysis_data: JSON response from folder upload analysis
            upload_filename: Original filename of uploaded ZIP
            project_name_override: Custom name for the project (optional)
            
        Returns:
            List of created Project objects
            
        Raises:
            ValueError: If analysis_data is invalid or missing required fields
        """
        if not analysis_data or 'projects' not in analysis_data:
            raise ValueError("Invalid analysis data: missing 'projects' field")
        
        projects = analysis_data.get('projects', [])
        overall = analysis_data.get('overall', {})
        
        created_projects = []
        
        with transaction.atomic():
            for project_data in projects:
                project = self._create_project(
                    user=user,
                    project_data=project_data,
                    overall_data=overall,
                    upload_filename=upload_filename,
                    project_name_override=project_name_override
                )
                created_projects.append(project)
                
                # Save languages and frameworks
                self._save_project_languages(project, project_data)
                self._save_project_frameworks(project, project_data)
                
                # Save files
                self._save_project_files(project, project_data)
                
                # Save contributors
                self._save_project_contributors(project, project_data)
        
        return created_projects
    
    def _create_project(
        self,
        user: User,
        project_data: Dict[str, Any],
        overall_data: Dict[str, Any],
        upload_filename: str,
        project_name_override: str
    ) -> Project:
        """
        Create the main Project record.
        
        Args:
            user: User who uploaded the project
            project_data: Individual project data from analysis
            overall_data: Overall analysis results
            upload_filename: Original ZIP filename
            project_name_override: Custom project name
            
        Returns:
            Created Project instance
        """
        # Determine project name
        if project_name_override:
            project_name = project_name_override
        else:
            # Generate name from root path or use default
            root = project_data.get('root', '')
            if root and root != '(non-git-files)':
                # Clean up root path for display
                project_name = root.strip('./').replace('/', ' - ') or 'Uploaded Project'
            else:
                project_name = 'Uploaded Files'
        
        # Get classification data (prefer project-specific over overall)
        classification = project_data.get('classification', {})
        if not classification:
            classification = overall_data
        
        # Parse classification type
        classification_type = classification.get('type', 'unknown')
        confidence = float(classification.get('confidence', 0.0))
        
        # Get file counts
        files = project_data.get('files', {})
        code_files = len(files.get('code', []))
        content_files = len(files.get('content', []))
        image_files = len(files.get('image', []))
        unknown_files = len(files.get('unknown', []))
        total_files = code_files + content_files + image_files + unknown_files
        
        # Parse timestamps
        created_at_timestamp = project_data.get('created_at')
        first_commit_date = None
        if created_at_timestamp:
            try:
                # Use timezone.UTC for Django 5.x compatibility
                first_commit_date = dt.datetime.fromtimestamp(created_at_timestamp, tz=timezone.UTC)
            except (ValueError, TypeError, AttributeError):
                # Fallback to None if there's any issue with timestamp parsing
                pass
        
        # Determine if this is a git repository
        project_id = project_data.get('id', 0)
        contributors = project_data.get('contributors', [])
        root = project_data.get('root', '')
        
        is_git_repo = (
            bool(project_id) and project_id > 0 and  # Git projects have ID > 0
            bool(contributors) and len(contributors) > 0 and  # Has contributors
            root != '(non-git-files)'  # Not unorganized files
        )
        
        project = Project.objects.create(
            user=user,
            name=project_name,
            classification_type=classification_type,
            classification_confidence=confidence,
            project_root_path=project_data.get('root', ''),
            project_tag=project_data.get('id'),
            total_files=total_files,
            code_files_count=code_files,
            text_files_count=content_files,
            image_files_count=image_files,
            git_repository=is_git_repo,
            first_commit_date=first_commit_date,
            upload_source='zip_file',
            original_zip_name=upload_filename
        )
        
        return project
    
    def _save_project_languages(self, project: Project, project_data: Dict[str, Any]) -> None:
        """
        Save programming languages detected in the project.
        
        Args:
            project: The project instance
            project_data: Project analysis data containing languages
        """
        classification = project_data.get('classification', {})
        detected_languages = classification.get('languages', [])
        
        if not detected_languages:
            return
        
        # Get or create language objects
        language_objects = []
        for lang_name in detected_languages:
            language, created = ProgrammingLanguage.objects.get_or_create(
                name=lang_name,
                defaults={
                    'category': self._get_language_category(lang_name)
                }
            )
            language_objects.append(language)
        
        # Create relationships with file counts
        files = project_data.get('files', {})
        code_files = files.get('code', [])
        
        # Count files by extension to estimate language usage
        extension_counts = {}
        for file_info in code_files:
            file_path = file_info.get('path', '') if isinstance(file_info, dict) else str(file_info)
            if '.' in file_path:
                ext = file_path.split('.')[-1].lower()
                extension_counts[ext] = extension_counts.get(ext, 0) + 1
        
        # Map extensions to languages (simplified)
        ext_to_lang = self._get_extension_language_mapping()
        
        for i, language in enumerate(language_objects):
            # Estimate file count for this language
            file_count = 0
            for ext, count in extension_counts.items():
                if ext_to_lang.get(ext) == language.name:
                    file_count += count
            
            # If we can't determine file count, distribute evenly
            if file_count == 0 and code_files:
                file_count = max(1, len(code_files) // len(language_objects))
            
            ProjectLanguage.objects.create(
                project=project,
                language=language,
                file_count=file_count,
                is_primary=bool(i == 0)  # First language is primary
            )
    
    def _save_project_frameworks(self, project: Project, project_data: Dict[str, Any]) -> None:
        """
        Save frameworks and libraries detected in the project.
        
        Args:
            project: The project instance
            project_data: Project analysis data containing frameworks
        """
        classification = project_data.get('classification', {})
        detected_frameworks = classification.get('frameworks', [])
        
        if not detected_frameworks:
            return
        
        for framework_name in detected_frameworks:
            # Get or create framework
            framework, created = Framework.objects.get_or_create(
                name=framework_name,
                defaults={
                    'category': self._get_framework_category(framework_name),
                    'language': self._get_framework_primary_language(framework_name)
                }
            )
            
            # Create relationship
            ProjectFramework.objects.create(
                project=project,
                framework=framework,
                detected_from='dependencies'  # Default, could be enhanced
            )
    
    def _save_project_files(self, project: Project, project_data: Dict[str, Any]) -> None:
        """
        Save individual file analysis results.
        
        Args:
            project: The project instance
            project_data: Project analysis data containing file information
        """
        files = project_data.get('files', {})
        
        # Process each file type
        for file_type, file_list in files.items():
            if file_type == 'unknown':
                # Handle unknown files (just filenames)
                for filename in file_list:
                    if isinstance(filename, str):
                        self._create_project_file(project, filename, file_type)
            else:
                # Handle structured file data
                for file_info in file_list:
                    if isinstance(file_info, dict):
                        filename = file_info.get('path', '')
                        self._create_project_file(project, filename, file_type, file_info)
                    elif isinstance(file_info, str):
                        self._create_project_file(project, file_info, file_type)
    
    def _create_project_file(
        self, 
        project: Project, 
        filename: str, 
        file_type: str, 
        file_info: Dict[str, Any] = None
    ) -> ProjectFile:
        """
        Create a ProjectFile record from file analysis data.
        
        Args:
            project: The project instance
            filename: Name of the file
            file_type: Type of file (code, content, image, unknown)
            file_info: Additional file metadata
            
        Returns:
            Created ProjectFile instance
        """
        if not file_info:
            file_info = {}
        
        # Extract file extension
        file_extension = ''
        if '.' in filename:
            file_extension = '.' + filename.split('.')[-1].lower()
        
        # Get file metrics based on type
        line_count = file_info.get('lines') if file_type == 'code' else None
        character_count = file_info.get('length') if file_type == 'content' else None
        file_size_bytes = file_info.get('size') if file_type == 'image' else None
        
        # Content preview for text files
        content_preview = file_info.get('text', '')
        is_truncated_raw = file_info.get('truncated', False)
        is_truncated = bool(is_truncated_raw) if is_truncated_raw not in [None, [], ''] else False
        
        # Detect language for code files
        detected_language = None
        if file_type == 'code' and file_extension:
            ext_to_lang = self._get_extension_language_mapping()
            lang_name = ext_to_lang.get(file_extension.lstrip('.'))
            if lang_name:
                detected_language, _ = ProgrammingLanguage.objects.get_or_create(
                    name=lang_name,
                    defaults={'category': self._get_language_category(lang_name)}
                )
        
        return ProjectFile.objects.create(
            project=project,
            file_path=filename,
            filename=filename.split('/')[-1],  # Extract just the filename
            file_extension=file_extension,
            file_type=file_type,
            file_size_bytes=file_size_bytes,
            line_count=line_count,
            character_count=character_count,
            content_preview=content_preview[:10000] if content_preview else '',
            is_content_truncated=is_truncated,
            detected_language=detected_language
        )
    
    def _save_project_contributors(self, project: Project, project_data: Dict[str, Any]) -> None:
        """
        Save git contributor information for the project.
        
        Args:
            project: The project instance
            project_data: Project analysis data containing contributors
        """
        contributors_data = project_data.get('contributors', [])
        
        if not contributors_data:
            return
        
        for contributor_info in contributors_data:
            name = contributor_info.get('name', '').strip()
            email = contributor_info.get('email', '').strip()
            
            if not name:
                continue
            
            # Get or create contributor
            contributor, created = Contributor.objects.get_or_create(
                name=name,
                email=email,
                defaults={'user': self._find_matching_user(name, email)}
            )
            
            # Create contribution record
            ProjectContribution.objects.create(
                project=project,
                contributor=contributor,
                commit_count=contributor_info.get('commits', 0),
                lines_added=contributor_info.get('lines_added', 0),
                lines_deleted=contributor_info.get('lines_deleted', 0),
                percent_of_commits=contributor_info.get('percent_commits', 0.0)
            )
    
    def _find_matching_user(self, name: str, email: str) -> Optional[User]:
        """
        Try to match a contributor to an existing User account.
        
        Args:
            name: Contributor name
            email: Contributor email
            
        Returns:
            User instance if match found, None otherwise
        """
        if not email:
            return None
        
        # Try exact email match first
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            pass
        
        # Try GitHub username match
        if name:
            try:
                return User.objects.get(github_username__iexact=name)
            except User.DoesNotExist:
                pass
        
        return None
    
    # Helper methods for categorization
    def _get_language_category(self, language: str) -> str:
        """Categorize programming language."""
        language_lower = language.lower()
        
        if language_lower in ['javascript', 'typescript', 'html', 'css']:
            return 'web'
        elif language_lower in ['python', 'r', 'julia', 'jupyter notebook']:
            return 'data'
        elif language_lower in ['swift', 'kotlin', 'dart']:
            return 'mobile'
        elif language_lower in ['c', 'c++', 'rust', 'go', 'assembly']:
            return 'system'
        else:
            return 'general'
    
    def _get_framework_category(self, framework: str) -> str:
        """Categorize framework/library."""
        framework_lower = framework.lower()
        
        if framework_lower in ['react', 'vue', 'angular', 'svelte', 'next.js']:
            return 'web_frontend'
        elif framework_lower in ['django', 'flask', 'express', 'fastapi']:
            return 'web_backend'
        elif framework_lower in ['react native', 'flutter', 'ionic']:
            return 'mobile'
        elif framework_lower in ['tensorflow', 'pytorch', 'pandas', 'numpy']:
            return 'data_science'
        elif framework_lower in ['jest', 'pytest', 'junit', 'cypress']:
            return 'testing'
        elif framework_lower in ['material-ui', 'antd', 'bootstrap', 'tailwind css']:
            return 'ui_library'
        elif framework_lower in ['webpack', 'vite', 'rollup', 'parcel']:
            return 'build_tool'
        elif framework_lower in ['prisma', 'typeorm', 'sqlalchemy', 'mongoose']:
            return 'database'
        else:
            return 'other'
    
    def _get_framework_primary_language(self, framework: str) -> Optional[ProgrammingLanguage]:
        """Get the primary language for a framework."""
        framework_lower = framework.lower()
        
        # Framework to language mapping
        framework_languages = {
            'django': 'Python',
            'flask': 'Python',
            'fastapi': 'Python',
            'react': 'JavaScript',
            'vue': 'JavaScript',
            'angular': 'TypeScript',
            'express': 'JavaScript',
            'spring': 'Java',
            'rails': 'Ruby',
            'laravel': 'PHP'
        }
        
        lang_name = framework_languages.get(framework_lower)
        if lang_name:
            language, _ = ProgrammingLanguage.objects.get_or_create(
                name=lang_name,
                defaults={'category': self._get_language_category(lang_name)}
            )
            return language
        
        return None
    
    def _get_extension_language_mapping(self) -> Dict[str, str]:
        """Get mapping of file extensions to programming languages."""
        return {
            'py': 'Python',
            'js': 'JavaScript',
            'jsx': 'JavaScript',
            'ts': 'TypeScript',
            'tsx': 'TypeScript',
            'java': 'Java',
            'c': 'C',
            'cpp': 'C++',
            'cc': 'C++',
            'cxx': 'C++',
            'h': 'C',
            'hpp': 'C++',
            'cs': 'C#',
            'go': 'Go',
            'rs': 'Rust',
            'php': 'PHP',
            'rb': 'Ruby',
            'swift': 'Swift',
            'kt': 'Kotlin',
            'scala': 'Scala',
            'sh': 'Shell',
            'ps1': 'PowerShell',
            'bat': 'Batch',
            'r': 'R',
            'jl': 'Julia',
            'html': 'HTML',
            'css': 'CSS',
            'sql': 'SQL',
            'ipynb': 'Jupyter Notebook'
        }