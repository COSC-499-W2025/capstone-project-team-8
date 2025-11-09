import os
import sys
import tempfile
from pathlib import Path
from django.test import TestCase

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
import django
django.setup()

from app.services.project_metadata import detect_languages, detect_frameworks


class MetadataDetectionTests(TestCase):
    """Streamlined test suite for language and framework detection"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = None

    def tearDown(self):
        """Clean up test fixtures"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

    def create_test_project(self, files_dict, folders=None):
        """Helper to create a temporary project structure for testing"""
        self.temp_dir = tempfile.mkdtemp()
        root_path = Path(self.temp_dir)
        
        if folders:
            for folder in folders:
                (root_path / folder).mkdir(parents=True, exist_ok=True)
        
        for file_path, content in files_dict.items():
            full_path = root_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            if isinstance(content, str):
                full_path.write_text(content)
            else:
                full_path.write_bytes(content)
        
        return root_path

    # ==================== Language Detection Tests ====================

    def test_detect_single_language(self):
        """Test detection of a single language (Python as representative)"""
        files = {
            "main.py": "print('hello')",
            "utils.py": "def helper(): pass",
            "models.py": "class User: pass"
        }
        project_path = self.create_test_project(files)
        
        languages = detect_languages(project_path)
        
        self.assertIsInstance(languages, list)
        self.assertIn('Python', languages)
        self.assertEqual(languages[0], 'Python')

    def test_detect_multiple_languages(self):
        """Test detection of multiple languages in a full-stack project"""
        files = {
            "backend/main.py": "print('hello')",
            "backend/models.py": "class User: pass",
            "frontend/app.js": "console.log('hello');",
            "frontend/index.html": "<html></html>",
            "frontend/style.css": "body { margin: 0; }"
        }
        folders = ["backend", "frontend"]
        project_path = self.create_test_project(files, folders)
        
        languages = detect_languages(project_path)
        
        self.assertGreater(len(languages), 1)
        self.assertIn('Python', languages)
        self.assertIn('JavaScript', languages)
        self.assertIn('HTML', languages)
        self.assertIn('CSS', languages)

    def test_language_prioritization(self):
        """Test that languages are sorted by file count"""
        files = {
            "main.py": "print('hello')",
            "utils.py": "def helper(): pass",
            "models.py": "class User: pass",
            "script.js": "console.log('test');"
        }
        project_path = self.create_test_project(files)
        
        languages = detect_languages(project_path)
        
        # Python (75%) should be first, JavaScript (25%) second
        self.assertEqual(languages[0], 'Python')
        self.assertIn('JavaScript', languages)

    def test_languages_empty_project(self):
        """Test language detection on empty project"""
        project_path = self.create_test_project({})
        
        languages = detect_languages(project_path)
        
        self.assertEqual(len(languages), 0)

    # ==================== Framework Detection Tests ====================

    def test_detect_python_frameworks(self):
        """Test detection of Python frameworks from requirements.txt"""
        files = {
            "main.py": "print('test')",
            "requirements.txt": "django==4.0\nflask==2.0\npandas==1.5.0"
        }
        project_path = self.create_test_project(files)
        
        frameworks = detect_frameworks(project_path)
        
        self.assertIn('Django', frameworks)
        self.assertIn('Flask', frameworks)
        self.assertIn('Pandas', frameworks)

    def test_detect_javascript_frameworks(self):
        """Test detection of JavaScript frameworks from package.json"""
        files = {
            "package.json": '''
            {
                "dependencies": {"react": "^18.0.0", "express": "^4.17.0"},
                "devDependencies": {"jest": "^29.0.0", "webpack": "^5.0.0"}
            }
            '''
        }
        project_path = self.create_test_project(files)
        
        frameworks = detect_frameworks(project_path)
        
        self.assertIn('React', frameworks)
        self.assertIn('Express', frameworks)
        self.assertIn('Jest', frameworks)
        self.assertIn('Webpack', frameworks)

    def test_detect_config_based_frameworks(self):
        """Test framework detection from config files (Next.js, Docker)"""
        files = {
            "index.js": "console.log('test');",
            "next.config.js": "module.exports = {}",
            "Dockerfile": "FROM node:18"
        }
        project_path = self.create_test_project(files)
        
        frameworks = detect_frameworks(project_path)
        
        self.assertIn('Next.js', frameworks)
        self.assertIn('Docker', frameworks)

    def test_frameworks_empty_project(self):
        """Test framework detection on empty project"""
        project_path = self.create_test_project({})
        
        frameworks = detect_frameworks(project_path)
        
        self.assertEqual(len(frameworks), 0)

    # ==================== Edge Cases ====================

    def test_malformed_dependency_files(self):
        """Test handling of malformed JSON in package.json"""
        files = {
            "index.js": "console.log('test');",
            "package.json": '{invalid json'
        }
        project_path = self.create_test_project(files)
        
        # Should not crash, just skip the malformed file
        frameworks = detect_frameworks(project_path)
        self.assertIsInstance(frameworks, list)

    def test_multiple_dependency_files(self):
        """Test project with multiple Python dependency files"""
        files = {
            "main.py": "print('test')",
            "requirements.txt": "django==4.0",
            "Pipfile": "[packages]\nflask = '*'"
        }
        project_path = self.create_test_project(files)
        
        frameworks = detect_frameworks(project_path)
        
        # Should detect from both files
        self.assertIn('Django', frameworks)
        self.assertIn('Flask', frameworks)

    def test_case_insensitive_detection(self):
        """Test case-insensitive framework detection"""
        files = {
            "main.py": "print('test')",
            "requirements.txt": "Django==4.0\nFLASK>=2.0"
        }
        project_path = self.create_test_project(files)
        
        frameworks = detect_frameworks(project_path)
        
        self.assertIn('Django', frameworks)
        self.assertIn('Flask', frameworks)

    def test_peer_dependencies(self):
        """Test that peerDependencies are detected"""
        files = {
            "package.json": '{"peerDependencies": {"react": "^18.0.0"}}'
        }
        project_path = self.create_test_project(files)
        
        frameworks = detect_frameworks(project_path)
        
        self.assertIn('React', frameworks)

    def test_ignore_special_directories(self):
        """Test that node_modules and venv are ignored"""
        files = {
            "src/index.js": "console.log('test');",
            "node_modules/react/index.js": "// React",
            "venv/lib/python3.9/site-packages/django/__init__.py": "# Django"
        }
        folders = ["src", "node_modules/react", "venv/lib/python3.9/site-packages/django"]
        project_path = self.create_test_project(files, folders)
        
        languages = detect_languages(project_path)
        frameworks = detect_frameworks(project_path)
        
        # Should only detect from src/, not from node_modules or venv
        self.assertEqual(languages.count('JavaScript'), 1)
        self.assertNotIn('Django', frameworks)

    def test_component_based_frameworks(self):
        """Test detection from component files (.vue, .svelte)"""
        files = {
            "App.vue": "<template><div>Test</div></template>",
            "Component.svelte": "<h1>Hello</h1>"
        }
        project_path = self.create_test_project(files)
        
        frameworks = detect_frameworks(project_path)
        
        self.assertIn('Vue', frameworks)
        self.assertIn('Svelte', frameworks)

    def test_multiple_competing_frameworks(self):
        """Test that all competing frameworks are detected"""
        files = {
            "main.py": "print('test')",
            "requirements.txt": "django==4.0\nflask==2.0\nfastapi==0.95"
        }
        project_path = self.create_test_project(files)
        
        frameworks = detect_frameworks(project_path)
        
        # All three should be detected, not just one
        self.assertIn('Django', frameworks)
        self.assertIn('Flask', frameworks)
        self.assertIn('FastAPI', frameworks)

    def test_requirements_with_comments(self):
        """Test that comments in requirements.txt are properly handled"""
        files = {
            "main.py": "print('test')",
            "requirements.txt": "# Web framework\ndjango==4.0\n# Testing\npytest>=7.0  # Unit tests"
        }
        project_path = self.create_test_project(files)
        
        frameworks = detect_frameworks(project_path)
        
        self.assertIn('Django', frameworks)
        self.assertIn('Pytest', frameworks)

    def test_empty_requirements_file(self):
        """Test handling of empty requirements.txt"""
        files = {
            "main.py": "print('test')",
            "requirements.txt": ""
        }
        project_path = self.create_test_project(files)
        
        frameworks = detect_frameworks(project_path)
        
        # Should not crash, just return empty or minimal results
        self.assertIsInstance(frameworks, list)

