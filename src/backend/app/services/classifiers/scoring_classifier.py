"""
Scoring Classifier Module

This module contains the scoring-based heuristic classification logic
for determining project types.
"""
from pathlib import Path
from typing import Union, Tuple

from .feature_extractor import extract_project_features
from .file_type_registry import FOLDER_HINTS


def simple_score_classify(
    root_dir: Union[str, Path],
    min_files_for_confident: int = 2,
    weights: Tuple[float, float, float] = (3.0, 2.0, 2.5),  # code, text, image
    folder_bonus: float = 1.5,
    margin_threshold: float = 0.25,
    force_mixed: bool = True
) -> str:
    """
    Classify a project using a scoring-based heuristic approach.
    
    Args:
        root_dir: Path to the project directory
        min_files_for_confident: Minimum files needed for confident classification
        weights: Tuple of (code_weight, text_weight, image_weight)
        folder_bonus: Bonus score for matching folder hints
        margin_threshold: Minimum score difference to avoid mixed classification
        force_mixed: Whether to force mixed classification when appropriate
        
    Returns:
        Classification result: 'coding', 'writing', 'art', 'mixed:category1+category2', or 'unknown'
    """
    features = extract_project_features(root_dir)
    total_files = features['total_files']
    
    # If project is too small, return unknown
    if total_files < min_files_for_confident:
        return 'unknown'
    
    # Special case: empty project
    if total_files == 0:
        return 'unknown'
    
    # Calculate ratios
    code_ratio = features['code_count'] / total_files
    text_ratio = features['text_count'] / total_files
    image_ratio = features['image_count'] / total_files
    
    # Apply weights to get base scores
    code_weight, text_weight, image_weight = weights
    score_code = code_ratio * code_weight
    score_text = text_ratio * text_weight
    score_image = image_ratio * image_weight
    
    # Apply folder name bonuses
    folder_names = set(features['folder_names'].keys())
    
    if folder_names & FOLDER_HINTS['code']:
        score_code += folder_bonus
    if folder_names & FOLDER_HINTS['writing']:
        score_text += folder_bonus
    if folder_names & FOLDER_HINTS['art']:
        score_image += folder_bonus
    
    # Additional cues
    # README-like files suggest coding or writing projects
    readme_indicators = any(
        'readme' in ext.lower() or ext.lower() in {'.md', '.txt'}
        for ext in features['ext_counts'].keys()
    )
    if readme_indicators:
        score_code += 0.5
        score_text += 0.1
    
    # requirements.txt files suggest coding projects
    requirements_indicators = any(
        'requirements' in ext.lower()
        for ext in features['ext_counts'].keys()
    )
    if requirements_indicators:
        score_code += 0.5

    # License files suggest coding projects
    license_indicators = any(
        'license' in ext.lower()
        for ext in features['ext_counts'].keys()
    )
    if license_indicators:
        score_code += 0.5
    
    # Package files suggest coding projects
    package_indicators = any(
        ext.lower() in {'.json', '.toml', '.yaml', '.yml', '.ini', '.cfg'}
        for ext in features['ext_counts'].keys()
    )
    if package_indicators:
        score_code += 0.3
    
    # Determine classification
    scores = {
        'coding': score_code,
        'writing': score_text,
        'art': score_image
    }
    
    # Sort by score (highest first)
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_label, top_score = sorted_scores[0]
    second_label, second_score = sorted_scores[1]
    
    # Check if top score is significantly higher than second
    score_difference = top_score - second_score
    
    # Check if we have multiple file types (indicating mixed content)
    has_multiple_types = sum(
        1 for count in [features['code_count'], features['text_count'], features['image_count']]
        if count > 0
    ) >= 2
    
    # Consider mixed if:
    # 1. Both scores are reasonably high and close, OR
    # 2. We have multiple file types and both top scores are decent
    condition1 = score_difference < margin_threshold and top_score > 1.0 and second_score > 0.8
    condition2 = has_multiple_types and top_score > 0.8 and second_score > 0.5 and score_difference < 1.0
    
    if force_mixed and (condition1 or condition2):
        return f"mixed:{top_label}+{second_label}"
    
    # If not mixed, return the top category
    return top_label
