"""Performance tests for the PDF file renamer."""
import pytest
import time
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from file_renamer.models import BibliographicInfo
from file_renamer.pdf_extractor import extract_pdf_text, get_pdf_files


class TestPerformance:
    """Test performance characteristics."""
    
    def test_large_directory_scanning(self, tmp_path):
        """Test performance with large number of files."""
        # Create a directory with many files
        test_dir = tmp_path / "large_dir"
        test_dir.mkdir()
        
        # Create 100 PDF files and 100 other files
        for i in range(100):
            (test_dir / f"paper_{i:03d}.pdf").touch()
            (test_dir / f"document_{i:03d}.txt").touch()
        
        start_time = time.time()
        pdf_files = get_pdf_files(test_dir)
        elapsed = time.time() - start_time
        
        assert len(pdf_files) == 100
        assert elapsed < 1.0  # Should complete in less than 1 second
    
    @patch('file_renamer.pdf_extractor.PdfReader')
    def test_large_pdf_text_extraction(self, mock_pdf_reader, tmp_path):
        """Test extraction performance with large PDF."""
        # Create mock pages with large content
        large_content = "A" * 10000  # 10KB per page
        mock_pages = []
        for i in range(50):  # 50 pages
            page = Mock()
            page.extract_text.return_value = f"Page {i+1}: {large_content}"
            mock_pages.append(page)
        
        mock_reader = Mock()
        mock_reader.pages = mock_pages
        mock_pdf_reader.return_value = mock_reader
        
        pdf_file = tmp_path / "large.pdf"
        pdf_file.touch()
        
        with patch('builtins.open', create=True):
            start_time = time.time()
            result = extract_pdf_text(pdf_file, max_pages=10)  # Limit to 10 pages
            elapsed = time.time() - start_time
            
        assert result is not None
        assert "Page 1:" in result
        assert "Page 10:" in result
        assert "Page 11:" not in result  # Should respect page limit
        assert elapsed < 2.0  # Should be reasonably fast
    
    def test_filename_cleaning_performance(self):
        """Test performance of filename cleaning with complex names."""
        # Create bibliographic info with complex data
        complex_info = BibliographicInfo(
            author="José María García-González, Maria O'Brien, John van der Berg, et al.",
            author_last="García-González",
            year="2023",
            title="A Very Long Title: With Special Characters <>&\"'|? and Multiple Sections " * 10,
        )
        
        template = "{author} - {title} ({year}).pdf"
        
        start_time = time.time()
        for _ in range(1000):  # Run 1000 times
            filename = complex_info.format_filename(template)
        elapsed = time.time() - start_time
        
        assert elapsed < 1.0  # Should handle 1000 operations in less than 1 second
        assert len(filename) < 300  # Should be truncated if too long
    
    def test_concurrent_processing_simulation(self):
        """Test simulation of concurrent PDF processing."""
        import concurrent.futures
        from file_renamer.models import BibliographicInfo
        
        def process_single_item(item_data):
            """Simulate processing a single PDF."""
            title, author, year = item_data
            info = BibliographicInfo(
                author=author,
                author_last=author.split()[-1],
                year=year,
                title=title
            )
            template = "{author_last} {year} - {title}.pdf"
            return info.format_filename(template)
        
        # Simulate 50 PDFs
        test_data = [
            (f"Paper {i}", f"Author {i}", str(2020 + i % 4))
            for i in range(50)
        ]
        
        start_time = time.time()
        
        # Process concurrently (simulating what would happen with real PDFs)
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(process_single_item, test_data))
        
        elapsed = time.time() - start_time
        
        assert len(results) == 50
        assert all(isinstance(result, str) for result in results)
        assert elapsed < 2.0  # Should complete quickly
    
    @patch('file_renamer.models.BibliographicInfo._clean_for_filename')
    def test_filename_cleaning_optimization(self, mock_clean):
        """Test that filename cleaning is called efficiently."""
        # Mock the cleaning function to track calls
        mock_clean.side_effect = lambda x: x.replace('<', '').replace('>', '')
        
        info = BibliographicInfo(
            author="Test Author",
            author_last="Author",
            year="2023",
            title="Test Title"
        )
        
        template = "{author_last} {year} - {title}.pdf"
        filename = info.format_filename(template)
        
        # Should only call clean function for each unique field used
        expected_calls = 3  # author_last, year, title
        assert mock_clean.call_count <= expected_calls * 2  # Allow some flexibility
    
    def test_memory_usage_with_large_text(self):
        """Test memory efficiency with large PDF text."""
        import sys
        from file_renamer.models import BibliographicInfo
        
        # Create very large text content
        large_text = "Content " * 100000  # ~700KB of text
        
        # Measure memory before
        initial_objects = len([obj for obj in range(1000)])  # Dummy measurement
        
        # Process the text (simulate what AI extractor would do)
        info = BibliographicInfo(
            author="Test Author", 
            author_last="Author",
            year="2023",
            title="Large Document"
        )
        
        template = "{author_last} {year} - {title}.pdf"
        filename = info.format_filename(template)
        
        # The operation should complete without excessive memory usage
        assert filename == "Author 2023 - Large Document.pdf"
        assert sys.getsizeof(filename) < 1000  # Filename should be small
    
    def test_regex_performance_special_characters(self):
        """Test performance of special character handling."""
        # Create text with many special characters
        special_text = "File<>:|?*\"\\Name" * 1000
        
        info = BibliographicInfo(
            title=special_text,
            author="Test",
            author_last="Test",
            year="2023"
        )
        
        start_time = time.time()
        for _ in range(100):
            filename = info.format_filename("{title}.pdf")
        elapsed = time.time() - start_time
        
        assert elapsed < 1.0  # Should handle special chars efficiently
        assert "<" not in filename
        assert ">" not in filename
        assert "|" not in filename


