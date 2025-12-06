import os
import re
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Iterable, Optional

# Heuristics maps and helpers
EXT_TO_LANG = {
	".py": "Python",
	".js": "JavaScript",
	".jsx": "JavaScript",
	".ts": "TypeScript",
	".tsx": "TypeScript",
	".java": "Java",
	".kt": "Kotlin",
	".kts": "Kotlin",
	".swift": "Swift",
	".cs": "C#",
	".cpp": "C++",
	".c": "C",
	".h": "C/C++ Header",
	".html": "HTML",
	".htm": "HTML",
	".css": "CSS",
	".scss": "CSS",
	".sass": "CSS",
	".less": "CSS",
	".json": "JSON",
	".xml": "XML",
	".yaml": "YAML",
	".yml": "YAML",
	".sh": "Shell",
	".bat": "Batch",
	".ps1": "PowerShell",
	".php": "PHP",
	".rb": "Ruby",
	".go": "Go",
	".rs": "Rust",
	".sql": "SQL",
	".dockerfile": "Dockerfile",
	".ini": "INI",
	".gradle": "Gradle",
	".pom": "Maven",
}

# Basic mapping from file types/keywords to skill categories
KEYWORD_SKILL_MAP = [
	# frontend
	(r"\bReact\b|\breact-dom\b|from 'react'|from \"react\"|<\s*Component\b", "Frontend Web"),
	(r"\bVue\b|\bvue-router\b|\bvuex\b", "Frontend Web"),
	(r"\bAngular\b|\b@NgModule\b", "Frontend Web"),
	(r"\.(css|scss|less)\b|class=\"[^\"]+\"|<div\b", "Frontend Web"),
	(r"\bHTML\b|<!DOCTYPE html>", "Frontend Web"),
	# web backend
	(r"\bFlask\b|\bfrom flask\b|\bapp = Flask\b", "Web Backend"),
	(r"\bDjango\b|\bdjango\.(contrib|urls|models)\b", "Web Backend"),
	(r"\bFastAPI\b|\bfrom fastapi\b", "Web Backend"),
	(r"\bExpress\b|\brequire\('express'\)|from 'express'|from \"express\"", "Web Backend"),
	(r"\bSpringBoot\b|\bSpringApplication\b|\b@SpringBootApplication\b|\bspringframework\b", "Web Backend"),
	# data / ml
	(r"\bPandas\b|\bimport pandas\b|\bpd\.", "Data Science"),
	(r"\bNumPy\b|\bimport numpy\b|\bnp\.", "Data Science"),
	(r"\bscikit-learn\b|\bsklearn\b", "Data Science"),
	(r"\btensorflow\b|\bkeras\b", "Machine Learning"),
	(r"\btorch\b|\bPyTorch\b", "Machine Learning"),
	# mobile
	(r"\bAndroid\b|com\.android\b|R\.layout\b|setContentView\(|Activity\b", "Mobile"),
	(r"\bSwiftUI\b|\bUIKit\b|import SwiftUI|import UIKit", "Mobile"),
	# devops / infra
	(r"\bDockerfile\b|\bFROM\b.+\b", "DevOps"),
	(r"\bkubernetes\b|\bkind: Deployment\b|\bapiVersion: apps/v1\b", "DevOps"),
	(r"\bhelm\b|\bChart.yaml\b", "DevOps"),
	(r"\bCI/CD\b|\btravis\b|github\.actions|gitlab-ci", "DevOps"),
	# databases
	(r"\bSELECT\b.+\bFROM\b|\bCREATE TABLE\b|\bINSERT INTO\b", "Databases"),
	(r"\bSQLAlchemy\b|\bfrom sqlalchemy\b", "Databases"),
	(r"\bmongodb\b|\bMongoClient\b", "Databases"),
	# testing
	(r"\bpytest\b|\bunittest\b|\bmocha\b|\bjest\b|\bdescribe\(|it\(", "Testing"),
	# game dev
	(r"\bUnityEngine\b|\bMonoBehaviour\b|using UnityEngine;", "Game Development"),
	# scripting / automation
	(r"\bimport os\b|\bsubprocess\b|\bsys\.", "Scripting"),
]

