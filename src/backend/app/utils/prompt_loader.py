"""
Prompt Template Loader Utility

This utility provides functions to load and process prompt templates from markdown files
in the prompts directory. Templates can be used to attach to prompt field in our LLM API,
and then attach the file/files you want to analyze.

Usage:
    from app.utils.prompt_loader import load_prompt_template, get_available_templates, build_prompt

    # Get all available templates
    templates = get_available_templates()
    
    # Load a specific template
    template = load_prompt_template('learning_frontend_code_analysis')
    
    # Build a complete prompt
    full_prompt = build_prompt('learning_frontend_code_analysis', 'Analyze my React components')
"""

import os
import re
from typing import Dict, List, Optional
from pathlib import Path


class PromptTemplate:
    """Represents a parsed prompt template with structured sections."""
    
    def __init__(self, name: str, objective: str, instructions: str, expected_output: str, full_content: str):
        self.name = name
        self.objective = objective.strip()
        self.instructions = instructions.strip()
        self.expected_output = expected_output.strip()
        self.full_content = full_content
    
    def to_dict(self) -> Dict[str, str]:
        """Convert template to dictionary representation."""
        return {
            'name': self.name,
            'objective': self.objective,
            'instructions': self.instructions,
            'expected_output': self.expected_output,
            'full_content': self.full_content
        }
    
    def build_prompt(self, user_input: str = "") -> str:
        """Build a complete prompt by combining template sections with user input."""
        prompt_parts = []
        
        # Add objective
        if self.objective:
            prompt_parts.append(f"Objective: {self.objective}")
        
        # Add instructions
        if self.instructions:
            prompt_parts.append(f"Instructions:\n{self.instructions}")
        
        # Add user input if provided
        if user_input.strip():
            prompt_parts.append(f"Additional Context/Requirements:\n{user_input.strip()}")
        
        # Add expected output
        if self.expected_output:
            prompt_parts.append(f"Expected Output: {self.expected_output}")
        
        return "\n\n".join(prompt_parts)


def get_prompts_directory() -> Path:
    """Get the path to the prompts directory."""
    # Get the directory of this file, then navigate to prompts
    current_dir = Path(__file__).parent
    prompts_dir = current_dir.parent / "prompts"
    return prompts_dir


def get_available_templates() -> List[str]:
    """
    Get list of available prompt template names (without .md extension).
    
    Returns:
        List of template names sorted alphabetically
    """
    prompts_dir = get_prompts_directory()
    
    if not prompts_dir.exists():
        return []
    
    templates = []
    for file_path in prompts_dir.glob("*.md"):
        template_name = file_path.stem
        templates.append(template_name)
    
    return sorted(templates)


def parse_markdown_template(content: str) -> Dict[str, str]:
    """
    Parse markdown template content into structured sections.
    
    Args:
        content: Raw markdown content
        
    Returns:
        Dictionary with parsed sections (objective, instructions, expected_output)
    """
    lines = content.split('\n')
    sections = {
        'objective': '',
        'instructions': '',
        'expected_output': ''
    }
    
    current_section = None
    section_content = []
    
    for line in lines:
        line = line.strip()
        
        # Check for section headers
        if line.startswith('**Objective:**'):
            if current_section and section_content:
                sections[current_section] = '\n'.join(section_content).strip()
            current_section = 'objective'
            section_content = [line.replace('**Objective:**', '').strip()]
            
        elif line.startswith('**Instructions:**'):
            if current_section and section_content:
                sections[current_section] = '\n'.join(section_content).strip()
            current_section = 'instructions'
            section_content = []
            
        elif line.startswith('**Expected Output:**'):
            if current_section and section_content:
                sections[current_section] = '\n'.join(section_content).strip()
            current_section = 'expected_output'
            section_content = [line.replace('**Expected Output:**', '').strip()]
            
        elif line and not line.startswith('#'):
            # Add content to current section
            if current_section:
                section_content.append(line)
    
    # Don't forget the last section
    if current_section and section_content:
        sections[current_section] = '\n'.join(section_content).strip()
    
    return sections


