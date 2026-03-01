"""Views for project evaluation endpoints."""

from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
import logging

from app.models import ProjectEvaluation
from app.serializers import (
	ProjectEvaluationSerializer,
	ProjectEvaluationDetailSerializer,
	LanguageEvaluationStatsSerializer,
	EvaluationSummarySerializer,
)
from app.services.evaluation import ProjectEvaluationService

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class LanguageEvaluationsView(APIView):
	"""Get all project evaluations for a specific language."""
	
	permission_classes = [IsAuthenticated]
	
	@extend_schema(
		parameters=[
			OpenApiParameter(
				name='language',
				description='Programming language to filter by (python, javascript, java, c, etc.)',
				required=True,
				type=str,
				location='path'
			),
			OpenApiParameter(
				name='min_score',
				description='Minimum score filter (0-100)',
				required=False,
				type=float,
			),
			OpenApiParameter(
				name='max_score',
				description='Maximum score filter (0-100)',
				required=False,
				type=float,
			),
			OpenApiParameter(
				name='sort',
				description='Sort by field (-overall_score for descending)',
				required=False,
				type=str,
			),
		],
		responses={200: ProjectEvaluationSerializer(many=True)},
		description='Get all project evaluations for a specific programming language',
		tags=['Evaluations'],
	)
	def get(self, request, language):
		"""
		Get all project evaluations for the specified language.
		
		Query Parameters:
			- language: Programming language name (path parameter)
			- min_score: Filter by minimum score (0-100)
			- max_score: Filter by maximum score (0-100)
			- sort: Sort field (default: -overall_score)
		"""
		try:
			# Get filter parameters
			min_score = float(request.GET.get('min_score', 0.0))
			max_score = float(request.GET.get('max_score', 100.0))
			sort_by = request.GET.get('sort', '-overall_score')
			
			# Validate score range
			if not (0 <= min_score <= 100) or not (0 <= max_score <= 100):
				return Response(
					{'error': 'Scores must be between 0 and 100'},
					status=status.HTTP_400_BAD_REQUEST
				)
			
			if min_score > max_score:
				return Response(
					{'error': 'min_score cannot be greater than max_score'},
					status=status.HTTP_400_BAD_REQUEST
				)
			
			# Get evaluations
			evaluations = ProjectEvaluationService.get_projects_by_language_evaluation(
				language=language,
				min_score=min_score,
				max_score=max_score,
				order_by=sort_by
			)
			
			# Serialize and return
			serializer = ProjectEvaluationSerializer(evaluations, many=True)
			
			return Response({
				'language': language,
				'count': len(evaluations),
				'min_score_filter': min_score,
				'max_score_filter': max_score,
				'evaluations': serializer.data,
			})
		
		except ValueError as e:
			return Response(
				{'error': f'Invalid parameter: {str(e)}'},
				status=status.HTTP_400_BAD_REQUEST
			)
		except Exception as e:
			logger.error(f"Error getting language evaluations: {str(e)}")
			return Response(
				{'error': 'An error occurred retrieving evaluations'},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)


@method_decorator(csrf_exempt, name="dispatch")
class ProjectEvaluationDetailView(APIView):
	"""Get detailed evaluation for a specific project and language."""
	
	permission_classes = [IsAuthenticated]
	
	@extend_schema(
		parameters=[
			OpenApiParameter(
				name='project_id',
				description='Project ID',
				required=True,
				type=int,
				location='path'
			),
			OpenApiParameter(
				name='language',
				description='Programming language',
				required=True,
				type=str,
				location='path'
			),
		],
		responses={200: ProjectEvaluationDetailSerializer()},
		description='Get detailed evaluation for a specific project and language',
		tags=['Evaluations'],
	)
	def get(self, request, project_id, language):
		"""
		Get detailed evaluation for a specific project and language.
		"""
		try:
			evaluation = ProjectEvaluation.objects.get(
				project_id=project_id,
				language__iexact=language
			)
			
			serializer = ProjectEvaluationDetailSerializer(evaluation)
			
			return Response(serializer.data)
		
		except ProjectEvaluation.DoesNotExist:
			return Response(
				{'error': f'No evaluation found for project {project_id} in {language}'},
				status=status.HTTP_404_NOT_FOUND
			)
		except Exception as e:
			logger.error(f"Error getting project evaluation: {str(e)}")
			return Response(
				{'error': 'An error occurred retrieving evaluation'},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)


