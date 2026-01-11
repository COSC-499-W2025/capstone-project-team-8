"""
Contribution Metrics Analyzer

Extracts rich contributor metrics from git history and file analysis:
- Activity type frequency (code/test/documentation/design)
- Contribution duration and timeline
- Lines of code by activity type
- Primary skill areas based on file types
"""

import subprocess
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from collections import defaultdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def extract_contributor_metrics(
    project_path: Path,
    file_analysis_results: List[Dict[str, Any]]
) -> Dict[str, Dict[str, Any]]:
    """
    Extract enriched contribution metrics for each contributor.
    
    Args:
        project_path: Path to the git repository
        file_analysis_results: Results from file scanner with activity type classification
        
    Returns:
        Dictionary mapping contributor names to their metrics:
        {
            "John Doe": {
                "commits": 25,
                "lines_added": 1500,
                "lines_deleted": 200,
                "first_commit": "2024-01-15",
                "last_commit": "2025-01-11",
                "contribution_duration_days": 360,
                "activity_types": {
                    "code": {"count": 18, "lines_added": 1200},
                    "test": {"count": 5, "lines_added": 200},
                    "documentation": {"count": 2, "lines_added": 100}
                },
                "primary_languages": ["Python", "JavaScript"],
                "file_type_distribution": {
                    ".py": {"commits": 15, "lines_added": 800},
                    ".js": {"commits": 8, "lines_added": 600}
                }
            }
        }
    """
    if not (project_path / ".git").exists():
        logger.debug(f"No .git folder at {project_path}, skipping metrics")
        return {}
    
    logger.info(f"Starting contribution metrics extraction from {project_path}")
    metrics = {}
    
    try:
        # Get all commits with author info and detailed stats
        commits = _extract_detailed_commits(project_path)
        logger.info(f"Extracted {len(commits)} commits from {project_path}")
        
        if not commits:
            logger.warning(f"No commits found for {project_path}")
            return {}
        
        # Aggregate by contributor
        for commit in commits:
            author = commit['author_name']
            if author not in metrics:
                metrics[author] = {
                    "commits": 0,
                    "lines_added": 0,
                    "lines_deleted": 0,
                    "first_commit": None,
                    "last_commit": None,
                    "activity_types": defaultdict(lambda: {"count": 0, "lines_added": 0, "lines_deleted": 0}),
                    "file_type_distribution": defaultdict(lambda: {"commits": 0, "lines_added": 0}),
                }
            
            metrics[author]["commits"] += 1
            metrics[author]["lines_added"] += commit['lines_added']
            metrics[author]["lines_deleted"] += commit['lines_deleted']
            
            # Track first and last commits
            if metrics[author]["first_commit"] is None:
                metrics[author]["first_commit"] = commit['commit_date']
            metrics[author]["last_commit"] = commit['commit_date']
            
            # Classify commit by activity type
            activity_type = _classify_commit_activity(commit)
            metrics[author]["activity_types"][activity_type]["count"] += 1
            metrics[author]["activity_types"][activity_type]["lines_added"] += commit['lines_added']
            metrics[author]["activity_types"][activity_type]["lines_deleted"] += commit['lines_deleted']
            
            # Track file types modified
            for file_ext in commit.get('file_extensions', []):
                metrics[author]["file_type_distribution"][file_ext]["commits"] += 1
                metrics[author]["file_type_distribution"][file_ext]["lines_added"] += commit['lines_added']
        
        # Post-process metrics
        for author in metrics:
            # Convert defaultdicts to regular dicts
            metrics[author]["activity_types"] = dict(metrics[author]["activity_types"])
            metrics[author]["file_type_distribution"] = dict(metrics[author]["file_type_distribution"])
            
            # Calculate contribution duration
            if metrics[author]["first_commit"] and metrics[author]["last_commit"]:
                first = datetime.strptime(metrics[author]["first_commit"], "%Y-%m-%d")
                last = datetime.strptime(metrics[author]["last_commit"], "%Y-%m-%d")
                metrics[author]["contribution_duration_days"] = (last - first).days
                metrics[author]["contribution_duration_months"] = round(metrics[author]["contribution_duration_days"] / 30.44, 1)
            
            # Extract primary languages/frameworks
            metrics[author]["primary_languages"] = _extract_languages_from_files(
                metrics[author]["file_type_distribution"]
            )
        
        logger.debug(f"Successfully extracted metrics for {len(metrics)} contributors")
        logger.info(f"Metrics extraction complete. Contributors: {list(metrics.keys())}")
    
    except Exception as e:
        logger.error(f"Error extracting contributor metrics: {e}", exc_info=True)
        return {}
    
    return metrics


