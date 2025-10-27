import os
import zipfile
import tempfile
from pathlib import Path
from collections import Counter
from typing import Dict, Any, Union, Tuple


# Extension sets for different file types
CODE_EXTS = {
    '.py', '.pyw', '.pyi',
    '.js', '.jsx', '.mjs', '.cjs',
    '.ts', '.tsx',
    '.java', '.jsp',
    '.c', '.h', '.cpp', '.cc', '.cxx', '.hpp', '.hh',
    '.cs',
    '.go',
    '.rs',
    '.php', '.php3', '.php4', '.php5', '.phtml',
    '.rb',
    '.swift',
    '.kt', '.kts',
    '.scala', '.sc',
    '.sh', '.bash', '.zsh',
    '.ps1', '.psm1', '.bat', '.cmd',
    '.pl', '.pm',
    '.r',
    '.jl',
    '.hs', '.lhs',
    '.erl', '.ex', '.exs',
    '.fs', '.fsi',
    '.vb',
    '.sql',
    '.asm', '.s',
    '.groovy',
    '.dart',
    '.lua',
    '.html', '.htm', '.css',
    '.json', '.xml',
    '.ipynb',  # Jupyter notebooks
    '.yaml', '.yml',  # Configuration files
    '.toml', '.ini', '.cfg', '.conf'
}

TEXT_EXTS = {
    '.txt', '.md', '.doc', '.docx', '.pdf', '.tex', '.bib',
    '.rtf', '.odt', '.pages',  # Additional document formats
    '.log'  # Log files
}

IMAGE_EXTS = {
    '.png', '.jpg', '.jpeg', '.svg', '.psd', '.gif', '.tiff', '.tif',
    '.bmp', '.webp', '.ico', '.raw', '.cr2', '.nef', '.arw',  # Additional image formats
    '.ai', '.eps', '.sketch', '.fig'  # Design files
}

OTHER_BINARY_EXTS = {
    '.exe', '.bin', '.dll', '.zip', '.tar', '.gz', '.7z', '.rar',
    '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm',  # Video files
    '.mp3', '.wav', '.flac', '.aac', '.ogg',  # Audio files
    '.db', '.sqlite', '.sqlite3'  # Database files
}

# Folder name hints for different project types
FOLDER_HINTS = {
    'code': {
        'src', 'lib', 'bin', 'app', 'srcs', 'source', 'sources',
        'code', 'scripts', 'utils', 'helpers', 'core', 'modules',
        'components', 'services', 'controllers', 'models', 'views',
        'tests', 'test', 'spec', 'specs', 'unit', 'integration',
        'build', 'dist', 'target', 'out', 'output', 'release',
        'config', 'conf', 'settings', 'env', 'environment'
    },
    'writing': {
        'paper', 'thesis', 'manuscript', 'chapters', 'docs', 'references',
        'documentation', 'doc', 'articles', 'posts', 'content',
        'research', 'notes', 'drafts', 'final', 'submission',
        'bibliography', 'citations', 'sources', 'literature'
    },
    'art': {
        'images', 'figures', 'art', 'assets', 'illustrations', 'sketches',
        'portfolio', 'gallery', 'design', 'graphics', 'visuals',
        'photos', 'pictures', 'media', 'resources', 'textures',
        'icons', 'logos', 'banners', 'thumbnails', 'previews'
    }
}


def extract_project_features(root_dir: Union[str, Path]) -> Dict[str, Any]:
    """
    Extract features from a project directory for classification.
    
    Args:
        root_dir: Path to the project directory
        
    Returns:
        Dictionary containing extracted features
    """
    root_path = Path(root_dir)
    ext_counts = Counter()
    folder_names = Counter()
    total_files = 0
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Count folder names (case-insensitive)
        folder_names.update([d.lower() for d in dirnames])
        
        for filename in filenames:
            total_files += 1
            ext = os.path.splitext(filename)[1].lower()
            ext_counts[ext] += 1
    
    # Ensure we don't divide by zero
    total_files = total_files or 1
    
    # Count files by category
    code_count = sum(ext_counts[ext] for ext in CODE_EXTS if ext in ext_counts)
    text_count = sum(ext_counts[ext] for ext in TEXT_EXTS if ext in ext_counts)
    image_count = sum(ext_counts[ext] for ext in IMAGE_EXTS if ext in ext_counts)
    
    return {
        'total_files': total_files,
        'code_count': code_count,
        'text_count': text_count,
        'image_count': image_count,
        'ext_counts': ext_counts,
        'folder_names': folder_names
    }


