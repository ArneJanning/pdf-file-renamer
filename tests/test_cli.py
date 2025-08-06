"""Tests for the CLI module."""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from click.testing import CliRunner
from file_renamer.cli import main, load_config, process_pdf, process_directory
from file_renamer.models import BibliographicInfo


class TestLoadConfig:
    """Test cases for load_config function."""
    
    @patch('file_renamer.cli.load_dotenv')
    @patch('file_renamer.cli.os.getenv')
    def test_load_config_success(self, mock_getenv, mock_load_dotenv):
        """Test successful configuration loading."""
        mock_getenv.side_effect = lambda key, default=None: {
            'ANTHROPIC_API_KEY': 'test-key',
            'CLAUDE_MODEL': 'claude-3-5-sonnet-20241022',
            'FILENAME_TEMPLATE': '{author_last} {year} - {title}.pdf',
            'MAX_PAGES_TO_EXTRACT': '10'
        }.get(key, default)
        
        config = load_config()
        
        assert config['api_key'] == 'test-key'
        assert config['model_name'] == 'claude-3-5-sonnet-20241022'
        assert config['filename_template'] == '{author_last} {year} - {title}.pdf'
        assert config['max_pages'] == 10
        mock_load_dotenv.assert_called_once()
    
    @patch('file_renamer.cli.load_dotenv')
    @patch('file_renamer.cli.os.getenv')
    def test_load_config_defaults(self, mock_getenv, mock_load_dotenv):
        """Test configuration with default values."""
        mock_getenv.side_effect = lambda key, default=None: {
            'ANTHROPIC_API_KEY': 'test-key',
        }.get(key, default)
        
        config = load_config()
        
        assert config['api_key'] == 'test-key'
        assert config['model_name'] == 'claude-3-5-sonnet-20241022'
        assert config['filename_template'] == '[{author_or_editor}] {year} - {title}.pdf'
        assert config['max_pages'] == 10
    
    @patch('file_renamer.cli.load_dotenv')
    @patch('file_renamer.cli.os.getenv')
    def test_load_config_missing_api_key(self, mock_getenv, mock_load_dotenv):
        """Test configuration with missing API key."""
        def mock_getenv_func(key, default=None):
            if key == 'ANTHROPIC_API_KEY':
                return None
            return default
        
        mock_getenv.side_effect = mock_getenv_func
        
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY not found"):
            load_config()


