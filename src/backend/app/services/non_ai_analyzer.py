"""
Non-AI Analysis Service

Generates resume items, summaries, and statistics from project metadata
without using any LLM/AI services. Uses templates and heuristics to create
human-readable analysis.
"""

from typing import Dict, Any, List, Optional
from collections import Counter


def generate_resume_items(project_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate resume-style bullet points for each project.
    
    Args:
        project_data: The structured project data from the upload endpoint
        
    Returns:
        List of resume items, each containing:
        - project_id: The project ID
        - project_name: The project root/name
        - bullets: List of resume-style bullet point strings
    """
    resume_items = []
    
    for project in project_data.get("projects", []):
        project_id = project.get("id", 0)
        project_name = project.get("root", "Unknown Project")
        classification = project.get("classification", {})
        files = project.get("files", {})
        contributors = project.get("contributors", [])
        
        bullets = []
        
        # Skip the unorganized files project (id=0)
        if project_id == 0:
            continue
        
        # Get project type
        project_type = classification.get("type", "unknown")
        languages = classification.get("languages", [])
        frameworks = classification.get("frameworks", [])
        features = classification.get("features", {})
        
        # Generate project type description
        if project_type == "coding":
            type_desc = "Software Development Project"
        elif project_type == "writing":
            type_desc = "Writing Project"
        elif project_type == "art":
            type_desc = "Art/Design Project"
        elif project_type.startswith("mixed:"):
            types = project_type.replace("mixed:", "").split("+")
            type_desc = " + ".join([t.capitalize() for t in types]) + " Project"
        else:
            type_desc = "Project"
        
        # Main bullet point
        main_bullet = f"Developed {type_desc}: {project_name}"
        bullets.append(main_bullet)
        
        # Add technology stack information for coding projects
        if project_type == "coding" or (project_type.startswith("mixed:") and "coding" in project_type):
            if languages:
                lang_str = ", ".join(languages[:3])  # Top 3 languages
                if len(languages) > 3:
                    lang_str += f" and {len(languages) - 3} more"
                bullets.append(f"• Implemented using {lang_str}")
            
            if frameworks:
                framework_str = ", ".join(frameworks[:3])  # Top 3 frameworks
                if len(frameworks) > 3:
                    framework_str += f" and {len(frameworks) - 3} more"
                bullets.append(f"• Utilized {framework_str} frameworks and libraries")
        
        # Add file statistics
        code_files = files.get("code", [])
        total_lines = sum(f.get("lines", 0) for f in code_files)
        if total_lines > 0:
            bullets.append(f"• Wrote {total_lines:,} lines of code across {len(code_files)} files")
        
        # Add contribution statistics if available
        if contributors:
            # Find primary contributor (highest commits)
            primary_contrib = contributors[0] if contributors else None
            if primary_contrib:
                commits = primary_contrib.get("commits", 0)
                lines_added = primary_contrib.get("lines_added", 0)
                if commits > 0:
                    bullets.append(f"• Contributed {commits} commits with {lines_added:,} lines added")
        
        # Add project scale information
        total_files = features.get("total_files", 0)
        if total_files > 0:
            bullets.append(f"• Managed project with {total_files} files")
        
        resume_items.append({
            "project_id": project_id,
            "project_name": project_name,
            "bullets": bullets
        })
    
    return resume_items


def generate_summary(project_data: Dict[str, Any]) -> str:
    """
    Generate a narrative summary of all projects.
    
    Args:
        project_data: The structured project data from the upload endpoint
        
    Returns:
        A string containing a human-readable summary
    """
    projects = project_data.get("projects", [])
    overall = project_data.get("overall", {})
    
    # Filter out unorganized files project
    real_projects = [p for p in projects if p.get("id", 0) != 0]
    
    if not real_projects:
        return "No projects detected in the uploaded files."
    
    # Build summary paragraphs
    summary_parts = []
    
    # Overall statistics
    totals = overall.get("totals", {})
    num_projects = totals.get("projects", len(real_projects))
    num_files = totals.get("files", 0)
    num_code_files = totals.get("code_files", 0)
    
    summary_parts.append(
        f"This portfolio contains {num_projects} project{'s' if num_projects != 1 else ''} "
        f"with a total of {num_files} files, including {num_code_files} code files."
    )
    
    # Project type breakdown
    project_types = Counter()
    for project in real_projects:
        classification = project.get("classification", {})
        proj_type = classification.get("type", "unknown")
        project_types[proj_type] += 1
    
    if len(project_types) == 1:
        proj_type = list(project_types.keys())[0]
        if proj_type == "coding":
            summary_parts.append("All projects are software development projects.")
        elif proj_type == "writing":
            summary_parts.append("All projects are writing projects.")
        elif proj_type == "art":
            summary_parts.append("All projects are art/design projects.")
    else:
        type_descriptions = []
        for ptype, count in project_types.most_common():
            if ptype == "coding":
                type_descriptions.append(f"{count} software development")
            elif ptype == "writing":
                type_descriptions.append(f"{count} writing")
            elif ptype == "art":
                type_descriptions.append(f"{count} art/design")
            elif ptype.startswith("mixed:"):
                type_descriptions.append(f"{count} mixed-type")
        
        if type_descriptions:
            summary_parts.append(
                f"The portfolio includes {', '.join(type_descriptions)} project{'s' if sum(project_types.values()) != 1 else ''}."
            )
    
    # Technology stack information
    overall_languages = overall.get("languages", [])
    overall_frameworks = overall.get("frameworks", [])
    
    if overall_languages:
        lang_str = ", ".join(overall_languages[:5])  # Top 5
        if len(overall_languages) > 5:
            lang_str += f", and {len(overall_languages) - 5} more"
        summary_parts.append(f"Technologies used include {lang_str}.")
    
    if overall_frameworks:
        framework_str = ", ".join(overall_frameworks[:5])  # Top 5
        if len(overall_frameworks) > 5:
            framework_str += f", and {len(overall_frameworks) - 5} more"
        summary_parts.append(f"Frameworks and libraries include {framework_str}.")
    
    # Contribution information
    total_contributors = 0
    total_commits = 0
    for project in real_projects:
        contributors = project.get("contributors", [])
        total_contributors = max(total_contributors, len(contributors))
        for contrib in contributors:
            total_commits += contrib.get("commits", 0)
    
    if total_commits > 0:
        summary_parts.append(
            f"Projects show active development with {total_commits} total commits "
            f"from {total_contributors} contributor{'s' if total_contributors != 1 else ''}."
        )
    
    return " ".join(summary_parts)


def generate_statistics(project_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate formatted statistics from project data.
    
    Args:
        project_data: The structured project data from the upload endpoint
        
    Returns:
        Dictionary containing formatted statistics
    """
    projects = project_data.get("projects", [])
    overall = project_data.get("overall", {})
    
    # Filter out unorganized files project
    real_projects = [p for p in projects if p.get("id", 0) != 0]
    
    totals = overall.get("totals", {})
    
    # Calculate code metrics
    total_lines = 0
    total_code_files = 0
    languages_counter = Counter()
    frameworks_counter = Counter()
    
    for project in real_projects:
        files = project.get("files", {})
        code_files = files.get("code", [])
        total_code_files += len(code_files)
        
        for code_file in code_files:
            total_lines += code_file.get("lines", 0)
        
        classification = project.get("classification", {})
        languages = classification.get("languages", [])
        frameworks = classification.get("frameworks", [])
        
        languages_counter.update(languages)
        frameworks_counter.update(frameworks)
    
    # Calculate contribution metrics
    total_commits = 0
    total_lines_added = 0
    total_lines_deleted = 0
    unique_contributors = set()
    
    for project in real_projects:
        contributors = project.get("contributors", [])
        for contrib in contributors:
            unique_contributors.add(contrib.get("name", "Unknown"))
            total_commits += contrib.get("commits", 0)
            total_lines_added += contrib.get("lines_added", 0)
            total_lines_deleted += contrib.get("lines_deleted", 0)
    
    # Build statistics dictionary
    stats = {
        "overview": {
            "total_projects": totals.get("projects", len(real_projects)),
            "total_files": totals.get("files", 0),
            "total_code_files": totals.get("code_files", 0),
            "total_text_files": totals.get("text_files", 0),
            "total_image_files": totals.get("image_files", 0)
        },
        "code_metrics": {
            "total_lines_of_code": total_lines,
            "average_lines_per_file": round(total_lines / total_code_files, 1) if total_code_files > 0 else 0,
            "code_files_count": total_code_files
        },
        "technologies": {
            "languages": dict(languages_counter.most_common()),
            "frameworks": dict(frameworks_counter.most_common())
        },
        "contributions": {
            "total_commits": total_commits,
            "total_lines_added": total_lines_added,
            "total_lines_deleted": total_lines_deleted,
            "net_lines": total_lines_added - total_lines_deleted,
            "unique_contributors": len(unique_contributors)
        },
        "project_types": {
            "classification": overall.get("classification", "unknown"),
            "confidence": overall.get("confidence", 0.0)
        }
    }
    
    return stats


def generate_non_ai_analysis(project_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate complete non-AI analysis including resume items, summary, and statistics.
    
    Args:
        project_data: The structured project data from the upload endpoint
        
    Returns:
        Dictionary containing:
        - resume_items: List of resume-style items
        - summary: Narrative summary string
        - statistics: Formatted statistics dictionary
    """
    return {
        "resume_items": generate_resume_items(project_data),
        "summary": generate_summary(project_data),
        "statistics": generate_statistics(project_data)
    }

