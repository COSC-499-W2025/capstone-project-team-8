"""
Language-Specific Rubrics Service

Defines evaluation criteria and scoring for different programming languages.
Each language has specific indicators of success and quality metrics.
"""

from typing import Dict, Any, List
from enum import Enum


class RubricCategory(Enum):
	"""Categories evaluated in the rubric."""
	CODE_STRUCTURE = "code_structure"
	TESTING = "testing"
	DOCUMENTATION = "documentation"
	DEPENDENCY_MANAGEMENT = "dependency_management"
	PROJECT_ORGANIZATION = "project_organization"
	BEST_PRACTICES = "best_practices"


class LanguageRubric:
	"""Base class for language-specific rubrics."""
	
	def __init__(self):
		self.language = "Unknown"
		self.category_weights = {
			RubricCategory.CODE_STRUCTURE: 0.25,
			RubricCategory.TESTING: 0.20,
			RubricCategory.DOCUMENTATION: 0.15,
			RubricCategory.DEPENDENCY_MANAGEMENT: 0.15,
			RubricCategory.PROJECT_ORGANIZATION: 0.15,
			RubricCategory.BEST_PRACTICES: 0.10,
		}
	
	def evaluate(self, project_analysis: Dict[str, Any]) -> Dict[str, Any]:
		"""
		Evaluate a project against the language rubric.
		
		Returns:
			Dict containing:
				- overall_score: 0-100
				- category_scores: dict of category -> score
				- rubric_evaluation: detailed evaluation details
				- evidence: supporting data
		"""
		raise NotImplementedError
	
	def _calculate_overall_score(self, category_scores: Dict[str, float]) -> float:
		"""Calculate weighted overall score from category scores."""
		total_weight = sum(
			self.category_weights.get(cat, 0) 
			for cat in category_scores.keys()
		)
		
		if total_weight == 0:
			return 0.0
		
		weighted_sum = sum(
			score * self.category_weights.get(cat, 0)
			for cat, score in category_scores.items()
		)
		
		# Category scores are already 0-100, so just return weighted average
		weighted_average = weighted_sum / total_weight
		return min(100.0, max(0.0, weighted_average))


class PythonRubric(LanguageRubric):
	"""Python project evaluation rubric."""
	
	def __init__(self):
		super().__init__()
		self.language = "python"
	
	def evaluate(self, project_analysis: Dict[str, Any]) -> Dict[str, Any]:
		"""Evaluate Python project."""
		files = project_analysis.get('files', [])
		
		category_scores = {}
		evidence = {}
		
		# Code Structure
		category_scores[RubricCategory.CODE_STRUCTURE] = self._evaluate_code_structure(
			files, evidence
		)
		
		# Testing
		category_scores[RubricCategory.TESTING] = self._evaluate_testing(
			files, evidence
		)
		
		# Documentation
		category_scores[RubricCategory.DOCUMENTATION] = self._evaluate_documentation(
			files, evidence
		)
		
		# Dependency Management
		category_scores[RubricCategory.DEPENDENCY_MANAGEMENT] = self._evaluate_dependencies(
			files, evidence
		)
		
		# Project Organization
		category_scores[RubricCategory.PROJECT_ORGANIZATION] = self._evaluate_organization(
			files, evidence
		)
		
		# Best Practices
		category_scores[RubricCategory.BEST_PRACTICES] = self._evaluate_best_practices(
			files, evidence
		)
		
		overall_score = self._calculate_overall_score(category_scores)
		
		return {
			'overall_score': overall_score,
			'category_scores': {cat.value: score for cat, score in category_scores.items()},
			'rubric_evaluation': self._build_rubric_details(category_scores),
			'evidence': evidence,
		}
	
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
	
	def _build_rubric_details(self, category_scores: Dict) -> Dict[str, Any]:
		"""Build detailed rubric evaluation report."""
		return {
			"rubric_type": "python",
			"evaluation_date": str(self._get_timestamp()),
			"category_details": {
				cat.value: {
					"score": score,
					"weight": self.category_weights[cat],
					"weighted_contribution": score * self.category_weights[cat] / 100,
				}
				for cat, score in category_scores.items()
			},
		}
	
	@staticmethod
	def _get_timestamp():
		from datetime import datetime
		return datetime.now()


