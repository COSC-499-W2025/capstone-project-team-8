"""
ZIP File Extractor Service

Responsible for extracting ZIP archives to temporary directories.
Single Responsibility: Extraction only.
"""

import zipfile
from pathlib import Path
from django.core.files.uploadedfile import UploadedFile


class ZipExtractor:
    """
    Service for extracting ZIP file uploads.
    
    Responsibilities:
        - Write uploaded file to disk
        - Extract ZIP contents to specified directory
        - Preserve directory structure
    """
    
    def extract(self, upload: UploadedFile, tmpdir_path: Path) -> Path:
        """
        Extract ZIP archive to temporary directory.
        
        The ZIP file is stored in a separate 'archive' subdirectory to prevent
        it from being included in file scans of the extracted content.
        
        Args:
            upload: The uploaded ZIP file
            tmpdir_path: Path to temporary directory for extraction
            
        Returns:
            Path to the extraction directory (content subdirectory)
        """
        # Create separate directories for archive and extracted content
        archive_dir = tmpdir_path / "archive"
        content_dir = tmpdir_path / "content"
        archive_dir.mkdir(exist_ok=True)
        content_dir.mkdir(exist_ok=True)
        
        # Write uploaded file to archive directory (separate from extracted files)
        archive_path = archive_dir / "upload.zip"
        with open(archive_path, "wb") as f:
            for chunk in upload.chunks():
                f.write(chunk)
        
        # Extract the archive to content directory
        with zipfile.ZipFile(archive_path, "r") as z:
            z.extractall(content_dir)
        
        return content_dir
