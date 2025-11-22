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

from app.services.analysis.analyzers import extract_skills


class SkillExtractionTests(TestCase):
    """Test suite for skill extraction functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = None

    def tearDown(self):
        """Clean up test fixtures"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

    def create_test_project(self, files_dict):
        """Helper to create a temporary project structure for testing"""
        self.temp_dir = tempfile.mkdtemp()
        root_path = Path(self.temp_dir)
        
        for file_path, content in files_dict.items():
            full_path = root_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        
        return root_path

    # ===== Common Use Cases =====

    def test_traditional_fullstack_java_html_css(self):
        """Test traditional full-stack: Java + HTML + CSS (JSP-style)"""
        project = self.create_test_project({
            'src/Main.java': 'public class Main { }',
            'web/index.html': '<html><body>Hello</body></html>',
            'web/style.css': 'body { color: blue; }'
        })
        
        skills = extract_skills(project)
        
        self.assertIn('Full-Stack Development', skills)
        self.assertIn('Web Design', skills)
        self.assertIn('Object-Oriented Programming', skills)
        self.assertNotIn('Backend Development', skills)  # Should only show Full-Stack
        self.assertNotIn('Frontend Development', skills)  # Should only show Full-Stack

    def test_modern_fullstack_django_react(self):
        """Test modern full-stack: Python + Django + TypeScript + React"""
        project = self.create_test_project({
            'backend/app.py': 'from django.db import models',
            'backend/requirements.txt': 'django==4.2.0\ndjango-rest-framework',
            'frontend/package.json': '{"dependencies": {"react": "^18.0.0", "typescript": "^5.0.0"}}',
            'frontend/App.tsx': 'export const App = () => <div>Hello</div>'
        })
        
        skills = extract_skills(project)
        
        self.assertIn('Full-Stack Development', skills)
        self.assertIn('RESTful APIs', skills)  # Django skill
        self.assertIn('Component-Based Architecture', skills)  # React skill
        self.assertNotIn('Django', skills)  # Framework name not in skills
        self.assertNotIn('React', skills)  # Framework name not in skills
        self.assertNotIn('Backend Development', skills)  # Should only show Full-Stack
        self.assertNotIn('Frontend Development', skills)  # Should only show Full-Stack

    def test_backend_only_python_flask(self):
        """Test backend-only project: Python + Flask API"""
        project = self.create_test_project({
            'app.py': 'from flask import Flask',
            'requirements.txt': 'flask==2.3.0',
            'models.py': 'class User: pass'
        })
        
        skills = extract_skills(project)
        
        self.assertIn('Backend Development', skills)
        self.assertIn('RESTful APIs', skills)  # Flask skill, not 'Flask' itself
        self.assertNotIn('Flask', skills)  # Framework name not in skills
        self.assertNotIn('Frontend Development', skills)
        self.assertNotIn('Full-Stack Development', skills)

    def test_frontend_only_react(self):
        """Test frontend-only project: TypeScript + React SPA"""
        project = self.create_test_project({
            'package.json': '{"dependencies": {"react": "^18.0.0", "react-dom": "^18.0.0"}}',
            'src/App.tsx': 'export const App = () => <div>Hello</div>',
            'src/index.tsx': 'import React from "react"'
        })
        
        skills = extract_skills(project)
        
        self.assertIn('Frontend Development', skills)
        self.assertIn('Component-Based Architecture', skills)  # React skill
        self.assertNotIn('React', skills)  # Framework name not in skills
        self.assertNotIn('Backend Development', skills)
        self.assertNotIn('Full-Stack Development', skills)

    def test_static_website_html_css(self):
        """Test static website: HTML + CSS only"""
        project = self.create_test_project({
            'index.html': '<html><body>Welcome</body></html>',
            'style.css': 'body { margin: 0; }',
            'about.html': '<html><body>About Us</body></html>'
        })
        
        skills = extract_skills(project)
        
        self.assertIn('Frontend Development', skills)
        self.assertIn('Web Design', skills)
        self.assertNotIn('Backend Development', skills)
        self.assertNotIn('Full-Stack Development', skills)

    # ===== Edge Cases =====

    def test_backend_language_without_frontend(self):
        """Test pure backend code without any frontend"""
        project = self.create_test_project({
            'main.py': 'def main(): pass',
            'utils.py': 'def helper(): pass'
        })
        
        skills = extract_skills(project)
        
        self.assertIn('Backend Development', skills)
        self.assertNotIn('Frontend Development', skills)
        self.assertNotIn('Full-Stack Development', skills)
        self.assertNotIn('Web Design', skills)

    def test_html_without_css_no_web_design(self):
        """Test HTML without CSS - should not show Web Design"""
        project = self.create_test_project({
            'index.html': '<html><body>No CSS here</body></html>'
        })
        
        skills = extract_skills(project)
        
        self.assertIn('Frontend Development', skills)
        self.assertNotIn('Web Design', skills)  # Requires both HTML and CSS

    def test_css_without_html_no_web_design(self):
        """Test CSS without HTML - should not show Web Design"""
        project = self.create_test_project({
            'style.css': 'body { color: red; }'
        })
        
        skills = extract_skills(project)
        
        self.assertIn('Frontend Development', skills)
        self.assertNotIn('Web Design', skills)  # Requires both HTML and CSS

    def test_docker_without_scripting_no_devops(self):
        """Test Docker without scripting - should not show DevOps"""
        project = self.create_test_project({
            'Dockerfile': 'FROM python:3.9\nRUN pip install django',
            'docker-compose.yml': 'version: "3"\nservices:\n  web:\n    build: .',
            'app.py': 'print("Hello")'
        })
        
        skills = extract_skills(project)
        
        self.assertIn('Containerization', skills)  # Docker adds Containerization
        self.assertNotIn('Docker', skills)  # Framework name not in skills
        self.assertNotIn('DevOps', skills)  # Requires Docker + scripting or CI/CD files

    def test_docker_with_scripting_shows_devops(self):
        """Test Docker with shell scripts - should show DevOps"""
        project = self.create_test_project({
            'Dockerfile': 'FROM python:3.9',
            'deploy.sh': '#!/bin/bash\ndocker build -t myapp .',
            'setup.sh': '#!/bin/bash\necho "Setup"'
        })
        
        skills = extract_skills(project)
        
        self.assertIn('Containerization', skills)  # Docker adds Containerization
        self.assertNotIn('Docker', skills)  # Framework name not in skills
        self.assertIn('DevOps', skills)  # Docker + Shell scripting
        self.assertIn('Automation', skills)

    def test_empty_project(self):
        """Test empty project - should return empty skills list"""
        project = self.create_test_project({})
        
        skills = extract_skills(project)
        
        self.assertEqual(skills, [])

    def test_only_readme_and_gitignore(self):
        """Test project with only README and .gitignore - no skills"""
        project = self.create_test_project({
            'README.md': '# My Project',
            '.gitignore': 'node_modules/'
        })
        
        skills = extract_skills(project)
        
        # Should be empty or minimal (just documentation-related)
        self.assertNotIn('Backend Development', skills)
        self.assertNotIn('Frontend Development', skills)

    # ===== Framework & Technology Detection =====

    def test_machine_learning_project(self):
        """Test ML project: Python + TensorFlow + Pandas"""
        project = self.create_test_project({
            'train.py': 'import tensorflow as tf',
            'requirements.txt': 'tensorflow==2.13.0\npandas==2.0.0\nnumpy==1.24.0',
            'data_prep.py': 'import pandas as pd'
        })
        
        skills = extract_skills(project)
        
        # Check for ML and data science skills (framework names become skill names)
        self.assertIn('Machine Learning', skills)
        self.assertIn('Data Science', skills)
        # Frameworks detected and their skills added
        ml_related = any(s in skills for s in ['Deep Learning', 'AI Development', 'Neural Networks'])
        self.assertTrue(ml_related)

    def test_mobile_development_react_native(self):
        """Test mobile app: TypeScript + React Native"""
        project = self.create_test_project({
            'package.json': '{"dependencies": {"react-native": "^0.72.0", "typescript": "^5.0.0"}}',
            'App.tsx': 'import { View } from "react-native"',
            'components/Button.tsx': 'export const Button = () => null'
        })
        
        skills = extract_skills(project)
        
        self.assertIn('Mobile Development', skills)
        self.assertIn('Cross-Platform Development', skills)  # React Native skill
        self.assertNotIn('React Native', skills)  # Framework name not in skills

    def test_ci_cd_with_jenkins(self):
        """Test project with CI/CD pipeline"""
        project = self.create_test_project({
            'Jenkinsfile': 'pipeline { agent any }',
            'src/app.py': 'def main(): pass'
        })
        
        skills = extract_skills(project)
        
        # Jenkinsfile should add CI/CD skills
        self.assertIn('CI/CD', skills)
        self.assertIn('Build Automation', skills)
        self.assertIn('DevOps', skills)
        self.assertIn('Backend Development', skills)

    def test_docker_consolidation(self):
        """Test Docker shows Containerization skill, not Docker itself"""
        project = self.create_test_project({
            'Dockerfile': 'FROM node:18',
            'docker-compose.yml': 'version: "3"'
        })
        
        skills = extract_skills(project)
        
        self.assertIn('Containerization', skills)  # Concept skill
        self.assertNotIn('Docker', skills)  # Framework name not in skills


    # ===== Creative Skills (File-based) =====

    def test_photography_raw_files(self):
        """Test photography project with RAW files"""
        project = self.create_test_project({
            'photos/img1.cr2': 'fake-raw-content',
            'photos/img2.cr2': 'fake-raw-content',
            'photos/img3.cr2': 'fake-raw-content',
            'photos/img4.nef': 'fake-raw-content'
        })
        
        skills = extract_skills(project)
        
        self.assertIn('Photography', skills)
        self.assertIn('RAW Photo Processing', skills)

    def test_graphic_design_photoshop(self):
        """Test graphic design project with Photoshop files"""
        project = self.create_test_project({
            'designs/poster.psd': 'fake-psd-content',
            'designs/logo.ai': 'fake-ai-content'
        })
        
        skills = extract_skills(project)
        
        self.assertIn('Adobe Photoshop', skills)
        self.assertIn('Adobe Illustrator', skills)
        self.assertIn('Graphic Design', skills)

    def test_ui_design_figma(self):
        """Test UI/UX project with Figma files"""
        project = self.create_test_project({
            'designs/mockup.fig': 'fake-figma-content',
            'designs/wireframe.fig': 'fake-figma-content'
        })
        
        skills = extract_skills(project)
        
        self.assertIn('Figma', skills)
        self.assertIn('UI/UX Design', skills)

    # ===== Language Skills Removal =====

    def test_no_python_programming_skill(self):
        """Test that 'Python Programming' is NOT in skills (languages are separate)"""
        project = self.create_test_project({
            'app.py': 'print("Hello")',
            'requirements.txt': 'django==4.2.0'
        })
        
        skills = extract_skills(project)
        
        self.assertNotIn('Python Programming', skills)  # Languages listed separately
        self.assertIn('Backend Development', skills)  # Context skill OK

    # ===== Paradigm Skills =====

    def test_functional_programming(self):
        """Test functional programming skill from functional languages"""
        project = self.create_test_project({
            'main.hs': 'main = putStrLn "Hello"',
            'utils.hs': 'double x = x * 2'
        })
        
        skills = extract_skills(project)
        
        self.assertIn('Functional Programming', skills)

    # ===== Skill Prioritization =====

    def test_fullstack_replaces_frontend_backend(self):
        """Test that Full-Stack skill replaces individual Frontend/Backend skills"""
        project = self.create_test_project({
            'backend/app.py': 'from flask import Flask',
            'backend/requirements.txt': 'flask==2.3.0',
            'frontend/index.html': '<html></html>',
            'frontend/style.css': 'body { }'
        })
        
        skills = extract_skills(project)
        
        self.assertIn('Full-Stack Development', skills)
        self.assertNotIn('Backend Development', skills)  # Replaced by Full-Stack
        self.assertNotIn('Frontend Development', skills)  # Replaced by Full-Stack

    def test_multiple_frameworks_detected(self):
        """Test that multiple frameworks add their respective skills"""
        project = self.create_test_project({
            'package.json': '{"dependencies": {"react": "^18.0.0", "redux": "^4.2.0", "axios": "^1.4.0"}}',
            'App.tsx': 'import React from "react"'
        })
        
        skills = extract_skills(project)
        
        # Framework skills added, not framework names
        self.assertIn('Component-Based Architecture', skills)  # React
        self.assertIn('State Management', skills)  # Redux
        self.assertNotIn('React', skills)  # Framework name not in skills
        self.assertNotIn('Redux', skills)  # Framework name not in skills
        self.assertNotIn('Axios', skills)  # Framework name not in skills (Axios adds no skills)

    # ===== Real-World Scenario =====

    def test_complete_web_app_scenario(self):
        """Test realistic complete web application"""
        project = self.create_test_project({
            # Backend
            'backend/app.py': 'from flask import Flask',
            'backend/requirements.txt': 'flask==2.3.0\nsqlalchemy==2.0.0',
            'backend/models.py': 'class User: pass',
            
            # Frontend
            'frontend/package.json': '{"dependencies": {"react": "^18.0.0", "tailwindcss": "^3.3.0"}}',
            'frontend/src/App.tsx': 'export const App = () => <div />',
            'frontend/src/index.html': '<html></html>',
            'frontend/src/styles.css': 'body { }',
            
            # DevOps
            'Dockerfile': 'FROM python:3.9',
            'docker-compose.yml': 'version: "3"',
            'deploy.sh': '#!/bin/bash\ndocker-compose up',
            
            # Tests
            'tests/test_app.py': 'import pytest'
        })
        
        skills = extract_skills(project)
        
        # Core skills
        self.assertIn('Full-Stack Development', skills)
        self.assertIn('Web Design', skills)
        
        # Framework skills (not framework names)
        self.assertIn('RESTful APIs', skills)  # Flask
        self.assertIn('Component-Based Architecture', skills)  # React
        self.assertIn('Utility-First CSS', skills)  # Tailwind
        self.assertIn('Containerization', skills)  # Docker
        self.assertIn('DevOps', skills)
        
        # Should NOT have framework names in skills
        self.assertNotIn('Flask', skills)
        self.assertNotIn('React', skills)
        self.assertNotIn('Tailwind CSS', skills)
        self.assertNotIn('Docker', skills)
        
        # Should NOT have redundant skills
        self.assertNotIn('Backend Development', skills)
        self.assertNotIn('Frontend Development', skills)
        self.assertNotIn('Python Programming', skills)


