"""
PDF text extractor using PyMuPDF (fitz).

Provides fast, reliable text extraction from PDF files.
PyMuPDF is significantly faster than alternatives and handles
complex PDFs (research papers, technical docs) well.

Installation:
    pip install PyMuPDF

Main functions:
    - read_pdf(): Extract plain text from a PDF file
    - get_pdf_metadata(): Extract PDF metadata (optional utility)
"""
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

try:
    import fitz  # PyMuPDF
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False


def read_pdf(path: Path) -> str:
    """
    Extract plain text from a PDF file using PyMuPDF.
    
    Args:
        path: Path to the PDF file on disk.
        
    Returns:
        Extracted text string. Returns empty string on error or if PyMuPDF not installed.
        
    Note:
        - Requires PyMuPDF: pip install PyMuPDF
        - Fast and memory-efficient
        - Handles Unicode and special characters well
        - Good for academic papers and technical documents
    
    Example:
        >>> from pathlib import Path
        >>> text = read_pdf(Path("research_paper.pdf"))
        >>> print(f"Extracted {len(text)} characters")
    """
    if not PDF_SUPPORT:
        logger.warning("PyMuPDF not installed. PDF text extraction unavailable.")
        return ""
    
    path = Path(path)
    
    # Validate input
    if not path.exists():
        logger.debug(f"PDF file not found: {path}")
        return ""
    
    if path.suffix.lower() != '.pdf':
        logger.debug(f"Not a PDF file: {path}")
        return ""
    
    try:
        # Open PDF document
        doc = fitz.open(str(path))
        
        text_parts = []
        
        # Extract text from each page
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Extract text with layout preservation
            # "text" mode preserves reading order
            text = page.get_text("text")
            
            if text and text.strip():
                text_parts.append(text.strip())
        
        # Close document
        doc.close()
        
        # Join pages with double newline
        full_text = '\n\n'.join(text_parts)
        
        return full_text
    
    except Exception as e:
        logger.warning(f"Failed to extract text from PDF {path}: {e}")
        return ""


def get_pdf_metadata(path: Path) -> Dict[str, Any]:
    """
    Extract metadata from a PDF file.
    
    Optional utility function for future enhancements.
    Can extract title, author, subject, keywords, creation date, etc.
    
    Args:
        path: Path to the PDF file
        
    Returns:
        Dictionary with metadata (empty dict on error)
        
    Example:
        >>> metadata = get_pdf_metadata(Path("paper.pdf"))
        >>> print(f"Title: {metadata.get('title', 'Unknown')}")
        >>> print(f"Author: {metadata.get('author', 'Unknown')}")
    """
    if not PDF_SUPPORT:
        return {}
    
    path = Path(path)
    if not path.exists() or path.suffix.lower() != '.pdf':
        return {}
    
    try:
        doc = fitz.open(str(path))
        metadata = doc.metadata or {}
        doc.close()
        return metadata
    except Exception as e:
        logger.warning(f"Failed to extract PDF metadata from {path}: {e}")
        return {}