@method_decorator(csrf_exempt, name="dispatch")
class TopProjectsByLanguageView(APIView):
	"""Get top-rated projects for a specific language."""
	
	permission_classes = [IsAuthenticated]
	
	@extend_schema(
		parameters=[
			OpenApiParameter(
				name='language',
				description='Programming language',
				required=True,
				type=str,
				location='path'
			),
			OpenApiParameter(
				name='limit',
				description='Maximum number of projects to return (default: 10)',
				required=False,
				type=int,
			),
		],
		responses={200: ProjectEvaluationSerializer(many=True)},
		description='Get top-rated projects for a specific programming language',
		tags=['Evaluations'],
	)
	def get(self, request, language):
		"""
		Get top-rated projects for the specified language.
		
		Query Parameters:
			- language: Programming language name (path parameter)
			- limit: Number of top projects to return (default: 10)
		"""
		try:
			limit = int(request.GET.get('limit', 10))
			
			if limit < 1 or limit > 100:
				limit = 10
			
			evaluations = ProjectEvaluationService.get_top_projects_for_language(
				language=language,
				limit=limit
			)
			
			serializer = ProjectEvaluationSerializer(evaluations, many=True)
			
			return Response({
				'language': language,
				'limit': limit,
				'count': len(evaluations),
				'top_projects': serializer.data,
			})
		
		except ValueError as e:
			return Response(
				{'error': f'Invalid parameter: {str(e)}'},
				status=status.HTTP_400_BAD_REQUEST
			)
		except Exception as e:
			logger.error(f"Error getting top projects: {str(e)}")
			return Response(
				{'error': 'An error occurred retrieving top projects'},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)


@method_decorator(csrf_exempt, name="dispatch")
class LanguageEvaluationStatisticsView(APIView):
	"""Get aggregated statistics for a language's evaluations."""
	
	permission_classes = [IsAuthenticated]
	
	@extend_schema(
		parameters=[
			OpenApiParameter(
				name='language',
				description='Programming language',
				required=True,
				type=str,
				location='path'
			),
		],
		responses={200: LanguageEvaluationStatsSerializer()},
		description='Get aggregated evaluation statistics for a programming language',
		tags=['Evaluations'],
	)
	def get(self, request, language):
		"""
		Get aggregated evaluation statistics for the specified language.
		"""
		try:
			stats = ProjectEvaluationService.get_language_statistics(language)
			
			serializer = LanguageEvaluationStatsSerializer(stats)
			
			return Response(serializer.data)
		
		except Exception as e:
			logger.error(f"Error getting language statistics: {str(e)}")
			return Response(
				{'error': 'An error occurred retrieving statistics'},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)


@method_decorator(csrf_exempt, name="dispatch")
class ProjectEvaluationSummaryView(APIView):
	"""Get a formatted summary of project evaluation."""
	
	permission_classes = [IsAuthenticated]
	
	@extend_schema(
		parameters=[
			OpenApiParameter(
				name='project_id',
				description='Project ID',
				required=True,
				type=int,
				location='path'
			),
			OpenApiParameter(
				name='language',
				description='Programming language',
				required=True,
				type=str,
				location='path'
			),
		],
		responses={200: EvaluationSummarySerializer()},
		description='Get a formatted summary of project evaluation with score, grade, and recommendations',
		tags=['Evaluations'],
	)
	def get(self, request, project_id, language):
		"""
		Get a formatted summary of project evaluation including grade and recommendations.
		"""
		try:
			evaluation = ProjectEvaluation.objects.get(
				project_id=project_id,
				language__iexact=language
			)
			
			# Build summary data
			summary_data = {
				'language': evaluation.language,
				'overall_score': evaluation.overall_score,
				'category_scores': evaluation.category_scores,
			}
			
			serializer = EvaluationSummarySerializer(summary_data)
			
			return Response(serializer.data)
		
		except ProjectEvaluation.DoesNotExist:
			return Response(
				{'error': f'No evaluation found for project {project_id} in {language}'},
				status=status.HTTP_404_NOT_FOUND
			)
		except Exception as e:
			logger.error(f"Error getting evaluation summary: {str(e)}")
			return Response(
				{'error': 'An error occurred retrieving evaluation summary'},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)


