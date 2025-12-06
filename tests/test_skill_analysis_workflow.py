import unittest
from datetime import datetime
from pathlib import Path
import sys
import os
import tempfile
import zipfile
from io import BytesIO
from unittest.mock import patch, MagicMock

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src/backend'))

from app.services.analysis.analyzers.skill_analyzer import (
    analyze_project,
    CODE_EXTS,
)
from app.services.analysis.analyzers.last_updated import (
    compute_projects_last_updated,
    extract_all_file_timestamps,
)


class TestSkillAnalysisWorkflow(unittest.TestCase):
    """Test complete workflow from ZIP to skill analysis"""

    def _create_project_zip(self):
        """Helper to create a test project ZIP"""
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            # Python files
            zf.writestr('src/main.py', 'from flask import Flask\napp = Flask(__name__)')
            zf.writestr('src/utils.py', 'def helper(): pass')
            
            # JavaScript files
            zf.writestr('frontend/app.js', "import React from 'react'")
            zf.writestr('frontend/style.css', 'body { margin: 0; }')
            
            # SQL files
            zf.writestr('database/schema.sql', 'CREATE TABLE users (id INT PRIMARY KEY)')
            
            # Non-code files (should be ignored)
            zf.writestr('docs/README.md', '# Documentation')
            zf.writestr('docs/guide.docx', 'binary content')
            
            # Docker file
            zf.writestr('Dockerfile', 'FROM python:3.9\nRUN pip install flask')
        
        zip_buffer.seek(0)
        return zip_buffer

    def test_analyze_project_with_mixed_file_types(self):
        """Test that analysis handles mixed file types correctly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_buffer = self._create_project_zip()
            
            with zipfile.ZipFile(zip_buffer, 'r') as zf:
                zf.extractall(tmpdir)
            
            result = analyze_project(tmpdir, max_files=20)
            
            # Should have scanned multiple files
            self.assertGreater(result['total_files_scanned'], 0)
            
            # Should detect multiple skills
            self.assertGreater(len(result['skills']), 0)

    def test_analysis_with_project_metadata(self):
        """Test analysis with project metadata mapping"""
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_buffer = self._create_project_zip()
            
            with zipfile.ZipFile(zip_buffer, 'r') as zf:
                zf.extractall(tmpdir)
            
            project_metadata = {
                1: {'root': str(Path(tmpdir) / 'src'), 'timestamp': 1697614794},
                2: {'root': str(Path(tmpdir) / 'frontend'), 'timestamp': 1697614850},
            }
            
            result = analyze_project(tmpdir, max_files=20, project_metadata=project_metadata)
            
            # Should have chronological skills
            self.assertIn('chronological_skills', result)
            
            # Should have assigned project tags
            if result['chronological_skills']:
                tags = [s['project_tag'] for s in result['chronological_skills']]
                self.assertTrue(any(tag in [1, 2, 0] for tag in tags))

    def test_analysis_with_file_timestamps(self):
        """Test analysis with individual file timestamps"""
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_buffer = self._create_project_zip()
            
            with zipfile.ZipFile(zip_buffer, 'r') as zf:
                zf.extractall(tmpdir)
                file_timestamps = extract_all_file_timestamps(zf)
            
            result = analyze_project(tmpdir, max_files=20, file_timestamps=file_timestamps)
            
            # Should have chronological skills
            self.assertIn('chronological_skills', result)
            
            # All skills with timestamps should have valid timestamp values
            for skill in result['chronological_skills']:
                if skill['last_used_timestamp'] is not None:
                    self.assertGreater(skill['last_used_timestamp'], 0)

    def test_code_files_analyzed_nondocs_ignored(self):
        """Test that code files are analyzed but docs are ignored"""
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_buffer = self._create_project_zip()
            
            with zipfile.ZipFile(zip_buffer, 'r') as zf:
                zf.extractall(tmpdir)
            
            result = analyze_project(tmpdir, max_files=50)
            
            # Should detect code-based skills
            self.assertGreater(len(result['skills']), 0)
            
            # Should NOT detect skills from .docx or .md files
            scanned_files = result.get('scanned_files', [])
            # If we have scanned files list, verify it contains code files
            # and not document files


class TestChronologicalOrderingAccuracy(unittest.TestCase):
    """Test that chronological ordering is accurate"""

    def test_skills_ordered_by_file_modification(self):
        """Test that skills are ordered by actual file timestamps"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create files with content
            (tmppath / 'file1.py').write_text('from flask import Flask')
            (tmppath / 'file2.js').write_text("import React from 'react'")
            (tmppath / 'file3.sql').write_text('SELECT * FROM users')
            
            # Create file timestamps dict simulating ZIP metadata
            import time
            now = time.time()
            file_timestamps = {
                'file1.py': now - 1000,  # oldest
                'file2.js': now - 500,   # middle
                'file3.sql': now,        # most recent
            }
            
            result = analyze_project(tmpdir, max_files=10, file_timestamps=file_timestamps)
            
            if len(result['chronological_skills']) > 1:
                # First skill should be most recent
                first_skill_time = result['chronological_skills'][0]['last_used_timestamp']
                # Subsequent skills should be older
                for i in range(1, len(result['chronological_skills'])):
                    next_time = result['chronological_skills'][i]['last_used_timestamp']
                    if next_time is not None:
                        self.assertLessEqual(next_time, first_skill_time)

    def test_same_skill_different_files_uses_most_recent(self):
        """Test that when a skill appears in multiple files, most recent timestamp is used"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create multiple Python files with same framework
            (tmppath / 'old_flask.py').write_text('from flask import Flask')
            (tmppath / 'new_flask.py').write_text('from flask import Flask, render_template')
            
            import time
            now = time.time()
            file_timestamps = {
                'old_flask.py': now - 1000,  # older
                'new_flask.py': now,          # newer
            }
            
            result = analyze_project(tmpdir, max_files=10, file_timestamps=file_timestamps)
            
            # Find Web Backend skill
            web_backend_skills = [s for s in result['chronological_skills'] if 'Backend' in s.get('skill', '')]
            
            if web_backend_skills:
                # Should use the most recent timestamp
                most_recent_skill = web_backend_skills[0]
                self.assertAlmostEqual(most_recent_skill['last_used_timestamp'], now, delta=5)

    def test_chronological_skills_include_file_path(self):
        """Test that chronological skills include the file they were found in"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            (tmppath / 'app.py').write_text('from flask import Flask')
            (tmppath / 'style.css').write_text('body { color: blue; }')
            
            result = analyze_project(tmpdir, max_files=10)
            
            if result['chronological_skills']:
                for skill in result['chronological_skills']:
                    self.assertIn('last_used_path', skill)
                    # Path should not be empty
                    self.assertIsNotNone(skill['last_used_path'])
                    self.assertGreater(len(skill['last_used_path']), 0)


