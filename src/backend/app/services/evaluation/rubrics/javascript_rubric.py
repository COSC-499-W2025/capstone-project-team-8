"""JavaScript/TypeScript project evaluation rubric."""

from typing import Dict, List

from .base import LanguageRubric


class JavaScriptRubric(LanguageRubric):
	"""JavaScript/TypeScript project evaluation rubric."""

	def __init__(self):
		super().__init__()
		self.language = "javascript"

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