# Language-specific keywords to map more precisely (language -> list of (regex, skill))
LANGUAGE_KEYWORDS: Dict[str, List[Tuple[str, str]]] = {
	"Python": [
		(r"\bflask\b", "Web Backend"),
		(r"\bdjango\b", "Web Backend"),
		(r"\bfastapi\b", "Web Backend"),
		(r"\bpandas\b", "Data Science"),
		(r"\bnumpy\b", "Data Science"),
		(r"\bscikit-learn\b|\bsklearn\b", "Data Science"),
		(r"\btensorflow\b|\bkeras\b", "Machine Learning"),
		(r"\btorch\b|\bpytorch\b", "Machine Learning"),
		(r"\bsqlalchemy\b", "Databases"),
		(r"\bselenium\b", "Testing"),
	],
	"JavaScript": [
		(r"\bReact\b|\breact-dom\b", "Frontend Web"),
		(r"\bVue\b", "Frontend Web"),
		(r"\bAngular\b", "Frontend Web"),
		(r"\bexpress\b", "Web Backend"),
		(r"\bnode\b", "Web Backend"),
		(r"\bjest\b|\bmocha\b", "Testing"),
	],
	"TypeScript": [
		(r"\bReact\b|\bAngular\b|\bVue\b", "Frontend Web"),
		(r"\bNode\b|\bExpress\b", "Web Backend"),
	],
	"Java": [
		(r"\bSpring\b|\bspringframework\b", "Web Backend"),
		(r"\bAndroid\b", "Mobile"),
	],
	"C#": [
		(r"\bASP\.NET\b|\baspnet\b|\bMicrosoft\.AspNetCore\b", "Web Backend"),
		(r"\bUnityEngine\b", "Game Development"),
	],
	"Go": [
		(r"\bgin-gonic\b|\bGin\b", "Web Backend"),
	],
	"YAML": [
		(r"\bapiVersion: apps/v1\b|\bkind: Deployment\b", "DevOps"),
	],
	"Dockerfile": [
		(r"\bFROM\b", "DevOps"),
	],
	"SQL": [
		(r"\bSELECT\b|\bINSERT\b|\bCREATE TABLE\b", "Databases"),
	],
}

SKIP_DIRS = {"node_modules", ".git", "venv", "env", "__pycache__", "dist", "build", ".next", "target"}

BINARY_EXTS = {
	".png", ".jpg", ".jpeg", ".gif", ".ico", ".exe", ".dll", ".so", ".dylib", ".class", ".jar", ".war", ".pyc"
}
# Code-specific extensions to analyze (whitelist approach)
# Only analyze actual code files, not documents, media, or other content
CODE_EXTS = {
	".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".kt", ".kts", ".swift", ".cs",
	".cpp", ".c", ".h", ".html", ".css", ".scss", ".sass", ".less", ".json", ".xml",
	".yaml", ".yml", ".sh", ".bat", ".ps1", ".php", ".rb", ".go", ".rs", ".sql",
	".dockerfile", ".ini", ".gradle", ".pom", ".vue", ".tsx", ".jsx", ".mjs", ".cjs",
	".properties", ".gradle", ".toml", ".lock", ".dockerfile", ".makefile", ".mk"
}

def _guess_language(path: Path, content: str) -> str:
	# extension-based
	suffix = path.suffix.lower()
	if suffix == "":
		name = path.name.lower()
		if name == "dockerfile":
			return "Dockerfile"
	# known extension
	if suffix in EXT_TO_LANG:
		return EXT_TO_LANG[suffix]
	# heuristics from content
	if re.search(r"\b<html\b|<!doctype html>", content, re.I):
		return "HTML"
	if re.search(r"\bpackage\s+com\b|\bpublic class\b", content):
		return "Java"
	# fallback to file suffix presented
	return EXT_TO_LANG.get(suffix, "Unknown")

