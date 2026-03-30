"""Java project evaluation rubric."""

from typing import Dict, List

from .base import LanguageRubric


class JavaRubric(LanguageRubric):
	"""Java project evaluation rubric."""

	def __init__(self):
		super().__init__()
		self.language = "java"

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
