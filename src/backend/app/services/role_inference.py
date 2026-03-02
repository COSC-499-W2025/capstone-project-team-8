"""
Role Inference Service

Infers the user's key role in a project based on:
- Whether the project is collaborative (has multiple active contributors)
- The user's contribution percentage (from git commit stats)
- The project classification type (coding / writing / art / mixed / unknown)
- The detected programming languages (frontend vs. backend heuristic)
"""

from typing import Dict, Any

# Languages that are primarily frontend-focused
_FRONTEND_LANGUAGES = {
    'javascript', 'typescript', 'css', 'html', 'scss', 'sass',
    'less', 'vue', 'svelte', 'jsx', 'tsx', 'coffeescript',
}

# Languages that are primarily backend / systems-focused
_BACKEND_LANGUAGES = {
    'python', 'java', 'c++', 'c', 'c#', 'php', 'ruby', 'go',
    'rust', 'kotlin', 'swift', 'scala', 'sql', 'r', 'perl',
    'haskell', 'elixir', 'erlang', 'clojure', 'bash', 'shell',
}

# Threshold at which a collaborator is considered the "lead"
_LEAD_THRESHOLD = 50.0


def _classify_languages(languages: list) -> str:
    """
    Given a list of detected language names, return:
      - 'frontend'      – only frontend languages detected
      - 'backend'       – only backend languages detected
      - 'full_stack'    – mix of both
      - 'unknown'       – no recognisable languages
    """
    normalised = {lang.lower() for lang in languages if lang}
    has_frontend = bool(normalised & _FRONTEND_LANGUAGES)
    has_backend  = bool(normalised & _BACKEND_LANGUAGES)

    if has_frontend and has_backend:
        return 'full_stack'
    if has_frontend:
        return 'frontend'
    if has_backend:
        return 'backend'
    return 'unknown'


def infer_user_role(project_data: Dict[str, Any]) -> str:
    """
    Infer the user's key role in a project from analysis data.

    Args:
        project_data: A dict (from folder-upload analysis or project detail)
                      that may contain:
                        - classification: {'type': str}   (or flat 'classification_type')
                        - is_collaborative: bool
                        - user_contribution_percent: float  (0–100)
                        - languages: list[str]

    Returns:
        One of the valid USER_ROLE_CHOICES strings defined on the Project model.
    """
    # --- Extract key fields with safe defaults -------------------------
    classification_obj  = project_data.get('classification', {})
    if isinstance(classification_obj, dict):
        classification_type = classification_obj.get('type', '')
    else:
        classification_type = str(classification_obj)

    # Fall back to the flat field used on the saved Project object
    if not classification_type:
        classification_type = project_data.get('classification_type', 'unknown') or 'unknown'

    classification_type = classification_type.lower()

    is_collaborative     = bool(project_data.get('is_collaborative', False))
    user_percent         = float(project_data.get('user_contribution_percent', 0.0))
    languages            = project_data.get('languages', [])

    # --- Determine base category from classification -------------------
    is_coding   = 'coding'  in classification_type
    is_writing  = 'writing' in classification_type
    is_art      = 'art'     in classification_type

    # ------------------------------------------------------------------ #
    # Non-collaborative: user did everything themselves
    # ------------------------------------------------------------------ #
    if not is_collaborative:
        if is_coding:
            return 'solo_developer'
        if is_writing:
            return 'writer'
        if is_art:
            return 'designer'
        return 'other'

    # ------------------------------------------------------------------ #
    # Collaborative – non-coding projects
    # ------------------------------------------------------------------ #
    if is_writing:
        return 'writer'
    if is_art:
        return 'designer'

    # ------------------------------------------------------------------ #
    # Collaborative – coding (or mixed-coding / unknown)
    # ------------------------------------------------------------------ #
    if is_coding or classification_type.startswith('mixed'):
        # High contributor → lead
        if user_percent >= _LEAD_THRESHOLD:
            return 'lead_developer'

        # Low contributor → specialise by language
        lang_category = _classify_languages(languages)
        if lang_category == 'frontend':
            return 'frontend_developer'
        if lang_category == 'backend':
            return 'backend_developer'
        if lang_category == 'full_stack':
            return 'full_stack_developer'

        # No language hint → plain contributor
        return 'contributor'

    # ------------------------------------------------------------------ #
    # Fallback for unknown / unrecognised classifications
    # ------------------------------------------------------------------ #
    return 'contributor'
