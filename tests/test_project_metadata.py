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


class LanguageDetectionTests(TestCase):
    """Test suite for language detection in coding projects"""

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

    def test_detect_python_language(self):
        """Test detection of Python as the primary language"""
        files = {
            "main.py": "print('hello')",
            "utils.py": "def helper(): pass",
            "models.py": "class User: pass",
            "requirements.txt": "django==4.0"
        }
        project_path = self.create_test_project(files)
        
        languages = detect_languages(project_path)
        
        self.assertIsInstance(languages, list)
        self.assertIn('Python', languages)
        self.assertEqual(languages[0], 'Python')  # Should be primary language

    def test_detect_javascript_language(self):
        """Test detection of JavaScript as the primary language"""
        files = {
            "index.js": "console.log('hello');",
            "app.js": "const express = require('express');",
            "utils.js": "function helper() {}",
            "package.json": '{"name": "test", "dependencies": {}}'
        }
        project_path = self.create_test_project(files)
        
        languages = detect_languages(project_path)
        
        self.assertIsInstance(languages, list)
        self.assertIn('JavaScript', languages)
        self.assertEqual(languages[0], 'JavaScript')

    def test_detect_typescript_language(self):
        """Test detection of TypeScript as the primary language"""
        files = {
            "index.ts": "const greeting: string = 'hello';",
            "app.tsx": "import React from 'react';",
            "types.ts": "interface User { name: string; }",
            "package.json": '{"name": "test", "dependencies": {"typescript": "^4.0.0"}}'
        }
        project_path = self.create_test_project(files)
        
        languages = detect_languages(project_path)
        
        self.assertIsInstance(languages, list)
        self.assertIn('TypeScript', languages)
        self.assertEqual(languages[0], 'TypeScript')

    def test_detect_java_language(self):
        """Test detection of Java as the primary language"""
        files = {
            "Main.java": "public class Main { }",
            "User.java": "public class User { }",
            "pom.xml": "<project></project>"
        }
        project_path = self.create_test_project(files)
        
        languages = detect_languages(project_path)
        
        self.assertIsInstance(languages, list)
        self.assertIn('Java', languages)
        self.assertEqual(languages[0], 'Java')

    def test_detect_cpp_language(self):
        """Test detection of C++ as the primary language"""
        files = {
            "main.cpp": "#include <iostream>",
            "utils.cpp": "void helper() {}",
            "header.hpp": "class MyClass { };"
        }
        project_path = self.create_test_project(files)
        
        languages = detect_languages(project_path)
        
        self.assertIsInstance(languages, list)
        self.assertIn('C++', languages)

    def test_detect_c_language(self):
        """Test detection of C as the primary language"""
        files = {
            "main.c": "#include <stdio.h>",
            "utils.c": "void helper() {}",
            "header.h": "void function();"
        }
        project_path = self.create_test_project(files)
        
        languages = detect_languages(project_path)
        
        self.assertIsInstance(languages, list)
        self.assertIn('C', languages)

    def test_detect_multiple_languages(self):
        """Test detection of multiple languages in a project"""
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
        
        self.assertIsInstance(languages, list)
        self.assertGreater(len(languages), 1)
        self.assertIn('Python', languages)
        self.assertIn('JavaScript', languages)
        self.assertIn('HTML', languages)
        self.assertIn('CSS', languages)

    def test_detect_languages_with_percentages(self):
        """Test that language detection prioritizes by file count"""
        files = {
            "main.py": "print('hello')",
            "utils.py": "def helper(): pass",
            "models.py": "class User: pass",
            "script.js": "console.log('test');"
        }
        project_path = self.create_test_project(files)
        
        languages = detect_languages(project_path)
        
        # Should return Python first (75% of code files) and JavaScript second (25%)
        self.assertIsInstance(languages, list)
        self.assertEqual(languages[0], 'Python')
        self.assertIn('JavaScript', languages)

    def test_detect_go_language(self):
        """Test detection of Go language"""
        files = {
            "main.go": "package main",
            "utils.go": "func helper() {}",
            "go.mod": "module example.com/test"
        }
        project_path = self.create_test_project(files)
        
        languages = detect_languages(project_path)
        
        self.assertIsInstance(languages, list)
        self.assertIn('Go', languages)

    def test_detect_rust_language(self):
        """Test detection of Rust language"""
        files = {
            "main.rs": "fn main() {}",
            "lib.rs": "pub fn helper() {}",
            "Cargo.toml": "[package]"
        }
        project_path = self.create_test_project(files)
        
        languages = detect_languages(project_path)
        
        self.assertIsInstance(languages, list)
        self.assertIn('Rust', languages)

    def test_detect_languages_empty_project(self):
        """Test language detection on empty project returns empty list"""
        project_path = self.create_test_project({})
        
        languages = detect_languages(project_path)
        
        self.assertIsInstance(languages, list)
        self.assertEqual(len(languages), 0)

    def test_detect_languages_non_coding_project(self):
        """Test language detection on non-coding project returns empty list"""
        files = {
            "document.txt": "Some text",
            "paper.pdf": b"fake_pdf_data",
            "image.png": b"fake_png_data"
        }
        project_path = self.create_test_project(files)
        
        languages = detect_languages(project_path)
        
        self.assertIsInstance(languages, list)
        self.assertEqual(len(languages), 0)


