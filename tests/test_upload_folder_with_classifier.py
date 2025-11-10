import io
import zipfile
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model


class UploadFolderWithClassifierTests(TestCase):
    """Test suite for upload folder functionality with project classification"""

    def setUp(self):
        self.client = Client()
        # create and authenticate user (some UserManagers require email)
        User = get_user_model()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="pass")
        self.client.force_login(self.user)
        # ensure upload-folder posts include consent_scan unless explicitly testing opt-out
        original_post = self.client.post
        def _post(path, data=None, *args, **kwargs):
            data = data or {}
            if path == "/api/upload-folder/" and "consent_scan" not in data:
                data = {**data, "consent_scan": "1"}
            return original_post(path, data, *args, **kwargs)
        self.client.post = _post

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
        # Check new structure
        self.assertIn("source", data)
        self.assertIn("projects", data)
        self.assertIn("overall", data)
        
        # Check overall classification
        overall = data["overall"]
        self.assertIn("classification", overall)
        self.assertIn("confidence", overall)
        self.assertEqual(overall["classification"], "coding")
        self.assertGreater(overall["confidence"], 0)
        
        # Check file totals
        self.assertGreaterEqual(overall["totals"]["files"], 7)
        self.assertGreater(overall["totals"]["code_files"], 0)
        self.assertGreater(overall["totals"]["text_files"], 0)


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
        self.assertIn("overall", data)
        
        overall = data["overall"]
        # Should be mixed or one of the dominant types
        self.assertIn(overall["classification"], ["coding", "mixed:coding+art", "mixed:art+coding"])
        self.assertGreater(overall["confidence"], 0)


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
        # Check new structure
        self.assertIn("source", data)
        self.assertIn("projects", data)
        self.assertIn("overall", data)
        
        # Check overall statistics
        overall = data["overall"]
        self.assertIn("classification", overall)
        self.assertIn("confidence", overall)
        self.assertGreaterEqual(overall["totals"]["files"], 3)

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
        self.assertIn("projects", data)
        
        # Should have 3 projects: 2 Git repos + 1 non-git-files (for standalone.txt)
        self.assertEqual(len(data["projects"]), 3)
        
        # Find the Git projects (exclude non-git-files project with id=0)
        git_projects = [p for p in data["projects"] if p["id"] != 0]
        self.assertEqual(len(git_projects), 2, "Should have 2 Git projects")
        
        # Find the projects
        project1 = None
        project2 = None
        for project in git_projects:
            if project["root"] == "project1":
                project1 = project
            elif project["root"] == "project2":
                project2 = project
        
        # Both projects should exist
        self.assertIsNotNone(project1)
        self.assertIsNotNone(project2)
        
        # Project 1 should be classified as coding (Python)
        self.assertEqual(project1["classification"]["type"], "coding")
        self.assertIn("confidence", project1["classification"])
        
        # Project 2 should be classified as coding (JavaScript)
        self.assertEqual(project2["classification"]["type"], "coding")
        self.assertIn("confidence", project2["classification"])
        
        # Each project should have files
        self.assertGreater(len(project1["files"]["code"]) + len(project1["files"]["content"]), 0)
        self.assertGreater(len(project2["files"]["code"]) + len(project2["files"]["content"]), 0)

    def test_api_response_includes_languages_and_frameworks(self):
        """Test that the API response includes languages and frameworks for coding projects"""
        files = {
            "main.py": "from django.http import HttpResponse",
            "app.py": "from flask import Flask",
            "requirements.txt": "django==4.0\nflask==2.0\npandas==1.5.0",
            "package.json": '{"dependencies": {"react": "^18.0.0", "express": "^4.17.0"}}',
            "src/App.jsx": "import React from 'react';",
            "server.js": "const express = require('express');"
        }
        zip_bytes = self.make_zip_bytes(files)
        upload = SimpleUploadedFile("fullstack_project.zip", zip_bytes, content_type="application/zip")
        
        resp = self.client.post("/api/upload-folder/", {"file": upload})
        self.assertEqual(resp.status_code, 200)
        
        data = resp.json()
        overall = data["overall"]
        
        # Check that overall includes languages
        self.assertIn("languages", overall, "Overall should include languages field")
        self.assertIsInstance(overall["languages"], list)
        self.assertIn("Python", overall["languages"])
        self.assertIn("JavaScript", overall["languages"])
        
        # Check that overall includes frameworks
        self.assertIn("frameworks", overall, "Overall should include frameworks field")
        self.assertIsInstance(overall["frameworks"], list)
        # Should detect frameworks from both requirements.txt and package.json
        self.assertIn("Django", overall["frameworks"])
        self.assertIn("Flask", overall["frameworks"])
        self.assertIn("React", overall["frameworks"])
        self.assertIn("Express", overall["frameworks"])

    def test_non_coding_project_no_languages_frameworks(self):
        """Test that non-coding projects don't have languages/frameworks or they're empty"""
        files = {
            "document.txt": "This is a text document",
            "paper.pdf": b"%PDF-1.4 fake pdf content",
            "image.png": b"\x89PNG\r\n\x1a\n\x00\x00"
        }
        zip_bytes = self.make_zip_bytes(files)
        upload = SimpleUploadedFile("documents.zip", zip_bytes, content_type="application/zip")
        
        resp = self.client.post("/api/upload-folder/", {"file": upload})
        self.assertEqual(resp.status_code, 200)
        
        data = resp.json()
        overall = data["overall"]
        
        # Non-coding projects should either not have languages/frameworks or they should be empty
        if "languages" in overall:
            self.assertEqual(len(overall["languages"]), 0)
        if "frameworks" in overall:
            self.assertEqual(len(overall["frameworks"]), 0)

    def test_git_project_languages_and_frameworks(self):
        """Test that individual Git projects include their own languages and frameworks"""
        files = {
            # Python project with Django
            "backend/.git/HEAD": "ref: refs/heads/main",
            "backend/.git/config": "[core]\n\trepositoryformatversion = 0",
            "backend/main.py": "from django.http import HttpResponse",
            "backend/requirements.txt": "django==4.0\ndjango-rest-framework==3.13.0",
            
            # JavaScript project with React
            "frontend/.git/HEAD": "ref: refs/heads/main",
            "frontend/.git/config": "[core]\n\trepositoryformatversion = 0",
            "frontend/src/App.jsx": "import React from 'react';",
            "frontend/package.json": '{"dependencies": {"react": "^18.0.0", "next": "^12.0.0"}}'
        }
        zip_bytes = self.make_zip_bytes(files)
        upload = SimpleUploadedFile("monorepo.zip", zip_bytes, content_type="application/zip")
        
        resp = self.client.post("/api/upload-folder/", {"file": upload})
        self.assertEqual(resp.status_code, 200)
        
        data = resp.json()
        projects = data["projects"]
        
        # Find backend and frontend projects
        backend_project = next((p for p in projects if "backend" in p["root"]), None)
        frontend_project = next((p for p in projects if "frontend" in p["root"]), None)
        
        self.assertIsNotNone(backend_project)
        self.assertIsNotNone(frontend_project)
        
        # Backend should have Python and Django
        backend_class = backend_project["classification"]
        self.assertIn("languages", backend_class)
        self.assertIn("Python", backend_class["languages"])
        self.assertIn("frameworks", backend_class)
        self.assertIn("Django", backend_class["frameworks"])
        
        # Frontend should have JavaScript and React/Next.js
        frontend_class = frontend_project["classification"]
        self.assertIn("languages", frontend_class)
        self.assertIn("JavaScript", frontend_class["languages"])
        self.assertIn("frameworks", frontend_class)
        self.assertIn("React", frontend_class["frameworks"])
        self.assertIn("Next.js", frontend_class["frameworks"])