"""
Utils module for utility functions.
"""

from .wordDocReader import read_docx
from .pdfReader import read_pdf, PDF_SUPPORT

__all__ = [
    'read_docx',
    'read_pdf',
    'PDF_SUPPORT',
]