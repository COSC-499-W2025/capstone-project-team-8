import zipfile
import tempfile
import os
from pathlib import Path

from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

import importlib


# These are the categories that a file will be classified as based off its extension
# The current system is expecting a zip files to be uploaded
# After these are scanned they would get sent to a respective analyzer
# Currently, it can only distinguish between repositories by searching them for a ".git" folder.
# Anything found within that folder would be tagged as part of that repository.
# Found projects are given two tags, one that is numeric (project_tag) and one that is human-readable (project_root).
# Project tag is increased sequentially starting at 1 for each discovered repository.
# Anything found outside of any .git folder would not receive a project tag.

EXT_IMAGE = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".tiff"}
EXT_CODE = {
    ".py", ".pyw", ".pyi",
    ".js", ".jsx", ".mjs", ".cjs",
    ".ts", ".tsx",
    ".java",".jsp",
    ".c", ".h", ".cpp", ".cc", ".cxx", ".hpp", ".hh",
    ".cs",
    ".go",
    ".rs",
    ".php", ".php3", ".php4", ".php5", ".phtml",
    ".rb",
    ".swift",
    ".kt", ".kts",
    ".scala", ".sc",
    ".sh", ".bash", ".zsh",
    ".ps1", ".psm1", ".bat", ".cmd",
    ".pl", ".pm",
    ".r",
    ".jl",
    ".hs", ".lhs",
    ".erl", ".ex", ".exs",
    ".fs", ".fsi",
    ".vb",
    ".sql",
    ".asm", ".s",
    ".groovy",
    ".dart",
    ".lua",
    ".html", ".htm", ".css",
    ".json", ".xml",
}
EXT_CONTENT = {".txt", ".md", ".doc", ".docx", ".pdf"}


def classify_file(path: Path):
    ext = path.suffix.lower()
    if ext in EXT_IMAGE:
        return "image"
    if ext in EXT_CODE:
        return "code"
    if ext in EXT_CONTENT:
        return "content"
    return "unknown"


