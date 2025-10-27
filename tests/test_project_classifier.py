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

from app.services.project_classifier import (
    extract_project_features,
    simple_score_classify,
    classify_project,
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

    def test_simple_score_classify_writing_project(self):
        """Test classification of a writing/research project"""
        files = {
            "chapter1.docx": "Chapter 1 content",
            "chapter2.docx": "Chapter 2 content",
            "references.pdf": "References",
            "thesis.tex": "\\documentclass{article}",
            "manuscript.md": "# Research Paper"
        }
        folders = ["chapters", "references"]
        project_path = self.create_test_project(files, folders)
        
        result = simple_score_classify(project_path)
        
        self.assertEqual(result, "writing")

    def test_simple_score_classify_art_project(self):
        """Test classification of an art/design project"""
        files = {
            "logo.png": b"fake_png_data",
            "banner.jpg": b"fake_jpg_data",
            "icon.svg": "<svg></svg>",
            "portfolio.psd": b"fake_psd_data",
            "sketch.gif": b"fake_gif_data"
        }
        folders = ["images", "portfolio", "assets"]
        project_path = self.create_test_project(files, folders)
        
        result = simple_score_classify(project_path)
        
        self.assertEqual(result, "art")

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

    def test_simple_score_classify_with_folder_bonuses(self):
        """Test that folder name hints provide classification bonuses"""
        files = {
            "main.py": "print('hello')",
            "README.md": "# Project"
        }
        folders = ["src", "lib"]  # Strong coding hints
        project_path = self.create_test_project(files, folders)
        
        result = simple_score_classify(project_path)
        
        self.assertEqual(result, "coding")

    def test_simple_score_classify_writing_with_folder_hints(self):
        """Test writing project with folder hints"""
        files = {
            "document.docx": "Content",
            "notes.txt": "Notes"
        }
        folders = ["paper", "thesis", "chapters"]  # Strong writing hints
        project_path = self.create_test_project(files, folders)
        
        result = simple_score_classify(project_path)
        
        self.assertEqual(result, "writing")

    def test_simple_score_classify_art_with_folder_hints(self):
        """Test art project with folder hints"""
        files = {
            "image1.png": b"fake_png_data",
            "image2.jpg": b"fake_jpg_data"
        }
        folders = ["images", "portfolio", "art"]  # Strong art hints
        project_path = self.create_test_project(files, folders)
        
        result = simple_score_classify(project_path)
        
        self.assertEqual(result, "art")

    def test_simple_score_classify_custom_weights(self):
        """Test classification with custom weights"""
        files = {
            "main.py": "print('hello')",
            "image.png": b"fake_png_data",
            "doc.txt": "Documentation"
        }
        project_path = self.create_test_project(files)
        
        # Test with higher code weight
        result_high_code = simple_score_classify(
            project_path, 
            weights=(10.0, 1.0, 1.0)  # Much higher code weight
        )
        
        # Test with higher image weight
        result_high_image = simple_score_classify(
            project_path,
            weights=(1.0, 1.0, 10.0)  # Much higher image weight
        )
        
        self.assertEqual(result_high_code, "coding")
        self.assertEqual(result_high_image, "art")

    def test_simple_score_classify_margin_threshold(self):
        """Test the margin threshold for mixed classification"""
        files = {
            "main.py": "print('hello')",
            "utils.py": "def helper(): pass",
            "image1.png": b"fake_png_data",
            "image2.jpg": b"fake_jpg_data",
            "doc.txt": "Documentation"
        }
        project_path = self.create_test_project(files)
        
        # With default margin (0.25), should be coding (code files dominate)
        result_default = simple_score_classify(project_path)

        # With higher margin (3.0), should pick mixed
        result_high_margin = simple_score_classify(project_path, margin_threshold=5.0)

        self.assertEqual(result_default, "coding")
        # The high margin result should be a single category
        self.assertIn("mixed:", result_high_margin)

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

    def test_classify_project_with_zip_path(self):
        """Test classify_project with a zip file path"""
        # Create a zip file
        files = {
            "main.py": "print('hello')",
            "README.md": "# Project"
        }
        project_path = self.create_test_project(files)
        
        # Create zip file
        zip_path = project_path.parent / "test_project.zip"
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file_path in project_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(project_path)
                    zipf.write(file_path, arcname)
        
        result = classify_project(zip_path)
        
        self.assertIsInstance(result, dict)
        self.assertIn('classification', result)
        self.assertEqual(result['classification'], 'coding')

    def test_extension_sets_completeness(self):
        """Test that extension sets are comprehensive"""
        # Test that common extensions are included
        self.assertIn('.py', CODE_EXTS)
        self.assertIn('.js', CODE_EXTS)
        self.assertIn('.java', CODE_EXTS)
        self.assertIn('.cpp', CODE_EXTS)
        
        self.assertIn('.md', TEXT_EXTS)
        self.assertIn('.txt', TEXT_EXTS)
        self.assertIn('.pdf', TEXT_EXTS)
        self.assertIn('.docx', TEXT_EXTS)
        
        self.assertIn('.png', IMAGE_EXTS)
        self.assertIn('.jpg', IMAGE_EXTS)
        self.assertIn('.gif', IMAGE_EXTS)
        self.assertIn('.svg', IMAGE_EXTS)

    def test_folder_hints_completeness(self):
        """Test that folder hints are comprehensive"""
        # Test coding hints
        self.assertIn('src', FOLDER_HINTS['code'])
        self.assertIn('lib', FOLDER_HINTS['code'])
        self.assertIn('app', FOLDER_HINTS['code'])
        
        # Test writing hints
        self.assertIn('docs', FOLDER_HINTS['writing'])
        self.assertIn('paper', FOLDER_HINTS['writing'])
        self.assertIn('thesis', FOLDER_HINTS['writing'])
        
        # Test art hints
        self.assertIn('images', FOLDER_HINTS['art'])
        self.assertIn('assets', FOLDER_HINTS['art'])
        self.assertIn('portfolio', FOLDER_HINTS['art'])

    def test_edge_case_empty_project(self):
        """Test classification of empty project"""
        project_path = self.create_test_project({})
        
        result = simple_score_classify(project_path)
        
        self.assertEqual(result, "unknown")

    def test_edge_case_single_file_no_extension(self):
        """Test classification with file having no extension"""
        files = {
            "README": "# Project without extension"
        }
        project_path = self.create_test_project(files)
        
        result = simple_score_classify(project_path)
        
        # Should handle gracefully and return unknown for small project
        self.assertEqual(result, "unknown")

    def test_edge_case_very_deep_nesting(self):
        """Test classification with very deep folder nesting"""
        files = {
            "a/b/c/d/e/f/g/h/i/j/deep.py": "print('deep')",
            "a/b/c/d/e/f/g/h/i/j/README.md": "# Deep project"
        }
        project_path = self.create_test_project(files)
        
        features = extract_project_features(project_path)
        
        self.assertEqual(features['total_files'], 2)
        self.assertEqual(features['code_count'], 1)
        self.assertEqual(features['text_count'], 1)
        
        result = simple_score_classify(project_path)
        self.assertEqual(result, "coding")
