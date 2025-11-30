import os
import datetime
import zipfile
from pathlib import Path, PurePosixPath
from typing import Dict, List, Any, Optional

from app.services.analysis.analyzers.project_discovery import discover_projects

ROOT_MARKERS_DIRECTORIES = {".git", ".svn", ".idea", ".vscode", ".hg", ".bzr"}
ROOT_MARKERS_FILES = {
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
    "pyproject.toml",
    "requirements.txt",
    "setup.py",
    "setup.cfg",
    "package.json",
    "build.zig",
    "cargo.toml",
    "pom.xml",
    "CMakeLists.txt",
    "meson.build",
    ".project",
    ".classpath",
}


def _zipinfo_datetime_to_iso(zinfo: zipfile.ZipInfo) -> Optional[str]:
    try:
        dt = datetime.datetime(*zinfo.date_time, tzinfo=datetime.timezone.utc)
        return dt.isoformat()
    except Exception:
        return None


def compute_projects_last_updated(
    root: Optional[str] = None, zip_file: Optional[zipfile.ZipFile] = None
) -> Dict[str, Any]:
    """
    Compute last-updated timestamps.

    If `zip_file` is provided, use ZIP entry timestamps (ZipInfo.date_time) to
    determine the most recent modification per discovered project. This preserves
    original file metadata instead of using filesystem mtimes (which can change
    during extraction).

    If `zip_file` is None, fall back to scanning files under `root` on the filesystem
    and using os.stat().st_mtime as before.
    """
    results: List[Dict[str, Any]] = []
    overall_ts = 0.0

    if zip_file is not None:
        # Build structures of entries
        entries = zip_file.infolist()
        # Map normalized posix path -> ZipInfo
        zip_map = {}
        for z in entries:
            # Normalize path (strip leading ./)
            p = PurePosixPath(z.filename)
            # skip directory entries that are just '' or '.'
            zip_map[str(p)] = z

        # Discover project roots inside ZIP by looking for markers in path components
        projects = {}  # project_root (as posix str) -> tag
        tag = 1
        for z in entries:
            p = PurePosixPath(z.filename)
            parts = p.parts
            # Check directory markers in any component
            for idx, part in enumerate(parts):
                if part in ROOT_MARKERS_DIRECTORIES:
                    # project root is everything before this marker
                    proj_parts = parts[:idx]
                    proj_root = PurePosixPath(*proj_parts) if proj_parts else PurePosixPath(".")
                    proj_root_str = str(proj_root)
                    if proj_root_str not in projects:
                        projects[proj_root_str] = tag
                        tag += 1
            # Check file markers (file name matches marker)
            if parts:
                if parts[-1] in ROOT_MARKERS_FILES:
                    proj_root = PurePosixPath(*parts[:-1]) if len(parts) > 1 else PurePosixPath(".")
                    proj_root_str = str(proj_root)
                    if proj_root_str not in projects:
                        projects[proj_root_str] = tag
                        tag += 1

        # For each discovered project root, find the latest ZipInfo.date_time among entries under that root
        for proj_root_str, tag in projects.items():
            latest_ts = 0.0
            latest_iso = None
            for z in entries:
                p = PurePosixPath(z.filename)
                # treat directories: names ending with '/' still match via parts
                # normalize match: check if project root is '.' (root of zip) or if p is under proj_root
                if proj_root_str == ".":
                    under = True
                else:
                    try:
                        under = PurePosixPath(proj_root_str) in p.parents or str(p).startswith(proj_root_str + "/")
                    except Exception:
                        under = False
                if under:
                    iso = _zipinfo_datetime_to_iso(z)
                    if iso:
                        try:
                            dt = datetime.datetime.fromisoformat(iso)
                            ts = dt.timestamp()
                            if ts > latest_ts:
                                latest_ts = ts
                                latest_iso = iso
                        except Exception:
                            continue
            results.append({"project_root": proj_root_str, "project_tag": tag, "last_updated": latest_iso})
            if latest_ts > overall_ts:
                overall_ts = latest_ts

        overall_iso = None
        if overall_ts > 0:
            overall_iso = datetime.datetime.fromtimestamp(overall_ts, tz=datetime.timezone.utc).isoformat()

        return {"projects": results, "overall_last_updated": overall_iso}

    # Fallback: filesystem scanning under `root`
    if root is None:
        return {"projects": [], "overall_last_updated": None}

    root_path = Path(root).resolve()
    # Reuse existing discovery on filesystem by scanning for markers
    # Simple reuse: walk and detect markers per directory (similar to project_discovery)
    projects_fs = {}
    tag = 1
    for dirpath, dirnames, filenames in os.walk(root_path, topdown=True):
        if any(item in ROOT_MARKERS_DIRECTORIES for item in dirnames) or any(item in ROOT_MARKERS_FILES for item in filenames):
            project_root = Path(dirpath).resolve()
            proj_rel = str(project_root.relative_to(root_path)) if project_root != root_path else "."
            if proj_rel not in projects_fs:
                projects_fs[proj_rel] = tag
                tag += 1
            dirnames.clear()

    for proj_rel, tag in projects_fs.items():
        latest_ts = 0.0
        latest_iso = None
        proj_abs = root_path if proj_rel == "." else root_path / proj_rel
        for dirpath, dirnames, filenames in os.walk(proj_abs):
            for fname in filenames:
                try:
                    fpath = Path(dirpath) / fname
                    st = fpath.stat()
                    m = float(st.st_mtime)
                    if m > latest_ts:
                        latest_ts = m
                except Exception:
                    continue
        if latest_ts > 0.0:
            latest_iso = datetime.datetime.fromtimestamp(latest_ts, tz=datetime.timezone.utc).isoformat()
            overall_ts = max(overall_ts, latest_ts)
        results.append({"project_root": proj_rel, "project_tag": tag, "last_updated": latest_iso})

    overall_iso = None
    if overall_ts > 0.0:
        overall_iso = datetime.datetime.fromtimestamp(overall_ts, tz=datetime.timezone.utc).isoformat()

    return {"projects": results, "overall_last_updated": overall_iso}
