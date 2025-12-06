import unittest
from datetime import datetime
from pathlib import Path
import sys
import os
import tempfile
import zipfile
from io import BytesIO

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src/backend'))

from app.services.analysis.analyzers.last_updated import (
    compute_projects_last_updated,
    extract_all_file_timestamps,
)


class TestComputeProjectsLastUpdated(unittest.TestCase):
    """Test project last updated computation"""

    def test_compute_projects_identifies_git_project(self):
        """Test that .git directory marks a project root"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create .git marker
            git_dir = Path(tmpdir) / '.git'
            git_dir.mkdir()
            
            # Create a file
            (Path(tmpdir) / 'file.py').write_text('print("test")')
            
            result = compute_projects_last_updated(tmpdir)
            
            self.assertIn('projects', result)
            self.assertGreater(len(result['projects']), 0)

    def test_compute_projects_identifies_readme_project(self):
        """Test that README.md marks a project root"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create README marker
            (Path(tmpdir) / 'README.md').write_text('# Project')
            
            result = compute_projects_last_updated(tmpdir)
            
            self.assertIn('projects', result)

    def test_compute_projects_nested_structure(self):
        """Test nested project structure"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create first project
            proj1 = tmppath / 'project1'
            proj1.mkdir()
            (proj1 / 'README.md').write_text('# Project 1')
            (proj1 / 'file.py').write_text('code')
            
            # Create second project
            proj2 = tmppath / 'project2'
            proj2.mkdir()
            (proj2 / '.git').mkdir()
            (proj2 / 'file.js').write_text('code')
            
            result = compute_projects_last_updated(tmpdir)
            
            self.assertIn('projects', result)
            self.assertGreaterEqual(len(result['projects']), 2)

    def test_compute_projects_returns_timestamps(self):
        """Test that timestamps are returned for each project"""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / 'README.md').write_text('# Project')
            
            result = compute_projects_last_updated(tmpdir)
            
            self.assertIn('overall_last_updated', result)
            # overall_last_updated can be string (ISO) or numeric
            self.assertTrue(isinstance(result['overall_last_updated'], (int, float, str)))

    def test_compute_projects_empty_directory(self):
        """Test behavior with empty directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = compute_projects_last_updated(tmpdir)
            
            self.assertIn('projects', result)
            # projects can be dict or list depending on implementation
            self.assertTrue(isinstance(result['projects'], (dict, list)))