def simple_score_classify(
    root_dir: Union[str, Path],
    min_files_for_confident: int = 2,
    weights: Tuple[float, float, float] = (3.0, 2.0, 2.5), # 3.0 for code, 2.0 for text, 2.5 for image
    folder_bonus: float = 1.5,
    margin_threshold: float = 0.25, # 0.25 for mixed classification
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
        
    Returns:
        Classification result: 'coding', 'writing', 'art', 'mixed:category1+category2', or 'unknown'
    """
    features = extract_project_features(root_dir)
    total_files = features['total_files']
    
    # Calculate ratios
    code_ratio = features['code_count'] / total_files
    text_ratio = features['text_count'] / total_files
    image_ratio = features['image_count'] / total_files
    
    # Apply weights to get base scores (default weights are 3.0 for code, 2.0 for text, 2.5 for image)
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
        score_text += 0.2
    
    # requirements.txt files suggest coding projects
    requirements_indicators = any(
        'requirements' in ext.lower() or ext.lower() in {'.txt'}
        for ext in features['ext_counts'].keys()
    )
    if requirements_indicators:
        score_code += 0.3

    # License files suggest coding projects
    license_indicators = any(
        'license' in ext.lower() or ext.lower() in {'.txt', '.md'}
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
    
    # If project is too small, return unknown
    if total_files < min_files_for_confident:
        return 'unknown'
    
    # Special case: empty project
    if total_files == 0:
        return 'unknown'
    
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
    has_multiple_types = sum(1 for count in [features['code_count'], features['text_count'], features['image_count']] if count > 0) >= 2
    
    # Consider mixed if:
    # 1. Both scores are reasonably high and close, OR
    # 2. We have multiple file types and both top scores are decent (only if force_mixed is True)
    condition1 = score_difference < margin_threshold and top_score > 1.0 and second_score > 0.8
    condition2 = has_multiple_types and top_score > 0.8 and second_score > 0.5 and score_difference < 1.0
    
    if force_mixed and (condition1 or condition2):
        return f"mixed:{top_label}+{second_label}"
    
    # If not mixed, return the top category
    return top_label


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
            
            # Calculate confidence based on score differences
            code_ratio = features['code_count'] / features['total_files']
            text_ratio = features['text_count'] / features['total_files']
            image_ratio = features['image_count'] / features['total_files']
            
            # Improved confidence calculation
            max_ratio = max(code_ratio, text_ratio, image_ratio)
            # Base confidence on file ratio and total files
            base_confidence = max_ratio * 1.5
            # Boost confidence for more files
            file_boost = min(features['total_files'] * 0.1, 0.3)
            confidence = min(base_confidence + file_boost, 1.0)
            
            return {
                'classification': classification,
                'confidence': confidence,
                'features': features,
                'source': 'zip_file'
            }
    
    # Handle directory
    else:
        features = extract_project_features(project_path)
        classification = simple_score_classify(project_path)
        
        # Calculate confidence
        code_ratio = features['code_count'] / features['total_files']
        text_ratio = features['text_count'] / features['total_files']
        image_ratio = features['image_count'] / features['total_files']
        
        max_ratio = max(code_ratio, text_ratio, image_ratio)
        # Base confidence on file ratio and total files
        base_confidence = max_ratio * 1.5
        # Boost confidence for more files
        file_boost = min(features['total_files'] * 0.1, 0.3)
        confidence = min(base_confidence + file_boost, 1.0)
        
        return {
            'classification': classification,
            'confidence': confidence,
            'features': features,
            'source': 'directory'
        }


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