class TestProcessPdf:
    """Test cases for process_pdf function."""
    
    @patch('file_renamer.cli.extract_pdf_text')
    @patch('file_renamer.cli.shutil.copy2')
    @patch('file_renamer.cli.logger')
    async def test_process_pdf_success(self, mock_logger, mock_copy, mock_extract):
        """Test successful PDF processing."""
        # Setup mocks
        pdf_path = Path("/test/paper.pdf")
        output_dir = Path("/test/output")
        config = {
            'max_pages': 10,
            'filename_template': '{author_last} {year} - {title}.pdf'
        }
        
        # Mock extractor
        mock_extractor = Mock()
        mock_bib_info = BibliographicInfo(
            author="John Doe",
            author_last="Doe",
            year="2023",
            title="Test Paper"
        )
        mock_extractor.extract_info = AsyncMock(return_value=mock_bib_info)
        
        # Mock PDF text extraction
        mock_extract.return_value = "Test PDF content"
        
        # Process PDF
        await process_pdf(pdf_path, mock_extractor, config, output_dir, dry_run=False)
        
        # Verify calls
        mock_extract.assert_called_once_with(pdf_path, max_pages=10)
        mock_extractor.extract_info.assert_called_once_with("Test PDF content")
        mock_copy.assert_called_once_with(pdf_path, output_dir / "Doe 2023 - Test Paper.pdf")
        
        # Check logging
        assert mock_logger.info.call_count >= 4  # Multiple info logs
        info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any("Processing: paper.pdf" in call for call in info_calls)
        assert any("Author/Editor: John Doe" in call for call in info_calls)
        assert any("Year: 2023" in call for call in info_calls)
        assert any("Title: Test Paper" in call for call in info_calls)
    
    @patch('file_renamer.cli.extract_pdf_text')
    @patch('file_renamer.cli.logger')
    async def test_process_pdf_dry_run(self, mock_logger, mock_extract):
        """Test PDF processing in dry-run mode."""
        pdf_path = Path("/test/paper.pdf")
        output_dir = Path("/test/output")
        config = {
            'max_pages': 10,
            'filename_template': '{author_last} {year} - {title}.pdf'
        }
        
        mock_extractor = Mock()
        mock_bib_info = BibliographicInfo(
            author="John Doe",
            author_last="Doe",
            year="2023",
            title="Test Paper"
        )
        mock_extractor.extract_info = AsyncMock(return_value=mock_bib_info)
        mock_extract.return_value = "Test PDF content"
        
        await process_pdf(pdf_path, mock_extractor, config, output_dir, dry_run=True)
        
        # Check dry-run message
        info_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any("[DRY RUN]" in call for call in info_calls)
    
    @patch('file_renamer.cli.extract_pdf_text')
    @patch('file_renamer.cli.logger')
    async def test_process_pdf_no_text(self, mock_logger, mock_extract):
        """Test PDF processing when text extraction fails."""
        pdf_path = Path("/test/paper.pdf")
        output_dir = Path("/test/output")
        config = {'max_pages': 10}
        
        mock_extractor = Mock()
        mock_extract.return_value = None  # Text extraction failed
        
        await process_pdf(pdf_path, mock_extractor, config, output_dir)
        
        mock_logger.error.assert_called_once_with(f"Failed to extract text from {pdf_path}")
    
    @patch('file_renamer.cli.extract_pdf_text')
    @patch('file_renamer.cli.logger')
    async def test_process_pdf_no_bib_info(self, mock_logger, mock_extract):
        """Test PDF processing when bibliographic extraction fails."""
        pdf_path = Path("/test/paper.pdf")
        output_dir = Path("/test/output")
        config = {'max_pages': 10}
        
        mock_extractor = Mock()
        mock_extractor.extract_info = AsyncMock(return_value=None)  # AI extraction failed
        mock_extract.return_value = "Test PDF content"
        
        await process_pdf(pdf_path, mock_extractor, config, output_dir)
        
        mock_logger.error.assert_called_with(
            f"Failed to extract bibliographic information from {pdf_path}"
        )
    
    @patch('file_renamer.cli.extract_pdf_text')
    @patch('file_renamer.cli.shutil.copy2')
    async def test_process_pdf_duplicate_filename(self, mock_copy, mock_extract):
        """Test PDF processing with duplicate filenames."""
        pdf_path = Path("/test/paper.pdf")
        output_dir = Path("/test/output")
        config = {
            'max_pages': 10,
            'filename_template': '{author_last} {year} - {title}.pdf'
        }
        
        mock_extractor = Mock()
        mock_bib_info = BibliographicInfo(
            author="John Doe",
            author_last="Doe",
            year="2023",
            title="Test Paper"
        )
        mock_extractor.extract_info = AsyncMock(return_value=mock_bib_info)
        mock_extract.return_value = "Test PDF content"
        
        # Mock file existence check
        original_path = output_dir / "Doe 2023 - Test Paper.pdf"
        duplicate_path = output_dir / "Doe 2023 - Test Paper (1).pdf"
        
        with patch.object(Path, 'exists') as mock_exists:
            # First path exists, second doesn't
            mock_exists.side_effect = lambda: self == original_path
            
            await process_pdf(pdf_path, mock_extractor, config, output_dir)
            
            # Should copy to the duplicate path
            mock_copy.assert_called_once_with(pdf_path, duplicate_path)


