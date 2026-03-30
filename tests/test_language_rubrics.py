"""
Tests for language rubric evaluation classes.

Verifies that each rubric evaluates projects correctly and that
the base class, factory function, and all imports work as expected.
"""
import os
import sys
import django

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
django.setup()

import pytest
from app.services.evaluation.language_rubrics import (
    RubricCategory,
    LanguageRubric,
    PythonRubric,
    JavaScriptRubric,
    JavaRubric,
    CRubric,
    get_rubric_for_language,
)


# --- Fixtures ---

@pytest.fixture
def empty_project():
    return {'files': []}


@pytest.fixture
def python_project():
    return {'files': [
        {'file_type': 'code', 'filename': 'main.py', 'file_path': 'src/main.py',
         'content_preview': 'class App:\n    def run(self) -> None:\n        pass\nif __name__ == "__main__":\n    App().run()'},
        {'file_type': 'code', 'filename': 'test_main.py', 'file_path': 'tests/test_main.py',
         'content_preview': 'import pytest\ndef test_app(): pass'},
        {'file_type': 'code', 'filename': '__init__.py', 'file_path': 'src/__init__.py',
         'content_preview': '"""Package init."""'},
        {'file_type': 'content', 'filename': 'README.md', 'file_path': 'README.md',
         'content_preview': '# My Project'},
        {'file_type': 'content', 'filename': 'requirements.txt', 'file_path': 'requirements.txt',
         'content_preview': 'pytest\nflask'},
        {'file_type': 'content', 'filename': '.gitignore', 'file_path': '.gitignore',
         'content_preview': '__pycache__\n*.pyc'},
    ]}


@pytest.fixture
def javascript_project():
    return {'files': [
        {'file_type': 'code', 'filename': 'index.js', 'file_path': 'src/index.js',
         'content_preview': 'import express from "express";\nexport default function handler() {}'},
        {'file_type': 'code', 'filename': 'app.ts', 'file_path': 'src/app.ts',
         'content_preview': 'class App { start() {} }'},
        {'file_type': 'code', 'filename': 'index.test.js', 'file_path': '__tests__/index.test.js',
         'content_preview': 'const jest = require("jest");\ntest("works", () => {});'},
        {'file_type': 'content', 'filename': 'package.json', 'file_path': 'package.json',
         'content_preview': '{"name": "my-app"}'},
        {'file_type': 'content', 'filename': 'package-lock.json', 'file_path': 'package-lock.json',
         'content_preview': '{}'},
        {'file_type': 'content', 'filename': 'README.md', 'file_path': 'README.md',
         'content_preview': '# JS Project'},
        {'file_type': 'content', 'filename': '.gitignore', 'file_path': '.gitignore',
         'content_preview': 'node_modules'},
    ]}


@pytest.fixture
def java_project():
    return {'files': [
        {'file_type': 'code', 'filename': 'App.java', 'file_path': 'src/main/java/App.java',
         'content_preview': 'package com.example;\npublic class App {\n    @Override\n    public void run() throws Exception {}\n}'},
        {'file_type': 'code', 'filename': 'AppTest.java', 'file_path': 'src/test/java/AppTest.java',
         'content_preview': 'import org.junit.Test;\n@Test\npublic class AppTest {}'},
        {'file_type': 'content', 'filename': 'pom.xml', 'file_path': 'pom.xml',
         'content_preview': '<project></project>'},
        {'file_type': 'content', 'filename': 'README.md', 'file_path': 'README.md',
         'content_preview': '# Java Project'},
        {'file_type': 'content', 'filename': '.gitignore', 'file_path': '.gitignore',
         'content_preview': 'target\nbuild'},
    ]}


@pytest.fixture
def c_project():
    return {'files': [
        {'file_type': 'code', 'filename': 'main.c', 'file_path': 'src/main.c',
         'content_preview': '#include "utils.h"\nint main() { char *p = malloc(10); free(p); return 0; }'},
        {'file_type': 'code', 'filename': 'utils.c', 'file_path': 'src/utils.c',
         'content_preview': '#include "utils.h"\nvoid helper() {}'},
        {'file_type': 'code', 'filename': 'utils.h', 'file_path': 'include/utils.h',
         'content_preview': '#ifndef UTILS_H\n#define UTILS_H\nstruct Data { int x; };\nvoid helper();\n#endif'},
        {'file_type': 'code', 'filename': 'test_main.c', 'file_path': 'test/test_main.c',
         'content_preview': '#include <assert.h>\nvoid test_main() { assert(1); }'},
        {'file_type': 'content', 'filename': 'Makefile', 'file_path': 'Makefile',
         'content_preview': 'all: main.o utils.o'},
        {'file_type': 'content', 'filename': 'README.md', 'file_path': 'README.md',
         'content_preview': '# C Project'},
        {'file_type': 'content', 'filename': '.gitignore', 'file_path': '.gitignore',
         'content_preview': '*.o\n*.out'},
    ]}


