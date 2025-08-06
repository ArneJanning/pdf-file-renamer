"""Tests for package-level functionality."""
import pytest
from file_renamer import __version__


def test_version():
    """Test that version is defined and valid."""
    assert __version__ == "0.1.0"


def test_package_imports():
    """Test that main modules can be imported."""
    from file_renamer import models
    from file_renamer import pdf_extractor  
    from file_renamer import ai_extractor
    from file_renamer import cli
    
    # Check key classes/functions exist
    assert hasattr(models, 'BibliographicInfo')
    assert hasattr(pdf_extractor, 'extract_pdf_text')
    assert hasattr(pdf_extractor, 'get_pdf_files')
    assert hasattr(ai_extractor, 'BibliographicExtractor')
    assert hasattr(cli, 'main')


def test_main_module():
    """Test that package can be run as module."""
    import file_renamer.__main__
    # Should not raise any import errors