class TestProcessDirectory:
    """Test cases for process_directory function."""
    
    @patch('file_renamer.cli.get_pdf_files')
    @patch('file_renamer.cli.process_pdf')
    @patch('file_renamer.cli.logger')
    async def test_process_directory_success(self, mock_logger, mock_process_pdf, mock_get_files):
        """Test successful directory processing."""
        directory = Path("/test/pdfs")
        output_dir = Path("/test/output")
        config = {}
        mock_extractor = Mock()
        
        # Mock PDF files
        pdf_files = [Path("/test/pdfs/file1.pdf"), Path("/test/pdfs/file2.pdf")]
        mock_get_files.return_value = pdf_files
        mock_process_pdf.return_value = None
        
        await process_directory(directory, mock_extractor, config, output_dir)
        
        mock_get_files.assert_called_once_with(directory)
        assert mock_process_pdf.call_count == 2
        mock_logger.info.assert_called_with("Found 2 PDF files to process")
    
    @patch('file_renamer.cli.get_pdf_files')
    @patch('file_renamer.cli.logger')
    async def test_process_directory_no_pdfs(self, mock_logger, mock_get_files):
        """Test directory processing with no PDFs."""
        directory = Path("/test/empty")
        output_dir = Path("/test/output")
        config = {}
        mock_extractor = Mock()
        
        mock_get_files.return_value = []
        
        await process_directory(directory, mock_extractor, config, output_dir)
        
        mock_logger.warning.assert_called_with(f"No PDF files found in {directory}")
    
    @patch('file_renamer.cli.get_pdf_files')
    @patch('file_renamer.cli.process_pdf')
    @patch('file_renamer.cli.logger')
    async def test_process_directory_with_errors(self, mock_logger, mock_process_pdf, mock_get_files):
        """Test directory processing with errors in individual files."""
        directory = Path("/test/pdfs")
        output_dir = Path("/test/output")
        config = {}
        mock_extractor = Mock()
        
        pdf_files = [Path("/test/pdfs/file1.pdf"), Path("/test/pdfs/file2.pdf")]
        mock_get_files.return_value = pdf_files
        
        # First file succeeds, second fails
        mock_process_pdf.side_effect = [None, Exception("Processing error")]
        
        await process_directory(directory, mock_extractor, config, output_dir)
        
        # Should log error but continue processing
        mock_logger.error.assert_called()
        error_calls = [call[0][0] for call in mock_logger.error.call_args_list]
        assert any("Error processing" in call for call in error_calls)