def _extract_detailed_commits(project_path: Path) -> List[Dict[str, Any]]:
    """
    Extract detailed commit information including files modified and activity type hints.
    
    Returns list of commits with:
    - author_name, author_email
    - commit_date (YYYY-MM-DD format)
    - lines_added, lines_deleted
    - file_extensions (list of extensions modified in commit)
    - commit_message (for activity classification)
    """
    commits = []
    
    try:
        # Use numstat with a reliable multi-line format
        # %H = hash, %an = author name, %ae = author email, %ci = commit date, %s = subject
        # Use delimiter @@@@@ to separate header from numstat
        cmd = [
            "git", "log", "--all", 
            "--pretty=format:%H%n%an%n%ae%n%ci%n%s%n@@@@@",
            "--numstat",
        ]
        
        logger.debug(f"Running git command for {project_path}")
        cp = _safe_run(cmd, cwd=project_path, timeout=30)
        if cp.returncode != 0:
            logger.warning(f"Git log failed: {cp.stderr}")
            return []
        
        logger.debug(f"Git log output length: {len(cp.stdout)} bytes")
        
        lines = cp.stdout.split('\n')
        i = 0
        
        while i < len(lines):
            # Look for commit hash line (40 hex chars)
            if i < len(lines) and len(lines[i].strip()) == 40 and all(c in '0123456789abcdef' for c in lines[i].strip()):
                commit_hash = lines[i].strip()
                author_name = lines[i+1].strip() if i+1 < len(lines) else "Unknown"
                author_email = lines[i+2].strip() if i+2 < len(lines) else ""
                commit_date_full = lines[i+3].strip() if i+3 < len(lines) else ""
                commit_message = lines[i+4].strip() if i+4 < len(lines) else ""
                
                # Parse date
                try:
                    commit_date = commit_date_full.split()[0]
                except:
                    commit_date = "1970-01-01"
                
                i += 5
                
                # Skip until we find the @@@@@ delimiter
                while i < len(lines) and lines[i].strip() != "@@@@@":
                    i += 1
                i += 1  # Skip the @@@@@ line
                
                # Collect numstat lines for this commit
                lines_added = 0
                lines_deleted = 0
                file_extensions = []
                
                while i < len(lines):
                    stat_line = lines[i].strip()
                    
                    # Stop at next commit or end
                    if not stat_line or (len(stat_line) == 40 and all(c in '0123456789abcdef' for c in stat_line)):
                        break
                    
                    # numstat format: "additions\tdeletions\tfilename"
                    parts = stat_line.split('\t')
                    if len(parts) >= 3:
                        try:
                            adds = int(parts[0]) if parts[0] != '-' else 0
                            dels = int(parts[1]) if parts[1] != '-' else 0
                            filename = parts[2]
                            
                            lines_added += adds
                            lines_deleted += dels
                            
                            # Extract file extension
                            file_ext = Path(filename).suffix.lower() or Path(filename).name.lower()
                            file_extensions.append(file_ext)
                        except (ValueError, IndexError):
                            pass
                    
                    i += 1
                
                # Add commit if valid
                if author_name and author_name != "Unknown":
                    commits.append({
                        "commit_hash": commit_hash,
                        "author_name": author_name,
                        "author_email": author_email,
                        "commit_date": commit_date,
                        "commit_message": commit_message,
                        "lines_added": lines_added,
                        "lines_deleted": lines_deleted,
                        "file_extensions": list(set(file_extensions)),  # unique extensions
                    })
            else:
                i += 1
    
    except Exception as e:
        logger.error(f"Error extracting commits: {e}", exc_info=True)
    
    logger.debug(f"Extracted {len(commits)} commits from {project_path}")
    return commits