def _detect_skills_from_content(language: str, content: str) -> List[str]:
	found = set()
	# generic keyword map
	for pattern, skill in KEYWORD_SKILL_MAP:
		if re.search(pattern, content, re.I | re.M):
			found.add(skill)
	# language-scoped keywords
	if language in LANGUAGE_KEYWORDS:
		for pattern, skill in LANGUAGE_KEYWORDS[language]:
			if re.search(pattern, content, re.I | re.M):
				found.add(skill)
	# simple fallbacks based on language alone
	if not found:
		if language in ("HTML", "CSS", "JavaScript", "TypeScript"):
			found.add("Frontend Web")
		elif language in ("Python", "Java", "C#", "Go", "PHP", "Ruby"):
			# could be backend, scripting or library code
			found.add("Web Backend")
		elif language in ("SQL",):
			found.add("Databases")
		elif language in ("Dockerfile", "YAML"):
			found.add("DevOps")
		else:
			found.add("General Programming")
	return list(found)

def _should_skip(path: Path) -> bool:
	parts = {p.lower() for p in path.parts}
	if parts & SKIP_DIRS:
		return True
	return False

def analyze_project(root_path: str, max_files: int = 10000, project_metadata: Optional[Dict[int, Dict[str, object]]] = None, file_timestamps: Optional[Dict[str, float]] = None) -> Dict:
	"""
	Walk the root_path and return a JSON-serializable dict describing:
	  - total_matches: total skill detections
	  - skills: mapping skill -> { count, percentage, languages: {lang: count} }
	  - chronological_skills: skills ranked by individual file timestamps (from ZIP metadata if available)
	
	Args:
		root_path: Path to scan for files and skills
		max_files: Maximum files to scan (default 10000)
		project_metadata: Optional dict mapping project_tag (int) -> {"timestamp": unix_timestamp, "root": project_root_path}
						 Used for project_tag association only, not for skill timestamps.
		file_timestamps: Optional dict mapping relative file paths -> unix_timestamp
						 If provided, uses these timestamps (from ZIP metadata) instead of filesystem mtime.
						 Keys should be relative to root_path.
	
	Returns:
		Dict with total_files_scanned, total_skill_matches, skills, and chronological_skills
	
	Heuristics are lightweight and file-content based.
	"""
	root = Path(root_path)
	if not root.exists():
		raise FileNotFoundError(f"Path not found: {root_path}")

	skill_counts: Counter = Counter()
	skill_lang_counts: Dict[str, Counter] = defaultdict(Counter)
	skill_latest_timestamp: Dict[str, Tuple[float, str, Optional[int]]] = {}  # skill -> (timestamp, file_path, project_tag)
	total_matches = 0
	seen_files = 0
	
	# Build project root -> tag mapping if metadata provided
	project_root_to_tag: Dict[str, int] = {}
	project_tag_to_timestamp: Dict[int, float] = {}
	if project_metadata:
		for tag, meta in project_metadata.items():
			if isinstance(meta, dict):
				proj_root = meta.get("root")
				timestamp = meta.get("timestamp")
				if proj_root:
					project_root_to_tag[str(proj_root)] = int(tag)
					if timestamp is not None:
						project_tag_to_timestamp[int(tag)] = float(timestamp) if isinstance(timestamp, (int, float)) else 0.0

	for dirpath, dirnames, filenames in os.walk(root):
		# modify dirnames in-place to skip
		dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
		for fname in filenames:
			fp = Path(dirpath) / fname
			if _should_skip(fp):
				continue
			if fp.suffix.lower() in BINARY_EXTS:
				continue
			# Only analyze code files (whitelist approach)
			if fp.suffix.lower() not in CODE_EXTS:
				continue
			try:
				with open(fp, "r", encoding="utf-8", errors="ignore") as fh:
					content = fh.read()
			except Exception:
				# skip unreadable files
				continue

			seen_files += 1
			if seen_files > max_files:
				break

			# Try to associate file with a project_tag via root matching
			project_tag = None
			if project_root_to_tag:
				fp_str = str(fp)
				# Match file to nearest project root (longest matching prefix)
				best_root = None
				best_len = 0
				for root_str, tag in project_root_to_tag.items():
					if fp_str.startswith(str(root_str)) and len(str(root_str)) > best_len:
						best_root = root_str
						best_len = len(str(root_str))
						project_tag = tag
			
			# If no project matched and root project (tag 0) exists, use it for root-level files
			if project_tag is None and 0 in project_tag_to_timestamp:
				project_tag = 0
			
			# Get individual file timestamp
			# Prefer ZIP metadata timestamp if available, else use filesystem mtime
			timestamp = None
			if file_timestamps:
				# Try to find this file's timestamp in the mapping
				try:
					rel_path = fp.relative_to(root)
					# Try both forward and backward slashes for Windows/Unix compatibility
					rel_path_str = str(rel_path).replace('\\', '/')
					if rel_path_str in file_timestamps:
						timestamp = file_timestamps[rel_path_str]
					else:
						# Fallback to filesystem
						timestamp = fp.stat().st_mtime
				except Exception:
					timestamp = fp.stat().st_mtime if fp.exists() else 0
			else:
				try:
					timestamp = fp.stat().st_mtime
				except Exception:
					timestamp = 0

			language = _guess_language(fp, content)
			skills = _detect_skills_from_content(language, content)

			for s in skills:
				skill_counts[s] += 1
				skill_lang_counts[s][language] += 1
				total_matches += 1
				
				# Track most recent timestamp for each skill (by individual file timestamp)
				if s not in skill_latest_timestamp or timestamp > skill_latest_timestamp[s][0]:
					skill_latest_timestamp[s] = (timestamp, str(fp), project_tag)

		if seen_files > max_files:
			break

	# Compute percentages
	skills_out = {}
	for skill, count in skill_counts.most_common():
		lang_counts = dict(skill_lang_counts[skill])
		percentage = (count / total_matches * 100.0) if total_matches > 0 else 0.0
		skills_out[skill] = {
			"count": count,
			"percentage": round(percentage, 2),
			"languages": lang_counts,
		}

	# Build chronological ranking (sorted by most recent timestamp descending, projects without timestamps last)
	chronological_skills = []
	
	# Separate skills into known-timestamp and unknown-timestamp groups
	known_ts_skills = []
	unknown_ts_skills = []
	
	for skill, (timestamp, filepath, project_tag) in skill_latest_timestamp.items():
		if timestamp > 0:
			known_ts_skills.append((skill, timestamp, filepath, project_tag))
		else:
			unknown_ts_skills.append((skill, filepath, project_tag))
	
	# Sort known timestamps descending (most recent first)
	known_ts_skills.sort(key=lambda x: x[1], reverse=True)
	
	# Sort unknown timestamps by skill name alphabetically
	unknown_ts_skills.sort(key=lambda x: x[0])
	
	# Combine: known first, then unknown
	all_ranked = [(s, ts, fp, tag) for s, ts, fp, tag in known_ts_skills] + \
	             [(s, 0, fp, tag) for s, fp, tag in unknown_ts_skills]
	
	for idx, (skill, timestamp, filepath, project_tag) in enumerate(all_ranked, start=1):
		chronological_skills.append({
			"rank": idx,
			"skill": skill,
			"last_used_timestamp": int(timestamp) if timestamp > 0 else None,
			"last_used_path": filepath,
			"project_tag": project_tag,
		})

	result = {
		"total_files_scanned": seen_files,
		"total_skill_matches": total_matches,
		"skills": skills_out,
		"chronological_skills": chronological_skills,
	}
	return result