# --- Factory function tests ---

class TestGetRubricForLanguage:
    """Test the factory function returns correct rubric instances."""

    def test_returns_python_rubric(self):
        rubric = get_rubric_for_language('python')
        assert isinstance(rubric, PythonRubric)

    def test_returns_javascript_rubric(self):
        rubric = get_rubric_for_language('javascript')
        assert isinstance(rubric, JavaScriptRubric)

    def test_returns_typescript_uses_js_rubric(self):
        rubric = get_rubric_for_language('typescript')
        assert isinstance(rubric, JavaScriptRubric)

    def test_returns_java_rubric(self):
        rubric = get_rubric_for_language('java')
        assert isinstance(rubric, JavaRubric)

    def test_returns_c_rubric(self):
        rubric = get_rubric_for_language('c')
        assert isinstance(rubric, CRubric)

    def test_returns_none_for_unknown(self):
        assert get_rubric_for_language('brainfuck') is None

    def test_case_insensitive(self):
        assert isinstance(get_rubric_for_language('Python'), PythonRubric)
        assert isinstance(get_rubric_for_language('JAVA'), JavaRubric)

    def test_strips_whitespace(self):
        assert isinstance(get_rubric_for_language('  python  '), PythonRubric)


# --- Return structure tests ---

class TestEvaluateReturnStructure:
    """Test that evaluate() returns the expected dict structure for all rubrics."""

    @pytest.mark.parametrize("rubric_cls", [PythonRubric, JavaScriptRubric, JavaRubric, CRubric])
    def test_has_required_keys(self, rubric_cls, empty_project):
        result = rubric_cls().evaluate(empty_project)
        assert 'overall_score' in result
        assert 'category_scores' in result
        assert 'rubric_evaluation' in result
        assert 'evidence' in result

    @pytest.mark.parametrize("rubric_cls", [PythonRubric, JavaScriptRubric, JavaRubric, CRubric])
    def test_overall_score_is_float(self, rubric_cls, empty_project):
        result = rubric_cls().evaluate(empty_project)
        assert isinstance(result['overall_score'], float)

    @pytest.mark.parametrize("rubric_cls", [PythonRubric, JavaScriptRubric, JavaRubric, CRubric])
    def test_overall_score_in_range(self, rubric_cls, empty_project):
        result = rubric_cls().evaluate(empty_project)
        assert 0.0 <= result['overall_score'] <= 100.0

    @pytest.mark.parametrize("rubric_cls", [PythonRubric, JavaScriptRubric, JavaRubric, CRubric])
    def test_category_scores_has_all_categories(self, rubric_cls, empty_project):
        result = rubric_cls().evaluate(empty_project)
        expected_categories = {cat.value for cat in RubricCategory}
        assert set(result['category_scores'].keys()) == expected_categories

    @pytest.mark.parametrize("rubric_cls", [PythonRubric, JavaScriptRubric, JavaRubric, CRubric])
    def test_rubric_evaluation_has_rubric_type(self, rubric_cls, empty_project):
        result = rubric_cls().evaluate(empty_project)
        assert 'rubric_type' in result['rubric_evaluation']
        assert result['rubric_evaluation']['rubric_type'] == rubric_cls().language


# --- Empty project tests ---

class TestEmptyProject:
    """All rubrics should score 0 on an empty project."""

    @pytest.mark.parametrize("rubric_cls", [PythonRubric, JavaScriptRubric, JavaRubric, CRubric])
    def test_empty_project_scores_zero(self, rubric_cls, empty_project):
        result = rubric_cls().evaluate(empty_project)
        assert result['overall_score'] == 0.0


# --- Python rubric scoring tests ---

class TestPythonRubricScoring:
    """Test that PythonRubric scores known projects correctly."""

    def test_scores_above_zero_for_real_project(self, python_project):
        result = PythonRubric().evaluate(python_project)
        assert result['overall_score'] > 0.0

    def test_detects_python_files(self, python_project):
        result = PythonRubric().evaluate(python_project)
        assert result['evidence']['py_files'] >= 1

    def test_detects_test_files(self, python_project):
        result = PythonRubric().evaluate(python_project)
        assert result['evidence']['test_file_count'] >= 1

    def test_detects_readme(self, python_project):
        result = PythonRubric().evaluate(python_project)
        assert result['evidence']['has_readme'] is True

    def test_detects_requirements(self, python_project):
        result = PythonRubric().evaluate(python_project)
        assert result['evidence']['has_requirements'] is True

    def test_detects_oop(self, python_project):
        result = PythonRubric().evaluate(python_project)
        assert result['evidence']['uses_oop'] is True


