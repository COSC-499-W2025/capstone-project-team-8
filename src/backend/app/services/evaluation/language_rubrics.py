"""
Language-Specific Rubrics Service

Re-exports all rubric classes from the rubrics subpackage for backward compatibility.
"""

from .rubrics.base import RubricCategory, LanguageRubric
from .rubrics.python_rubric import PythonRubric
from .rubrics.javascript_rubric import JavaScriptRubric
from .rubrics.java_rubric import JavaRubric
from .rubrics.c_rubric import CRubric
from .rubrics import get_rubric_for_language

__all__ = [
    'RubricCategory',
    'LanguageRubric',
    'PythonRubric',
    'JavaScriptRubric',
    'JavaRubric',
    'CRubric',
    'get_rubric_for_language',
]
