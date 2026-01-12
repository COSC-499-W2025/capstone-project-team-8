"""
Test Human File Filter Service

TDD tests for filtering out auto-generated files and keeping only human-written files.
"""
import unittest
from pathlib import Path


class TestHumanFileFilter(unittest.TestCase):
    """Test filtering of auto-generated vs human-written files."""
    
    def setUp(self):
        """Import the filter service."""
        from app.services.human_file_filter import HumanFileFilter
        self.filter = HumanFileFilter()
    
    # ==================== LOCK FILES ====================
    
    def test_excludes_package_lock_json(self):
        """package-lock.json should be excluded (auto-generated)."""
        self.assertFalse(self.filter.is_human_readable("package-lock.json"))
    
    def test_excludes_yarn_lock(self):
        """yarn.lock should be excluded (auto-generated)."""
        self.assertFalse(self.filter.is_human_readable("yarn.lock"))
    
    def test_excludes_pipfile_lock(self):
        """Pipfile.lock should be excluded (auto-generated)."""
        self.assertFalse(self.filter.is_human_readable("Pipfile.lock"))
    
    def test_excludes_poetry_lock(self):
        """poetry.lock should be excluded (auto-generated)."""
        self.assertFalse(self.filter.is_human_readable("poetry.lock"))
    
    def test_excludes_composer_lock(self):
        """composer.lock should be excluded (auto-generated)."""
        self.assertFalse(self.filter.is_human_readable("composer.lock"))
    
    def test_excludes_gemfile_lock(self):
        """Gemfile.lock should be excluded (auto-generated)."""
        self.assertFalse(self.filter.is_human_readable("Gemfile.lock"))
    
    def test_excludes_pnpm_lock(self):
        """pnpm-lock.yaml should be excluded (auto-generated)."""
        self.assertFalse(self.filter.is_human_readable("pnpm-lock.yaml"))
    
    # ==================== MINIFIED FILES ====================
    
    def test_excludes_minified_js(self):
        """*.min.js should be excluded (auto-generated)."""
        self.assertFalse(self.filter.is_human_readable("app.min.js"))
        self.assertFalse(self.filter.is_human_readable("vendor.min.js"))
    
    def test_excludes_minified_css(self):
        """*.min.css should be excluded (auto-generated)."""
        self.assertFalse(self.filter.is_human_readable("styles.min.css"))
    
    def test_excludes_bundle_files(self):
        """*.bundle.js should be excluded (auto-generated)."""
        self.assertFalse(self.filter.is_human_readable("main.bundle.js"))
    
    def test_excludes_source_maps(self):
        """*.map files should be excluded (auto-generated)."""
        self.assertFalse(self.filter.is_human_readable("app.js.map"))
        self.assertFalse(self.filter.is_human_readable("styles.css.map"))
    
    # ==================== BUILD/CONFIG FILES ====================
    
    def test_excludes_generated_markers(self):
        """Files with .generated. in name should be excluded."""
        self.assertFalse(self.filter.is_human_readable("schema.generated.ts"))
        self.assertFalse(self.filter.is_human_readable("types.generated.js"))
    
    def test_excludes_auto_markers(self):
        """Files with .auto. in name should be excluded."""
        self.assertFalse(self.filter.is_human_readable("config.auto.json"))
    
    def test_excludes_git_files(self):
        """.git directory files should be excluded."""
        self.assertFalse(self.filter.is_human_readable(".git/HEAD"))
        self.assertFalse(self.filter.is_human_readable(".git/config"))
        self.assertFalse(self.filter.is_human_readable("project/.git/objects/abc"))
    
    # ==================== HUMAN-WRITTEN FILES (SHOULD PASS) ====================
    
    def test_includes_regular_js(self):
        """Regular .js files should be included."""
        self.assertTrue(self.filter.is_human_readable("app.js"))
        self.assertTrue(self.filter.is_human_readable("src/index.js"))
    
    def test_includes_regular_python(self):
        """Regular .py files should be included."""
        self.assertTrue(self.filter.is_human_readable("main.py"))
        self.assertTrue(self.filter.is_human_readable("src/utils/helpers.py"))
    
    def test_includes_readme(self):
        """README files should be included."""
        self.assertTrue(self.filter.is_human_readable("README.md"))
        self.assertTrue(self.filter.is_human_readable("readme.txt"))
    
    def test_includes_package_json(self):
        """package.json (not lock) should be included."""
        self.assertTrue(self.filter.is_human_readable("package.json"))
    
    def test_includes_requirements_txt(self):
        """requirements.txt should be included."""
        self.assertTrue(self.filter.is_human_readable("requirements.txt"))
    
    def test_includes_dockerfile(self):
        """Dockerfile should be included."""
        self.assertTrue(self.filter.is_human_readable("Dockerfile"))
    
    def test_includes_html_files(self):
        """HTML files should be included."""
        self.assertTrue(self.filter.is_human_readable("index.html"))
        self.assertTrue(self.filter.is_human_readable("templates/base.html"))
    
    def test_includes_css_files(self):
        """Regular CSS files should be included."""
        self.assertTrue(self.filter.is_human_readable("styles.css"))
        self.assertTrue(self.filter.is_human_readable("src/app.css"))
    
    def test_includes_typescript(self):
        """TypeScript files should be included."""
        self.assertTrue(self.filter.is_human_readable("app.ts"))
        self.assertTrue(self.filter.is_human_readable("components/Button.tsx"))
    
    # ==================== PATH HANDLING ====================
    
    def test_handles_nested_paths(self):
        """Should handle nested file paths correctly."""
        self.assertTrue(self.filter.is_human_readable("src/components/Button.jsx"))
        self.assertFalse(self.filter.is_human_readable("node_modules/react/index.js"))
    
    def test_handles_path_objects(self):
        """Should handle Path objects as well as strings."""
        self.assertTrue(self.filter.is_human_readable(Path("src/app.py")))
        self.assertFalse(self.filter.is_human_readable(Path("package-lock.json")))
    
    # ==================== FILTER METHOD ====================
    
    def test_filter_files_returns_only_human_readable(self):
        """filter_files should return only human-readable files."""
        files = [
            {"path": "src/app.js", "type": "code"},
            {"path": "package-lock.json", "type": "code"},
            {"path": "README.md", "type": "content"},
            {"path": "dist/bundle.min.js", "type": "code"},
            {"path": "styles.css", "type": "code"},
        ]
        
        filtered = self.filter.filter_files(files)
        paths = [f["path"] for f in filtered]
        
        self.assertIn("src/app.js", paths)
        self.assertIn("README.md", paths)
        self.assertIn("styles.css", paths)
        self.assertNotIn("package-lock.json", paths)
        self.assertNotIn("dist/bundle.min.js", paths)
    
    def test_filter_preserves_file_data(self):
        """filter_files should preserve all file data."""
        files = [
            {"path": "app.py", "type": "code", "lines": 100, "extra": "data"},
        ]
        
        filtered = self.filter.filter_files(files)
        
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["lines"], 100)
        self.assertEqual(filtered[0]["extra"], "data")


class TestHumanFileFilterIntegration(unittest.TestCase):
    """Integration tests for human file filter with the upload response."""
    
    def test_condensed_section_in_response(self):
        """
        Test that the response includes a 'human_readable_files' condensed section.
        This tests the full integration with data_transformer.
        """
        # This will be implemented after the service is created
        pass


if __name__ == "__main__":
    unittest.main()
