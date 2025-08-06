"""Pytest configuration and fixtures."""
import pytest
from pathlib import Path
from unittest.mock import Mock
from fpdf import FPDF
import tempfile
import os
from file_renamer.models import BibliographicInfo


@pytest.fixture
def sample_bib_info():
    """Sample bibliographic information for testing."""
    return BibliographicInfo(
        author="F. Scott Fitzgerald",
        author_last="Fitzgerald",
        year="1925",
        title="The Great Gatsby"
    )


@pytest.fixture
def sample_bib_info_with_editor():
    """Sample bibliographic information with editor for testing."""
    return BibliographicInfo(
        editor="John Smith",
        editor_last="Smith",
        year="2023",
        title="Handbook of AI"
    )


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        'api_key': 'test-api-key',
        'model_name': 'claude-3-5-sonnet-20241022',
        'filename_template': '{author_or_editor_last} {year} - {title}.pdf',
        'max_pages': 10
    }


@pytest.fixture
def mock_extractor():
    """Mock BibliographicExtractor for testing."""
    mock = Mock()
    mock.extract_info.return_value = BibliographicInfo(
        author="Test Author",
        author_last="Author",
        year="2023",
        title="Test Document"
    )
    return mock


@pytest.fixture
def temp_pdf_dir(tmp_path):
    """Create a temporary directory with sample PDF files."""
    pdf_dir = tmp_path / "pdfs"
    pdf_dir.mkdir()
    
    # Create some dummy PDF files
    for name in ["paper1.pdf", "paper2.pdf", "document.pdf"]:
        (pdf_dir / name).touch()
    
    # Create some non-PDF files that should be ignored
    (pdf_dir / "readme.txt").touch()
    (pdf_dir / "image.jpg").touch()
    
    return pdf_dir


@pytest.fixture
def sample_pdf_text():
    """Sample PDF text content for testing."""
    return """--- Page 1 ---
The Great Gatsby

by F. Scott Fitzgerald

Published: 1925

--- Page 2 ---
In my younger and more vulnerable years my father gave me some advice
that I've been turning over in my mind ever since.

"Whenever you feel like criticizing anyone," he told me, "just remember
that all the people in this world haven't had the advantages that you've had."
"""


@pytest.fixture
def complex_pdf_text():
    """Complex PDF text with multiple authors."""
    return """--- Page 1 ---
Advanced Machine Learning Techniques

José María García-González, Maria O'Brien, and John van der Berg

Department of Computer Science
University of Technology

2023

--- Page 2 ---
Abstract

This paper presents advanced techniques in machine learning...
"""


@pytest.fixture
def empty_pdf_text():
    """Empty PDF text for testing error cases."""
    return ""


@pytest.fixture
def create_test_pdf():
    """Factory function to create test PDF files."""
    def _create_pdf(title, author, year, content="Test content"):
        """Create a test PDF file with given metadata."""
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, title, ln=True, align='C')
        pdf.ln(10)
        
        # Author
        pdf.set_font("Arial", "", 12)
        pdf.cell(200, 10, f"by {author}", ln=True, align='C')
        pdf.ln(5)
        
        # Year
        pdf.cell(200, 10, f"Published: {year}", ln=True, align='C')
        pdf.ln(10)
        
        # Content
        pdf.set_font("Arial", "", 10)
        pdf.multi_cell(0, 10, content)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
            pdf.output(tmp_file.name)
            return Path(tmp_file.name)
    
    return _create_pdf


@pytest.fixture
def mock_api_response():
    """Mock API response from Claude."""
    return BibliographicInfo(
        author="Test Author",
        author_last="Author",
        editor=None,
        editor_last=None,
        year="2023",
        title="Test Document"
    )


@pytest.fixture(autouse=True)
def clean_environment():
    """Clean environment variables before each test."""
    # Store original environment
    original_env = os.environ.copy()
    
    # Clean test-related env vars
    for key in ['ANTHROPIC_API_KEY', 'FILENAME_TEMPLATE', 'MAX_PAGES_TO_EXTRACT', 'CLAUDE_MODEL']:
        if key in os.environ:
            del os.environ[key]
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


class MockPdfReader:
    """Mock PDF reader for testing."""
    
    def __init__(self, pages_content=None):
        """Initialize with page content."""
        self.pages_content = pages_content or ["Test page content"]
        self.pages = [MockPage(content) for content in self.pages_content]


class MockPage:
    """Mock PDF page for testing."""
    
    def __init__(self, content):
        """Initialize with content."""
        self._content = content
    
    def extract_text(self):
        """Return the page content."""
        return self._content


@pytest.fixture
def mock_pdf_reader():
    """Factory for creating mock PDF readers."""
    def _create_reader(pages_content):
        return MockPdfReader(pages_content)
    return _create_reader


@pytest.fixture
def test_env_file(tmp_path):
    """Create a test .env file."""
    env_file = tmp_path / ".env"
    env_content = """
ANTHROPIC_API_KEY=test-key-12345
FILENAME_TEMPLATE={author_last} {year} - {title}.pdf
MAX_PAGES_TO_EXTRACT=5
CLAUDE_MODEL=claude-3-haiku-20240307
"""
    env_file.write_text(env_content.strip())
    return env_file


@pytest.fixture
def invalid_filename_chars():
    """Characters that are invalid in filenames."""
    return '<>:"/\\|?*'


@pytest.fixture
def long_text():
    """Very long text for testing truncation."""
    return "A" * 1000


# Test data for various scenarios
TEST_CASES = {
    'simple': {
        'author': 'John Doe',
        'year': '2023',
        'title': 'Simple Paper',
        'expected_filename': 'Doe 2023 - Simple Paper.pdf'
    },
    'complex_names': {
        'author': 'José María García-González',
        'year': '2022',
        'title': 'Complex Names Study',
        'expected_filename': 'García-González 2022 - Complex Names Study.pdf'
    },
    'with_editor': {
        'editor': 'Jane Smith',
        'year': '2021',
        'title': 'Edited Volume',
        'expected_filename': 'Smith 2021 - Edited Volume.pdf'
    },
    'special_chars': {
        'author': 'Author Name',
        'year': '2023',
        'title': 'Title: With <Special> Characters?',
        'expected_filename': 'Name 2023 - Title With Special Characters.pdf'
    },
    'no_year': {
        'author': 'Unknown Author',
        'title': 'No Year Paper',
        'expected_filename': 'Author Unknown Year - No Year Paper.pdf'
    }
}


@pytest.fixture(params=TEST_CASES.keys())
def test_case(request):
    """Parametrized fixture for test cases."""
    return TEST_CASES[request.param]