class FrameworkDetectionTests(TestCase):
    """Test suite for framework detection in coding projects"""

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

    def test_detect_django_framework(self):
        """Test detection of Django framework"""
        files = {
            "manage.py": "#!/usr/bin/env python",
            "settings.py": "INSTALLED_APPS = []",
            "requirements.txt": "Django==4.0.0\npsycopg2==2.9.0"
        }
        project_path = self.create_test_project(files)
        
        frameworks = detect_frameworks(project_path)
        
        self.assertIsInstance(frameworks, list)
        self.assertIn('Django', frameworks)

    def test_detect_flask_framework(self):
        """Test detection of Flask framework"""
        files = {
            "app.py": "from flask import Flask",
            "requirements.txt": "Flask==2.0.0\nFlask-SQLAlchemy==2.5.0"
        }
        project_path = self.create_test_project(files)
        
        frameworks = detect_frameworks(project_path)
        
        self.assertIsInstance(frameworks, list)
        self.assertIn('Flask', frameworks)

    def test_detect_fastapi_framework(self):
        """Test detection of FastAPI framework"""
        files = {
            "main.py": "from fastapi import FastAPI",
            "requirements.txt": "fastapi==0.68.0\nuvicorn==0.15.0"
        }
        project_path = self.create_test_project(files)
        
        frameworks = detect_frameworks(project_path)
        
        self.assertIsInstance(frameworks, list)
        self.assertIn('FastAPI', frameworks)

    def test_detect_react_framework(self):
        """Test detection of React framework"""
        files = {
            "package.json": '{"dependencies": {"react": "^18.0.0", "react-dom": "^18.0.0"}}',
            "src/App.jsx": "import React from 'react';"
        }
        folders = ["src"]
        project_path = self.create_test_project(files, folders)
        
        frameworks = detect_frameworks(project_path)
        
        self.assertIsInstance(frameworks, list)
        self.assertIn('React', frameworks)

    def test_detect_vue_framework(self):
        """Test detection of Vue framework"""
        files = {
            "package.json": '{"dependencies": {"vue": "^3.0.0"}}',
            "src/App.vue": "<template><div></div></template>"
        }
        folders = ["src"]
        project_path = self.create_test_project(files, folders)
        
        frameworks = detect_frameworks(project_path)
        
        self.assertIsInstance(frameworks, list)
        self.assertIn('Vue', frameworks)

    def test_detect_angular_framework(self):
        """Test detection of Angular framework"""
        files = {
            "package.json": '{"dependencies": {"@angular/core": "^13.0.0"}}',
            "angular.json": '{"version": 1}'
        }
        project_path = self.create_test_project(files)
        
        frameworks = detect_frameworks(project_path)
        
        self.assertIsInstance(frameworks, list)
        self.assertIn('Angular', frameworks)

    def test_detect_express_framework(self):
        """Test detection of Express framework"""
        files = {
            "package.json": '{"dependencies": {"express": "^4.17.0"}}',
            "server.js": "const express = require('express');"
        }
        project_path = self.create_test_project(files)
        
        frameworks = detect_frameworks(project_path)
        
        self.assertIsInstance(frameworks, list)
        self.assertIn('Express', frameworks)

    def test_detect_nextjs_framework(self):
        """Test detection of Next.js framework"""
        files = {
            "package.json": '{"dependencies": {"next": "^12.0.0", "react": "^18.0.0"}}',
            "next.config.js": "module.exports = {}"
        }
        project_path = self.create_test_project(files)
        
        frameworks = detect_frameworks(project_path)
        
        self.assertIsInstance(frameworks, list)
        self.assertIn('Next.js', frameworks)

    def test_detect_spring_framework(self):
        """Test detection of Spring framework"""
        files = {
            "pom.xml": """<project>
                <dependencies>
                    <dependency>
                        <groupId>org.springframework.boot</groupId>
                        <artifactId>spring-boot-starter</artifactId>
                    </dependency>
                </dependencies>
            </project>"""
        }
        project_path = self.create_test_project(files)
        
        frameworks = detect_frameworks(project_path)
        
        self.assertIsInstance(frameworks, list)
        self.assertIn('Spring Boot', frameworks)

    def test_detect_laravel_framework(self):
        """Test detection of Laravel framework"""
        files = {
            "composer.json": '{"require": {"laravel/framework": "^9.0"}}',
            "artisan": "#!/usr/bin/env php"
        }
        project_path = self.create_test_project(files)
        
        frameworks = detect_frameworks(project_path)
        
        self.assertIsInstance(frameworks, list)
        self.assertIn('Laravel', frameworks)

    def test_detect_multiple_frameworks(self):
        """Test detection of multiple frameworks in a project"""
        files = {
            "backend/requirements.txt": "Django==4.0.0",
            "backend/manage.py": "#!/usr/bin/env python",
            "frontend/package.json": '{"dependencies": {"react": "^18.0.0"}}'
        }
        folders = ["backend", "frontend"]
        project_path = self.create_test_project(files, folders)
        
        frameworks = detect_frameworks(project_path)
        
        self.assertIsInstance(frameworks, list)
        self.assertGreater(len(frameworks), 1)
        self.assertIn('Django', frameworks)
        self.assertIn('React', frameworks)

    def test_detect_frameworks_empty_project(self):
        """Test framework detection on empty project returns empty list"""
        project_path = self.create_test_project({})
        
        frameworks = detect_frameworks(project_path)
        
        self.assertIsInstance(frameworks, list)
        self.assertEqual(len(frameworks), 0)

    def test_detect_frameworks_no_dependencies(self):
        """Test framework detection when no frameworks are present"""
        files = {
            "main.py": "print('hello world')",
            "utils.py": "def helper(): pass"
        }
        project_path = self.create_test_project(files)
        
        frameworks = detect_frameworks(project_path)
        
        self.assertIsInstance(frameworks, list)
        self.assertEqual(len(frameworks), 0)

    def test_detect_tensorflow_framework(self):
        """Test detection of TensorFlow framework"""
        files = {
            "model.py": "import tensorflow as tf",
            "requirements.txt": "tensorflow==2.8.0"
        }
        project_path = self.create_test_project(files)
        
        frameworks = detect_frameworks(project_path)
        
        self.assertIsInstance(frameworks, list)
        self.assertIn('TensorFlow', frameworks)

    def test_detect_pytorch_framework(self):
        """Test detection of PyTorch framework"""
        files = {
            "model.py": "import torch",
            "requirements.txt": "torch==1.10.0"
        }
        project_path = self.create_test_project(files)
        
        frameworks = detect_frameworks(project_path)
        
        self.assertIsInstance(frameworks, list)
        self.assertIn('PyTorch', frameworks)

