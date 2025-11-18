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
        
        Args:
            upload: The uploaded ZIP file
            tmpdir_path: Path to temporary directory for extraction
            
        Returns:
            Path to the extraction directory (same as tmpdir_path)
        """
        # Write uploaded file to disk first
        archive_path = tmpdir_path / "upload.zip"
        with open(archive_path, "wb") as f:
            for chunk in upload.chunks():
                f.write(chunk)
        
        # Extract the archive
        with zipfile.ZipFile(archive_path, "r") as z:
            z.extractall(tmpdir_path)
        
        return tmpdir_path
