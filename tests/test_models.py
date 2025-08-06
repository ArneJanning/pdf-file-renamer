"""Tests for the models module."""
import pytest
from file_renamer.models import BibliographicInfo


class TestBibliographicInfo:
    """Test cases for BibliographicInfo model."""
    
    def test_create_with_author(self):
        """Test creating BibliographicInfo with author."""
        info = BibliographicInfo(
            author="F. Scott Fitzgerald",
            author_last="Fitzgerald",
            year="1925",
            title="The Great Gatsby"
        )
        assert info.author == "F. Scott Fitzgerald"
        assert info.author_last == "Fitzgerald"
        assert info.year == "1925"
        assert info.title == "The Great Gatsby"
        assert info.editor is None
        assert info.editor_last is None
    
    def test_create_with_editor(self):
        """Test creating BibliographicInfo with editor."""
        info = BibliographicInfo(
            editor="John Smith",
            editor_last="Smith",
            year="2023",
            title="Handbook of AI"
        )
        assert info.author is None
        assert info.author_last is None
        assert info.editor == "John Smith"
        assert info.editor_last == "Smith"
        assert info.year == "2023"
        assert info.title == "Handbook of AI"
    
    def test_create_minimal(self):
        """Test creating BibliographicInfo with minimal data."""
        info = BibliographicInfo(title="Unknown Paper")
        assert info.author is None
        assert info.author_last is None
        assert info.editor is None
        assert info.editor_last is None
        assert info.year is None
        assert info.title == "Unknown Paper"
    
    def test_author_or_editor_property(self):
        """Test author_or_editor property."""
        # With author
        info = BibliographicInfo(
            author="F. Scott Fitzgerald",
            title="The Great Gatsby"
        )
        assert info.author_or_editor == "F. Scott Fitzgerald"
        
        # With editor only
        info = BibliographicInfo(
            editor="John Smith",
            title="Handbook"
        )
        assert info.author_or_editor == "John Smith (Ed.)"
        
        # With neither
        info = BibliographicInfo(title="Unknown")
        assert info.author_or_editor == "Unknown"
    
    def test_author_or_editor_last_property(self):
        """Test author_or_editor_last property."""
        # With author_last
        info = BibliographicInfo(
            author="F. Scott Fitzgerald",
            author_last="Fitzgerald",
            title="The Great Gatsby"
        )
        assert info.author_or_editor_last == "Fitzgerald"
        
        # With editor_last only
        info = BibliographicInfo(
            editor="John Smith",
            editor_last="Smith",
            title="Handbook"
        )
        assert info.author_or_editor_last == "Smith"
        
        # With neither
        info = BibliographicInfo(title="Unknown")
        assert info.author_or_editor_last == "Unknown"
    
    def test_format_filename_basic(self):
        """Test basic filename formatting."""
        info = BibliographicInfo(
            author="F. Scott Fitzgerald",
            author_last="Fitzgerald",
            year="1925",
            title="The Great Gatsby"
        )
        
        # Default template
        template = "{author_or_editor_last} {year} - {title}.pdf"
        filename = info.format_filename(template)
        assert filename == "Fitzgerald 1925 - The Great Gatsby.pdf"
    
    def test_format_filename_all_variables(self):
        """Test filename formatting with all variables."""
        info = BibliographicInfo(
            author="F. Scott Fitzgerald",
            author_last="Fitzgerald",
            editor="Jane Doe",
            editor_last="Doe",
            year="1925",
            title="The Great Gatsby"
        )
        
        template = "{author} | {author_last} | {editor} | {editor_last} | {year} | {title}.pdf"
        filename = info.format_filename(template)
        assert filename == "F. Scott Fitzgerald | Fitzgerald | Jane Doe | Doe | 1925 | The Great Gatsby.pdf"
    
    def test_format_filename_missing_values(self):
        """Test filename formatting with missing values."""
        info = BibliographicInfo(title="Unknown Paper")
        
        template = "{author_or_editor_last} {year} - {title}.pdf"
        filename = info.format_filename(template)
        assert filename == "Unknown Unknown Year - Unknown Paper.pdf"
    
    def test_clean_for_filename(self):
        """Test filename cleaning functionality."""
        # Test with invalid characters
        info = BibliographicInfo(
            author='Author: Name/Test',
            author_last='Name*Test',
            title='Title: With <Invalid> Characters?'
        )
        
        template = "{author} - {title}.pdf"
        filename = info.format_filename(template)
        assert ':' not in filename
        assert '/' not in filename
        assert '<' not in filename
        assert '>' not in filename
        assert '?' not in filename
        assert '*' not in filename
    
    def test_clean_for_filename_long_title(self):
        """Test filename cleaning with very long title."""
        long_title = "A" * 250  # Very long title
        info = BibliographicInfo(
            author="Author",
            author_last="Author",
            title=long_title
        )
        
        template = "{title}.pdf"
        filename = info.format_filename(template)
        # Should be truncated but still end with .pdf
        assert len(filename) < 250
        assert filename.endswith("...pdf")
    
    def test_format_filename_multiple_spaces(self):
        """Test filename formatting removes multiple spaces."""
        info = BibliographicInfo(
            author="Author    Name",
            title="Title    With    Spaces"
        )
        
        template = "{author} - {title}.pdf"
        filename = info.format_filename(template)
        assert "    " not in filename
        assert filename == "Author Name - Title With Spaces.pdf"
    
    def test_complex_template(self):
        """Test complex custom templates."""
        info = BibliographicInfo(
            author="Jane Doe",
            author_last="Doe",
            year="2023",
            title="Machine Learning"
        )
        
        # Academic style
        template = "{author_last}, {author} ({year}). {title}.pdf"
        filename = info.format_filename(template)
        assert filename == "Doe, Jane Doe (2023). Machine Learning.pdf"
        
        # Minimal style
        template = "{author_last}-{year}-{title}.pdf"
        filename = info.format_filename(template)
        assert filename == "Doe-2023-Machine Learning.pdf"
        
        # Library style
        template = "[{year}] {author_or_editor} - {title}.pdf"
        filename = info.format_filename(template)
        assert filename == "[2023] Jane Doe - Machine Learning.pdf"