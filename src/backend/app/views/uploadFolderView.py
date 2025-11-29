from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated

from app.services.folder_upload import FolderUploadService
from app.services.database_service import ProjectDatabaseService
import tempfile
import zipfile
import os
from app.services.analysis.analyzers.skill_analyzer import analyze_project
from app.services.analysis.analyzers.last_updated import compute_projects_last_updated
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
                    # Run skill analyzer on the extracted content
                    analysis_result = analyze_project(extract_dir)

                    # Compute last-updated timestamps for discovered projects (best-effort)
                    try:
                        # Use zip metadata timestamps (ZipInfo.date_time) instead of filesystem mtimes
                        with zipfile.ZipFile(tmp_zip_path, "r") as zf_for_meta:
                            last_updated_info = compute_projects_last_updated(zip_file=zf_for_meta)
                    except Exception as e:
                        # non-fatal: record analyzer failure info in analysis_result
                        if not isinstance(analysis_result, dict):
                            analysis_result = {}
                        analysis_result.setdefault("last_updated_error", str(e))
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
            response_payload = service.process_zip(upload, github_username)
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
                    if last_updated_info:
                        # Build a lookup mapping project_root -> last_updated ISO string
                        lookup = {p["project_root"]: p.get("last_updated") for p in last_updated_info.get("projects", [])}
                        for project in projects:
                            try:
                                # Try several matching strategies:
                                possible_keys = []
                                if project.project_root_path:
                                    possible_keys.append(project.project_root_path)
                                # Some payloads store plain project_root in response_payload['projects']
                                # Try matching by name as fallback
                                possible_keys.append(project.name)
                                matched_iso = None
                                for key in possible_keys:
                                    if key in lookup and lookup[key]:
                                        matched_iso = lookup[key]
                                        break
                                if matched_iso:
                                    # parse ISO and set project's updated_at
                                    try:
                                        dt = datetime.datetime.fromisoformat(matched_iso)
                                    except Exception:
                                        # fallback: try parsing without timezone and assume UTC
                                        dt = datetime.datetime.strptime(matched_iso, "%Y-%m-%dT%H:%M:%S")
                                        dt = dt.replace(tzinfo=datetime.timezone.utc)
                                    if dt.tzinfo is None:
                                        dt = dt.replace(tzinfo=datetime.timezone.utc)
                                    project.updated_at = dt
                                    project.save(update_fields=["updated_at"])
                            except Exception as e:
                                db_update_warnings.append(f"Failed to update project {project.id} updated_at: {str(e)}")
                    if db_update_warnings:
                        response_payload.setdefault("database_warning", "")
                        response_payload["database_warning"] += " | ".join(db_update_warnings)
                    
                except Exception as db_error:
                    response_payload["database_warning"] = f"Analysis completed but failed to save to database: {str(db_error)}"
            else:
                response_payload["database_info"] = "Analysis completed. Sign in to save projects to your account."
            
            # Merge in skill analysis if available
            if analysis_result is not None:
                # Avoid clobbering existing keys; attach under "skill_analysis"
                response_payload["skill_analysis"] = analysis_result

            # Attach last-updated info to the response payload (if available)
            if last_updated_info is not None:
                response_payload["last_updated"] = last_updated_info

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