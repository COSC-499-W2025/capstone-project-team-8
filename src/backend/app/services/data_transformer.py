"""
Data Transformation Service

Handles transformation of analysis results into the structured JSON format.
This is a simple extraction of the _transform_to_new_structure function.
"""

from pathlib import Path as PathLib


def transform_to_new_structure(
        results, 
        projects, 
        projects_rel, 
        project_classifications, 
        git_contrib_data,
        project_timestamps=None,
        filter_username=None,
        ):
    """
    Transform the collected data into the new JSON structure.
    
    Args:
        results: List of file analysis results
        projects: Dict mapping project root paths to numeric tags
        projects_rel: Dict mapping numeric tags to relative root paths
        project_classifications: Dict of project classifications
        git_contrib_data: Dict of git contribution data per project
        project_timestamps: Dict mapping project tags to Unix timestamps (optional)
        filter_username: Optional GitHub username to filter contributors (optional)
        
    Returns:
        Dict with the new structure: {source, projects, overall}
    """
    if project_timestamps is None:
        project_timestamps = {}
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
                # Attach inline text preview if available (from earlier read)
                if "text" in r:
                    file_info["text"] = r.get("text")
                    if r.get("truncated"):
                        file_info["truncated"] = True
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
            
            # Add languages if available (for coding projects)
            if "languages" in classification:
                class_obj["languages"] = classification["languages"]
            
            # Add frameworks if available (for coding projects)
            if "frameworks" in classification:
                class_obj["frameworks"] = classification["frameworks"]
            
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

                if filter_username:
                    uname = filter_username.lower()

                    def _matches(u: str, c: dict) -> bool:
                        name = c["name"].lower()
                        email_local = c.get("email", "").split("@")[0].lower() if c.get("email") else ""
                        # Match full name, first token, or email local part
                        first_token = name.split()[0]
                        return (
                            u == name
                            or u == first_token
                            or (email_local and u == email_local)
                        )

                    contributors_list = [c for c in contributors_list if _matches(uname, c)]

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
    
    # Add languages and frameworks to overall if available
    if "languages" in overall_classification:
        overall["languages"] = overall_classification["languages"]
    if "frameworks" in overall_classification:
        overall["frameworks"] = overall_classification["frameworks"]

    # Summarize filtered user if requested
    user_contrib_summary = None
    if filter_username:
        total_commits_user = 0
        total_added_user = 0
        total_deleted_user = 0
        projects_with_user = []
        for proj in project_data.values():
            user_entries = proj["contributors"]
            if user_entries:
                # After filtering, list has either that user or is empty
                for c in user_entries:
                    total_commits_user += c.get("commits", 0)
                    total_added_user += c.get("lines_added", 0)
                    total_deleted_user += c.get("lines_deleted", 0)
                projects_with_user.append(
                    {
                        "project_id": proj["id"],
                        "root": proj["root"],
                        "commits": sum(c.get("commits", 0) for c in user_entries),
                        "lines_added": sum(c.get("lines_added", 0) for c in user_entries),
                        "lines_deleted": sum(c.get("lines_deleted", 0) for c in user_entries),
                    }
                )

        user_contrib_summary = {
            "username": filter_username,
            "found": len(projects_with_user) > 0,
            "projects": projects_with_user,
            "totals": {
                "commits": total_commits_user,
                "lines_added": total_added_user,
                "lines_deleted": total_deleted_user,
            },
        }
    
    # Convert project_data dict to sorted list
    # Sort by timestamp (chronologically, oldest first), then by tag as fallback
    # Put unorganized files project (id=0) at the end
    regular_projects = [tag for tag in project_data.keys() if tag != 0]
    
    # Sort by timestamp if available, otherwise by tag
    sorted_tags = sorted(
        regular_projects,
        key=lambda tag: (project_timestamps.get(tag, float('inf')), tag)
    )
    
    if 0 in project_data:
        sorted_tags.append(0)
    
    # Add timestamp to project data if available
    projects_list = []
    for tag in sorted_tags:
        project = project_data[tag]
        if tag in project_timestamps and project_timestamps[tag] > 0:
            project["created_at"] = project_timestamps[tag]
        projects_list.append(project)
    
    payload = {
        "source": "zip_file",
        "projects": projects_list,
        "overall": overall
    }
    if user_contrib_summary:
        payload["user_contributions"] = user_contrib_summary
    return payload