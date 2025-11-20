"""
Project Discovery Service

Responsible for discovering Git repositories within extracted directories.
Single Responsibility: Project/repository discovery only.
"""

from pathlib import Path
from typing import Dict


class ProjectDiscoveryService:
    """
    Service for discovering Git projects in a directory tree.
    
    Responsibilities:
        - Find all .git directories
        - Assign numeric tags to each project
        - Return mapping of project paths to tags
    """
    
    def discover(self, tmpdir_path: Path) -> Dict[Path, int]:
        """
        Discover Git projects in the extracted directory.
        
        Args:
            tmpdir_path: Path to extracted directory
            
        Returns:
            Dictionary mapping project root paths to numeric tags
            Example: {Path('/tmp/project1'): 1, Path('/tmp/project2'): 2}
        """
        # Import the existing analyzer to reuse the logic
        from app.services.analysis import analyzers
        
        return analyzers.discover_projects(tmpdir_path)
