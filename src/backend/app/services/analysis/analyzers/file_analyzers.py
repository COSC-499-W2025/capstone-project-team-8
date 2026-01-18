"""
File content analyzers for different file types.
"""

from typing import Dict, Any
from pathlib import Path
from fnmatch import fnmatch
from app.services.analysis.analyzers import project_metadata

DEFAULT_IGNORES = set(project_metadata.DEFAULT_IGNORES)

def _is_ignored(path: Path) -> bool:
    """
    Determine whether a path should be ignored:
    - If any path part matches a DEFAULT_IGNORES entry
    - If an ancestor directory contains a .gitignore and the relative path matches any pattern
    This is intentionally lightweight (uses fnmatch and substring checks) to avoid heavy processing.
    """
    try:
        for part in path.parts:
            if part in DEFAULT_IGNORES:
                return True

        # walk up to find .gitignore files and test patterns relative to that directory
        for parent in [path] + list(path.parents):
            gitignore = parent / ".gitignore"
            if gitignore.exists():
                try:
                    raw = gitignore.read_text(errors="ignore")
                except Exception:
                    continue
                rel = None
                try:
                    rel = str(path.relative_to(parent))
                except Exception:
                    rel = str(path)
                for line in raw.splitlines():
                    pat = line.strip()
                    if not pat or pat.startswith("#"):
                        continue
                    # treat directory patterns (ending with /) specially
                    if pat.endswith("/"):
                        if any(p == pat.rstrip("/") for p in path.parts):
                            return True
                    # try fnmatch against the relative path and filename
                    if fnmatch(rel, pat) or fnmatch(path.name, pat) or pat in rel:
                        return True
        return False
    except Exception:
        # On error, be conservative and do not ignore
        return False


def analyze_image(path: Path) -> Dict[str, Any]:
    """Analyze image files and return basic metadata."""
    if _is_ignored(path):
        # avoid expensive stat for ignored files if desired; still return minimal info
        return {"type": "image", "path": str(path), "size": None, "bytes": None, "skipped": True}
    try:
        size = path.stat().st_size
    except Exception:
        size = None
    return {"type": "image", "path": str(path), "size": size, "bytes": size}


def analyze_content(path: Path) -> Dict[str, Any]:
    """Analyze text/content files (documents, etc.)."""
    if _is_ignored(path):
        # skip heavy text reads for ignored files
        return {"type": "content", "path": str(path), "length": None, "chars": None, "bytes": None, "lines": None, "skipped": True}
    try:
        text = path.read_text(errors="ignore")
        length = len(text)
        file_size = path.stat().st_size
        lines = text.count("\n") + 1 if text else 0
        # small-file heuristic: skip empty or very short text files (<5 lines)
        if lines > 0 and lines < 5:
            return {"type": "content", "path": str(path), "length": length, "chars": length, "bytes": file_size, "lines": lines, "skipped": True, "reason": "too_few_lines"}
    except Exception:
        length = None
        file_size = None
        lines = None
    return {"type": "content", "path": str(path), "length": length, "chars": length, "bytes": file_size, "lines": lines}


def analyze_code(path: Path) -> Dict[str, Any]:
    """Analyze code files and return simple metrics."""
    if _is_ignored(path):
        # skip heavy reads/counts for ignored files
        return {"type": "code", "path": str(path), "lines": None, "chars": None, "bytes": None, "skipped": True}
    try:
        text = path.read_text(errors="ignore")
        lines = text.count("\n") + 1
        length = len(text)
        file_size = path.stat().st_size
        # skip empty or very small code files (<5 lines)
        if lines == 0 or lines < 5:
            return {"type": "code", "path": str(path), "lines": lines, "chars": length, "bytes": file_size, "skipped": True, "reason": "too_few_lines"}
    except Exception:
        lines = None
        length = None
        file_size = None
    return {"type": "code", "path": str(path), "lines": lines, "chars": length, "bytes": file_size}