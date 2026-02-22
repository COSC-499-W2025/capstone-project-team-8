# Project Evaluation Metrics System

## Overview

The Project Evaluation Metrics System automatically evaluates projects during the folder upload process based on **language-specific rubrics**. Each project receives evaluation scores across multiple quality dimensions, providing evidence of success and opportunities for improvement.

## Key Features

### 1. **Language-Specific Rubrics**
Evaluation criteria are customized for each programming language:
- **Python** - Comprehensive Python best practices
- **JavaScript/TypeScript** - Modern JS/TS standards
- **Java** - Enterprise Java patterns
- **C** - Systems programming standards
- **Extensible Framework** - Easy to add more languages

### 2. **Evaluation Categories**
Each project is evaluated across 6 key dimensions:

- **Code Structure (25%)** - Module organization, classes, functions
- **Testing (20%)** - Test coverage, test frameworks, assertions
- **Documentation (15%)** - READMEs, comments, docstrings
- **Dependency Management (15%)** - Package management, lock files
- **Project Organization (15%)** - Directory structure, .gitignore
- **Best Practices (10%)** - Linting, CI/CD, Docker, type hints

### 3. **Automatic Processing**
- Evaluations are automatically generated when projects are uploaded
- Runs for all detected languages in multi-language projects
- Evidence-driven scoring based on actual project artifacts

## Database Schema

### ProjectEvaluation Model

```python
class ProjectEvaluation(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE)
    language = models.CharField(max_length=50)
    
    # Scores
    overall_score = models.FloatField()  # 0-100
    code_quality_score = models.FloatField()
    documentation_score = models.FloatField()
    structure_score = models.FloatField()
    testing_score = models.FloatField()
    
    # Detailed data
    category_scores = models.JSONField()  # Category breakdown
    rubric_evaluation = models.JSONField()  # Detailed rubric info
    evidence = models.JSONField()  # Supporting evidence
    
    evaluated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

## API Endpoints

### 1. **Get Projects by Language**
```
GET /api/evaluations/<language>/
```
Get all project evaluations for a specific language.

**Query Parameters:**
- `min_score` (0-100): Filter by minimum score
- `max_score` (0-100): Filter by maximum score
- `sort`: Sort field (default: `-overall_score`)

**Example:**
```
GET /api/evaluations/python/?min_score=70&max_score=100&sort=-overall_score
```

**Response:**
```json
{
  "language": "python",
  "count": 15,
  "min_score_filter": 70,
  "max_score_filter": 100,
  "evaluations": [
    {
      "id": 1,
      "project_id": 42,
      "project_name": "My Project",
      "language": "python",
      "overall_score": 85.5,
      "category_scores": {
        "code_structure": 90.0,
        "testing": 75.0,
        "documentation": 85.0,
        ...
      }
    }
  ]
}
```

### 2. **Get Top Projects by Language**
```
GET /api/evaluations/<language>/top/
```
Get the highest-rated projects for a language.

**Query Parameters:**
- `limit` (1-100): Number of projects to return (default: 10)

**Example:**
```
GET /api/evaluations/javascript/top/?limit=20
```

### 3. **Get Language Statistics**
```
GET /api/evaluations/<language>/stats/
```
Get aggregated evaluation statistics for a language.

**Response:**
```json
{
  "language": "python",
  "total_projects": 25,
  "average_score": 72.5,
  "highest_score": 95.0,
  "lowest_score": 45.0,
  "average_code_quality": 75.3,
  "average_documentation": 68.2,
  "average_testing": 65.5,
  "average_structure": 78.1
}
```

### 4. **Get Project Evaluation Detail**
```
GET /api/evaluations/project/<project_id>/<language>/
```
Get detailed evaluation for a specific project and language.

**Response:**
```json
{
  "id": 1,
  "project_id": 42,
  "project_name": "My Project",
  "language": "python",
  "overall_score": 85.5,
  "category_scores": { ... },
  "evidence": {
    "py_files": 10,
    "has_tests": true,
    "test_framework": "pytest",
    "has_readme": true,
    "has_ci_config": true,
    ...
  },
  "rubric_evaluation": { ... }
}
```

### 5. **Get Evaluation Summary**
```
GET /api/evaluations/project/<project_id>/<language>/summary/
```
Get a formatted summary with grade, strengths, and improvement areas.

**Response:**
```json
{
  "language": "python",
  "overall_score": 85.5,
  "score_percentage": "85.5%",
  "grade": "B",
  "category_breakdown": {
    "Code Structure": 90.0,
    "Testing": 75.0,
    "Documentation": 85.0,
    ...
  },
  "top_strengths": [
    "Code Structure",
    "Documentation",
    "Project Organization"
  ],
  "areas_for_improvement": [
    "Testing",
    "Dependency Management"
  ]
}
```

### 6. **Get Project All Evaluations**
```
GET /api/evaluations/project/<project_id>/
```
Get all evaluations for a project across all detected languages.

## Evaluation Examples

### Python Project Evaluation

A Python project might be evaluated like this:

**Evidence Found:**
- ✅ 15 Python files with proper module structure
- ✅ `__main__` entry point found
- ✅ Uses OOP (classes defined)
- ✅ pytest framework configured
- ✅ Test files with proper naming
- ✅ Comprehensive README.md
- ✅ Docstrings in code
- ✅ requirements.txt with pinned versions
- ✅ Source code in src/ directory
- ✅ Tests in tests/ directory
- ✅ .gitignore present
- ✅ GitHub Actions CI configuration

**Resulting Scores:**
```
Code Structure: 95/100
Testing: 85/100
Documentation: 90/100
Dependency Management: 85/100
Project Organization: 90/100
Best Practices: 80/100

