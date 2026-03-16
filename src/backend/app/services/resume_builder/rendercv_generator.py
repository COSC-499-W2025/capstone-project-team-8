"""
RenderCV-based PDF generator.

Converts frontend resume JSON → RenderCV YAML → PDF via `rendercv render`.
Requires: pip install "rendercv[full]" pyyaml
"""
import os
import re
import glob
import subprocess
import tempfile
from typing import Any

import yaml


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_bullets(content: str) -> list[str]:
    """Split a bullet-point blob into a plain list of strings."""
    if not content:
        return []
    lines = []
    for line in content.split("\n"):
        line = re.sub(r"^[•\-]\s*", "", line).strip()
        if line:
            lines.append(line)
    return lines


def _extract_github_username(github_url: str) -> str:
    """Return 'johndoe' from 'https://github.com/johndoe'."""
    if not github_url:
        return ""
    return github_url.rstrip("/").split("/")[-1]


def _extract_linkedin_username(linkedin_url: str) -> str:
    """Return 'johndoe' from 'https://linkedin.com/in/johndoe'."""
    if not linkedin_url:
        return ""
    m = re.search(r"linkedin\.com/in/([^/? ]+)", linkedin_url)
    return m.group(1) if m else linkedin_url.rstrip("/").split("/")[-1]


def _normalize_phone(phone: str) -> str | None:
    """
    Coerce a raw phone string into E.164 format that RenderCV accepts.
    """
    if not phone:
        return None
    digits = re.sub(r"\D", "", str(phone))
    if not digits:
        return None
    if digits.startswith("+"):
        return phone  # already E.164
    if len(digits) == 10:
        return f"+1{digits}"
    if len(digits) == 11 and digits[0] == "1":
        return f"+{digits}"
    # For other lengths just prepend + and hope for the best;
    # if still invalid, omit rather than crash.
    candidate = f"+{digits}"
    return candidate


# ---------------------------------------------------------------------------
# Core converter
# ---------------------------------------------------------------------------

def resume_data_to_rendercv_yaml(resume_data: dict, theme: str = "classic") -> dict:
    """
    Convert the frontend resumeData object to a RenderCV-compatible YAML dict.

    Frontend shape (mirrors page.js state):
    {
      name, email, phone, github_url, linkedin_url, portfolio_url, location,
      sections: {
        education:     [{id, title (school), degree_type (B.Sc./M.Sc./etc.), company (major), duration, content}],
        experience:    [{id, title (job title), company, duration, content}],
        projects:      [{id, title, company (tech stack), duration, content}],
        skills:        [{id, title}],
        certifications:[{id, title, company, duration, content}],
        summary:       str,
      }
    }
    """
    cv: dict[str, Any] = {}

    # ── personal info ──────────────────────────────────────────────────────
    cv["name"] = resume_data.get("name") or "Your Name"
    if resume_data.get("email"):
        cv["email"] = resume_data["email"]
    if resume_data.get("phone"):
        normalized = _normalize_phone(resume_data["phone"])
        if normalized:
            cv["phone"] = normalized
    if resume_data.get("location"):
        cv["location"] = resume_data["location"]
    if resume_data.get("portfolio_url"):
        cv["website"] = resume_data["portfolio_url"]

    social = []
    gh = _extract_github_username(resume_data.get("github_url", ""))
    if gh:
        social.append({"network": "GitHub", "username": gh})
    li = _extract_linkedin_username(resume_data.get("linkedin_url", ""))
    if li:
        social.append({"network": "LinkedIn", "username": li})
    if social:
        cv["social_networks"] = social

    # ── sections ───────────────────────────────────────────────────────────
    sections: dict[str, Any] = {}
    raw_sections = resume_data.get("sections", {})

    # Summary (RenderCV supports a plain-text section as a list of bullets)
    summary = raw_sections.get("summary", "")
    if summary and summary.strip():
        sections["summary"] = [summary.strip()]

    # Education
    edu_entries = []
    for item in raw_sections.get("education", []):
        entry: dict[str, Any] = {
            "institution": item.get("title") or "University",
        }
        # degree_type e.g. "B.Sc.", company holds the major e.g. "Computer Science"
        degree_type = item.get("degree_type", "").strip()
        major = item.get("company", "").strip()
        entry["area"] = major or degree_type  # RenderCV area = field of study
        entry["degree"] = degree_type          # RenderCV degree = degree type
        if item.get("duration"):
            entry["date"] = item["duration"]
        bullets = _parse_bullets(item.get("content", ""))
        if bullets:
            entry["highlights"] = bullets
        edu_entries.append(entry)
    if edu_entries:
        sections["education"] = edu_entries

    # Experience
    exp_entries = []
    for item in raw_sections.get("experience", []):
        entry = {
            "company": item.get("company") or "Company",
            "position": item.get("title") or "Position",
        }
        if item.get("duration"):
            entry["date"] = item["duration"]
        bullets = _parse_bullets(item.get("content", ""))
        if bullets:
            entry["highlights"] = bullets
        exp_entries.append(entry)
    if exp_entries:
        sections["experience"] = exp_entries

    # Projects
    proj_entries = []
    for item in raw_sections.get("projects", []):
        entry: dict[str, Any] = {
            "name": item.get("title") or "Project",
        }
        if item.get("duration"):
            entry["date"] = item["duration"]
        bullets = _parse_bullets(item.get("content", ""))
        # Prepend tech stack as first highlight if present
        tech = item.get("company", "")
        if tech:
            bullets = [tech] + bullets if bullets else [tech]
        if bullets:
            entry["highlights"] = bullets
        proj_entries.append(entry)
    if proj_entries:
        sections["projects"] = proj_entries

    # Skills → OneLineEntry list
    skill_titles = [s.get("title", "") for s in raw_sections.get("skills", []) if s.get("title")]
    if skill_titles:
        sections["technical_skills"] = [
            {"label": "Skills", "details": ", ".join(skill_titles)}
        ]

    # Certifications (treated as NormalEntry)
    cert_entries = []
    for item in raw_sections.get("certifications", []):
        entry = {"name": item.get("title") or "Certification"}
        org = item.get("company", "")
        if item.get("duration"):
            entry["date"] = item["duration"]
        bullets = _parse_bullets(item.get("content", ""))
        if org:
            bullets = [f"Issued by {org}"] + bullets
        if bullets:
            entry["highlights"] = bullets
        cert_entries.append(entry)
    if cert_entries:
        sections["certifications"] = cert_entries

    if sections:
        cv["sections"] = sections

    # ── design ─────────────────────────────────────────────────────────────
    VALID_THEMES = {"classic", "moderncv", "engineeringclassic", "sb2nov"}
    chosen_theme = theme if theme in VALID_THEMES else "classic"

    return {
        "cv": cv,
        "design": {"theme": chosen_theme},
    }