def generate_chronological_skill_detection(
    project_skills: Dict[int, Iterable[str]],
    project_timestamps: Dict[int, int],
    *,
    ignore_zero_timestamps: bool = True,
    max_entries: int = None
) -> Dict[int, Dict[str, object]]:
    """
    Generate a chronological ranking of skills based on per-project timestamps.

    Args:
        project_skills: Mapping from project_tag (int) to an iterable of detected skills (strings).
                        Example: {1: ['Frontend Web','Databases'], 2: ['Machine Learning']}
        project_timestamps: Mapping from project_tag (int) to Unix timestamp (int).
                            Timestamps of 0 or missing are treated as unknown.
        ignore_zero_timestamps: If True, projects with missing/zero timestamps are placed after
                                known timestamps or omitted from ranking (see below).
        max_entries: Optional cap on number of ranked skills to return.

    Returns:
        Ordered mapping (1-based rank) -> { "skill": str, "project_tag": int, "timestamp": int | None }

    Behavior:
        - For each skill, the earliest timestamp among projects that include that skill is chosen.
        - By default unknown timestamps (<= 0 or missing) are treated as unknown and placed after known timestamps.
        - If ignore_zero_timestamps is True, unknown-timestamp skills will still be included but with timestamp=None and placed after known ones.
    """
    # Build earliest occurrence per skill: skill -> (timestamp, project_tag)
    earliest: Dict[str, Tuple[float, int]] = {}

    for tag, skills in project_skills.items():
        # normalize timestamp; treat missing or non-positive as "unknown"
        raw_ts = project_timestamps.get(tag, 0)
        if raw_ts and isinstance(raw_ts, (int, float)) and raw_ts > 0:
            ts_val = float(raw_ts)
        else:
            # Unknown timestamp represented as +inf so known timestamps sort before it
            ts_val = float("inf")

        # Use a set to avoid duplicate skills reported multiple times for same project
        for skill in set(skills):
            if skill not in earliest or ts_val < earliest[skill][0]:
                earliest[skill] = (ts_val, tag)

    # Convert earliest dict to list and optionally filter/format unknown timestamps
    items = []
    for skill, (ts_val, tag) in earliest.items():
        if ts_val == float("inf"):
            # unknown timestamp
            if ignore_zero_timestamps:
                items.append((skill, None, tag))
            else:
                # keep as None but place after known ones by using +inf internally
                items.append((skill, None, tag))
        else:
            items.append((skill, int(ts_val), tag))

    # Sort: known timestamps ascending first, then unknowns (None)
    def sort_key(entry):
        skill, ts, tag = entry
        return (ts if ts is not None else float("inf"), skill)

    items.sort(key=sort_key)

    # Apply max_entries if provided
    if max_entries is not None:
        items = items[:max_entries]

    # Build ranked mapping 1-based
    ranked: Dict[int, Dict[str, object]] = {}
    for idx, (skill, ts, tag) in enumerate(items, start=1):
        ranked[idx] = {
            "skill": skill,
            "project_tag": tag,
            "timestamp": ts  # None indicates unknown
        }

    return ranked

