"""
Folder Upload Service - Main Orchestrator

Coordinates all upload processing steps.
Single Responsibility: Orchestration only.
"""

import tempfile
import importlib
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from django.core.files.uploadedfile import UploadedFile

from .zip_validator import ZipValidator
from .zip_extractor import ZipExtractor
from .project_discovery_service import ProjectDiscoveryService
from .file_scanner_service import FileScannerService
from app.services.data_transformer import transform_to_new_structure


class FolderUploadService:
    """
    Main orchestrator service for processing uploaded ZIP files.
    
    Responsibilities:
        - Coordinate the workflow between all services
        - Manage temporary directory lifecycle
        - Handle classification and git contribution extraction
        - Transform results to response format
    
    Process Flow:
        1. Validate ZIP file
        2. Extract to temporary directory
        3. Discover Git projects
        4. Scan and analyze files
        5. Classify projects
        6. Extract Git contributions
        7. Transform to response format
    """
    
    def __init__(self):
        """Initialize the orchestrator with all required services."""
        self.validator = ZipValidator()
        self.extractor = ZipExtractor()
        self.project_discovery = ProjectDiscoveryService()
        self.file_scanner = FileScannerService()
        
        # Lazy import project classifier
        self.project_classifier = importlib.import_module("app.services.classifiers.project_classifier")
        
        # Try to import git_contributions analyzer
        try:
            self.git_finder = importlib.import_module("app.services.analysis.analyzers.git_contributions")
        except Exception:
            self.git_finder = None
    
    def process_zip(
        self,
        upload: UploadedFile,
        github_username: Optional[str] = None,
        send_to_llm: bool = False
    ) -> Dict[str, Any]:
        """
        Main orchestrator method to process an uploaded ZIP file.
        
        This method coordinates all steps of the upload processing workflow.
        
        Args:
            upload: The uploaded ZIP file
            github_username: Optional GitHub username for filtering contributors
            
        Returns:
            Dictionary containing the processed data ready for JSON response
            
        Raises:
            ValueError: If validation fails
        """
        # Step 1: Validate
        self.validator.validate(upload)
        
        # Use temporary directory for extraction
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Step 2: Extract
            archive_path = tmpdir_path / "upload.zip"
            self.extractor.extract(upload, tmpdir_path)
            
            # Step 3: Discover projects
            projects = self.project_discovery.discover(tmpdir_path)
            
            # Build relative projects mapping
            projects_rel = self._build_projects_rel(projects, tmpdir_path)
            
            # Step 4: Scan files
            results = self.file_scanner.scan(tmpdir_path, projects, projects_rel)
            
            # Step 5: Classify projects
            project_classifications = self._classify_projects(
                archive_path, 
                projects, 
                tmpdir_path
            )
            
            # Step 6: Get Git contributors and timestamps
            git_contrib_data, project_timestamps = self._get_git_contributors(projects)
            
            # Step 7: Get timestamps for non-git projects from ZIP metadata
            zip_timestamps = self._get_zip_file_timestamps(archive_path, projects, tmpdir_path)
            # Merge with git timestamps (git timestamps take priority)
            for tag, timestamp in zip_timestamps.items():
                if tag not in project_timestamps or project_timestamps[tag] == 0:
                    project_timestamps[tag] = timestamp
            

            # Step 8: Generate AI summaries if consent given
            project_summaries = self._generate_project_summaries(
                projects, 
                tmpdir_path, 
                send_to_llm 
            )

            # Step 7b: Get end timestamps (newest files) for non-git projects from ZIP metadata
            zip_end_timestamps = self._get_zip_file_end_timestamps(archive_path, projects, tmpdir_path)
            # TODO: In future, could get git last commit timestamps here and merge (git takes priority)
            
            # Step 8: Transform results

            response_data = transform_to_new_structure(
                results,
                projects,
                projects_rel,
                project_classifications,
                git_contrib_data,
                project_timestamps,
                github_username,
                project_summaries,
                send_to_llm,
                project_end_timestamps=zip_end_timestamps

            )
            
            # Step 9: Generate resume items for each project
            from app.services.resume_item_generator import ResumeItemGenerator
            from app.services.analysis.analyzers.content_analyzer import analyze_project_content
            generator = ResumeItemGenerator()
            
            for project in response_data.get('projects', []):
                try:
                    # Extract content files for content analysis
                    content_files = []
                    files = project.get('files', {})
                    for content_file in files.get('content', []):
                        if 'text' in content_file:
                            content_files.append({
                                'path': content_file.get('path', ''),
                                'text': content_file.get('text', '')
                            })
                    
                    # Analyze content if content files are available
                    content_summary = None
                    if content_files:
                        try:
                            content_summary = analyze_project_content(content_files)
                        except Exception as e:
                            # Log but don't fail - resume generation can work without content analysis
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.debug(f"Content analysis failed for project {project.get('id')}: {e}")
                    
                    # Generate resume items with content summary
                    resume_items = generator.generate_resume_items(project, github_username, content_summary)
                    project['resume_items'] = resume_items
                except Exception as e:
                    # Log error but don't break the flow
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Failed to generate resume items for project {project.get('id')}: {e}")
                    project['resume_items'] = {'items': [], 'generated_at': 0}
            
            return response_data
    
    def _build_projects_rel(
        self, 
        projects: Dict[Path, int], 
        tmpdir_path: Path
    ) -> Dict[int, str]:
        """
        Build mapping of project tags to relative path strings.
        
        Args:
            projects: Mapping of project root paths to numeric tags
            tmpdir_path: Path to extracted directory
            
        Returns:
            Dictionary mapping numeric tags to relative root path strings
        """
        projects_rel = {}
        if projects:
            for root_path, tag in projects.items():
                try:
                    rel_root = root_path.relative_to(tmpdir_path)
                    root_str = Path(rel_root).as_posix()
                except Exception:
                    root_str = str(root_path)
                projects_rel[tag] = root_str
        return projects_rel
    
    def _classify_projects(
        self, 
        archive_path: Path, 
        projects: Dict[Path, int],
        tmpdir_path: Path
    ) -> Dict[str, Any]:
        """
        Classify the overall upload and individual projects.
        
        Args:
            archive_path: Path to the ZIP archive
            projects: Mapping of project root paths to numeric tags
            tmpdir_path: Path to extracted directory
            
        Returns:
            Dictionary of classification results
        """
        project_classifications = {}
        
        try:
            # Classify overall
            overall_classification = self.project_classifier.classify_project(archive_path)
            project_classifications["overall"] = overall_classification
            
            # Classify each Git project
            if projects:
                for root_path, tag in projects.items():
                    try:
                        project_class = self.project_classifier.classify_project(root_path)
                        project_classifications[f"project_{tag}"] = {
                            **project_class,
                            "project_root": str(root_path.relative_to(tmpdir_path)) if root_path.is_relative_to(tmpdir_path) else str(root_path),
                            "project_tag": tag
                        }
                    except Exception as e:
                        project_classifications[f"project_{tag}"] = {
                            "classification": "unknown",
                            "confidence": 0.0,
                            "error": str(e),
                            "project_root": str(root_path.relative_to(tmpdir_path)) if root_path.is_relative_to(tmpdir_path) else str(root_path),
                            "project_tag": tag
                        }
        except Exception as e:
            project_classifications = {
                "overall": {
                    "classification": "unknown",
                    "confidence": 0.0,
                    "error": str(e)
                }
            }
        
        return project_classifications
    
    def _get_git_contributors(
        self, 
        projects: Dict[Path, int]
    ) -> Tuple[Dict[str, Any], Dict[int, int]]:
        """
        Extract Git contribution data for each project.
        
        Args:
            projects: Mapping of project root paths to numeric tags
            
        Returns:
            Tuple of (contribution data dict, timestamps dict)
        """
        git_contrib_data = {}
        project_timestamps = {}
        
        if self.git_finder and projects:
            for root_path, tag in projects.items():
                try:
                    contrib_result = self.git_finder.get_git_contributors(root_path)
                    git_contrib_data[f"project_{tag}"] = contrib_result
                except Exception as e:
                    git_contrib_data[f"project_{tag}"] = {"error": str(e)}
                
                # Get timestamp
                try:
                    timestamp = self.git_finder.get_project_timestamp(root_path)
                    project_timestamps[tag] = timestamp
                except Exception:
                    project_timestamps[tag] = 0
        
        return git_contrib_data, project_timestamps
    
    def _get_zip_file_timestamps(
        self,
        zip_path: Path,
        projects: Dict[Path, int],
        tmpdir_path: Path
    ) -> Dict[int, int]:
        """
        Extract timestamps from ZIP file metadata for non-git projects.
        Finds the oldest file in each project directory based on ZIP metadata.
        
        Args:
            zip_path: Path to the ZIP file
            projects: Dict mapping project root paths to tag IDs
            tmpdir_path: Path to the temporary extraction directory
            
        Returns:
            Dict mapping project tag to Unix timestamp (oldest file in that project)
        """
        import zipfile
        from datetime import datetime
        
        project_timestamps = {}
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                # Group by project tag
                for root_path, tag in projects.items():
                    # Skip tag 0 (unorganized non-git files)
                    if tag == 0:
                        continue
                    
                    # Calculate relative path from tmpdir
                    try:
                        rel_root = root_path.relative_to(tmpdir_path)
                        project_prefix = str(rel_root).replace('\\', '/')
                    except ValueError:
                        continue
                    
                    oldest_time = None
                    
                    # Find oldest file in this project
                    for zip_info in zf.infolist():
                        if zip_info.is_dir():
                            continue
                        
                        # Normalize path separators
                        file_path = zip_info.filename.replace('\\', '/')
                        
                        # Check if file belongs to this project
                        if file_path.startswith(project_prefix + '/') or file_path == project_prefix:
                            try:
                                # Convert date_time tuple to Unix timestamp
                                # date_time is (year, month, day, hour, minute, second)
                                dt = datetime(*zip_info.date_time)
                                timestamp = int(dt.timestamp())
                                
                                if oldest_time is None or timestamp < oldest_time:
                                    oldest_time = timestamp
                            except (ValueError, OSError):
                                # Skip files with invalid timestamps
                                continue
                    
                    if oldest_time is not None:
                        project_timestamps[tag] = oldest_time
                        
        except Exception:
            # If anything fails, just return empty dict
            pass
        
        return project_timestamps
