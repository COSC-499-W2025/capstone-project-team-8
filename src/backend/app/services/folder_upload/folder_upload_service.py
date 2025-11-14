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
        github_username: Optional[str] = None
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
            self.extractor.extract(upload, tmpdir_path)
            
            # Step 3: Discover projects
            projects = self.project_discovery.discover(tmpdir_path)
            
            # Build relative projects mapping
            projects_rel = self._build_projects_rel(projects, tmpdir_path)
            
            # Step 4: Scan files
            results = self.file_scanner.scan(tmpdir_path, projects, projects_rel)
            
            # Step 5: Classify projects
            archive_path = tmpdir_path / "upload.zip"
            project_classifications = self._classify_projects(
                archive_path, 
                projects, 
                tmpdir_path
            )
            
            # Step 6: Get Git contributors
            git_contrib_data, project_timestamps = self._get_git_contributors(projects)
            
            # Step 7: Transform results
            response_data = transform_to_new_structure(
                results,
                projects,
                projects_rel,
                project_classifications,
                git_contrib_data,
                project_timestamps,
                github_username
            )
            
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
