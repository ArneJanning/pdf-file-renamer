#!/usr/bin/env python3
import asyncio
import logging
import os
import shutil
from pathlib import Path

import click
from dotenv import load_dotenv

from .ai_extractor import BibliographicExtractor
from .pdf_extractor import extract_pdf_text, get_pdf_files

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
        'filename_template': os.getenv('FILENAME_TEMPLATE', '[{author_or_editor}] {year} - {title}.pdf'),
        'max_pages': int(os.getenv('MAX_PAGES_TO_EXTRACT', '10'))
    }
    
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
    new_filename = bib_info.format_filename(config['filename_template'])
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
    logger.info(f"  New filename: {new_path.name}")
    
    if not dry_run:
        # Copy file to new location with new name
        shutil.copy2(pdf_path, new_path)
        logger.info(f"  Copied to: {new_path}")
    else:
        logger.info(f"  [DRY RUN] Would copy to: {new_path}")


async def process_directory(directory: Path, extractor: BibliographicExtractor, config: dict, output_dir: Path, dry_run: bool = False):
    """Process all PDFs in a directory."""
    pdf_files = get_pdf_files(directory)
    
    if not pdf_files:
        logger.warning(f"No PDF files found in {directory}")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    for pdf_path in pdf_files:
        try:
            await process_pdf(pdf_path, extractor, config, output_dir, dry_run)
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {e}")
            continue


@click.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), 
              help='Output directory for renamed files (default: input directory)')
@click.option('--dry-run', '-n', is_flag=True, 
              help='Show what would be done without actually renaming files')
@click.option('--template', '-t', 
              help='Filename template (overrides .env setting)')
def main(directory: Path, output: Path, dry_run: bool, template: str):
    """
    Rename PDF files based on their bibliographic information.
    
    This tool extracts text from the first pages of PDF files, uses Claude AI
    to identify bibliographic information (author, year, title), and renames
    the files accordingly.
    """
    try:
        # Load configuration
        config = load_config()
        
        # Override template if provided
        if template:
            config['filename_template'] = template
        
        # Set output directory
        if output:
            output_dir = output
            output_dir.mkdir(parents=True, exist_ok=True)
        else:
            output_dir = directory
        
        # Create extractor
        extractor = BibliographicExtractor(
            api_key=config['api_key'],
            model_name=config['model_name']
        )
        
        # Process directory
        asyncio.run(process_directory(directory, extractor, config, output_dir, dry_run))
        
        logger.info("Processing complete!")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        raise click.ClickException(str(e))


if __name__ == '__main__':
    main()