class UploadFolderView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, format=None):
        usage = {
            "endpoint": "/api/upload-folder/",
            "method": "POST",
            "field": "file (zip archive)",
            "description": "Upload a zip file containing a folder of files. The server will extract and analyze files by type (image/content/code).",
        }
        accept = request.META.get("HTTP_ACCEPT", "")
        if "text/html" in accept:
            html = """
            <html>
                <body>
                <h1>Upload Folder</h1>
                <form method="post" enctype="multipart/form-data">
                  <input type="file" name="file" accept=".zip" />
                  <button type="submit">Upload</button>
                </form>
                <p>Note: Use POST with form field 'file' containing a zip archive.</p>
              </body>
            </html>
            """
            return HttpResponse(html)
        return JsonResponse({"usage": usage})

    def post(self, request, format=None):
        """Accept a ZIP file upload representing a folder. Extract and analyze files."""
        upload = request.FILES.get("file")
        if not upload:
            return JsonResponse({"error": "No file provided. Use 'file' form field."}, status=400)

        # Verify zip
        if not zipfile.is_zipfile(upload):
            return JsonResponse({"error": "Uploaded file is not a zip archive."}, status=400)

        # Import analyzers and project classifier here to avoid circular import problems at module import time.
        # The analyzers implementation now lives at app/services/analyzers.py
        # The project classifier implementation now lives at app/services/project_classifier.py
        analyzers = importlib.import_module("app.services.analyzers")
        project_classifier = importlib.import_module("app.services.project_classifier")

        results = []
        git_analysis = None
        projects = {}

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            # write uploaded file to disk first
            archive_path = tmpdir_path / "upload.zip"
            with open(archive_path, "wb") as f:
                for chunk in upload.chunks():
                    f.write(chunk)

            with zipfile.ZipFile(archive_path, "r") as z:
                z.extractall(tmpdir)

            # Discover git projects under the extracted tree so files can be tagged
            projects = analyzers.discover_git_projects(tmpdir_path)

            # Check for .git directory in extracted files
            git_repo_path = None
            if projects:
                # Pick the first discovered repo for top-level analysis (optional)
                git_repo_path = next(iter(projects.keys()))
                git_analysis = analyzers.analyze_git_repository(git_repo_path)

            # Faster check: is git available for blame?
            try:
                git_available = analyzers._git_bin() is not None
            except Exception:
                git_available = False

            # Walk all files and analyze
            for root, _, files in os.walk(tmpdir_path):
                for fname in files:
                    fpath = Path(root) / fname

                    # Skip .git directory contents from file analysis
                    if ".git" in fpath.parts:
                        continue

                    kind = classify_file(fpath)
                    if kind == "image":
                        res = analyzers.analyze_image(fpath)
                    elif kind == "code":
                        res = analyzers.analyze_code(fpath)
                        # Add blame if possible and file is within the chosen repo
                        if git_available and git_repo_path and git_repo_path in fpath.parents:
                            res["blame"] = analyzers.analyze_file_blame(fpath, git_repo_path)
                    elif kind == "content":
                        res = analyzers.analyze_content(fpath)
                    else:
                        res = {"type": "unknown", "path": str(fpath)}

                    if not isinstance(res, dict):
                        res = {"type": kind if kind else "unknown", "path": str(fpath)}
                    res.setdefault("type", kind if kind else "unknown")

                    # Normalize to relative POSIX path for response
                    try:
                        rel = fpath.relative_to(tmpdir_path)
                        res["path"] = Path(rel).as_posix()
                    except Exception:
                        res["path"] = fpath.name

                    results.append(res)
        
        # Post-process results to assign project tags.
        # Prefer using the authoritative `projects` mapping discovered earlier
        # (project_root Path -> numeric tag). Build a tag->relative-root mapping
        # and use it to assign both numeric `project_tag` and human-readable
        # `project_root` to results. If `projects` is empty, fall back to the
        # previous heuristic that parsed '/.git/' from result paths.
        response_data = {"results": results}
        if projects:
            projects_rel: dict[int, str] = {}
            for root_path, tag in projects.items():
                # Convert repo root to relative POSIX string for matching
                try:
                    # root_path was under tmpdir_path; we can reconstruct relative by stripping common prefix
                    # Since tmpdir_path no longer exists, rely on string replacement fallback if needed
                    # But discover_git_projects used absolute resolved paths; emulate relative by joining names from root_path
                    # Simpler: find the leaf folder name sequence beneath the temp root by scanning result paths.
                    # We will derive by picking any result path that starts with the repo leaf segment.
                    # However, we stored relative paths in results, so re-derive using the shortest common prefix in results.
                    # Easier approach: compute the last folder name sequence from root_path and find matching result prefix.
                    # In practice, root_path is tmpdir/XYZ..., so just take the final components after tmpdir.
                    pass
                except Exception:
                    pass
            # Derive relative roots directly by scanning results for .git markers (consistent with tests)
            repo_roots: dict[int, str] = {}
            # For each discovered project root, find a representative path prefix in results:
            for root_path, tag in projects.items():
                # Take the lowest-level directory name(s) under the zip by comparing to first-level result paths
                # Best-effort: choose the shortest path in results that appears to belong to this repo
                candidates = []
                for r in results:
                    p = r.get("path", "")
                    # If this was extracted under root_path, its absolute startswith root_path; we lost that relation,
                    # so approximate by looking for '<repo_name>/' prefix. Use the tail name of root_path.
                    repo_name = root_path.name
                    if p == repo_name or p.startswith(repo_name + "/"):
                        candidates.append(p.split("/")[0])
                if candidates:
                    repo_roots[tag] = min(candidates, key=len)
                else:
                    # Fallback to the leaf directory name
                    repo_roots[tag] = root_path.name

            # Assign tags to results using repo_roots prefixes
            for r in results:
                p = r.get("path", "")
                for tag, root_str in repo_roots.items():
                    if p == root_str or p.startswith(root_str + "/"):
                        r["project_tag"] = tag
                        r["project_root"] = root_str
                        break
        else:
            # Fallback heuristic if no projects discovered
            project_roots: list[str] = []
            for r in results:
                p = r.get("path", "")
                if "/.git/" in p or p.endswith("/.git") or p.endswith("/.git/HEAD"):
                    root = p.split("/.git/")[0] if "/.git/" in p else p.rsplit("/", 1)[0]
                    if root and root not in project_roots:
                        project_roots.append(root)
            for r in results:
                p = r.get("path", "")
                for root in project_roots:
                    if p == root or p.startswith(root + "/"):
                        r["project_tag"] = root
                        r["project_root"] = root
                        break

        if git_analysis:
            response_data["git_analysis"] = git_analysis

        return JsonResponse(response_data)
    
                    for tag, root_str in projects_rel.items():
                        if p == root_str or p.startswith(root_str + "/"):
                            r["project_tag"] = tag
                            r["project_root"] = root_str
                            break
            else:
                # Fallback heuristic: detect '.git' mentions in paths and assign root string as tag
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
                            # for fallback we only have root string; set both fields to it
                            r["project_tag"] = root
                            r["project_root"] = root
                            break

            # Perform project-level classification
            project_classifications = {}
            try:
                # Classify the overall zip file
                overall_classification = project_classifier.classify_project(archive_path)
                project_classifications["overall"] = overall_classification
                
                # If we found Git projects, classify each one individually
                if projects:
                    for root_path, tag in projects.items():
                        try:
                            project_class = project_classifier.classify_project(root_path)
                            project_classifications[f"project_{tag}"] = {
                                **project_class,
                                "project_root": str(root_path.relative_to(tmpdir_path)) if root_path.is_relative_to(tmpdir_path) else str(root_path),
                                "project_tag": tag
                            }
                        except Exception as e:
                            project_classifications[f"project_{tag}"] = {
                                "classification": "unknown",
                                "confidence": 0.0,
                                "error": str(e),
                                "project_root": str(root_path.relative_to(tmpdir_path)) if root_path.is_relative_to(tmpdir_path) else str(root_path),
                                "project_tag": tag
                            }
            except Exception as e:
                # If project classification fails, continue without it
                project_classifications = {
                    "overall": {
                        "classification": "unknown",
                        "confidence": 0.0,
                        "error": str(e)
                    }
                }

        return JsonResponse({
            "results": results,
            "project_classifications": project_classifications
        })

    def get(self, request, format=None):
        """Return usage or HTML form."""
        accept = request.META.get("HTTP_ACCEPT", "")
        usage = {
            "endpoint": "/api/upload-folder/",
            "method": "POST",
            "field": "file (zip archive)",
            "description": "Upload a zip file containing a folder of files. The server will extract and analyze files by type (image/content/code), discover Git repositories, tag files with project information, and classify project types (coding/writing/art/mixed).",
        }

        if "text/html" in accept:
            html = """
            <html>
              <body>
                <h1>Upload Folder</h1>
                <form method="post" enctype="multipart/form-data">
                  <input type="file" name="file" accept=".zip" />
                  <button type="submit">Upload</button>
                </form>
                <p>Note: Use POST with form field 'file' containing a zip archive. The system will analyze individual files, discover Git repositories, and classify project types.</p>
              </body>
            </html>
            """
            return HttpResponse(html)

        return JsonResponse({"usage": usage})