def _generate_project_summaries(self, projects, tmpdir_path, send_to_llm):
    """
    Generate AI summaries for projects if user consented to LLM.

    Args:
        projects: Dict of project paths to tags
        tmpdir_path: Path to extracted files
        send_to_llm: Boolean indicating user consent for LLM processing
    
    Returns:
        Dict mapping project tags to AI summary text
    """
    if not send_to_llm:
        return {}

    from app.services.llm.azure_client import ai_analyze
    from app.utils.prompt_loader import load_prompt_template
    import logging

    logger = logging.getLogger(__name__)
    summaries = {}

    for project_path, tag in projects.items():
        try:
            # Build context for this project
            context = self._build_summary_context(project_path, tmpdir_path)

            context_str = f"""
Project Name: {context['project_name']}
Classification: {context['classification']}
Primary Languages: {context['languages']}
Frameworks: {context['frameworks']}
Contribution Score: {context['contribution_score']}
Commit Percentage: {context['commit_percentage']}
Lines Changed Percentage: {context['lines_changed_percentage']}
Total Commits: {context['total_commits']}
Date Range: {context['first_commit_date']}
"""

            # Load prompt template
            prompt_template = load_prompt_template("project_contribution_summary")
            prompt = prompt_template.build_prompt(context_str)

            # Generate summary
            summary = ai_analyze(prompt)
            summaries[tag] = summary

        except Exception as e:
            logger.warning(f"Failed to generate summary for project {tag}: {e}")
            summaries[tag] = ""

    return summaries


