"""
Tests for Content-Based Skill Extraction

Tests cover:
- Document type → skill mapping
- Writing style → skill mapping
- Topic → skill mapping
- Complexity → skill mapping
- Structural features → skill mapping
- Project-level skill aggregation
- Deduplication logic
- Quality filters (no generic skills)
- Integration scenarios
"""

import os
import sys
from django.test import TestCase

# Add paths for Django
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
import django
django.setup()

from app.services.analysis.analyzers.content_skills_extractor import (
    extract_skills_from_document,
    extract_skills_from_project_content,
    integrate_content_skills
)
from app.services.analysis.analyzers.content_analyzer import (
    DocumentAnalysis,
    ProjectContentSummary
)


class ContentSkillsExtractorTests(TestCase):
    """Test content-based skill extraction"""
    
    # ===== Document Type Skills Tests =====
    
    def test_research_paper_skills(self):
        """Test skill extraction from research paper"""
        analysis = DocumentAnalysis(
            word_count=1000, character_count=5000, paragraph_count=10, sentence_count=50,
            document_type='research_paper', writing_style='academic', complexity_level='advanced',
            topics=['Machine Learning'], key_terms=[], domain_indicators={'academic_writing': 5},
            has_citations=True, has_code_blocks=False, has_mathematical_notation=True,
            has_lists=False, has_tables=False, has_headings=True,
            avg_word_length=5.5, avg_sentence_length=20, estimated_read_time=5,
            vocabulary_richness=0.7, specialized_term_count=10
        )
        
        skills = extract_skills_from_document(analysis)
        
        self.assertIn('Academic Research', skills)  # From document type
        self.assertIn('Academic Writing', skills)  # From writing style
        self.assertIn('Literature Review', skills)
        self.assertIn('Research Methodology', skills)  # Has citations
        self.assertIn('Advanced Writing', skills)
        self.assertIn('Mathematical Writing', skills)
    
    def test_technical_documentation_skills(self):
        """Test skill extraction from technical documentation"""
        analysis = DocumentAnalysis(
            word_count=800, character_count=4000, paragraph_count=8, sentence_count=40,
            document_type='technical_documentation', writing_style='technical', 
            complexity_level='intermediate',
            topics=['Web Development', 'Database Management'], key_terms=[], 
            domain_indicators={'technical_writing': 8},
            has_citations=False, has_code_blocks=True, has_mathematical_notation=False,
            has_lists=True, has_tables=True, has_headings=True,
            avg_word_length=5.0, avg_sentence_length=15, estimated_read_time=4,
            vocabulary_richness=0.6, specialized_term_count=15
        )
        
        skills = extract_skills_from_document(analysis)
        
        self.assertIn('Technical Writing', skills)
        self.assertIn('Code Documentation', skills)  # Has code blocks
    
    def test_blog_post_skills(self):
        """Test skill extraction from blog post (technical blog)"""
        analysis = DocumentAnalysis(
            word_count=600, character_count=3000, paragraph_count=6, sentence_count=30,
            document_type='blog_post', writing_style='casual', complexity_level='intermediate',
            topics=['DevOps'], key_terms=[], domain_indicators={},
            has_citations=False, has_code_blocks=True, has_mathematical_notation=False,
            has_lists=True, has_tables=False, has_headings=True,
            avg_word_length=4.5, avg_sentence_length=12, estimated_read_time=3,
            vocabulary_richness=0.5, specialized_term_count=5
        )
        
        skills = extract_skills_from_document(analysis)
        
        # All blogs get Content Creation
        self.assertIn('Content Creation', skills)
        # Technical blogs (with code blocks or topics) also get Technical Writing
        self.assertIn('Technical Writing', skills)
        # Should NOT include overly generic skills
        self.assertNotIn('Writing', skills)
    
    def test_creative_writing_skills(self):
        """Test skill extraction from creative writing"""
        analysis = DocumentAnalysis(
            word_count=2000, character_count=10000, paragraph_count=20, sentence_count=100,
            document_type='creative_writing', writing_style='creative', 
            complexity_level='advanced',
            topics=[], key_terms=[], domain_indicators={'creative_writing': 15},
            has_citations=False, has_code_blocks=False, has_mathematical_notation=False,
            has_lists=False, has_tables=False, has_headings=True,
            avg_word_length=5.0, avg_sentence_length=18, estimated_read_time=10,
            vocabulary_richness=0.75, specialized_term_count=0
        )
        
        skills = extract_skills_from_document(analysis)
        
        self.assertIn('Creative Writing', skills)
        self.assertIn('Storytelling', skills)
        self.assertIn('Advanced Writing', skills)
    
    def test_non_technical_blog_post(self):
        """Test that non-technical blogs only get Content Creation"""
        analysis = DocumentAnalysis(
            word_count=500, character_count=2500, paragraph_count=5, sentence_count=25,
            document_type='blog_post', writing_style='casual', complexity_level='intermediate',
            topics=[], key_terms=[], domain_indicators={},  # No tech topics or indicators
            has_citations=False, has_code_blocks=False, has_mathematical_notation=False,
            has_lists=True, has_tables=False, has_headings=True,
            avg_word_length=4.0, avg_sentence_length=10, estimated_read_time=2,
            vocabulary_richness=0.4, specialized_term_count=0
        )
        
        skills = extract_skills_from_document(analysis)
        
        # All blogs get Content Creation
        self.assertIn('Content Creation', skills)
        # Non-technical blogs should NOT get Technical Writing
        self.assertNotIn('Technical Writing', skills)
    
    # ===== Complexity Level Tests =====
    
    def test_advanced_complexity_adds_skill(self):
        """Test that advanced complexity adds skill"""
        analysis = DocumentAnalysis(
            word_count=500, character_count=2500, paragraph_count=5, sentence_count=25,
            document_type='general_article', writing_style='formal', 
            complexity_level='advanced',
            topics=[], key_terms=[], domain_indicators={},
            has_citations=False, has_code_blocks=False, has_mathematical_notation=False,
            has_lists=False, has_tables=False, has_headings=False,
            avg_word_length=6.0, avg_sentence_length=22, estimated_read_time=3,
            vocabulary_richness=0.8, specialized_term_count=10
        )
        
        skills = extract_skills_from_document(analysis)
        
        self.assertIn('Advanced Writing', skills)
    
    
    def test_basic_complexity_no_skill(self):
        """Test that basic complexity doesn't add any skill"""
        analysis = DocumentAnalysis(
            word_count=100, character_count=500, paragraph_count=2, sentence_count=10,
            document_type='general_article', writing_style='formal', 
            complexity_level='basic',
            topics=[], key_terms=[], domain_indicators={},
            has_citations=False, has_code_blocks=False, has_mathematical_notation=False,
            has_lists=False, has_tables=False, has_headings=False,
            avg_word_length=4.0, avg_sentence_length=10, estimated_read_time=1,
            vocabulary_richness=0.3, specialized_term_count=0
        )
        
        skills = extract_skills_from_document(analysis)
        
        # Should get NO skills for basic general article
        self.assertEqual(len(skills), 0)
    
    # ===== Topic-Based Skills Tests =====
    
    def test_multiple_topics_extract_skills(self):
        """Test extraction of multiple topic-based skills"""
        analysis = DocumentAnalysis(
            word_count=1000, character_count=5000, paragraph_count=10, sentence_count=50,
            document_type='technical_documentation', writing_style='technical', 
            complexity_level='intermediate',
            topics=['UI/UX Design'],
            key_terms=[], domain_indicators={'technical_writing': 5},
            has_citations=False, has_code_blocks=True, has_mathematical_notation=False,
            has_lists=True, has_tables=False, has_headings=True,
            avg_word_length=5.0, avg_sentence_length=15, estimated_read_time=5,
            vocabulary_richness=0.6, specialized_term_count=10
        )
        
        skills = extract_skills_from_document(analysis)
        
        self.assertIn('Technical Writing', skills)
        self.assertIn('UX Writing', skills)
    
    # ===== Structural Feature Tests =====
    
    def test_mathematical_notation_in_technical_doc(self):
        """Test that mathematical notation adds Mathematical Writing"""
        analysis = DocumentAnalysis(
            word_count=800, character_count=4000, paragraph_count=8, sentence_count=40,
            document_type='technical_documentation', writing_style='technical', 
            complexity_level='advanced',
            topics=[], key_terms=[], domain_indicators={'technical_writing': 5},
            has_citations=False, has_code_blocks=False, has_mathematical_notation=True,
            has_lists=False, has_tables=False, has_headings=True,
            avg_word_length=5.5, avg_sentence_length=18, estimated_read_time=4,
            vocabulary_richness=0.7, specialized_term_count=15
        )
        
        skills = extract_skills_from_document(analysis)
        
        self.assertIn('Mathematical Writing', skills)
    
    
    # ===== Project-Level Skills Tests =====
    
    def test_long_form_content_skill(self):
        """Test that projects with >10k words get Long-Form Content skill"""
        # Create multiple analyses
        analyses = [
            DocumentAnalysis(
                word_count=4000, character_count=20000, paragraph_count=40, sentence_count=200,
                document_type='technical_documentation', writing_style='technical', 
                complexity_level='intermediate',
                topics=['Web Development'], key_terms=[], domain_indicators={'technical_writing': 10},
                has_citations=False, has_code_blocks=True, has_mathematical_notation=False,
                has_lists=True, has_tables=False, has_headings=True,
                avg_word_length=5.0, avg_sentence_length=15, estimated_read_time=20,
                vocabulary_richness=0.6, specialized_term_count=20
            )
            for _ in range(3)  # 3 docs x 4000 words = 12000 total
        ]
        
        summary = ProjectContentSummary(
            total_documents=3, total_words=12000, total_characters=60000,
            document_types={'technical_documentation': 3},
            primary_document_type='technical_documentation',
            writing_styles=['technical'], primary_writing_style='technical',
            complexity_levels=['intermediate'], primary_complexity='intermediate',
            all_topics=['Web Development'] * 3, primary_topics=['Web Development'],
            domain_indicators={'technical_writing': 30},
            has_citations=False, has_code_examples=True, has_mathematical_content=False,
            average_document_length=4000, estimated_total_read_time=60,
            vocabulary_richness=0.6, document_analyses=analyses
        )
        
        skills = extract_skills_from_project_content(summary)
        
        self.assertIn('Long-Form Content', skills)
    
    def test_multiple_technical_docs_deduplication(self):
        """Test that multiple technical docs with code blocks show only Code Documentation"""
        analyses = [
            DocumentAnalysis(
                word_count=500, character_count=2500, paragraph_count=5, sentence_count=25,
                document_type='technical_documentation', writing_style='technical', 
                complexity_level='intermediate',
                topics=[], key_terms=[], domain_indicators={'technical_writing': 5},
                has_citations=False, has_code_blocks=True, has_mathematical_notation=False,
                has_lists=True, has_tables=False, has_headings=True,
                avg_word_length=5.0, avg_sentence_length=15, estimated_read_time=3,
                vocabulary_richness=0.6, specialized_term_count=10
            )
            for _ in range(6)  # 6 technical docs
        ]
        
        summary = ProjectContentSummary(
            total_documents=6, total_words=3000, total_characters=15000,
            document_types={'technical_documentation': 6},
            primary_document_type='technical_documentation',
            writing_styles=['technical'], primary_writing_style='technical',
            complexity_levels=['intermediate'], primary_complexity='intermediate',
            all_topics=[], primary_topics=[],
            domain_indicators={'technical_writing': 30},
            has_citations=False, has_code_examples=True, has_mathematical_content=False,
            average_document_length=500, estimated_total_read_time=18,
            vocabulary_richness=0.6, document_analyses=analyses
        )
        
        skills = extract_skills_from_project_content(summary)
        
        # Should get Code Documentation (has code blocks)
        # Technical Writing is removed by deduplication when Code Documentation exists
        self.assertIn('Code Documentation', skills)
        self.assertNotIn('Technical Writing', skills)  # Deduplicated
    
    def test_research_portfolio_skill(self):
        """Test that 3+ research papers get Research Portfolio skill"""
        analyses = [
            DocumentAnalysis(
                word_count=2000, character_count=10000, paragraph_count=20, sentence_count=100,
                document_type='research_paper', writing_style='academic', 
                complexity_level='advanced',
                topics=[], key_terms=[], domain_indicators={'academic_writing': 10},
                has_citations=True, has_code_blocks=False, has_mathematical_notation=True,
                has_lists=False, has_tables=True, has_headings=True,
                avg_word_length=5.5, avg_sentence_length=20, estimated_read_time=10,
                vocabulary_richness=0.7, specialized_term_count=15
            )
            for _ in range(4)  # 4 research papers
        ]
        
        summary = ProjectContentSummary(
            total_documents=4, total_words=8000, total_characters=40000,
            document_types={'research_paper': 4},
            primary_document_type='research_paper',
            writing_styles=['academic'], primary_writing_style='academic',
            complexity_levels=['advanced'], primary_complexity='advanced',
            all_topics=[], primary_topics=[],
            domain_indicators={'academic_writing': 40},
            has_citations=True, has_code_examples=False, has_mathematical_content=True,
            average_document_length=2000, estimated_total_read_time=40,
            vocabulary_richness=0.7, document_analyses=analyses
        )
        
        skills = extract_skills_from_project_content(summary)
        
        self.assertIn('Research Portfolio', skills)
    
    # ===== Empty/Edge Case Tests =====
    
    def test_empty_project_returns_empty_skills(self):
        """Test that empty project returns no skills"""
        summary = ProjectContentSummary(
            total_documents=0, total_words=0, total_characters=0,
            document_types={}, primary_document_type='unknown',
            writing_styles=[], primary_writing_style='unknown',
            complexity_levels=[], primary_complexity='basic',
            all_topics=[], primary_topics=[], domain_indicators={},
            has_citations=False, has_code_examples=False, has_mathematical_content=False,
            average_document_length=0, estimated_total_read_time=0,
            vocabulary_richness=0, document_analyses=[]
        )
        
        skills = extract_skills_from_project_content(summary)
        
        self.assertEqual(skills, [])
    
    # ===== Integration Tests =====
    
    def test_integrate_content_skills(self):
        """Test integration of content skills with existing skills"""
        existing_skills = ['Python', 'Django', 'RESTful APIs']
        
        content_files = [
            {
                'path': 'api_docs.md',
                'text': '''
                # API Documentation
                
                This guide explains how to use the REST API endpoints.
                
                ## Authentication
                
                Use the `/api/auth` endpoint with your credentials.
                
                ```python
                import requests
                response = requests.post('/api/auth', json={'username': 'user'})
                ```
                '''
            }
        ]
        
        combined_skills = integrate_content_skills(existing_skills, content_files)
        
        # Should have both code skills and content skills
        self.assertIn('Python', combined_skills)
        self.assertIn('Django', combined_skills)
        # Should have Code Documentation (has code blocks)
        self.assertIn('Code Documentation', combined_skills)
        # Generic "Technical Writing" should be removed when Code Documentation exists
        self.assertNotIn('Technical Writing', combined_skills)
        
        # Should be sorted
        self.assertEqual(combined_skills, sorted(combined_skills))
    
    def test_integrate_content_skills_empty_content(self):
        """Test integration with no content files"""
        existing_skills = ['Python', 'Django']
        content_files = []
        
        combined_skills = integrate_content_skills(existing_skills, content_files)
        
        # Should just return existing skills
        self.assertEqual(combined_skills, existing_skills)