def _classify_commit_activity(commit: Dict[str, Any]) -> str:
    """
    Classify a commit as code/test/documentation/design/configuration based on:
    - File types modified
    - Commit message keywords
    - File names
    """
    message = commit['commit_message'].lower()
    file_exts = commit['file_extensions']
    
    # Check file types FIRST (strongest signal)
    test_exts = {'.test.ts', '.test.js', '.spec.ts', '.spec.js', '.test.py'}
    doc_exts = {'.md', '.rst', '.txt', '.doc', '.docx'}
    design_exts = {'.css', '.scss', '.less', '.fig', '.sketch', '.psd'}
    config_exts = {'.yml', '.yaml', '.json', '.toml', '.ini', '.conf'}
    
    has_test = any(ext in test_exts or 'test' in ext.lower() for ext in file_exts)
    has_doc = any(ext in doc_exts for ext in file_exts)
    has_design = any(ext in design_exts for ext in file_exts)
    has_config = any(ext in config_exts for ext in file_exts)
    
    if has_test:
        return "test"
    if has_doc:
        return "documentation"
    if has_design:
        return "design"
    if has_config:
        return "configuration"
    
    # Keywords for activity classification (fallback if no file type match)
    TEST_KEYWORDS = ['test', 'spec', 'mock', 'fixture', '__tests__', '.test.', '.spec.']
    DOC_KEYWORDS = ['doc', 'readme', 'guide', 'manual', 'wiki', 'changelog', 'contributing']
    DESIGN_KEYWORDS = ['design', 'ui', 'ux', 'style', 'theme', 'layout', 'component']
    CONFIG_KEYWORDS = ['config', 'setup', 'docker', 'env', 'build', 'ci', 'package.json']
    
    # Check message keywords (weaker signal)
    for keyword in TEST_KEYWORDS:
        if keyword in message:
            return "test"
    for keyword in DOC_KEYWORDS:
        if keyword in message:
            return "documentation"
    for keyword in DESIGN_KEYWORDS:
        if keyword in message:
            return "design"
    for keyword in CONFIG_KEYWORDS:
        if keyword in message:
            return "configuration"
    
    # Default to code
    return "code"


def _extract_languages_from_files(file_distribution: Dict[str, Dict]) -> List[str]:
    """
    Extract primary programming languages from file extension distribution.
    Returns top 5 languages by commit count.
    """
    language_map = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.jsx': 'React',
        '.ts': 'TypeScript',
        '.tsx': 'TypeScript',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.cs': 'C#',
        '.go': 'Go',
        '.rs': 'Rust',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.scala': 'Scala',
        '.sh': 'Shell',
        '.html': 'HTML',
        '.css': 'CSS',
        '.sql': 'SQL',
        '.json': 'JSON',
        '.yaml': 'YAML',
        '.yml': 'YAML',
        '.xml': 'XML',
    }
    
    language_commits = defaultdict(int)
    
    for ext, stats in file_distribution.items():
        if ext in language_map:
            language = language_map[ext]
            language_commits[language] += stats.get('commits', 0)
    
    # Sort by commit count and return top 5
    sorted_langs = sorted(language_commits.items(), key=lambda x: x[1], reverse=True)
    return [lang for lang, _ in sorted_langs[:5]]


def _safe_run(cmd, cwd: Path, timeout: int = 10) -> subprocess.CompletedProcess:
    """Run subprocess command with environment protection and timeout."""
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        env=env,
        timeout=timeout,
    )
