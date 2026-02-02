"""
Tests for the folder upload service layer components.

Following TDD approach:
1. Write tests first
2. Implement services to make tests pass
3. Refactor as needed
"""

import io
import zipfile
import tempfile
from pathlib import Path

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile


class ZipValidatorTests(TestCase):
    """Tests for ZipValidator service."""
    
    def make_zip_bytes(self, files: dict) -> bytes:
        """Helper: Create an in-memory zip archive."""
        bio = io.BytesIO()
        with zipfile.ZipFile(bio, mode="w") as z:
            for name, content in files.items():
                data = content.encode("utf-8") if isinstance(content, str) else content
                z.writestr(name, data)
        return bio.getvalue()
    
    def test_validate_valid_zip(self):
        """Test that a valid ZIP file passes validation."""
        from app.services.folder_upload.zip_validator import ZipValidator
        
        zip_bytes = self.make_zip_bytes({"test.txt": "hello"})
        upload = SimpleUploadedFile("test.zip", zip_bytes, content_type="application/zip")
        
        validator = ZipValidator()
        result = validator.validate(upload)
        
        self.assertTrue(result)
    
    def test_validate_invalid_file(self):
        """Test that a non-ZIP file raises ValueError."""
        from app.services.folder_upload.zip_validator import ZipValidator
        
        upload = SimpleUploadedFile("test.txt", b"not a zip", content_type="text/plain")
        
        validator = ZipValidator()
        
        with self.assertRaises(ValueError) as context:
            validator.validate(upload)
        
        self.assertIn("not a zip archive", str(context.exception).lower())
    
    def test_validate_none_file(self):
        """Test that None upload raises ValueError."""
        from app.services.folder_upload.zip_validator import ZipValidator
        
        validator = ZipValidator()
        
        with self.assertRaises(ValueError) as context:
            validator.validate(None)
        
        self.assertIn("no file", str(context.exception).lower())
    
    def test_validate_empty_upload(self):
        """Test that empty upload raises ValueError."""
        from app.services.folder_upload.zip_validator import ZipValidator
        
        upload = SimpleUploadedFile("empty.zip", b"", content_type="application/zip")
        
        validator = ZipValidator()
        
        with self.assertRaises(ValueError):
            validator.validate(upload)


class ZipExtractorTests(TestCase):
    """Tests for ZipExtractor service."""
    
    def make_zip_bytes(self, files: dict) -> bytes:
        """Helper: Create an in-memory zip archive."""
        bio = io.BytesIO()
        with zipfile.ZipFile(bio, mode="w") as z:
            for name, content in files.items():
                data = content.encode("utf-8") if isinstance(content, str) else content
                z.writestr(name, data)
        return bio.getvalue()
    
    def test_extract_to_temp_dir(self):
        """Test extraction to a temporary directory."""
        from app.services.folder_upload.zip_extractor import ZipExtractor
        
        files = {"test.txt": "hello world"}
        zip_bytes = self.make_zip_bytes(files)
        upload = SimpleUploadedFile("test.zip", zip_bytes, content_type="application/zip")
        
        extractor = ZipExtractor()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            result_path = extractor.extract(upload, tmpdir_path)
            
            # Check that extraction returns the content subdirectory
            expected_content_dir = tmpdir_path / "content"
            self.assertEqual(result_path, expected_content_dir)
            
            # Check that file exists in content subdirectory
            extracted_file = expected_content_dir / "test.txt"
            self.assertTrue(extracted_file.exists())
            self.assertEqual(extracted_file.read_text(), "hello world")
    
    def test_preserve_nested_structure(self):
        """Test that nested folder structure is preserved."""
        from app.services.folder_upload.zip_extractor import ZipExtractor
        
        files = {
            "folder/subfolder/deep.txt": "nested",
            "folder/file.txt": "top"
        }
        zip_bytes = self.make_zip_bytes(files)
        upload = SimpleUploadedFile("test.zip", zip_bytes, content_type="application/zip")
        
        extractor = ZipExtractor()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            content_dir = extractor.extract(upload, tmpdir_path)
            
            # Check nested structure in content subdirectory
            self.assertTrue((content_dir / "folder" / "subfolder" / "deep.txt").exists())
            self.assertTrue((content_dir / "folder" / "file.txt").exists())
    
    def test_extract_creates_archive_file(self):
        """Test that the archive file is created in archive subdirectory."""
        from app.services.folder_upload.zip_extractor import ZipExtractor
        
        files = {"test.txt": "content"}
        zip_bytes = self.make_zip_bytes(files)
        upload = SimpleUploadedFile("test.zip", zip_bytes, content_type="application/zip")
        
        extractor = ZipExtractor()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            extractor.extract(upload, tmpdir_path)
            
            # Check that upload.zip was created in archive subdirectory (separate from content)
            archive_path = tmpdir_path / "archive" / "upload.zip"
            self.assertTrue(archive_path.exists())


