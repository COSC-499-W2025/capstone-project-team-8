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
import re

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
        
        # Build last-updated lookups from analysis_data if provided
        last_updated_meta = {}
        lu = analysis_data.get("analysis_meta", {}).get("last_updated") if isinstance(analysis_data.get("analysis_meta"), dict) else None
        if lu:
            # lu expected shape: {"projects": [{"project_root": "...", "project_tag": int, "last_updated": "ISO"}, ...], "overall_last_updated": "..."}"
            try:
                for entry in lu.get("projects", []) if isinstance(lu.get("projects", []), list) else []:
                    tag = entry.get("project_tag")
                    root = entry.get("project_root")
                    iso = entry.get("last_updated")
                    if tag is not None and iso:
                        last_updated_meta.setdefault("by_tag", {})[int(tag)] = iso
                    if root is not None and iso:
                        # normalize root key similar to view/transformer
                        rk = root.strip()
                        if rk in ("", ".", "./"):
                            rk = "."
                        else:
                            rk = rk.lstrip("./").rstrip("/")
                        last_updated_meta.setdefault("by_root", {})[rk] = iso
            except Exception:
                # non-fatal: ignore malformed timestamps
                last_updated_meta = {}

        with transaction.atomic():
            for project_data in projects:
                # Attach matched last-updated ISO onto project_data for _create_project to consume
                try:
                    matched_iso = None
                    pid = project_data.get("id")
                    root = str(project_data.get("root", "") or "")
                    # 1) by tag
                    if pid is not None and "by_tag" in last_updated_meta:
                        matched_iso = last_updated_meta["by_tag"].get(int(pid))
                    # 2) by root
                    if not matched_iso and root and "by_root" in last_updated_meta:
                        rk = root.strip()
                        if rk in ("", ".", "./"):
                            rk = "."
                        else:
                            rk = rk.lstrip("./").rstrip("/")
                        matched_iso = last_updated_meta["by_root"].get(rk)
                    if matched_iso:
                        project_data["_last_updated_iso"] = matched_iso
                except Exception:
                    # ignore matching errors and continue
                    pass

                project = self._create_project(
                    user=user,
                    project_data=project_data,
                    overall_data=overall,
                    upload_filename=upload_filename,
                    project_name_override=project_name_override,
                    project_summaries=analysis_data.get('project_summaries', {}),
                    send_to_llm=analysis_data.get('send_to_llm', False)
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
        project_name_override: str,
        project_summaries: Dict[int, str] = None,
        send_to_llm: bool = False
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
            # Check for both old and new name for backward compatibility
            if root and root not in ('(non-git-files)', '(non-project files)'):
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
        created_at_dt = None
        first_commit_date = None
        if created_at_timestamp:
            try:
                # Assume Unix seconds timestamp; produce tz-aware UTC datetime
                created_at_dt = dt.datetime.fromtimestamp(float(created_at_timestamp), tz=dt.timezone.utc)
                # Keep existing behavior: also use the timestamp for first_commit_date if desired
                first_commit_date = created_at_dt
            except (ValueError, TypeError, AttributeError):
                created_at_dt = None
                first_commit_date = None

        # Ensure created_at is set: default to now when payload didn't include a created_at
        if created_at_dt is None:
            created_at_dt = timezone.now()

        # Prefer explicit last-updated ISO from analyzer for updated_at if present
        updated_at_dt = None
        last_updated_iso = project_data.get("_last_updated_iso") or project_data.get("last_updated")
        if last_updated_iso:
            try:
                # Try robust parsing (datetime.fromisoformat preserves timezone if present)
                parsed = None
                try:
                    parsed = dt.datetime.fromisoformat(last_updated_iso)
                except Exception:
                    # try common fallback without microseconds/timezone
                    try:
                        parsed = dt.datetime.strptime(last_updated_iso, "%Y-%m-%dT%H:%M:%S")
                        parsed = parsed.replace(tzinfo=dt.timezone.utc)
                    except Exception:
                        parsed = None
                if parsed:
                    if parsed.tzinfo is None:
                        parsed = parsed.replace(tzinfo=dt.timezone.utc)
                    updated_at_dt = parsed
                else:
                    updated_at_dt = None
            except Exception:
                updated_at_dt = None

        # If no updated_at from payload, updated_at will be created_at_dt or now
        if updated_at_dt is None:
            updated_at_dt = created_at_dt or timezone.now()

        # Determine if this is a git repository
        project_id = project_data.get('id', 0)
        contributors = project_data.get('contributors', [])
        root = project_data.get('root', '')
        
        is_git_repo = (
            bool(project_id) and project_id > 0 and
            bool(contributors) and len(contributors) > 0 and
            root not in ('(non-git-files)', '(non-project files)')
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
            # Explicitly set created_at/updated_at from the incoming JSON timestamp when available.
            # These fields are nullable in the model so existing rows remain compatible.
            , created_at=created_at_dt
            , updated_at=updated_at_dt
        )

        project.ai_summary = project_data.get('ai_summary', '')
        project.llm_consent = project_data.get('llm_consent', False)
        if project.ai_summary:
            project.ai_summary_generated_at = timezone.now()
        
        # Save resume bullet points if available
        bullet_points = project_data.get('bullet_points', [])
        if bullet_points:
            project.resume_bullet_points = bullet_points
        
        project.save()

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
                is_primary=bool(i == 0)
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
            
            matched_user = self._find_matching_user(name, email, project.user)
            
            # Get or create contributor
            contributor, created = Contributor.objects.get_or_create(
                name=name,
                email=email,
                defaults={'user': matched_user}
            )
            
            if not created and matched_user and contributor.user_id != matched_user.id:
                contributor.user = matched_user
                contributor.save(update_fields=['user'])
            
            # Create contribution record
            ProjectContribution.objects.create(
                project=project,
                contributor=contributor,
                commit_count=contributor_info.get('commits', 0),
                lines_added=contributor_info.get('lines_added', 0),
                lines_deleted=contributor_info.get('lines_deleted', 0),
                percent_of_commits=contributor_info.get('percent_commits', 0.0)
            )
    
    def _find_matching_user(self, name: str, email: str, project_user: Optional[User] = None) -> Optional[User]:
        """
        Try to match a contributor to an existing User account.
        
        Args:
            name: Contributor name
            email: Contributor email
            
        Returns:
            User instance if match found, None otherwise
        """
        emails_to_check = self._extract_emails(email)
        
        normalized_name = name.strip() if name else None

        # Prefer linking to the uploading user when identities align
        if project_user:
            project_emails = {project_user.email.lower()}
            if project_user.github_email:
                project_emails.add(project_user.github_email.lower())
            for candidate in emails_to_check:
                if candidate.lower() in project_emails:
                    return project_user
            if normalized_name and project_user.github_username and project_user.github_username.lower() == normalized_name.lower():
                return project_user

        for candidate in emails_to_check:
            primary_match = User.objects.filter(email__iexact=candidate).first()
            if primary_match:
                return primary_match

            github_matches = User.objects.filter(github_email__iexact=candidate)
            if normalized_name:
                github_matches = github_matches.filter(github_username__iexact=normalized_name)
            github_match = github_matches.first()
            if github_match:
                return github_match

            # Fallback: if no exact github_username match, allow first github_email match
            if not normalized_name:
                loose_github_match = User.objects.filter(github_email__iexact=candidate).first()
                if loose_github_match:
                    return loose_github_match

        # Try GitHub username match if no email matches
        if normalized_name:
            username_match = User.objects.filter(github_username__iexact=normalized_name).first()
            if username_match:
                return username_match
        
        return None

    def _extract_emails(self, raw_email: str) -> List[str]:
        """Split raw email field into individual addresses."""
        if not raw_email:
            return []
        
        # Split on commas, semicolons, whitespace, and newlines
        parts = re.split(r'[\s,;]+', raw_email)
        emails = []
        for part in parts:
            candidate = part.strip()
            if candidate and '@' in candidate:
                emails.append(candidate)
        return emails
    
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