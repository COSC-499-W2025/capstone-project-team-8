import os
import sys
import tempfile
import zipfile
from pathlib import Path
from django.test import TestCase
from unittest.mock import patch, MagicMock

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
import django
django.setup()

from app.services.classifiers.project_classifier import (
    classify_project,
)
from app.services.classifiers.feature_extractor import extract_project_features
from app.services.classifiers.scoring_classifier import simple_score_classify
from app.services.classifiers.file_type_registry import (
    CODE_EXTS,
    TEXT_EXTS,
    IMAGE_EXTS,
    FOLDER_HINTS
)


class ProjectClassifierTests(TestCase):
    """Test suite for project classification functionality"""

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
        
        # Create folders if specified
        if folders:
            for folder in folders:
                (root_path / folder).mkdir(parents=True, exist_ok=True)
        
        # Create files
        for file_path, content in files_dict.items():
            full_path = root_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            if isinstance(content, str):
                full_path.write_text(content)
            else:
                full_path.write_bytes(content)
        
        return root_path

    def test_extract_project_features_basic(self):
        """Test basic feature extraction from a project"""
        files = {
            "main.py": "print('hello')",
            "utils.py": "def helper(): pass",
            "README.md": "# Project",
            "image.png": b"fake_png_data",
            "config.json": '{"key": "value"}'
        }
        project_path = self.create_test_project(files)
        
        features = extract_project_features(project_path)
        
        self.assertEqual(features['total_files'], 5)
        self.assertEqual(features['code_count'], 3)  # .py, .py, .json
        self.assertEqual(features['text_count'], 1)  # .md
        self.assertEqual(features['image_count'], 1)  # .png
        self.assertIn('.py', features['ext_counts'])
        self.assertIn('.md', features['ext_counts'])
        self.assertIn('.png', features['ext_counts'])

    def test_extract_project_features_with_folders(self):
        """Test feature extraction with folder structure"""
        files = {
            "src/main.py": "print('hello')",
            "docs/README.md": "# Documentation",
            "images/logo.png": b"fake_png_data",
            "tests/test.py": "def test(): pass"
        }
        folders = ["src", "docs", "images", "tests"]
        project_path = self.create_test_project(files, folders)
        
        features = extract_project_features(project_path)
        
        self.assertEqual(features['total_files'], 4)
        self.assertEqual(features['code_count'], 2)  # .py files
        self.assertEqual(features['text_count'], 1)  # .md
        self.assertEqual(features['image_count'], 1)  # .png
        
        # Check folder names are captured
        folder_names = set(features['folder_names'].keys())
        self.assertIn('src', folder_names)
        self.assertIn('docs', folder_names)
        self.assertIn('images', folder_names)
        self.assertIn('tests', folder_names)

    def test_simple_score_classify_coding_project(self):
        """Test classification of a coding project"""
        files = {
            "main.py": "print('hello')",
            "utils.py": "def helper(): pass",
            "requirements.txt": "django==4.0",
            "README.md": "# My Project",
            "src/__init__.py": "",
            "src/models.py": "class Model: pass"
        }
        folders = ["src"]
        project_path = self.create_test_project(files, folders)
        
        result = simple_score_classify(project_path)
        
        self.assertEqual(result, "coding")


    def test_simple_score_classify_mixed_project(self):
        """Test classification of a mixed project"""
        files = {
            "main.py": "print('hello')",
            "analysis.py": "import pandas",
            "paper.docx": "Research paper",
            "figures/plot1.png": b"fake_png_data",
            "figures/plot2.jpg": b"fake_jpg_data",
            "README.md": "# Data Analysis Project"
        }
        folders = ["figures"]
        project_path = self.create_test_project(files, folders)
        
        result = simple_score_classify(project_path)
        
        # Should return mixed since both coding and art have significant presence
        self.assertTrue(result.startswith("mixed:"))

    def test_simple_score_classify_small_project(self):
        """Test classification of a very small project (should return unknown)"""
        files = {
            "single.py": "print('hello')"
        }
        project_path = self.create_test_project(files)
        
        result = simple_score_classify(project_path, min_files_for_confident=3)
        
        self.assertEqual(result, "unknown")

    def test_classify_project_integration(self):
        """Test the main classify_project function integration"""
        files = {
            "main.py": "print('hello')",
            "utils.py": "def helper(): pass",
            "README.md": "# Project",
            "src/__init__.py": ""
        }
        folders = ["src"]
        project_path = self.create_test_project(files, folders)
        
        result = classify_project(project_path)
        
        self.assertIsInstance(result, dict)
        self.assertIn('classification', result)
        self.assertIn('confidence', result)
        self.assertIn('features', result)
        self.assertEqual(result['classification'], 'coding')
        self.assertGreater(result['confidence'], 0)


