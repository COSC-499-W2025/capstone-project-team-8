"""
Test that excluded directories (node_modules, .next, etc.) are not scanned.
"""
import unittest
import tempfile
import zipfile
from pathlib import Path
from app.services.folder_upload.file_scanner_service import FileScannerService


class TestExcludedDirectories(unittest.TestCase):
    """Test that common build/dependency directories are excluded from scanning."""
    
    def setUp(self):
        """Create a temporary directory with test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # Create directory structure with excluded folders
        self.create_test_structure()
        
        self.scanner = FileScannerService()
    
    def create_test_structure(self):
        """Create a realistic project structure with excluded directories."""
        # Create main source files (should be scanned)
        (self.temp_path / "src").mkdir()
        (self.temp_path / "src" / "index.js").write_text("console.log('main');")
        (self.temp_path / "README.md").write_text("# Project")
        
        # Create node_modules (should be excluded)
        (self.temp_path / "node_modules").mkdir()
        (self.temp_path / "node_modules" / "react").mkdir()
        (self.temp_path / "node_modules" / "react" / "index.js").write_text("// React")
        
        # Create .next build folder (should be excluded)
        (self.temp_path / ".next").mkdir()
        (self.temp_path / ".next" / "static").mkdir()
        (self.temp_path / ".next" / "static" / "chunks").mkdir()
        (self.temp_path / ".next" / "static" / "chunks" / "main.js").write_text("// Build output")
        
        # Create __pycache__ (should be excluded)
        (self.temp_path / "__pycache__").mkdir()
        (self.temp_path / "__pycache__" / "test.pyc").write_bytes(b"compiled")
        
        # Create dist folder (should be excluded)
        (self.temp_path / "dist").mkdir()
        (self.temp_path / "dist" / "bundle.js").write_text("// Bundled")
        
        # Create .venv (should be excluded)
        (self.temp_path / ".venv").mkdir()
        (self.temp_path / ".venv" / "lib").mkdir()
        (self.temp_path / ".venv" / "lib" / "site.py").write_text("# Python lib")
    
    def test_excluded_directories_not_scanned(self):
        """Test that excluded directories are not scanned."""
        results = self.scanner.scan(self.temp_path, {}, {})
        
        # Get all scanned file paths
        scanned_paths = [result.get('path', '') for result in results]
        
        # Assert source files ARE scanned
        self.assertTrue(
            any('src/index.js' in path for path in scanned_paths),
            "Source files should be scanned"
        )
        self.assertTrue(
            any('README.md' in path for path in scanned_paths),
            "Root files should be scanned"
        )
        
        # Assert excluded directories are NOT scanned
        self.assertFalse(
            any('node_modules' in path for path in scanned_paths),
            "node_modules should not be scanned"
        )
        self.assertFalse(
            any('.next' in path for path in scanned_paths),
            ".next should not be scanned"
        )
        self.assertFalse(
            any('__pycache__' in path for path in scanned_paths),
            "__pycache__ should not be scanned"
        )
        self.assertFalse(
            any('dist' in path for path in scanned_paths),
            "dist should not be scanned"
        )
        self.assertFalse(
            any('.venv' in path for path in scanned_paths),
            ".venv should not be scanned"
        )
    
    def test_scan_only_includes_user_code(self):
        """Test that only user code files are included in scan results."""
        results = self.scanner.scan(self.temp_path, {}, {})
        
        # Should only have 2 files: src/index.js and README.md
        self.assertEqual(
            len(results), 
            2, 
            f"Expected 2 files, but got {len(results)}: {[r.get('path') for r in results]}"
        )
    
    def test_excluded_dirs_constant(self):
        """Test that EXCLUDED_DIRS contains expected directories."""
        expected_exclusions = {
            'node_modules', '__pycache__', '.next', 
            'dist', 'build', '.venv', 'venv'
        }
        
        # .git is NOT excluded because we need it for git analysis
        should_not_be_excluded = {'.git'}
        
        for excluded in expected_exclusions:
            self.assertIn(
                excluded, 
                self.scanner.EXCLUDED_DIRS,
                f"{excluded} should be in EXCLUDED_DIRS"
            )
        
        for not_excluded in should_not_be_excluded:
            self.assertNotIn(
                not_excluded,
                self.scanner.EXCLUDED_DIRS,
                f"{not_excluded} should NOT be in EXCLUDED_DIRS (needed for git analysis)"
            )
    
    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
