import subprocess
from pathlib import Path
from collections import defaultdict
from typing import Dict, Any
import os
import re


def get_project_timestamp(project_path: Path) -> int:
    """Get project timestamp from first git commit.
    
    Returns Unix timestamp (integer) of the first commit, or 0 if:
    - Not a git repository
    - Git repo has no commits
    - Error occurred
    
    Args:
        project_path: Path to the project directory
        
    Returns:
        int: Unix timestamp of first commit, or 0 on failure
    """
    if not (project_path / ".git").exists():
        return 0
    
    try:
        cp = _safe_run(
            ["git", "log", "--reverse", "--format=%ct", "--all"],
            cwd=project_path,
            timeout=5
        )
        
        if cp.returncode != 0:
            return 0
        
        timestamps = cp.stdout.strip().splitlines()
        if timestamps and timestamps[0]:
            return int(timestamps[0])
        else:
            return 0
            
    except subprocess.TimeoutExpired:
        return 0
    except Exception:
        return 0


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


def _normalize_name(name: str) -> str:
    normalized = name.lower().strip()
    normalized = re.sub(r'[^a-z\s]', '', normalized)
    normalized = ' '.join(normalized.split())
    return normalized

def _split_tokens(norm: str) -> list:
    return norm.split()

def _find_canonical_identity(email: str, name: str, all_identities: list) -> tuple:
    norm_name = _normalize_name(name)
    email_user = email.split('@')[0] if '@' in email else email
    email_user = re.sub(r'^\d+\+', '', email_user)
    norm_email_user = _normalize_name(email_user)

    matches = []
    for other_email, other_name in all_identities:
        other_norm_name = _normalize_name(other_name)
        other_email_user = other_email.split('@')[0] if '@' in other_email else other_email
        other_email_user = re.sub(r'^\d+\+', '', other_email_user)
        other_norm_email_user = _normalize_name(other_email_user)

        other_tokens = _split_tokens(other_norm_name)
        # Previous direct equality checks
        direct_match = (
            norm_name == other_norm_name or
            norm_name == other_norm_email_user or
            norm_email_user == other_norm_name or
            norm_email_user == other_norm_email_user
        )
        # New token-based match: username equals any token of spaced name
        token_match = (
            (len(other_tokens) >= 2 and (norm_email_user in other_tokens or norm_name in other_tokens)) or
            (len(_split_tokens(norm_name)) >= 2 and (other_norm_email_user in _split_tokens(norm_name)))
        )

        if direct_match or token_match:
            matches.append((other_email, other_name))

    if not matches:
        return (email, name)

    def identity_score(identity):
        e, n = identity
        norm_n = _normalize_name(n)
        tokens = _split_tokens(norm_n)
        score = 0
        # Strongly prefer multi-word names (real names)
        if len(tokens) >= 2:
            score += 10000
        # Prefer non-noreply email modestly
        if 'users.noreply.github.com' not in e:
            score += 500
        # Prefer longer multi-word name
        score += len(n)
        return score

    matches.sort(key=identity_score, reverse=True)
    return matches[0]

def get_git_contributors(repo_path: Path) -> Dict[str, Any]:
    if not (repo_path / ".git").exists():
        return {"error": f"No .git folder found at {repo_path}"}

    all_identities = []
    contributors_by_email = defaultdict(lambda: {
        "name": "",
        "commits": 0,
        "lines_added": 0,
        "lines_deleted": 0,
        "email": ""
    })

    try:
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
                raw_name = author_info.split("<")[0].strip()
                email = author_info.split("<")[-1].replace(">", "").strip() if "<" in author_info else ""
                all_identities.append((email, raw_name))
                contributors_by_email[email]["name"] = raw_name
                contributors_by_email[email]["commits"] = commits
                contributors_by_email[email]["email"] = email

        try:
            cp2 = _safe_run(["git", "log", "--pretty=format:%an <%ae>", "--numstat", "--all"], cwd=repo_path, timeout=12)
            if cp2.returncode != 0:
                return {"error": f"git log --numstat failed: {cp2.stderr.strip()}"}
            blame_output = cp2.stdout
        except subprocess.TimeoutExpired:
            return {"error": "git log --numstat timed out"}

        current_email = None
        for line in blame_output.splitlines():
            if not line.strip():
                continue
            if "\t" not in line:
                if "<" in line and ">" in line:
                    current_email = line.split("<")[-1].replace(">", "").strip()
                else:
                    current_email = None
            else:
                parts = line.split("\t")
                if len(parts) >= 2 and current_email:
                    added, deleted = parts[:2]
                    if added.isdigit():
                        contributors_by_email[current_email]["lines_added"] += int(added)
                    if deleted.isdigit():
                        contributors_by_email[current_email]["lines_deleted"] += int(deleted)

        # Merge under canonical identities
        canonical = defaultdict(lambda: {
            "commits": 0, "lines_added": 0, "lines_deleted": 0, "email_set": set(), "names": set()
        })
        for email, stats in contributors_by_email.items():
            name = stats["name"]
            canon_email, canon_name = _find_canonical_identity(email, name, all_identities)
            key = canon_name.lower().strip()  # identity by final chosen name
            canonical[key]["commits"] += stats["commits"]
            canonical[key]["lines_added"] += stats["lines_added"]
            canonical[key]["lines_deleted"] += stats["lines_deleted"]
            canonical[key]["email_set"].add(email)
            canonical[key]["names"].add(canon_name)
            canonical[key]["names"].add(name)

        # Final formatting: choose best real name with space if available
        contributors = {}
        for key, agg in canonical.items():
            spaced = [n for n in agg["names"] if " " in n.strip()]
            if spaced:
                # prefer longest spaced name
                final_name = max(spaced, key=len)
            else:
                # fallback: attempt crude split (e.g., kylekmcleod -> Kyle McLeod) using known capitalizations from other spaced names
                n = list(agg["names"])[0]
                cleaned = re.sub(r'[^A-Za-z]', '', n)
                # heuristic: try to split before last 5+ letter tail matching any observed last token
                observed_last_tokens = {t.split()[-1].lower() for t in sum([list(canonical[k]["names"]) for k in canonical], []) if " " in t}
                candidate_split = None
                for last in sorted(observed_last_tokens, key=len, reverse=True):
                    if cleaned.lower().endswith(last) and len(last) >= 4 and len(cleaned) > len(last)+2:
                        idx = len(cleaned) - len(last)
                        candidate_split = cleaned[:idx], cleaned[idx:]
                        break
                if candidate_split:
                    first, last = candidate_split
                    final_name = first.capitalize() + " " + last.capitalize()
                else:
                    final_name = n  # leave unchanged

            contributors[final_name] = {
                "commits": agg["commits"],
                "lines_added": agg["lines_added"],
                "lines_deleted": agg["lines_deleted"],
                "email": ", ".join(sorted(agg["email_set"]))
            }

        total_commits = sum(c["commits"] for c in contributors.values()) or 1
        for name, stats in contributors.items():
            stats["percent_of_commits"] = round((stats["commits"] / total_commits) * 100, 2)

        return {"contributors": contributors, "total_commits": total_commits}

    except Exception as e:
        return {"error": f"Git analysis failed for {repo_path}: {str(e)}"}