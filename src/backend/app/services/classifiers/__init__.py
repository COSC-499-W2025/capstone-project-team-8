"""
Classification services for files and projects.
"""

from .file_classifier import classify_file
from .project_classifier import classify_project
from .file_types import EXT_IMAGE, EXT_CODE, EXT_CONTENT

__all__ = [
    'classify_file',
    'classify_project',
    'EXT_IMAGE',
    'EXT_CODE', 
    'EXT_CONTENT'
]