class SkillExtractionEdgeCasesTests(TestCase):
    """Additional edge case tests"""

    def setUp(self):
        self.temp_dir = None

    def tearDown(self):
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

    def create_test_project(self, files_dict):
        self.temp_dir = tempfile.mkdtemp()
        root_path = Path(self.temp_dir)
        for file_path, content in files_dict.items():
            full_path = root_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        return root_path

    def test_skills_are_sorted(self):
        """Test that returned skills are sorted alphabetically"""
        project = self.create_test_project({
            'app.py': 'from django import models',
            'requirements.txt': 'django==4.2.0',
            'index.html': '<html></html>'
        })
        
        skills = extract_skills(project)
        
        # Check that skills are sorted
        self.assertEqual(skills, sorted(skills))

    def test_skills_are_unique(self):
        """Test that no duplicate skills are returned"""
        project = self.create_test_project({
            'Dockerfile': 'FROM python:3.9',
            'docker-compose.yml': 'version: "3"',
            'app.py': 'print("Hello")'
        })
        
        skills = extract_skills(project)
        
        # Check no duplicates
        self.assertEqual(len(skills), len(set(skills)))

    def test_case_sensitivity(self):
        """Test that skill names are case-consistent"""
        project = self.create_test_project({
            'package.json': '{"dependencies": {"react": "^18.0.0"}}',
            'App.jsx': 'export const App = () => null'
        })
        
        skills = extract_skills(project)
        
        # Check skills exist and are properly capitalized
        self.assertIn('Component-Based Architecture', skills)
        self.assertIn('Frontend Development', skills)
        # Should not have all-lowercase skills
        self.assertTrue(all(not s.islower() for s in skills if s))

    def test_large_project_performance(self):
        """Test skill extraction on a project with many files"""
        files = {}
        
        # Create 100 Python files
        for i in range(100):
            files[f'src/module{i}.py'] = f'def function{i}(): pass'
        
        # Add some frameworks
        files['requirements.txt'] = 'django==4.2.0\ndjango-rest-framework'
        
        project = self.create_test_project(files)
        
        # Should complete without timing out
        skills = extract_skills(project)
        
        self.assertIn('Backend Development', skills)
        self.assertIn('RESTful APIs', skills)  # Django skill
        self.assertNotIn('Django', skills)  # Framework name not in skills

    def test_non_coding_project_with_documentation(self):
        """Test project that's just documentation"""
        project = self.create_test_project({
            'README.md': '# Documentation Project',
            'docs/guide.md': '## User Guide',
            'docs/api.md': '## API Reference'
        })
        
        skills = extract_skills(project)
        
        # May have Documentation skill or be empty
        self.assertNotIn('Backend Development', skills)
        self.assertNotIn('Frontend Development', skills)

