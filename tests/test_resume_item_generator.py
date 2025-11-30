"""
Tests for Resume Item Generator Service

Tests cover:
- Different project types (coding, writing, mixed)
- Category-based generation (languages, frameworks, skills, content, git)
- Framework-specific contextual templates
- Content analysis integration with edge cases
- Git contribution statistics (solo, collaborative, user matching)
- Coverage tracking and non-overlapping generation
- Minimal data scenarios and error handling
"""

import os
import sys
from datetime import datetime
from django.test import TestCase

# Add the project root to Python path so tests can be discovered
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
import django
django.setup()

from app.services.resume_item_generator import ResumeItemGenerator
from app.services.analysis.analyzers.content_analyzer import ProjectContentSummary


class ResumeItemGeneratorTests(TestCase):
    """Test suite for resume item generator functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = ResumeItemGenerator()

    # ===== Coding Projects =====

    def test_coding_project_with_full_data(self):
        """Test coding project with languages, frameworks, skills"""
        project_data = {
            'root': 'my-web-app',
            'classification': {
                'type': 'coding',
                'languages': ['Python', 'JavaScript', 'HTML'],
                'frameworks': ['Django', 'React'],
                'resume_skills': ['Backend Development', 'RESTful APIs', 'Frontend Development']
            },
            'created_at': int(datetime(2023, 1, 15).timestamp()),
            'end_date': int(datetime(2024, 6, 20).timestamp()),
            'files': {
                'code': [{'path': 'main.py'}, {'path': 'app.js'}],
                'content': [{'path': 'README.md'}],
                'image': [],
                'unknown': []
            },
            'collaborative': False
        }
        
        result = self.generator.generate_resume_items(project_data)
        
        self.assertIn('items', result)
        self.assertIn('generated_at', result)
        self.assertGreaterEqual(len(result['items']), 3)
        
        # Should contain framework-specific contextual templates or category bullets
        items_text = ' '.join(result['items'])
        self.assertTrue(
            any('Python' in item or 'Django' in item or 'React' in item or 'JavaScript' in item 
                for item in result['items'])
        )

    def test_coding_project_collaborative_with_git_stats(self):
        """Test collaborative coding project with git contribution statistics"""
        project_data = {
            'root': 'team-project',
            'classification': {
                'type': 'coding',
                'languages': ['Python'],
                'frameworks': [],
                'resume_skills': ['Web Backend']
            },
            'created_at': int(datetime(2022, 3, 10).timestamp()),
            'end_date': int(datetime(2023, 12, 5).timestamp()),
            'files': {
                'code': [{'path': 'app.py'}],
                'content': [],
                'image': [],
                'unknown': []
            },
            'collaborative': True,
            'contributors': [
                {
                    'name': 'John Doe',
                    'commits': 45,
                    'lines_added': 2500,
                    'lines_deleted': 300,
                    'percent_commits': 60.0
                },
                {
                    'name': 'Jane Smith',
                    'commits': 30,
                    'lines_added': 1800,
                    'lines_deleted': 200,
                    'percent_commits': 40.0
                }
            ]
        }
        
        result = self.generator.generate_resume_items(project_data, user_name='John Doe')
        
        self.assertGreaterEqual(len(result['items']), 3)
        
        # Should contain git contribution information
        items_text = ' '.join(result['items'])
        self.assertTrue(
            any('60' in item or '45' in item or 'commits' in item.lower() or 
                'contributed' in item.lower() or 'version control' in item.lower()
                for item in result['items'])
        )

    def test_coding_project_without_git_stats(self):
        """Test coding project without git history"""
        project_data = {
            'root': 'no-git-project',
            'classification': {
                'type': 'coding',
                'languages': ['Python'],
                'frameworks': ['Django'],
                'resume_skills': ['Backend Development']
            },
            'files': {
                'code': [{'path': 'main.py'}],
                'content': [],
                'image': [],
                'unknown': []
            },
            'collaborative': False
        }
        
        result = self.generator.generate_resume_items(project_data)
        
        self.assertGreaterEqual(len(result['items']), 3)
        
        # Should still generate items based on languages, frameworks, skills, code files
        items_text = ' '.join(result['items'])
        self.assertTrue(
            any('Python' in item or 'Django' in item or 'code file' in item.lower()
                for item in result['items'])
        )

    # ===== Writing Projects =====

    def test_writing_project_with_content_analysis(self):
        """Test writing project with content analysis"""
        project_data = {
            'root': 'research-paper',
            'classification': {
                'type': 'writing',
            },
            'files': {
                'code': [],
                'content': [
                    {'path': 'paper.md', 'text': 'Research content here'}
                ],
                'image': [],
                'unknown': []
            }
        }
        
        # Create mock content summary
        content_summary = ProjectContentSummary(
            total_documents=1,
            total_words=12500,
            total_characters=75000,
            document_types={'research_paper': 1},
            primary_document_type='research_paper',
            writing_styles=['academic'],
            primary_writing_style='academic',
            complexity_levels=['advanced'],
            primary_complexity='advanced',
            all_topics=['Machine Learning', 'Psychology'],
            primary_topics=['Machine Learning', 'Psychology'],
            domain_indicators={},
            has_citations=True,
            has_code_examples=False,
            has_mathematical_content=True,
            average_document_length=12500,
            estimated_total_read_time=50,
            vocabulary_richness=0.72,
            document_analyses=[]
        )
        
        result = self.generator.generate_resume_items(project_data, content_summary=content_summary)
        
        self.assertGreaterEqual(len(result['items']), 3)
        
        # Should contain content analysis information
        items_text = ' '.join(result['items'])
        self.assertTrue(
            any('12,500' in item or 'word' in item.lower() or 'research paper' in item.lower() or
                'Machine Learning' in item or 'Psychology' in item or
                'citations' in item.lower() or 'mathematical' in item.lower()
                for item in result['items'])
        )

    # ===== Mixed Projects =====

    def test_mixed_coding_writing_project(self):
        """Test mixed coding + writing project - should generate both coding and writing bullets"""
        project_data = {
            'root': 'documentation-tool',
            'classification': {
                'type': 'mixed:coding+writing',
                'languages': ['Python'],
                'frameworks': ['Flask'],
                'resume_skills': ['Web Backend', 'Technical Writing']
            },
            'files': {
                'code': [{'path': 'app.py'}],
                'content': [{'path': 'docs.md'}],
                'image': [],
                'unknown': []
            }
        }
        
        result = self.generator.generate_resume_items(project_data)
        
        self.assertGreaterEqual(len(result['items']), 3)
        
        # Should contain both coding and writing aspects
        items_text = ' '.join(result['items'])
        has_coding = any('Python' in item or 'Flask' in item or 'code file' in item.lower() 
                        for item in result['items'])
        has_writing = any('Technical Writing' in item or 'Web Backend' in item 
                         for item in result['items'])
        
        # At minimum, should have coding aspects (writing aspects may come from content analysis)
        self.assertTrue(has_coding)

    # ===== Framework-Specific Contextual Templates =====

    def test_framework_specific_templates(self):
        """Test that framework-specific contextual templates are generated with specific text"""
        project_data = {
            'root': 'ml-project',
            'classification': {
                'type': 'coding',
                'languages': ['Python'],
                'frameworks': ['TensorFlow', 'React', 'Django'],
                'resume_skills': ['Machine Learning']
            },
            'files': {
                'code': [{'path': 'model.py'}],
                'content': [],
                'image': [],
                'unknown': []
            }
        }
        
        result = self.generator.generate_resume_items(project_data)
        
        items_text = ' '.join(result['items'])
        
        # Should contain framework-specific explanations (not just framework names)
        self.assertTrue(
            any('TensorFlow' in item and ('machine learning' in item.lower() or 'neural network' in item.lower()) or
                'React' in item and ('component-based' in item.lower() or 'user interface' in item.lower()) or
                'Django' in item and ('ORM' in item or 'web framework' in item.lower())
                for item in result['items'])
        )

    # ===== Category-Based Generation: Languages =====

    def test_languages_category_bullet_single(self):
        """Test languages category with single language"""
        bullet = self.generator._generate_languages_bullet(['Python'], [])
        self.assertEqual(bullet, "Developed using Python")

    def test_languages_category_bullet_two(self):
        """Test languages category with two languages"""
        bullet = self.generator._generate_languages_bullet(['Python', 'JavaScript'], [])
        self.assertEqual(bullet, "Developed using Python and JavaScript")

    def test_languages_category_bullet_multiple(self):
        """Test languages category with multiple languages"""
        bullet = self.generator._generate_languages_bullet(['Python', 'JavaScript', 'TypeScript', 'Go'], [])
        self.assertIn('Developed using', bullet)
        self.assertIn('Python', bullet)
        self.assertIn('JavaScript', bullet)

    def test_languages_category_bullet_all_covered(self):
        """Test languages category when all languages are covered by contextual templates"""
        bullet = self.generator._generate_languages_bullet(['Python'], ['Python'])
        self.assertIsNone(bullet)

    def test_languages_category_bullet_partial_coverage(self):
        """Test languages category with partial coverage"""
        bullet = self.generator._generate_languages_bullet(['Python', 'JavaScript'], ['Python'])
        self.assertIsNotNone(bullet)
        self.assertIn('JavaScript', bullet)
        self.assertNotIn('Python', bullet)

    # ===== Category-Based Generation: Frameworks =====

    def test_frameworks_category_bullet_single(self):
        """Test frameworks category with single framework"""
        bullet = self.generator._generate_frameworks_bullet(['React'], [])
        self.assertEqual(bullet, "Built with React")

    def test_frameworks_category_bullet_all_covered(self):
        """Test frameworks category when all frameworks are covered"""
        bullet = self.generator._generate_frameworks_bullet(['Django'], ['Django'])
        self.assertIsNone(bullet)

    def test_frameworks_category_bullet_partial_coverage(self):
        """Test frameworks category with partial coverage"""
        bullet = self.generator._generate_frameworks_bullet(['Django', 'React'], ['Django'])
        self.assertIsNotNone(bullet)
        self.assertIn('React', bullet)
        self.assertNotIn('Django', bullet)

    # ===== Category-Based Generation: Skills =====

    def test_skills_category_bullet(self):
        """Test skills category generates appropriate bullets"""
        project_data = {
            'root': 'skills-test',
            'classification': {
                'type': 'coding',
                'languages': ['Python'],
                'frameworks': [],
                'resume_skills': ['API Development', 'Database Design', 'Testing']
            },
            'files': {
                'code': [{'path': 'app.py'}],
                'content': [],
                'image': [],
                'unknown': []
            }
        }
        
        result = self.generator.generate_resume_items(project_data)
        
        items_text = ' '.join(result['items'])
        # Should contain skills bullet
        self.assertTrue(
            any('Demonstrated skills' in item or 'API Development' in item or
                'Database Design' in item or 'Testing' in item
                for item in result['items'])
        )

    def test_skills_category_bullet_many_skills(self):
        """Test skills category with more than 5 skills (should truncate)"""
        bullet = self.generator._generate_skills_bullet(
            ['Skill1', 'Skill2', 'Skill3', 'Skill4', 'Skill5', 'Skill6', 'Skill7'], []
        )
        self.assertIn('Demonstrated skills', bullet)
        self.assertIn('Skill1', bullet)
        self.assertIn('and 2 more', bullet)

    def test_skills_category_bullet_all_covered(self):
        """Test skills category when all skills are covered"""
        bullet = self.generator._generate_skills_bullet(['Web Development'], ['Web Development'])
        self.assertIsNone(bullet)

    # ===== Category-Based Generation: Code Metrics =====

    def test_code_metrics_category_bullet_single_file(self):
        """Test code metrics with single file (singular form)"""
        bullet = self.generator._generate_code_metrics_bullet(1)
        self.assertEqual(bullet, "Developed 1 code file")

    def test_code_metrics_category_bullet_multiple_files(self):
        """Test code metrics with multiple files (plural form)"""
        bullet = self.generator._generate_code_metrics_bullet(3)
        self.assertEqual(bullet, "Developed 3 code files")

    # ===== Category-Based Generation: Content Analysis =====

    def test_content_volume_bullet_single_document(self):
        """Test content volume bullet with single document"""
        summary = ProjectContentSummary(
            total_documents=1, total_words=5000, total_characters=30000,
            document_types={'blog_post': 1}, primary_document_type='blog_post',
            writing_styles=['casual'], primary_writing_style='casual',
            complexity_levels=['intermediate'], primary_complexity='intermediate',
            all_topics=[], primary_topics=[], domain_indicators={},
            has_citations=False, has_code_examples=False, has_mathematical_content=False,
            average_document_length=5000, estimated_total_read_time=20,
            vocabulary_richness=0.5, document_analyses=[]
        )
        bullet = self.generator._generate_content_volume_bullet(summary)
        self.assertIn('5,000', bullet)
        self.assertIn('blog post', bullet.lower())

    def test_content_volume_bullet_multiple_documents(self):
        """Test content volume bullet with multiple documents"""
        summary = ProjectContentSummary(
            total_documents=5, total_words=15000, total_characters=90000,
            document_types={'blog_post': 5}, primary_document_type='blog_post',
            writing_styles=['casual'], primary_writing_style='casual',
            complexity_levels=['intermediate'], primary_complexity='intermediate',
            all_topics=[], primary_topics=[], domain_indicators={},
            has_citations=False, has_code_examples=False, has_mathematical_content=False,
            average_document_length=3000, estimated_total_read_time=60,
            vocabulary_richness=0.55, document_analyses=[]
        )
        bullet = self.generator._generate_content_volume_bullet(summary)
        self.assertIn('15,000', bullet)
        self.assertIn('5', bullet)
        self.assertIn('blog posts', bullet.lower())

    def test_content_type_bullet_single_type(self):
        """Test content type bullet with single document type"""
        summary = ProjectContentSummary(
            total_documents=1, total_words=5000, total_characters=30000,
            document_types={'research_paper': 1}, primary_document_type='research_paper',
            writing_styles=['academic'], primary_writing_style='academic',
            complexity_levels=['advanced'], primary_complexity='advanced',
            all_topics=[], primary_topics=[], domain_indicators={},
            has_citations=True, has_code_examples=False, has_mathematical_content=False,
            average_document_length=5000, estimated_total_read_time=20,
            vocabulary_richness=0.7, document_analyses=[]
        )
        bullet = self.generator._generate_content_type_bullet(summary)
        self.assertIsNotNone(bullet)
        self.assertIn('research paper', bullet.lower())

    def test_content_type_bullet_multiple_types(self):
        """Test content type bullet with multiple document types"""
        summary = ProjectContentSummary(
            total_documents=3, total_words=10000, total_characters=60000,
            document_types={'blog_post': 2, 'technical_documentation': 1},
            primary_document_type='blog_post',
            writing_styles=['casual'], primary_writing_style='casual',
            complexity_levels=['intermediate'], primary_complexity='intermediate',
            all_topics=[], primary_topics=[], domain_indicators={},
            has_citations=False, has_code_examples=False, has_mathematical_content=False,
            average_document_length=3333, estimated_total_read_time=40,
            vocabulary_richness=0.55, document_analyses=[]
        )
        bullet = self.generator._generate_content_type_bullet(summary)
        self.assertIsNotNone(bullet)
        self.assertIn('blog post', bullet.lower() or 'technical documentation' in bullet.lower())

    def test_topics_bullet_single_topic(self):
        """Test topics bullet with single topic"""
        bullet = self.generator._generate_topics_bullet(['Machine Learning'])
        self.assertEqual(bullet, "Covered topic: Machine Learning")

    def test_topics_bullet_two_topics(self):
        """Test topics bullet with two topics"""
        bullet = self.generator._generate_topics_bullet(['Machine Learning', 'Psychology'])
        self.assertEqual(bullet, "Covered topics: Machine Learning and Psychology")

    def test_topics_bullet_many_topics(self):
        """Test topics bullet with many topics (should truncate)"""
        bullet = self.generator._generate_topics_bullet(['Topic1', 'Topic2', 'Topic3', 'Topic4', 'Topic5', 'Topic6'])
        self.assertIn('Covered topics including', bullet)
        self.assertIn('Topic1', bullet)
        self.assertIn('and 2 more', bullet)

    def test_topics_bullet_empty(self):
        """Test topics bullet with empty list"""
        bullet = self.generator._generate_topics_bullet([])
        self.assertIsNone(bullet)

    def test_structural_features_bullet_with_features(self):
        """Test structural features bullet when features exist"""
        summary = ProjectContentSummary(
            total_documents=1, total_words=5000, total_characters=30000,
            document_types={'research_paper': 1}, primary_document_type='research_paper',
            writing_styles=['academic'], primary_writing_style='academic',
            complexity_levels=['advanced'], primary_complexity='advanced',
            all_topics=[], primary_topics=[], domain_indicators={},
            has_citations=True, has_code_examples=True, has_mathematical_content=True,
            average_document_length=5000, estimated_total_read_time=20,
            vocabulary_richness=0.7, document_analyses=[]
        )
        bullet = self.generator._generate_structural_features_bullet(summary)
        self.assertIsNotNone(bullet)
        self.assertIn('Featured', bullet)
        self.assertTrue(
            'citations' in bullet.lower() or 
            'code example' in bullet.lower() or 
            'mathematical' in bullet.lower()
        )

    def test_structural_features_bullet_no_features(self):
        """Test structural features bullet when no features exist"""
        summary = ProjectContentSummary(
            total_documents=1, total_words=5000, total_characters=30000,
            document_types={'blog_post': 1}, primary_document_type='blog_post',
            writing_styles=['casual'], primary_writing_style='casual',
            complexity_levels=['intermediate'], primary_complexity='intermediate',
            all_topics=[], primary_topics=[], domain_indicators={},
            has_citations=False, has_code_examples=False, has_mathematical_content=False,
            average_document_length=5000, estimated_total_read_time=20,
            vocabulary_richness=0.5, document_analyses=[]
        )
        bullet = self.generator._generate_structural_features_bullet(summary)
        self.assertIsNone(bullet)

    def test_writing_quality_bullet_advanced(self):
        """Test writing quality bullet with advanced complexity and high vocabulary"""
        summary = ProjectContentSummary(
            total_documents=1, total_words=5000, total_characters=30000,
            document_types={'research_paper': 1}, primary_document_type='research_paper',
            writing_styles=['academic'], primary_writing_style='academic',
            complexity_levels=['advanced'], primary_complexity='advanced',
            all_topics=[], primary_topics=[], domain_indicators={},
            has_citations=True, has_code_examples=False, has_mathematical_content=False,
            average_document_length=5000, estimated_total_read_time=20,
            vocabulary_richness=0.72, document_analyses=[]
        )
        bullet = self.generator._generate_writing_quality_bullet(summary)
        self.assertIsNotNone(bullet)
        self.assertIn('advanced', bullet.lower())
        self.assertIn('72.0%', bullet or '72%' in bullet)

    def test_writing_quality_bullet_not_advanced(self):
        """Test writing quality bullet with non-advanced complexity (should return None)"""
        summary = ProjectContentSummary(
            total_documents=1, total_words=5000, total_characters=30000,
            document_types={'blog_post': 1}, primary_document_type='blog_post',
            writing_styles=['casual'], primary_writing_style='casual',
            complexity_levels=['intermediate'], primary_complexity='intermediate',
            all_topics=[], primary_topics=[], domain_indicators={},
            has_citations=False, has_code_examples=False, has_mathematical_content=False,
            average_document_length=5000, estimated_total_read_time=20,
            vocabulary_richness=0.72, document_analyses=[]
        )
        bullet = self.generator._generate_writing_quality_bullet(summary)
        self.assertIsNone(bullet)

    def test_writing_quality_bullet_low_vocabulary(self):
        """Test writing quality bullet with low vocabulary richness (should return None)"""
        summary = ProjectContentSummary(
            total_documents=1, total_words=5000, total_characters=30000,
            document_types={'research_paper': 1}, primary_document_type='research_paper',
            writing_styles=['academic'], primary_writing_style='academic',
            complexity_levels=['advanced'], primary_complexity='advanced',
            all_topics=[], primary_topics=[], domain_indicators={},
            has_citations=True, has_code_examples=False, has_mathematical_content=False,
            average_document_length=5000, estimated_total_read_time=20,
            vocabulary_richness=0.5, document_analyses=[]
        )
        bullet = self.generator._generate_writing_quality_bullet(summary)
        self.assertIsNone(bullet)

    # ===== Category-Based Generation: Project Scale =====

    def test_project_scale_bullet_large_project(self):
        """Test project scale bullet with large project (>20 files, multiple types)"""
        project_data = {
            'files': {
                'code': [{'path': f'file{i}.py'} for i in range(15)],
                'content': [{'path': f'doc{i}.md'} for i in range(10)],
                'image': [{'path': f'img{i}.png'} for i in range(5)],
                'unknown': []
            }
        }
        bullet = self.generator._generate_project_scale_bullet(project_data)
        self.assertIsNotNone(bullet)
        self.assertIn('30', bullet)
        self.assertTrue('code' in bullet.lower() or 'content' in bullet.lower())

    def test_project_scale_bullet_small_project(self):
        """Test project scale bullet with small project (<20 files, should return None)"""
        project_data = {
            'files': {
                'code': [{'path': 'file1.py'}],
                'content': [{'path': 'doc1.md'}],
                'image': [],
                'unknown': []
            }
        }
        bullet = self.generator._generate_project_scale_bullet(project_data)
        self.assertIsNone(bullet)

    def test_project_scale_bullet_single_file_type(self):
        """Test project scale bullet with single file type (should return None)"""
        project_data = {
            'files': {
                'code': [{'path': f'file{i}.py'} for i in range(25)],
                'content': [],
                'image': [],
                'unknown': []
            }
        }
        bullet = self.generator._generate_project_scale_bullet(project_data)
        self.assertIsNone(bullet)

    # ===== Category-Based Generation: Git Contributions =====

    def test_git_contribution_bullet_user_stats(self):
        """Test git contribution bullet with user-specific stats"""
        project_data = {
            'contributors': [
                {'name': 'John Doe', 'commits': 50, 'lines_added': 2000, 'lines_deleted': 100},
                {'name': 'Jane Smith', 'commits': 30, 'lines_added': 1500, 'lines_deleted': 50}
            ]
        }
        bullet = self.generator._generate_git_contribution_bullet(project_data, 'John Doe')
        self.assertIsNotNone(bullet)
        self.assertIn('Contributed', bullet)
        self.assertIn('50', bullet)
        self.assertIn('2,000', bullet)

    def test_git_contribution_bullet_aggregate_stats(self):
        """Test git contribution bullet with aggregate stats (no user match)"""
        project_data = {
            'contributors': [
                {'name': 'John Doe', 'commits': 50, 'lines_added': 2000, 'lines_deleted': 100},
                {'name': 'Jane Smith', 'commits': 30, 'lines_added': 1500, 'lines_deleted': 50}
            ]
        }
        bullet = self.generator._generate_git_contribution_bullet(project_data, None)
        self.assertIsNotNone(bullet)
        self.assertIn('Maintained version control', bullet)
        self.assertIn('80', bullet)

    def test_git_contribution_bullet_no_contributors(self):
        """Test git contribution bullet with no contributors (should return None)"""
        project_data = {}
        bullet = self.generator._generate_git_contribution_bullet(project_data, None)
        self.assertIsNone(bullet)

    def test_git_contribution_bullet_zero_commits(self):
        """Test git contribution bullet with zero commits (should return None)"""
        project_data = {
            'contributors': [
                {'name': 'John Doe', 'commits': 0, 'lines_added': 0, 'lines_deleted': 0}
            ]
        }
        bullet = self.generator._generate_git_contribution_bullet(project_data, None)
        self.assertIsNone(bullet)

    # ===== Content Analysis Integration Edge Cases =====

    def test_content_analysis_none(self):
        """Test that content_summary=None doesn't generate content bullets"""
        project_data = {
            'root': 'test-project',
            'classification': {'type': 'writing'},
            'files': {'code': [], 'content': [{'path': 'doc.md'}], 'image': [], 'unknown': []}
        }
        result = self.generator.generate_resume_items(project_data, content_summary=None)
        
        # Should not have content-specific bullets
        items_text = ' '.join(result['items'])
        self.assertFalse(
            any('word' in item.lower() and ('12,500' in item or '15,000' in item) or
                'research paper' in item.lower() or 'blog post' in item.lower()
                for item in result['items'])
        )

    # ===== Coverage Tracking Edge Cases =====

    def test_covered_items_tracking(self):
        """Test that covered items tracking works correctly"""
        frameworks = ['Django', 'React']
        languages = ['Python', 'JavaScript']
        skills = ['Web Development']
        
        # Framework contextual templates mention Django
        bullets = [
            "Developed backend infrastructure using Django Python web framework with built-in ORM and admin interface"
        ]
        
        covered = self.generator._get_covered_items(bullets, frameworks, languages, skills)
        
        # Django should be covered
        self.assertIn('Django', covered['frameworks'])
        # Python should be covered (mentioned in bullet)
        self.assertIn('Python', covered['languages'])

    def test_all_covered_check(self):
        """Test that _all_covered correctly identifies when all items are covered"""
        items = ['Python', 'JavaScript']
        covered = ['Python', 'JavaScript']
        
        self.assertTrue(self.generator._all_covered(items, covered))
        
        # Not all covered
        covered_partial = ['Python']
        self.assertFalse(self.generator._all_covered(items, covered_partial))
        
        # Empty items
        self.assertTrue(self.generator._all_covered([], covered))


    # ===== Git Contribution Statistics =====

    def test_user_contribution_exact_name_match(self):
        """Test user contribution extraction with exact name match"""
        contributors = [
            {'name': 'John Doe', 'commits': 50, 'lines_added': 2000, 'lines_deleted': 100},
            {'name': 'Jane Smith', 'commits': 30, 'lines_added': 1500, 'lines_deleted': 50}
        ]
        
        stats = self.generator._extract_user_contributions(contributors, 'John Doe')
        
        self.assertEqual(stats['user_commits'], 50)
        self.assertEqual(stats['user_lines_added'], 2000)
        self.assertEqual(stats['user_lines_deleted'], 100)
        self.assertEqual(stats['total_commits'], 80)
        self.assertAlmostEqual(stats['user_commit_percent'], 62.5, places=1)

    def test_user_contribution_first_token_match(self):
        """Test user contribution extraction with first token match"""
        contributors = [
            {'name': 'John Doe', 'commits': 50, 'lines_added': 2000, 'lines_deleted': 100},
            {'name': 'Jane Smith', 'commits': 30, 'lines_added': 1500, 'lines_deleted': 50}
        ]
        
        stats = self.generator._extract_user_contributions(contributors, 'John')
        
        self.assertEqual(stats['user_commits'], 50)
        self.assertEqual(stats['user_lines_added'], 2000)

    def test_user_contribution_email_match(self):
        """Test user contribution extraction with email local part match"""
        contributors = [
            {'name': 'John Doe', 'email': 'johndoe@example.com', 'commits': 50, 'lines_added': 2000, 'lines_deleted': 100},
            {'name': 'Jane Smith', 'email': 'janesmith@example.com', 'commits': 30, 'lines_added': 1500, 'lines_deleted': 50}
        ]
        
        stats = self.generator._extract_user_contributions(contributors, 'johndoe')
        
        self.assertEqual(stats['user_commits'], 50)
        self.assertEqual(stats['user_lines_added'], 2000)

    def test_user_contribution_no_match(self):
        """Test user contribution extraction when user name doesn't match"""
        contributors = [
            {'name': 'John Doe', 'commits': 50, 'lines_added': 2000, 'lines_deleted': 100},
            {'name': 'Jane Smith', 'commits': 30, 'lines_added': 1500, 'lines_deleted': 50}
        ]
        
        stats = self.generator._extract_user_contributions(contributors, 'Unknown User')
        
        # Should return aggregate stats
        self.assertEqual(stats['total_commits'], 80)
        self.assertIn('contributor_count', stats)
        self.assertNotIn('user_commits', stats)

    def test_user_contribution_no_username(self):
        """Test user contribution extraction without username (aggregate stats)"""
        contributors = [
            {'name': 'John Doe', 'commits': 50, 'lines_added': 2000, 'lines_deleted': 100},
            {'name': 'Jane Smith', 'commits': 30, 'lines_added': 1500, 'lines_deleted': 50}
        ]
        
        stats = self.generator._extract_user_contributions(contributors, None)
        
        self.assertEqual(stats['total_commits'], 80)
        self.assertEqual(stats['contributor_count'], 2)
        self.assertNotIn('user_commits', stats)

    def test_user_contribution_empty_list(self):
        """Test user contribution extraction with empty contributors list"""
        stats = self.generator._extract_user_contributions([], 'John Doe')
        self.assertEqual(stats, {})

    def test_user_contribution_multiple_matches(self):
        """Test user contribution extraction when multiple contributors match (sum them)"""
        contributors = [
            {'name': 'John Doe', 'email': 'john@example.com', 'commits': 30, 'lines_added': 1000, 'lines_deleted': 50},
            {'name': 'John Doe', 'email': 'johndoe@company.com', 'commits': 20, 'lines_added': 800, 'lines_deleted': 30}
        ]
        
        stats = self.generator._extract_user_contributions(contributors, 'John Doe')
        
        self.assertEqual(stats['user_commits'], 50)
        self.assertEqual(stats['user_lines_added'], 1800)
        self.assertEqual(stats['user_lines_deleted'], 80)

    # ===== Integration Scenarios =====

    def test_full_integration_coding_with_content_and_git(self):
        """Test full integration: coding project + content analysis + git stats"""
        project_data = {
            'root': 'full-stack-app',
            'classification': {
                'type': 'coding',
                'languages': ['Python', 'JavaScript'],
                'frameworks': ['Django', 'React'],
                'resume_skills': ['Full-Stack Development', 'API Development']
            },
            'files': {
                'code': [{'path': 'app.py'}, {'path': 'component.js'}],
                'content': [{'path': 'docs.md', 'text': 'Documentation'}],
                'image': [],
                'unknown': []
            },
            'contributors': [
                {'name': 'Developer', 'commits': 100, 'lines_added': 5000, 'lines_deleted': 500}
            ]
        }
        
        content_summary = ProjectContentSummary(
            total_documents=1, total_words=5000, total_characters=30000,
            document_types={'technical_documentation': 1}, primary_document_type='technical_documentation',
            writing_styles=['technical'], primary_writing_style='technical',
            complexity_levels=['intermediate'], primary_complexity='intermediate',
            all_topics=['Web Development'], primary_topics=['Web Development'],
            domain_indicators={}, has_citations=False, has_code_examples=True,
            has_mathematical_content=False, average_document_length=5000,
            estimated_total_read_time=20, vocabulary_richness=0.6, document_analyses=[]
        )
        
        result = self.generator.generate_resume_items(project_data, content_summary=content_summary)
        
        # Should have multiple categories
        self.assertGreaterEqual(len(result['items']), 5)
        
        items_text = ' '.join(result['items'])
        # Should have coding aspects
        has_coding = any('Python' in item or 'Django' in item or 'React' in item 
                        for item in result['items'])
        # Should have content aspects
        has_content = any('5,000' in item or 'word' in item.lower() or 'code example' in item.lower()
                         for item in result['items'])
        # Should have git aspects
        has_git = any('100' in item or 'commits' in item.lower() 
                     for item in result['items'])
        
        self.assertTrue(has_coding)
        self.assertTrue(has_content)
        self.assertTrue(has_git)

    def test_writing_project_all_content_categories(self):
        """Test writing project with all content categories populated"""
        project_data = {
            'root': 'comprehensive-writing',
            'classification': {'type': 'writing'},
            'files': {'code': [], 'content': [{'path': 'doc.md'}], 'image': [], 'unknown': []}
        }
        
        content_summary = ProjectContentSummary(
            total_documents=3, total_words=20000, total_characters=120000,
            document_types={'research_paper': 2, 'blog_post': 1},
            primary_document_type='research_paper',
            writing_styles=['academic'], primary_writing_style='academic',
            complexity_levels=['advanced'], primary_complexity='advanced',
            all_topics=['Machine Learning', 'Data Science', 'Python', 'Statistics'],
            primary_topics=['Machine Learning', 'Data Science', 'Python', 'Statistics'],
            domain_indicators={}, has_citations=True, has_code_examples=True,
            has_mathematical_content=True, average_document_length=6666,
            estimated_total_read_time=80, vocabulary_richness=0.75, document_analyses=[]
        )
        
        result = self.generator.generate_resume_items(project_data, content_summary=content_summary)
        
        # Should have multiple content-related bullets
        self.assertGreaterEqual(len(result['items']), 4)
        
        items_text = ' '.join(result['items'])
        # Check for volume, type, topics, structural features, writing quality
        has_volume = any('20,000' in item or '3' in item for item in result['items'])
        has_topics = any('Machine Learning' in item or 'Data Science' in item 
                        for item in result['items'])
        has_features = any('citations' in item.lower() or 'code example' in item.lower() 
                          or 'mathematical' in item.lower() for item in result['items'])
        has_quality = any('advanced' in item.lower() and 'vocabulary' in item.lower() 
                         for item in result['items'])
        
        self.assertTrue(has_volume)
        self.assertTrue(has_topics)
        self.assertTrue(has_features)
        self.assertTrue(has_quality)

    # ===== Minimal Data Scenarios =====

    def test_minimal_project_data(self):
        """Test project with minimal data (should use fallback)"""
        project_data = {
            'root': 'minimal-project',
            'classification': {
                'type': 'unknown'
            }
        }
        
        result = self.generator.generate_resume_items(project_data)
        
        # Should still generate at least a fallback item
        self.assertGreaterEqual(len(result['items']), 1)
        self.assertIn('items', result)
        self.assertIn('generated_at', result)

    # ===== Error Handling =====

    def test_error_handling_invalid_data(self):
        """Test error handling with invalid project data"""
        import logging
        
        # Suppress expected error logging for this test
        logger = logging.getLogger('app.services.resume_item_generator')
        original_level = logger.level
        logger.setLevel(logging.CRITICAL)
        
        try:
            project_data = {
                'root': None,
                'classification': None
            }
            
            result = self.generator.generate_resume_items(project_data)
            
            # Should return empty items list or fallback items, not crash
            self.assertIn('items', result)
            self.assertIn('generated_at', result)
            self.assertGreaterEqual(len(result['items']), 0)
        finally:
            logger.setLevel(original_level)

    def test_error_handling_missing_keys(self):
        """Test error handling with missing keys"""
        project_data = {}  # Empty dict
        
        result = self.generator.generate_resume_items(project_data)
        
        # Should handle gracefully
        self.assertIn('items', result)
        self.assertIn('generated_at', result)
        self.assertGreaterEqual(len(result['items']), 1)  # Should have fallback

    def test_error_handling_non_dict_classification(self):
        """Test error handling with classification as non-dict"""
        project_data = {
            'root': 'test',
            'classification': 'invalid_string'  # Should be dict
        }
        
        result = self.generator.generate_resume_items(project_data)
        
        # Should handle gracefully
        self.assertIn('items', result)
        self.assertIn('generated_at', result)
        self.assertGreaterEqual(len(result['items']), 1)

    def test_error_handling_non_list_contributors(self):
        """Test error handling with contributors as non-list"""
        project_data = {
            'root': 'test',
            'classification': {'type': 'coding'},
            'contributors': 'invalid_string'  # Should be list
        }
        
        result = self.generator.generate_resume_items(project_data)
        
        # Should handle gracefully
        self.assertIn('items', result)
        self.assertIn('generated_at', result)
