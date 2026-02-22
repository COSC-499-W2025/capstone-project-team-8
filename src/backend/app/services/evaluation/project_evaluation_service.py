"""
Project Evaluation Service

Orchestrates the evaluation of projects using language-specific rubrics.
Handles the creation and storage of project evaluations.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
from .language_rubrics import get_rubric_for_language
from app.models import Project, ProjectLanguage, ProjectEvaluation


class ProjectEvaluationService:
	"""Service for evaluating projects and generating evaluation metrics."""
	
	def __init__(self):
		"""Initialize the evaluation service."""
		pass
	
	def evaluate_project(self, project: Project, project_root_path: Optional[str] = None) -> Optional['ProjectEvaluation']:
		"""
		Evaluate a project and store the evaluation results.
		
		Args:
			project: Project model instance to evaluate
			project_root_path: Optional, path to project files if needed
			
		Returns:
			ProjectEvaluation instance or None if evaluation fails
		"""
		# Determine primary language
		primary_language = self._get_primary_language(project)
		
		if not primary_language:
			return None
		
		# Build project analysis data
		project_analysis = self._build_project_analysis(project)
		
		# Get appropriate rubric
		rubric = get_rubric_for_language(primary_language)
		
		if not rubric:
			return None
		
		# Evaluate project
		evaluation_result = rubric.evaluate(project_analysis)
		
		# Store evaluation
		evaluation = self._store_evaluation(
			project=project,
			language=primary_language,
			evaluation_result=evaluation_result
		)
		
		return evaluation
	
	def evaluate_project_for_all_languages(self, project: Project) -> List['ProjectEvaluation']:
		"""
		Evaluate a project for all detected languages.
		
		Args:
			project: Project to evaluate
			
		Returns:
			List of ProjectEvaluation instances
		"""
		evaluations = []
		
		# Get all project languages
		project_languages = ProjectLanguage.objects.filter(project=project)
		
		if not project_languages.exists():
			# Try to evaluate for primary classification
			evaluation = self.evaluate_project(project)
			if evaluation:
				evaluations.append(evaluation)
		else:
			# Evaluate for each detected language
			for proj_lang in project_languages:
				language_name = proj_lang.language.name
				
				project_analysis = self._build_project_analysis(project)
				
				rubric = get_rubric_for_language(language_name)
				
				if rubric:
					evaluation_result = rubric.evaluate(project_analysis)
					
					evaluation = self._store_evaluation(
						project=project,
						language=language_name,
						evaluation_result=evaluation_result
					)
					
					evaluations.append(evaluation)
		
		return evaluations
	
	def _get_primary_language(self, project: Project) -> Optional[str]:
		"""
		Get the primary programming language for a project.
		
		Args:
			project: Project instance
			
		Returns:
			Language name or None
		"""
		# Try to get primary language from ProjectLanguage
		primary = ProjectLanguage.objects.filter(
			project=project,
			is_primary=True
		).first()
		
		if primary:
			return primary.language.name
		
		# Try to infer from classification type
		if 'coding' in project.classification_type:
			# Get most common language
			highest_count = ProjectLanguage.objects.filter(
				project=project
			).order_by('-file_count').first()
			
			if highest_count:
				return highest_count.language.name
		
		return None
	
	def _build_project_analysis(self, project: Project) -> Dict[str, Any]:
		"""
		Build a project analysis dictionary with file information.
		
		Args:
			project: Project instance
			
		Returns:
			Dictionary with project analysis data
		"""
		files = []
		
		# Get all files from project
		for project_file in project.files.all():
			file_data = {
				'filename': project_file.filename,
				'file_path': project_file.file_path,
				'file_type': project_file.file_type,
				'file_extension': project_file.file_extension,
				'content_preview': project_file.content_preview,
				'line_count': project_file.line_count,
				'character_count': project_file.character_count,
			}
			files.append(file_data)
		
		return {
			'project_id': project.id,
			'project_name': project.name,
			'classification_type': project.classification_type,
			'files': files,
			'total_files': project.total_files,
			'code_files_count': project.code_files_count,
			'text_files_count': project.text_files_count,
			'image_files_count': project.image_files_count,
		}
	
	def _store_evaluation(
		self,
		project: Project,
		language: str,
		evaluation_result: Dict[str, Any]
	) -> ProjectEvaluation:
		"""
		Store the evaluation result in the database.
		
		Args:
			project: Project being evaluated
			language: Programming language
			evaluation_result: Evaluation result dictionary
			
		Returns:
			ProjectEvaluation instance
		"""
		# Delete existing evaluation if present
		ProjectEvaluation.objects.filter(project=project, language=language).delete()
		
		# Create new evaluation
		evaluation = ProjectEvaluation.objects.create(
			project=project,
			language=language,
			overall_score=evaluation_result['overall_score'],
			category_scores=evaluation_result['category_scores'],
			rubric_evaluation=evaluation_result['rubric_evaluation'],
			evidence=evaluation_result['evidence'],
		)
		
		# Extract and store individual category scores
		category_scores = evaluation_result['category_scores']
		
		if 'code_structure' in category_scores:
			evaluation.structure_score = category_scores['code_structure']
		
		if 'documentation' in category_scores:
			evaluation.documentation_score = category_scores['documentation']
		
		if 'testing' in category_scores:
			evaluation.testing_score = category_scores['testing']
		
		if 'project_organization' in category_scores:
			evaluation.code_quality_score = category_scores.get('best_practices', 0.0)
		
		evaluation.save()
		
		return evaluation
	
	@staticmethod
	def get_projects_by_language_evaluation(
		language: str,
		min_score: float = 0.0,
		max_score: float = 100.0,
		order_by: str = '-overall_score'
	) -> List[ProjectEvaluation]:
		"""
		Get all project evaluations for a specific language.
		
		Args:
			language: Programming language
			min_score: Minimum evaluation score (0-100)
			max_score: Maximum evaluation score (0-100)
			order_by: Field to order by
			
		Returns:
			Queryset of ProjectEvaluation objects
		"""
		evaluations = ProjectEvaluation.objects.filter(
			language__iexact=language,
			overall_score__gte=min_score,
			overall_score__lte=max_score
		).order_by(order_by)
		
		return evaluations
	
	@staticmethod
	def get_top_projects_for_language(
		language: str,
		limit: int = 10
	) -> List[ProjectEvaluation]:
		"""
		Get top-ranked projects for a specific language.
		
		Args:
			language: Programming language
			limit: Maximum number of projects to return
			
		Returns:
			List of top ProjectEvaluation objects
		"""
		return ProjectEvaluationService.get_projects_by_language_evaluation(
			language=language,
			order_by='-overall_score'
		)[:limit]
	
	@staticmethod
	def get_language_statistics(language: str) -> Dict[str, Any]:
		"""
		Get aggregated statistics for a language's evaluations.
		
		Args:
			language: Programming language
			
		Returns:
			Dictionary with statistics
		"""
		from django.db.models import Avg, Max, Min, Count
		
		evaluations = ProjectEvaluation.objects.filter(language__iexact=language)
		
		stats = evaluations.aggregate(
			count=Count('id'),
			avg_score=Avg('overall_score'),
			max_score=Max('overall_score'),
			min_score=Min('overall_score'),
			avg_code_quality=Avg('code_quality_score'),
			avg_documentation=Avg('documentation_score'),
			avg_testing=Avg('testing_score'),
			avg_structure=Avg('structure_score'),
		)
		
		return {
			'language': language,
			'total_projects': stats['count'],
			'average_score': round(stats['avg_score'] or 0.0, 2),
			'highest_score': stats['max_score'],
			'lowest_score': stats['min_score'],
			'average_code_quality': round(stats['avg_code_quality'] or 0.0, 2),
			'average_documentation': round(stats['avg_documentation'] or 0.0, 2),
			'average_testing': round(stats['avg_testing'] or 0.0, 2),
			'average_structure': round(stats['avg_structure'] or 0.0, 2),
		}
	
	@staticmethod
	def get_all_evaluations(
		min_score: float = 0.0,
		max_score: float = 100.0,
		order_by: str = '-overall_score',
		language: Optional[str] = None
	) -> List[ProjectEvaluation]:
		"""
		Get all project evaluations across all projects, optionally filtered by language.
		
		Args:
			min_score: Minimum evaluation score (0-100)
			max_score: Maximum evaluation score (0-100)
			order_by: Field to order by (default: -overall_score)
			language: Optional language filter
			
		Returns:
			List of all ProjectEvaluation objects
		"""
		query = ProjectEvaluation.objects.filter(
			overall_score__gte=min_score,
			overall_score__lte=max_score
		)
		
		if language:
			query = query.filter(language__iexact=language)
		
		return query.order_by(order_by)
