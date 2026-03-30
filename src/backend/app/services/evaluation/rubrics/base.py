"""
Base classes for language-specific evaluation rubrics.
"""

from typing import Dict, Any, List
from enum import Enum
from datetime import datetime


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
		files = project_analysis.get('files', [])

		category_scores = {}
		evidence = {}

		category_scores[RubricCategory.CODE_STRUCTURE] = self._evaluate_code_structure(
			files, evidence
		)
		category_scores[RubricCategory.TESTING] = self._evaluate_testing(
			files, evidence
		)
		category_scores[RubricCategory.DOCUMENTATION] = self._evaluate_documentation(
			files, evidence
		)
		category_scores[RubricCategory.DEPENDENCY_MANAGEMENT] = self._evaluate_dependencies(
			files, evidence
		)
		category_scores[RubricCategory.PROJECT_ORGANIZATION] = self._evaluate_organization(
			files, evidence
		)
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
		raise NotImplementedError

	def _evaluate_testing(self, files: List[Dict], evidence: Dict) -> float:
		raise NotImplementedError

	def _evaluate_documentation(self, files: List[Dict], evidence: Dict) -> float:
		raise NotImplementedError

	def _evaluate_dependencies(self, files: List[Dict], evidence: Dict) -> float:
		raise NotImplementedError

	def _evaluate_organization(self, files: List[Dict], evidence: Dict) -> float:
		raise NotImplementedError

	def _evaluate_best_practices(self, files: List[Dict], evidence: Dict) -> float:
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

	def _build_rubric_details(self, category_scores: Dict) -> Dict[str, Any]:
		"""Build detailed rubric evaluation report."""
		return {
			"rubric_type": self.language,
			"evaluation_date": str(datetime.now()),
			"category_details": {
				cat.value: {
					"score": score,
					"weight": self.category_weights[cat],
					"weighted_contribution": score * self.category_weights[cat] / 100,
				}
				for cat, score in category_scores.items()
			},
		}
