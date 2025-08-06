"""Integration tests for the PDF file renamer."""
import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from click.testing import CliRunner

from file_renamer.cli import main
from file_renamer.models import BibliographicInfo
from file_renamer.pdf_extractor import extract_pdf_text, get_pdf_files
from file_renamer.ai_extractor import BibliographicExtractor


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""
    
    @patch('file_renamer.cli.load_dotenv')
    @patch('file_renamer.cli.os.getenv')
    @patch('file_renamer.ai_extractor.AnthropicModel')
    @patch('file_renamer.ai_extractor.Agent')
    @patch('file_renamer.pdf_extractor.PdfReader')
    @patch('file_renamer.cli.shutil.copy2')
    def test_complete_workflow_success(
        self, 
        mock_copy, 
        mock_pdf_reader, 
        mock_agent_class, 
        mock_anthropic_model,
        mock_getenv,
        mock_load_dotenv,
        temp_pdf_dir
    ):
        """Test complete workflow from CLI to file renaming."""
        # Setup environment
        mock_getenv.side_effect = lambda key, default=None: {
            'ANTHROPIC_API_KEY': 'test-key',
            'FILENAME_TEMPLATE': '{author_last} {year} - {title}.pdf',
            'MAX_PAGES_TO_EXTRACT': '2',
            'CLAUDE_MODEL': 'claude-3-5-sonnet-20241022'
        }.get(key, default)
        
        # Setup PDF reader mock
        mock_page = Mock()
        mock_page.extract_text.return_value = "The Great Gatsby by F. Scott Fitzgerald (1925)"
        mock_reader = Mock()
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader
        
        # Setup AI extractor mock
        mock_agent = Mock()
        mock_result = Mock()
        mock_result.output = BibliographicInfo(
            author="F. Scott Fitzgerald",
            author_last="Fitzgerald",
            year="1925",
            title="The Great Gatsby"
        )
        mock_agent.run = AsyncMock(return_value=mock_result)
        mock_agent_class.return_value = mock_agent
        
        # Setup file operations
        with patch('builtins.open', create=True):
            with patch.object(Path, 'exists', return_value=False):
                runner = CliRunner()
                result = runner.invoke(main, [str(temp_pdf_dir)])
        
        assert result.exit_code == 0
        
        # Verify PDF reading was attempted
        assert mock_pdf_reader.called
        
        # Verify AI extraction was called
        mock_agent.run.assert_called()
        
        # Verify file copying
        assert mock_copy.call_count > 0  # Should copy files
    
    @patch('file_renamer.cli.load_dotenv')
    @patch('file_renamer.cli.os.getenv')
    def test_missing_api_key_workflow(self, mock_getenv, mock_load_dotenv, temp_pdf_dir):
        """Test workflow with missing API key."""
        mock_getenv.return_value = None
        
        runner = CliRunner()
        result = runner.invoke(main, [str(temp_pdf_dir)])
        
        assert result.exit_code == 1
        assert "ANTHROPIC_API_KEY not found" in result.output
    
    @patch('file_renamer.cli.load_config')
    @patch('file_renamer.ai_extractor.AnthropicModel')
    @patch('file_renamer.ai_extractor.Agent')
    @patch('file_renamer.pdf_extractor.extract_pdf_text')
    def test_pdf_extraction_failure_workflow(
        self, 
        mock_extract_text, 
        mock_agent_class, 
        mock_anthropic_model,
        mock_load_config, 
        temp_pdf_dir
    ):
        """Test workflow when PDF text extraction fails."""
        mock_load_config.return_value = {
            'api_key': 'test-key',
            'model_name': 'claude-3-5-sonnet-20241022',
            'filename_template': '{title}.pdf',
            'max_pages': 10
        }
        
        # PDF extraction fails
        mock_extract_text.return_value = None
        
        runner = CliRunner()
        result = runner.invoke(main, [str(temp_pdf_dir)])
        
        assert result.exit_code == 0  # Should complete but with errors
        assert "Failed to extract text" in result.output
    
    def test_dry_run_workflow(self, temp_pdf_dir):
        """Test complete dry-run workflow."""
        with patch('file_renamer.cli.load_config') as mock_config:
            with patch('file_renamer.ai_extractor.AnthropicModel'):
                with patch('file_renamer.ai_extractor.Agent') as mock_agent_class:
                    with patch('file_renamer.pdf_extractor.extract_pdf_text') as mock_extract:
                        with patch('file_renamer.cli.shutil.copy2') as mock_copy:
                            
                            mock_config.return_value = {
                                'api_key': 'test-key',
                                'model_name': 'claude-3-5-sonnet-20241022',
                                'filename_template': '{author_last} {year} - {title}.pdf',
                                'max_pages': 10
                            }
                            
                            # Setup successful extraction
                            mock_extract.return_value = "Test PDF content"
                            
                            # Setup AI response
                            mock_agent = Mock()
                            mock_result = Mock()
                            mock_result.output = BibliographicInfo(
                                author="Test Author",
                                author_last="Author", 
                                year="2023",
                                title="Test Paper"
                            )
                            mock_agent.run = AsyncMock(return_value=mock_result)
                            mock_agent_class.return_value = mock_agent
                            
                            runner = CliRunner()
                            result = runner.invoke(main, [str(temp_pdf_dir), '--dry-run'])
                            
                            assert result.exit_code == 0
                            assert "DRY RUN" in result.output
                            mock_copy.assert_not_called()  # No files should be copied


