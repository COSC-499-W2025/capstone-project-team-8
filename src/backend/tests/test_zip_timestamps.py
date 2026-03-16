import os
import sys
import tempfile
import zipfile
from pathlib import Path
from datetime import datetime
from django.test import TestCase

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
import django
django.setup()

from app.services.folder_upload.folder_upload_service import FolderUploadService


class ZipTimestampExtractionTests(TestCase):
    """Test suite for extracting timestamps from ZIP file metadata for non-git projects"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dirs = []
        self.service = FolderUploadService()

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        import stat
        
        def handle_remove_readonly(func, path, exc):
            """Error handler for Windows readonly files"""
            os.chmod(path, stat.S_IWRITE)
            func(path)
        
        for temp_dir in self.temp_dirs:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, onerror=handle_remove_readonly)

    def create_zip_with_timestamps(self, file_dates):
        """
        Create a ZIP file with specific file timestamps.
        
        Args:
            file_dates: List of tuples (filename, datetime_tuple)
                       datetime_tuple is (year, month, day, hour, minute, second)
        
        Returns:
            Path to created ZIP file
        """
        temp_dir = tempfile.mkdtemp()
        self.temp_dirs.append(temp_dir)
        
        # Create actual files
        for filename, _ in file_dates:
            file_path = Path(temp_dir) / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(f"Content of {filename}")
        
        # Create ZIP with custom timestamps
        zip_path = Path(temp_dir) / "test.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            for filename, date_tuple in file_dates:
                file_path = Path(temp_dir) / filename
                zip_info = zipfile.ZipInfo(filename, date_time=date_tuple)
                with open(file_path, 'rb') as f:
                    zf.writestr(zip_info, f.read())
        
        return zip_path

    def test_extract_oldest_timestamp_from_single_project(self):
        """Test extracting oldest file timestamp from a single non-git project"""
        # Create ZIP with files from 2023, 2024, and 2025
        zip_path = self.create_zip_with_timestamps([
            ("project1/file1.txt", (2023, 1, 15, 10, 30, 0)),  # Oldest
            ("project1/file2.txt", (2024, 6, 20, 14, 45, 0)),
            ("project1/file3.txt", (2025, 11, 1, 9, 15, 0)),   # Newest
        ])
        
        tmpdir = Path(tempfile.mkdtemp())
        self.temp_dirs.append(str(tmpdir))
        
        # Extract to get proper project structure
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(tmpdir)
        
        # Simulate projects dict (project1 has tag 1)
        projects = {tmpdir / "project1": 1}
        
        # Call the method we'll implement
        result = self.service._get_zip_file_timestamps(zip_path, projects, tmpdir)
        
        # Should return timestamp for oldest file (2023-01-15)
        expected_timestamp = int(datetime(2023, 1, 15, 10, 30, 0).timestamp())
        self.assertEqual(result[1], expected_timestamp)

    def test_extract_timestamps_from_multiple_projects(self):
        """Test extracting timestamps from multiple non-git projects"""
        zip_path = self.create_zip_with_timestamps([
            ("projectA/old.txt", (2020, 3, 10, 8, 0, 0)),      # ProjectA oldest
            ("projectA/newer.txt", (2022, 7, 15, 12, 0, 0)),
            ("projectB/ancient.txt", (2019, 1, 1, 0, 0, 0)),   # ProjectB oldest (oldest overall)
            ("projectB/recent.txt", (2023, 5, 20, 16, 30, 0)),
            ("projectC/mid.txt", (2021, 11, 25, 10, 15, 0)),   # ProjectC only file
        ])
        
        tmpdir = Path(tempfile.mkdtemp())
        self.temp_dirs.append(str(tmpdir))
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(tmpdir)
        
        projects = {
            tmpdir / "projectA": 1,
            tmpdir / "projectB": 2,
            tmpdir / "projectC": 3,
        }
        
        result = self.service._get_zip_file_timestamps(zip_path, projects, tmpdir)
        
        # Check each project got its oldest file timestamp
        self.assertEqual(result[1], int(datetime(2020, 3, 10, 8, 0, 0).timestamp()))
        self.assertEqual(result[2], int(datetime(2019, 1, 1, 0, 0, 0).timestamp()))
        self.assertEqual(result[3], int(datetime(2021, 11, 25, 10, 15, 0).timestamp()))

    def test_skip_tag_zero_non_git_files(self):
        """Test that tag 0 (unorganized non-git files) is skipped"""
        zip_path = self.create_zip_with_timestamps([
            ("random/file.txt", (2020, 1, 1, 0, 0, 0)),
        ])
        
        tmpdir = Path(tempfile.mkdtemp())
        self.temp_dirs.append(str(tmpdir))
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(tmpdir)
        
        projects = {tmpdir / "random": 0}  # Tag 0 = unorganized files
        
        result = self.service._get_zip_file_timestamps(zip_path, projects, tmpdir)
        
        # Should not include tag 0
        self.assertNotIn(0, result)
        self.assertEqual(len(result), 0)

    def test_handle_nested_directory_structure(self):
        """Test that nested directories are handled correctly"""
        zip_path = self.create_zip_with_timestamps([
            ("project/src/main/java/App.java", (2022, 5, 10, 14, 20, 0)),  # Oldest
            ("project/src/test/Test.java", (2023, 8, 15, 9, 30, 0)),
            ("project/README.md", (2024, 1, 5, 11, 45, 0)),
        ])
        
        tmpdir = Path(tempfile.mkdtemp())
        self.temp_dirs.append(str(tmpdir))
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(tmpdir)
        
        projects = {tmpdir / "project": 1}
        
        result = self.service._get_zip_file_timestamps(zip_path, projects, tmpdir)
        
        # Should return the oldest nested file
        expected_timestamp = int(datetime(2022, 5, 10, 14, 20, 0).timestamp())
        self.assertEqual(result[1], expected_timestamp)

    def test_handle_invalid_timestamps_gracefully(self):
        """Test that invalid timestamps don't crash the function"""
        temp_dir = tempfile.mkdtemp()
        self.temp_dirs.append(temp_dir)
        
        # Create file
        file_path = Path(temp_dir) / "project" / "file.txt"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("content")
        
        # Create ZIP with intentionally invalid date
        zip_path = Path(temp_dir) / "test.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            # Invalid date tuple (month 13 doesn't exist)
            try:
                zip_info = zipfile.ZipInfo("project/file.txt", date_time=(2023, 13, 99, 25, 61, 61))
                with open(file_path, 'rb') as f:
                    zf.writestr(zip_info, f.read())
            except:
                # If zipfile rejects it, use a valid date for testing
                zip_info = zipfile.ZipInfo("project/file.txt", date_time=(2023, 1, 1, 0, 0, 0))
                with open(file_path, 'rb') as f:
                    zf.writestr(zip_info, f.read())
        
        tmpdir = Path(tempfile.mkdtemp())
        self.temp_dirs.append(str(tmpdir))
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(tmpdir)
        
        projects = {tmpdir / "project": 1}
        
        # Should not crash, just skip invalid files
        result = self.service._get_zip_file_timestamps(zip_path, projects, tmpdir)
        
        # Result might be empty or contain valid timestamp, but shouldn't crash
        self.assertIsInstance(result, dict)

    def test_empty_zip_returns_empty_dict(self):
        """Test that an empty ZIP returns an empty result"""
        temp_dir = tempfile.mkdtemp()
        self.temp_dirs.append(temp_dir)
        
        zip_path = Path(temp_dir) / "empty.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            pass  # Empty ZIP
        
        tmpdir = Path(tempfile.mkdtemp())
        self.temp_dirs.append(str(tmpdir))
        
        projects = {}
        
        result = self.service._get_zip_file_timestamps(zip_path, projects, tmpdir)
        
        self.assertEqual(result, {})

    def test_git_timestamps_take_priority_over_zip_timestamps(self):
        """Integration test: Git timestamps should be preferred over ZIP timestamps"""
        # This will be tested in the integration flow
        # When a project has both git history AND zip metadata,
        # the git timestamp (first commit) should take priority
        pass  # Placeholder for integration test


