# PDF File Renamer

A powerful CLI tool that automatically renames PDF files based on their bibliographic information (author, year, title) using Claude AI. Perfect for organizing academic papers, books, and other PDF documents with consistent, meaningful filenames.

## Features

- 🤖 **AI-Powered Extraction**: Uses Claude AI to intelligently extract bibliographic information from PDFs
- 📚 **Smart Name Detection**: Handles various naming conventions (e.g., "van Gogh", "O'Brien", "Smith Jr.")
- 🎯 **Flexible Templates**: Fully customizable filename templates with multiple variables
- 📁 **Batch Processing**: Process entire directories of PDFs at once
- 🔍 **Preview Mode**: Dry-run option to preview changes before applying them
- 🛡️ **Safe Operation**: Automatic handling of duplicate filenames
- ⚡ **Fast Processing**: Analyzes only the first pages of PDFs for efficiency

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
- [Filename Templates](#filename-templates)
- [Examples](#examples)
- [API Key Setup](#api-key-setup)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [License](#license)

## Installation

### Prerequisites

- Python 3.12 or higher
- An Anthropic API key for Claude AI

### Install from source

1. Clone the repository:
```bash
git clone https://github.com/ArneJanning/pdf-file-renamer.git
cd pdf-file-renamer
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package:
```bash
pip install -e .
```

### Install using uv (recommended)

If you have [uv](https://github.com/astral-sh/uv) installed:
```bash
uv pip install -e .
```

## Quick Start

1. **Set up your API key**:
```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

2. **Test with dry-run**:
```bash
pdf-renamer /path/to/pdf/directory --dry-run
```

3. **Rename PDFs**:
```bash
pdf-renamer /path/to/pdf/directory
```

## Configuration

### Environment Variables

Create a `.env` file in your working directory (or copy `.env.example`):

```env
# Claude API Configuration
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# File naming template
# Default: {author_or_editor_last} {year} - {title}.pdf
FILENAME_TEMPLATE={author_or_editor_last} {year} - {title}.pdf

# Number of pages to extract for analysis (default: 10)
MAX_PAGES_TO_EXTRACT=10

# Claude model to use (default: claude-3-5-sonnet-20241022)
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key (required) | None |
| `FILENAME_TEMPLATE` | Template for renamed files | `{author_or_editor_last} {year} - {title}.pdf` |
| `MAX_PAGES_TO_EXTRACT` | Number of PDF pages to analyze | 10 |
| `CLAUDE_MODEL` | Claude model to use | `claude-3-5-sonnet-20241022` |

## Usage

### Basic Command

```bash
pdf-renamer [OPTIONS] DIRECTORY
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--output` | `-o` | Output directory for renamed files (default: input directory) |
| `--dry-run` | `-n` | Preview changes without renaming files |
| `--template` | `-t` | Override the filename template from .env |
| `--help` | | Show help message |

### Command Examples

**Preview changes (dry-run)**:
```bash
pdf-renamer ~/Documents/Papers --dry-run
```

**Rename to a different directory**:
```bash
pdf-renamer ~/Downloads/PDFs --output ~/Documents/Organized
```

**Use a custom template**:
```bash
pdf-renamer ~/Papers --template "{author_last}, {author} ({year}) - {title}.pdf"
```

**Process current directory**:
```bash
pdf-renamer .
```

## Filename Templates

### Available Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{author}` | Full author name | "F. Scott Fitzgerald" |
| `{author_last}` | Author's last name only | "Fitzgerald" |
| `{editor}` | Full editor name | "John Smith" |
| `{editor_last}` | Editor's last name only | "Smith" |
| `{author_or_editor}` | Author or editor (with suffix) | "F. Scott Fitzgerald" or "John Smith (Ed.)" |
| `{author_or_editor_last}` | Last name of author or editor | "Fitzgerald" or "Smith" |
| `{year}` | Publication year | "1925" |
| `{title}` | Publication title | "The Great Gatsby" |

### Template Examples

1. **Default format** (clean and simple):
   ```
   {author_or_editor_last} {year} - {title}.pdf
   → Fitzgerald 1925 - The Great Gatsby.pdf
   ```

2. **Academic citation style**:
   ```
   {author_last}, {author} ({year}). {title}.pdf
   → Fitzgerald, F. Scott Fitzgerald (1925). The Great Gatsby.pdf
   ```

3. **Library style**:
   ```
   [{year}] {author_or_editor} - {title}.pdf
   → [1925] F. Scott Fitzgerald - The Great Gatsby.pdf
   ```

4. **Minimal style**:
   ```
   {author_last}-{year}-{title}.pdf
   → Fitzgerald-1925-The Great Gatsby.pdf
   ```

5. **Full information**:
   ```
   {author} ({year}) - {title} [{author_last}].pdf
   → F. Scott Fitzgerald (1925) - The Great Gatsby [Fitzgerald].pdf
   ```

## Examples

### Example 1: Organizing Research Papers

```bash
# Preview the renaming
pdf-renamer ~/Downloads/papers --dry-run

# Output:
# Processing: quantum_computing_2023.pdf
#   Author/Editor: Alice Johnson
#   Year: 2023
#   Title: Advances in Quantum Computing Algorithms
#   New filename: Johnson 2023 - Advances in Quantum Computing Algorithms.pdf
#   [DRY RUN] Would copy to: ~/Downloads/papers/Johnson 2023 - Advances in Quantum Computing Algorithms.pdf

# Apply the renaming
pdf-renamer ~/Downloads/papers
```

### Example 2: Custom Organization System

```bash
# Organize by year with custom template
pdf-renamer ~/Library/PDFs \
  --template "[{year}] {author_last} - {title}.pdf" \
  --output ~/Library/Organized
```

### Example 3: Processing Books

```bash
# Books often have editors instead of authors
pdf-renamer ~/Books --template "{author_or_editor} - {title} ({year}).pdf"

# Output example:
# Original: handbook_of_ai.pdf
# Renamed: Smith (Ed.) - Handbook of Artificial Intelligence (2022).pdf
```

## API Key Setup

### Getting an Anthropic API Key

1. Sign up at [console.anthropic.com](https://console.anthropic.com)
2. Navigate to API Keys section
3. Create a new API key
4. Copy the key (starts with `sk-ant-api...`)

### Setting the API Key

**Method 1: Environment file (recommended)**
```bash
echo "ANTHROPIC_API_KEY=sk-ant-api..." > .env
```

**Method 2: Export in shell**
```bash
export ANTHROPIC_API_KEY="sk-ant-api..."
```

**Method 3: Pass via environment**
```bash
ANTHROPIC_API_KEY="sk-ant-api..." pdf-renamer /path/to/pdfs
```

## Advanced Usage

### Handling Special Cases

**Multiple authors**: Claude will intelligently handle papers with multiple authors, often using "et al." for many authors:
```
Original: collaborative_research.pdf
Renamed: Smith et al 2023 - Collaborative Research Methods.pdf
```

**Non-English names**: The AI correctly handles various naming conventions:
```
van Gogh → van Gogh (not "Gogh")
O'Brien → O'Brien (not "Brien")
José García → García (not "José")
```

**Missing information**: Files with missing data use defaults:
```
No author: Unknown 2023 - Title.pdf
No year: Author Unknown Year - Title.pdf
```

### Performance Tips

1. **Batch size**: Process directories with 100-200 PDFs at a time for best performance
2. **Page extraction**: Reduce `MAX_PAGES_TO_EXTRACT` for faster processing of large PDFs
3. **Model selection**: Use `claude-3-5-sonnet` for best accuracy, or `claude-3-haiku` for speed

### Integration with File Managers

**macOS Automator**: Create a Quick Action to rename PDFs from Finder
**Windows**: Add to Send To menu for right-click renaming
**Linux**: Create a Nautilus script or KDE Service Menu

## Troubleshooting

### Common Issues

**"ANTHROPIC_API_KEY not found"**
- Ensure your `.env` file is in the current directory
- Check the API key is correctly formatted
- Try exporting the key: `export ANTHROPIC_API_KEY="your-key"`

**"Failed to extract text from PDF"**
- The PDF might be scanned/image-based (OCR not supported yet)
- The PDF might be corrupted
- Try opening the PDF in a reader to verify it's valid

**"Failed to extract bibliographic information"**
- The PDF might not contain clear bibliographic information
- Try increasing `MAX_PAGES_TO_EXTRACT`
- The PDF might be in an unsupported language

**Rate limiting errors**
- Add delays between large batches
- Reduce concurrent processing
- Check your API tier limits

### Debug Mode

Run with logging to see detailed information:
```bash
# Set logging level
export LOG_LEVEL=DEBUG
pdf-renamer /path/to/pdfs
```

## Development

### Project Structure

```
pdf-file-renamer/
├── file_renamer/
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # Entry point
│   ├── cli.py               # CLI interface
│   ├── models.py            # Pydantic models
│   ├── ai_extractor.py      # Claude AI integration
│   └── pdf_extractor.py     # PDF text extraction
├── tests/                   # Comprehensive test suite
│   ├── conftest.py         # Test fixtures
│   ├── test_models.py      # Model tests
│   ├── test_pdf_extractor.py # PDF extraction tests
│   ├── test_ai_extractor.py # AI integration tests
│   ├── test_cli.py         # CLI tests
│   ├── test_integration.py # Integration tests
│   └── test_performance.py # Performance tests
├── .github/workflows/      # CI/CD workflows
├── .env.example            # Example configuration
├── pyproject.toml          # Project configuration
├── README.md               # This file
├── TEST_SUMMARY.md         # Test suite documentation
└── LICENSE                 # MIT License
```

### Running from Source

```bash
# Clone the repository
git clone https://github.com/ArneJanning/pdf-file-renamer.git
cd pdf-file-renamer

# Install in development mode
pip install -e .

# Run directly
python -m file_renamer /path/to/pdfs
```

### Testing

The project includes a comprehensive test suite with 80+ tests covering:

**Install test dependencies:**
```bash
pip install -e ".[test]"
```

**Run all tests:**
```bash
pytest tests/ -v
```

**Run with coverage:**
```bash
pytest tests/ --cov=file_renamer --cov-report=term-missing
```

**Run performance tests:**
```bash
pytest tests/test_performance.py -v
```

**Use the test runner:**
```bash
python run_tests.py --install
```

**Test categories:**
- **Unit Tests**: Individual component functionality
- **Integration Tests**: End-to-end workflows  
- **Performance Tests**: Scalability and efficiency
- **CLI Tests**: Command-line interface behavior

See [TEST_SUMMARY.md](TEST_SUMMARY.md) for detailed test documentation.

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `pytest`
5. Commit: `git commit -am 'Add feature'`
6. Push: `git push origin feature-name`
7. Create a Pull Request

### Adding New Features

To add a new template variable:
1. Update `models.py` to add the field
2. Update the Claude prompt in `ai_extractor.py`
3. Add the variable to `format_filename()`
4. Update documentation

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Built with [PydanticAI](https://ai.pydantic.dev/) for structured AI interactions
- Powered by [Claude](https://www.anthropic.com/) from Anthropic
- PDF processing via [pypdf](https://pypdf.readthedocs.io/)
- CLI interface using [Click](https://click.palletsprojects.com/)

## Support

- **Issues**: [GitHub Issues](https://github.com/ArneJanning/pdf-file-renamer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ArneJanning/pdf-file-renamer/discussions)
- **Email**: your-email@example.com

---

Made with ❤️ by Arne Janning