class ProjectDiscoveryServiceTests(TestCase):
    """Tests for ProjectDiscoveryService."""
    
    def test_discover_single_repo(self):
        """Test discovering a single Git repository."""
        from app.services.folder_upload.project_discovery_service import ProjectDiscoveryService
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create a .git directory
            git_dir = tmpdir_path / "project" / ".git"
            git_dir.mkdir(parents=True)
            (git_dir / "HEAD").write_text("ref: refs/heads/main")
            
            service = ProjectDiscoveryService()
            projects = service.discover(tmpdir_path)
            
            # Should find 1 project
            self.assertEqual(len(projects), 1)
            # Project tag should be 1
            self.assertIn(1, projects.values())
    
    def test_discover_multiple_repos(self):
        """Test discovering multiple Git repositories."""
        from app.services.folder_upload.project_discovery_service import ProjectDiscoveryService
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create two .git directories
            (tmpdir_path / "project1" / ".git" / "HEAD").parent.mkdir(parents=True)
            (tmpdir_path / "project1" / ".git" / "HEAD").write_text("ref: refs/heads/main")
            
            (tmpdir_path / "project2" / ".git" / "HEAD").parent.mkdir(parents=True)
            (tmpdir_path / "project2" / ".git" / "HEAD").write_text("ref: refs/heads/main")
            
            service = ProjectDiscoveryService()
            projects = service.discover(tmpdir_path)
            
            # Should find 2 projects
            self.assertEqual(len(projects), 2)
            # Should have tags 1 and 2
            tags = set(projects.values())
            self.assertEqual(tags, {1, 2})
    
    def test_no_repos_returns_empty(self):
        """Test that no repos returns empty dict."""
        from app.services.folder_upload.project_discovery_service import ProjectDiscoveryService
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create some files but no .git
            (tmpdir_path / "file.txt").write_text("content")
            
            service = ProjectDiscoveryService()
            projects = service.discover(tmpdir_path)
            
            # Should find no projects
            self.assertEqual(len(projects), 0)


class FileScannerServiceTests(TestCase):
    """Tests for FileScannerService."""
    
    def test_scan_files_basic(self):
        """Test basic file scanning."""
        from app.services.folder_upload.file_scanner_service import FileScannerService
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create test files
            (tmpdir_path / "test.py").write_text("print('hello')")
            (tmpdir_path / "readme.md").write_text("# README")
            
            service = FileScannerService()
            results = service.scan(tmpdir_path, {}, {})
            
            # Should find 2 files
            self.assertEqual(len(results), 2)
            
            # Check that files have type field
            for result in results:
                self.assertIn("type", result)
                self.assertIn("path", result)
    
    def test_exclude_git_files(self):
        """Test that .git files are scanned but tagged properly."""
        from app.services.folder_upload.file_scanner_service import FileScannerService
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create .git directory with files
            git_dir = tmpdir_path / ".git"
            git_dir.mkdir()
            (git_dir / "HEAD").write_text("ref: refs/heads/main")
            (tmpdir_path / "regular.txt").write_text("content")
            
            service = FileScannerService()
            results = service.scan(tmpdir_path, {}, {})
            
            # Should find files (including .git)
            self.assertGreaterEqual(len(results), 2)
    
    def test_normalize_paths(self):
        """Test that paths are normalized to relative POSIX format."""
        from app.services.folder_upload.file_scanner_service import FileScannerService
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create nested file
            nested = tmpdir_path / "folder" / "subfolder" / "file.txt"
            nested.parent.mkdir(parents=True)
            nested.write_text("content")
            
            service = FileScannerService()
            results = service.scan(tmpdir_path, {}, {})
            
            # Path should be relative and use forward slashes
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]["path"], "folder/subfolder/file.txt")
    
    def test_assign_project_tags(self):
        """Test that project tags are assigned correctly."""
        from app.services.folder_upload.file_scanner_service import FileScannerService
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create project structure
            project_dir = tmpdir_path / "myproject"
            project_dir.mkdir()
            (project_dir / "file.py").write_text("code")
            
            # Mock projects dict
            projects = {project_dir: 1}
            projects_rel = {1: "myproject"}
            
            service = FileScannerService()
            results = service.scan(tmpdir_path, projects, projects_rel)
            
            # File should have project_tag
            py_file = [r for r in results if r["path"].endswith("file.py")][0]
            self.assertEqual(py_file.get("project_tag"), 1)
            self.assertEqual(py_file.get("project_root"), "myproject")


class FolderUploadServiceTests(TestCase):
    """Integration tests for FolderUploadService orchestrator."""
    
    def make_zip_bytes(self, files: dict) -> bytes:
        """Helper: Create an in-memory zip archive."""
        bio = io.BytesIO()
        with zipfile.ZipFile(bio, mode="w") as z:
            for name, content in files.items():
                data = content.encode("utf-8") if isinstance(content, str) else content
                z.writestr(name, data)
        return bio.getvalue()
    
    def test_process_zip_end_to_end(self):
        """Test complete zip processing workflow."""
        from app.services.folder_upload.folder_upload_service import FolderUploadService
        
        files = {
            "project/.git/HEAD": "ref: refs/heads/main",
            "project/main.py": "print('hello')",
            "project/README.md": "# Project"
        }
        zip_bytes = self.make_zip_bytes(files)
        upload = SimpleUploadedFile("test.zip", zip_bytes, content_type="application/zip")
        
        service = FolderUploadService()
        result = service.process_zip(upload)
        
        # Check response structure
        self.assertIn("source", result)
        self.assertIn("projects", result)
        self.assertIn("overall", result)
        
        # Should have at least one project
        self.assertGreaterEqual(len(result["projects"]), 1)
    
    def test_process_zip_with_invalid_file(self):
        """Test that invalid zip raises ValueError."""
        from app.services.folder_upload.folder_upload_service import FolderUploadService
        
        upload = SimpleUploadedFile("test.txt", b"not a zip", content_type="text/plain")
        
        service = FolderUploadService()
        
        with self.assertRaises(ValueError):
            service.process_zip(upload)
    
    def test_process_zip_with_github_username(self):
        """Test processing with GitHub username filter."""
        from app.services.folder_upload.folder_upload_service import FolderUploadService
        
        files = {"test.txt": "content"}
        zip_bytes = self.make_zip_bytes(files)
        upload = SimpleUploadedFile("test.zip", zip_bytes, content_type="application/zip")
        
        service = FolderUploadService()
        result = service.process_zip(upload, github_username="testuser")
        
        # Should process successfully
        self.assertIn("source", result)
