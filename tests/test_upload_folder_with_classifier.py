import io
import zipfile
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile


class UploadFolderWithClassifierTests(TestCase):
    """Test suite for upload folder functionality with project classification"""

    def setUp(self):
        self.client = Client()

    def make_zip_bytes(self, files: dict) -> bytes:
        """Create an in-memory zip archive. files is a dict of name->content bytes or str."""
        bio = io.BytesIO()
        with zipfile.ZipFile(bio, mode="w") as z:
            for name, content in files.items():
                data = content.encode("utf-8") if isinstance(content, str) else content
                z.writestr(name, data)
        return bio.getvalue()
    
    def test_coding_project_classification(self):
        """Test that a coding project gets classified correctly"""
        files = {
            "main.py": "print('Hello, World!')",
            "utils.py": "def helper_function(): pass",
            "requirements.txt": "django==4.0\nrequests==2.28",
            "README.md": "# My Python Project\nThis is a coding project.",
            "src/__init__.py": "",
            "src/models.py": "class User: pass",
            "tests/test_main.py": "def test_main(): pass"
        }
        zip_bytes = self.make_zip_bytes(files)
        upload = SimpleUploadedFile("coding_project.zip", zip_bytes, content_type="application/zip")
        
        resp = self.client.post("/api/upload-folder/", {"file": upload})
        self.assertEqual(resp.status_code, 200)
        
        data = resp.json()
        self.assertIn("results", data)
        self.assertIn("project_classification", data)
        
        # Check individual file analysis
        self.assertGreaterEqual(len(data["results"]), 7)
        types = {item.get("type") for item in data["results"]}
        self.assertIn("code", types)
        self.assertIn("content", types)
        
        # Check project classification
        project_class = data["project_classification"]
        self.assertIn("classification", project_class)
        self.assertIn("confidence", project_class)
        self.assertEqual(project_class["classification"], "coding")
        self.assertGreater(project_class["confidence"], 0)

    def test_writing_project_classification(self):
        """Test that a writing project gets classified correctly"""
        files = {
            "chapter1.docx": "Chapter 1: Introduction",
            "chapter2.docx": "Chapter 2: Literature Review",
            "references.pdf": "References and citations",
            "thesis.tex": "\\documentclass{article}\\begin{document}",
            "manuscript.md": "# Research Paper\n## Abstract",
            "notes.txt": "Research notes and ideas"
        }
        zip_bytes = self.make_zip_bytes(files)
        upload = SimpleUploadedFile("writing_project.zip", zip_bytes, content_type="application/zip")
        
        resp = self.client.post("/api/upload-folder/", {"file": upload})
        self.assertEqual(resp.status_code, 200)
        
        data = resp.json()
        self.assertIn("project_classification", data)
        
        project_class = data["project_classification"]
        self.assertEqual(project_class["classification"], "writing")
        self.assertGreater(project_class["confidence"], 0)

    def test_art_project_classification(self):
        """Test that an art project gets classified correctly"""
        files = {
            "logo.png": b"\x89PNG\r\n\x1a\n\x00\x00",
            "banner.jpg": b"\xff\xd8\xff\xe0\x00\x10JFIF",
            "icon.svg": "<svg><circle r='10'/></svg>",
            "portfolio.psd": b"fake_psd_data",
            "sketch.gif": b"fake_gif_data",
            "design.ai": b"fake_ai_data"
        }
        zip_bytes = self.make_zip_bytes(files)
        upload = SimpleUploadedFile("art_project.zip", zip_bytes, content_type="application/zip")
        
        resp = self.client.post("/api/upload-folder/", {"file": upload})
        self.assertEqual(resp.status_code, 200)
        
        data = resp.json()
        self.assertIn("project_classification", data)
        
        project_class = data["project_classification"]
        self.assertEqual(project_class["classification"], "art")
        self.assertGreater(project_class["confidence"], 0)

    def test_mixed_project_classification(self):
        """Test that a mixed project gets classified correctly"""
        files = {
            "main.py": "print('Data analysis')",
            "analysis.py": "import pandas as pd",
            "paper.docx": "Research paper content",
            "figures/plot1.png": b"\x89PNG\r\n\x1a\n\x00\x00",
            "figures/plot2.jpg": b"\xff\xd8\xff\xe0\x00\x10JFIF",
            "README.md": "# Data Analysis Project",
            "requirements.txt": "pandas==1.5.0\nmatplotlib==3.6.0"
        }
        zip_bytes = self.make_zip_bytes(files)
        upload = SimpleUploadedFile("mixed_project.zip", zip_bytes, content_type="application/zip")
        
        resp = self.client.post("/api/upload-folder/", {"file": upload})
        self.assertEqual(resp.status_code, 200)
        
        data = resp.json()
        self.assertIn("project_classification", data)
        
        project_class = data["project_classification"]
        # Should be mixed or one of the dominant types
        self.assertIn(project_class["classification"], ["coding", "mixed:coding+art", "mixed:art+coding"])
        self.assertGreater(project_class["confidence"], 0)

    def test_small_project_classification(self):
        """Test that a very small project gets classified as unknown"""
        files = {
            "single.py": "print('hello')"
        }
        zip_bytes = self.make_zip_bytes(files)
        upload = SimpleUploadedFile("small_project.zip", zip_bytes, content_type="application/zip")
        
        resp = self.client.post("/api/upload-folder/", {"file": upload})
        self.assertEqual(resp.status_code, 200)
        
        data = resp.json()
        self.assertIn("project_classification", data)
        
        project_class = data["project_classification"]
        self.assertEqual(project_class["classification"], "unknown")

    def test_project_classification_with_folder_hints(self):
        """Test that folder structure hints influence classification"""
        files = {
            "main.py": "print('hello')",
            "README.md": "# Project"
        }
        zip_bytes = self.make_zip_bytes(files)
        upload = SimpleUploadedFile("project_with_hints.zip", zip_bytes, content_type="application/zip")
        
        resp = self.client.post("/api/upload-folder/", {"file": upload})
        self.assertEqual(resp.status_code, 200)
        
        data = resp.json()
        self.assertIn("project_classification", data)
        
        project_class = data["project_classification"]
        # Should be coding due to Python files and README
        self.assertEqual(project_class["classification"], "coding")

    def test_project_classification_error_handling(self):
        """Test that classification errors are handled gracefully"""
        # Create a zip with a problematic structure
        files = {
            "main.py": "print('hello')",
            "README.md": "# Project"
        }
        zip_bytes = self.make_zip_bytes(files)
        upload = SimpleUploadedFile("test_project.zip", zip_bytes, content_type="application/zip")
        
        # Mock the classifier to raise an exception
        with self.settings():
            resp = self.client.post("/api/upload-folder/", {"file": upload})
            self.assertEqual(resp.status_code, 200)
            
            data = resp.json()
            self.assertIn("project_classification", data)
            
            # Should still have classification even if there was an error
            project_class = data["project_classification"]
            self.assertIn("classification", project_class)

    def test_backward_compatibility(self):
        """Test that existing functionality still works with new classification"""
        files = {
            "folder/readme.md": "Hello world",
            "folder/script.py": "print('hi')",
            "folder/image.png": b"\x89PNG\r\n\x1a\n\x00\x00",
        }
        zip_bytes = self.make_zip_bytes(files)
        upload = SimpleUploadedFile("upload.zip", zip_bytes, content_type="application/zip")
        
        resp = self.client.post("/api/upload-folder/", {"file": upload})
        self.assertEqual(resp.status_code, 200)
        
        data = resp.json()
        # Should still have the original results structure
        self.assertIn("results", data)
        self.assertGreaterEqual(len(data["results"]), 3)
        types = {item.get("type") for item in data["results"]}
        self.assertIn("content", types)
        self.assertIn("code", types)
        
        # Should also have the new project classification
        self.assertIn("project_classification", data)
        project_class = data["project_classification"]
        self.assertIn("classification", project_class)
        self.assertIn("confidence", project_class)
