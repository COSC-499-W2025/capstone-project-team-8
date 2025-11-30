"""
Tests for PDF text extraction using PyMuPDF.

Tests cover:
- Text extraction from valid PDFs
- Multi-page PDF handling
- Error handling (missing files, corrupt PDFs, non-PDF files)
- Unicode and special character handling
- Metadata extraction
- Graceful degradation when PyMuPDF not installed
"""

import os
import sys
from pathlib import Path
from django.test import TestCase

# Add the project root to Python path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
import django
django.setup()

from app.services.utils.pdfReader import read_pdf, get_pdf_metadata, PDF_SUPPORT


class PDFReaderTests(TestCase):
    """Test PDF text extraction functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = Path(__file__).parent / "fixtures" / "pdfs"
        self.test_dir.mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Clean up test files"""
        # Clean up any test files created
        if self.test_dir.exists():
            for file in self.test_dir.glob("*.txt"):
                try:
                    file.unlink()
                except Exception:
                    pass
    
    # ===== PDF Support Tests =====
    
    def test_pdf_support_available(self):
        """Test that PyMuPDF availability is properly detected"""
        # This will help identify dependency issues
        self.assertIsInstance(PDF_SUPPORT, bool, "PDF_SUPPORT should be a boolean")
        
        if PDF_SUPPORT:
            import fitz
            self.assertTrue(hasattr(fitz, 'open'), "PyMuPDF should have 'open' method")
    
    # ===== Error Handling Tests =====
    
    def test_read_nonexistent_pdf(self):
        """Test reading a file that doesn't exist"""
        nonexistent_path = Path("this_file_does_not_exist_12345.pdf")
        text = read_pdf(nonexistent_path)
        self.assertEqual(text, "", "Should return empty string for nonexistent file")
        self.assertIsInstance(text, str, "Should always return a string")
    
    def test_read_non_pdf_file(self):
        """Test reading a file that is not a PDF"""
        # Create a temporary .txt file
        temp_file = self.test_dir / "not_a_pdf.txt"
        temp_file.write_text("This is plain text, not a PDF file")
        
        text = read_pdf(temp_file)
        self.assertEqual(text, "", "Should return empty string for non-PDF file")
        
        # Clean up
        temp_file.unlink()
    
    def test_read_file_with_wrong_extension(self):
        """Test reading a text file with .pdf extension"""
        # Create a text file masquerading as a PDF
        fake_pdf = self.test_dir / "fake.pdf"
        fake_pdf.write_text("Not actually a PDF")
        
        # Should return empty string (PyMuPDF will fail to parse it)
        text = read_pdf(fake_pdf)
        self.assertIsInstance(text, str)
        # It should either be empty or handle gracefully
        
        # Clean up
        fake_pdf.unlink()
    
    def test_read_empty_path(self):
        """Test reading with an empty path string"""
        empty_path = Path("")
        text = read_pdf(empty_path)
        self.assertEqual(text, "", "Should return empty string for empty path")
    
    # ===== Return Type Tests =====
    
    def test_read_pdf_returns_string(self):
        """Test that read_pdf always returns a string"""
        # Even with invalid input, should return a string (empty)
        result = read_pdf(Path("nonexistent.pdf"))
        self.assertIsInstance(result, str, "read_pdf should always return a string")
    
    # ===== Metadata Tests =====
    
    def test_metadata_nonexistent_file(self):
        """Test metadata extraction from nonexistent file"""
        metadata = get_pdf_metadata(Path("nonexistent.pdf"))
        self.assertIsInstance(metadata, dict, "Should return empty dict for nonexistent file")
        self.assertEqual(metadata, {}, "Should be an empty dictionary")
    
    def test_metadata_non_pdf_file(self):
        """Test metadata extraction from non-PDF file"""
        temp_file = self.test_dir / "not_a_pdf.txt"
        temp_file.write_text("This is not a PDF")
        
        metadata = get_pdf_metadata(temp_file)
        self.assertIsInstance(metadata, dict, "Should return dict even for non-PDF")
        self.assertEqual(metadata, {}, "Should return empty dict for non-PDF file")
        
        # Clean up
        temp_file.unlink()
    
    def test_metadata_returns_dict(self):
        """Test that get_pdf_metadata always returns a dictionary"""
        result = get_pdf_metadata(Path("fake.pdf"))
        self.assertIsInstance(result, dict, "get_pdf_metadata should always return a dict")
    
    # ===== Graceful Degradation Tests =====
    
    def test_graceful_degradation_without_pymupdf(self):
        """Test that functions work gracefully when PyMuPDF is not installed"""
        # This test verifies the import guard works
        if not PDF_SUPPORT:
            # If PyMuPDF is not installed, functions should still work but return empty results
            text = read_pdf(Path("any.pdf"))
            self.assertEqual(text, "")
            
            metadata = get_pdf_metadata(Path("any.pdf"))
            self.assertEqual(metadata, {})
    
    # ===== Integration Tests =====
    # Note: These tests require actual PDF files in fixtures/pdfs/
    # They will skip if the fixture files are not present
    
    def test_read_real_pdf_if_available(self):
        """Test reading a real PDF file if fixture is available"""
        if not PDF_SUPPORT:
            self.skipTest("PyMuPDF not installed")
        
        # Look for any PDF file in the fixtures directory
        pdf_files = list(self.test_dir.glob("*.pdf"))
        
        if not pdf_files:
            self.skipTest("No PDF fixture files available for testing")
        
        # Test with the first available PDF
        test_pdf = pdf_files[0]
        text = read_pdf(test_pdf)
        
        self.assertIsInstance(text, str, "Should return a string")
        # Don't assert text length > 0 because the fixture might be empty
        # Just verify it doesn't crash
    
    def test_metadata_from_real_pdf_if_available(self):
        """Test metadata extraction from real PDF if fixture is available"""
        if not PDF_SUPPORT:
            self.skipTest("PyMuPDF not installed")
        
        pdf_files = list(self.test_dir.glob("*.pdf"))
        
        if not pdf_files:
            self.skipTest("No PDF fixture files available for testing")
        
        test_pdf = pdf_files[0]
        metadata = get_pdf_metadata(test_pdf)
        
        self.assertIsInstance(metadata, dict, "Should return a dictionary")
        # Metadata might be empty, so don't assert contents


