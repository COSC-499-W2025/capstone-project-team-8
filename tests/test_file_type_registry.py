"""
Tests for file_type_registry module.
"""
import pytest
from src.backend.app.services.classifiers.file_type_registry import (
    CODE_EXTS,
    TEXT_EXTS,
    IMAGE_EXTS,
    OTHER_BINARY_EXTS,
    FOLDER_HINTS,
    is_code_file,
    is_text_file,
    is_image_file,
    get_file_category,
)


class TestFileExtensions:
    """Test file extension constants."""
    
    def test_code_extensions_exist(self):
        """Test that CODE_EXTS contains common programming languages."""
        assert '.py' in CODE_EXTS
        assert '.js' in CODE_EXTS
        assert '.java' in CODE_EXTS
        assert '.cpp' in CODE_EXTS
        assert len(CODE_EXTS) > 10
    
    def test_text_extensions_exist(self):
        """Test that TEXT_EXTS contains document formats."""
        assert '.txt' in TEXT_EXTS
        assert '.md' in TEXT_EXTS
        assert '.pdf' in TEXT_EXTS
        assert len(TEXT_EXTS) > 5
    
    def test_image_extensions_exist(self):
        """Test that IMAGE_EXTS contains image formats."""
        assert '.png' in IMAGE_EXTS
        assert '.jpg' in IMAGE_EXTS
        assert '.svg' in IMAGE_EXTS
        assert len(IMAGE_EXTS) > 5
    
    def test_no_overlap_between_categories(self):
        """Test that file extensions don't overlap between categories."""
        assert not (CODE_EXTS & TEXT_EXTS)
        assert not (CODE_EXTS & IMAGE_EXTS)
        assert not (TEXT_EXTS & IMAGE_EXTS)


class TestFolderHints:
    """Test folder name hints."""
    
    def test_folder_hints_structure(self):
        """Test that FOLDER_HINTS has expected keys."""
        assert 'code' in FOLDER_HINTS
        assert 'writing' in FOLDER_HINTS
        assert 'art' in FOLDER_HINTS
    
    def test_code_folder_hints(self):
        """Test common code folder names exist."""
        assert 'src' in FOLDER_HINTS['code']
        assert 'lib' in FOLDER_HINTS['code']
        assert 'tests' in FOLDER_HINTS['code']
    
    def test_writing_folder_hints(self):
        """Test common writing folder names exist."""
        assert 'docs' in FOLDER_HINTS['writing']
        assert 'paper' in FOLDER_HINTS['writing']
    
    def test_art_folder_hints(self):
        """Test common art folder names exist."""
        assert 'images' in FOLDER_HINTS['art']
        assert 'assets' in FOLDER_HINTS['art']


class TestFileClassificationHelpers:
    """Test helper functions for file classification."""
    
    def test_is_code_file(self):
        """Test code file detection."""
        assert is_code_file('script.py')
        assert is_code_file('app.js')
        assert is_code_file('Main.java')
        assert not is_code_file('document.txt')
        assert not is_code_file('image.png')
    
    def test_is_text_file(self):
        """Test text file detection."""
        assert is_text_file('README.md')
        assert is_text_file('notes.txt')
        assert is_text_file('paper.pdf')
        assert not is_text_file('script.py')
        assert not is_text_file('photo.jpg')
    
    def test_is_image_file(self):
        """Test image file detection."""
        assert is_image_file('logo.png')
        assert is_image_file('photo.jpg')
        assert is_image_file('icon.svg')
        assert not is_image_file('script.py')
        assert not is_image_file('doc.txt')
    
    def test_get_file_category(self):
        """Test getting file category."""
        assert get_file_category('script.py') == 'code'
        assert get_file_category('README.md') == 'text'
        assert get_file_category('logo.png') == 'image'
        assert get_file_category('video.mp4') == 'binary'
        assert get_file_category('unknown.xyz') == 'unknown'
    
    def test_case_insensitive(self):
        """Test that file classification is case-insensitive."""
        assert is_code_file('Script.PY')
        assert is_code_file('SCRIPT.PY')
        assert get_file_category('README.MD') == 'text'
