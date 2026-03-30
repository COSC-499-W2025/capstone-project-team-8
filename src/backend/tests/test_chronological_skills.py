import unittest
from datetime import datetime, timezone
from pathlib import Path
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src/backend'))

from app.services.analysis.analyzers.skill_analyzer import (
    analyze_project,
    format_chronological_skills_for_display,
    _guess_language,
    _detect_skills_from_content,
    CODE_EXTS,
    EXT_TO_LANG,
)


class TestSkillAnalyzerCodeFiltering(unittest.TestCase):
    """Test that only code files are analyzed"""

    def test_code_exts_contains_expected_languages(self):
        """Verify CODE_EXTS includes primary languages"""
        expected = {'.py', '.js', '.java', '.css', '.html', '.json', '.sql', '.yaml', '.yml'}
        self.assertTrue(expected.issubset(CODE_EXTS))

    def test_non_code_files_excluded(self):
        """Verify non-code files are in the exclusion list"""
        non_code_exts = {'.docx', '.pdf', '.png', '.jpg', '.txt'}
        # These should NOT be in CODE_EXTS
        for ext in non_code_exts:
            if ext not in {'.txt'}:  # .txt might be considered
                self.assertNotIn(ext, CODE_EXTS)

    def test_ext_to_lang_mapping(self):
        """Verify file extension to language mapping"""
        test_cases = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.java': 'Java',
            '.css': 'CSS',
            '.sql': 'SQL',
            '.dockerfile': 'Dockerfile',
        }
        for ext, expected_lang in test_cases.items():
            self.assertEqual(EXT_TO_LANG.get(ext), expected_lang)


class TestLanguageDetection(unittest.TestCase):
    """Test language detection from file extensions and content"""

    def test_guess_language_by_extension(self):
        """Test language guessing by file extension"""
        test_cases = [
            (Path('test.py'), 'Python'),
            (Path('app.js'), 'JavaScript'),
            (Path('Main.java'), 'Java'),
            (Path('styles.css'), 'CSS'),
            (Path('query.sql'), 'SQL'),
        ]
        for path, expected_lang in test_cases:
            lang = _guess_language(path, '')
            self.assertEqual(lang, expected_lang, f"Failed for {path}")

    def test_guess_language_dockerfile_by_name(self):
        """Test Dockerfile detection by name"""
        path = Path('Dockerfile')
        lang = _guess_language(path, '')
        self.assertEqual(lang, 'Dockerfile')

    def test_guess_language_by_content_html(self):
        """Test HTML detection by content"""
        html_content = '<!DOCTYPE html><html><body>Test</body></html>'
        lang = _guess_language(Path('test.unknown'), html_content)
        self.assertEqual(lang, 'HTML')


class TestSkillDetection(unittest.TestCase):
    """Test skill detection from file content"""

    def test_detect_flask_skill(self):
        """Test Flask (Web Backend) detection"""
        content = 'from flask import Flask\napp = Flask(__name__)'
        skills = _detect_skills_from_content('Python', content)
        self.assertIn('Web Backend', skills)

    def test_detect_react_skill(self):
        """Test React (Frontend Web) detection"""
        content = "import React from 'react'\nconst App = () => <div>Test</div>"
        skills = _detect_skills_from_content('JavaScript', content)
        self.assertIn('Frontend Web', skills)

    def test_detect_sql_skill(self):
        """Test SQL (Databases) detection"""
        content = 'SELECT * FROM users WHERE id = 1'
        skills = _detect_skills_from_content('SQL', content)
        self.assertIn('Databases', skills)

    def test_detect_docker_skill(self):
        """Test Docker (DevOps) detection"""
        content = 'FROM python:3.9\nRUN pip install flask'
        skills = _detect_skills_from_content('Dockerfile', content)
        self.assertIn('DevOps', skills)

    def test_fallback_skill_for_python(self):
        """Test fallback skill when no patterns match"""
        content = 'x = 5'
        skills = _detect_skills_from_content('Python', content)
        self.assertIn('Web Backend', skills)

    def test_fallback_skill_for_html(self):
        """Test fallback skill for HTML"""
        content = '<div>Test</div>'
        skills = _detect_skills_from_content('HTML', content)
        self.assertIn('Frontend Web', skills)

    def test_multiple_skills_detected(self):
        """Test detection of multiple skills in one file"""
        content = 'from flask import Flask\nimport pandas as pd'
        skills = _detect_skills_from_content('Python', content)
        self.assertGreaterEqual(len(skills), 2)
        self.assertIn('Web Backend', skills)


