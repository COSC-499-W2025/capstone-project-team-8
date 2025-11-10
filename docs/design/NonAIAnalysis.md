# Non-AI Analysis Feature

## Overview

The non-AI analysis feature provides an alternative to LLM-based analysis, generating resume items, summaries, and statistics using rule-based templates and heuristics. This allows users to get analysis without requiring any AI/LLM services.

## What It Generates

### 1. Resume Items
- **Format**: Bullet-point style descriptions for each project
- **Content**: 
  - Project type and name
  - Technologies used (languages, frameworks)
  - Code metrics (lines of code, file counts)
  - Contribution statistics (commits, lines added/deleted)
  - Project scale information

**Example:**
```json
{
  "project_id": 1,
  "project_name": "my-web-app",
  "bullets": [
    "Developed Software Development Project: my-web-app",
    "• Implemented using JavaScript, Python, HTML",
    "• Utilized React, Django frameworks and libraries",
    "• Wrote 480 lines of code across 3 files",
    "• Contributed 25 commits with 1,200 lines added",
    "• Managed project with 15 files"
  ]
}
```

### 2. Summary
- **Format**: Narrative text describing the portfolio
- **Content**:
  - Overall project count and file statistics
  - Project type breakdown
  - Technology stack overview
  - Contribution activity summary

**Example:**
```
This portfolio contains 2 projects with a total of 23 files, including 16 code files. 
The portfolio includes 2 software development projects. 
Technologies used include JavaScript, Python, HTML, CSS, R. 
Frameworks and libraries include React, Django, Pandas, NumPy. 
Projects show active development with 40 total commits from 2 contributors.
```

### 3. Statistics
- **Format**: Structured data with metrics
- **Sections**:
  - **Overview**: File counts by type
  - **Code Metrics**: Lines of code, averages
  - **Technologies**: Language and framework usage
  - **Contributions**: Commit and line change statistics
  - **Project Types**: Classification information

**Example:**
```json
{
  "overview": {
    "total_projects": 2,
    "total_files": 23,
    "total_code_files": 16,
    "total_text_files": 5,
    "total_image_files": 2
  },
  "code_metrics": {
    "total_lines_of_code": 950,
    "average_lines_per_file": 59.4,
    "code_files_count": 16
  },
  "technologies": {
    "languages": {"Python": 2, "JavaScript": 1, "HTML": 1, "CSS": 1, "R": 1},
    "frameworks": {"React": 1, "Django": 1, "Pandas": 1, "NumPy": 1}
  },
  "contributions": {
    "total_commits": 40,
    "total_lines_added": 2000,
    "total_lines_deleted": 200,
    "net_lines": 1800,
    "unique_contributors": 2
  },
  "project_types": {
    "classification": "coding",
    "confidence": 0.80
  }
}
```

## How to Use

### API Endpoint

**POST** `/api/upload-folder/`

Include the `include_non_ai_analysis` parameter in your form data:

```bash
curl -X POST http://localhost:8000/api/upload-folder/ \
  -F "file=@projects.zip" \
  -F "consent_scan=true" \
  -F "include_non_ai_analysis=true"
```

### Response Structure

When `include_non_ai_analysis=true`, the response will include an additional `non_ai_analysis` field:

```json
{
  "send_to_llm": false,
  "scan_performed": true,
  "source": "zip_file",
  "projects": [...],
  "overall": {...},
  "non_ai_analysis": {
    "resume_items": [...],
    "summary": "...",
    "statistics": {...}
  }
}
```

## Comparison: AI vs Non-AI Analysis

### What Non-AI Analysis Can Do
✅ Generate structured resume items from project metadata  
✅ Create summaries based on file counts, types, and technologies  
✅ Calculate comprehensive statistics  
✅ Work without any external services  
✅ Fast and deterministic results  
✅ No API costs or rate limits  

### What Non-AI Analysis Cannot Do
❌ Generate creative or nuanced descriptions  
❌ Understand code semantics or functionality  
❌ Create context-aware narratives  
❌ Analyze code quality or complexity beyond metrics  
❌ Generate personalized insights  

### How Close Can We Get?

**Statistics**: ✅ **100%** - All statistics are already available and can be formatted identically to AI output.

**Summary**: ⚠️ **~70-80%** - Can generate good summaries using templates, but lacks:
- Contextual understanding of what the project actually does
- Creative phrasing and variety
- Nuanced insights about project relationships

**Resume Items**: ⚠️ **~60-70%** - Can generate functional resume bullets, but lacks:
- Action verbs and achievement-focused language
- Impact statements (e.g., "improved performance by X%")
- Contextual descriptions of what was built

## Implementation Details

### Service Location
`src/backend/app/services/non_ai_analyzer.py`

### Key Functions
- `generate_resume_items(project_data)`: Creates resume-style bullet points
- `generate_summary(project_data)`: Generates narrative summary
- `generate_statistics(project_data)`: Formats statistics
- `generate_non_ai_analysis(project_data)`: Main entry point

### Template-Based Generation

The service uses:
- **Templates**: Pre-defined sentence structures filled with project data
- **Heuristics**: Rules for selecting which information to include
- **Aggregation**: Combining data across multiple projects

### Error Handling

If non-AI analysis generation fails, the endpoint will:
- Log a warning
- Return an error object in `non_ai_analysis`
- Continue processing the rest of the response normally

## Testing

Run tests with:
```bash
python -m unittest tests.test_non_ai_analyzer
```

Or using Django's test runner:
```bash
python manage.py test tests.test_non_ai_analyzer
```

## Future Improvements

1. **Enhanced Templates**: More variety in resume item phrasing
2. **Customizable Formats**: Allow users to specify resume style preferences
3. **Better Aggregation**: Smarter combination of project information
4. **Export Formats**: Direct export to resume formats (PDF, DOCX)
5. **User Preferences**: Allow users to customize what information to include

