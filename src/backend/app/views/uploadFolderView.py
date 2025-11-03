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

# Currently anything outside of a git folder is given a project id = 0
# In the future we will implement alternative project detection methods.

EXT_IMAGE = {
    '.png', '.jpg', '.jpeg', '.svg', '.psd', '.gif', '.tiff', '.tif',
    '.bmp', '.webp', '.ico', '.raw', '.cr2', '.nef', '.arw',
    '.ai', '.eps', '.sketch', '.fig'
}
EXT_CODE = {
    '.py', '.pyw', '.pyi',
    '.js', '.jsx', '.mjs', '.cjs',
    '.ts', '.tsx',
    '.java', '.jsp',
    '.c', '.h', '.cpp', '.cc', '.cxx', '.hpp', '.hh',
    '.cs',
    '.go',
    '.rs',
    '.php', '.php3', '.php4', '.php5', '.phtml',
    '.rb',
    '.swift',
    '.kt', '.kts',
    '.scala', '.sc',
    '.sh', '.bash', '.zsh',
    '.ps1', '.psm1', '.bat', '.cmd',
    '.pl', '.pm',
    '.r',
    '.jl',
    '.hs', '.lhs',
    '.erl', '.ex', '.exs',
    '.fs', '.fsi',
    '.vb',
    '.sql',
    '.asm', '.s',
    '.groovy',
    '.dart',
    '.lua',
    '.html', '.htm', '.css',
    '.json', '.xml',
    '.ipynb',  # Jupyter notebooks
    '.yaml', '.yml',  # Configuration files
    '.toml', '.ini', '.cfg', '.conf'
}
EXT_CONTENT = {    
    '.txt', '.md', '.doc', '.docx', '.pdf', '.tex', '.bib',
    '.rtf', '.odt', '.pages',  # Additional document formats
    '.log'  # Log files
    }


def classify_file(path: Path):
    ext = path.suffix.lower()
    if ext in EXT_IMAGE:
        return "image"
    if ext in EXT_CODE:
        return "code"
    if ext in EXT_CONTENT:
        return "content"
    return "unknown"


def _transform_to_new_structure(results, projects, projects_rel, project_classifications, git_contrib_data):
    """
    Transform the collected data into the new JSON structure.
    
    Args:
        results: List of file analysis results
        projects: Dict mapping project root paths to numeric tags
        projects_rel: Dict mapping numeric tags to relative root paths
        project_classifications: Dict of project classifications
        git_contrib_data: Dict of git contribution data per project
        
    Returns:
        Dict with the new structure: {source, projects, overall}
    """
    # Initialize project data structure
    project_data = {}
    for tag, root_str in projects_rel.items():
        project_data[tag] = {
            "id": tag,
            "root": root_str,
            "classification": {},
            "files": {
                "code": [],
                "content": [],
                "image": [],
                "unknown": []
            },
            "contributors": []
        }
    
    # Check if there are files without a project_tag (unorganized files)
    has_unorganized_files = any(
        r.get("project_tag") is None 
        and not ("/.git/" in r.get("path", "") or r.get("path", "").endswith("/.git") or r.get("path", "").startswith(".git/"))
        for r in results
    )
    
    # Create a special project for unorganized files if needed
    if has_unorganized_files:
        project_data[0] = {
            "id": 0,
            "root": "(non-git-files)",  # TODO: Rename to "(unorganized-files)" in future version
            "classification": {},
            "files": {
                "code": [],
                "content": [],
                "image": [],
                "unknown": []
            },
            "contributors": []
        }
    
    # Organize files by project
    for r in results:
        file_type = r.get("type", "unknown")
        file_path = r.get("path", "")
        project_tag = r.get("project_tag")
        
        # Skip files within .git directory
        if "/.git/" in file_path or file_path.endswith("/.git") or file_path.startswith(".git/"):
            continue
        
        # Files without a project_tag go to the special unorganized files project (id=0)
        if project_tag is None and has_unorganized_files:
            project_tag = 0
        
        if project_tag in project_data:
            # Use just the filename, not the full path
            from pathlib import Path as PathLib
            filename = PathLib(file_path).name
            
            if file_type == "code":
                lines = r.get("lines")
                file_info = {"path": filename}
                if lines is not None:
                    file_info["lines"] = lines
                project_data[project_tag]["files"]["code"].append(file_info)
            elif file_type == "content":
                length = r.get("length")
                file_info = {"path": filename}
                if length is not None:
                    file_info["length"] = length
                project_data[project_tag]["files"]["content"].append(file_info)
            elif file_type == "image":
                size = r.get("size")
                file_info = {"path": filename}
                if size is not None:
                    file_info["size"] = size
                project_data[project_tag]["files"]["image"].append(file_info)
            else:
                # For unknown files, just add the filename
                project_data[project_tag]["files"]["unknown"].append(filename)
    
    # Add classification data to each project
    for tag in project_data:
        # Unorganized files (id=0) use overall classification
        if tag == 0:
            classification = project_classifications.get("overall", {})
        else:
            project_key = f"project_{tag}"
            classification = project_classifications.get(project_key, {})
        
        if classification:
            # Extract classification type (handle mixed types like "mixed:coding+writing")
            class_type = classification.get("classification", "unknown")
            
            # Build classification object
            class_obj = {
                "type": class_type,
                "confidence": round(classification.get("confidence", 0.0), 3)
            }
            
            # Add features if available
            if "features" in classification:
                features = classification["features"]
                class_obj["features"] = {
                    "total_files": features.get("total_files", 0),
                    "code": features.get("code_count", 0),
                    "text": features.get("text_count", 0),
                    "image": features.get("image_count", 0)
                }
            
            project_data[tag]["classification"] = class_obj
    
    # Add contributors to each project
    for tag in project_data:
        project_key = f"project_{tag}"
        if project_key in git_contrib_data:
            contrib_data = git_contrib_data[project_key]
            
            if "contributors" in contrib_data:
                contributors_list = []
                total_commits = contrib_data.get("total_commits", 0)
                
                for name, stats in contrib_data["contributors"].items():
                    contributor = {
                        "name": name,
                        "commits": stats.get("commits", 0),
                        "lines_added": stats.get("lines_added", 0),
                        "lines_deleted": stats.get("lines_deleted", 0),
                        "percent_commits": stats.get("percent_of_commits", 0)
                    }
                    
                    # Add email if available
                    if "email" in stats and stats["email"]:
                        contributor["email"] = stats["email"]
                    
                    contributors_list.append(contributor)
                
                # Sort by commits descending
                contributors_list.sort(key=lambda x: x["commits"], reverse=True)
                project_data[tag]["contributors"] = contributors_list
    
    # Build overall statistics
    overall_classification = project_classifications.get("overall", {})
    
    # Count real projects (exclude unorganized files project with id=0)
    total_projects = len([tag for tag in project_data.keys() if tag != 0])
    total_files = 0
    total_code_files = 0
    total_text_files = 0
    total_image_files = 0
    
    # Count all files (including those not in any project)
    for r in results:
        file_type = r.get("type", "unknown")
        # Skip .git files from the count
        if ".git/" in r.get("path", "") or r.get("path", "").endswith("/.git"):
            continue
            
        total_files += 1
        if file_type == "code":
            total_code_files += 1
        elif file_type == "content":
            total_text_files += 1
        elif file_type == "image":
            total_image_files += 1
    
    overall = {
        "classification": overall_classification.get("classification", "unknown"),
        "confidence": round(overall_classification.get("confidence", 0.0), 3),
        "totals": {
            "projects": total_projects,
            "files": total_files,
            "code_files": total_code_files,
            "text_files": total_text_files,
            "image_files": total_image_files
        }
    }
    
    # Convert project_data dict to sorted list
    # Sort by tag, but put unorganized files project (id=0) at the end
    sorted_tags = sorted([tag for tag in project_data.keys() if tag != 0])
    if 0 in project_data:
        sorted_tags.append(0)
    projects_list = [project_data[tag] for tag in sorted_tags]
    
    return {
        "source": "zip_file",
        "projects": projects_list,
        "overall": overall
    }