class TestComponentIntegration:
    """Test integration between different components."""
    
    @patch('file_renamer.pdf_extractor.PdfReader')
    def test_pdf_extractor_with_real_paths(self, mock_pdf_reader, tmp_path):
        """Test PDF extractor with real file paths."""
        # Create a temporary PDF file
        pdf_file = tmp_path / "test.pdf"
        pdf_file.touch()
        
        # Mock PDF content
        mock_page = Mock()
        mock_page.extract_text.return_value = "Test content"
        mock_reader = Mock()
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader
        
        with patch('builtins.open', create=True):
            result = extract_pdf_text(pdf_file, max_pages=1)
            
        assert result == "--- Page 1 ---\nTest content"
    
    def test_get_pdf_files_integration(self, temp_pdf_dir):
        """Test PDF file discovery integration."""
        pdf_files = get_pdf_files(temp_pdf_dir)
        
        assert len(pdf_files) == 3  # 3 PDF files created in fixture
        assert all(f.suffix == '.pdf' for f in pdf_files)
        assert all(f.is_file() for f in pdf_files)
    
    def test_bibliographic_info_formatting_integration(self):
        """Test bibliographic info formatting with various templates."""
        info = BibliographicInfo(
            author="Jane Doe",
            author_last="Doe",
            year="2023",
            title="Research Paper"
        )
        
        # Test multiple templates
        templates_and_expected = [
            ('{author_last} {year} - {title}.pdf', 'Doe 2023 - Research Paper.pdf'),
            ('{author} ({year}). {title}.pdf', 'Jane Doe (2023). Research Paper.pdf'),
            ('[{year}] {title} - {author_last}.pdf', '[2023] Research Paper - Doe.pdf'),
            ('{title}.pdf', 'Research Paper.pdf')
        ]
        
        for template, expected in templates_and_expected:
            result = info.format_filename(template)
            assert result == expected
    
    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('file_renamer.ai_extractor.AnthropicModel')
    @patch('file_renamer.ai_extractor.Agent')
    async def test_ai_extractor_integration(self, mock_agent_class, mock_anthropic_model):
        """Test AI extractor integration with mocked API."""
        # Setup mock agent
        mock_agent = Mock()
        mock_result = Mock()
        expected_info = BibliographicInfo(
            author="Integration Test Author",
            author_last="Author",
            year="2023",
            title="Integration Test"
        )
        mock_result.output = expected_info
        mock_agent.run = AsyncMock(return_value=mock_result)
        mock_agent_class.return_value = mock_agent
        
        extractor = BibliographicExtractor(api_key="test-key")
        pdf_text = "Integration Test by Integration Test Author (2023)"
        
        result = await extractor.extract_info(pdf_text)
        
        assert result == expected_info
        mock_agent.run.assert_called_once()


