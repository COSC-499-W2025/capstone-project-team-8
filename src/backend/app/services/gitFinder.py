import subprocess
from pathlib import Path
from collections import defaultdict
from typing import Dict, Any
import os


def _safe_run(cmd, cwd: Path, timeout: int = 10) -> subprocess.CompletedProcess:
    """Run subprocess command with environment protection and timeout."""
    env = dict(**os.environ)
    # Prevent git from prompting for credentials or stdin
    env.setdefault("GIT_TERMINAL_PROMPT", "0")
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        env=env,
        timeout=timeout,
    )


def get_git_contributors(repo_path: Path) -> Dict[str, Any]:
    """Analyze a Git repository to determine contributor commit and line stats.

    Returns a dict containing contributor statistics or an error entry on failure.
    Uses short timeouts and non-interactive git env to avoid hanging the test runner.
    """
    if not (repo_path / ".git").exists():
        return {"error": f"No .git folder found at {repo_path}"}

    contributors = defaultdict(lambda: {"commits": 0, "lines_added": 0, "lines_deleted": 0})
    try:
        # Get commit count per author safely
        try:
            cp = _safe_run(["git", "shortlog", "-sne", "--all"], cwd=repo_path, timeout=8)
            if cp.returncode != 0:
                return {"error": f"git shortlog failed: {cp.stderr.strip()}"}
            log_output = cp.stdout
        except subprocess.TimeoutExpired:
            return {"error": "git shortlog timed out"}

        for line in log_output.strip().splitlines():
            parts = line.strip().split("\t")
            if len(parts) == 2:
                commits_str, author_info = parts
                try:
                    commits = int(commits_str.strip())
                except ValueError:
                    commits = 0
                name = author_info.split("<")[0].strip()
                email = author_info.split("<")[-1].replace(">", "").strip() if "<" in author_info else ""
                contributors[name]["commits"] = commits
                contributors[name]["email"] = email

        # Get line changes per author
        try:
            cp2 = _safe_run(["git", "log", "--pretty=format:%an", "--numstat", "--all"], cwd=repo_path, timeout=12)
            if cp2.returncode != 0:
                return {"error": f"git log --numstat failed: {cp2.stderr.strip()}"}
            blame_output = cp2.stdout
        except subprocess.TimeoutExpired:
            return {"error": "git log --numstat timed out"}

        current_author = None
        for line in blame_output.splitlines():
            if not line.strip():
                continue
            if "\t" not in line:
                current_author = line.strip()
            else:
                parts = line.split("\t")
                if len(parts) >= 2 and current_author:
                    added, deleted = parts[:2]
                    if added.isdigit():
                        contributors[current_author]["lines_added"] += int(added)
                    if deleted.isdigit():
                        contributors[current_author]["lines_deleted"] += int(deleted)

        total_commits = sum(c["commits"] for c in contributors.values()) or 1
        for name, stats in contributors.items():
            stats["percent_of_commits"] = round((stats["commits"] / total_commits) * 100, 2)

        return {"contributors": dict(contributors), "total_commits": total_commits}

    except Exception as e:
        return {"error": f"Git analysis failed for {repo_path}: {str(e)}"}