class JavaScriptRubric(LanguageRubric):
	"""JavaScript/TypeScript project evaluation rubric."""
	
	def __init__(self):
		super().__init__()
		self.language = "javascript"
	
	def evaluate(self, project_analysis: Dict[str, Any]) -> Dict[str, Any]:
		"""Evaluate JavaScript/TypeScript project."""
		files = project_analysis.get('files', [])
		
		category_scores = {}
		evidence = {}
		
		# Code Structure
		category_scores[RubricCategory.CODE_STRUCTURE] = self._evaluate_code_structure(
			files, evidence
		)
		
		# Testing
		category_scores[RubricCategory.TESTING] = self._evaluate_testing(
			files, evidence
		)
		
		# Documentation
		category_scores[RubricCategory.DOCUMENTATION] = self._evaluate_documentation(
			files, evidence
		)
		
		# Dependency Management
		category_scores[RubricCategory.DEPENDENCY_MANAGEMENT] = self._evaluate_dependencies(
			files, evidence
		)
		
		# Project Organization
		category_scores[RubricCategory.PROJECT_ORGANIZATION] = self._evaluate_organization(
			files, evidence
		)
		
		# Best Practices
		category_scores[RubricCategory.BEST_PRACTICES] = self._evaluate_best_practices(
			files, evidence
		)
		
		overall_score = self._calculate_overall_score(category_scores)
		
		return {
			'overall_score': overall_score,
			'category_scores': {cat.value: score for cat, score in category_scores.items()},
			'rubric_evaluation': self._build_rubric_details(category_scores),
			'evidence': evidence,
		}
	
	def _evaluate_code_structure(self, files: List[Dict], evidence: Dict) -> float:
		"""Evaluate JavaScript code structure."""
		score = 0.0
		max_score = 0.0
		
		# Check for module structure
		js_files = [f for f in files if f.get('file_type') == 'code' and f.get('filename', '').endswith(('.js', '.ts', '.tsx', '.jsx'))]
		evidence['js_files'] = len(js_files)
		
		if len(js_files) > 1:
			score += 20
		max_score += 20
		
		# Check for imports/exports
		has_modules = any('import ' in f.get('content_preview', '') or 'export ' in f.get('content_preview', '') for f in js_files)
		evidence['uses_modules'] = has_modules
		
		if has_modules:
			score += 15
		max_score += 15
		
		# Check for classes
		has_classes = any('class ' in f.get('content_preview', '') for f in js_files)
		evidence['uses_classes'] = has_classes
		
		if has_classes:
			score += 15
		max_score += 15
		
		# Check for functions/arrow functions
		has_functions = any('function ' in f.get('content_preview', '') or '=>' in f.get('content_preview', '') for f in js_files)
		evidence['has_functions'] = has_functions
		
		if has_functions:
			score += 15
		max_score += 15
		
		# Check for TypeScript
		ts_files = [f for f in files if f.get('filename', '').endswith(('.ts', '.tsx'))]
		evidence['uses_typescript'] = len(ts_files) > 0
		
		if len(ts_files) > 0:
			score += 20
		max_score += 20
		
		return (score / max_score * 100) if max_score > 0 else 0.0
	
	def _evaluate_testing(self, files: List[Dict], evidence: Dict) -> float:
		"""Evaluate testing in JavaScript project."""
		score = 0.0
		max_score = 0.0
		
		# Check for test files
		test_files = [
			f for f in files 
			if f.get('file_type') == 'code' and any(pattern in f.get('filename', '').lower() for pattern in ['test', 'spec'])
		]
		evidence['test_file_count'] = len(test_files)
		
		if len(test_files) > 0:
			score += 25
		max_score += 25
		
		# Check for test frameworks
		has_jest = any('jest' in f.get('content_preview', '').lower() for f in files)
		has_mocha = any('mocha' in f.get('content_preview', '').lower() for f in files)
		has_vitest = any('vitest' in f.get('content_preview', '').lower() for f in files)
		
		evidence['uses_jest'] = has_jest
		evidence['uses_mocha'] = has_mocha
		evidence['uses_vitest'] = has_vitest
		
		if has_jest or has_mocha or has_vitest:
			score += 25
		max_score += 25
		
		# Check for test configuration
		has_test_config = any(f.get('filename') in ['jest.config.js', 'jest.config.json', '.mocharc.json', 'vitest.config.js'] for f in files)
		evidence['has_test_config'] = has_test_config
		
		if has_test_config:
			score += 20
		max_score += 20
		
		# Check for coverage config
		has_coverage_config = any('coverage' in f.get('filename', '').lower() or 'nyc' in f.get('filename', '').lower() for f in files)
		evidence['has_coverage_config'] = has_coverage_config
		
		if has_coverage_config:
			score += 15
		max_score += 15
		
		return (score / max_score * 100) if max_score > 0 else 0.0
	
	def _evaluate_documentation(self, files: List[Dict], evidence: Dict) -> float:
		"""Evaluate documentation in JavaScript project."""
		score = 0.0
		max_score = 0.0
		
		# Check for README
		has_readme = any(f.get('filename', '').lower() in ['readme.md', 'readme.txt'] for f in files)
		evidence['has_readme'] = has_readme
		
		if has_readme:
			score += 25
		max_score += 25
		
		# Check for JSDoc comments
		has_jsdoc = any('/**' in f.get('content_preview', '') or '@param' in f.get('content_preview', '') for f in files if f.get('file_type') == 'code')
		evidence['has_jsdoc'] = has_jsdoc
		
		if has_jsdoc:
			score += 25
		max_score += 25
		
		# Check for comments
		has_comments = any('//' in f.get('content_preview', '') for f in files if f.get('file_type') == 'code')
		evidence['has_comments'] = has_comments
		
		if has_comments:
			score += 25
		max_score += 25
		
		# Check for documentation files
		has_docs = any('docs' in f.get('file_path', '').lower() or f.get('filename', '').endswith(('.md', '.mdx')) for f in files)
		evidence['has_docs'] = has_docs
		
		if has_docs:
			score += 25
		max_score += 25
		
		return (score / max_score * 100) if max_score > 0 else 0.0
	
	def _evaluate_dependencies(self, files: List[Dict], evidence: Dict) -> float:
		"""Evaluate dependency management."""
		score = 0.0
		max_score = 0.0
		
		# Check for package.json
		has_package_json = any(f.get('filename') == 'package.json' for f in files)
		evidence['has_package_json'] = has_package_json
		
		if has_package_json:
			score += 35
		max_score += 35
		
		# Check for lock file
		has_lock = any(f.get('filename') in ['package-lock.json', 'yarn.lock', 'pnpm-lock.yaml'] for f in files)
		evidence['has_lock_file'] = has_lock
		
		if has_lock:
			score += 30
		max_score += 30
		
		# Check for .npmrc or .yarnrc
		has_npm_config = any(f.get('filename') in ['.npmrc', '.yarnrc'] for f in files)
		evidence['has_npm_config'] = has_npm_config
		
		if has_npm_config:
			score += 20
		max_score += 20
		
		# Check for node_modules or .gitignore mention
		has_node_ignore = any(f.get('filename') == '.gitignore' and 'node_modules' in f.get('content_preview', '') for f in files)
		evidence['ignores_node_modules'] = has_node_ignore
		
		if has_node_ignore:
			score += 15
		max_score += 15
		
		return (score / max_score * 100) if max_score > 0 else 0.0
	
	def _evaluate_organization(self, files: List[Dict], evidence: Dict) -> float:
		"""Evaluate project organization."""
		score = 0.0
		max_score = 0.0
		
		# Check for source structure
		folders = set()
		for f in files:
			path_parts = f.get('file_path', '').split('/')
			if len(path_parts) > 1:
				folders.add(path_parts[0])
		
		has_src_structure = any(folder in folders for folder in ['src', 'lib', 'app', 'components'])
		evidence['has_src_structure'] = has_src_structure
		
		if has_src_structure:
			score += 20
		max_score += 20
		
		# Check for tests directory
		has_tests_dir = '__tests__' in folders or 'tests' in folders or 'test' in folders
		evidence['has_tests_directory'] = has_tests_dir
		
		if has_tests_dir:
			score += 20
		max_score += 20
		
		# Check for public/static directory
		has_public = 'public' in folders or 'static' in folders
		evidence['has_public_directory'] = has_public
		
		if has_public:
			score += 15
		max_score += 15
		
		# Check for .gitignore
		has_gitignore = any(f.get('filename') == '.gitignore' for f in files)
		evidence['has_gitignore'] = has_gitignore
		
		if has_gitignore:
			score += 20
		max_score += 20
		
		# Check for environment files
		has_env_files = any(f.get('filename') in ['.env.example', '.env.local', '.env.sample'] for f in files)
		evidence['has_env_files'] = has_env_files
		
		if has_env_files:
			score += 15
		max_score += 15
		
		# Check for configuration files
		has_config = any(f.get('filename') in ['.eslintrc', '.prettierrc', 'tsconfig.json'] for f in files)
		evidence['has_config_files'] = has_config
		
		if has_config:
			score += 10
		max_score += 10
		
		return (score / max_score * 100) if max_score > 0 else 0.0
	
	def _evaluate_best_practices(self, files: List[Dict], evidence: Dict) -> float:
		"""Evaluate best practices in JavaScript project."""
		score = 0.0
		max_score = 0.0
		
		# Check for linting
		has_eslint = any(f.get('filename') in ['.eslintrc', '.eslintrc.js', '.eslintrc.json', 'eslint.config.mjs'] for f in files)
		evidence['has_eslint'] = has_eslint
		
		if has_eslint:
			score += 20
		max_score += 20
		
		# Check for code formatting
		has_prettier = any(f.get('filename') in ['.prettierrc', '.prettierrc.json', '.prettierignore'] for f in files)
		evidence['has_prettier'] = has_prettier
		
		if has_prettier:
			score += 20
		max_score += 20
		
		# Check for build tool
		has_build_tool = any(f.get('filename') in ['webpack.config.js', 'vite.config.js', 'rollup.config.js', 'build.js', 'tsconfig.json'] for f in files)
		evidence['has_build_tool'] = has_build_tool
		
		if has_build_tool:
			score += 20
		max_score += 20
		
		# Check for CI/CD config
		has_ci = any('.github' in f.get('file_path', '') or '.gitlab-ci.yml' in f.get('filename', '') for f in files)
		evidence['has_ci_config'] = has_ci
		
		if has_ci:
			score += 20
		max_score += 20
		
		# Check for Dockerfile (containerization)
		has_docker = any(f.get('filename') in ['Dockerfile', 'docker-compose.yml'] for f in files)
		evidence['has_docker'] = has_docker
		
		if has_docker:
			score += 20
		max_score += 20
		
		return (score / max_score * 100) if max_score > 0 else 0.0
	
	def _build_rubric_details(self, category_scores: Dict) -> Dict[str, Any]:
		"""Build detailed rubric evaluation report."""
		return {
			"rubric_type": "javascript",
			"evaluation_date": str(self._get_timestamp()),
			"category_details": {
				cat.value: {
					"score": score,
					"weight": self.category_weights[cat],
					"weighted_contribution": score * self.category_weights[cat] / 100,
				}
				for cat, score in category_scores.items()
			},
		}
	
	@staticmethod
	def _get_timestamp():
		from datetime import datetime
		return datetime.now()


