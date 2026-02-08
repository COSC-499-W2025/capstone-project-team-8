"""
Tests for feature_extractor module.
"""
import pytest
import tempfile
import os
from pathlib import Path
from app.services.classifiers.feature_extractor import extract_project_features


class TestFeatureExtractor:
    """Test feature extraction from project directories."""
    
    def test_extract_empty_directory(self):
        """Test feature extraction from empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            features = extract_project_features(tmpdir)
            
            assert features['total_files'] == 0
            assert features['code_count'] == 0
            assert features['text_count'] == 0
            assert features['image_count'] == 0
            assert len(features['ext_counts']) == 0
            assert len(features['folder_names']) == 0
    
    def test_extract_code_project(self):
        """Test feature extraction from a coding project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create code files
            (tmpdir_path / 'script.py').write_text('print("hello")')
            (tmpdir_path / 'app.js').write_text('console.log("hello")')
            (tmpdir_path / 'Main.java').write_text('public class Main {}')
            
            # Create folders
            (tmpdir_path / 'src').mkdir()
            (tmpdir_path / 'tests').mkdir()
            
            features = extract_project_features(tmpdir)
            
            assert features['total_files'] == 3
            assert features['code_count'] == 3
            assert features['text_count'] == 0
            assert features['image_count'] == 0
            assert '.py' in features['ext_counts']
            assert '.js' in features['ext_counts']
            assert '.java' in features['ext_counts']
            assert 'src' in features['folder_names']
            assert 'tests' in features['folder_names']
    
    def test_extract_mixed_project(self):
        """Test feature extraction from mixed project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create various files
            (tmpdir_path / 'script.py').write_text('code')
            (tmpdir_path / 'README.md').write_text('docs')
            (tmpdir_path / 'logo.png').write_bytes(b'fake image')
            (tmpdir_path / 'data.json').write_text('{}')
            
            features = extract_project_features(tmpdir)
            
            assert features['total_files'] == 4
            assert features['code_count'] == 2  # .py and .json
            assert features['text_count'] == 1  # .md
            assert features['image_count'] == 1  # .png
    
    def test_extract_with_subdirectories(self):
        """Test feature extraction handles subdirectories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create nested structure
            (tmpdir_path / 'src').mkdir()
            (tmpdir_path / 'src' / 'utils').mkdir()
            (tmpdir_path / 'src' / 'app.py').write_text('code')
            (tmpdir_path / 'src' / 'utils' / 'helper.py').write_text('code')
            (tmpdir_path / 'docs').mkdir()
            (tmpdir_path / 'docs' / 'README.md').write_text('docs')
            
            features = extract_project_features(tmpdir)
            
            assert features['total_files'] == 3
            assert features['code_count'] == 2
            assert features['text_count'] == 1
            assert 'src' in features['folder_names']
            assert 'utils' in features['folder_names']
            assert 'docs' in features['folder_names']
    
    def test_case_insensitive_extensions(self):
        """Test that extension counting is case-insensitive."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            (tmpdir_path / 'script.PY').write_text('code')
            (tmpdir_path / 'app.Js').write_text('code')
            (tmpdir_path / 'README.MD').write_text('docs')
            
            features = extract_project_features(tmpdir)
            
            assert features['code_count'] == 2
            assert features['text_count'] == 1
            assert '.py' in features['ext_counts']  # Should be lowercase
            assert '.js' in features['ext_counts']
            assert '.md' in features['ext_counts']
    
    def test_case_insensitive_folders(self):
        """Test that folder counting is case-insensitive."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            (tmpdir_path / 'SRC').mkdir()
            (tmpdir_path / 'Tests').mkdir()
            (tmpdir_path / 'DOCS').mkdir()
            
            features = extract_project_features(tmpdir)
            
            # Folders should be counted in lowercase
            assert 'src' in features['folder_names']
            assert 'tests' in features['folder_names']
            assert 'docs' in features['folder_names']
    
    def test_extension_counts_accuracy(self):
        """Test that extension counts are accurate."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create multiple files with same extension
            (tmpdir_path / 'file1.py').write_text('code')
            (tmpdir_path / 'file2.py').write_text('code')
            (tmpdir_path / 'file3.py').write_text('code')
            (tmpdir_path / 'script.js').write_text('code')
            
            features = extract_project_features(tmpdir)
            
            assert features['ext_counts']['.py'] == 3
            assert features['ext_counts']['.js'] == 1
