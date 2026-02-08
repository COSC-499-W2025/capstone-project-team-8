"""
Tests for confidence_calculator module.
"""
import pytest
from app.services.classifiers.confidence_calculator import calculate_confidence


class TestConfidenceCalculator:
    """Test confidence calculation logic."""
    
    def test_high_confidence_pure_code(self):
        """Test high confidence for pure coding project."""
        features = {
            'total_files': 10,
            'code_count': 10,
            'text_count': 0,
            'image_count': 0
        }
        confidence = calculate_confidence(features)
        assert confidence > 0.7
        assert confidence <= 1.0
    
    def test_medium_confidence_mixed(self):
        """Test medium confidence for mixed project."""
        features = {
            'total_files': 10,
            'code_count': 6,
            'text_count': 3,
            'image_count': 1
        }
        confidence = calculate_confidence(features)
        assert 0.4 < confidence < 0.9
    
    def test_low_confidence_few_files(self):
        """Test low confidence for project with few files."""
        features = {
            'total_files': 2,
            'code_count': 1,
            'text_count': 1,
            'image_count': 0
        }
        confidence = calculate_confidence(features)
        assert confidence < 0.7
    
    def test_confidence_capped_at_one(self):
        """Test that confidence never exceeds 1.0."""
        features = {
            'total_files': 100,
            'code_count': 100,
            'text_count': 0,
            'image_count': 0
        }
        confidence = calculate_confidence(features)
        assert confidence <= 1.0
    
    def test_confidence_increases_with_files(self):
        """Test that confidence increases with more files."""
        features1 = {
            'total_files': 3,
            'code_count': 3,
            'text_count': 0,
            'image_count': 0
        }
        features2 = {
            'total_files': 10,
            'code_count': 10,
            'text_count': 0,
            'image_count': 0
        }
        
        conf1 = calculate_confidence(features1)
        conf2 = calculate_confidence(features2)
        
        assert conf2 > conf1
    
    def test_zero_files_returns_low_confidence(self):
        """Test that zero files returns minimal confidence."""
        features = {
            'total_files': 0,
            'code_count': 0,
            'text_count': 0,
            'image_count': 0
        }
        confidence = calculate_confidence(features)
        assert 0.0 <= confidence < 0.5
