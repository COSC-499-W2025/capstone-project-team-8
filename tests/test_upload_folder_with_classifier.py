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
        self.assertIn("project_classifications", data)
        
        # Check individual file analysis
        self.assertGreaterEqual(len(data["results"]), 7)
        types = {item.get("type") for item in data["results"]}
        self.assertIn("code", types)
        self.assertIn("content", types)
        
        # Check project classifications
        project_classifications = data["project_classifications"]
        self.assertIn("overall", project_classifications)
        
        overall_class = project_classifications["overall"]
        self.assertIn("classification", overall_class)
        self.assertIn("confidence", overall_class)
        self.assertEqual(overall_class["classification"], "coding")
        self.assertGreater(overall_class["confidence"], 0)


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
        self.assertIn("project_classifications", data)
        
        project_classifications = data["project_classifications"]
        self.assertIn("overall", project_classifications)
        overall_class = project_classifications["overall"]
        # Should be mixed or one of the dominant types
        self.assertIn(overall_class["classification"], ["coding", "mixed:coding+art", "mixed:art+coding"])
        self.assertGreater(overall_class["confidence"], 0)


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
        
        # Should also have the new project classifications
        self.assertIn("project_classifications", data)
        project_classifications = data["project_classifications"]
        self.assertIn("overall", project_classifications)
        overall_class = project_classifications["overall"]
        self.assertIn("classification", overall_class)
        self.assertIn("confidence", overall_class)

    def test_git_project_discovery_and_classification(self):
        """Test that Git projects are discovered and classified individually"""
        files = {
            # First Git project (Python)
            "project1/.git/HEAD": "ref: refs/heads/main",
            "project1/.git/config": "[core]\n\trepositoryformatversion = 0",
            "project1/main.py": "print('Hello from project 1')",
            "project1/requirements.txt": "django==4.0",
            "project1/README.md": "# Project 1",
            
            # Second Git project (JavaScript)
            "project2/.git/HEAD": "ref: refs/heads/main",
            "project2/.git/config": "[core]\n\trepositoryformatversion = 0",
            "project2/index.js": "console.log('Hello from project 2')",
            "project2/package.json": '{"name": "project2", "version": "1.0.0"}',
            "project2/README.md": "# Project 2",
            
            # Files outside any Git project
            "standalone.txt": "This is not in a Git project"
        }
        zip_bytes = self.make_zip_bytes(files)
        upload = SimpleUploadedFile("multi_git_project.zip", zip_bytes, content_type="application/zip")
        
        resp = self.client.post("/api/upload-folder/", {"file": upload})
        self.assertEqual(resp.status_code, 200)
        
        data = resp.json()
        self.assertIn("results", data)
        self.assertIn("project_classifications", data)
        
        # Check that files are tagged with project information
        results = data["results"]
        project1_files = [r for r in results if r.get("project_tag") == 1]
        project2_files = [r for r in results if r.get("project_tag") == 2]
        untagged_files = [r for r in results if "project_tag" not in r]
        
        # Should have files from both projects
        self.assertGreater(len(project1_files), 0)
        self.assertGreater(len(project2_files), 0)
        self.assertGreater(len(untagged_files), 0)  # standalone.txt
        
        # Check project classifications
        project_classifications = data["project_classifications"]
        self.assertIn("overall", project_classifications)
        self.assertIn("project_1", project_classifications)
        self.assertIn("project_2", project_classifications)
        
        # Project 1 should be classified as coding (Python)
        project1_class = project_classifications["project_1"]
        self.assertEqual(project1_class["classification"], "coding")
        self.assertIn("project_root", project1_class)
        self.assertEqual(project1_class["project_tag"], 1)
        
        # Project 2 should be classified as coding (JavaScript)
        project2_class = project_classifications["project_2"]
        self.assertEqual(project2_class["classification"], "coding")
        self.assertIn("project_root", project2_class)
        self.assertEqual(project2_class["project_tag"], 2)