class JavaRubric(LanguageRubric):
	"""Java project evaluation rubric."""
	
	def __init__(self):
		super().__init__()
		self.language = "java"
	
	def evaluate(self, project_analysis: Dict[str, Any]) -> Dict[str, Any]:
		"""Evaluate Java project."""
		files = project_analysis.get('files', [])
		
		category_scores = {}
		evidence = {}
		
		# Code Structure
		category_scores[RubricCategory.CODE_STRUCTURE] = self._evaluate_code_structure(
			files, evidence
		)
		
		# Testing
		category_scores[RubricCategory.TESTING] = self._evaluate_testing(
			files, evidence
		)
		
		# Documentation
		category_scores[RubricCategory.DOCUMENTATION] = self._evaluate_documentation(
			files, evidence
		)
		
		# Dependency Management
		category_scores[RubricCategory.DEPENDENCY_MANAGEMENT] = self._evaluate_dependencies(
			files, evidence
		)
		
		# Project Organization
		category_scores[RubricCategory.PROJECT_ORGANIZATION] = self._evaluate_organization(
			files, evidence
		)
		
		# Best Practices
		category_scores[RubricCategory.BEST_PRACTICES] = self._evaluate_best_practices(
			files, evidence
		)
		
		overall_score = self._calculate_overall_score(category_scores)
		
		return {
			'overall_score': overall_score,
			'category_scores': {cat.value: score for cat, score in category_scores.items()},
			'rubric_evaluation': self._build_rubric_details(category_scores),
			'evidence': evidence,
		}
	
	def _evaluate_code_structure(self, files: List[Dict], evidence: Dict) -> float:
		"""Evaluate Java code structure."""
		score = 0.0
		max_score = 0.0
		
		# Check for Java files
		java_files = [f for f in files if f.get('file_type') == 'code' and f.get('filename', '').endswith('.java')]
		evidence['java_files'] = len(java_files)
		
		if len(java_files) > 0:
			score += 15
		max_score += 15
		
		# Check for package structure
		has_packages = any('package ' in f.get('content_preview', '') for f in java_files)
		evidence['uses_packages'] = has_packages
		
		if has_packages:
			score += 20
		max_score += 20
		
		# Check for classes
		has_classes = any('class ' in f.get('content_preview', '') or 'interface ' in f.get('content_preview', '') for f in java_files)
		evidence['defines_classes'] = has_classes
		
		if has_classes:
			score += 20
		max_score += 20
		
		# Check for enums
		has_enums = any('enum ' in f.get('content_preview', '') for f in java_files)
		evidence['uses_enums'] = has_enums
		
		if has_enums:
			score += 15
		max_score += 15
		
		# Check for annotations
		has_annotations = any('@' in f.get('content_preview', '') for f in java_files)
		evidence['uses_annotations'] = has_annotations
		
		if has_annotations:
			score += 15
		max_score += 15
		
		# Check for access modifiers
		has_access_modifiers = any('public ' in f.get('content_preview', '') or 'private ' in f.get('content_preview', '') for f in java_files)
		evidence['uses_access_modifiers'] = has_access_modifiers
		
		if has_access_modifiers:
			score += 15
		max_score += 15
		
		return (score / max_score * 100) if max_score > 0 else 0.0
	
	def _evaluate_testing(self, files: List[Dict], evidence: Dict) -> float:
		"""Evaluate testing in Java project."""
		score = 0.0
		max_score = 0.0
		
		# Check for test files
		test_files = [
			f for f in files 
			if f.get('file_type') == 'code' and 'test' in f.get('filename', '').lower() and f.get('filename', '').endswith('.java')
		]
		evidence['test_file_count'] = len(test_files)
		
		if len(test_files) > 0:
			score += 30
		max_score += 30
		
		# Check for JUnit
		has_junit = any('junit' in f.get('content_preview', '').lower() or '@Test' in f.get('content_preview', '') for f in files)
		evidence['uses_junit'] = has_junit
		
		if has_junit:
			score += 25
		max_score += 25
		
		# Check for TestNG
		has_testng = any('testng' in f.get('content_preview', '').lower() for f in files)
		evidence['uses_testng'] = has_testng
		
		if has_testng:
			score += 15
		max_score += 15
		
		# Check for Mockito
		has_mockito = any('mockito' in f.get('content_preview', '').lower() for f in files)
		evidence['uses_mockito'] = has_mockito
		
		if has_mockito:
			score += 15
		max_score += 15
		
		# Check for test resources
		has_test_resources = any('src/test/resources' in f.get('file_path', '') for f in files)
		evidence['has_test_resources'] = has_test_resources
		
		if has_test_resources:
			score += 15
		max_score += 15
		
		return (score / max_score * 100) if max_score > 0 else 0.0
	
	def _evaluate_documentation(self, files: List[Dict], evidence: Dict) -> float:
		"""Evaluate documentation in Java project."""
		score = 0.0
		max_score = 0.0
		
		# Check for README
		has_readme = any(f.get('filename', '').lower() in ['readme.md', 'readme.txt'] for f in files)
		evidence['has_readme'] = has_readme
		
		if has_readme:
			score += 25
		max_score += 25
		
		# Check for Javadoc
		has_javadoc = any('/**' in f.get('content_preview', '') or '@param' in f.get('content_preview', '') for f in files if f.get('file_type') == 'code')
		evidence['has_javadoc'] = has_javadoc
		
		if has_javadoc:
			score += 30
		max_score += 30
		
		# Check for comments
		has_comments = any('//' in f.get('content_preview', '') for f in files if f.get('file_type') == 'code')
		evidence['has_comments'] = has_comments
		
		if has_comments:
			score += 20
		max_score += 20
		
		# Check for documentation files
		has_docs = any('docs' in f.get('file_path', '').lower() or f.get('filename', '').endswith('.md') for f in files)
		evidence['has_docs'] = has_docs
		
		if has_docs:
			score += 25
		max_score += 25
		
		return (score / max_score * 100) if max_score > 0 else 0.0
	
	def _evaluate_dependencies(self, files: List[Dict], evidence: Dict) -> float:
		"""Evaluate dependency management."""
		score = 0.0
		max_score = 0.0
		
		# Check for Maven (pom.xml)
		has_maven = any(f.get('filename') == 'pom.xml' for f in files)
		evidence['uses_maven'] = has_maven
		
		if has_maven:
			score += 35
		max_score += 35
		
		# Check for Gradle (build.gradle)
		has_gradle = any(f.get('filename') in ['build.gradle', 'build.gradle.kts'] for f in files)
		evidence['uses_gradle'] = has_gradle
		
		if has_gradle:
			score += 35
		max_score += 35
		
		# Check for Ant
		has_ant = any(f.get('filename') == 'build.xml' for f in files)
		evidence['uses_ant'] = has_ant
		
		if has_ant:
			score += 20
		max_score += 20
		
		# Check for .gitignore mentioning target/build
		has_build_ignore = any(f.get('filename') == '.gitignore' and ('target' in f.get('content_preview', '') or 'build' in f.get('content_preview', '')) for f in files)
		evidence['ignores_build_artifacts'] = has_build_ignore
		
		if has_build_ignore:
			score += 10
		max_score += 10
		
		return (score / max_score * 100) if max_score > 0 else 0.0
	
	def _evaluate_organization(self, files: List[Dict], evidence: Dict) -> float:
		"""Evaluate project organization."""
		score = 0.0
		max_score = 0.0
		
		# Check for src/main/java structure
		has_source_structure = any('src/main/java' in f.get('file_path', '') for f in files)
		evidence['has_source_structure'] = has_source_structure
		
		if has_source_structure:
			score += 25
		max_score += 25
		
		# Check for src/test/java structure
		has_test_structure = any('src/test/java' in f.get('file_path', '') for f in files)
		evidence['has_test_structure'] = has_test_structure
		
		if has_test_structure:
			score += 25
		max_score += 25
		
		# Check for resources folder
		has_resources = any('src/main/resources' in f.get('file_path', '') for f in files)
		evidence['has_resources_folder'] = has_resources
		
		if has_resources:
			score += 20
		max_score += 20
		
		# Check for .gitignore
		has_gitignore = any(f.get('filename') == '.gitignore' for f in files)
		evidence['has_gitignore'] = has_gitignore
		
		if has_gitignore:
			score += 15
		max_score += 15
		
		# Check for configuration folder
		has_config = any(f.get('filename') in ['application.properties', 'application.yml', 'config.xml'] for f in files)
		evidence['has_config_files'] = has_config
		
		if has_config:
			score += 15
		max_score += 15
		
		return (score / max_score * 100) if max_score > 0 else 0.0
	
	def _evaluate_best_practices(self, files: List[Dict], evidence: Dict) -> float:
		"""Evaluate best practices in Java project."""
		score = 0.0
		max_score = 0.0
		
		# Check for design patterns (Interfaces, Abstract classes)
		has_interfaces = any('interface ' in f.get('content_preview', '') for f in files if f.get('file_type') == 'code')
		evidence['uses_interfaces'] = has_interfaces
		
		if has_interfaces:
			score += 20
		max_score += 20
		
		# Check for exception handling
		has_exception_handling = any('catch' in f.get('content_preview', '') or 'throws' in f.get('content_preview', '') for f in files if f.get('file_type') == 'code')
		evidence['has_exception_handling'] = has_exception_handling
		
		if has_exception_handling:
			score += 15
		max_score += 15
		
		# Check for CI/CD config
		has_ci = any('.github' in f.get('file_path', '') or '.gitlab-ci.yml' in f.get('filename', '') or '.travis.yml' in f.get('filename', '') for f in files)
		evidence['has_ci_config'] = has_ci
		
		if has_ci:
			score += 20
		max_score += 20
		
		# Check for code coverage tools
		has_coverage = any('jacoco' in f.get('content_preview', '').lower() or 'cobertura' in f.get('content_preview', '').lower() for f in files)
		evidence['has_coverage_tool'] = has_coverage
		
		if has_coverage:
			score += 20
		max_score += 20
		
		# Check for Dockerfile
		has_docker = any(f.get('filename') in ['Dockerfile', 'docker-compose.yml'] for f in files)
		evidence['has_docker'] = has_docker
		
		if has_docker:
			score += 15
		max_score += 15
		
		# Check for logging framework
		has_logging = any('log4j' in f.get('content_preview', '').lower() or 'slf4j' in f.get('content_preview', '').lower() or 'java.util.logging' in f.get('content_preview', '') for f in files)
		evidence['has_logging_framework'] = has_logging
		
		if has_logging:
			score += 10
		max_score += 10
		
		return (score / max_score * 100) if max_score > 0 else 0.0
	
	def _build_rubric_details(self, category_scores: Dict) -> Dict[str, Any]:
		"""Build detailed rubric evaluation report."""
		return {
			"rubric_type": "java",
			"evaluation_date": str(self._get_timestamp()),
			"category_details": {
				cat.value: {
					"score": score,
					"weight": self.category_weights[cat],
					"weighted_contribution": score * self.category_weights[cat] / 100,
				}
				for cat, score in category_scores.items()
			},
		}
	
	@staticmethod
	def _get_timestamp():
		from datetime import datetime
		return datetime.now()


