"""
File Scanner Service

Responsible for scanning and analyzing all files in a directory tree.
Single Responsibility: File scanning and analysis only.
"""

import os
from pathlib import Path
from typing import Dict, List, Any

from app.services.classifiers import classify_file
from app.services.utils import read_docx, read_pdf


class FileScannerService:
    """
    Service for scanning and analyzing files.
    
    Responsibilities:
        - Walk directory tree
        - Classify each file by type
        - Analyze files using appropriate analyzers
        - Normalize file paths
        - Assign project tags to files
    """
    
    # Directories to exclude from scanning
    EXCLUDED_DIRS = {
        'node_modules', '__pycache__', 'venv', 'env',
        'dist', 'build', '.next', '.nuxt', 'vendor', 'target',
        'coverage', '.pytest_cache', '.mypy_cache', '.venv',
        '.tox', '.eggs', '*.egg-info', '.gradle', 'out',
        'bin', 'obj', '.vs', '.idea', '.vscode',
    }
    
    def __init__(self):
        """Initialize with required analyzers."""
        from app.services.analysis import analyzers
        self.analyzers = analyzers
    
    def scan(
        self, 
        tmpdir_path: Path, 
        projects: Dict[Path, int],
        projects_rel: Dict[int, str]
    ) -> List[Dict[str, Any]]:
        """
        Scan all files in the directory and analyze them.
        
        Args:
            tmpdir_path: Path to extracted directory
            projects: Mapping of project root paths to numeric tags
            projects_rel: Mapping of numeric tags to relative root paths
            
        Returns:
            List of analysis results for each file
        """
        results = []
        
        for root, dirs, files in os.walk(tmpdir_path):
            # Filter out excluded directories IN-PLACE (prevents descending into them)
            dirs[:] = [d for d in dirs if d not in self.EXCLUDED_DIRS]
            
            for fname in files:
                fpath = Path(root) / fname
                
                # Classify file type
                kind = classify_file(fpath)
                
                # Analyze based on type
                if kind == "image":
                    res = self.analyzers.analyze_image(fpath)
                elif kind == "code":
                    res = self.analyzers.analyze_code(fpath)
                elif kind == "content":
                    res = self.analyzers.analyze_content(fpath)
                else:
                    res = {"type": "unknown", "path": str(fpath)}
                
                # Ensure result is a dict with type field
                if not isinstance(res, dict):
                    res = {"type": kind if kind else "unknown", "path": str(fpath)}
                res.setdefault("type", kind if kind else "unknown")
                
                # Normalize path to be relative
                try:
                    rel = fpath.relative_to(tmpdir_path)
                    res["path"] = Path(rel).as_posix()
                except Exception:
                    res.setdefault("path", fname)
                
                # For content files, attach the text
                if res.get("type") == "content":
                    try:
                        real_path = tmpdir_path / Path(res.get("path"))
                        if real_path.suffix.lower() == ".docx":
                            text = read_docx(real_path)
                        elif real_path.suffix.lower() == ".pdf":
                            text = read_pdf(real_path)
                        else:
                            text = real_path.read_text(errors="ignore")
                        
                        # Cap size
                        MAX_TEXT = 20000
                        if len(text) > MAX_TEXT:
                            res["text"] = text[:MAX_TEXT]
                            res["truncated"] = True
                        else:
                            res["text"] = text
                    except Exception:
                        pass
                
                results.append(res)
        
        # Assign project tags
        self._assign_project_tags(results, projects, projects_rel, tmpdir_path)
        
        return results
    
    def _assign_project_tags(
        self, 
        results: List[Dict], 
        projects: Dict[Path, int],
        projects_rel: Dict[int, str],
        tmpdir_path: Path
    ) -> None:
        """
        Assign project tags to results based on discovered projects.
        
        Args:
            results: List of file analysis results (modified in place)
            projects: Mapping of project root paths to numeric tags
            projects_rel: Mapping of numeric tags to relative root paths
            tmpdir_path: Path to extracted directory
        """
        if projects:
            # Use authoritative projects mapping
            for r in results:
                p = r.get("path", "")
                for tag, root_str in projects_rel.items():
                    if p == root_str or p.startswith(root_str + "/"):
                        r["project_tag"] = tag
                        r["project_root"] = root_str
                        break
        else:
            # Fallback heuristic: detect .git in paths
            project_roots = []
            for r in results:
                p = r.get("path", "")
                if "/.git/" in p or p.endswith("/.git") or p.endswith("/.git/HEAD"):
                    root = p.split("/.git/")[0] if "/.git/" in p else p.rsplit("/", 1)[0]
                    if root not in project_roots:
                        project_roots.append(root)
            
            for r in results:
                p = r.get("path", "")
                for root in project_roots:
                    if p == root or p.startswith(root + "/"):
                        r["project_tag"] = root
                        r["project_root"] = root
                        break
