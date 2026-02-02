"""
Tests for incremental upload functionality.
"""

import io
import zipfile
import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from app.models import Project, Portfolio, ProjectFile, PortfolioProject
from app.services.incremental_upload_service import IncrementalUploadService

User = get_user_model()


class IncrementalUploadServiceTests(TestCase):
    """Test the IncrementalUploadService."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.service = IncrementalUploadService()

    def make_zip_bytes(self, file_map):
        """Create a ZIP file in memory from a file map."""
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename, content in file_map.items():
                if isinstance(content, str):
                    content = content.encode('utf-8')
                zip_file.writestr(filename, content)
        buffer.seek(0)
        return buffer.getvalue()

    def test_merge_into_existing_project(self):
        """Test merging files into an existing project."""
        # Create base project
        base_project = Project.objects.create(
            user=self.user,
            name='Base Project',
            classification_type='coding',
            project_root_path='project',
            total_files=2
        )

        # Create some existing files
        ProjectFile.objects.create(
            project=base_project,
            file_path='main.py',
            filename='main.py',
            content_hash='abc123',
            file_type='code'
        )

        # Create incremental upload data
        files = {
            'project/main.py': 'print("hello world")',  # Duplicate
            'project/utils.py': 'def helper(): pass',    # New file
        }
        zip_bytes = self.make_zip_bytes(files)
        upload_file = SimpleUploadedFile('update.zip', zip_bytes, content_type='application/zip')

        # Process incremental upload
        result = self.service.process_incremental_upload(
            user=self.user,
            upload_file=upload_file,
            target_project_id=base_project.id
        )

        # Verify results
        self.assertEqual(result['merge_strategy'], 'project_update')
        self.assertEqual(len(result['processed_projects']), 1)

        # Check incremental project was created
        incremental_project = result['processed_projects'][0]
        self.assertTrue(incremental_project.is_incremental_update)
        self.assertEqual(incremental_project.base_project, base_project)
        self.assertEqual(incremental_project.version_number, 2)

        # Verify files were processed with deduplication
        self.assertGreater(result['files_added'], 0)

    def test_add_to_existing_portfolio(self):
        """Test adding new projects to an existing portfolio."""
        # Create portfolio with existing project
        portfolio = Portfolio.objects.create(
            user=self.user,
            title='Test Portfolio',
            slug='test-portfolio'
        )

        existing_project = Project.objects.create(
            user=self.user,
            name='Existing Project',
            project_root_path='existing'
        )

        PortfolioProject.objects.create(
            portfolio=portfolio,
            project=existing_project,
            order=0
        )

        # Create incremental upload with new project
        files = {
            'new-project/README.md': '# New Project',
            'new-project/app.py': 'print("new app")',
        }
        zip_bytes = self.make_zip_bytes(files)
        upload_file = SimpleUploadedFile('addition.zip', zip_bytes, content_type='application/zip')

        # Process incremental upload
        result = self.service.process_incremental_upload(
            user=self.user,
            upload_file=upload_file,
            target_portfolio_id=portfolio.id
        )

        # Verify results
        self.assertEqual(result['merge_strategy'], 'portfolio_expansion')
        
        # Check portfolio was updated
        portfolio.refresh_from_db()
        self.assertIsNotNone(portfolio.last_incremental_upload)

    def test_create_new_standalone_projects(self):
        """Test creating new standalone projects."""
        files = {
            'standalone/main.py': 'print("standalone")',
            'standalone/README.md': '# Standalone Project',
        }
        zip_bytes = self.make_zip_bytes(files)
        upload_file = SimpleUploadedFile('standalone.zip', zip_bytes, content_type='application/zip')

        # Process incremental upload without targets
        result = self.service.process_incremental_upload(
            user=self.user,
            upload_file=upload_file
        )

        # Verify results
        self.assertEqual(result['merge_strategy'], 'new_standalone')
        self.assertGreater(len(result['processed_projects']), 0)

        # Check session ID was assigned
        for project in result['processed_projects']:
            self.assertIsNotNone(project.incremental_upload_session)

    def test_file_deduplication_across_versions(self):
        """Test that files are deduplicated across project versions."""
        import hashlib
        
        # Create base project with files
        base_project = Project.objects.create(
            user=self.user,
            name='Base Project',
            project_root_path='project'
        )

        # Calculate the same hash that the service would calculate
        shared_content = 'def shared(): pass'
        shared_hash = hashlib.sha256(shared_content.encode('utf-8')).hexdigest()

        ProjectFile.objects.create(
            project=base_project,
            file_path='shared.py',
            filename='shared.py',
            content_hash=shared_hash,
            file_type='code',
            content_preview=shared_content
        )

        # Upload increment with same file
        files = {
            'project/shared.py': 'def shared(): pass',  # Exact duplicate
            'project/new.py': 'def new(): pass',        # New file
        }

        upload_project_data = {
            'id': 1,
            'root': 'project',
            'classification': {'type': 'coding', 'confidence': 0.8},
            'files': {
                'code': [
                    {'path': 'shared.py', 'lines': 1, 'text': 'def shared(): pass'},
                    {'path': 'new.py', 'lines': 1, 'text': 'def new(): pass'}
                ]
            }
        }

        # Create incremental project and process files
        incremental_project = Project.objects.create(
            user=self.user,
            name='Incremental Project',
            base_project=base_project,
            version_number=2,
            is_incremental_update=True
        )

        files_added, files_deduplicated = self.service._process_incremental_files(
            incremental_project, upload_project_data, base_project
        )

        # Verify deduplication
        self.assertEqual(files_added, 1)  # Only new.py
        self.assertEqual(files_deduplicated, 1)  # shared.py is duplicate

        # Check that we have both the original file and the duplicate marked file
        shared_files = ProjectFile.objects.filter(
            project=incremental_project,
            filename='shared.py'
        )
        self.assertEqual(shared_files.count(), 2)  # Original + duplicate
        
        # Check that one is marked as duplicate
        duplicate_files = shared_files.filter(is_duplicate=True)
        self.assertEqual(duplicate_files.count(), 1)
        
        # Check that one is not marked as duplicate (the original)
        original_files = shared_files.filter(is_duplicate=False)
        self.assertEqual(original_files.count(), 1)

    def test_get_project_history(self):
        """Test retrieving project version history."""
        # Create base project
        base_project = Project.objects.create(
            user=self.user,
            name='Base Project',
            version_number=1,
            created_at='2023-01-01T00:00:00Z'
        )

        # Create incremental versions
        v2_project = Project.objects.create(
            user=self.user,
            name='Base Project (v2)',
            base_project=base_project,
            version_number=2,
            is_incremental_update=True,
            created_at='2023-01-02T00:00:00Z'
        )

        v3_project = Project.objects.create(
            user=self.user,
            name='Base Project (v3)',
            base_project=base_project,
            version_number=3,
            is_incremental_update=True,
            created_at='2023-01-03T00:00:00Z'
        )

        # Get history
        history = self.service.get_project_history(base_project)

        # Verify history
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0]['version'], 1)  # Base project
        self.assertEqual(history[1]['version'], 2)
        self.assertEqual(history[2]['version'], 3)


class IncrementalUploadAPITests(TestCase):
    """Test the incremental upload API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def make_zip_bytes(self, file_map):
        """Create a ZIP file in memory from a file map."""
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename, content in file_map.items():
                if isinstance(content, str):
                    content = content.encode('utf-8')
                zip_file.writestr(filename, content)
        buffer.seek(0)
        return buffer.getvalue()

    def test_incremental_upload_api(self):
        """Test the incremental upload API endpoint."""
        # Create target project
        project = Project.objects.create(
            user=self.user,
            name='Target Project'
        )

        # Create upload file
        files = {
            'project/new_file.py': 'print("new functionality")',
        }
        zip_bytes = self.make_zip_bytes(files)
        upload_file = SimpleUploadedFile('increment.zip', zip_bytes, content_type='application/zip')

        # Make API request
        response = self.client.post('/api/incremental-upload/', {
            'file': upload_file,
            'target_project_id': project.id,
            'consent_send_llm': True
        }, format='multipart')

        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['merge_strategy'], 'project_update')
        self.assertGreater(data['projects_processed'], 0)

    def test_project_history_api(self):
        """Test the project history API endpoint."""
        # Create project with versions
        base_project = Project.objects.create(
            user=self.user,
            name='Base Project',
            version_number=1
        )

        incremental_project = Project.objects.create(
            user=self.user,
            name='Base Project (v2)',
            base_project=base_project,
            version_number=2,
            is_incremental_update=True
        )

        # Make API request
        response = self.client.get(f'/api/projects/{base_project.id}/history/')

        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['base_project']['id'], base_project.id)
        self.assertEqual(data['total_versions'], 2)
        self.assertEqual(len(data['versions']), 2)

    def test_portfolio_incremental_stats_api(self):
        """Test the portfolio incremental stats API endpoint."""
        # Create portfolio
        portfolio = Portfolio.objects.create(
            user=self.user,
            title='Test Portfolio',
            slug='test-portfolio'
        )

        # Create project with incremental version
        base_project = Project.objects.create(
            user=self.user,
            name='Base Project'
        )

        incremental_project = Project.objects.create(
            user=self.user,
            name='Base Project (v2)',
            base_project=base_project,
            is_incremental_update=True,
            incremental_upload_session='test_session_123'
        )

        # Add to portfolio
        PortfolioProject.objects.create(
            portfolio=portfolio,
            project=base_project,
            order=0
        )

        # Make API request
        response = self.client.get(f'/api/portfolio/{portfolio.id}/incremental-stats/')

        # Verify response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['portfolio']['id'], portfolio.id)
        self.assertGreaterEqual(data['incremental_uploads'], 1)
        self.assertGreaterEqual(data['total_versions'], 2)

    def test_unauthorized_access(self):
        """Test that unauthorized users cannot access incremental upload."""
        self.client.force_authenticate(user=None)

        response = self.client.post('/api/incremental-upload/', {
            'file': SimpleUploadedFile('test.zip', b'test content')
        })

        self.assertEqual(response.status_code, 401)

    def test_invalid_target_project(self):
        """Test error handling for invalid target project."""
        files = {'test.py': 'print("test")'}
        zip_bytes = self.make_zip_bytes(files)
        upload_file = SimpleUploadedFile('test.zip', zip_bytes, content_type='application/zip')

        response = self.client.post('/api/incremental-upload/', {
            'file': upload_file,
            'target_project_id': 999999  # Non-existent project
        }, format='multipart')

        self.assertEqual(response.status_code, 404)
        self.assertIn('not found', response.json()['error'])

    def test_invalid_target_portfolio(self):
        """Test error handling for invalid target portfolio."""
        files = {'test.py': 'print("test")'}
        zip_bytes = self.make_zip_bytes(files)
        upload_file = SimpleUploadedFile('test.zip', zip_bytes, content_type='application/zip')

        response = self.client.post('/api/incremental-upload/', {
            'file': upload_file,
            'target_portfolio_id': 999999  # Non-existent portfolio
        }, format='multipart')

        self.assertEqual(response.status_code, 404)
        self.assertIn('not found', response.json()['error'])