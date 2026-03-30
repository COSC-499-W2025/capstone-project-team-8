"""Language-specific evaluation rubrics subpackage."""

from .base import RubricCategory, LanguageRubric
from .python_rubric import PythonRubric
from .javascript_rubric import JavaScriptRubric
from .java_rubric import JavaRubric
from .c_rubric import CRubric


def get_rubric_for_language(language: str) -> LanguageRubric:
    """
    Factory function to get the appropriate rubric for a language.

    Args:
        language: Programming language name (python, javascript, java, c, etc.)

    Returns:
        LanguageRubric instance for the language, or None if no specific rubric exists
    """
    language = language.lower().strip()

    rubric_map = {
        'python': PythonRubric(),
        'javascript': JavaScriptRubric(),
        'typescript': JavaScriptRubric(),
        'java': JavaRubric(),
        'c': CRubric(),
    }

    return rubric_map.get(language, None)


__all__ = [
    'RubricCategory',
    'LanguageRubric',
    'PythonRubric',
    'JavaScriptRubric',
    'JavaRubric',
    'CRubric',
    'get_rubric_for_language',
]
