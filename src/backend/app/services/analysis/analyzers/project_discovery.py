"""
Project discovery utilities for finding project roots and organizing files.
"""

import os
from typing import Dict, Optional
from pathlib import Path


def discover_projects(root: Path) -> Dict[Path, int]:
    """Scan `root` for project root markers. Return a mapping of project_root -> tag_id.

    The project_root is the directory that contains a project root marker (i.e. the repository root).
    Tags are assigned sequentially starting at 1 in discovery order.
    """
    ROOT_MARKERS_DIRECTORIES = [".git", ".svn", ".idea", ".vscode", ".hg", ".bzr"]
    ROOT_MARKERS_FILES = [
        ".env",
        ".env.example",
        "README.md",
        "README",
        "README.txt",
        "readme.txt",
        "Readme.txt",
        "Makefile",
        "docker-compose.yml",
        "docker-compose.yaml",
        "LICENSE",
        "COPYING",
        "pyproject.toml",  # Python
        "requirements.txt",  # Python
        "setup.py",  # Python
        "setup.cfg",  # Python
        "package.json",  # nodejs
        "build.zig",  # Zig
        "cargo.toml",  # Rust
        "pom.xml",  # Java
        "CMakeLists.txt",  # CMake/C/C++
        "meson.build",  # Meson/C/C++
    ]
    projects: Dict[Path, int] = {}
    tag = 1
    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        if any(item in ROOT_MARKERS_DIRECTORIES for item in dirnames) or any(
            item in ROOT_MARKERS_FILES for item in filenames
        ):
            project_root = Path(dirpath)
            project_root = project_root.resolve() # Normalize path for consistent comparisons
            if project_root not in projects:
                projects[project_root] = tag
                tag += 1
            dirnames.clear() # If this folder is a project do not descend any further
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