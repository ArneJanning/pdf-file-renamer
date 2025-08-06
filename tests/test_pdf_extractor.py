"""Tests for the pdf_extractor module."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from pypdf import PdfReader
from file_renamer.pdf_extractor import extract_pdf_text, get_pdf_files


class TestExtractPdfText:
    """Test cases for extract_pdf_text function."""
    
    @patch('file_renamer.pdf_extractor.open')
    @patch('file_renamer.pdf_extractor.PdfReader')
    def test_extract_text_success(self, mock_pdf_reader, mock_open):
        """Test successful text extraction from PDF."""
        # Mock PDF pages
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "Page 1 content"
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = "Page 2 content"
        
        # Mock PDF reader
        mock_reader = Mock()
        mock_reader.pages = [mock_page1, mock_page2]
        mock_pdf_reader.return_value = mock_reader
        
        # Mock file open
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        # Test extraction
        result = extract_pdf_text(Path("/test/file.pdf"), max_pages=2)
        
        assert result == "--- Page 1 ---\nPage 1 content\n\n--- Page 2 ---\nPage 2 content"
        mock_open.assert_called_once_with(Path("/test/file.pdf"), 'rb')
        mock_pdf_reader.assert_called_once_with(mock_file)
    
    @patch('file_renamer.pdf_extractor.open')
    @patch('file_renamer.pdf_extractor.PdfReader')
    def test_extract_text_limited_pages(self, mock_pdf_reader, mock_open):
        """Test text extraction with page limit."""
        # Mock 5 pages but only extract 3
        mock_pages = []
        for i in range(5):
            page = Mock()
            page.extract_text.return_value = f"Page {i+1} content"
            mock_pages.append(page)
        
        mock_reader = Mock()
        mock_reader.pages = mock_pages
        mock_pdf_reader.return_value = mock_reader
        
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        result = extract_pdf_text(Path("/test/file.pdf"), max_pages=3)
        
        # Should only have 3 pages
        assert "Page 1 content" in result
        assert "Page 2 content" in result
        assert "Page 3 content" in result
        assert "Page 4 content" not in result
        assert "Page 5 content" not in result
    
    @patch('file_renamer.pdf_extractor.open')
    @patch('file_renamer.pdf_extractor.PdfReader')
    def test_extract_text_empty_pages(self, mock_pdf_reader, mock_open):
        """Test extraction with empty pages."""
        # Mock pages with empty content
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = "   "  # Only whitespace
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = ""  # Empty
        mock_page3 = Mock()
        mock_page3.extract_text.return_value = "Valid content"
        
        mock_reader = Mock()
        mock_reader.pages = [mock_page1, mock_page2, mock_page3]
        mock_pdf_reader.return_value = mock_reader
        
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        result = extract_pdf_text(Path("/test/file.pdf"))
        
        # Should only include page with valid content
        assert result == "--- Page 3 ---\nValid content"
    
    @patch('file_renamer.pdf_extractor.open')
    @patch('file_renamer.pdf_extractor.PdfReader')
    def test_extract_text_no_content(self, mock_pdf_reader, mock_open):
        """Test extraction when no text can be extracted."""
        # Mock pages with no extractable content
        mock_page = Mock()
        mock_page.extract_text.return_value = ""
        
        mock_reader = Mock()
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader
        
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        result = extract_pdf_text(Path("/test/file.pdf"))
        
        assert result is None
    
    @patch('file_renamer.pdf_extractor.open')
    @patch('file_renamer.pdf_extractor.PdfReader')
    @patch('file_renamer.pdf_extractor.logger')
    def test_extract_text_exception(self, mock_logger, mock_pdf_reader, mock_open):
        """Test extraction handles exceptions gracefully."""
        mock_open.side_effect = FileNotFoundError("File not found")
        
        result = extract_pdf_text(Path("/test/nonexistent.pdf"))
        
        assert result is None
        mock_logger.error.assert_called_once()
        assert "Error extracting text" in mock_logger.error.call_args[0][0]
    
    @patch('file_renamer.pdf_extractor.open')
    @patch('file_renamer.pdf_extractor.PdfReader')
    def test_extract_text_single_page(self, mock_pdf_reader, mock_open):
        """Test extraction from single-page PDF."""
        mock_page = Mock()
        mock_page.extract_text.return_value = "Single page content"
        
        mock_reader = Mock()
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader
        
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        result = extract_pdf_text(Path("/test/file.pdf"))
        
        assert result == "--- Page 1 ---\nSingle page content"
    
    @patch('file_renamer.pdf_extractor.open')
    @patch('file_renamer.pdf_extractor.PdfReader')
    def test_extract_text_corrupted_pdf(self, mock_pdf_reader, mock_open):
        """Test extraction from corrupted PDF."""
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        mock_pdf_reader.side_effect = Exception("Invalid PDF structure")
        
        result = extract_pdf_text(Path("/test/corrupted.pdf"))
        
        assert result is None


class TestGetPdfFiles:
    """Test cases for get_pdf_files function."""
    
    def test_get_pdf_files_success(self, tmp_path):
        """Test getting PDF files from directory."""
        # Create test files
        (tmp_path / "file1.pdf").touch()
        (tmp_path / "file2.pdf").touch()
        (tmp_path / "file3.PDF").touch()  # Different case
        (tmp_path / "document.txt").touch()  # Non-PDF
        (tmp_path / "report.docx").touch()  # Non-PDF
        
        pdf_files = get_pdf_files(tmp_path)
        
        assert len(pdf_files) == 2  # Only .pdf extension (case-sensitive)
        pdf_names = [f.name for f in pdf_files]
        assert "file1.pdf" in pdf_names
        assert "file2.pdf" in pdf_names
        assert "file3.PDF" not in pdf_names  # glob is case-sensitive
    
    def test_get_pdf_files_empty_directory(self, tmp_path):
        """Test getting PDF files from empty directory."""
        pdf_files = get_pdf_files(tmp_path)
        assert pdf_files == []
    
    def test_get_pdf_files_no_pdfs(self, tmp_path):
        """Test directory with no PDF files."""
        (tmp_path / "file.txt").touch()
        (tmp_path / "document.docx").touch()
        
        pdf_files = get_pdf_files(tmp_path)
        assert pdf_files == []
    
    def test_get_pdf_files_nested_structure(self, tmp_path):
        """Test that only top-level PDFs are returned."""
        # Create PDFs at different levels
        (tmp_path / "top.pdf").touch()
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "nested.pdf").touch()
        
        pdf_files = get_pdf_files(tmp_path)
        
        assert len(pdf_files) == 1
        assert pdf_files[0].name == "top.pdf"
    
    def test_get_pdf_files_nonexistent_directory(self):
        """Test error when directory doesn't exist."""
        with pytest.raises(ValueError, match="does not exist"):
            get_pdf_files(Path("/nonexistent/directory"))
    
    def test_get_pdf_files_file_instead_of_directory(self, tmp_path):
        """Test error when path is a file instead of directory."""
        file_path = tmp_path / "file.txt"
        file_path.touch()
        
        with pytest.raises(ValueError, match="is not a directory"):
            get_pdf_files(file_path)
    
    def test_get_pdf_files_special_names(self, tmp_path):
        """Test handling of PDFs with special names."""
        # Create PDFs with special characters
        (tmp_path / "file with spaces.pdf").touch()
        (tmp_path / "file-with-dashes.pdf").touch()
        (tmp_path / "file_with_underscores.pdf").touch()
        (tmp_path / "file.multiple.dots.pdf").touch()
        
        pdf_files = get_pdf_files(tmp_path)
        
        assert len(pdf_files) == 4
        pdf_names = [f.name for f in pdf_files]
        assert "file with spaces.pdf" in pdf_names
        assert "file-with-dashes.pdf" in pdf_names
        assert "file_with_underscores.pdf" in pdf_names
        assert "file.multiple.dots.pdf" in pdf_names
    
    def test_get_pdf_files_returns_path_objects(self, tmp_path):
        """Test that Path objects are returned."""
        (tmp_path / "test.pdf").touch()
        
        pdf_files = get_pdf_files(tmp_path)
        
        assert len(pdf_files) == 1
        assert isinstance(pdf_files[0], Path)
        assert pdf_files[0].is_file()
        assert pdf_files[0].suffix == ".pdf"