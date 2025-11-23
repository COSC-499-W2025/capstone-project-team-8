"""
Skill Analyzer Module (reworked)

Determines skills based on key code files only. Dependency/lock/doc files are
conservatively classified as "other" and do not influence skill percentages.

Output:
  {
    "total_files": <number considered>,
    "matched_total": <files matched to known skills>,
    "skills": [
      {
        "skill": "data_processing",
        "count": 3,
        "percent": 60.0,              # percent of matched_total (excludes "other")
        "languages": [
           {"language": "Python", "count": 2, "percent": 66.7},
           {"language": "JavaScript", "count": 1, "percent": 33.3}
        ],
        "examples": [...]
      },
      ...
    ],
    "raw_counts": {...}
  }
"""

from collections import Counter, defaultdict
from typing import List, Dict, Any
from pathlib import Path


# Priority-ordered skill keyword mapping. The order controls which skill wins when multiple keywords match.
_SKILL_KEYWORDS = {
    "data_processing": [
        "pandas", "numpy", "dataframe", "groupby", "merge(", "join(", "read_csv", "to_csv", "iloc", "loc",
        "filter(", "dropna", "fillna", "pivot", "aggregate", "apply("
    ],
    "machine_learning": [
        "tensorflow", "keras", "pytorch", "torch", "sklearn", "scikit-learn", "model.fit", "predict(", "training",
        "nn.Module", "loss=", "optimizer", "transformer", "bert", "lstm", "randomforest"
    ],
    "web_backend": [
        "django", "flask", "fastapi", "express", "koa", "routes", "app.get(", "app.post(", "@app.route", "controller",
        "middleware"
    ],
    "web_frontend": [
        "react", "vue", "angular", "svelte", "component(", "useState", "useEffect", "jsx", "tsx", "props", "ng-"
    ],
    "testing": ["pytest", "unittest", "mocha", "jest", "assert", "test_", "spec("],
    "devops": ["docker", "dockerfile", "docker-compose", "kubernetes", "helm", "ci", "github actions", "gitlab-ci"],
    "database": ["sqlalchemy", "select ", "insert ", "update ", "create table", "psycopg2", "sqlite3", "mysql", "pgsql"],
    "visualization": ["matplotlib", "seaborn", "plotly", "bokeh", "altair", "ggplot"],
    "scripting": ["bash", "sh ", "argparse", "click", "sys.argv"],
    "mobile": ["react-native", "expo", "android", "ios", "swift", "kotlin"],
}

# conservative extensions and dependency filenames (treated as "other")
_CONSERVATIVE_EXTS = {".lock", ".json", ".md", ".rst", ".txt", ".yml", ".yaml", ".ini", ".toml"}
_DEPENDENCY_FILENAMES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "composer.lock", "Pipfile.lock"}

# map extensions to languages (reuse a small mapping instead of importing whole module)
_EXTENSION_TO_LANG = {
    ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript",
    ".java": "Java", ".go": "Go", ".rb": "Ruby", ".cs": "C#", ".cpp": "C++", ".c": "C", ".php": "PHP",
    ".rs": "Rust", ".swift": "Swift", ".kt": "Kotlin", ".scala": "Scala", ".sh": "Shell", ".ps1": "PowerShell",
    ".html": "HTML", ".htm": "HTML", ".css": "CSS", ".ipynb": "Jupyter Notebook"
}

# triggers that indicate code-like content (used for content files that include inline text)
_CODE_ONLY_TRIGGERS = {
    "read_csv", "to_csv", "iloc", "loc", "apply(", "groupby", "merge(", "join(", "model.fit",
    "predict(", "import ", "def ", "class ", "tensorflow", "keras", "pytorch", "torch", "sklearn",
    "scikit-learn", "nn.module", "loss=", "optimizer", "transformer", "bert", "lstm", "randomforest"
}


def _normalize(text: str) -> str:
    return (text or "").lower()


