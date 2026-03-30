"""C project evaluation rubric."""

from typing import Dict, List

from .base import LanguageRubric


class CRubric(LanguageRubric):
	"""C project evaluation rubric."""

	def __init__(self):
		super().__init__()
		self.language = "c"

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