class UploadFolderView(APIView):
    parser_classes = (MultiPartParser, FormParser)

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
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            # write uploaded file to disk first
            archive_path = tmpdir_path / "upload.zip"
            with open(archive_path, "wb") as f:
                for chunk in upload.chunks():
                    f.write(chunk)

            with zipfile.ZipFile(archive_path, "r") as z:
                z.extractall(tmpdir)

            # Discover all projects under the extracted tree so files can be tagged
            # Currently detects Git repositories; future versions will detect other project types
            projects = analyzers.discover_all_projects(tmpdir_path)

            for root, _, files in os.walk(tmpdir):
                for fname in files:
                    fpath = Path(root) / fname
                    # Use classifier to determine category and call analyzer
                    kind = classify_file(fpath)
                    if kind == "image":
                        res = analyzers.analyze_image(fpath)
                    elif kind == "code":
                        res = analyzers.analyze_code(fpath)
                    elif kind == "content":
                        res = analyzers.analyze_content(fpath)
                    else:
                        res = {"type": "unknown", "path": str(fpath)}

                    # Guarantee a 'type' field exists (some analyzers may omit it)
                    if not isinstance(res, dict):
                        # Ensure we always append a dict
                        res = {"type": kind if kind else "unknown", "path": str(fpath)}
                    res.setdefault("type", kind if kind else "unknown")

                    # Normalize path to be relative to the extracted tmpdir so we don't leak absolute temp paths
                    try:
                        rel = fpath.relative_to(tmpdir_path)
                        # Normalize to POSIX-style path (forward slashes) for consistent matching
                        res["path"] = Path(rel).as_posix()
                    except Exception:
                        # Fallback: use the filename only
                        res.setdefault("path", fname)

                    results.append(res)

            # Post-process results to assign project tags.
            # Prefer using the authoritative `projects` mapping discovered earlier
            # (project_root Path -> numeric tag). Build a tag->relative-root mapping
            # and use it to assign both numeric `project_tag` and human-readable
            # `project_root` to results. If `projects` is empty, fall back to the
            # previous heuristic that parsed '/.git/' from result paths.
            projects_rel = {}
            if projects:
                for root_path, tag in projects.items():
                    try:
                        rel_root = root_path.relative_to(tmpdir_path)
                        root_str = Path(rel_root).as_posix()
                    except Exception:
                        # If relative conversion fails, fall back to the resolved path string
                        root_str = str(root_path)
                    projects_rel[tag] = root_str

                # assign tags using projects_rel
                for r in results:
                    p = r.get("path", "")
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

            # Also compute per-project contribution data using new service
            try:
                git_finder = importlib.import_module("app.services.gitFinder")
            except Exception:
                git_finder = None

            git_contrib_data = {}
            if git_finder and projects:
                for root_path, tag in projects.items():
                    try:
                        contrib_result = git_finder.get_git_contributors(root_path)
                        git_contrib_data[f"project_{tag}"] = contrib_result
                    except Exception as e:
                        git_contrib_data[f"project_{tag}"] = {"error": str(e)}

            # Transform the data into the new structure
            response_payload = _transform_to_new_structure(
                results, 
                projects, 
                projects_rel,
                project_classifications, 
                git_contrib_data
            )

            return JsonResponse(response_payload)

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