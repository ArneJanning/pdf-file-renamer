#!/usr/bin/env python3
import asyncio
import logging
import os
import shutil
from pathlib import Path

import click
from dotenv import load_dotenv

from .ai_extractor import BibliographicExtractor, ScreenshotExtractor
from .pdf_extractor import extract_pdf_text, extract_screenshot_text, get_all_supported_files

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config():
    """Load configuration from .env file."""
    load_dotenv()
    
    config = {
        'api_key': os.getenv('ANTHROPIC_API_KEY'),
        'model_name': os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022'),
        'pdf_template': os.getenv('PDF_FILENAME_TEMPLATE', '{author_or_editor_last} {year} - {full_title}.pdf'),
        'screenshot_template': os.getenv('SCREENSHOT_FILENAME_TEMPLATE', '{datetime} {application} - {main_subject}.png'),
        'max_pages': int(os.getenv('MAX_PAGES_TO_EXTRACT', '10')),
        'ocr_method': os.getenv('OCR_METHOD', 'tesseract').lower()  # 'tesseract' or 'claude'
    }
    
    # Backward compatibility: if old FILENAME_TEMPLATE exists, use it for PDFs
    if os.getenv('FILENAME_TEMPLATE'):
        config['pdf_template'] = os.getenv('FILENAME_TEMPLATE')
    
    if not config['api_key']:
        raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
    
    return config


async def process_pdf(pdf_path: Path, extractor: BibliographicExtractor, config: dict, output_dir: Path, dry_run: bool = False):
    """
    Process a single PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        extractor: BibliographicExtractor instance
        config: Configuration dictionary
        output_dir: Output directory for renamed files
        dry_run: If True, only show what would be done without renaming
    """
    logger.info(f"Processing: {pdf_path.name}")
    
    # Extract text from PDF
    pdf_text = extract_pdf_text(pdf_path, max_pages=config['max_pages'])
    if not pdf_text:
        logger.error(f"Failed to extract text from {pdf_path}")
        return
    
    # Extract bibliographic information
    bib_info = await extractor.extract_info(pdf_text)
    if not bib_info:
        logger.error(f"Failed to extract bibliographic information from {pdf_path}")
        return
    
    # Format new filename
    new_filename = bib_info.format_filename(config['pdf_template'])
    new_path = output_dir / new_filename
    
    # Ensure unique filename if file already exists
    counter = 1
    while new_path.exists():
        stem = new_filename.rsplit('.', 1)[0]
        new_path = output_dir / f"{stem} ({counter}).pdf"
        counter += 1
    
    logger.info(f"  Author/Editor: {bib_info.author_or_editor}")
    logger.info(f"  Year: {bib_info.year or 'Unknown'}")
    logger.info(f"  Title: {bib_info.title}")
    if bib_info.subtitle:
        logger.info(f"  Subtitle: {bib_info.subtitle}")
        logger.info(f"  Full title: {bib_info.full_title}")
    logger.info(f"  Template: {config['pdf_template']}")
    logger.info(f"  New filename: {new_path.name}")
    
    if not dry_run:
        try:
            # Copy file to new location with new name
            shutil.copy2(pdf_path, new_path)
            logger.info(f"  Copied to: {new_path}")
            
            # Delete the original file after successful copy
            pdf_path.unlink()
            logger.info(f"  Deleted original: {pdf_path}")
        except Exception as e:
            logger.error(f"  Failed to process file {pdf_path}: {e}")
            # If new file was created but delete failed, clean up the new file
            if new_path.exists():
                try:
                    new_path.unlink()
                    logger.info(f"  Cleaned up incomplete copy: {new_path}")
                except Exception as cleanup_error:
                    logger.error(f"  Failed to clean up {new_path}: {cleanup_error}")
            return
    else:
        logger.info(f"  [DRY RUN] Would copy to: {new_path}")
        logger.info(f"  [DRY RUN] Would delete original: {pdf_path}")