@method_decorator(csrf_exempt, name="dispatch")
class ProjectAllEvaluationsView(APIView):
	"""Get all evaluations for a specific project across all languages."""
	
	permission_classes = [IsAuthenticated]
	
	@extend_schema(
		parameters=[
			OpenApiParameter(
				name='project_id',
				description='Project ID',
				required=True,
				type=int,
				location='path'
			),
		],
		responses={200: ProjectEvaluationSerializer(many=True)},
		description='Get all evaluations for a project across all detected languages',
		tags=['Evaluations'],
	)
	def get(self, request, project_id):
		"""
		Get all evaluations for the specified project across all languages.
		"""
		try:
			evaluations = ProjectEvaluation.objects.filter(
				project_id=project_id
			).order_by('-overall_score')
			
			if not evaluations.exists():
				return Response(
					{'error': f'No evaluations found for project {project_id}'},
					status=status.HTTP_404_NOT_FOUND
				)
			
			serializer = ProjectEvaluationSerializer(evaluations, many=True)
			
			return Response({
				'project_id': project_id,
				'evaluation_count': len(evaluations),
				'evaluations': serializer.data,
			})
		
		except Exception as e:
			logger.error(f"Error getting project evaluations: {str(e)}")
			return Response(
				{'error': 'An error occurred retrieving project evaluations'},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)


@method_decorator(csrf_exempt, name="dispatch")
class AllEvaluationsView(APIView):
	"""Get all evaluations across all projects."""
	
	permission_classes = [IsAuthenticated]
	
	@extend_schema(
		parameters=[
			OpenApiParameter(
				name='language',
				description='Filter by programming language (optional)',
				required=False,
				type=str,
			),
			OpenApiParameter(
				name='min_score',
				description='Minimum score filter (0-100)',
				required=False,
				type=float,
			),
			OpenApiParameter(
				name='max_score',
				description='Maximum score filter (0-100)',
				required=False,
				type=float,
			),
			OpenApiParameter(
				name='sort',
				description='Sort field (default: -overall_score for descending)',
				required=False,
				type=str,
			),
			OpenApiParameter(
				name='limit',
				description='Maximum number of results to return (default: all)',
				required=False,
				type=int,
			),
		],
		responses={200: ProjectEvaluationSerializer(many=True)},
		description='Get all project evaluations across all projects with optional filtering and sorting',
		tags=['Evaluations'],
	)
	def get(self, request):
		"""
		Get all project evaluations across all projects.
		
		Query Parameters:
			- language: Filter by programming language (optional)
			- min_score: Filter by minimum score (0-100)
			- max_score: Filter by maximum score (0-100)
			- sort: Sort field (default: -overall_score)
			- limit: Maximum number of results
		"""
		try:
			# Get filter parameters
			language = request.GET.get('language', None)
			min_score = float(request.GET.get('min_score', 0.0))
			max_score = float(request.GET.get('max_score', 100.0))
			sort_by = request.GET.get('sort', '-overall_score')
			limit = request.GET.get('limit')
			
			# Validate score range
			if not (0 <= min_score <= 100) or not (0 <= max_score <= 100):
				return Response(
					{'error': 'Scores must be between 0 and 100'},
					status=status.HTTP_400_BAD_REQUEST
				)
			
			if min_score > max_score:
				return Response(
					{'error': 'min_score cannot be greater than max_score'},
					status=status.HTTP_400_BAD_REQUEST
				)
			
			# Get evaluations
			evaluations = ProjectEvaluationService.get_all_evaluations(
				min_score=min_score,
				max_score=max_score,
				order_by=sort_by,
				language=language
			)
			
			# Apply limit if provided
			if limit:
				eval_limit = int(limit)
				if eval_limit > 0:
					evaluations = evaluations[:eval_limit]
			
			# Serialize and return
			serializer = ProjectEvaluationSerializer(evaluations, many=True)
			
			return Response({
				'total_count': len(evaluations),
				'language_filter': language or 'all',
				'score_range': {
					'min': min_score,
					'max': max_score,
				},
				'sort_by': sort_by,
				'evaluations': serializer.data,
			})
		
		except ValueError as e:
			return Response(
				{'error': f'Invalid parameter: {str(e)}'},
				status=status.HTTP_400_BAD_REQUEST
			)
		except Exception as e:
			logger.error(f"Error getting all evaluations: {str(e)}")
			return Response(
				{'error': 'An error occurred retrieving evaluations'},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)