# ---------------------------------------------------------------------------
# PDF generation
# ---------------------------------------------------------------------------

def generate_pdf(resume_data: dict, theme: str = "classic") -> bytes:
    """
    Generate a PDF from resume_data using RenderCV.

    Returns raw PDF bytes.
    Raises RuntimeError on failure.
    """
    rendercv_dict = resume_data_to_rendercv_yaml(resume_data, theme)

    with tempfile.TemporaryDirectory() as tmpdir:
        yaml_path = os.path.join(tmpdir, "resume.yaml")

        # Write YAML with allow_unicode so special chars survive
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(
                rendercv_dict,
                f,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False,
            )

        def _run(yaml_dict: dict) -> subprocess.CompletedProcess:
            with open(yaml_path, "w", encoding="utf-8") as f:
                yaml.dump(yaml_dict, f, allow_unicode=True,
                          default_flow_style=False, sort_keys=False)
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            return subprocess.run(
                ["rendercv", "render", "resume.yaml"],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=120,
                env=env,
            )

        result = _run(rendercv_dict)

        # If RenderCV rejected the phone number, strip it and retry once
        if result.returncode != 0:
            err_text = (result.stderr or result.stdout or "")
            if "cv.phone" in err_text and "not a valid phone number" in err_text:
                rendercv_dict.get("cv", rendercv_dict).pop("phone", None)
                result = _run(rendercv_dict)

        if result.returncode != 0:
            err = (result.stderr or result.stdout or "Unknown error").strip()
            raise RuntimeError(f"RenderCV failed: {err}")

        # Find the generated PDF (output dir is resume_output/)
        pattern = os.path.join(tmpdir, "**", "*.pdf")
        pdf_files = glob.glob(pattern, recursive=True)
        if not pdf_files:
            raise RuntimeError("RenderCV ran but produced no PDF.")

        with open(pdf_files[0], "rb") as fh:
            return fh.read()


def generate_yaml_string(resume_data: dict, theme: str = "classic") -> str:
    """Return the RenderCV YAML as a plain string (for download)."""
    rendercv_dict = resume_data_to_rendercv_yaml(resume_data, theme)
    return yaml.dump(
        rendercv_dict,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    )
