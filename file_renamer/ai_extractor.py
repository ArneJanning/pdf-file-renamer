import logging
import os
from typing import Optional

from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel

from .models import BibliographicInfo, ScreenshotInfo

logger = logging.getLogger(__name__)


class BibliographicExtractor:
    """Extract bibliographic information from PDF text using Claude."""
    
    def __init__(self, api_key: str, model_name: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize the extractor with Claude model.
        
        Args:
            api_key: Anthropic API key
            model_name: Name of the Claude model to use
        """
        # Set the API key in environment variable for pydantic-ai
        os.environ['ANTHROPIC_API_KEY'] = api_key
        
        self.model = AnthropicModel(model_name)
        
        # Create an agent with structured output
        self.agent = Agent(
            model=self.model,
            output_type=BibliographicInfo,
            system_prompt=(
                "You are an expert at extracting bibliographic information from academic papers, "
                "books, and other publications. Extract the author(s), editor(s), year of publication, "
                "and title from the provided text. "
                "\n\n"
                "Guidelines:\n"
                "- For multiple authors, list the main authors or use 'et al.' if there are many\n"
                "- Also extract just the last name of the primary author (author_last field)\n"
                "- If there's no author but there is an editor, provide the editor information\n"
                "- Also extract just the last name of the primary editor (editor_last field)\n"
                "- Extract the publication year in YYYY format if possible\n"
                "- Extract the complete title of the publication\n"
                "- For last names, handle various naming conventions correctly (e.g., 'van Gogh' → 'van Gogh', 'O'Brien' → 'O'Brien')\n"
                "- If information is unclear or missing, make your best educated guess based on the context"
            )
        )
    
    async def extract_info(self, pdf_text: str) -> Optional[BibliographicInfo]:
        """
        Extract bibliographic information from PDF text.
        
        Args:
            pdf_text: Text extracted from PDF
            
        Returns:
            BibliographicInfo object or None if extraction fails
        """
        try:
            prompt = (
                "Please extract the bibliographic information from the following text. "
                "Focus on finding the author(s) or editor(s), publication year, and title.\n\n"
                f"Text:\n{pdf_text}"
            )
            
            result = await self.agent.run(prompt)
            # The result is wrapped in a structured response
            return result.output
            
        except Exception as e:
            logger.error(f"Error extracting bibliographic info: {e}")
            return None


class ScreenshotExtractor:
    """Extract information from screenshot text using Claude."""
    
    def __init__(self, api_key: str, model_name: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize the extractor with Claude model.
        
        Args:
            api_key: Anthropic API key
            model_name: Name of the Claude model to use
        """
        # Set the API key in environment variable for pydantic-ai
        os.environ['ANTHROPIC_API_KEY'] = api_key
        
        self.model = AnthropicModel(model_name)
        
        # Create an agent with structured output for screenshots
        self.agent = Agent(
            model=self.model,
            output_type=ScreenshotInfo,
            system_prompt=(
                "You are an expert at analyzing screenshots and extracting meaningful information. "
                "From the OCR text extracted from screenshots, identify the application, date/time, "
                "content type, and main subject to create descriptive filenames. "
                "\n\n"
                "Guidelines:\n"
                "- Identify the application or software shown (e.g., 'Chrome', 'Word', 'WhatsApp', 'Terminal')\n"
                "- Extract any visible dates in YYYY-MM-DD format if possible\n"
                "- Extract any visible times in HH:MM format if possible\n"
                "- Determine the content type (e.g., 'email', 'chat', 'document', 'website', 'error', 'settings')\n"
                "- Summarize the main subject or topic in a few descriptive words\n"
                "- For applications, use common names (e.g., 'Chrome' not 'Google Chrome')\n"
                "- Make the main subject descriptive but concise (e.g., 'Login Error Message', 'Chat with John', 'Email about Meeting')\n"
                "- If information is unclear, make reasonable inferences based on UI elements and text content"
            )
        )
    
    async def extract_info(self, screenshot_text: str) -> Optional[ScreenshotInfo]:
        """
        Extract screenshot information from OCR text.
        
        Args:
            screenshot_text: Text extracted from screenshot via OCR
            
        Returns:
            ScreenshotInfo object or None if extraction fails
        """
        try:
            prompt = (
                "Please analyze the following OCR text extracted from a screenshot and provide "
                "structured information about it. Focus on identifying the application, any dates/times, "
                "the type of content, and the main subject.\n\n"
                f"OCR Text:\n{screenshot_text}"
            )
            
            result = await self.agent.run(prompt)
            return result.output
            
        except Exception as e:
            logger.error(f"Error extracting screenshot info: {e}")
            return None