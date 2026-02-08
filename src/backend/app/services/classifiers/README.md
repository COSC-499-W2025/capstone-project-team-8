# Project Classifier Module

This module provides classification functionality for uploaded projects, determining whether they are coding projects, writing projects, art/design projects, or mixed.

## Architecture

The module has been refactored into smaller, focused components for better maintainability and testability:

### Module Structure

```
classifiers/
├── __init__.py
├── project_classifier.py      # Main orchestrator
├── file_type_registry.py      # File extension and folder constants
├── feature_extractor.py       # Feature extraction from projects
├── scoring_classifier.py      # Scoring-based classification logic
├── confidence_calculator.py   # Confidence score calculation
└── file_classifier.py         # Individual file classification
```

### Components

#### `project_classifier.py`
Main entry point for project classification. Orchestrates the classification pipeline:
- Handles both zip files and directories
- Extracts features
- Performs classification
- Calculates confidence
- Detects languages and frameworks for coding projects
- Generates human-readable explanations

**Key Functions:**
- `classify_project(project_path)` - Main classification function
- `get_classification_explanation(result)` - Generate explanation text

#### `file_type_registry.py`
Central registry for file types and project structure hints.

**Constants:**
- `CODE_EXTS` - Programming language file extensions
- `TEXT_EXTS` - Document and text file extensions  
- `IMAGE_EXTS` - Image and design file extensions
- `OTHER_BINARY_EXTS` - Binary file extensions
- `FOLDER_HINTS` - Folder name patterns for different project types

**Helper Functions:**
- `is_code_file(filename)` - Check if file is code
- `is_text_file(filename)` - Check if file is text/document
- `is_image_file(filename)` - Check if file is an image
- `get_file_category(filename)` - Get file category

#### `feature_extractor.py`
Extracts statistical features from project directories.

**Functions:**
- `extract_project_features(root_dir)` - Extract file counts, extension distribution, folder structure

**Returns:**
```python
{
    'total_files': int,
    'code_count': int,
    'text_count': int,
    'image_count': int,
    'ext_counts': Counter,
    'folder_names': Counter
}
```

#### `scoring_classifier.py`
Implements scoring-based heuristic classification.

**Functions:**
- `simple_score_classify(root_dir, ...)` - Classify using weighted scoring

**Parameters:**
- `min_files_for_confident` - Minimum files needed for classification
- `weights` - Tuple of (code_weight, text_weight, image_weight)
- `folder_bonus` - Score bonus for matching folder patterns
- `margin_threshold` - Threshold for mixed classification
- `force_mixed` - Whether to prefer mixed classification

**Returns:** Classification string ('coding', 'writing', 'art', 'mixed:X+Y', or 'unknown')

#### `confidence_calculator.py`
Calculates confidence scores for classifications.

**Functions:**
- `calculate_confidence(features)` - Calculate 0-1 confidence score

**Algorithm:**
- Base confidence from dominant file type ratio
- Boost from total file count
- Capped at 1.0

## Usage

### Basic Classification

```python
from app.services.classifiers.project_classifier import classify_project

result = classify_project('/path/to/project')
# or
result = classify_project('/path/to/project.zip')

print(result['classification'])  # 'coding', 'writing', 'art', 'mixed:coding+writing'
print(result['confidence'])      # 0.0-1.0
print(result['languages'])       # ['Python', 'JavaScript']
print(result['frameworks'])      # ['Django', 'React']
print(result['resume_skills'])   # ['Python', 'Django', 'React', ...]
```

### Custom Classification

```python
from app.services.classifiers.scoring_classifier import simple_score_classify

# Classify with custom parameters
classification = simple_score_classify(
    '/path/to/project',
    weights=(5.0, 1.0, 1.0),  # Strongly prefer coding
    folder_bonus=2.0,
    force_mixed=False
)
```

### Feature Extraction Only

```python
from app.services.classifiers.feature_extractor import extract_project_features

features = extract_project_features('/path/to/project')
print(f"Found {features['code_count']} code files")
print(f"Extensions: {features['ext_counts']}")
```

## Testing

All modules have comprehensive unit tests:

```bash
# Test all classifier modules
docker compose exec backend python -m pytest tests/test_file_type_registry.py \
    tests/test_feature_extractor.py \
    tests/test_scoring_classifier.py \
    tests/test_confidence_calculator.py \
    tests/test_project_classifier.py -v

# 44 tests total
```

## Classification Logic

### Scoring Algorithm

1. **Count files by type** (code, text, image)
2. **Calculate ratios** relative to total files
3. **Apply weights** to ratios (default: code=3.0, text=2.0, image=2.5)
4. **Add folder bonuses** if folder names match patterns
5. **Add file indicator bonuses** (README, requirements.txt, etc.)
6. **Determine top 2 categories** by score
7. **Check for mixed project** based on score difference and file diversity
8. **Return classification**

### Confidence Calculation

- **Base:** Dominant file type ratio × 0.8
- **Boost:** Total files × 0.05 (capped at 0.2)
- **Result:** min(base + boost, 1.0)

## Future Enhancements

- Machine learning-based classification
- Support for more file types and frameworks
- Project complexity metrics
- Dependency graph analysis
- README content analysis

## Benefits of Refactored Architecture

✅ **Single Responsibility:** Each module has one focused purpose  
✅ **Testability:** Smaller units are easier to test in isolation  
✅ **Maintainability:** Changes to one aspect don't affect others  
✅ **Extensibility:** Easy to add new classification algorithms  
✅ **Reusability:** Components can be used independently  
✅ **Readability:** Clear separation of concerns