Overall: 87.5/100 → Grade: B
```

### JavaScript Project Evaluation

A JavaScript project evaluation might show:

**Evidence Found:**
- ✅ 25 JS/TS files with ES6 modules
- ✅ TypeScript configuration
- ✅ Jest test suite with 15 test files
- ✅ Airbnb ESLint config
- ✅ Prettier formatting config
- ✅ Vite build tool configured
- ✅ package.json and package-lock.json
- ✅ Comprehensive README
- ✅ JSDoc comments
- ✅ Docker configuration
- ✅ GitHub Actions workflow
- ❌ Low test coverage (missing coverage config)

**Resulting Scores:**
```
Code Structure: 90/100
Testing: 70/100
Documentation: 85/100
Dependency Management: 95/100
Project Organization: 85/100
Best Practices: 88/100

Overall: 85.5/100 → Grade: B
```

## Integration with Upload Process

When a project is uploaded:

1. **Files are scanned and classified** (existing process)
2. **Languages are detected** (existing process)
3. **Project metadata is saved to database** (existing process)
4. **NEW: Evaluations are automatically generated** for each detected language
5. **Evidence is collected** showing what led to each score
6. **Evaluation results are persisted** to the database

## Using Evaluations in Frontend

### Display Project Grade
```javascript
// Get single evaluation
const response = await fetch(`/api/evaluations/project/${projectId}/${language}/summary/`);
const evaluation = await response.json();

// Display grade
console.log(`Grade: ${evaluation.grade}`);
console.log(`Score: ${evaluation.score_percentage}`);
```

### Show Language Rankings
```javascript
// Get top projects for a language
const response = await fetch(`/api/evaluations/python/top/?limit=10`);
const data = await response.json();

// Display rankings
data.top_projects.forEach((proj, idx) => {
  console.log(`${idx + 1}. ${proj.project_name}: ${proj.overall_score}%`);
});
```

### Build Portfolio Selection Filter
```javascript
// Get all Python projects within score range
const response = await fetch(`/api/evaluations/python/?min_score=70&max_score=100`);
const data = await response.json();

// Use for portfolio showcasing
const quality_projects = data.evaluations;
```

## Extending with New Languages

To add evaluation support for a new language:

1. **Create a new Rubric class:**
```python
from app.services.evaluation.language_rubrics import LanguageRubric

class GoRubric(LanguageRubric):
    def __init__(self):
        super().__init__()
        self.language = "go"
    
    def evaluate(self, project_analysis):
        # Implement Go-specific evaluation
        ...
```

2. **Register in factory function:**
```python
def get_rubric_for_language(language: str) -> LanguageRubric:
    rubric_map = {
        ...
        'go': GoRubric(),
    }
    return rubric_map.get(language, None)
```

3. **Done!** The evaluation service will automatically use it for Go projects.

## Scoring Methodology

### Score Calculation

Each category score is calculated as:
```
Category Score = (Evidence Points / Max Evidence Points) × 100
```

### Overall Score Calculation
```
Overall Score = Σ(Category Score × Category Weight)
```

Where weights are:
- Code Structure: 25%
- Testing: 20%
- Documentation: 15%
- Dependency Management: 15%
- Project Organization: 15%
- Best Practices: 10%

### Grade Mapping
- A: 90-100
- B: 80-89
- C: 70-79
- D: 60-69
- F: < 60

## Performance Considerations

- Evaluations are generated **asynchronously** during upload processing
- If evaluation fails, upload still succeeds (non-blocking)
- Evaluations can be **regenerated** on-demand
- Index on `(language, overall_score)` for fast queries
- Index on `(project, language)` for unique lookups

## Future Enhancements

Potential improvements to this system:

1. **Custom Rubrics** - Users define their own evaluation criteria
2. **Historical Tracking** - Track how scores change over time
3. **Peer Comparison** - Show how projects compare to peers
4. **Improvement Suggestions** - AI-generated recommendations
5. **Weighted Importance** - Users adjust category weights
6. **Team Metrics** - Aggregate team quality over projects
7. **Temporal Analysis** - Identify improvement trends
8. **Export Reports** - Generate PDF evaluation reports

## Troubleshooting

### Evaluations not being generated
- Ensure ProjectDatabaseService is importing ProjectEvaluationService
- Check that project files are being saved correctly
- Verify evaluation service doesn't throw exceptions during upload

### Scores seem incorrect
- Review the `evidence` field in the evaluation to see what was detected
- Check if language detection is working correctly
- Compare against the rubric criteria for that language

### Performance issues
- Cache evaluation statistics results
- Consider evaluating only on-demand for very large projects
- Use database query optimization for language filtering

## API Authentication

All evaluation endpoints require authentication:
```bash
# Get token
curl -X POST http://localhost:8000/api/token/ \
  -d "username=user&password=pass"

# Use token
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/evaluations/python/
```
