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
            if len(examples["other"]) < 5:
                examples["other"].append(path)

    total = len(candidates)

    # Match skills for each candidate code file
    for r in candidates:
        path = r.get("path", "") or ""
        ext = Path(path).suffix.lower()
        lang = _EXTENSION_TO_LANG.get(ext, "unknown")
        text_blob = _normalize(r.get("text", "")) + " " + _normalize(path)

        matched_skill = None
        # For HTML files we prefer frontend unless strong code triggers present in text
        if ext in (".html", ".htm"):
            # if text contains code-only triggers, allow matching
            if any(trigger in text_blob for trigger in _CODE_ONLY_TRIGGERS):
                for skill, keywords in _SKILL_KEYWORDS.items():
                    for kw in keywords:
                        if kw in text_blob:
                            matched_skill = skill
                            break
                    if matched_skill:
                        break
            else:
                matched_skill = "web_frontend"
        else:
            # normal matching across keywords
            for skill, keywords in _SKILL_KEYWORDS.items():
                for kw in keywords:
                    if kw in text_blob:
                        matched_skill = skill
                        break
                if matched_skill:
                    break

        if matched_skill:
            counts[matched_skill] += 1
            skill_lang_counts[matched_skill][lang] += 1
            if len(examples[matched_skill]) < 5:
                examples[matched_skill].append(path)
        else:
            counts["other"] += 1
            if len(examples["other"]) < 5:
                examples["other"].append(path)

    # Build structured output; exclude "other" from percentage denominator
    other_count = counts.get("other", 0)
    matched_total = sum(cnt for k, cnt in counts.items() if k != "other")

    skills_list = []
    for skill, cnt in counts.most_common():
        if skill == "other":
            # include other but percent 0 (per request)
            percent = 0.0
            langs = []
        else:
            percent = round((cnt / matched_total) * 100, 1) if matched_total > 0 else 0.0
            # languages breakdown for this skill
            lang_counts = skill_lang_counts.get(skill, {})
            langs = []
            for lang, lcnt in lang_counts.most_common():
                lpercent = round((lcnt / cnt) * 100, 1) if cnt > 0 else 0.0
                langs.append({"language": lang, "count": lcnt, "percent": lpercent})
        skills_list.append({
            "skill": skill,
            "count": cnt,
            "percent": percent,
            "languages": langs,
            "examples": examples.get(skill, [])
        })

    return {
        "total_files": total,
        "matched_total": matched_total,
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