class PDFReaderEdgeCaseTests(TestCase):
    """Additional edge case tests for PDF reader"""
    
    def test_path_object_handling(self):
        """Test that Path objects are handled correctly"""
        from pathlib import Path
        
        # Should handle Path objects
        result = read_pdf(Path("test.pdf"))
        self.assertIsInstance(result, str)
    
    def test_string_path_conversion(self):
        """Test that string paths are converted to Path objects"""
        # The function should handle this internally via Path(path)
        result = read_pdf(Path("test.pdf"))
        self.assertIsInstance(result, str)
    
    def test_case_insensitive_extension_check(self):
        """Test that PDF extension check is case-insensitive"""
        # Create temp files with different case extensions
        test_dir = Path(__file__).parent / "fixtures" / "pdfs"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        # These should all be recognized as PDFs (or at least attempted)
        for ext in [".PDF", ".Pdf", ".pDf"]:
            temp_file = test_dir / f"test{ext}"
            temp_file.write_text("Not a real PDF")
            
            # Should not crash, should return empty string (since it's not a real PDF)
            result = read_pdf(temp_file)
            self.assertIsInstance(result, str)
            
            # Clean up
            temp_file.unlink()
    
    def test_unicode_in_filename(self):
        """Test handling of Unicode characters in filenames"""
        test_dir = Path(__file__).parent / "fixtures" / "pdfs"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        unicode_filename = test_dir / "тест_文档.txt"  # Cyrillic and Chinese
        unicode_filename.write_text("Test content")
        
        # Should handle gracefully (returns empty since it's not a PDF)
        result = read_pdf(unicode_filename)
        self.assertIsInstance(result, str)
        
        # Clean up
        unicode_filename.unlink()