# --- JavaScript rubric scoring tests ---

class TestJavaScriptRubricScoring:
    """Test that JavaScriptRubric scores known projects correctly."""

    def test_scores_above_zero_for_real_project(self, javascript_project):
        result = JavaScriptRubric().evaluate(javascript_project)
        assert result['overall_score'] > 0.0

    def test_detects_js_files(self, javascript_project):
        result = JavaScriptRubric().evaluate(javascript_project)
        assert result['evidence']['js_files'] >= 1

    def test_detects_typescript(self, javascript_project):
        result = JavaScriptRubric().evaluate(javascript_project)
        assert result['evidence']['uses_typescript'] is True

    def test_detects_modules(self, javascript_project):
        result = JavaScriptRubric().evaluate(javascript_project)
        assert result['evidence']['uses_modules'] is True

    def test_detects_package_json(self, javascript_project):
        result = JavaScriptRubric().evaluate(javascript_project)
        assert result['evidence']['has_package_json'] is True


# --- Java rubric scoring tests ---

class TestJavaRubricScoring:
    """Test that JavaRubric scores known projects correctly."""

    def test_scores_above_zero_for_real_project(self, java_project):
        result = JavaRubric().evaluate(java_project)
        assert result['overall_score'] > 0.0

    def test_detects_java_files(self, java_project):
        result = JavaRubric().evaluate(java_project)
        assert result['evidence']['java_files'] >= 1

    def test_detects_packages(self, java_project):
        result = JavaRubric().evaluate(java_project)
        assert result['evidence']['uses_packages'] is True

    def test_detects_maven(self, java_project):
        result = JavaRubric().evaluate(java_project)
        assert result['evidence']['uses_maven'] is True

    def test_detects_junit(self, java_project):
        result = JavaRubric().evaluate(java_project)
        assert result['evidence']['uses_junit'] is True


# --- C rubric scoring tests ---

class TestCRubricScoring:
    """Test that CRubric scores known projects correctly."""

    def test_scores_above_zero_for_real_project(self, c_project):
        result = CRubric().evaluate(c_project)
        assert result['overall_score'] > 0.0

    def test_detects_c_files(self, c_project):
        result = CRubric().evaluate(c_project)
        assert result['evidence']['c_files'] >= 1

    def test_detects_header_files(self, c_project):
        result = CRubric().evaluate(c_project)
        assert result['evidence']['header_files'] >= 1

    def test_detects_structs(self, c_project):
        result = CRubric().evaluate(c_project)
        assert result['evidence']['uses_structs'] is True

    def test_detects_makefile(self, c_project):
        result = CRubric().evaluate(c_project)
        assert result['evidence']['has_makefile'] is True

    def test_detects_header_guards(self, c_project):
        result = CRubric().evaluate(c_project)
        assert result['evidence']['uses_header_guards'] is True


# --- Import compatibility tests ---

class TestImportCompatibility:
    """Verify all public symbols are importable from the original module path."""

    def test_import_from_language_rubrics(self):
        from app.services.evaluation.language_rubrics import (
            RubricCategory,
            LanguageRubric,
            PythonRubric,
            JavaScriptRubric,
            JavaRubric,
            CRubric,
            get_rubric_for_language,
        )
        assert RubricCategory is not None
        assert LanguageRubric is not None

    def test_import_from_evaluation_package(self):
        from app.services.evaluation import (
            get_rubric_for_language,
            PythonRubric,
            JavaScriptRubric,
            JavaRubric,
            CRubric,
        )
        assert get_rubric_for_language is not None

    def test_import_in_project_evaluation_service(self):
        from app.services.evaluation.project_evaluation_service import ProjectEvaluationService
        assert ProjectEvaluationService is not None


# --- Base class tests ---

class TestLanguageRubricBase:
    """Test the base LanguageRubric class."""

    def test_default_language_is_unknown(self):
        rubric = LanguageRubric()
        assert rubric.language == "Unknown"

    def test_category_weights_sum_to_one(self):
        rubric = LanguageRubric()
        total = sum(rubric.category_weights.values())
        assert abs(total - 1.0) < 0.01

    def test_calculate_overall_score_empty(self):
        rubric = LanguageRubric()
        assert rubric._calculate_overall_score({}) == 0.0

    def test_calculate_overall_score_perfect(self):
        rubric = LanguageRubric()
        scores = {cat: 100.0 for cat in RubricCategory}
        assert rubric._calculate_overall_score(scores) == 100.0

    def test_calculate_overall_score_zero(self):
        rubric = LanguageRubric()
        scores = {cat: 0.0 for cat in RubricCategory}
        assert rubric._calculate_overall_score(scores) == 0.0
