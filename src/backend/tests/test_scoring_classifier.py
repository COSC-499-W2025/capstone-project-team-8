"""
Tests for scoring_classifier module.
"""
import pytest
import tempfile
from pathlib import Path
from app.services.classifiers.scoring_classifier import simple_score_classify
from app.services.classifiers.feature_extractor import extract_project_features


class TestScoringClassifier:
    """Test scoring-based classification logic."""
    
    def test_classify_empty_project(self):
        """Test classification of empty/minimal project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            (tmpdir_path / 'file.txt').write_text('test')
            
            # Too few files should return 'unknown'
            result = simple_score_classify(tmpdir, min_files_for_confident=2)
            assert result == 'unknown'
    
    def test_classify_coding_project(self):
        """Test classification of pure coding project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create code files
            (tmpdir_path / 'app.py').write_text('code')
            (tmpdir_path / 'script.js').write_text('code')
            (tmpdir_path / 'Main.java').write_text('code')
            
            # Create code folders
            (tmpdir_path / 'src').mkdir()
            (tmpdir_path / 'tests').mkdir()
            
            result = simple_score_classify(tmpdir, force_mixed=False)
            assert result == 'coding'
    
    def test_classify_writing_project(self):
        """Test classification of writing project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create text files
            (tmpdir_path / 'paper.tex').write_text('text')
            (tmpdir_path / 'chapter1.md').write_text('text')
            (tmpdir_path / 'notes.txt').write_text('text')
            
            # Create writing folders
            (tmpdir_path / 'chapters').mkdir()
            (tmpdir_path / 'references').mkdir()
            
            result = simple_score_classify(tmpdir, force_mixed=False)
            assert result == 'writing'
    
    def test_classify_art_project(self):
        """Test classification of art/design project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create image files
            (tmpdir_path / 'logo.png').write_bytes(b'fake')
            (tmpdir_path / 'photo.jpg').write_bytes(b'fake')
            (tmpdir_path / 'icon.svg').write_text('<svg/>')
            
            # Create art folders
            (tmpdir_path / 'images').mkdir()
            (tmpdir_path / 'assets').mkdir()
            
            result = simple_score_classify(tmpdir, force_mixed=False)
            assert result == 'art'
    
    def test_classify_mixed_project(self):
        """Test classification of mixed project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create mixed content
            (tmpdir_path / 'app.py').write_text('code')
            (tmpdir_path / 'script.js').write_text('code')
            (tmpdir_path / 'README.md').write_text('text')
            (tmpdir_path / 'doc.pdf').write_bytes(b'fake')
            
            result = simple_score_classify(tmpdir, force_mixed=True)
            assert result.startswith('mixed:')
            assert 'coding' in result or 'writing' in result
    
    def test_folder_bonus_affects_classification(self):
        """Test that folder names influence classification."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create equal number of code and text files
            (tmpdir_path / 'file1.py').write_text('code')
            (tmpdir_path / 'file2.md').write_text('text')
            
            # But add code-specific folders
            (tmpdir_path / 'src').mkdir()
            (tmpdir_path / 'tests').mkdir()
            
            result = simple_score_classify(tmpdir, force_mixed=False)
            # Folder bonus should tip it toward coding
            assert result == 'coding'
    
    def test_different_weights(self):
        """Test that custom weights affect classification."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create equal files
            (tmpdir_path / 'file1.py').write_text('code')
            (tmpdir_path / 'file2.py').write_text('code')
            (tmpdir_path / 'file3.md').write_text('text')
            
            # Default weights should favor code
            result1 = simple_score_classify(tmpdir, weights=(3.0, 2.0, 2.5), force_mixed=False)
            
            # High text weight should favor text
            result2 = simple_score_classify(tmpdir, weights=(1.0, 10.0, 1.0), force_mixed=False)
            
            assert result1 == 'coding'
            assert result2 == 'writing'
    
    def test_margin_threshold(self):
        """Test that margin threshold affects mixed classification."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # Create slightly more code than text
            (tmpdir_path / 'file1.py').write_text('code')
            (tmpdir_path / 'file2.py').write_text('code')
            (tmpdir_path / 'file3.md').write_text('text')
            
            # With low margin, should classify as mixed
            result1 = simple_score_classify(tmpdir, margin_threshold=0.1, force_mixed=True)
            
            # With high margin, should classify as coding
            result2 = simple_score_classify(tmpdir, margin_threshold=5.0, force_mixed=False)
            
            assert 'mixed:' in result1 or result1 == 'coding'
            assert result2 == 'coding'