class ClassifierMetadataIntegrationTests(TestCase):
    """
    Integration tests for language and framework detection with project classification.
    
    Note: Detailed language and framework detection tests are in test_project_metadata.py.
    These tests only verify proper integration with the classify_project() function.
    """

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
        
        # Create folders if specified
        if folders:
            for folder in folders:
                (root_path / folder).mkdir(parents=True, exist_ok=True)
        
        # Create files
        for file_path, content in files_dict.items():
            full_path = root_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            if isinstance(content, str):
                full_path.write_text(content)
            else:
                full_path.write_bytes(content)
        
        return root_path

    def test_classify_project_includes_languages(self):
        """Test that classify_project includes languages for coding projects"""
        files = {
            "main.py": "print('hello')",
            "utils.py": "def helper(): pass",
            "requirements.txt": "Django==4.0.0"
        }
        project_path = self.create_test_project(files)
        
        result = classify_project(project_path)
        
        self.assertIn('languages', result)
        self.assertIsInstance(result['languages'], list)
        self.assertIn('Python', result['languages'])

    def test_classify_project_includes_frameworks(self):
        """Test that classify_project includes frameworks for coding projects"""
        files = {
            "main.py": "print('hello')",
            "manage.py": "#!/usr/bin/env python",
            "requirements.txt": "Django==4.0.0"
        }
        project_path = self.create_test_project(files)
        
        result = classify_project(project_path)
        
        self.assertIn('frameworks', result)
        self.assertIsInstance(result['frameworks'], list)
        self.assertIn('Django', result['frameworks'])

    def test_classify_non_coding_project_no_languages(self):
        """Test that non-coding projects don't include languages/frameworks"""
        files = {
            "document.txt": "Some text",
            "paper.pdf": b"fake_pdf_data",
            "essay.doc": b"fake_doc_data"
        }
        project_path = self.create_test_project(files)
        
        result = classify_project(project_path)
        
        # Should not have languages/frameworks or they should be empty
        if 'languages' in result:
            self.assertEqual(len(result['languages']), 0)
        if 'frameworks' in result:
            self.assertEqual(len(result['frameworks']), 0)

    def test_classify_fullstack_project(self):
        """Test classification of a full-stack project with multiple languages and frameworks"""
        files = {
            "backend/main.py": "print('hello')",
            "backend/requirements.txt": "Django==4.0.0\ndjango-rest-framework==3.13.0",
            "backend/manage.py": "#!/usr/bin/env python",
            "frontend/src/App.jsx": "import React from 'react';",
            "frontend/package.json": '{"dependencies": {"react": "^18.0.0", "next": "^12.0.0"}}'
        }
        folders = ["backend", "frontend", "frontend/src"]
        project_path = self.create_test_project(files, folders)
        
        result = classify_project(project_path)
        
        self.assertEqual(result['classification'], 'coding')
        self.assertIn('languages', result)
        self.assertIn('frameworks', result)
        self.assertIn('Python', result['languages'])
        self.assertIn('JavaScript', result['languages'])
        self.assertIn('Django', result['frameworks'])
        self.assertIn('React', result['frameworks'])