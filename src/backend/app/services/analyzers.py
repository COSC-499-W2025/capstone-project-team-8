import subprocess
from typing import Dict, Any, Optional
from pathlib import Path
import os
import shutil


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


def _git_bin() -> Optional[str]:
    """Return path to git executable from GIT_BIN env or PATH."""
    return os.environ.get("GIT_BIN") or shutil.which("git")


def analyze_git_repository(path: Path) -> Dict[str, Any]:
    """
    Analyze a git repository to extract contribution information.
    Returns contributor stats, commit history, and file blame information.
    """
    git = _git_bin()
    if not git:
        return {
            "type": "git",
            "error": "git not available. Install git or set GIT_BIN to the git executable.",
        }

    try:
        # Check if .git directory exists
        git_dir = path / ".git"
        if not git_dir.exists():
            return {"type": "git", "error": "Not a git repository"}

        # Change to repository directory
        repo_path = str(path)

        # Get commit statistics per author
        result = subprocess.run(
            ["git", "-C", repo_path, "shortlog", "-sn", "--all"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return {"type": "git", "error": "Failed to read git log"}

        # Parse commit counts
        contributors = []
        for line in result.stdout.strip().split("\n"):
            s = line.strip()
            if not s:
                continue
            parts = s.split("\t", 1)
            if len(parts) == 2:
                try:
                    commits = int(parts[0].strip())
                except ValueError:
                    continue
                contributors.append({"commits": commits, "author": parts[1]})

        # Get total file count and lines changed per author
        stats_result = subprocess.run(
            [
                "git",
                "-C",
                repo_path,
                "log",
                "--all",
                "--numstat",
                "--pretty=format:%an",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        author_stats: Dict[str, Any] = {}
        current_author: Optional[str] = None

        for line in stats_result.stdout.split("\n"):
            s = line.strip()
            if not s:
                continue

            # Check if line is an author name (no tabs)
            if "\t" not in s:
                current_author = s
                author_stats.setdefault(
                    current_author,
                    {"lines_added": 0, "lines_deleted": 0, "files_changed": set()},
                )
            elif current_author:
                # Parse numstat line: added\tdeleted\tfilename
                parts = s.split("\t")
                if len(parts) == 3:
                    added, deleted, filename = parts
                    if added != "-" and deleted != "-":
                        author_stats[current_author]["lines_added"] += int(added)
                        author_stats[current_author]["lines_deleted"] += int(deleted)
                        author_stats[current_author]["files_changed"].add(filename)

        # Convert sets to counts
        for a in list(author_stats.keys()):
            author_stats[a]["files_changed"] = len(author_stats[a]["files_changed"])

        return {
            "type": "git",
            "path": str(path),
            "contributors": contributors,
            "author_stats": author_stats,
            "total_contributors": len(contributors),
        }

    except subprocess.TimeoutExpired:
        return {"type": "git", "error": "Git analysis timed out"}
    except Exception as e:
        return {"type": "git", "error": f"Git analysis failed: {str(e)}"}


def analyze_file_blame(file_path: Path, repo_path: Path) -> Dict[str, Any]:
    """
    Get git blame information for a specific file to show line-by-line contributions.
    """
    git = _git_bin()
    if not git:
        return {
            "error": "git not available. Install git or set GIT_BIN to the git executable."
        }

    try:
        rel = str(file_path.relative_to(repo_path))
        result = subprocess.run(
            [git, "-C", str(repo_path), "blame", "--line-porcelain", rel],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return {"error": "Failed to get blame information"}

        # Parse blame output
        author_lines: Dict[str, int] = {}
        for line in result.stdout.split("\n"):
            if line.startswith("author "):
                author = line[7:]
                author_lines[author] = author_lines.get(author, 0) + 1

        return {"type": "blame", "file": str(file_path), "contributions": author_lines}
    except subprocess.TimeoutExpired:
        return {"error": "Blame analysis timed out"}

    except Exception as e:
        return {"error": f"Blame analysis failed: {str(e)}"}


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
    for dirpath, dirnames, filenames in os.walk(root):
        # Look for a `.git` subdirectory
        if any(item in ROOT_MARKERS_DIRECTORIES for item in dirnames) or any(
            item in ROOT_MARKERS_FILES for item in filenames
        ):
            project_root = Path(dirpath)
            # Normalize path for consistent comparisons
            project_root = project_root.resolve()
            if project_root not in projects:
                projects[project_root] = tag
                tag += 1
            # avoid descending into `.git` or other version control folders
            try:
                dirnames.remove(".git")
            except ValueError:
                pass
            try:
                dirnames.remove(".svn")
            except ValueError:
                pass
            try:
                dirnames.remove(".hg")
            except ValueError:
                pass
            try:
                dirnames.remove(".bzr")
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
