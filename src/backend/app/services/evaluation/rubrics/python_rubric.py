"""Python project evaluation rubric."""

from typing import Dict, List

from .base import LanguageRubric


class PythonRubric(LanguageRubric):
	"""Python project evaluation rubric."""

	def __init__(self):
		super().__init__()
		self.language = "python"

	def _evaluate_code_structure(self, files: List[Dict], evidence: Dict) -> float:
		"""Evaluate Python code structure - modules, classes, functions."""
		score = 0.0
		max_score = 0.0

		# Check for proper module structure
		py_files = [f for f in files if f.get('file_type') == 'code' and f.get('filename', '').endswith('.py')]
		evidence['py_files'] = len(py_files)
		evidence['has_modules'] = len(py_files) > 1

		if len(py_files) > 1:
			score += 15
		max_score += 15

		# Check for major structural patterns
		has_main = any('__main__' in f.get('content_preview', '') for f in py_files)
		evidence['has_main_entry'] = has_main
		if has_main:
			score += 10
		max_score += 10

		# Check for class definitions (OOP)
		has_classes = any('class ' in f.get('content_preview', '') for f in py_files)
		evidence['uses_oop'] = has_classes
		if has_classes:
			score += 15
		max_score += 15

		# Check for functions
		has_functions = any('def ' in f.get('content_preview', '') for f in py_files)
		evidence['has_functions'] = has_functions
		if has_functions:
			score += 15
		max_score += 15

		return (score / max_score * 100) if max_score > 0 else 0.0

	def _evaluate_testing(self, files: List[Dict], evidence: Dict) -> float:
		"""Evaluate testing presence and structure."""
		score = 0.0
		max_score = 0.0

		# Check for test files
		test_files = [
			f for f in files
			if f.get('file_type') == 'code' and 'test' in f.get('filename', '').lower()
		]
		evidence['test_file_count'] = len(test_files)

		if len(test_files) > 0:
			score += 30
		max_score += 30

		# Check for test frameworks
		has_pytest = any('pytest' in f.get('content_preview', '') or 'import pytest' in f.get('content_preview', '') for f in files)
		has_unittest = any('unittest' in f.get('content_preview', '') for f in files)

		evidence['uses_pytest'] = has_pytest
		evidence['uses_unittest'] = has_unittest

		if has_pytest or has_unittest:
			score += 20
		max_score += 20

		# Check for pytest.ini or setup.cfg
		config_files = [f for f in files if f.get('filename') in ['pytest.ini', 'setup.cfg', 'pyproject.toml']]
		evidence['has_test_config'] = len(config_files) > 0

		if len(config_files) > 0:
			score += 15
		max_score += 15

		# Check for __init__.py indicating package structure
		has_init_files = any(f.get('filename') == '__init__.py' for f in files)
		evidence['has_package_init'] = has_init_files

		if has_init_files:
			score += 20
		max_score += 20

		return (score / max_score * 100) if max_score > 0 else 0.0

	def _evaluate_documentation(self, files: List[Dict], evidence: Dict) -> float:
		"""Evaluate documentation quality."""
		score = 0.0
		max_score = 0.0

		# Check for README
		has_readme = any(f.get('filename', '').lower() in ['readme.md', 'readme.txt', 'readme.rst'] for f in files)
		evidence['has_readme'] = has_readme

		if has_readme:
			score += 25
		max_score += 25

		# Check for docstrings
		has_docstrings = any('"""' in f.get('content_preview', '') or "'''" in f.get('content_preview', '') for f in files if f.get('file_type') == 'code')
		evidence['has_docstrings'] = has_docstrings

		if has_docstrings:
			score += 25
		max_score += 25

		# Check for comments
		has_comments = any('#' in f.get('content_preview', '') for f in files if f.get('file_type') == 'code')
		evidence['has_comments'] = has_comments

		if has_comments:
			score += 25
		max_score += 25

		# Check for CONTRIBUTING, LICENSE files
		has_meta_docs = any(f.get('filename', '').lower() in ['contributing.md', 'license', 'contributing.txt'] for f in files)
		evidence['has_meta_docs'] = has_meta_docs

		if has_meta_docs:
			score += 25
		max_score += 25

		return (score / max_score * 100) if max_score > 0 else 0.0

	def _evaluate_dependencies(self, files: List[Dict], evidence: Dict) -> float:
		"""Evaluate dependency management."""
		score = 0.0
		max_score = 0.0

		# Check for requirements.txt
		has_requirements = any(f.get('filename') in ['requirements.txt', 'requirements-dev.txt'] for f in files)
		evidence['has_requirements'] = has_requirements

		if has_requirements:
			score += 30
		max_score += 30

		# Check for setup.py or pyproject.toml
		has_setup = any(f.get('filename') in ['setup.py', 'pyproject.toml', 'setup.cfg'] for f in files)
		evidence['has_setup_config'] = has_setup

		if has_setup:
			score += 30
		max_score += 30

		# Check for Pipfile (pipenv)
		has_pipfile = any(f.get('filename') == 'Pipfile' for f in files)
		evidence['uses_pipenv'] = has_pipfile

		if has_pipfile:
			score += 20
		max_score += 20

		# Check for .python-version
		has_python_version = any(f.get('filename') == '.python-version' for f in files)
		evidence['specifies_python_version'] = has_python_version

		if has_python_version:
			score += 20
		max_score += 20

		return (score / max_score * 100) if max_score > 0 else 0.0

	def _evaluate_organization(self, files: List[Dict], evidence: Dict) -> float:
		"""Evaluate project organization and structure."""
		score = 0.0
		max_score = 0.0

		# Check for src/ or app/ directories
		folders = set()
		for f in files:
			path_parts = f.get('file_path', '').split('/')
			if len(path_parts) > 1:
				folders.add(path_parts[0])

		has_src_structure = any(folder in folders for folder in ['src', 'app', 'lib'])
		evidence['has_src_structure'] = has_src_structure

		if has_src_structure:
			score += 25
		max_score += 25

		# Check for tests directory
		has_tests_dir = 'tests' in folders or 'test' in folders
		evidence['has_tests_directory'] = has_tests_dir

		if has_tests_dir:
			score += 25
		max_score += 25

		# Check for docs directory
		has_docs_dir = 'docs' in folders
		evidence['has_docs_directory'] = has_docs_dir

		if has_docs_dir:
			score += 25
		max_score += 25

		# Check for .gitignore
		has_gitignore = any(f.get('filename') == '.gitignore' for f in files)
		evidence['has_gitignore'] = has_gitignore

		if has_gitignore:
			score += 25
		max_score += 25

		return (score / max_score * 100) if max_score > 0 else 0.0

	def _evaluate_best_practices(self, files: List[Dict], evidence: Dict) -> float:
		"""Evaluate adherence to Python best practices."""
		score = 0.0
		max_score = 0.0

		# Check for type hints
		has_type_hints = any('-> ' in f.get('content_preview', '') or ': int' in f.get('content_preview', '') for f in files if f.get('file_type') == 'code')
		evidence['has_type_hints'] = has_type_hints

		if has_type_hints:
			score += 20
		max_score += 20

		# Check for linting config (pylint, flake8)
		has_linting_config = any(f.get('filename') in ['.pylintrc', '.flake8', 'pyproject.toml'] for f in files)
		evidence['has_linting_config'] = has_linting_config

		if has_linting_config:
			score += 20
		max_score += 20

		# Check for CI/CD config
		has_ci_config = any(f.get('filename') in ['.github/workflows', '.gitlab-ci.yml', '.travis.yml'] or '.github' in f.get('file_path', '') for f in files)
		evidence['has_ci_config'] = has_ci_config

		if has_ci_config:
			score += 25
		max_score += 25

		# Check for .env or config files
		has_config_files = any(f.get('filename') in ['.env.example', 'config.py', 'settings.py'] for f in files)
		evidence['has_config_files'] = has_config_files

		if has_config_files:
			score += 20
		max_score += 20

		# Check for virtual environment indicator
		has_venv = any(f.get('filename') in ['pyproject.toml', 'Pipfile', 'poetry.lock'] for f in files)
		evidence['uses_virtual_env'] = has_venv

		if has_venv:
			score += 15
		max_score += 15

		return (score / max_score * 100) if max_score > 0 else 0.0
