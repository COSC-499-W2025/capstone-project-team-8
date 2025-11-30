"""
Tests for Content Analyzer

Tests cover:
- Document type classification (research papers, blog posts, technical docs, etc.)
- Topic extraction from text
- Writing style detection (academic, technical, casual, creative, formal)
- Complexity assessment (basic, intermediate, advanced)
- Structural feature detection (citations, code blocks, math, lists, tables, headings)
- Metrics calculation (word count, read time, vocabulary richness)
- Project-level content aggregation
- Edge cases (empty text, very short documents, missing data)
"""

import os
import sys
from pathlib import Path
from django.test import TestCase

# Add the project root to Python path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
import django
django.setup()

from app.services.analysis.analyzers.content_analyzer import (
    ContentAnalyzer,
    analyze_document,
    analyze_project_content,
    DocumentAnalysis,
    ProjectContentSummary
)


class ContentAnalyzerTests(TestCase):
    """Test content analysis functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = ContentAnalyzer()
    
    # ===== Document Type Classification Tests =====
    
    def test_research_paper_detection(self):
        """Test detection of research paper document type"""
        text = """
        Abstract
        
        This study examines the effects of machine learning on data analysis.
        
        Introduction
        
        Previous research by Smith et al. (2020) has shown that neural networks
        can improve prediction accuracy.
        
        Methodology
        
        We conducted experiments using a dataset of 10,000 samples.
        
        Results
        
        Our findings indicate a 25% improvement over baseline methods.
        
        Conclusion
        
        This research demonstrates the effectiveness of the proposed approach.
        
        References
        
        Smith, J. et al. (2020). Machine Learning Applications.
        """
        
        analysis = self.analyzer.analyze_document(text)
        
        self.assertEqual(analysis.document_type, 'research_paper')
        self.assertTrue(analysis.has_citations)
        self.assertGreater(analysis.word_count, 0)
    
    def test_technical_documentation_detection(self):
        """Test detection of technical documentation"""
        text = """
        # API Documentation
        
        ## Authentication
        
        Use the `/api/auth` endpoint to authenticate users.
        
        ### Request
        
        ```json
        {
            "username": "user",
            "password": "pass"
        }
        ```
        
        ### Response
        
        Returns a JSON object with an access token.
        
        ## Functions
        
        ### getUserData(userId)
        
        **Parameters:**
        - userId: The ID of the user to fetch
        
        **Returns:**
        - User object with name, email, and profile data
        """
        
        analysis = self.analyzer.analyze_document(text)
        
        self.assertEqual(analysis.document_type, 'technical_documentation')
        self.assertTrue(analysis.has_code_blocks)
        self.assertTrue(analysis.has_headings)
    
    def test_blog_post_detection(self):
        """Test detection of blog post/article"""
        text = """
        How to Build Your First Machine Learning Model: A Beginner's Guide
        
        Welcome! In this tutorial, we'll walk through the process of building
        your first machine learning model. Don't worry if you're new to this -
        I'll explain everything step by step.
        
        Let's get started!
        
        First, you'll need to install Python and some libraries...
        """
        
        analysis = self.analyzer.analyze_document(text)
        
        self.assertEqual(analysis.document_type, 'blog_post')
        self.assertEqual(analysis.writing_style, 'casual')
    
    def test_creative_writing_detection(self):
        """Test detection of creative writing"""
        text = """
        Chapter 1: The Beginning
        
        Once upon a time in a distant land, there lived a young protagonist
        named Sarah. She whispered to her companion, "We must find the ancient
        artifact before sunset."
        
        The character development in this scene was crucial to the overall plot.
        The narrative continued as they journeyed through the dark forest.
        
        "We're almost there," he said, looking at the mysterious map.
        """
        
        analysis = self.analyzer.analyze_document(text)
        
        self.assertEqual(analysis.document_type, 'creative_writing')
        self.assertEqual(analysis.writing_style, 'creative')
    
    # ===== Writing Style Detection Tests =====
    
    def test_academic_style_detection(self):
        """Test detection of academic writing style"""
        text = """
        This research investigates the hypothesis that neural networks can
        improve classification accuracy. The methodology employed in this study
        follows established protocols for machine learning experiments.
        """
        
        analysis = self.analyzer.analyze_document(text)
        self.assertEqual(analysis.writing_style, 'academic')
    
    def test_technical_style_detection(self):
        """Test detection of technical writing style"""
        text = """
        The API endpoint accepts GET requests and returns JSON data.
        Use the `fetch()` function to retrieve user information.
        """
        
        analysis = self.analyzer.analyze_document(text)
        self.assertEqual(analysis.writing_style, 'technical')
    
    def test_casual_style_detection(self):
        """Test detection of casual writing style"""
        text = """
        Hey there! I'm going to show you how to set up your development
        environment. You'll love how easy this is, and we'll get you
        up and running in no time. Let's dive in!
        """
        
        analysis = self.analyzer.analyze_document(text)
        self.assertEqual(analysis.writing_style, 'casual')
    
    # ===== Complexity Assessment Tests =====
    
    def test_basic_complexity(self):
        """Test detection of basic writing complexity"""
        text = "This is a short text. It has simple words. Very easy to read."
        
        analysis = self.analyzer.analyze_document(text)
        self.assertEqual(analysis.complexity_level, 'basic')
    
    def test_advanced_complexity(self):
        """Test detection of advanced writing complexity"""
        text = """
        The multifaceted ramifications of contemporary technological innovations
        necessitate comprehensive evaluation of societal implications. Consequently,
        interdisciplinary collaboration becomes paramount for addressing these
        substantial challenges. Furthermore, the paradigmatic shift in computational
        methodologies requires sophisticated analytical frameworks.
        """
        
        analysis = self.analyzer.analyze_document(text)
        self.assertEqual(analysis.complexity_level, 'advanced')
    
    # ===== Topic Extraction Tests =====
    
    def test_machine_learning_topic_extraction(self):
        """Test extraction of Machine Learning topic"""
        text = """
        This project implements a neural network for image classification using
        deep learning techniques. The machine learning model achieves 95% accuracy
        on the test dataset.
        """
        
        analysis = self.analyzer.analyze_document(text)
        self.assertIn('Machine Learning', analysis.topics)
    
    def test_web_development_topic_extraction(self):
        """Test extraction of Web Development topic"""
        text = """
        This web application uses a REST API backend with a React frontend.
        The web development stack includes Node.js and PostgreSQL.
        """
        
        analysis = self.analyzer.analyze_document(text)
        self.assertIn('Web Development', analysis.topics)
    
    def test_multiple_topics_extraction(self):
        """Test extraction of multiple topics"""
        text = """
        This project combines machine learning and web development to create
        an AI-powered web application. The cloud infrastructure uses AWS and
        Kubernetes for deployment automation (DevOps).
        """
        
        analysis = self.analyzer.analyze_document(text)
        # Should detect multiple topics
        self.assertGreater(len(analysis.topics), 1)
    
    # ===== Structural Feature Detection Tests =====
    
    def test_citation_detection(self):
        """Test detection of citations in text"""
        text_with_bracket_citations = "According to recent research [1], machine learning is effective."
        analysis1 = self.analyzer.analyze_document(text_with_bracket_citations)
        self.assertTrue(analysis1.has_citations)
        
        text_with_parenthetical = "Smith (2020) found that AI improves accuracy."
        analysis2 = self.analyzer.analyze_document(text_with_parenthetical)
        self.assertTrue(analysis2.has_citations)
        
        text_with_et_al = "Previous work by Jones et al. demonstrated this effect."
        analysis3 = self.analyzer.analyze_document(text_with_et_al)
        self.assertTrue(analysis3.has_citations)
    
    def test_code_block_detection(self):
        """Test detection of code blocks"""
        text_with_fenced = """
        Here's an example:
        ```python
        def hello():
            print("Hello, World!")
        ```
        """
        analysis1 = self.analyzer.analyze_document(text_with_fenced)
        self.assertTrue(analysis1.has_code_blocks)
        
        text_with_inline = "Use the `print()` function to output text."
        analysis2 = self.analyzer.analyze_document(text_with_inline)
        self.assertTrue(analysis2.has_code_blocks)
    
    def test_math_notation_detection(self):
        """Test detection of mathematical notation"""
        text_with_latex = "The equation is $E = mc^2$ where m is mass."
        analysis1 = self.analyzer.analyze_document(text_with_latex)
        self.assertTrue(analysis1.has_mathematical_notation)
        
        text_with_theorem = "Theorem 1: The sum of angles in a triangle equals 180 degrees."
        analysis2 = self.analyzer.analyze_document(text_with_theorem)
        self.assertTrue(analysis2.has_mathematical_notation)
    
    def test_list_detection(self):
        """Test detection of lists"""
        text_with_bullets = """
        Features include:
        - Fast processing
        - Easy to use
        - Highly scalable
        """
        analysis1 = self.analyzer.analyze_document(text_with_bullets)
        self.assertTrue(analysis1.has_lists)
        
        text_with_numbers = """
        Steps:
        1. Install dependencies
        2. Configure settings
        3. Run the application
        """
        analysis2 = self.analyzer.analyze_document(text_with_numbers)
        self.assertTrue(analysis2.has_lists)
    
    def test_table_detection(self):
        """Test detection of tables"""
        text_with_table = """
        | Feature | Status |
        |---------|--------|
        | API     | Done   |
        | UI      | WIP    |
        """
        
        analysis = self.analyzer.analyze_document(text_with_table)
        self.assertTrue(analysis.has_tables)
    
    def test_heading_detection(self):
        """Test detection of markdown headings"""
        text_with_headings = """
        # Main Title
        
        ## Section 1
        
        ### Subsection 1.1
        
        Content goes here.
        """
        
        analysis = self.analyzer.analyze_document(text_with_headings)
        self.assertTrue(analysis.has_headings)
    
    # ===== Metrics Calculation Tests =====
    
    def test_word_count(self):
        """Test word count calculation"""
        text = "This text has exactly seven words total."
        analysis = self.analyzer.analyze_document(text)
        self.assertEqual(analysis.word_count, 7)
    
    def test_sentence_count(self):
        """Test sentence count calculation"""
        text = "First sentence. Second sentence! Third sentence?"
        analysis = self.analyzer.analyze_document(text)
        self.assertEqual(analysis.sentence_count, 3)
    
    def test_paragraph_count(self):
        """Test paragraph count calculation"""
        text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
        analysis = self.analyzer.analyze_document(text)
        self.assertEqual(analysis.paragraph_count, 3)
    
    def test_read_time_estimation(self):
        """Test reading time estimation"""
        # Create text with ~400 words (should be 2 minutes at 200 words/min)
        text = " ".join(["word"] * 400)
        analysis = self.analyzer.analyze_document(text)
        self.assertEqual(analysis.estimated_read_time, 2)
    
    def test_vocabulary_richness(self):
        """Test vocabulary richness calculation"""
        # Text with all unique words
        text_rich = "unique different distinct separate individual varied diverse"
        analysis_rich = self.analyzer.analyze_document(text_rich)
        self.assertEqual(analysis_rich.vocabulary_richness, 1.0)
        
        # Text with repeated words
        text_poor = "word word word word word"
        analysis_poor = self.analyzer.analyze_document(text_poor)
        self.assertLess(analysis_poor.vocabulary_richness, 0.5)
    
    # ===== Edge Cases Tests =====
    
    def test_empty_text(self):
        """Test handling of empty text"""
        analysis = self.analyzer.analyze_document("")
        
        self.assertEqual(analysis.word_count, 0)
        self.assertEqual(analysis.document_type, 'unknown')
        self.assertEqual(len(analysis.topics), 0)
    
    def test_whitespace_only(self):
        """Test handling of whitespace-only text"""
        analysis = self.analyzer.analyze_document("   \n\n   \t   ")
        
        self.assertEqual(analysis.word_count, 0)
        self.assertEqual(analysis.document_type, 'unknown')
    
    def test_very_short_text(self):
        """Test handling of very short text"""
        text = "Short."
        analysis = self.analyzer.analyze_document(text)
        
        self.assertEqual(analysis.word_count, 1)
        self.assertEqual(analysis.complexity_level, 'basic')
    
    # ===== Convenience Function Tests =====
    
    def test_analyze_document_convenience_function(self):
        """Test the convenience function for single document analysis"""
        text = "This is a test document about machine learning."
        analysis = analyze_document(text)
        
        self.assertIsInstance(analysis, DocumentAnalysis)
        self.assertGreater(analysis.word_count, 0)
    
    # ===== Project Content Summary Tests =====
    
    def test_project_content_aggregation(self):
        """Test aggregation of multiple documents"""
        files = [
            {
                'path': 'doc1.md',
                'text': 'This is a research paper about machine learning. Abstract. Introduction. Methodology. Results. Conclusion.'
            },
            {
                'path': 'doc2.md',
                'text': 'This is another research paper about data science. Abstract. Introduction. Methodology. Results. Conclusion.'
            }
        ]
        
        summary = self.analyzer.analyze_project_content(files)
        
        self.assertEqual(summary.total_documents, 2)
        self.assertGreater(summary.total_words, 0)
        self.assertEqual(summary.primary_document_type, 'research_paper')
    
    def test_project_topic_aggregation(self):
        """Test aggregation of topics across documents"""
        files = [
            {'path': 'doc1.md', 'text': 'Machine learning and neural networks for AI.'},
            {'path': 'doc2.md', 'text': 'Deep learning with machine learning models.'},
            {'path': 'doc3.md', 'text': 'Web development with REST APIs.'}
        ]
        
        summary = self.analyzer.analyze_project_content(files)
        
        # Machine Learning should be the primary topic (appears in 2/3 docs)
        self.assertIn('Machine Learning', summary.primary_topics)
    
    def test_project_structural_features(self):
        """Test aggregation of structural features"""
        files = [
            {'path': 'doc1.md', 'text': 'Document with citations [1] and references.'},
            {'path': 'doc2.md', 'text': 'Document with code ```python\nprint("hi")\n```'},
            {'path': 'doc3.md', 'text': 'Document with math $E=mc^2$'}
        ]
        
        summary = self.analyzer.analyze_project_content(files)
        
        self.assertTrue(summary.has_citations)
        self.assertTrue(summary.has_code_examples)
        self.assertTrue(summary.has_mathematical_content)
    
    def test_empty_project(self):
        """Test handling of project with no content"""
        summary = self.analyzer.analyze_project_content([])
        
        self.assertEqual(summary.total_documents, 0)
        self.assertEqual(summary.total_words, 0)
        self.assertEqual(summary.primary_document_type, 'unknown')
    
    def test_project_with_empty_files(self):
        """Test handling of project with empty text files"""
        files = [
            {'path': 'empty1.md', 'text': ''},
            {'path': 'empty2.md', 'text': '   '},
            {'path': 'valid.md', 'text': 'This has actual content.'}
        ]
        
        summary = self.analyzer.analyze_project_content(files)
        
        # Should only analyze the valid file
        self.assertEqual(summary.total_documents, 1)
        self.assertGreater(summary.total_words, 0)
    
    def test_analyze_project_content_convenience_function(self):
        """Test the convenience function for project analysis"""
        files = [
            {'path': 'doc1.md', 'text': 'First document about machine learning.'},
            {'path': 'doc2.md', 'text': 'Second document about data science.'}
        ]
        
        summary = analyze_project_content(files)
        
        self.assertIsInstance(summary, ProjectContentSummary)
        self.assertEqual(summary.total_documents, 2)
    
    # ===== Domain Indicator Tests =====
    
    def test_technical_writing_domain(self):
        """Test detection of technical writing domain"""
        text = "This documentation provides a comprehensive guide and manual for the API specification."
        analysis = self.analyzer.analyze_document(text)
        
        self.assertIn('technical_writing', analysis.domain_indicators)
        self.assertGreater(analysis.domain_indicators['technical_writing'], 0)
    
    def test_academic_writing_domain(self):
        """Test detection of academic writing domain"""
        text = "This research study presents an analysis of the findings from our hypothesis testing."
        analysis = self.analyzer.analyze_document(text)
        
        self.assertIn('academic_writing', analysis.domain_indicators)
        self.assertGreater(analysis.domain_indicators['academic_writing'], 0)
    
    # ===== Integration Tests =====
    
    def test_complete_document_analysis_workflow(self):
        """Test complete analysis workflow with real-world-like content"""
        text = """
        # Machine Learning for Beginners: A Complete Guide
        
        ## Introduction
        
        In this tutorial, we'll explore the fundamentals of machine learning and
        neural networks. You'll learn how to build your first AI model step by step.
        
        ## What is Machine Learning?
        
        Machine learning is a subset of artificial intelligence (AI) that enables
        systems to learn and improve from experience.
        
        ## Building Your First Model
        
        Let's start with a simple example:
        
        ```python
        import tensorflow as tf
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dense(10, activation='softmax')
        ])
        ```
        
        ## Results
        
        Our model achieved 95% accuracy on the test set.
        
        ## Conclusion
        
        Machine learning opens up exciting possibilities for data analysis and
        automation. We hope you'll continue learning!
        """
        
        analysis = self.analyzer.analyze_document(text, "ml_tutorial.md")
        
        # Verify comprehensive analysis
        self.assertGreater(analysis.word_count, 50)
        # Document could be classified as blog_post, technical_documentation, or research_paper
        # depending on the balance of keywords
        self.assertIn(analysis.document_type, ['blog_post', 'technical_documentation', 'research_paper'])
        self.assertTrue(analysis.has_code_blocks)
        self.assertTrue(analysis.has_headings)
        self.assertIn('Machine Learning', analysis.topics)
        self.assertGreater(analysis.estimated_read_time, 0)
        self.assertIsInstance(analysis.key_terms, list)