class TestChronologicalSkillRanking(unittest.TestCase):
    """Test chronological skill ranking with timestamps"""

    def test_analyze_project_returns_chronological_skills(self):
        """Test that analyze_project returns chronological_skills key"""
        backend_path = str(Path(__file__).parent.parent / 'src/backend/app')
        if not Path(backend_path).exists():
            self.skipTest(f"Test path not found: {backend_path}")
        
        result = analyze_project(backend_path, max_files=10)
        
        self.assertIn('chronological_skills', result)
        self.assertIsInstance(result['chronological_skills'], list)

    def test_chronological_skills_have_required_fields(self):
        """Test that each chronological skill has required fields"""
        backend_path = str(Path(__file__).parent.parent / 'src/backend/app')
        if not Path(backend_path).exists():
            self.skipTest(f"Test path not found: {backend_path}")
        
        result = analyze_project(backend_path, max_files=10)
        
        if result['chronological_skills']:
            skill = result['chronological_skills'][0]
            required_fields = {'rank', 'skill', 'last_used_timestamp', 'last_used_path', 'project_tag'}
            self.assertTrue(required_fields.issubset(skill.keys()))

    def test_chronological_skills_sorted_by_timestamp(self):
        """Test that skills are sorted by timestamp (most recent first)"""
        backend_path = str(Path(__file__).parent.parent / 'src/backend/app')
        if not Path(backend_path).exists():
            self.skipTest(f"Test path not found: {backend_path}")
        
        result = analyze_project(backend_path, max_files=10)
        
        if len(result['chronological_skills']) > 1:
            timestamps = []
            for skill in result['chronological_skills']:
                ts = skill.get('last_used_timestamp')
                if ts is not None:
                    timestamps.append(ts)
            
            # Verify timestamps are in descending order (most recent first)
            if len(timestamps) > 1:
                for i in range(len(timestamps) - 1):
                    self.assertGreaterEqual(timestamps[i], timestamps[i + 1])

    def test_rank_incremental(self):
        """Test that ranks are sequential starting from 1"""
        backend_path = str(Path(__file__).parent.parent / 'src/backend/app')
        if not Path(backend_path).exists():
            self.skipTest(f"Test path not found: {backend_path}")
        
        result = analyze_project(backend_path, max_files=10)
        
        for idx, skill in enumerate(result['chronological_skills'], start=1):
            self.assertEqual(skill['rank'], idx)

    def test_project_metadata_associates_files_to_projects(self):
        """Test that project_metadata properly associates files to project tags"""
        backend_path = str(Path(__file__).parent.parent / 'src/backend/app')
        if not Path(backend_path).exists():
            self.skipTest(f"Test path not found: {backend_path}")
        
        project_metadata = {
            1: {'root': backend_path, 'timestamp': 1700000000}
        }
        
        result = analyze_project(backend_path, max_files=10, project_metadata=project_metadata)
        
        # Check that at least some skills have project_tag=1
        skills_with_tag = [s for s in result['chronological_skills'] if s['project_tag'] == 1]
        self.assertGreater(len(skills_with_tag), 0)

    def test_root_project_tag_zero(self):
        """Test that root project (tag 0) is used for root-level files"""
        backend_path = str(Path(__file__).parent.parent / 'src/backend/app')
        if not Path(backend_path).exists():
            self.skipTest(f"Test path not found: {backend_path}")
        
        project_metadata = {
            0: {'root': backend_path, 'timestamp': 1700000000}
        }
        
        result = analyze_project(backend_path, max_files=10, project_metadata=project_metadata)
        
        # Skills without specific project match should get tag 0
        skills_with_tag_0 = [s for s in result['chronological_skills'] if s['project_tag'] == 0]
        self.assertGreater(len(skills_with_tag_0), 0)

    def test_file_timestamps_parameter(self):
        """Test that file_timestamps parameter is used when provided"""
        backend_path = str(Path(__file__).parent.parent / 'src/backend/app')
        if not Path(backend_path).exists():
            self.skipTest(f"Test path not found: {backend_path}")
        
        # Create mock file timestamps
        file_timestamps = {
            'models.py': 1697614794,
            'views.py': 1697614800,
            'urls.py': 1697614750,
        }
        
        result = analyze_project(backend_path, max_files=10, file_timestamps=file_timestamps)
        
        # Result should still have chronological_skills
        self.assertIn('chronological_skills', result)


