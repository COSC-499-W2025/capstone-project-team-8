"""
Confidence Calculator Module

This module handles confidence score calculation for project classifications.
"""
from typing import Dict, Any


def calculate_confidence(features: Dict[str, Any]) -> float:
    """
    Calculate confidence score for a project classification.
    
    Confidence is based on:
    - How dominant the primary file type is (ratio)
    - Total number of files (more files = more confidence)
    
    Args:
        features: Dictionary containing project features:
            - total_files: Total number of files
            - code_count: Number of code files
            - text_count: Number of text files
            - image_count: Number of image files
            
    Returns:
        Confidence score between 0.0 and 1.0
    """
    total_files = features['total_files']
    
    # Handle edge case: no files
    if total_files == 0:
        return 0.0
    
    code_count = features['code_count']
    text_count = features['text_count']
    image_count = features['image_count']
    
    # Calculate ratios
    code_ratio = code_count / total_files
    text_ratio = text_count / total_files
    image_ratio = image_count / total_files
    
    # Get the maximum ratio (dominant file type)
    max_ratio = max(code_ratio, text_ratio, image_ratio)
    
    # Base confidence on how dominant the primary type is
    # Use a lower multiplier to avoid hitting 1.0 too easily
    base_confidence = max_ratio * 0.8
    
    # Boost confidence based on total files (more files = more confident)
    # Scale: 0.05 per file, cap at 0.2
    file_boost = min(total_files * 0.05, 0.2)
    
    # Calculate final confidence
    confidence = min(base_confidence + file_boost, 1.0)
    
    return confidence