def load_prompt_template(template_name: str) -> Optional[PromptTemplate]:
    """
    Load and parse a prompt template from markdown file.
    
    Args:
        template_name: Name of template file (without .md extension)
        
    Returns:
        PromptTemplate object or None if template not found
        
    Raises:
        FileNotFoundError: If template file doesn't exist
        ValueError: If template content is invalid
    """
    prompts_dir = get_prompts_directory()
    template_path = prompts_dir / f"{template_name}.md"
    
    if not template_path.exists():
        raise FileNotFoundError(f"Template '{template_name}' not found at {template_path}")
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.strip():
            raise ValueError(f"Template '{template_name}' is empty")
        
        # Parse the markdown content
        sections = parse_markdown_template(content)
        
        return PromptTemplate(
            name=template_name,
            objective=sections['objective'],
            instructions=sections['instructions'],
            expected_output=sections['expected_output'],
            full_content=content
        )
        
    except Exception as e:
        raise ValueError(f"Failed to parse template '{template_name}': {str(e)}")


def build_prompt(template_name: str, user_input: str = "") -> str:
    """
    Build a complete prompt by loading a template and adding user input.
    
    Args:
        template_name: Name of template to use
        user_input: Additional context or requirements
        
    Returns:
        Complete prompt string ready for LLM API
        
    Example:
        prompt = build_prompt('learning_frontend_code_analysis', 'Focus on React performance')
    """
    template = load_prompt_template(template_name)
    if not template:
        raise ValueError(f"Template '{template_name}' could not be loaded")
    
    return template.build_prompt(user_input)


def get_template_info(template_name: str) -> Optional[Dict[str, str]]:
    """
    Get information about a specific template without building a prompt.
    
    Args:
        template_name: Name of template
        
    Returns:
        Dictionary with template information or None if not found
    """
    try:
        template = load_prompt_template(template_name)
        return template.to_dict() if template else None
    except (FileNotFoundError, ValueError):
        return None


def search_templates(query: str) -> List[str]:
    """
    Search for templates containing specific keywords.
    
    Args:
        query: Search query (case-insensitive)
        
    Returns:
        List of matching template names
    """
    query = query.lower()
    templates = get_available_templates()
    
    matching_templates = []
    for template_name in templates:
        # Search in template name
        if query in template_name.lower():
            matching_templates.append(template_name)
            continue
            
        # Search in template content
        try:
            template = load_prompt_template(template_name)
            if template and (
                query in template.objective.lower() or
                query in template.instructions.lower() or
                query in template.expected_output.lower()
            ):
                matching_templates.append(template_name)
        except (FileNotFoundError, ValueError):
            continue
    
    return matching_templates


# Category mapping for easier discovery
TEMPLATE_CATEGORIES = {
    'code_analysis': [
        'learning_frontend_code_analysis',
        'learning_backend_code_analysis',
        'improvement_best_practice_analysis',
        'quality_code_complexity_analysis',
        'quality_code_style_consistency_analysis'
    ],
    'testing': [
        'testing_unit_test_generation'
    ],
    'refactoring': [
        'improvement_refactoring',
        'evolution_refactoring_recommendation_generation',
        'architecture_refactoring_for_design_patterns'
    ],
    'business_analysis': [
        'swot_analysis',
        'business_model_canvas_analysis',
        'competitive_positioning_map',
        'porters_five_forces_analysis'
    ],
    'architecture': [
        'architecture_design_pattern_identification',
        'architecture_diagram_generation',
        'architecture_layer_identification',
        'architecture_coupling_cohesion_analysis'
    ],
    'performance': [
        'performance_bottleneck_identification',
        'performance_code_optimization_suggestions',
        'performance_scalability_analysis'
    ]
}


def get_templates_by_category(category: str) -> List[str]:
    """
    Get templates belonging to a specific category.
    
    Args:
        category: Category name (e.g., 'code_analysis', 'testing', 'business_analysis')
        
    Returns:
        List of template names in that category
    """
    return TEMPLATE_CATEGORIES.get(category, [])


def get_all_categories() -> Dict[str, List[str]]:
    """Get all categories and their associated templates."""
    return TEMPLATE_CATEGORIES.copy()