class TestExtractAllFileTimestamps(unittest.TestCase):
    """Test extraction of file timestamps from ZIP archives"""

    def _create_test_zip(self, files_dict):
        """Helper to create a ZIP with specified files and timestamps"""
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            for filename, content in files_dict.items():
                zf.writestr(filename, content)
        zip_buffer.seek(0)
        return zip_buffer

    def test_extract_all_file_timestamps_returns_dict(self):
        """Test that extract_all_file_timestamps returns a dict"""
        test_files = {
            'file1.py': 'print("hello")',
            'file2.py': 'print("world")',
        }
        zip_buffer = self._create_test_zip(test_files)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            timestamps = extract_all_file_timestamps(zf)
        
        self.assertIsInstance(timestamps, dict)

    def test_extract_all_file_timestamps_includes_files(self):
        """Test that all files are in the returned dict"""
        test_files = {
            'file1.py': 'print("hello")',
            'file2.js': 'console.log("world")',
            'file3.sql': 'SELECT * FROM users',
        }
        zip_buffer = self._create_test_zip(test_files)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            timestamps = extract_all_file_timestamps(zf)
        
        self.assertEqual(len(timestamps), 3)
        self.assertIn('file1.py', timestamps)
        self.assertIn('file2.js', timestamps)
        self.assertIn('file3.sql', timestamps)

    def test_extract_all_file_timestamps_are_unix_timestamps(self):
        """Test that returned timestamps are valid Unix timestamps"""
        test_files = {
            'file1.py': 'code1',
            'file2.py': 'code2',
        }
        zip_buffer = self._create_test_zip(test_files)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            timestamps = extract_all_file_timestamps(zf)
        
        for filename, timestamp in timestamps.items():
            self.assertIsInstance(timestamp, (int, float))
            # Unix timestamp should be reasonable (after 2000)
            self.assertGreater(timestamp, 946684800)  # Jan 1, 2000
            # Should be before year 2100
            self.assertLess(timestamp, 4102444800)

    def test_extract_all_file_timestamps_excludes_directories(self):
        """Test that directories are excluded from timestamps"""
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            # Add a directory entry
            dir_info = zipfile.ZipInfo('folder/')
            zf.writestr(dir_info, '')
            # Add a file
            zf.writestr('folder/file.py', 'code')
        zip_buffer.seek(0)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            timestamps = extract_all_file_timestamps(zf)
        
        # Should only contain the file, not the directory
        self.assertNotIn('folder/', timestamps)
        self.assertIn('folder/file.py', timestamps)

    def test_extract_all_file_timestamps_nested_structure(self):
        """Test extraction from nested directory structure"""
        test_files = {
            'src/main.py': 'main code',
            'src/utils/helper.py': 'helper code',
            'tests/test.py': 'test code',
        }
        zip_buffer = self._create_test_zip(test_files)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            timestamps = extract_all_file_timestamps(zf)
        
        self.assertEqual(len(timestamps), 3)
        self.assertIn('src/main.py', timestamps)
        self.assertIn('src/utils/helper.py', timestamps)
        self.assertIn('tests/test.py', timestamps)

    def test_extract_all_file_timestamps_path_format(self):
        """Test that paths are in POSIX format"""
        test_files = {
            'dir/subdir/file.py': 'code',
        }
        zip_buffer = self._create_test_zip(test_files)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            timestamps = extract_all_file_timestamps(zf)
        
        paths = list(timestamps.keys())
        # Should use forward slashes
        self.assertTrue(all('/' in p or '\\' not in p for p in paths))

    def test_extract_timestamps_large_zip(self):
        """Test extraction from ZIP with many files"""
        test_files = {f'file{i}.py': f'code{i}' for i in range(50)}
        zip_buffer = self._create_test_zip(test_files)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            timestamps = extract_all_file_timestamps(zf)
        
        self.assertEqual(len(timestamps), 50)
        # All timestamps should be reasonable
        for ts in timestamps.values():
            self.assertIsInstance(ts, (int, float))
            self.assertGreater(ts, 0)

    def test_extract_timestamps_preserves_different_times(self):
        """Test that files can have different timestamps"""
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            # Create files with different timestamps
            info1 = zipfile.ZipInfo('file1.py', date_time=(2025, 1, 1, 12, 0, 0))
            zf.writestr(info1, 'code1')
            
            info2 = zipfile.ZipInfo('file2.py', date_time=(2025, 1, 15, 18, 30, 45))
            zf.writestr(info2, 'code2')
        zip_buffer.seek(0)
        
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            timestamps = extract_all_file_timestamps(zf)
        
        # Both files should be present
        self.assertEqual(len(timestamps), 2)
        # Timestamps should be different
        ts1 = timestamps['file1.py']
        ts2 = timestamps['file2.py']
        self.assertNotEqual(ts1, ts2)
        # file2 should be more recent
        self.assertGreater(ts2, ts1)


class TestFileTimestampIntegration(unittest.TestCase):
    """Test integration of file timestamp extraction with analysis"""

    def test_project_last_updated_workflow(self):
        """Test the complete workflow of computing last updated times"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create a project structure
            (tmppath / 'README.md').write_text('# Test Project')
            (tmppath / 'src').mkdir()
            (tmppath / 'src' / 'main.py').write_text('print("main")')
            (tmppath / 'src' / 'utils.py').write_text('def helper(): pass')
            
            result = compute_projects_last_updated(tmpdir)
            
            # Verify structure
            self.assertIn('projects', result)
            self.assertIn('overall_last_updated', result)
            # overall_last_updated can be string (ISO) or numeric
            self.assertTrue(isinstance(result['overall_last_updated'], (int, float, str)))

    def test_timestamps_increase_with_newer_files(self):
        """Test that newer files result in newer last_updated times"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create first file
            (tmppath / 'README.md').write_text('# Project')
            result1 = compute_projects_last_updated(tmpdir)
            ts1 = result1['overall_last_updated']
            
            # Wait and create a newer file
            import time
            time.sleep(1)
            (tmppath / 'newer_file.py').write_text('newer code')
            result2 = compute_projects_last_updated(tmpdir)
            ts2 = result2['overall_last_updated']
            
            # Second timestamp should be >= first
            self.assertGreaterEqual(ts2, ts1)


if __name__ == '__main__':
    unittest.main()
