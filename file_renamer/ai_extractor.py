import logging
import os
from typing import Optional, Union
from pathlib import Path
import base64

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
                "- For multiple authors, list all authors separated by ' and ' (e.g., 'John Smith and Jane Doe and Bob Johnson')\n"
                "- For author_last field, extract the correct last name(s) for each author separated by ' and '\n"
                "- Handle compound last names correctly (e.g., 'Jan Andre Lee Ludvigsen' → last name is 'Lee Ludvigsen')\n"
                "- Handle cultural naming conventions (e.g., 'Vincent van Gogh' → last name is 'van Gogh', 'María de la Cruz' → last name is 'de la Cruz')\n"
                "- Examples: 'Peter Millward and Jan Andre Lee Ludvigsen and Jonathan Sly' → author_last should be 'Millward and Lee Ludvigsen and Sly'\n"
                "- If there's no author but there is an editor, provide all editors in the same format\n"
                "- For editor_last field, apply the same last name extraction rules for editors\n"
                "- Extract the publication year in YYYY format if possible\n"
                "- Extract the main title and subtitle separately if present\n"
                "- Title should be the main title only (before colon, dash, or 'How'/'Why'/'What' phrases)\n"
                "- Subtitle should be the descriptive part after colon, dash, or explanatory phrases\n"
                "- Examples: 'Red Mafiya: How the Russian Mob Has Invaded America' → title='Red Mafiya', subtitle='How the Russian Mob Has Invaded America'\n"
                "- 'Digital Transformation - A Guide for Modern Business' → title='Digital Transformation', subtitle='A Guide for Modern Business'\n"
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
                "Focus on finding the author(s) or editor(s), publication year, main title, and subtitle (if present). "
                "Pay special attention to splitting titles and subtitles properly.\n\n"
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
                "Analyze the screenshot to identify the application, date/time, "
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
    
    async def extract_info(self, screenshot_data: Union[str, Path]) -> Optional[ScreenshotInfo]:
        """
        Extract screenshot information from OCR text or image file.
        
        Args:
            screenshot_data: Either OCR text string or Path to image file
            
        Returns:
            ScreenshotInfo object or None if extraction fails
        """
        try:
            if isinstance(screenshot_data, Path):
                # Use Claude Vision to analyze the image directly
                # For Claude Vision, we need to use the Anthropic API directly
                # as pydantic-ai doesn't yet support image inputs natively
                return await self._extract_from_image(screenshot_data)
            else:
                # Use OCR text (backward compatibility)
                prompt = (
                    "Please analyze the following OCR text extracted from a screenshot and provide "
                    "structured information about it. Focus on identifying the application, any dates/times, "
                    "the type of content, and the main subject.\n\n"
                    f"OCR Text:\n{screenshot_data}"
                )
                
                result = await self.agent.run(prompt)
                return result.output
            
        except Exception as e:
            logger.error(f"Error extracting screenshot info: {e}")
            return None
    
    def _create_image_prompt(self, image_path: Path) -> list:
        """Create a prompt with image for Claude Vision."""
        # Read and encode the image
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Determine the media type
        suffix = image_path.suffix.lower()
        media_type_map = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp',
            '.tiff': 'image/tiff',
        }
        media_type = media_type_map.get(suffix, 'image/png')
        
        # Create the prompt with image
        prompt = [
            {
                "type": "text",
                "text": (
                    "Please analyze this screenshot and provide structured information about it. "
                    "Focus on identifying the application, any dates/times, the type of content, "
                    "and the main subject. Look at all visual elements including UI components, "
                    "logos, and text to make accurate identifications."
                )
            },
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": image_data
                }
            }
        ]
        
        return prompt
    
    async def _extract_from_image(self, image_path: Path) -> Optional[ScreenshotInfo]:
        """Extract information directly from image using Claude Vision."""
        try:
            # Import anthropic directly for image support
            import anthropic
            
            # Create Anthropic client
            client = anthropic.AsyncAnthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
            
            # Read and encode the image
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Determine the media type
            suffix = image_path.suffix.lower()
            media_type_map = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp',
                '.webp': 'image/webp',
                '.tiff': 'image/tiff',
            }
            media_type = media_type_map.get(suffix, 'image/png')
            
            # Create the message with image
            message = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Please analyze this screenshot and extract the following information in a structured format:\n"
                                "1. Application or software shown (e.g., 'Chrome', 'WhatsApp', 'Terminal')\n"
                                "2. Any visible date (in YYYY-MM-DD format if possible)\n"
                                "3. Any visible time (in HH:MM format if possible)\n"
                                "4. Content type (e.g., 'email', 'chat', 'document', 'website', 'error', 'settings')\n"
                                "5. Main subject or topic (a concise description in a few words)\n\n"
                                "Provide the response in this exact JSON format:\n"
                                "{\n"
                                '  "application": "app name or null",\n'
                                '  "date": "YYYY-MM-DD or null",\n'
                                '  "time": "HH:MM or null",\n'
                                '  "content_type": "type or null",\n'
                                '  "main_subject": "subject description"\n'
                                "}"
                            )
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data
                            }
                        }
                    ]
                }]
            )
            
            # Parse the response
            import json
            response_text = message.content[0].text
            
            # Try to extract JSON from the response
            # Sometimes Claude might wrap it in markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            # Parse JSON response
            data = json.loads(response_text)
            
            # Create ScreenshotInfo object
            return ScreenshotInfo(
                application=data.get("application"),
                date=data.get("date"),
                time=data.get("time"),
                content_type=data.get("content_type"),
                main_subject=data.get("main_subject", "Unknown Subject")
            )
            
        except Exception as e:
            logger.error(f"Error using Claude Vision: {e}")
            return None