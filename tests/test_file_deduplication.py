"""
Tests for File Deduplication Feature

Verifies that duplicate files are detected and only stored once.
"""

import pytest
from django.contrib.auth import get_user_model
from app.models import Project, ProjectFile
from app.services.database_service import ProjectDatabaseService
from app.utils.file_hash import compute_text_hash

User = get_user_model()


@pytest.mark.django_db
class TestFileDeduplication:
    """Test suite for file deduplication functionality."""
    
    def setup_method(self):
        """Set up test user and service."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.db_service = ProjectDatabaseService()
    
    def test_duplicate_file_detection(self):
        """Test that duplicate files are detected across projects."""
        # Same content, different filenames
        file_content = "print('Hello, World!')\n"
        expected_hash = compute_text_hash(file_content)
        
        # First upload with file1.py
        analysis_data_1 = {
            'projects': [{
                'id': 1,
                'root': 'project1',
                'classification': {
                    'type': 'coding',
                    'confidence': 0.8,
                    'languages': ['Python']
                },
                'files': {
                    'code': [{
                        'path': 'file1.py',
                        'lines': 1,
                        'text': file_content
                    }]
                }
            }],
            'overall': {
                'classification': 'coding',
                'confidence': 0.8
            }
        }
        
        projects_1 = self.db_service.save_project_analysis(
            user=self.user,
            analysis_data=analysis_data_1,
            upload_filename='upload1.zip'
        )
        
        # Verify first file is not marked as duplicate
        file1 = ProjectFile.objects.get(project=projects_1[0], filename='file1.py')
        assert file1.content_hash == expected_hash
        assert file1.is_duplicate is False
        assert file1.original_file is None
        
        # Second upload with same content, different filename
        analysis_data_2 = {
            'projects': [{
                'id': 1,
                'root': 'project2',
                'classification': {
                    'type': 'coding',
                    'confidence': 0.8,
                    'languages': ['Python']
                },
                'files': {
                    'code': [{
                        'path': 'file2.py',  # Different name
                        'lines': 1,
                        'text': file_content  # Same content
                    }]
                }
            }],
            'overall': {
                'classification': 'coding',
                'confidence': 0.8
            }
        }
        
        projects_2 = self.db_service.save_project_analysis(
            user=self.user,
            analysis_data=analysis_data_2,
            upload_filename='upload2.zip'
        )
        
        # Verify second file is marked as duplicate
        file2 = ProjectFile.objects.get(project=projects_2[0], filename='file2.py')
        assert file2.content_hash == expected_hash
        assert file2.is_duplicate is True
        assert file2.original_file == file1
    
    def test_unique_files_not_marked_as_duplicates(self):
        """Test that unique files are not marked as duplicates."""
        analysis_data = {
            'projects': [{
                'id': 1,
                'root': 'project1',
                'classification': {
                    'type': 'coding',
                    'confidence': 0.8,
                    'languages': ['Python']
                },
                'files': {
                    'code': [
                        {'path': 'file1.py', 'lines': 1, 'text': 'print("A")'},
                        {'path': 'file2.py', 'lines': 1, 'text': 'print("B")'},
                        {'path': 'file3.py', 'lines': 1, 'text': 'print("C")'}
                    ]
                }
            }],
            'overall': {
                'classification': 'coding',
                'confidence': 0.8
            }
        }
        
        projects = self.db_service.save_project_analysis(
            user=self.user,
            analysis_data=analysis_data,
            upload_filename='upload.zip'
        )
        
        # All files should be unique
        files = ProjectFile.objects.filter(project=projects[0])
        assert files.count() == 3
        
        for f in files:
            assert f.is_duplicate is False
            assert f.original_file is None
            assert f.content_hash  # Hash should be computed
    
    def test_duplicate_detection_scoped_to_user(self):
        """Test that duplicate detection is scoped to individual users."""
        # Create second user
        user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        
        file_content = "console.log('test');\n"
        
        analysis_data = {
            'projects': [{
                'id': 1,
                'root': 'project',
                'classification': {
                    'type': 'coding',
                    'confidence': 0.8,
                    'languages': ['JavaScript']
                },
                'files': {
                    'code': [{
                        'path': 'script.js',
                        'lines': 1,
                        'text': file_content
                    }]
                }
            }],
            'overall': {
                'classification': 'coding',
                'confidence': 0.8
            }
        }
        
        # User 1 uploads file
        projects_1 = self.db_service.save_project_analysis(
            user=self.user,
            analysis_data=analysis_data,
            upload_filename='upload1.zip'
        )
        
        # User 2 uploads same file
        projects_2 = self.db_service.save_project_analysis(
            user=user2,
            analysis_data=analysis_data,
            upload_filename='upload2.zip'
        )
        
        # Both should NOT be marked as duplicates (different users)
        file1 = ProjectFile.objects.get(project=projects_1[0])
        file2 = ProjectFile.objects.get(project=projects_2[0])
        
        assert file1.is_duplicate is False
        assert file2.is_duplicate is False
        assert file1.content_hash == file2.content_hash  # Same hash though
    
    def test_incremental_upload_deduplication(self):
        """Test deduplication across incremental uploads."""
        # First upload
        analysis_1 = {
            'projects': [{
                'id': 1,
                'root': 'project',
                'classification': {
                    'type': 'coding',
                    'confidence': 0.8,
                    'languages': ['Python']
                },
                'files': {
                    'code': [
                        {'path': 'utils.py', 'lines': 10, 'text': 'def helper():\n    pass\n'},
                        {'path': 'main.py', 'lines': 20, 'text': 'from utils import helper\n'}
                    ]
                }
            }],
            'overall': {'classification': 'coding', 'confidence': 0.8}
        }
        
        projects_1 = self.db_service.save_project_analysis(
            user=self.user,
            analysis_data=analysis_1,
            upload_filename='initial.zip'
        )
        
        # Second upload includes one duplicate and one new file
        analysis_2 = {
            'projects': [{
                'id': 1,
                'root': 'project',
                'classification': {
                    'type': 'coding',
                    'confidence': 0.8,
                    'languages': ['Python']
                },
                'files': {
                    'code': [
                        {'path': 'utils.py', 'lines': 10, 'text': 'def helper():\n    pass\n'},  # Duplicate
                        {'path': 'config.py', 'lines': 5, 'text': 'DEBUG = True\n'}  # New
                    ]
                }
            }],
            'overall': {'classification': 'coding', 'confidence': 0.8}
        }
        
        projects_2 = self.db_service.save_project_analysis(
            user=self.user,
            analysis_data=analysis_2,
            upload_filename='incremental.zip'
        )
        
        # Check total files for user
        all_files = ProjectFile.objects.filter(project__user=self.user)
        assert all_files.count() == 4  # 2 from first + 2 from second
        
        # Check duplicate status
        duplicates = all_files.filter(is_duplicate=True)
        assert duplicates.count() == 1
        
        # The duplicate utils.py should reference the original
        duplicate_utils = ProjectFile.objects.get(
            project=projects_2[0],
            filename='utils.py'
        )
        original_utils = ProjectFile.objects.get(
            project=projects_1[0],
            filename='utils.py'
        )
        
        assert duplicate_utils.is_duplicate is True
        assert duplicate_utils.original_file == original_utils


@pytest.mark.django_db
class TestFileHashUtils:
    """Test the file hash utility functions."""
    
    def test_compute_text_hash_consistency(self):
        """Test that same content produces same hash."""
        from app.utils.file_hash import compute_text_hash
        
        text = "Hello, World!"
        hash1 = compute_text_hash(text)
        hash2 = compute_text_hash(text)
        
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 produces 64 hex chars
    
    def test_compute_file_hash_consistency(self):
        """Test that same binary content produces same hash."""
        from app.utils.file_hash import compute_file_hash
        
        content = b"Binary content"
        hash1 = compute_file_hash(content)
        hash2 = compute_file_hash(content)
        
        assert hash1 == hash2
        assert len(hash1) == 64
