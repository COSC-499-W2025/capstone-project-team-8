# Prompt Template Utility

A Python utility for loading and using structured prompt templates from markdown files. This utility makes it easy to use our collection of 70+ analysis templates in LLM API calls.

## Features

- **70+ Pre-built Open Source Templates** - Code analysis, testing, refactoring, business analysis, and more that might be useful
- **Structured Parsing** - Extracts objective, instructions, and expected output from markdown
- **Easy Integration** - Simple functions to build complete prompts
- **Search & Discovery** - Find templates by keyword or category
- **Template Categories** - Organized by purpose

## Overview

### Basic Usage

```python
from app.utils.prompt_loader import build_prompt

# Build a prompt for code analysis
prompt = build_prompt(
    'learning_frontend_code_analysis', 
    'Focus on React performance and state management'
)

import requests

# Send prompt + user's code file for analysis
# The prompt contains the analysis instructions, the file contains the code to analyze
code_file_path = 'my_react_component.jsx'  # User's code file
with open(code_file_path, 'rb') as f:
    files = {'file': ('my_react_component.jsx', f)}
    data = {'prompt': prompt, 'model': 'mistral:latest'}
    response = requests.post(
        'http://localhost:3001/api/query',
        data=data,
        files=files,
        headers={'x-api-key': 'your-api-key'}
    )

print(response.json())
```

### Explore Available Templates

```python
from app.utils.prompt_loader import get_available_templates, search_templates

# List all templates
templates = get_available_templates()
print(f"Found {len(templates)} templates")

# Search for specific types
code_templates = search_templates("code analysis")
test_templates = search_templates("test")
business_templates = search_templates("business")
```

### Inspect Template Details

```python
from app.utils.prompt_loader import load_prompt_template

# Load and inspect a template
template = load_prompt_template('improvement_best_practice_analysis')
print(f"Objective: {template.objective}")
print(f"Instructions: {template.instructions}")
print(f"Expected Output: {template.expected_output}")
```

## Functions

| Function | Description | Example |
|----------|-------------|---------|
| `get_available_templates()` | List all template names | `templates = get_available_templates()` |
| `load_prompt_template(name)` | Load template details | `template = load_prompt_template('testing_unit_test_generation')` |
| `build_prompt(name, context)` | Build complete prompt | `prompt = build_prompt('swot_analysis', 'Analyze our mobile app')` |
| `search_templates(query)` | Search by keyword | `results = search_templates('performance')` |
| `get_templates_by_category(cat)` | Get templates by category | `templates = get_templates_by_category('code_analysis')` |

## 🧪 Testing

Run the test suite to verify everything works:

```bash
python tests\test_prompt_loader.py
```