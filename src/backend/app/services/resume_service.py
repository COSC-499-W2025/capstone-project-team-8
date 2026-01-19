"""Lightweight resume template and context helpers."""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from django.contrib.auth import get_user_model

User = get_user_model()


@dataclass(frozen=True)
class ResumeTemplate:
    id: str
    name: str
    description: str
    ai_supported: bool = True

    def as_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "ai_supported": self.ai_supported,
        }


_RESUME_TEMPLATES: List[ResumeTemplate] = [
    ResumeTemplate(
        id="classic",
        name="Classic",
        description="Traditional layout with left headline and experience focus.",
        ai_supported=True,
    ),
    ResumeTemplate(
        id="modern",
        name="Modern",
        description="Clean single-column layout emphasising skills and impact.",
        ai_supported=True,
    ),
    ResumeTemplate(
        id="minimal",
        name="Minimal",
        description="Simple template for quick non-AI exports.",
        ai_supported=False,
    ),
]


def list_templates() -> List[Dict[str, Any]]:
    """Return available resume templates as dictionaries."""
    return [template.as_dict() for template in _RESUME_TEMPLATES]


def get_template(template_id: Optional[str]) -> ResumeTemplate:
    """Fetch a resume template, defaulting to the first template."""
    if template_id:
        for template in _RESUME_TEMPLATES:
            if template.id == template_id:
                return template
    return _RESUME_TEMPLATES[0]


def build_resume_context(user: User) -> Dict[str, Any]:
    """Build a simple resume context stub for previews."""
    display_name = user.get_full_name() or user.username
    return {
        "full_name": display_name,
        "summary": (
            "Auto-generated preview summary for {}. "
            "This will be replaced with analyzer-driven achievements.".format(display_name)
        ),
        "contact": {
            "email": user.email,
            "github": getattr(user, "github_username", ""),
            "portfolio": getattr(user, "portfolio_url", ""),
        },
        "projects": [],
        "skills": [],
        "education": [],
        "experience": [],
    }