class CRubric(LanguageRubric):
	"""C project evaluation rubric."""
	
	def __init__(self):
		super().__init__()
		self.language = "c"
	
	def evaluate(self, project_analysis: Dict[str, Any]) -> Dict[str, Any]:
		"""Evaluate C project."""
		files = project_analysis.get('files', [])
		
		category_scores = {}
		evidence = {}
		
		# Code Structure
		category_scores[RubricCategory.CODE_STRUCTURE] = self._evaluate_code_structure(
			files, evidence
		)
		
		# Testing
		category_scores[RubricCategory.TESTING] = self._evaluate_testing(
			files, evidence
		)
		
		# Documentation
		category_scores[RubricCategory.DOCUMENTATION] = self._evaluate_documentation(
			files, evidence
		)
		
		# Dependency Management
		category_scores[RubricCategory.DEPENDENCY_MANAGEMENT] = self._evaluate_dependencies(
			files, evidence
		)
		
		# Project Organization
		category_scores[RubricCategory.PROJECT_ORGANIZATION] = self._evaluate_organization(
			files, evidence
		)
		
		# Best Practices
		category_scores[RubricCategory.BEST_PRACTICES] = self._evaluate_best_practices(
			files, evidence
		)
		
		overall_score = self._calculate_overall_score(category_scores)
		
		return {
			'overall_score': overall_score,
			'category_scores': {cat.value: score for cat, score in category_scores.items()},
			'rubric_evaluation': self._build_rubric_details(category_scores),
			'evidence': evidence,
		}
	
	def _evaluate_code_structure(self, files: List[Dict], evidence: Dict) -> float:
		"""Evaluate C code structure."""
		score = 0.0
		max_score = 0.0
		
		# Check for C source files
		c_files = [f for f in files if f.get('file_type') == 'code' and f.get('filename', '').endswith('.c')]
		h_files = [f for f in files if f.get('file_type') == 'code' and f.get('filename', '').endswith('.h')]
		
		evidence['c_files'] = len(c_files)
		evidence['header_files'] = len(h_files)
		
		if len(c_files) > 0:
			score += 15
		max_score += 15
		
		# Check for header files (good practice)
		if len(h_files) > 0:
			score += 15
		max_score += 15
		
		# Check for function definitions
		has_functions = any('(' in f.get('content_preview', '') and ')' in f.get('content_preview', '') for f in c_files)
		evidence['has_functions'] = has_functions
		
		if has_functions:
			score += 15
		max_score += 15
		
		# Check for structs
		has_structs = any('struct ' in f.get('content_preview', '') for f in c_files + h_files)
		evidence['uses_structs'] = has_structs
		
		if has_structs:
			score += 15
		max_score += 15
		
		# Check for pointers
		has_pointers = any('*' in f.get('content_preview', '') for f in c_files)
		evidence['uses_pointers'] = has_pointers
		
		if has_pointers:
			score += 20
		max_score += 20
		
		# Check for modular design (multiple files)
		if len(c_files) > 2:
			score += 20
		max_score += 20
		
		return (score / max_score * 100) if max_score > 0 else 0.0
	
	def _evaluate_testing(self, files: List[Dict], evidence: Dict) -> float:
		"""Evaluate testing in C project."""
		score = 0.0
		max_score = 0.0
		
		# Check for test files
		test_files = [
			f for f in files 
			if f.get('file_type') == 'code' and any(pattern in f.get('filename', '').lower() for pattern in ['test', 'spec']) and f.get('filename', '').endswith('.c')
		]
		evidence['test_file_count'] = len(test_files)
		
		if len(test_files) > 0:
			score += 25
		max_score += 25
		
		# Check for testing frameworks
		has_criterion = any('criterion' in f.get('content_preview', '').lower() for f in files)
		has_unity = any('unity' in f.get('content_preview', '').lower() for f in files)
		has_cmocka = any('cmocka' in f.get('content_preview', '').lower() for f in files)
		
		evidence['uses_criterion'] = has_criterion
		evidence['uses_unity'] = has_unity
		evidence['uses_cmocka'] = has_cmocka
		
		if has_criterion or has_unity or has_cmocka:
			score += 30
		max_score += 30
		
		# Check for assertions
		has_assertions = any('assert' in f.get('content_preview', '').lower() for f in files if f.get('file_type') == 'code')
		evidence['uses_assertions'] = has_assertions
		
		if has_assertions:
			score += 20
		max_score += 20
		
		# Check for memory safety (valgrind mentions)
		has_memory_check = any('valgrind' in f.get('content_preview', '').lower() for f in files)
		evidence['checks_memory'] = has_memory_check
		
		if has_memory_check:
			score += 25
		max_score += 25
		
		return (score / max_score * 100) if max_score > 0 else 0.0
	
	def _evaluate_documentation(self, files: List[Dict], evidence: Dict) -> float:
		"""Evaluate documentation in C project."""
		score = 0.0
		max_score = 0.0
		
		# Check for README
		has_readme = any(f.get('filename', '').lower() in ['readme.md', 'readme.txt'] for f in files)
		evidence['has_readme'] = has_readme
		
		if has_readme:
			score += 25
		max_score += 25
		
		# Check for comments (especially important in C)
		has_comments = any('//' in f.get('content_preview', '') or '/*' in f.get('content_preview', '') for f in files if f.get('file_type') == 'code')
		evidence['has_comments'] = has_comments
		
		if has_comments:
			score += 30
		max_score += 30
		
		# Check for function documentation
		has_function_docs = any('/**' in f.get('content_preview', '') for f in files)
		evidence['has_function_documentation'] = has_function_docs
		
		if has_function_docs:
			score += 25
		max_score += 25
		
		# Check for Doxygen config
		has_doxygen = any(f.get('filename') == 'Doxyfile' for f in files)
		evidence['uses_doxygen'] = has_doxygen
		
		if has_doxygen:
			score += 20
		max_score += 20
		
		return (score / max_score * 100) if max_score > 0 else 0.0
	
	def _evaluate_dependencies(self, files: List[Dict], evidence: Dict) -> float:
		"""Evaluate dependency management."""
		score = 0.0
		max_score = 0.0
		
		# Check for Makefile
		has_makefile = any(f.get('filename') in ['Makefile', 'makefile'] for f in files)
		evidence['has_makefile'] = has_makefile
		
		if has_makefile:
			score += 30
		max_score += 30
		
		# Check for CMake
		has_cmake = any(f.get('filename') in ['CMakeLists.txt', 'cmake.txt'] for f in files)
		evidence['uses_cmake'] = has_cmake
		
		if has_cmake:
			score += 30
		max_score += 30
		
		# Check for build scripts
		has_build_script = any(f.get('filename') in ['build.sh', 'compile.sh'] for f in files)
		evidence['has_build_script'] = has_build_script
		
		if has_build_script:
			score += 20
		max_score += 20
		
		# Check for header guards
		has_header_guards = any('#ifndef' in f.get('content_preview', '') for f in files if f.get('filename', '').endswith('.h'))
		evidence['uses_header_guards'] = has_header_guards
		
		if has_header_guards:
			score += 20
		max_score += 20
		
		return (score / max_score * 100) if max_score > 0 else 0.0
	
	def _evaluate_organization(self, files: List[Dict], evidence: Dict) -> float:
		"""Evaluate project organization."""
		score = 0.0
		max_score = 0.0
		
		# Check for source/header separation
		has_src_dir = any('src' in f.get('file_path', '').lower() for f in files)
		has_include_dir = any('include' in f.get('file_path', '').lower() for f in files)
		
		evidence['has_src_directory'] = has_src_dir
		evidence['has_include_directory'] = has_include_dir
		
		if has_src_dir:
			score += 20
		max_score += 20
		
		if has_include_dir:
			score += 20
		max_score += 20
		
		# Check for tests directory
		has_tests_dir = any('test' in f.get('file_path', '').lower() for f in files)
		evidence['has_tests_directory'] = has_tests_dir
		
		if has_tests_dir:
			score += 20
		max_score += 20
		
		# Check for .gitignore
		has_gitignore = any(f.get('filename') == '.gitignore' for f in files)
		evidence['has_gitignore'] = has_gitignore
		
		if has_gitignore:
			score += 20
		max_score += 20
		
		# Check for documentation directory
		has_docs = any('docs' in f.get('file_path', '').lower() or f.get('filename', '').endswith('.md') for f in files)
		evidence['has_docs'] = has_docs
		
		if has_docs:
			score += 20
		max_score += 20
		
		return (score / max_score * 100) if max_score > 0 else 0.0
	
	def _evaluate_best_practices(self, files: List[Dict], evidence: Dict) -> float:
		"""Evaluate best practices in C project."""
		score = 0.0
		max_score = 0.0
		
		# Check for code linting (cppcheck, clint)
		has_linting = any('.clintrc' in f.get('filename', '') or 'cppcheck' in f.get('content_preview', '').lower() for f in files)
		evidence['has_linting_config'] = has_linting
		
		if has_linting:
			score += 20
		max_score += 20
		
		# Check for memory management (malloc/free patterns)
		has_memory_mgmt = any('malloc' in f.get('content_preview', '') or 'free(' in f.get('content_preview', '') for f in files if f.get('file_type') == 'code')
		evidence['manages_memory'] = has_memory_mgmt
		
		if has_memory_mgmt:
			score += 20
		max_score += 20
		
		# Check for CI/CD
		has_ci = any('.github' in f.get('file_path', '') or '.gitlab-ci.yml' in f.get('filename', '') for f in files)
		evidence['has_ci_config'] = has_ci
		
		if has_ci:
			score += 20
		max_score += 20
		
		# Check for Dockerfile
		has_docker = any(f.get('filename') in ['Dockerfile', 'docker-compose.yml'] for f in files)
		evidence['has_docker'] = has_docker
		
		if has_docker:
			score += 20
		max_score += 20
		
		# Check for code formatting consistency
		has_format_config = any(f.get('filename') in ['.astylerc', '.clang-format'] for f in files)
		evidence['has_format_config'] = has_format_config
		
		if has_format_config:
			score += 20
		max_score += 20
		
		return (score / max_score * 100) if max_score > 0 else 0.0
	
	def _build_rubric_details(self, category_scores: Dict) -> Dict[str, Any]:
		"""Build detailed rubric evaluation report."""
		return {
			"rubric_type": "c",
			"evaluation_date": str(self._get_timestamp()),
			"category_details": {
				cat.value: {
					"score": score,
					"weight": self.category_weights[cat],
					"weighted_contribution": score * self.category_weights[cat] / 100,
				}
				for cat, score in category_scores.items()
			},
		}
	
	@staticmethod
	def _get_timestamp():
		from datetime import datetime
		return datetime.now()


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
		'typescript': JavaScriptRubric(),  # Same rubric as JS
		'java': JavaRubric(),
		'c': CRubric(),
		'c': CRubric(),
	}
	
	return rubric_map.get(language, None)