class ZipTimestampIntegrationTests(TestCase):
    """Integration tests for ZIP timestamp functionality in full upload flow"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dirs = []

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        import stat
        
        def handle_remove_readonly(func, path, exc):
            os.chmod(path, stat.S_IWRITE)
            func(path)
        
        for temp_dir in self.temp_dirs:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, onerror=handle_remove_readonly)

    def test_non_git_projects_ordered_chronologically(self):
        """Test that non-git projects are ordered by ZIP file timestamps"""
        from django.test import Client
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # Create ZIP with multiple non-git projects with different timestamps
        temp_dir = tempfile.mkdtemp()
        self.temp_dirs.append(temp_dir)
        
        # Create project directories
        old_project = Path(temp_dir) / "old-project"
        old_project.mkdir()
        (old_project / "old.txt").write_text("Old project")
        
        new_project = Path(temp_dir) / "new-project"
        new_project.mkdir()
        (new_project / "new.txt").write_text("New project")
        
        # Create ZIP with specific timestamps
        zip_path = Path(temp_dir) / "projects.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            # Old project - 2020
            zip_info = zipfile.ZipInfo("old-project/old.txt", date_time=(2020, 1, 1, 0, 0, 0))
            zf.writestr(zip_info, "Old project")
            
            # New project - 2024
            zip_info = zipfile.ZipInfo("new-project/new.txt", date_time=(2024, 6, 15, 0, 0, 0))
            zf.writestr(zip_info, "New project")
        
        with open(zip_path, 'rb') as f:
            zip_content = f.read()
        
        uploaded_file = SimpleUploadedFile(
            "projects.zip",
            zip_content,
            content_type="application/zip"
        )
        
        client = Client()
        response = client.post(
            "/api/upload-folder/",
            {"file": uploaded_file, "consent_scan": "1"},
            format="multipart"
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should have projects in chronological order
        self.assertIn("projects", data)
        projects = data["projects"]
        
        # Filter to non-git projects only (excluding id=0 unorganized files)
        non_git_projects = [p for p in projects if p.get("id") != 0]
        
        if len(non_git_projects) >= 2:
            # Old project should come before new project
            project_roots = [p["root"] for p in non_git_projects]
            old_index = next(i for i, root in enumerate(project_roots) if "old-project" in root)
            new_index = next(i for i, root in enumerate(project_roots) if "new-project" in root)
            
            self.assertLess(old_index, new_index, 
                          "Old project should appear before new project in chronological order")