async def process_screenshot(image_path: Path, extractor: ScreenshotExtractor, config: dict, output_dir: Path, dry_run: bool = False):
    """
    Process a single screenshot file.
    
    Args:
        image_path: Path to the image file
        extractor: ScreenshotExtractor instance
        config: Configuration dictionary
        output_dir: Output directory for renamed files
        dry_run: If True, only show what would be done without renaming
    """
    logger.info(f"Processing: {image_path.name}")
    
    # Choose OCR method based on configuration
    if config.get('ocr_method') == 'claude':
        # Use Claude Vision directly on the image
        logger.debug("Using Claude Vision for OCR")
        screenshot_info = await extractor.extract_info(image_path)
    else:
        # Use Tesseract OCR (default)
        logger.debug("Using Tesseract for OCR")
        screenshot_text = extract_screenshot_text(image_path)
        if not screenshot_text:
            logger.error(f"Failed to extract text from {image_path}")
            return
        screenshot_info = await extractor.extract_info(screenshot_text)
    
    if not screenshot_info:
        logger.error(f"Failed to extract information from {image_path}")
        return
    
    # Format new filename - preserve original extension
    original_ext = image_path.suffix.lower()
    template_with_ext = config['screenshot_template'].replace('.png', original_ext)
    new_filename = screenshot_info.format_filename(template_with_ext)
    new_path = output_dir / new_filename
    
    # Ensure unique filename if file already exists
    counter = 1
    while new_path.exists():
        stem = new_filename.rsplit('.', 1)[0]
        ext = new_filename.split('.')[-1]
        new_path = output_dir / f"{stem} ({counter}).{ext}"
        counter += 1
    
    logger.info(f"  Application: {screenshot_info.application or 'Unknown'}")
    logger.info(f"  Date: {screenshot_info.date or 'Unknown'}")
    logger.info(f"  Content Type: {screenshot_info.content_type or 'Unknown'}")
    logger.info(f"  Main Subject: {screenshot_info.main_subject}")
    logger.info(f"  New filename: {new_path.name}")
    
    if not dry_run:
        try:
            # Copy file to new location with new name
            shutil.copy2(image_path, new_path)
            logger.info(f"  Copied to: {new_path}")
            
            # Delete the original file after successful copy
            image_path.unlink()
            logger.info(f"  Deleted original: {image_path}")
        except Exception as e:
            logger.error(f"  Failed to process file {image_path}: {e}")
            # If new file was created but delete failed, clean up the new file
            if new_path.exists():
                try:
                    new_path.unlink()
                    logger.info(f"  Cleaned up incomplete copy: {new_path}")
                except Exception as cleanup_error:
                    logger.error(f"  Failed to clean up {new_path}: {cleanup_error}")
            return
    else:
        logger.info(f"  [DRY RUN] Would copy to: {new_path}")
        logger.info(f"  [DRY RUN] Would delete original: {image_path}")


async def process_directory(directory: Path, pdf_extractor: BibliographicExtractor, screenshot_extractor: ScreenshotExtractor, config: dict, output_dir: Path, dry_run: bool = False):
    """Process all supported files (PDFs and screenshots) in a directory."""
    pdf_files, screenshot_files = get_all_supported_files(directory)
    
    total_files = len(pdf_files) + len(screenshot_files)
    if total_files == 0:
        logger.warning(f"No supported files found in {directory}")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files and {len(screenshot_files)} screenshot files to process")
    
    # Process PDF files
    if pdf_files:
        logger.info("Processing PDF files...")
        for pdf_path in pdf_files:
            try:
                await process_pdf(pdf_path, pdf_extractor, config, output_dir, dry_run)
            except Exception as e:
                logger.error(f"Error processing PDF {pdf_path}: {e}")
                continue
    
    # Process screenshot files  
    if screenshot_files:
        logger.info("Processing screenshot files...")
        for image_path in screenshot_files:
            try:
                await process_screenshot(image_path, screenshot_extractor, config, output_dir, dry_run)
            except Exception as e:
                logger.error(f"Error processing screenshot {image_path}: {e}")
                continue


@click.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), 
              help='Output directory for renamed files (default: input directory)')
@click.option('--dry-run', '-n', is_flag=True, 
              help='Show what would be done without actually renaming files')
@click.option('--pdf-template', 
              help='PDF filename template (overrides .env setting)')
@click.option('--screenshot-template',
              help='Screenshot filename template (overrides .env setting)')
@click.option('--ocr-method', type=click.Choice(['tesseract', 'claude'], case_sensitive=False),
              help='OCR method for screenshots: tesseract (local, fast) or claude (accurate, uses API)')
def main(directory: Path, output: Path, dry_run: bool, pdf_template: str, screenshot_template: str, ocr_method: str):
    """
    Rename PDF files and screenshots based on their content.
    
    This tool processes both PDF files and screenshots:
    - For PDFs: Extracts bibliographic information (author, year, title) and renames accordingly
    - For screenshots: Uses OCR to extract text, then AI to identify application, date, and content
    
    Supported screenshot formats: PNG, JPG, JPEG, BMP, GIF, TIFF, WEBP
    
    OCR Methods for screenshots:
    - tesseract: Local OCR processing (fast, requires Tesseract installed)
    - claude: Claude Vision API (more accurate, no OCR needed, uses more API credits)
    """
    try:
        # Load configuration
        config = load_config()
        
        # Override templates if provided
        if pdf_template:
            config['pdf_template'] = pdf_template
        if screenshot_template:
            config['screenshot_template'] = screenshot_template
        if ocr_method:
            config['ocr_method'] = ocr_method.lower()
        
        # Set output directory
        if output:
            output_dir = output
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = directory
        
        # Create extractors
        pdf_extractor = BibliographicExtractor(
            api_key=config['api_key'],
            model_name=config['model_name']
        )
        screenshot_extractor = ScreenshotExtractor(
            api_key=config['api_key'],
            model_name=config['model_name']
        )
        
        # Process directory
        asyncio.run(process_directory(directory, pdf_extractor, screenshot_extractor, config, output_dir, dry_run))
        
        logger.info("Processing complete!")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        raise click.ClickException(str(e))


if __name__ == '__main__':
    main()