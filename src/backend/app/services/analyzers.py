from pathlib import Path
from typing import Dict, Any, Optional
import os


def analyze_image(path: Path) -> Dict[str, Any]:
    # Placeholder image analysis - return basic metadata
    try:
        size = path.stat().st_size
    except Exception:
        size = None
    return {"type": "image", "path": str(path), "size": size}


def analyze_content(path: Path) -> Dict[str, Any]:
    # Placeholder content analysis (text/word)
    try:
        text = path.read_text(errors="ignore")
        length = len(text)
    except Exception:
        length = None
    return {"type": "content", "path": str(path), "length": length}


def analyze_code(path: Path) -> Dict[str, Any]:
    # Placeholder code analysis - return simple metrics
    try:
        text = path.read_text(errors="ignore")
        lines = text.count("\n") + 1
    except Exception:
        lines = None
    return {"type": "code", "path": str(path), "lines": lines}


def discover_git_projects(root: Path) -> Dict[Path, int]:
    """Scan `root` for `.git` directories. Return a mapping of project_root -> tag_id.

    The project_root is the directory that contains the `.git` folder (i.e. the repository root).
    Tags are assigned sequentially starting at 1 in discovery order.
    """
    projects: Dict[Path, int] = {}
    tag = 1
    for dirpath, dirnames, _ in os.walk(root):
        # Look for a `.git` subdirectory
        if ".git" in dirnames:
            project_root = Path(dirpath)
            # Normalize path for consistent comparisons
            project_root = project_root.resolve()
            if project_root not in projects:
                projects[project_root] = tag
                tag += 1
            # avoid descending into `.git` itself
            try:
                dirnames.remove(".git")
            except ValueError:
                pass
    return projects


def find_project_tag_for_path(path: Path, projects: Dict[Path, int]) -> Optional[int]:
    """Given a file `path` and a dict of project roots -> tag, return the tag for the nearest ancestor project.

    If the file is not under any discovered project root, return None.
    """
    path = path.resolve()
    best_tag: Optional[int] = None
    best_len = -1

    # Match any project root that is an ancestor of the path (this includes .git children)
    # Use Path.is_relative_to when available for clarity and performance.
    for root, tag in projects.items():
        try:
            try:
                is_rel = path.is_relative_to(root)
            except AttributeError:
                # Python <3.9 fallback
                try:
                    path.relative_to(root)
                    is_rel = True
                except Exception:
                    is_rel = False

            if is_rel:
                # choose the deepest (longest) matching root
                l = len(str(root))
                if l > best_len:
                    best_len = l
                    best_tag = tag
        except Exception:
            # ignore any filesystem/permission errors and continue
            continue

    return best_tag
