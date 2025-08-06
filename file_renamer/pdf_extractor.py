import logging
from pathlib import Path
from typing import Optional

from pypdf import PdfReader

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