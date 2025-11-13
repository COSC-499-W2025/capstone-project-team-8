"""
File classification service for determining file types based on extensions.

This module provides utilities to classify files into categories
(image, code, content, unknown) based on their file extensions.
"""

from pathlib import Path
from .file_types import EXT_IMAGE, EXT_CODE, EXT_CONTENT


def classify_file(path: Path) -> str:
    """
    Classify a file based on its extension.
    
    Args:
        path: Path object representing the file
        
    Returns:
        str: One of "image", "code", "content", or "unknown"
    """
    ext = path.suffix.lower()
    if ext in EXT_IMAGE:
        return "image"
    if ext in EXT_CODE:
        return "code"
    if ext in EXT_CONTENT:
        return "content"
    return "unknown"