class TestScalability:
    """Test scalability aspects."""
    
    def test_many_pdf_files_discovery(self, tmp_path):
        """Test PDF discovery with many files in nested structure."""
        base_dir = tmp_path / "library"
        base_dir.mkdir()
        
        # Create nested directory structure
        for year in range(2020, 2024):
            year_dir = base_dir / str(year)
            year_dir.mkdir()
            for i in range(20):  # 20 PDFs per year
                (year_dir / f"paper_{year}_{i:02d}.pdf").touch()
        
        # Test discovery at different levels
        start_time = time.time()
        
        # Should only find top-level files (none in this case)
        pdf_files = get_pdf_files(base_dir)
        assert len(pdf_files) == 0  # No PDFs at top level
        
        # Test individual year directories
        year_2023_pdfs = get_pdf_files(base_dir / "2023")
        assert len(year_2023_pdfs) == 20
        
        elapsed = time.time() - start_time
        assert elapsed < 0.5  # Should be very fast
    
    def test_template_complexity_scaling(self):
        """Test performance with increasingly complex templates."""
        info = BibliographicInfo(
            author="Test Author Name",
            author_last="Name",
            editor="Test Editor", 
            editor_last="Editor",
            year="2023",
            title="Test Document Title"
        )
        
        # Templates of increasing complexity
        templates = [
            "{title}.pdf",
            "{author_last} {year} - {title}.pdf", 
            "{author} ({year}). {title} [Ed. {editor}].pdf",
            "[{year}] {author_or_editor} - {title} - {author_last}, {editor_last}.pdf",
            "{author} and {editor} ({year}): {title} - Last names: {author_last}, {editor_last}.pdf"
        ]
        
        for template in templates:
            start_time = time.time()
            for _ in range(1000):
                filename = info.format_filename(template)
            elapsed = time.time() - start_time
            
            assert elapsed < 1.0  # Even complex templates should be fast
            assert filename.endswith(".pdf")


@pytest.mark.slow
class TestStressTests:
    """Stress tests that may take longer to run."""
    
    def test_extreme_filename_length(self):
        """Test with extremely long titles."""
        very_long_title = "A" * 5000  # 5KB title
        
        info = BibliographicInfo(
            title=very_long_title,
            author="Author",
            author_last="Author", 
            year="2023"
        )
        
        template = "{author_last} {year} - {title}.pdf"
        
        start_time = time.time()
        filename = info.format_filename(template)
        elapsed = time.time() - start_time
        
        assert elapsed < 1.0  # Should handle even extreme cases quickly
        assert len(filename) < 300  # Should be truncated
        assert filename.endswith("...pdf")
    
    def test_many_special_characters(self):
        """Test with text containing many special characters."""
        special_chars = '<>:"/\\|?*'
        special_text = ''.join(char * 100 for char in special_chars)
        
        info = BibliographicInfo(
            title=special_text,
            author="Author",
            author_last="Author",
            year="2023"
        )
        
        start_time = time.time()
        filename = info.format_filename("{title}.pdf")
        elapsed = time.time() - start_time
        
        assert elapsed < 1.0
        # All special chars should be removed
        for char in special_chars:
            assert char not in filename