import logging
import os
from typing import Optional

from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel

from .models import BibliographicInfo

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