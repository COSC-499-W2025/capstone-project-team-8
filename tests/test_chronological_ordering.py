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

from app.services.gitFinder import get_project_timestamp


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
