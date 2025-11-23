import os
import re
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Iterable

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

def analyze_project(root_path: str, max_files: int = 10000) -> Dict:
	"""
	Walk the root_path and return a JSON-serializable dict describing:
	  - total_matches: total skill detections
	  - skills: mapping skill -> { count, percentage, languages: {lang: count} }
	Heuristics are lightweight and file-content based.
	"""
	root = Path(root_path)
	if not root.exists():
		raise FileNotFoundError(f"Path not found: {root_path}")

	skill_counts: Counter = Counter()
	skill_lang_counts: Dict[str, Counter] = defaultdict(Counter)
	total_matches = 0
	seen_files = 0

	for dirpath, dirnames, filenames in os.walk(root):
		# modify dirnames in-place to skip
		dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
		for fname in filenames:
			fp = Path(dirpath) / fname
			if _should_skip(fp):
				continue
			if fp.suffix.lower() in BINARY_EXTS:
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

			language = _guess_language(fp, content)
			skills = _detect_skills_from_content(language, content)

			for s in skills:
				skill_counts[s] += 1
				skill_lang_counts[s][language] += 1
				total_matches += 1

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

	result = {
		"total_files_scanned": seen_files,
		"total_skill_matches": total_matches,
		"skills": skills_out,
	}
	return result

# Small helper for example/debugging; in production the caller would call analyze_project directly.
if __name__ == "__main__":
	import json, sys
	if len(sys.argv) < 2:
		print("Usage: skill_analyzer.py /path/to/project")
	else:
		res = analyze_project(sys.argv[1])
		print(json.dumps(res, indent=2))