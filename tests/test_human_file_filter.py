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
        from app.services.data_transformer import transform_to_new_structure
        
        # Mock results with both human-readable and auto-generated files
        results = [
            {"type": "code", "path": "src/app.js", "lines": 100, "project_tag": 1, "project_root": "my-project"},
            {"type": "code", "path": "package-lock.json", "lines": 5000, "project_tag": 1, "project_root": "my-project"},
            {"type": "code", "path": "dist/bundle.min.js", "lines": 1, "project_tag": 1, "project_root": "my-project"},
            {"type": "content", "path": "README.md", "length": 500, "project_tag": 1, "project_root": "my-project"},
            {"type": "content", "path": "docs/guide.md", "length": 1000, "project_tag": 1, "project_root": "my-project"},
        ]
        
        projects = {Path("my-project"): 1}
        projects_rel = {1: "my-project"}
        project_classifications = {
            "project_1": {"classification": "coding", "confidence": 0.9},
            "overall": {"classification": "coding", "confidence": 0.9}
        }
        
        response = transform_to_new_structure(
            results=results,
            projects=projects,
            projects_rel=projects_rel,
            project_classifications=project_classifications,
            git_contrib_data={},
            project_timestamps={},
        )
        
        # Check that human_readable_files exists in response
        self.assertIn("human_readable_files", response)
        
        human_files = response["human_readable_files"]
        
        # Check structure
        self.assertIn("code", human_files)
        self.assertIn("content", human_files)
        self.assertIn("summary", human_files)
        
        # Check that only human-readable code files are included
        code_paths = [f["path"] for f in human_files["code"]]
        self.assertIn("app.js", code_paths)
        self.assertNotIn("package-lock.json", code_paths)
        self.assertNotIn("bundle.min.js", code_paths)
        
        # Check that all content files are included (they're human-written)
        content_paths = [f["path"] for f in human_files["content"]]
        self.assertIn("README.md", content_paths)
        self.assertIn("guide.md", content_paths)
        
        # Check summary has counts
        self.assertEqual(human_files["summary"]["total_code_files"], 1)
        self.assertEqual(human_files["summary"]["total_content_files"], 2)
    
    def test_human_readable_files_per_project(self):
        """Test that each project has its own human_readable_files section."""
        from app.services.data_transformer import transform_to_new_structure
        
        results = [
            {"type": "code", "path": "project-a/main.py", "lines": 50, "project_tag": 1, "project_root": "project-a"},
            {"type": "code", "path": "project-a/poetry.lock", "lines": 500, "project_tag": 1, "project_root": "project-a"},
            {"type": "code", "path": "project-b/app.js", "lines": 30, "project_tag": 2, "project_root": "project-b"},
        ]
        
        projects = {Path("project-a"): 1, Path("project-b"): 2}
        projects_rel = {1: "project-a", 2: "project-b"}
        project_classifications = {
            "project_1": {"classification": "coding", "confidence": 0.9},
            "project_2": {"classification": "coding", "confidence": 0.9},
            "overall": {"classification": "coding", "confidence": 0.9}
        }
        
        response = transform_to_new_structure(
            results=results,
            projects=projects,
            projects_rel=projects_rel,
            project_classifications=project_classifications,
            git_contrib_data={},
            project_timestamps={},
        )
        
        # Each project should have human_readable_files
        for project in response["projects"]:
            self.assertIn("human_readable_files", project)
            
            if project["root"] == "project-a":
                code_paths = [f["path"] for f in project["human_readable_files"]["code"]]
                self.assertIn("main.py", code_paths)
                self.assertNotIn("poetry.lock", code_paths)
            elif project["root"] == "project-b":
                code_paths = [f["path"] for f in project["human_readable_files"]["code"]]
                self.assertIn("app.js", code_paths)


class TestHumanFileContentExtraction(unittest.TestCase):
    """Tests for extracting human-readable file contents for LLM analysis."""
    
    def test_get_human_readable_content_from_project(self):
        """
        Test that we can extract content from human-readable files only.
        """
        import tempfile
        import os
        from app.services.human_file_filter import HumanFileFilter
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            src_dir = os.path.join(tmpdir, "src")
            os.makedirs(src_dir)
            
            # Human-readable file
            with open(os.path.join(src_dir, "app.py"), "w") as f:
                f.write("def hello():\n    print('Hello World')\n")
            
            # Auto-generated file (should be excluded)
            with open(os.path.join(tmpdir, "package-lock.json"), "w") as f:
                f.write('{"name": "test", "lockfileVersion": 2}')
            
            # Human-readable content file
            with open(os.path.join(tmpdir, "README.md"), "w") as f:
                f.write("# My Project\n\nThis is a test project.")
            
            filter_service = HumanFileFilter()
            
            # Test the new method
            contents = filter_service.get_human_readable_contents(
                tmpdir,
                file_extensions=[".py", ".md"]
            )
            
            # Should include app.py and README.md content
            self.assertIn("app.py", contents)
            self.assertIn("README.md", contents)
            self.assertIn("def hello()", contents)
            self.assertIn("# My Project", contents)
            
            # Should NOT include package-lock.json
            self.assertNotIn("lockfileVersion", contents)
    
    def test_content_extraction_respects_token_limit(self):
        """
        Test that content extraction respects a maximum character limit.
        """
        import tempfile
        import os
        from app.services.human_file_filter import HumanFileFilter
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a large file
            with open(os.path.join(tmpdir, "large.py"), "w") as f:
                f.write("x = 1\n" * 10000)  # Large file
            
            filter_service = HumanFileFilter()
            
            # Extract with a limit
            contents = filter_service.get_human_readable_contents(
                tmpdir,
                file_extensions=[".py"],
                max_chars=1000
            )
            
            # Content should be truncated
            self.assertLessEqual(len(contents), 1500)  # Allow some overhead for file headers
    
    def test_content_excludes_lock_files(self):
        """
        Test that lock files are excluded from content extraction.
        """
        import tempfile
        import os
        from app.services.human_file_filter import HumanFileFilter
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create various lock files
            lock_files = ["package-lock.json", "yarn.lock", "poetry.lock", "Pipfile.lock"]
            for lock_file in lock_files:
                with open(os.path.join(tmpdir, lock_file), "w") as f:
                    f.write(f"content of {lock_file}")
            
            # Create a human file
            with open(os.path.join(tmpdir, "app.js"), "w") as f:
                f.write("console.log('hello');")
            
            filter_service = HumanFileFilter()
            contents = filter_service.get_human_readable_contents(
                tmpdir,
                file_extensions=[".js", ".json", ".lock", ".yaml"]
            )
            
            # Should include app.js
            self.assertIn("console.log", contents)
            
            # Should NOT include any lock file content
            for lock_file in lock_files:
                self.assertNotIn(f"content of {lock_file}", contents)


if __name__ == "__main__":
    unittest.main()