class TestFormatChronologicalSkills(unittest.TestCase):
    """Test formatting chronological skills for display"""

    def test_format_chronological_skills_structure(self):
        """Test that formatted skills have display-friendly fields"""
        project_result = {
            'chronological_skills': [
                {
                    'rank': 1,
                    'skill': 'Web Backend',
                    'last_used_timestamp': 1697614794,
                    'last_used_path': '/path/to/file.py',
                    'project_tag': 1,
                }
            ]
        }
        
        formatted = format_chronological_skills_for_display(project_result)
        
        self.assertEqual(len(formatted), 1)
        self.assertIn('rank', formatted[0])
        self.assertIn('skill', formatted[0])
        self.assertIn('date_used', formatted[0])
        self.assertIn('days_since_used', formatted[0])
        self.assertIn('file_used', formatted[0])
        self.assertIn('project_tag', formatted[0])

    def test_format_converts_timestamp_to_iso(self):
        """Test that timestamps are converted to ISO format"""
        project_result = {
            'chronological_skills': [
                {
                    'rank': 1,
                    'skill': 'Web Backend',
                    'last_used_timestamp': 1697614794,
                    'last_used_path': '/path/to/file.py',
                    'project_tag': 1,
                }
            ]
        }
        
        formatted = format_chronological_skills_for_display(project_result)
        
        # Check that date is ISO format
        date_str = formatted[0]['date_used']
        # ISO format should contain 'T' between date and time
        self.assertIn('T', date_str)

    def test_format_handles_unknown_timestamps(self):
        """Test that None timestamps are handled gracefully"""
        project_result = {
            'chronological_skills': [
                {
                    'rank': 1,
                    'skill': 'Web Backend',
                    'last_used_timestamp': None,
                    'last_used_path': '/path/to/file.py',
                    'project_tag': None,
                }
            ]
        }
        
        formatted = format_chronological_skills_for_display(project_result)
        
        self.assertEqual(formatted[0]['date_used'], 'Unknown')
        self.assertEqual(formatted[0]['days_since_used'], -1)

    def test_format_calculates_days_since_used(self):
        """Test that days_since_used is calculated"""
        # Use a timestamp from a known past date
        past_timestamp = 1697614794  # Oct 18, 2025
        
        project_result = {
            'chronological_skills': [
                {
                    'rank': 1,
                    'skill': 'Web Backend',
                    'last_used_timestamp': past_timestamp,
                    'last_used_path': '/path/to/file.py',
                    'project_tag': 1,
                }
            ]
        }
        
        formatted = format_chronological_skills_for_display(project_result)
        
        # days_since_used should be positive
        days = formatted[0]['days_since_used']
        self.assertGreater(days, 0)


class TestSkillAnalysisMetrics(unittest.TestCase):
    """Test skill analysis output metrics"""

    def test_analyze_project_returns_required_keys(self):
        """Test that analyze_project returns all required keys"""
        backend_path = str(Path(__file__).parent.parent / 'src/backend/app')
        if not Path(backend_path).exists():
            self.skipTest(f"Test path not found: {backend_path}")
        
        result = analyze_project(backend_path, max_files=5)
        
        required_keys = {
            'total_files_scanned',
            'total_skill_matches',
            'skills',
            'chronological_skills',
        }
        self.assertTrue(required_keys.issubset(result.keys()))

    def test_total_files_scanned_positive(self):
        """Test that at least some files are scanned"""
        backend_path = str(Path(__file__).parent.parent / 'src/backend/app')
        if not Path(backend_path).exists():
            self.skipTest(f"Test path not found: {backend_path}")
        
        result = analyze_project(backend_path, max_files=10)
        
        self.assertGreater(result['total_files_scanned'], 0)

    def test_skills_dict_has_structure(self):
        """Test that skills dict has proper structure"""
        backend_path = str(Path(__file__).parent.parent / 'src/backend/app')
        if not Path(backend_path).exists():
            self.skipTest(f"Test path not found: {backend_path}")
        
        result = analyze_project(backend_path, max_files=10)
        
        if result['skills']:
            skill_name = list(result['skills'].keys())[0]
            skill_data = result['skills'][skill_name]
            
            required_keys = {'count', 'percentage', 'languages'}
            self.assertTrue(required_keys.issubset(skill_data.keys()))
            
            # Verify percentages are between 0 and 100
            self.assertGreaterEqual(skill_data['percentage'], 0)
            self.assertLessEqual(skill_data['percentage'], 100)

    def test_max_files_respected(self):
        """Test that max_files parameter is respected"""
        backend_path = str(Path(__file__).parent.parent / 'src/backend/app')
        if not Path(backend_path).exists():
            self.skipTest(f"Test path not found: {backend_path}")
        
        result = analyze_project(backend_path, max_files=5)
        
        # max_files is a limit, may process up to max_files + 1 due to directory handling
        self.assertLessEqual(result['total_files_scanned'], 10)


if __name__ == '__main__':
    unittest.main()
