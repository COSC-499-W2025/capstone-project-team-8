"""
Project Classifier Module

Main orchestrator for project classification. Uses extracted modules for
feature extraction, scoring, and confidence calculation.
"""
import zipfile
import tempfile
from pathlib import Path
from typing import Dict, Any, Union

from ..analysis.analyzers import detect_languages, detect_frameworks, extract_resume_skills
from .feature_extractor import extract_project_features
from .scoring_classifier import simple_score_classify  
from .confidence_calculator import calculate_confidence
from .file_type_registry import FOLDER_HINTS


def classify_project(project_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Main function to classify a project (directory or zip file).
    
    Args:
        project_path: Path to project directory or zip file
        
    Returns:
        Dictionary containing classification results and metadata
    """
    project_path = Path(project_path)
    
    # Handle zip files
    if project_path.suffix.lower() == '.zip':
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Extract zip file
            with zipfile.ZipFile(project_path, 'r') as zipf:
                zipf.extractall(tmpdir_path)
            
            # Find the root directory (handle cases where zip contains a single folder)
            extracted_items = list(tmpdir_path.iterdir())
            if len(extracted_items) == 1 and extracted_items[0].is_dir():
                root_dir = extracted_items[0]
            else:
                root_dir = tmpdir_path
            
            # Extract features and classify
            features = extract_project_features(root_dir)
            classification = simple_score_classify(root_dir)
            
            # Calculate confidence
            confidence = calculate_confidence(features)
            
            result = {
                'classification': classification,
                'confidence': confidence,
                'features': features,
                'source': 'zip_file'
            }
            
            # Detect languages and frameworks for coding projects
            if classification == 'coding' or (classification.startswith('mixed:') and 'coding' in classification):
                result['languages'] = detect_languages(root_dir)
                result['frameworks'] = detect_frameworks(root_dir)
            else:
                result['languages'] = []
                result['frameworks'] = []
            
            # Extract resume_skills for ALL project types (coding, art, writing, mixed)
            # This includes creative skills like Photography, Adobe Photoshop, Video Editing, etc.
            result['resume_skills'] = extract_resume_skills(root_dir, result['languages'], result['frameworks'])
            
            return result
    
    # Handle directory
    else:
        features = extract_project_features(project_path)
        classification = simple_score_classify(project_path)
        
        # Calculate confidence
        confidence = calculate_confidence(features)
        
        result = {
            'classification': classification,
            'confidence': confidence,
            'features': features,
            'source': 'directory'
        }
        
        # Detect languages and frameworks for coding projects
        if classification == 'coding' or (classification.startswith('mixed:') and 'coding' in classification):
            result['languages'] = detect_languages(project_path)
            result['frameworks'] = detect_frameworks(project_path)
        else:
            result['languages'] = []
            result['frameworks'] = []
        
        # Extract resume_skills for ALL project types (coding, art, writing, mixed)
        # This includes creative skills like Photography, Adobe Photoshop, Video Editing, etc.
        result['resume_skills'] = extract_resume_skills(project_path, result['languages'], result['frameworks'])
        
        return result


def get_classification_explanation(classification_result: Dict[str, Any]) -> str:
    """
    Generate a human-readable explanation of the classification result.
    
    Args:
        classification_result: Result from classify_project()
        
    Returns:
        Human-readable explanation string
    """
    classification = classification_result['classification']
    confidence = classification_result['confidence']
    features = classification_result['features']
    
    explanation_parts = []
    
    # Main classification
    if classification == 'unknown':
        explanation_parts.append("Project type could not be determined (too few files or unclear patterns).")
    elif classification.startswith('mixed:'):
        categories = classification.split(':')[1].split('+')
        explanation_parts.append(f"Mixed project type: {categories[0]} and {categories[1]}.")
    else:
        explanation_parts.append(f"Project classified as: {classification}.")
    
    # Confidence
    if confidence > 0.7:
        explanation_parts.append("High confidence classification.")
    elif confidence > 0.4:
        explanation_parts.append("Medium confidence classification.")
    else:
        explanation_parts.append("Low confidence classification.")
    
    # File statistics
    total = features['total_files']
    code = features['code_count']
    text = features['text_count']
    image = features['image_count']
    
    explanation_parts.append(f"Analysis of {total} files: {code} code files, {text} text files, {image} image files.")
    
    # Folder hints
    folder_names = set(features['folder_names'].keys())
    hints_found = []
    
    if folder_names & FOLDER_HINTS['code']:
        hints_found.append("coding")
    if folder_names & FOLDER_HINTS['writing']:
        hints_found.append("writing")
    if folder_names & FOLDER_HINTS['art']:
        hints_found.append("art")
    
    if hints_found:
        explanation_parts.append(f"Folder structure suggests: {', '.join(hints_found)} project.")
    
    return " ".join(explanation_parts)
