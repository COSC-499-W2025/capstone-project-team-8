from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated

from app.services.folder_upload import FolderUploadService
from app.services.database_service import ProjectDatabaseService
import tempfile
import zipfile
import os
from app.services.analysis.analyzers.skill_analyzer import analyze_project, generate_chronological_skill_detection


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
                    
                except Exception as db_error:
                    response_payload["database_warning"] = f"Analysis completed but failed to save to database: {str(db_error)}"
            else:
                response_payload["database_info"] = "Analysis completed. Sign in to save projects to your account."
            
            # Merge in skill analysis if available
            if analysis_result is not None:
                # Avoid clobbering existing keys; attach under "skill_analysis"
                response_payload["skill_analysis"] = analysis_result

            # --- NEW: build chronological skill detection if possible ---
            try:
                def _parse_tag(tag_val):
                    # Normalize tag values to integers: 1, "1", "project_1" -> 1
                    if tag_val is None:
                        return None
                    try:
                        return int(tag_val)
                    except Exception:
                        pass
                    if isinstance(tag_val, str):
                        if tag_val.isdigit():
                            return int(tag_val)
                        # match "project_123"
                        if tag_val.startswith("project_"):
                            try:
                                return int(tag_val.split("_", 1)[1])
                            except Exception:
                                return None
                    return None

                def _parse_timestamp(raw):
                    # Accept ints, digit-strings, or ISO datetimes
                    if raw is None:
                        return None
                    if isinstance(raw, (int, float)):
                        try:
                            return int(raw)
                        except Exception:
                            return None
                    if isinstance(raw, str):
                        s = raw.strip()
                        if s.isdigit():
                            try:
                                return int(s)
                            except Exception:
                                return None
                        # try ISO parse (very small, may fail for some formats)
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(s)
                            return int(dt.timestamp())
                        except Exception:
                            return None
                    return None

                project_skills = {}
                # Collect skills from "results"
                results = response_payload.get("results")
                if isinstance(results, list):
                    for item in results:
                        if not isinstance(item, dict):
                            continue
                        tag_candidate = item.get("project_tag") or item.get("project_id") or item.get("tag") or item.get("id")
                        tag = _parse_tag(tag_candidate)
                        # try fallback keys that might contain "project_1"
                        if tag is None:
                            # sometimes results use string keys like "project_1"
                            possible_keys = [k for k in item.keys() if isinstance(k, str) and k.startswith("project_")]
                            if possible_keys:
                                tag = _parse_tag(possible_keys[0])
                        if tag is None:
                            continue

                        skills = None
                        if "skills" in item and isinstance(item["skills"], dict):
                            skills = list(item["skills"].keys())
                        elif "detected_skills" in item and isinstance(item["detected_skills"], list):
                            skills = item["detected_skills"]
                        elif "skill_analysis" in item and isinstance(item["skill_analysis"], dict):
                            sa = item["skill_analysis"]
                            if isinstance(sa.get("skills"), dict):
                                skills = list(sa.get("skills").keys())
                            elif isinstance(sa, dict) and "skills" in sa and isinstance(sa["skills"], list):
                                skills = sa["skills"]
                        if skills:
                            project_skills[tag] = skills

                # Collect skills from "projects" list
                if not project_skills:
                    projects_list = response_payload.get("projects")
                    if isinstance(projects_list, list):
                        for p in projects_list:
                            if not isinstance(p, dict):
                                continue
                            tag = _parse_tag(p.get("project_tag") or p.get("project_id") or p.get("tag") or p.get("id"))
                            if tag is None:
                                continue
                            skills = None
                            if "skills" in p and isinstance(p["skills"], dict):
                                skills = list(p["skills"].keys())
                            elif "skill_analysis" in p and isinstance(p["skill_analysis"], dict):
                                sa = p["skill_analysis"]
                                if isinstance(sa.get("skills"), dict):
                                    skills = list(sa.get("skills").keys())
                            if skills:
                                project_skills[tag] = skills

                # Fallback: if we only ran analyze_project earlier, attach its skills to tag 0
                if not project_skills and analysis_result and isinstance(analysis_result, dict) and "skills" in analysis_result:
                    project_skills[0] = list(analysis_result.get("skills", {}).keys())

                # Build project_timestamps robustly from multiple possible payload locations
                project_timestamps = {}

                # 1) direct mapping
                if "project_timestamps" in response_payload and isinstance(response_payload["project_timestamps"], dict):
                    for k, v in response_payload["project_timestamps"].items():
                        parsed_k = _parse_tag(k)
                        if parsed_k is None:
                            continue
                        ts = _parse_timestamp(v)
                        # allow zero timestamps too (may be valid); if parsing fails set None
                        project_timestamps[parsed_k] = ts if ts is not None else 0

                # 2) git contributions structure: keys like "project_1"
                if not project_timestamps:
                    git_contrib = response_payload.get("git_contributions") or response_payload.get("git_contrib") or response_payload.get("git_contributions_data")
                    if isinstance(git_contrib, dict):
                        for key, val in git_contrib.items():
                            if not isinstance(val, dict):
                                continue
                            tag = _parse_tag(key)
                            if tag is None:
                                # maybe nested entry contains a tag
                                tag = _parse_tag(val.get("project_tag") or val.get("project_id") or val.get("tag"))
                            # common timestamp fields
                            ts_candidate = val.get("timestamp") or val.get("first_commit_ts") or val.get("created_at") or val.get("created") or val.get("first_seen")
                            ts = _parse_timestamp(ts_candidate)
                            if tag is not None:
                                project_timestamps[tag] = ts if ts is not None else 0

                # 3) per-item timestamps inside results/projects
                if results and isinstance(results, list):
                    for item in results:
                        if not isinstance(item, dict):
                            continue
                        tag = _parse_tag(item.get("project_tag") or item.get("project_id") or item.get("tag") or item.get("id"))
                        ts = _parse_timestamp(item.get("timestamp") or item.get("created_at") or item.get("first_commit_ts"))
                        if tag is not None and ts is not None:
                            project_timestamps.setdefault(tag, ts)

                if isinstance(response_payload.get("projects"), list):
                    for p in response_payload.get("projects"):
                        if not isinstance(p, dict):
                            continue
                        tag = _parse_tag(p.get("project_tag") or p.get("project_id") or p.get("tag") or p.get("id"))
                        ts = _parse_timestamp(p.get("timestamp") or p.get("created_at") or p.get("first_commit_ts"))
                        if tag is not None and ts is not None:
                            project_timestamps.setdefault(tag, ts)

                # If still empty, leave as empty dict; generator will treat unknown timestamps as None
                if project_skills:
                    # ensure integer keys for skills mapping too
                    project_skills = {int(k): v for k, v in project_skills.items()}

                    chrono = generate_chronological_skill_detection(project_skills, project_timestamps)
                    response_payload["chronological_skill_detection"] = chrono

            except Exception:
                # Non-fatal: don't block response if chronology fails
                pass
            # --- END new chronology logic ---

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