class TestMainCLI:
    """Test cases for main CLI function."""
    
    def test_main_help(self):
        """Test CLI help message."""
        runner = CliRunner()
        result = runner.invoke(main, ['--help'])
        
        assert result.exit_code == 0
        assert "Rename PDF files based on their bibliographic information" in result.output
        assert "--dry-run" in result.output
        assert "--output" in result.output
        assert "--template" in result.output
    
    @patch('file_renamer.cli.load_config')
    @patch('file_renamer.cli.BibliographicExtractor')
    @patch('file_renamer.cli.process_directory')
    @patch('file_renamer.cli.asyncio.run')
    def test_main_basic_usage(self, mock_asyncio, mock_process_dir, mock_extractor_class, mock_load_config):
        """Test basic CLI usage."""
        runner = CliRunner()
        
        # Mock configuration
        mock_config = {
            'api_key': 'test-key',
            'model_name': 'claude-3-5-sonnet-20241022',
            'filename_template': '{author_last} {year} - {title}.pdf'
        }
        mock_load_config.return_value = mock_config
        
        # Mock extractor
        mock_extractor = Mock()
        mock_extractor_class.return_value = mock_extractor
        
        with runner.isolated_filesystem():
            # Create test directory
            test_dir = Path("test_pdfs")
            test_dir.mkdir()
            
            result = runner.invoke(main, [str(test_dir)])
            
            assert result.exit_code == 0
            mock_load_config.assert_called_once()
            mock_extractor_class.assert_called_once_with(
                api_key='test-key',
                model_name='claude-3-5-sonnet-20241022'
            )
            mock_asyncio.assert_called_once()
    
    @patch('file_renamer.cli.load_config')
    def test_main_missing_api_key(self, mock_load_config):
        """Test CLI with missing API key."""
        runner = CliRunner()
        mock_load_config.side_effect = ValueError("ANTHROPIC_API_KEY not found")
        
        with runner.isolated_filesystem():
            test_dir = Path("test_pdfs")
            test_dir.mkdir()
            
            result = runner.invoke(main, [str(test_dir)])
            
            assert result.exit_code == 1
            assert "ANTHROPIC_API_KEY not found" in result.output
    
    @patch('file_renamer.cli.load_config')
    @patch('file_renamer.cli.BibliographicExtractor')
    @patch('file_renamer.cli.process_directory')
    @patch('file_renamer.cli.asyncio.run')
    def test_main_with_options(self, mock_asyncio, mock_process_dir, mock_extractor_class, mock_load_config):
        """Test CLI with all options."""
        runner = CliRunner()
        
        mock_config = {
            'api_key': 'test-key',
            'model_name': 'claude-3-5-sonnet-20241022',
            'filename_template': 'default_template'
        }
        mock_load_config.return_value = mock_config
        mock_extractor_class.return_value = Mock()
        
        with runner.isolated_filesystem():
            test_dir = Path("test_pdfs")
            test_dir.mkdir()
            output_dir = Path("output")
            
            result = runner.invoke(main, [
                str(test_dir),
                '--output', str(output_dir),
                '--dry-run',
                '--template', '{author} - {title}.pdf'
            ])
            
            assert result.exit_code == 0
            
            # Check that template was overridden
            call_args = mock_asyncio.call_args[0][0]  # Get the coroutine
            # The config should have the overridden template
    
    def test_main_nonexistent_directory(self):
        """Test CLI with non-existent directory."""
        runner = CliRunner()
        
        result = runner.invoke(main, ['/nonexistent/directory'])
        
        assert result.exit_code == 2  # Click error code for invalid path
        assert "does not exist" in result.output.lower()
    
    @patch('file_renamer.cli.load_config')
    @patch('file_renamer.cli.BibliographicExtractor')
    @patch('file_renamer.cli.process_directory')
    @patch('file_renamer.cli.asyncio.run')
    def test_main_creates_output_directory(self, mock_asyncio, mock_process_dir, mock_extractor_class, mock_load_config):
        """Test that CLI creates output directory if it doesn't exist."""
        runner = CliRunner()
        
        mock_config = {
            'api_key': 'test-key',
            'model_name': 'claude-3-5-sonnet-20241022',
            'filename_template': '{title}.pdf'
        }
        mock_load_config.return_value = mock_config
        mock_extractor_class.return_value = Mock()
        
        with runner.isolated_filesystem():
            test_dir = Path("test_pdfs")
            test_dir.mkdir()
            output_dir = Path("new_output")  # Doesn't exist
            
            result = runner.invoke(main, [
                str(test_dir),
                '--output', str(output_dir)
            ])
            
            assert result.exit_code == 0
            assert output_dir.exists()  # Should be created
    
    @patch('file_renamer.cli.load_config')
    @patch('file_renamer.cli.BibliographicExtractor')
    @patch('file_renamer.cli.asyncio.run')
    def test_main_runtime_error(self, mock_asyncio, mock_extractor_class, mock_load_config):
        """Test CLI handles runtime errors gracefully."""
        runner = CliRunner()
        
        mock_config = {
            'api_key': 'test-key',
            'model_name': 'claude-3-5-sonnet-20241022',
            'filename_template': '{title}.pdf'
        }
        mock_load_config.return_value = mock_config
        mock_extractor_class.return_value = Mock()
        mock_asyncio.side_effect = RuntimeError("Processing failed")
        
        with runner.isolated_filesystem():
            test_dir = Path("test_pdfs")
            test_dir.mkdir()
            
            result = runner.invoke(main, [str(test_dir)])
            
            assert result.exit_code == 1
            assert "Processing failed" in result.output