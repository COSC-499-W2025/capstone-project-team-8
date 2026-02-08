"""
Feature Extractor Module

This module handles extraction of features from project directories
for use in project classification.
"""
import os
from pathlib import Path
from collections import Counter
from typing import Dict, Any, Union

from .file_type_registry import CODE_EXTS, TEXT_EXTS, IMAGE_EXTS


def extract_project_features(root_dir: Union[str, Path]) -> Dict[str, Any]:
    """
    Extract features from a project directory for classification.
    
    Args:
        root_dir: Path to the project directory
        
    Returns:
        Dictionary containing extracted features:
            - total_files: Total number of files
            - code_count: Number of code files
            - text_count: Number of text/document files
            - image_count: Number of image files
            - ext_counts: Counter of file extensions
            - folder_names: Counter of folder names (lowercase)
    """
    root_path = Path(root_dir)
    ext_counts = Counter()
    folder_names = Counter()
    total_files = 0
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Count folder names (case-insensitive)
        folder_names.update([d.lower() for d in dirnames])
        
        for filename in filenames:
            total_files += 1
            ext = os.path.splitext(filename)[1].lower()
            ext_counts[ext] += 1
    
    # Count files by category
    code_count = sum(ext_counts[ext] for ext in CODE_EXTS if ext in ext_counts)
    text_count = sum(ext_counts[ext] for ext in TEXT_EXTS if ext in ext_counts)
    image_count = sum(ext_counts[ext] for ext in IMAGE_EXTS if ext in ext_counts)
    
    return {
        'total_files': total_files,
        'code_count': code_count,
        'text_count': text_count,
        'image_count': image_count,
        'ext_counts': ext_counts,
        'folder_names': folder_names
    }
