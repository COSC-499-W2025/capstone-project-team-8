"""Evaluation serializers for project evaluation data."""

from rest_framework import serializers
from app.models import ProjectEvaluation, Project


class ProjectEvaluationSerializer(serializers.ModelSerializer):
	"""Serializer for ProjectEvaluation model."""
	
	project_name = serializers.CharField(source='project.name', read_only=True)
	project_id = serializers.IntegerField(source='project.id', read_only=True)
	
	class Meta:
		model = ProjectEvaluation
		fields = [
			'id',
			'project_id',
			'project_name',
			'language',
			'overall_score',
			'category_scores',
			'code_quality_score',
			'documentation_score',
			'structure_score',
			'testing_score',
			'evidence',
			'rubric_evaluation',
			'evaluated_at',
			'created_at',
		]
		read_only_fields = [
			'id',
			'project_id',
			'project_name',
			'evaluated_at',
			'created_at',
		]


class ProjectEvaluationDetailSerializer(serializers.ModelSerializer):
	"""Detailed serializer for ProjectEvaluation with full evidence."""
	
	project_name = serializers.CharField(source='project.name', read_only=True)
	project_id = serializers.IntegerField(source='project.id', read_only=True)
	project_description = serializers.CharField(source='project.description', read_only=True)
	project_classification = serializers.CharField(source='project.classification_type', read_only=True)
	
	class Meta:
		model = ProjectEvaluation
		fields = [
			'id',
			'project_id',
			'project_name',
			'project_description',
			'project_classification',
			'language',
			'overall_score',
			'category_scores',
			'code_quality_score',
			'documentation_score',
			'structure_score',
			'testing_score',
			'evidence',
			'rubric_evaluation',
			'evaluated_at',
			'created_at',
		]
		read_only_fields = [
			'id',
			'project_id',
			'project_name',
			'project_description',
			'project_classification',
			'evaluated_at',
			'created_at',
		]


class LanguageEvaluationStatsSerializer(serializers.Serializer):
	"""Serializer for language evaluation statistics."""
	
	language = serializers.CharField()
	total_projects = serializers.IntegerField()
	average_score = serializers.FloatField()
	highest_score = serializers.FloatField()
	lowest_score = serializers.FloatField()
	average_code_quality = serializers.FloatField()
	average_documentation = serializers.FloatField()
	average_testing = serializers.FloatField()
	average_structure = serializers.FloatField()


class EvaluationSummarySerializer(serializers.Serializer):
	"""Serializer for evaluation summary of a single evaluation."""
	
	language = serializers.CharField()
	overall_score = serializers.FloatField()
	score_percentage = serializers.SerializerMethodField()
	grade = serializers.SerializerMethodField()
	category_breakdown = serializers.SerializerMethodField()
	top_strengths = serializers.SerializerMethodField()
	areas_for_improvement = serializers.SerializerMethodField()
	
	def get_score_percentage(self, obj):
		"""Convert score to percentage."""
		return f"{obj['overall_score']:.1f}%"
	
	def get_grade(self, obj):
		"""Calculate letter grade from score."""
		score = obj['overall_score']
		if score >= 90:
			return 'A'
		elif score >= 80:
			return 'B'
		elif score >= 70:
			return 'C'
		elif score >= 60:
			return 'D'
		else:
			return 'F'
	
	def get_category_breakdown(self, obj):
		"""Get formatted category scores."""
		categories = obj.get('category_scores', {})
		return {
			name.replace('_', ' ').title(): round(score, 2)
			for name, score in categories.items()
		}
	
	def get_top_strengths(self, obj):
		"""Identify top scoring categories."""
		categories = obj.get('category_scores', {})
		if not categories:
			return []
		
		sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)
		return [
			name.replace('_', ' ').title()
			for name, _ in sorted_cats[:3]
		]
	
	def get_areas_for_improvement(self, obj):
		"""Identify lowest scoring categories."""
		categories = obj.get('category_scores', {})
		if not categories:
			return []
		
		sorted_cats = sorted(categories.items(), key=lambda x: x[1])
		# Only show areas that need improvement (score < 70)
		return [
			name.replace('_', ' ').title()
			for name, score in sorted_cats
			if score < 70
		]


class ProjectEvaluationListSerializer(serializers.Serializer):
	"""Serializer for list of evaluations."""
	
	language = serializers.CharField()
	total_projects = serializers.IntegerField()
	average_score = serializers.FloatField()
	projects = ProjectEvaluationSerializer(many=True)


class LanguageComparisonSerializer(serializers.Serializer):
	"""Serializer for comparing evaluations across languages."""
	
	project_id = serializers.IntegerField()
	project_name = serializers.CharField()
	evaluations = serializers.ListField(child=serializers.DictField())