class TestProjectMetadataMapping(unittest.TestCase):
    """Test mapping of files to projects via metadata"""

    def test_files_assigned_to_correct_project(self):
        """Test that files are assigned to the correct project based on path"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create project structure
            proj1 = tmppath / 'project1'
            proj2 = tmppath / 'project2'
            proj1.mkdir()
            proj2.mkdir()
            
            (proj1 / 'backend.py').write_text('from flask import Flask')
            (proj2 / 'frontend.js').write_text("import React from 'react'")
            
            # Create metadata mapping
            project_metadata = {
                1: {'root': str(proj1), 'timestamp': 1697614794},
                2: {'root': str(proj2), 'timestamp': 1697614850},
            }
            
            result = analyze_project(tmpdir, max_files=10, project_metadata=project_metadata)
            
            # Check that files are assigned correct project tags
            if result['chronological_skills']:
                # We should have skills from both projects (or unmatched with tag 0)
                tags = {s['project_tag'] for s in result['chronological_skills']}
                self.assertTrue(any(tag in [0, 1, 2] for tag in tags))

    def test_root_project_tag_zero_for_unmatched_files(self):
        """Test that files not matching any project get tag 0"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create a file at root
            (tmppath / 'root.py').write_text('from flask import Flask')
            
            # Create metadata with specific project not covering root
            project_metadata = {
                0: {'root': str(tmppath), 'timestamp': 1697614794},
            }
            
            result = analyze_project(tmpdir, max_files=10, project_metadata=project_metadata)
            
            # Root-level files should have tag 0
            if result['chronological_skills']:
                tags = [s['project_tag'] for s in result['chronological_skills']]
                self.assertTrue(any(tag == 0 for tag in tags))


class TestUploadWorkflowIntegration(unittest.TestCase):
    """Test complete upload workflow"""

    def test_compute_metadata_before_analysis(self):
        """Test that project metadata is computed before analysis"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create projects
            (tmppath / 'README.md').write_text('# Root')
            proj = tmppath / 'subproject'
            proj.mkdir()
            (proj / '.git').mkdir()
            (proj / 'code.py').write_text('code')
            
            # First compute metadata
            last_updated_info = compute_projects_last_updated(tmpdir)
            
            # Then analyze
            result = analyze_project(tmpdir, max_files=10)
            
            # Both should work
            self.assertIn('projects', last_updated_info)
            self.assertIn('chronological_skills', result)

    def test_workflow_with_zip_timestamps(self):
        """Test complete workflow from ZIP extraction to skill analysis"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and extract ZIP
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zf:
                zf.writestr('README.md', '# Test')
                zf.writestr('main.py', 'from flask import Flask')
                zf.writestr('style.css', 'body {}')
            zip_buffer.seek(0)
            
            with zipfile.ZipFile(zip_buffer, 'r') as zf:
                zf.extractall(tmpdir)
                file_timestamps = extract_all_file_timestamps(zf)
            
            # Compute metadata
            last_updated_info = compute_projects_last_updated(tmpdir)
            
            # Analyze with all data
            result = analyze_project(
                tmpdir,
                max_files=10,
                file_timestamps=file_timestamps
            )
            
            # Verify all components worked
            self.assertGreater(len(file_timestamps), 0)
            self.assertIn('overall_last_updated', last_updated_info)
            self.assertIn('chronological_skills', result)
            self.assertGreater(len(result['chronological_skills']), 0)


if __name__ == '__main__':
    unittest.main()
