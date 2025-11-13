"""
File content analyzers for different file types.
"""

from typing import Dict, Any
from pathlib import Path


def analyze_image(path: Path) -> Dict[str, Any]:
    """Analyze image files and return basic metadata."""
    try:
        size = path.stat().st_size
    except Exception:
        size = None
    return {"type": "image", "path": str(path), "size": size}


def analyze_content(path: Path) -> Dict[str, Any]:
    """Analyze text/content files (documents, etc.)."""
    try:
        text = path.read_text(errors="ignore")
        length = len(text)
    except Exception:
        length = None
    return {"type": "content", "path": str(path), "length": length}


def analyze_code(path: Path) -> Dict[str, Any]:
    """Analyze code files and return simple metrics."""
    try:
        text = path.read_text(errors="ignore")
        lines = text.count("\n") + 1
    except Exception:
        lines = None
    return {"type": "code", "path": str(path), "lines": lines}