def detect_skills_from_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Reworked: only consider key code files by extension (ignore dependency/docs).
    Aggregate skills counts and per-language breakdown.
    """
    counts = Counter()
    examples = defaultdict(list)
    skill_lang_counts = defaultdict(Counter)

    # Build candidate list: only files with known code extensions and not marked skipped.
    candidates: List[Dict[str, Any]] = []
    for r in results:
        if r.get("skipped"):
            continue
        path = r.get("path", "") or ""
        ext = Path(path).suffix.lower()
        filename = Path(path).name
        # treat dependency/lock/doc files as "other" and skip as candidates
        if filename in _DEPENDENCY_FILENAMES or ext in _CONSERVATIVE_EXTS:
            counts["other"] += 1
            if len(examples["other"]) < 5:
                examples["other"].append(path)
            continue
        # only consider files whose extension maps to a programming language
        if ext in _EXTENSION_TO_LANG:
            candidates.append(r)
        else:
            # not a key code file -> other
            counts["other"] += 1
                        break
                if matched_skill:
                    break
            if not matched_skill:
                matched_skill = "web_frontend"
        else:
            # For content files: use text only (not path) and be conservative
            if r.get("type") == "content":
                # if no inline text, avoid matching from filename alone (README, lock files, etc.)
                if not text_blob.strip():
                    matched_skill = None
                else:
                    # If this is a dependency/lock/doc file, require a code-only trigger in text
                    if ext in _CONSERVATIVE_EXTS or filename in _DEPENDENCY_FILENAMES:
                        # only match if one of the code-only triggers is found in the text
                        if any(trigger in text_blob for trigger in _CODE_ONLY_TRIGGERS):
                            for skill, keywords in _SKILL_KEYWORDS.items():
                                for kw in keywords:
                                    if kw in text_blob:
                                        matched_skill = skill
                                        break
                                if matched_skill:
                                    break
                    else:
                        # general content files: allow keywords but prefer code-like triggers as before
                        for skill, keywords in _SKILL_KEYWORDS.items():
                            for kw in keywords:
                                # accept if kw is a code-only trigger or contains code-like token
                                if kw in _CODE_ONLY_TRIGGERS or any(ch in kw for ch in (".", "(", "import", "def", "class")):
                                    if kw in text_blob:
                                        matched_skill = skill
                                        break
                            if matched_skill:
                                break
            else:
                # For code files, match using both text and path (path helps with filenames like Dockerfile, settings)
                search_blob = " ".join([text_blob, path_blob])
                for skill, keywords in _SKILL_KEYWORDS.items():
                    for kw in keywords:
                        if kw in search_blob:
                            matched_skill = skill
                            break
                    if matched_skill:
                        break

        if matched_skill:
            counts[matched_skill] += 1
            # store up to some example paths per skill
            if len(examples[matched_skill]) < 5:
                examples[matched_skill].append(path)
        else:
            # Count "other" to keep track of unmatched files
            counts["other"] += 1
            if len(examples["other"]) < 5:
                examples["other"].append(path)

    # Build structured output
    skills_list = []
    # exclude "other" from percentage denominator
    other_count = counts.get("other", 0)
    matched_total = total - other_count
    for skill, cnt in counts.most_common():
        if matched_total > 0 and skill != "other":
            percent = round((cnt / matched_total) * 100, 1)
        else:
            # do not compute a meaningful percent for "other" or when no matched files exist
            percent = 0.0
        skills_list.append({
            "skill": skill,
            "count": cnt,
            "percent": percent,
            "examples": examples.get(skill, [])  # sample file paths
        })

    return {
        "total_files": total,
        "skills": skills_list,
        "raw_counts": dict(counts)
    }


def generate_skill_tags(skills_summary: Dict[str, Any], min_percent: float = 5.0) -> List[str]:
    """
    Create a compact list of skill tags from a skills_summary (as returned by detect_skills_from_results).

    Args:
        skills_summary: result of detect_skills_from_results(...)
        min_percent: minimum percentage threshold (0-100) to include a skill as a tag

    Returns:
        List of skill names (strings) where percent >= min_percent
    """
    tags = []
    for s in skills_summary.get("skills", []):
        if s.get("percent", 0.0) >= min_percent:
            tags.append(s.get("skill"))
    return tags


# Convenience wrapper
def analyze_and_tag(results: List[Dict[str, Any]], min_percent: float = 5.0) -> Dict[str, Any]:
    """
    Run detection and return both the summary and generated tags.
    """
    summary = detect_skills_from_results(results)
    tags = generate_skill_tags(summary, min_percent=min_percent)
    return {"summary": summary, "tags": tags}