def _build_summary_context(self, project_path, tmpdir_path):
    """
    Build context dict for AI summary prompt.

    Args:
        project_path: Path to the project
        tmpdir_path: Temp directory path
    
    Returns:
        Dict with project context for prompt template
    """
    try:
        rel_path = project_path.relative_to(tmpdir_path)
        project_name = str(rel_path)
    except Exception:
        project_name = project_path.name if hasattr(project_path, 'name') else "Project"

    # Minimal context - can be enhanced later
    return {
        "project_name": project_name,
        "classification": "coding",
        "languages": "Multiple",
        "frameworks": "Unknown",
        "contribution_score": "N/A",
        "commit_percentage": "N/A",
        "lines_changed_percentage": "N/A",
        "total_commits": "N/A",
        "first_commit_date": ""
    }


def _get_zip_file_end_timestamps(
    self,
    zip_path: Path,
    projects: Dict[Path, int],
    tmpdir_path: Path
) -> Dict[int, int]:
    """
    Extract end timestamps from ZIP file metadata for non-git projects.
    Finds the newest (most recent) file in each project directory based on ZIP metadata.
    
    Args:
        zip_path: Path to the ZIP file
        projects: Dict mapping project root paths to tag IDs
        tmpdir_path: Path to the temporary extraction directory
        
    Returns:
        Dict mapping project tag to Unix timestamp (newest file in that project)
    """
    import zipfile
    from datetime import datetime
    
    project_timestamps = {}
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Group by project tag
            for root_path, tag in projects.items():
                # Skip tag 0 (unorganized non-git files)
                if tag == 0:
                    continue
                
                # Calculate relative path from tmpdir
                try:
                    rel_root = root_path.relative_to(tmpdir_path)
                    project_prefix = str(rel_root).replace('\\', '/')
                except ValueError:
                    continue
                
                newest_time = None
                
                # Find newest file in this project
                for zip_info in zf.infolist():
                    if zip_info.is_dir():
                        continue
                    
                    # Normalize path separators
                    file_path = zip_info.filename.replace('\\', '/')
                    
                    # Check if file belongs to this project
                    if file_path.startswith(project_prefix + '/') or file_path == project_prefix:
                        try:
                            # Convert date_time tuple to Unix timestamp
                            dt = datetime(*zip_info.date_time)
                            timestamp = int(dt.timestamp())
                            
                            if newest_time is None or timestamp > newest_time:
                                newest_time = timestamp
                        except (ValueError, OSError):
                            continue
                
                if newest_time is not None:
                    project_timestamps[tag] = newest_time
                    
    except Exception:
        pass
    
    return project_timestamps
