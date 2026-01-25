from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse
from app.serializers import ErrorResponseSerializer, UploadFolderSerializer

from app.services.folder_upload import FolderUploadService
from app.services.database_service import ProjectDatabaseService
import tempfile
import zipfile
import os
from pathlib import Path
from app.services.analysis.analyzers.skill_analyzer import analyze_project, generate_chronological_skill_detection
from app.services.analysis.analyzers.last_updated import compute_projects_last_updated, extract_all_file_timestamps
import datetime


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




class UploadFolderView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    #permission_classes = [IsAuthenticated]

    @extend_schema(
        request=UploadFolderSerializer,
        responses={
            200: OpenApiResponse(description="Project uploaded and analyzed successfully"),
            400: ErrorResponseSerializer,
        },
        description="Upload a ZIP file containing projects for analysis. Requires consent flags for scanning and LLM analysis.",
        tags=["Upload"],
    )
    def post(self, request, format=None):
        """
        Accept a ZIP file upload representing a folder. Extract and analyze files.
        
        Refactored to use FolderUploadService for business logic.
        View only handles HTTP concerns (request parsing, response building).
        """
        # Extract request data
        upload = request.FILES.get("file")
        if not upload:
            return JsonResponse({"error": "No file provided. Use 'file' form field."}, status=400)
        
        github_username = request.data.get("github_username") or request.data.get("github_user")
        
        # Parse user consents
        def _parse_bool(v, default=False):
            if v is None:
                return default
            return str(v).lower() in ("1", "true", "yes", "on")

        scan_consent = _parse_bool(request.data.get("consent_scan"), default=False)
        send_to_llm = _parse_bool(request.data.get("consent_send_llm"), default=False)

        # Handle no-consent case (return minimal response without processing)
        if not scan_consent:
            minimal_payload = {
                "send_to_llm": send_to_llm,
                "scan_performed": False,
                "source": "zip_file",
                "projects": [],
                "overall": {"classification": "skipped", "confidence": 0.0, "reason": "user_declined_scan"},
                "results": [],
                "git_contributions": {}
            }
            return JsonResponse(minimal_payload)

        # Try to produce skill analysis by extracting the uploaded zip to a temp dir.
        analysis_result = None
        last_updated_info = None
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_zip_path = os.path.join(tmpdir, getattr(upload, "name", "upload.zip") or "upload.zip")
                # Save uploaded file to disk
                with open(tmp_zip_path, "wb") as out_f:
                    for chunk in upload.chunks():
                        out_f.write(chunk)
                # Extract safely to a subfolder
                extract_dir = os.path.join(tmpdir, "extracted")
                os.makedirs(extract_dir, exist_ok=True)
                try:
                    with zipfile.ZipFile(tmp_zip_path, "r") as zf:
                        zf.extractall(extract_dir)
                    
                    # Compute last-updated timestamps for discovered projects FIRST
                    last_updated_info = None
                    project_metadata = {}
                    file_timestamps = {}
                    try:
                        # Use zip metadata timestamps (ZipInfo.date_time) instead of filesystem mtimes
                        with zipfile.ZipFile(tmp_zip_path, "r") as zf_for_meta:
                            last_updated_info = compute_projects_last_updated(zip_file=zf_for_meta)
                            # Extract all individual file timestamps from ZIP
                            file_timestamps = extract_all_file_timestamps(zf_for_meta)
                        
                        # Convert last_updated_info to project_metadata format for skill_analyzer
                        if last_updated_info and "projects" in last_updated_info:
                            for proj in last_updated_info["projects"]:
                                tag = proj.get("project_tag")
                                last_updated_iso = proj.get("last_updated")
                                project_root = proj.get("project_root")
                                
                                if tag is not None and last_updated_iso:
                                    try:
                                        dt = datetime.datetime.fromisoformat(last_updated_iso.replace('Z', '+00:00'))
                                        timestamp = dt.timestamp()
                                        root_abs = str(Path(extract_dir) / project_root) if project_root and project_root != "." else extract_dir
                                        project_metadata[tag] = {
                                            "root": root_abs,
                                            "timestamp": timestamp
                                        }
                                    except Exception:
                                        pass
                            
                            # Add a root project (tag 0) for files at the root level using overall timestamp
                            # This ensures root-level files get the correct ZIP metadata timestamp instead of extraction time
                            overall_iso = last_updated_info.get("overall_last_updated")
                            if overall_iso:
                                try:
                                    dt = datetime.datetime.fromisoformat(overall_iso.replace('Z', '+00:00'))
                                    timestamp = dt.timestamp()
                                    project_metadata[0] = {
                                        "root": extract_dir,
                                        "timestamp": timestamp
                                    }
                                except Exception:
                                    pass
                    except Exception as e:
                        # non-fatal: record analyzer failure info but continue
                        pass
                    
                    # Run skill analyzer with project metadata and file timestamps for chronological ranking
                    try:
                        analysis_result = analyze_project(
                            extract_dir, 
                            project_metadata=project_metadata if project_metadata else None,
                            file_timestamps=file_timestamps if file_timestamps else None
                        )
                    except Exception as e:
                        analysis_result = {"error": f"skill analysis failed: {str(e)}"}
                    
                except zipfile.BadZipFile:
                    # Not a zip or corrupted; leave analysis_result as None
                    analysis_result = {"error": "uploaded file is not a valid zip or extraction failed"}
                # tmpdir and its contents cleaned up automatically
        except Exception as e:
            # Non-fatal: keep going to service processing but record the analyzer error
            analysis_result = {"error": f"analysis failure: {str(e)}"}

        # Delegate to service layer for business logic
        try:
            service = FolderUploadService()
            response_payload = service.process_zip(upload, github_username, send_to_llm)

            # Merge last_updated_info into the payload so the DB service can persist it
            if last_updated_info is not None:
                response_payload.setdefault("analysis_meta", {})
                response_payload["analysis_meta"]["last_updated"] = last_updated_info

            if request.user.is_authenticated:
                try:
                    db_service = ProjectDatabaseService()
                    projects = db_service.save_project_analysis(
                        user=request.user,
                        analysis_data=response_payload,
                        upload_filename=upload.name or "upload.zip"
                    )
                    
                    # Add database IDs to response
                    response_payload["saved_projects"] = [
                        {"id": project.id, "name": project.name} 
                        for project in projects
                    ]

                    # If we computed last-updated info, try to apply it to saved DB projects.
                    db_update_warnings = []
                    applied_updates = []
                    if last_updated_info:
                        # Build lookups from analyzer output:
                        tag_lookup = {}   # project_tag (int) -> iso
                        root_lookup = {}  # normalized project_root (str) -> iso

                        def _norm_root_key(s: str) -> str:
                            if s is None:
                                return ""
                            # normalize posix-ish project root keys used by analyzer
                            k = s.strip()
                            if k in (".", "", "./"):
                                return "."
                            k = k.lstrip("./")
                            if k.endswith("/"):
                                k = k[:-1]
                            return k

                        for p in last_updated_info.get("projects", []):
                            iso = p.get("last_updated")
                            tag = p.get("project_tag")
                            root = p.get("project_root")
                            if tag is not None:
                                try:
                                    tag_lookup[int(tag)] = iso
                                except Exception:
                                    pass
                            if root is not None:
                                root_lookup[_norm_root_key(root)] = iso

                        # Also allow mapping via response_payload['projects'] if present (helps match names/tags)
                        payload_project_map = {}
                        for pp in response_payload.get("projects", []) or []:
                            # project entries may contain project_tag and project_root
                            t = pp.get("project_tag")
                            r = pp.get("project_root")
                            if t is not None:
                                payload_project_map[int(t)] = _norm_root_key(r or "")

                        for project in projects:
                            try:
                                matched_iso = None
                                # 1) Match by project_tag if available
                                if getattr(project, "project_tag", None) is not None:
                                    pt = project.project_tag
                                    if pt in tag_lookup and tag_lookup[pt]:
                                        matched_iso = tag_lookup[pt]
                                # 2) Match via response payload mapping (tag -> root) then root_lookup
                                if not matched_iso and getattr(project, "project_tag", None) is not None:
                                    pt = project.project_tag
                                    root_key = payload_project_map.get(pt)
                                    if root_key and root_key in root_lookup and root_lookup[root_key]:
                                        matched_iso = root_lookup[root_key]
                                # 3) Match by project_root_path (normalize)
                                if not matched_iso and getattr(project, "project_root_path", None):
                                    ppath_key = _norm_root_key(project.project_root_path)
                                    if ppath_key in root_lookup and root_lookup[ppath_key]:
                                        matched_iso = root_lookup[ppath_key]
                                # 4) Match by project name as last resort
                                if not matched_iso and project.name:
                                    nkey = _norm_root_key(project.name)
                                    if nkey in root_lookup and root_lookup[nkey]:
                                        matched_iso = root_lookup[nkey]

                                if matched_iso:
                                    # parse ISO robustly and set updated_at
                                    try:
                                        dt = datetime.datetime.fromisoformat(matched_iso)
                                    except Exception:
                                        try:
                                            dt = datetime.datetime.strptime(matched_iso, "%Y-%m-%dT%H:%M:%S")
                                            dt = dt.replace(tzinfo=datetime.timezone.utc)
                                        except Exception:
                                            dt = None
                                    if dt is not None:
                                        if dt.tzinfo is None:
                                            dt = dt.replace(tzinfo=datetime.timezone.utc)
                                        project.updated_at = dt
                                        project.save(update_fields=["updated_at"])
                                        applied_updates.append({"project_id": project.id, "updated_at": matched_iso})
                            except Exception as e:
                                db_update_warnings.append(f"Failed to update project {getattr(project,'id', 'unknown')} updated_at: {str(e)}")
                    if applied_updates:
                        response_payload["last_updated_applied"] = applied_updates
                    if db_update_warnings:
                        response_payload.setdefault("database_warning", "")
                        if response_payload["database_warning"]:
                            response_payload["database_warning"] += " | "
                        response_payload["database_warning"] += " | ".join(db_update_warnings)
                    
                except Exception as db_error:
                    response_payload["database_warning"] = f"Analysis completed but failed to save to database: {str(db_error)}"
            else:
                response_payload["database_info"] = "Analysis completed. Sign in to save projects to your account."
            
            # Merge in skill analysis if available
            if analysis_result is not None:
                # Avoid clobbering existing keys; attach under "skill_analysis"
                response_payload["skill_analysis"] = analysis_result

            # Build ordered payload with consent metadata
            ordered_payload = {"send_to_llm": bool(send_to_llm), "scan_performed": True}
            for k, v in response_payload.items():
                if k not in ("send_to_llm", "scan_performed"):
                    ordered_payload[k] = v

            # Add requested username echo
            if github_username:
                ordered_payload["requested_username"] = github_username

            return JsonResponse(ordered_payload)
            
        except ValueError as e:
            # Handle validation errors from service
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            # Handle unexpected errors
            return JsonResponse({"error": f"Processing failed: {str(e)}"}, status=500)

    @extend_schema(
        exclude=True,  # Hide from API docs since it's just for HTML form
    )
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
                                                        <div>
                                                            <label>
                                                                <input type="checkbox" name="consent_scan" value="1" />
                                                                Allow server to scan my uploaded files
                                                            </label>
                                                        </div>
                                    <div>
                                        <label>
                                            <input type="checkbox" name="consent_send_llm" value="1" />
                                            Allow sending scanned results to LLM (consent required)
                                        </label>
                                    </div>
        <div>
            <label>
                Your Full Name (optional):
                <input type="text" name="github_username" placeholder="e.g., John Doe" />
            </label>
        </div>
                  <button type="submit">Upload</button>
                </form>
                <p>Note: Use POST with form field 'file' containing a zip archive. The system will analyze individual files, discover Git repositories, and classify project types.</p>
              </body>
            </html>
            """
            return HttpResponse(html)
        
        

        return JsonResponse({"usage": usage})