class TestErrorHandlingIntegration:
    """Test error handling across components."""
    
    def test_invalid_pdf_path_integration(self):
        """Test handling of invalid PDF paths."""
        with pytest.raises(ValueError):
            get_pdf_files(Path("/nonexistent/path"))
    
    @patch('file_renamer.pdf_extractor.PdfReader')
    def test_corrupted_pdf_integration(self, mock_pdf_reader, tmp_path):
        """Test handling of corrupted PDF files."""
        pdf_file = tmp_path / "corrupted.pdf"
        pdf_file.touch()
        
        # Mock PDF reader to raise an exception
        mock_pdf_reader.side_effect = Exception("Corrupted PDF")
        
        with patch('builtins.open', create=True):
            result = extract_pdf_text(pdf_file)
            
        assert result is None
    
    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('file_renamer.ai_extractor.AnthropicModel')
    @patch('file_renamer.ai_extractor.Agent')
    async def test_ai_api_error_integration(self, mock_agent_class, mock_anthropic_model):
        """Test handling of AI API errors."""
        # Setup mock to raise an exception
        mock_agent = Mock()
        mock_agent.run = AsyncMock(side_effect=Exception("API Error"))
        mock_agent_class.return_value = mock_agent
        
        extractor = BibliographicExtractor(api_key="test-key")
        result = await extractor.extract_info("Some text")
        
        assert result is None


class TestRealFileOperations:
    """Test with real file operations (but mocked API calls)."""
    
    @patch('file_renamer.cli.load_dotenv')
    @patch('file_renamer.cli.os.getenv')
    @patch('file_renamer.ai_extractor.AnthropicModel')  
    @patch('file_renamer.ai_extractor.Agent')
    def test_file_rename_integration(
        self,
        mock_agent_class,
        mock_anthropic_model,
        mock_getenv,
        mock_load_dotenv,
        create_test_pdf,
        tmp_path
    ):
        """Test actual file renaming with real file operations."""
        # Setup environment
        mock_getenv.side_effect = lambda key, default=None: {
            'ANTHROPIC_API_KEY': 'test-key',
            'FILENAME_TEMPLATE': '{author_last} {year} - {title}.pdf',
            'MAX_PAGES_TO_EXTRACT': '1',
            'CLAUDE_MODEL': 'claude-3-5-sonnet-20241022'
        }.get(key, default)
        
        # Create a real test PDF
        test_pdf = create_test_pdf(
            title="Test Integration",
            author="Test Author", 
            year="2023",
            content="This is test content for integration testing."
        )
        
        # Move to test directory
        test_dir = tmp_path / "pdfs"
        test_dir.mkdir()
        new_pdf_path = test_dir / "original.pdf"
        test_pdf.rename(new_pdf_path)
        
        # Setup AI mock
        mock_agent = Mock()
        mock_result = Mock()
        mock_result.output = BibliographicInfo(
            author="Test Author",
            author_last="Author",
            year="2023", 
            title="Test Integration"
        )
        mock_agent.run = AsyncMock(return_value=mock_result)
        mock_agent_class.return_value = mock_agent
        
        # Run the CLI
        runner = CliRunner()
        result = runner.invoke(main, [str(test_dir)])
        
        assert result.exit_code == 0
        
        # Check that the file was renamed
        expected_filename = "Author 2023 - Test Integration.pdf"
        expected_path = test_dir / expected_filename
        assert expected_path.exists()
        assert new_pdf_path.exists()  # Original should still exist (copy, not move)
    
    def test_duplicate_filename_handling(self, tmp_path, create_test_pdf):
        """Test handling of duplicate filenames in real filesystem."""
        test_dir = tmp_path / "pdfs"
        test_dir.mkdir()
        
        # Create first file with target name
        existing_file = test_dir / "Author 2023 - Test Paper.pdf"
        existing_file.touch()
        
        # Create test PDF
        test_pdf = create_test_pdf("Test Paper", "Test Author", "2023")
        new_pdf_path = test_dir / "original.pdf" 
        test_pdf.rename(new_pdf_path)
        
        # Test the duplicate handling logic
        from file_renamer.models import BibliographicInfo
        info = BibliographicInfo(
            author="Test Author",
            author_last="Author", 
            year="2023",
            title="Test Paper"
        )
        
        template = "{author_last} {year} - {title}.pdf"
        filename = info.format_filename(template)
        new_path = test_dir / filename
        
        # Simulate duplicate handling
        counter = 1
        while new_path.exists():
            stem = filename.rsplit('.', 1)[0]
            new_path = test_dir / f"{stem} ({counter}).pdf"
            counter += 1
        
        # Should create path with (1) suffix
        assert new_path.name == "Author 2023 - Test Paper (1).pdf"
        assert not new_path.exists()  # Shouldn't exist yet