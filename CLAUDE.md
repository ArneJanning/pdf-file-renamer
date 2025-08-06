# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python 3.12 CLI tool called "file-renamer" that renames PDF files based on bibliographic information extracted using Claude AI. It uses PydanticAI to interact with the Anthropic API.

## Development Setup

The project uses Python 3.12 (specified in `.python-version`) and has a `pyproject.toml` configuration file. The `uv` package manager is available at `/home/arne/.local/bin/uv`.

### Install dependencies:
```bash
uv pip install -e .
```

### Set up environment:
1. Copy `.env.example` to `.env`
2. Add your Anthropic API key to `.env`

## Running the Application

### As installed CLI tool:
```bash
pdf-renamer /path/to/pdf/directory
```

### From source:
```bash
python -m file_renamer /path/to/pdf/directory
```

### Common commands:
```bash
# Dry run to preview changes
pdf-renamer /path/to/pdfs --dry-run

# Custom output directory
pdf-renamer /path/to/pdfs --output /path/to/renamed

# Custom filename template
pdf-renamer /path/to/pdfs --template "{author} ({year}) - {title}.pdf"
```

## Project Structure

- `__init__.py` - Package initialization
- `__main__.py` - Entry point for running as module
- `cli.py` - Main CLI application using Click
- `models.py` - Pydantic models for bibliographic information
- `ai_extractor.py` - PydanticAI integration for Claude
- `pdf_extractor.py` - PDF text extraction utilities
- `pyproject.toml` - Project configuration with dependencies
- `.env.example` - Example environment configuration

## Key Dependencies

- `pydantic-ai[anthropic]` - For structured AI interactions with Claude
- `pypdf` - For PDF text extraction
- `click` - For CLI interface
- `python-dotenv` - For environment variable management

## Architecture

The application follows a modular design:
1. PDF text extraction (`pdf_extractor.py`)
2. AI-powered bibliographic extraction (`ai_extractor.py`) 
3. Structured data models (`models.py`)
4. CLI interface (`cli.py`)

The workflow:
1. User specifies a directory containing PDFs
2. App extracts text from first 10 pages of each PDF
3. Sends text to Claude to extract author/editor, year, and title
4. Renames files based on configurable template
5. Handles duplicates by appending numbers