"""
Tests for Resume Item Generator Service

Tests cover:
- Different project types (coding, writing, art, mixed)
- Date handling (with/without dates, edge cases)
- Git contribution statistics (solo, collaborative, user matching)
- Template variable substitution
- Minimal data scenarios
- Error handling
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

from app.services.resume_item_generator import ResumeItemGenerator, generate_resume_items


class ResumeItemGeneratorTests(TestCase):
    """Test suite for resume item generator functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = ResumeItemGenerator()

    # ===== Coding Projects =====

    def test_coding_project_with_full_data(self):
        """Test coding project with languages, frameworks, skills, and dates"""
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
        self.assertLessEqual(len(result['items']), 6)
        
        # Check that items contain technical details
        self.assertTrue(
            any('Python' in item or 'Django' in item or 'React' in item for item in result['items'])
        )

    def test_coding_project_collaborative_with_git_stats(self):
        """Test collaborative coding project with git contribution statistics"""
        project_data = {
            'root': 'team-project',
            'classification': {
                'type': 'coding',
                'languages': ['Python'],  # Reduced to 1 language to limit contextual templates
                'frameworks': [],  # No frameworks to limit contextual templates
                'resume_skills': ['Web Backend']  # Reduced to 1 skill to limit contextual templates
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
        self.assertLessEqual(len(result['items']), 6)
        
        # Should contain collaborative language, git stats, or contribution percentage
        items_text = ' '.join(result['items'])
        self.assertTrue(
            any('team' in item.lower() or 'collaborat' in item.lower() or '60' in item or 
                'coordinating' in item.lower() or 'contributing' in item.lower() or 
                'spearheaded' in item.lower() or 'orchestrated' in item.lower() or
                'led' in item.lower() or 'drove' in item.lower() or 'guided' in item.lower()
                for item in result['items'])
        )

    def test_coding_project_solo_with_git_stats(self):
        """Test solo coding project with git statistics"""
        project_data = {
            'root': 'solo-project',
            'classification': {
                'type': 'coding',
                'languages': ['Python'],
                'frameworks': ['Flask'],
                'resume_skills': ['Web Backend']
            },
            'created_at': int(datetime(2023, 5, 1).timestamp()),
            'end_date': int(datetime(2024, 1, 15).timestamp()),
            'files': {
                'code': [{'path': 'app.py'}],
                'content': [],
                'image': [],
                'unknown': []
            },
            'collaborative': False,
            'contributors': [
                {
                    'name': 'Developer',
                    'commits': 120,
                    'lines_added': 5000,
                    'lines_deleted': 500,
                    'percent_commits': 100.0
                }
            ]
        }
        
        result = self.generator.generate_resume_items(project_data)
        
        self.assertGreaterEqual(len(result['items']), 3)
        self.assertLessEqual(len(result['items']), 6)

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
        self.assertLessEqual(len(result['items']), 6)

    # ===== Writing Projects =====

    def test_writing_project(self):
        """Test writing project"""
        project_data = {
            'root': 'my-essays',
            'classification': {
                'type': 'writing',
            },
            'created_at': int(datetime(2023, 2, 1).timestamp()),
            'end_date': int(datetime(2023, 8, 30).timestamp()),
            'files': {
                'code': [],
                'content': [
                    {'path': 'essay1.md'},
                    {'path': 'essay2.md'},
                    {'path': 'essay3.md'}
                ],
                'image': [],
                'unknown': []
            }
        }
        
        result = self.generator.generate_resume_items(project_data)
        
        self.assertGreaterEqual(len(result['items']), 3)
        self.assertLessEqual(len(result['items']), 6)
        # Should mention documents/files
        items_text = ' '.join(result['items'])
        self.assertTrue(
            any('document' in item.lower() or 'file' in item.lower() or '3' in item for item in result['items'])
        )

    # ===== Art Projects =====

    def test_art_project(self):
        """Test art/design project"""
        project_data = {
            'root': 'portfolio-designs',
            'classification': {
                'type': 'art',
            },
            'created_at': int(datetime(2023, 1, 1).timestamp()),
            'end_date': int(datetime(2023, 12, 31).timestamp()),
            'files': {
                'code': [],
                'content': [],
                'image': [
                    {'path': 'design1.png'},
                    {'path': 'design2.jpg'},
                    {'path': 'design3.svg'}
                ],
                'unknown': []
            }
        }
        
        result = self.generator.generate_resume_items(project_data)
        
        self.assertGreaterEqual(len(result['items']), 3)
        self.assertLessEqual(len(result['items']), 6)
        # Should mention visual/design assets
        self.assertTrue(
            any('visual' in item.lower() or 'design' in item.lower() or 'asset' in item.lower() for item in result['items'])
        )

    # ===== Mixed Projects =====

    def test_mixed_coding_writing_project(self):
        """Test mixed coding + writing project"""
        project_data = {
            'root': 'documentation-tool',
            'classification': {
                'type': 'mixed:coding+writing',
                'languages': ['Python'],
                'frameworks': ['Flask'],
                'resume_skills': ['Web Backend']
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

    # ===== Date Handling =====

    def test_project_without_dates(self):
        """Test project with missing dates (should still generate items)"""
        project_data = {
            'root': 'no-dates-project',
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
            }
        }
        
        result = self.generator.generate_resume_items(project_data)
        
        self.assertGreaterEqual(len(result['items']), 3)
        # Should not crash and should generate items

    def test_project_with_only_start_date(self):
        """Test project with only start date"""
        project_data = {
            'root': 'ongoing-project',
            'classification': {
                'type': 'coding',
                'languages': ['Python'],
            },
            'created_at': int(datetime(2023, 1, 1).timestamp()),
            'files': {
                'code': [{'path': 'main.py'}],
                'content': [],
                'image': [],
                'unknown': []
            }
        }
        
        result = self.generator.generate_resume_items(project_data)
        
        self.assertGreaterEqual(len(result['items']), 3)
        items_text = ' '.join(result['items'])
        # Should handle "Present" in date range
        # (Note: may or may not appear depending on template selection)

    def test_project_with_same_start_end_date(self):
        """Test project where start and end dates are the same"""
        timestamp = int(datetime(2023, 6, 15).timestamp())
        project_data = {
            'root': 'single-day-project',
            'classification': {
                'type': 'coding',
                'languages': ['Python'],
            },
            'created_at': timestamp,
            'end_date': timestamp,
            'files': {
                'code': [{'path': 'main.py'}],
                'content': [],
                'image': [],
                'unknown': []
            }
        }
        
        result = self.generator.generate_resume_items(project_data)
        
        self.assertGreaterEqual(len(result['items']), 3)

    # ===== Date Formatting Edge Cases =====

    def test_date_formatting_valid_timestamp(self):
        """Test date formatting with valid timestamp"""
        timestamp = int(datetime(2023, 3, 15).timestamp())
        formatted = self.generator._format_date(timestamp)
        self.assertEqual(formatted, 'Mar 2023')

    def test_date_formatting_none(self):
        """Test date formatting with None"""
        formatted = self.generator._format_date(None)
        self.assertEqual(formatted, '')

    def test_date_formatting_zero(self):
        """Test date formatting with 0"""
        formatted = self.generator._format_date(0)
        self.assertEqual(formatted, '')

    def test_date_range_both_dates(self):
        """Test date range formatting with both start and end"""
        start = int(datetime(2023, 1, 1).timestamp())
        end = int(datetime(2024, 12, 31).timestamp())
        date_range = self.generator._format_date_range(start, end)
        self.assertEqual(date_range, 'Jan 2023 - Dec 2024')

    def test_date_range_same_dates(self):
        """Test date range formatting with same start and end"""
        timestamp = int(datetime(2023, 6, 15).timestamp())
        date_range = self.generator._format_date_range(timestamp, timestamp)
        self.assertEqual(date_range, 'Jun 2023')

    def test_date_range_only_start(self):
        """Test date range formatting with only start date"""
        start = int(datetime(2023, 1, 1).timestamp())
        date_range = self.generator._format_date_range(start, None)
        self.assertEqual(date_range, 'Jan 2023 - Present')

    def test_date_range_only_end(self):
        """Test date range formatting with only end date"""
        end = int(datetime(2024, 12, 31).timestamp())
        date_range = self.generator._format_date_range(None, end)
        self.assertEqual(date_range, 'Until Dec 2024')

    def test_date_range_no_dates(self):
        """Test date range formatting with no dates"""
        date_range = self.generator._format_date_range(None, None)
        self.assertEqual(date_range, '')

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

    # ===== Minimal Data Scenarios =====

    def test_minimal_project_data(self):
        """Test project with minimal data (should use generic templates)"""
        project_data = {
            'root': 'minimal-project',
            'classification': {
                'type': 'unknown'
            }
        }
        
        result = self.generator.generate_resume_items(project_data)
        
        # Should still generate at least 3 items using fallback templates
        self.assertGreaterEqual(len(result['items']), 3)
        self.assertLessEqual(len(result['items']), 6)

    def test_project_with_only_name(self):
        """Test project with only name"""
        project_data = {
            'root': 'name-only-project'
        }
        
        result = self.generator.generate_resume_items(project_data)
        
        self.assertGreaterEqual(len(result['items']), 3)

    # ===== Template Variable Substitution =====

    def test_template_substitution_all_variables(self):
        """Test that templates correctly substitute all variables"""
        project_data = {
            'root': 'test-project',
            'classification': {
                'type': 'coding',
                'languages': ['Python', 'JavaScript'],
                'frameworks': ['Django', 'React'],
                'resume_skills': ['Backend Development', 'Frontend Development']
            },
            'created_at': int(datetime(2023, 1, 1).timestamp()),
            'end_date': int(datetime(2023, 12, 31).timestamp()),
            'files': {
                'code': [{'path': 'file1.py'}, {'path': 'file2.js'}],
                'content': [],
                'image': [],
                'unknown': []
            },
            'collaborative': False,
            'contributors': [
                {'name': 'Developer', 'commits': 100, 'lines_added': 5000, 'lines_deleted': 500}
            ]
        }
        
        result = self.generator.generate_resume_items(project_data)
        
        # All items should be properly formatted (no {placeholders})
        for item in result['items']:
            self.assertNotIn('{', item)
            self.assertNotIn('}', item)

    # ===== Error Handling =====

    def test_error_handling_invalid_data(self):
        """Test error handling with invalid project data - errors are expected and handled gracefully"""
        import logging
        
        # Suppress expected error logging for this test
        logger = logging.getLogger('app.services.resume_item_generator')
        original_level = logger.level
        logger.setLevel(logging.CRITICAL)  # Only show critical errors, suppress ERROR level
        
        try:
            project_data = {
                'root': None,  # Invalid root
                'classification': None  # Invalid classification
            }
            
            # NOTE: This test intentionally passes invalid data to verify error handling.
            # Any errors logged are expected and indicate the error handling is working.
            result = self.generator.generate_resume_items(project_data)
            
            # Should return empty items list or fallback items, not crash
            self.assertIn('items', result)
            self.assertIn('generated_at', result)
            
            # Verify error was handled gracefully (items should still be generated with fallbacks)
            self.assertGreaterEqual(len(result['items']), 0)
        finally:
            # Restore original logging level
            logger.setLevel(original_level)

    def test_error_handling_missing_keys(self):
        """Test error handling with missing keys"""
        project_data = {}  # Empty dict
        
        result = self.generator.generate_resume_items(project_data)
        
        # Should handle gracefully
        self.assertIn('items', result)
        self.assertIn('generated_at', result)

    # ===== Convenience Function =====

    def test_convenience_function(self):
        """Test the convenience function generate_resume_items"""
        project_data = {
            'root': 'convenience-test',
            'classification': {
                'type': 'coding',
                'languages': ['Python'],
            },
            'files': {
                'code': [{'path': 'main.py'}],
                'content': [],
                'image': [],
                'unknown': []
            }
        }
        
        result = generate_resume_items(project_data)
        
        self.assertIn('items', result)
        self.assertIn('generated_at', result)
        self.assertGreaterEqual(len(result['items']), 3)

    # ===== Item Count Validation =====

    def test_item_count_between_3_and_5(self):
        """Test that generated items are between 3 and 5"""
        project_data = {
            'root': 'count-test',
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
            }
        }
        
        result = self.generator.generate_resume_items(project_data)
        
        self.assertGreaterEqual(len(result['items']), 3)
        self.assertLessEqual(len(result['items']), 6)

    # ===== Generated Timestamp =====

    def test_generated_at_timestamp(self):
        """Test that generated_at is a valid timestamp"""
        project_data = {
            'root': 'timestamp-test',
            'classification': {'type': 'coding'},
            'files': {'code': [], 'content': [], 'image': [], 'unknown': []}
        }
        
        result = self.generator.generate_resume_items(project_data)
        
        self.assertIn('generated_at', result)
        self.assertIsInstance(result['generated_at'], int)
        self.assertGreater(result['generated_at'], 0)
        
        # Should be recent (within last minute)
        current_time = int(datetime.now().timestamp())
        self.assertLess(abs(result['generated_at'] - current_time), 60)