def format_chronological_skills_for_display(project_result: Dict) -> List[Dict[str, object]]:
	"""
	Format the chronological_skills output for UI display.
	
	Returns a list of dicts with:
	  - rank: position (1-based)
	  - skill: skill name
	  - date_used: human-readable date (ISO format) or "Unknown" if no timestamp
	  - days_since_used: approximate days since last used, or -1 if unknown
	  - file_used: last file path where skill was detected
	  - project_tag: project tag where skill was most recently used (or None)
	"""
	from datetime import datetime, timezone
	import time
	
	if "chronological_skills" not in project_result:
		return []
	
	current_time = time.time()
	formatted = []
	
	for entry in project_result["chronological_skills"]:
		ts = entry["last_used_timestamp"]
		project_tag = entry.get("project_tag")
		
		if ts is not None and ts > 0:
			dt = datetime.fromtimestamp(ts, tz=timezone.utc)
			date_str = dt.isoformat()
			days_since = (current_time - ts) / (24 * 3600)
		else:
			date_str = "Unknown"
			days_since = -1
		
		formatted.append({
			"rank": entry["rank"],
			"skill": entry["skill"],
			"date_used": date_str,
			"days_since_used": round(days_since, 1) if days_since >= 0 else -1,
			"file_used": entry["last_used_path"],
			"project_tag": project_tag,
		})
	
	return formatted

# Small helper for example/debugging; in production the caller would call analyze_project directly.
if __name__ == "__main__":
	import json, sys
	if len(sys.argv) < 2:
		print("Usage: skill_analyzer.py /path/to/project")
	else:
		res = analyze_project(sys.argv[1])
		print(json.dumps(res, indent=2))