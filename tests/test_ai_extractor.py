"""Tests for the ai_extractor module."""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from file_renamer.ai_extractor import BibliographicExtractor
from file_renamer.models import BibliographicInfo


class TestBibliographicExtractor:
    """Test cases for BibliographicExtractor class."""
    
    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('file_renamer.ai_extractor.AnthropicModel')
    @patch('file_renamer.ai_extractor.Agent')
    def test_init_success(self, mock_agent, mock_anthropic_model):
        """Test successful initialization of BibliographicExtractor."""
        mock_model = Mock()
        mock_anthropic_model.return_value = mock_model
        
        extractor = BibliographicExtractor(api_key="test-key")
        
        mock_anthropic_model.assert_called_once_with('claude-3-5-sonnet-20241022')
        mock_agent.assert_called_once()
        
        # Check that the agent is initialized with correct parameters
        args, kwargs = mock_agent.call_args
        assert 'model' in kwargs
        assert 'output_type' in kwargs
        assert kwargs['output_type'] is BibliographicInfo
        assert 'system_prompt' in kwargs
        assert "bibliographic information" in kwargs['system_prompt']
    
    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('file_renamer.ai_extractor.AnthropicModel')
    @patch('file_renamer.ai_extractor.Agent')
    def test_init_custom_model(self, mock_agent, mock_anthropic_model):
        """Test initialization with custom model."""
        extractor = BibliographicExtractor(
            api_key="test-key",
            model_name="claude-3-haiku-20240307"
        )
        
        mock_anthropic_model.assert_called_once_with('claude-3-haiku-20240307')
    
    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('file_renamer.ai_extractor.AnthropicModel')
    @patch('file_renamer.ai_extractor.Agent')
    async def test_extract_info_success(self, mock_agent_class, mock_anthropic_model):
        """Test successful information extraction."""
        # Mock the agent instance
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        
        # Mock the run result
        mock_result = Mock()
        expected_info = BibliographicInfo(
            author="F. Scott Fitzgerald",
            author_last="Fitzgerald",
            year="1925",
            title="The Great Gatsby"
        )
        mock_result.output = expected_info
        mock_agent.run = AsyncMock(return_value=mock_result)
        
        extractor = BibliographicExtractor(api_key="test-key")
        pdf_text = "The Great Gatsby by F. Scott Fitzgerald, published in 1925"
        
        result = await extractor.extract_info(pdf_text)
        
        assert result == expected_info
        mock_agent.run.assert_called_once()
        
        # Check the prompt contains the PDF text
        call_args = mock_agent.run.call_args[0][0]
        assert pdf_text in call_args
        assert "bibliographic information" in call_args
    
    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('file_renamer.ai_extractor.AnthropicModel')
    @patch('file_renamer.ai_extractor.Agent')
    async def test_extract_info_with_editor(self, mock_agent_class, mock_anthropic_model):
        """Test extraction with editor information."""
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        
        mock_result = Mock()
        expected_info = BibliographicInfo(
            editor="John Smith",
            editor_last="Smith",
            year="2023",
            title="Handbook of AI"
        )
        mock_result.output = expected_info
        mock_agent.run = AsyncMock(return_value=mock_result)
        
        extractor = BibliographicExtractor(api_key="test-key")
        pdf_text = "Handbook of AI edited by John Smith (2023)"
        
        result = await extractor.extract_info(pdf_text)
        
        assert result == expected_info
        assert result.author is None
        assert result.editor == "John Smith"
    
    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('file_renamer.ai_extractor.AnthropicModel')
    @patch('file_renamer.ai_extractor.Agent')
    @patch('file_renamer.ai_extractor.logger')
    async def test_extract_info_exception(self, mock_logger, mock_agent_class, mock_anthropic_model):
        """Test extraction handles exceptions gracefully."""
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        mock_agent.run = AsyncMock(side_effect=Exception("API Error"))
        
        extractor = BibliographicExtractor(api_key="test-key")
        pdf_text = "Some PDF text"
        
        result = await extractor.extract_info(pdf_text)
        
        assert result is None
        mock_logger.error.assert_called_once()
        assert "Error extracting bibliographic info" in mock_logger.error.call_args[0][0]
    
    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('file_renamer.ai_extractor.AnthropicModel')
    @patch('file_renamer.ai_extractor.Agent')
    async def test_extract_info_minimal_data(self, mock_agent_class, mock_anthropic_model):
        """Test extraction with minimal bibliographic data."""
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        
        mock_result = Mock()
        expected_info = BibliographicInfo(title="Unknown Title")
        mock_result.output = expected_info
        mock_agent.run = AsyncMock(return_value=mock_result)
        
        extractor = BibliographicExtractor(api_key="test-key")
        pdf_text = "Some document with unclear authorship"
        
        result = await extractor.extract_info(pdf_text)
        
        assert result == expected_info
        assert result.title == "Unknown Title"
        assert result.author is None
        assert result.year is None
    
    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('file_renamer.ai_extractor.AnthropicModel')
    @patch('file_renamer.ai_extractor.Agent')
    async def test_extract_info_complex_names(self, mock_agent_class, mock_anthropic_model):
        """Test extraction with complex author names."""
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        
        mock_result = Mock()
        expected_info = BibliographicInfo(
            author="José María García-González et al.",
            author_last="García-González",
            year="2022",
            title="Advanced Research Methods"
        )
        mock_result.output = expected_info
        mock_agent.run = AsyncMock(return_value=mock_result)
        
        extractor = BibliographicExtractor(api_key="test-key")
        pdf_text = "Advanced Research Methods by José María García-González et al. (2022)"
        
        result = await extractor.extract_info(pdf_text)
        
        assert result == expected_info
        assert result.author_last == "García-González"
        assert "et al." in result.author
    
    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('file_renamer.ai_extractor.AnthropicModel')
    @patch('file_renamer.ai_extractor.Agent')
    async def test_extract_info_long_text(self, mock_agent_class, mock_anthropic_model):
        """Test extraction from long PDF text."""
        mock_agent = Mock()
        mock_agent_class.return_value = mock_agent
        
        mock_result = Mock()
        expected_info = BibliographicInfo(
            author="Research Team",
            author_last="Team",
            year="2023",
            title="Comprehensive Study"
        )
        mock_result.output = expected_info
        mock_agent.run = AsyncMock(return_value=mock_result)
        
        extractor = BibliographicExtractor(api_key="test-key")
        
        # Simulate long PDF text
        pdf_text = "--- Page 1 ---\n" + "A" * 1000 + "\n\n--- Page 2 ---\n" + "B" * 1000
        
        result = await extractor.extract_info(pdf_text)
        
        assert result == expected_info
        # Verify the long text was passed to the agent
        call_args = mock_agent.run.call_args[0][0]
        assert "Page 1" in call_args
        assert "Page 2" in call_args
    
    def test_system_prompt_content(self):
        """Test that system prompt contains expected instructions."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            with patch('file_renamer.ai_extractor.AnthropicModel'):
                with patch('file_renamer.ai_extractor.Agent') as mock_agent:
                    extractor = BibliographicExtractor(api_key="test-key")
                    
                    # Get the system prompt from the Agent call
                    call_kwargs = mock_agent.call_args[1]
                    system_prompt = call_kwargs['system_prompt']
                    
                    # Check key instructions are present
                    assert "bibliographic information" in system_prompt
                    assert "author_last" in system_prompt
                    assert "editor_last" in system_prompt
                    assert "last name" in system_prompt
                    assert "van Gogh" in system_prompt  # Example of naming convention
                    assert "O'Brien" in system_prompt   # Example of naming convention
    
    def test_api_key_set_in_environment(self):
        """Test that API key is set in environment during initialization."""
        with patch('file_renamer.ai_extractor.AnthropicModel'):
            with patch('file_renamer.ai_extractor.Agent'):
                extractor = BibliographicExtractor(api_key="test-secret-key")
                
                # The constructor should have set the environment variable
                import os
                assert os.environ.get('ANTHROPIC_API_KEY') == 'test-secret-key'