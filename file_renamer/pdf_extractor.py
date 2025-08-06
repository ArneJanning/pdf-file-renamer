import logging
from pathlib import Path
from typing import Optional

from pypdf import PdfReader
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)


def extract_pdf_text(pdf_path: Path, max_pages: int = 10) -> Optional[str]:
    """
    Extract text from the first n pages of a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        max_pages: Maximum number of pages to extract (default: 10)
        
    Returns:
        Extracted text or None if extraction fails
    """
    try:
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            text_parts = []
            
            # Extract text from up to max_pages
            pages_to_extract = min(len(reader.pages), max_pages)
            
            for page_num in range(pages_to_extract):
                page = reader.pages[page_num]
                text = page.extract_text()
                if text.strip():
                    text_parts.append(f"--- Page {page_num + 1} ---\n{text}")
            
            if not text_parts:
                logger.warning(f"No text could be extracted from {pdf_path}")
                return None
                
            return "\n\n".join(text_parts)
            
    except Exception as e:
        logger.error(f"Error extracting text from {pdf_path}: {e}")
        return None


def extract_screenshot_text(image_path: Path) -> Optional[str]:
    """
    Extract text from screenshot using OCR.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Extracted text or None if extraction fails
    """
    try:
        # Open and process the image
        image = Image.open(image_path)
        
        # Use tesseract to extract text
        text = pytesseract.image_to_string(image, lang='eng+deu')  # Support English and German
        
        if not text.strip():
            logger.warning(f"No text could be extracted from {image_path}")
            return None
            
        return text.strip()
        
    except Exception as e:
        logger.error(f"Error extracting text from {image_path}: {e}")
        return None


def get_pdf_files(directory: Path) -> list[Path]:
    """
    Get all PDF files in a directory.
    
    Args:
        directory: Directory path to search for PDFs
        
    Returns:
        List of PDF file paths
    """
    if not directory.exists():
        raise ValueError(f"Directory {directory} does not exist")
    
    if not directory.is_dir():
        raise ValueError(f"{directory} is not a directory")
    
    pdf_files = list(directory.glob("*.pdf"))
    return pdf_files


def get_screenshot_files(directory: Path) -> list[Path]:
    """
    Get all screenshot/image files in a directory.
    
    Args:
        directory: Directory path to search for images
        
    Returns:
        List of image file paths
    """
    if not directory.exists():
        raise ValueError(f"Directory {directory} does not exist")
    
    if not directory.is_dir():
        raise ValueError(f"{directory} is not a directory")
    
    # Common screenshot/image extensions
    extensions = ["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.gif", "*.tiff", "*.webp"]
    image_files = []
    
    for ext in extensions:
        image_files.extend(directory.glob(ext))
        # Also check uppercase extensions
        image_files.extend(directory.glob(ext.upper()))
    
    return sorted(image_files)


def get_all_supported_files(directory: Path) -> tuple[list[Path], list[Path]]:
    """
    Get both PDF and screenshot files from a directory.
    
    Args:
        directory: Directory path to search
        
    Returns:
        Tuple of (pdf_files, screenshot_files)
    """
    pdf_files = get_pdf_files(directory)
    screenshot_files = get_screenshot_files(directory)
    
    return pdf_files, screenshot_files