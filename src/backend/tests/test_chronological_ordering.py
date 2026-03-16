import os
import sys
import tempfile
import subprocess
from pathlib import Path
from django.test import TestCase

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
import django
django.setup()

from app.services.analysis.analyzers import get_project_timestamp


class ChronologicalOrderingTests(TestCase):
    """Test suite for chronological project ordering functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = None

    def tearDown(self):
        """Clean up test fixtures"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            import stat
            
            def handle_remove_readonly(func, path, exc):
                """Error handler for Windows readonly files"""
                os.chmod(path, stat.S_IWRITE)
                func(path)
            
            shutil.rmtree(self.temp_dir, onerror=handle_remove_readonly)

    def create_git_repo_with_commits(self, delay_seconds=1):
        """Helper to create a git repository with commits at different times"""
        self.temp_dir = tempfile.mkdtemp()
        repo_path = Path(self.temp_dir)
        
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_path, check=True, capture_output=True)
        
        # Create first commit
        (repo_path / "file1.txt").write_text("First commit")
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "First commit"], cwd=repo_path, check=True, capture_output=True)
        
        # Get the first commit timestamp
        result = subprocess.run(
            ["git", "log", "--reverse", "--format=%ct"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        first_timestamp = int(result.stdout.strip().split('\n')[0])
        
        # Add a second commit (optional, to test we get the FIRST one)
        import time
        time.sleep(delay_seconds)
        (repo_path / "file2.txt").write_text("Second commit")
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Second commit"], cwd=repo_path, check=True, capture_output=True)
        
        return repo_path, first_timestamp

    def test_get_timestamp_from_git_repo(self):
        """Test that we can get the first commit timestamp from a git repository"""
        repo_path, expected_timestamp = self.create_git_repo_with_commits()
        
        result = get_project_timestamp(repo_path)
        
        self.assertIsInstance(result, int)
        self.assertEqual(result, expected_timestamp)
        self.assertGreater(result, 0)

    def test_get_timestamp_returns_first_commit_not_last(self):
        """Test that we get the FIRST commit timestamp, not the most recent"""
        repo_path, first_timestamp = self.create_git_repo_with_commits(delay_seconds=2)
        
        result = get_project_timestamp(repo_path)
        
        # Should return the first commit timestamp
        self.assertEqual(result, first_timestamp)
        
        # Verify there are multiple commits
        commit_count = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        self.assertGreater(int(commit_count.stdout.strip()), 1)

    def test_get_timestamp_non_git_directory_returns_zero(self):
        """Test that non-git directories return 0 (will be handled by fallback later)"""
        self.temp_dir = tempfile.mkdtemp()
        non_git_path = Path(self.temp_dir)
        
        # Create some files but no .git
        (non_git_path / "file.txt").write_text("content")
        
        result = get_project_timestamp(non_git_path)
        
        # Should return 0 for non-git repos (for now)
        self.assertEqual(result, 0)

    def test_get_timestamp_handles_empty_git_repo(self):
        """Test that a git repo with no commits returns 0"""
        self.temp_dir = tempfile.mkdtemp()
        repo_path = Path(self.temp_dir)
        
        # Initialize git repo but don't commit
        subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
        
        result = get_project_timestamp(repo_path)
        
        # Should return 0 for empty git repos
        self.assertEqual(result, 0)


class ProjectSortingIntegrationTests(TestCase):
    """Integration tests for chronological sorting in upload endpoint"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dirs = []

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

    def create_zip_with_multiple_git_projects(self):
        """Create a zip file containing multiple git projects with different timestamps"""
        import zipfile
        import time
        
        # Create temp directory for projects
        projects_root = tempfile.mkdtemp()
        self.temp_dirs.append(projects_root)
        root_path = Path(projects_root)
        
        # Project 1: Oldest project (created first)
        project1 = root_path / "old-project"
        project1.mkdir()
        subprocess.run(["git", "init"], cwd=project1, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=project1, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=project1, check=True, capture_output=True)
        (project1 / "old.txt").write_text("Old project")
        subprocess.run(["git", "add", "."], cwd=project1, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Old commit"], cwd=project1, check=True, capture_output=True)
        
        time.sleep(2)  # Ensure different timestamps
        
        # Project 2: Newest project (created last)
        project2 = root_path / "new-project"
        project2.mkdir()
        subprocess.run(["git", "init"], cwd=project2, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=project2, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=project2, check=True, capture_output=True)
        (project2 / "new.txt").write_text("New project")
        subprocess.run(["git", "add", "."], cwd=project2, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "New commit"], cwd=project2, check=True, capture_output=True)
        
        time.sleep(1)
        
        # Project 3: Middle project
        project3 = root_path / "middle-project"
        project3.mkdir()
        subprocess.run(["git", "init"], cwd=project3, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=project3, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=project3, check=True, capture_output=True)
        (project3 / "middle.txt").write_text("Middle project")
        subprocess.run(["git", "add", "."], cwd=project3, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Middle commit"], cwd=project3, check=True, capture_output=True)
        
        # Create zip file
        zip_path = Path(tempfile.mkdtemp()) / "projects.zip"
        self.temp_dirs.append(zip_path.parent)
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for project_dir in [project1, project2, project3]:
                for root, dirs, files in os.walk(project_dir):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(projects_root)
                        zipf.write(file_path, arcname)
        
        return zip_path

    def test_projects_ordered_chronologically_oldest_first(self):
        """Test that projects in the response are ordered chronologically (oldest first)"""
        from django.test import Client
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        zip_path = self.create_zip_with_multiple_git_projects()
        
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
        
        # Should have 3 git projects (excluding unorganized files project if present)
        self.assertIn("projects", data)
        projects = data["projects"]
        
        # Filter out unorganized files project (id=0)
        git_projects = [p for p in projects if p.get("id") != 0]
        self.assertEqual(len(git_projects), 3)
        
        # Projects should be ordered: old-project, new-project, middle-project
        # (based on chronological order of first commits)
        project_roots = [p["root"] for p in git_projects]
        
        # First project should be old-project (oldest)
        self.assertIn("old-project", project_roots[0])
        
        # Last project should be middle-project (newest)
        self.assertIn("middle-project", project_roots[-1])
        
        # Verify timestamps are in ascending order if included
        if "created_at" in git_projects[0]:
            timestamps = [p.get("created_at", 0) for p in git_projects]
            self.assertEqual(timestamps, sorted(timestamps))
