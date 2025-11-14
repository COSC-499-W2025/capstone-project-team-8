"""
ZIP File Validator Service

Responsible for validating that uploaded files are valid ZIP archives.
Single Responsibility: Validation only.
"""

import zipfile
from typing import Union
from django.core.files.uploadedfile import UploadedFile


class ZipValidator:
    """
    Service for validating ZIP file uploads.
    
    Responsibilities:
        - Check if uploaded file exists
        - Verify file is a valid ZIP archive
        - Raise appropriate errors for invalid files
    """
    
    def validate(self, upload: Union[UploadedFile, None]) -> bool:
        """
        Validate that the uploaded file is a valid ZIP archive.
        
        Args:
            upload: The uploaded file from Django request
            
        Returns:
            True if valid ZIP file
            
        Raises:
            ValueError: If file is None or not a valid ZIP archive
        """
        if not upload:
            raise ValueError("No file provided")
        
        if not zipfile.is_zipfile(upload):
            raise ValueError("Uploaded file is not a zip archive")
        
        return True
