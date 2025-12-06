"""
HELPER FOR RESUME SKILL EXTRACTOR

Content-Based Skill Extraction

Extracts professional skills from analyzed document content.
Integrates with content_analyzer.py to provide content-aware skill detection.

Usage:
    from app.services.analysis.analyzers.content_skills_extractor import (
        extract_skills_from_project_content
    )
    
    # Analyze content
    summary = analyze_project_content(content_files)
    
    # Extract skills
    skills = extract_skills_from_project_content(summary)
"""

from typing import List, Set
from .content_analyzer import DocumentAnalysis, ProjectContentSummary


# ========== Skill Mapping Dictionaries ==========

# Document types → Skills (only meaningful types)
DOCUMENT_TYPE_SKILLS = {
    'research_paper': [
        'Academic Research',  # Research skill (distinct from Academic Writing)
        'Literature Review'   # Specific scholarly skill
    ],
    'creative_writing': [
        'Creative Writing',  # Specific enough
        'Storytelling'       # Complementary skill
    ],
    # 'technical_documentation' handled by writing_style = 'technical'
    # 'blog_post' handled in _add_structural_skills
    # 'general_article' intentionally omitted - too generic
}

# Writing styles → Skills (only specialized styles)
WRITING_STYLE_SKILLS = {
    'academic': ['Academic Writing'],
    'technical': ['Technical Writing'], 
    'creative': ['Creative Writing'],
    # 'casual', 'formal' intentionally omitted - not resume-worthy
}

# Topics → Domain-specific skills (only truly unique ones)
TOPIC_TO_SKILLS = {
    # Domain expertise shown in languages/frameworks/topics arrays
    # Only include skills that are genuinely different from "Technical Writing"
    'UI/UX Design': ['UX Writing'],
    # ADD MORE HERE AS NEEDED
}

# Domain indicators → Writing specializations
DOMAIN_INDICATOR_SKILLS = {
    'technical_writing': ['Technical Writing'],
    'academic_writing': ['Academic Writing'], 
    'creative_writing': ['Creative Writing'],
    'business_writing': ['Business Writing'],
    'scientific_writing': ['Scientific Writing'],
}


# Specific skills that supersede generic ones (for deduplication)
SPECIFIC_DOC_SKILLS = {
    'Code Documentation',  # Specialized documentation skill
    'UX Writing',          # Different from technical writing
}

MATH_DOCUMENT_TYPES = {'research_paper', 'technical_documentation'}

# ========== Skill Extraction Functions ==========

def extract_skills_from_document(analysis: DocumentAnalysis) -> Set[str]:

    skills = set()
    
    # Document type skills (only for specialized types)
    if analysis.document_type in DOCUMENT_TYPE_SKILLS:
        skills.update(DOCUMENT_TYPE_SKILLS[analysis.document_type])
    
    # Writing style skills (only specialized styles)
    if analysis.writing_style in WRITING_STYLE_SKILLS:
        skills.update(WRITING_STYLE_SKILLS[analysis.writing_style])
    
    # Complexity skill (only if truly advanced)
    if analysis.complexity_level == 'advanced':
        skills.add('Advanced Writing')
    
    # Topic-specific documentation skills
    for topic in analysis.topics:
        if topic in TOPIC_TO_SKILLS:
            skills.update(TOPIC_TO_SKILLS[topic])
    
    # Domain indicator skills (based on keyword density)
    if analysis.domain_indicators:
        # Get the most prominent domain
        top_domain = max(analysis.domain_indicators, key=analysis.domain_indicators.get)
        if top_domain in DOMAIN_INDICATOR_SKILLS:
            skills.update(DOMAIN_INDICATOR_SKILLS[top_domain])

     # Blog posts → Content Creation (always) + conditionally Technical Writing
    if analysis.document_type == 'blog_post':
        _add_blog_post_skills(analysis, skills)
    
    # Structural feature skills (only meaningful combinations)
    _add_structural_skills(analysis, skills)
    
    
    return skills


def extract_skills_from_project_content(summary: ProjectContentSummary) -> List[str]:
    """
    Extract skills from project content summary.
    
    This is the main function to integrate with resume_skill_extractor.
    Aggregates skills from all documents and adds project-level skills.
    Performs deduplication to avoid redundant skills.
    """
    if not summary or summary.total_documents == 0:
        return []
    
    skills = set()
    
    # Aggregate skills from individual documents
    for doc_analysis in summary.document_analyses:
        skills.update(extract_skills_from_document(doc_analysis))
    
    # Project-level skills (only for substantial work)
    _add_project_level_skills(summary, skills)
    
    # Deduplication: remove generic skills if specific ones exist
    _deduplicate_skills(skills)
    
    
    return sorted(list(skills))


# ========== Helper Functions ==========

def _add_structural_skills(analysis: DocumentAnalysis, skills: Set[str]) -> None:
    # Add skills based on structural features (only meaningful combinations)

    # Citations in research papers → Research Methodology
    if analysis.has_citations and analysis.document_type == 'research_paper':
        skills.add('Research Methodology')
    
    # Code blocks in technical writing → Code Documentation
    if analysis.has_code_blocks and analysis.writing_style and 'technical' in analysis.writing_style.lower():
        skills.add('Code Documentation')
    
    # Mathematical notation in technical/academic → Mathematical Writing
    if analysis.has_mathematical_notation and analysis.document_type in MATH_DOCUMENT_TYPES:
        skills.add('Mathematical Writing')
    

def _add_blog_post_skills(analysis: DocumentAnalysis, skills: Set[str]) -> None:

        skills.add('Content Creation')
        
        # Add Technical Writing if it's a technical blog
        is_technical_blog = (
            analysis.writing_style == 'technical' or
            analysis.has_code_blocks or
            analysis.topics or  # Has detected tech topics
            'technical_writing' in analysis.domain_indicators
        )
        
        if is_technical_blog:
            skills.add('Technical Writing')


def _add_project_level_skills(summary: ProjectContentSummary, skills: Set[str]) -> None:
    # Add project-level skills based on aggregate metrics

    # Long-form content (substantial writing)
    if summary.total_words > 10000:
        skills.add('Long-Form Content')
    
    # Research portfolio (multiple research papers)
    if (summary.total_documents >= 3 and 
        summary.primary_document_type == 'research_paper'):
        skills.add('Research Portfolio')


def _deduplicate_skills(skills: Set[str]) -> None:
    # Remove redundant/generic skills when more specific ones exist

    # If specific documentation skills exist, remove generic "Technical Writing"
    if skills & SPECIFIC_DOC_SKILLS:
        skills.discard('Technical Writing')
    
    # Note: Academic Writing/Research and Research Methodology are complementary, not redundant


# ========== Integration Helper ==========

def integrate_content_skills(
    existing_skills: List[str],
    content_files: List[dict]
) -> List[str]:
    """
    Helper function to integrate content-based skills with existing skills.
    
    This is designed to be called from resume_skill_extractor.py
    
    Args:
        existing_skills: Skills already extracted (from languages, frameworks, etc.)
        content_files: List of dicts with 'path' and 'text' keys
        
    Returns:
        Combined list of skills (deduplicated and sorted)
    """
    from .content_analyzer import analyze_project_content
    
    # If no content files, return existing skills
    if not content_files:
        return existing_skills
    
    # Analyze content
    summary = analyze_project_content(content_files)
    
    # Extract content-based skills
    content_skills = extract_skills_from_project_content(summary)
    
    # Merge with existing skills (remove duplicates)
    all_skills = set(existing_skills)
    all_skills.update(content_skills)
    
    return sorted(list(all_skills))

