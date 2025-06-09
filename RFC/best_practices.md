# Python Project Best Practices

A comprehensive guide to modern Python project patterns and practices, extracted from real-world development experience.

## Project Structure

### Modern Python Package Layout

```bash
project-root/
├── src/
│   └── package_name/
│       ├── __init__.py          # Public API exports
│       ├── module1.py           # Core functionality modules
│       ├── module2.py
│       └── cli.py               # CLI interface (if applicable)
├── tests/
│   ├── test_module1.py
│   └── test_module2.py
├── RFC/                         # Design documents and RFCs
├── icons/                       # Static assets
├── pyproject.toml              # Modern Python project config
├── justfile                    # Task automation (alternative to Makefile)
├── README.md                   # User-facing documentation
└── .gitignore
```

**Key Benefits:**

- `src/` layout prevents accidental imports during development
- Clear separation between source code, tests, and documentation
- Standardized configuration in `pyproject.toml`

### Module Organization Principles

**Separation of Concerns:**

- **Data Processing**: Core logic and algorithms
- **I/O Operations**: File reading, network requests, API calls
- **CLI Interface**: Argument parsing and user interaction
- **Output Generation**: Formatting and file generation
- **Constants**: Configuration and lookup tables

**Example Module Breakdown:**

```python
# constants.py - Configuration and lookup data
MONTH_NAMES = ["JANUARY", "FEBRUARY", ...]
WASTE_TYPE_KEYWORDS = ["organic", "paper", ...]

# data_processor.py - Core business logic
def extract_data_from_source(source): ...
def process_extracted_data(data): ...

# io_operations.py - External interactions
def download_file(url, output_path): ...
def read_pdf_file(file_path): ...

# output_generator.py - Result formatting
def generate_ical_calendar(data): ...
def generate_language_specific_output(data, language): ...

# cli.py - User interface
def main(): ...
```

## Package Configuration

### pyproject.toml Best Practices

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "your-package"
version = "0.1.0"
description = "Clear, concise description"
authors = [
    {name = "Your Name", email = "noreply@example.com"}
]
readme = "README.md"
license = {file = "LICENSE"}
requires-python = ">=3.11"
classifiers = [
    "Development Status :: 4 - Beta",
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
]
keywords = ["relevant", "keywords"]
dependencies = [
    "core-dependency>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "ruff>=0.1.0", 
    "mypy>=1.0.0",
    "build",
]

[project.scripts]
your-command = "your_package.cli:main"

# uv-specific configuration for modern package management
[tool.uv]
dev-dependencies = [
    "pytest>=7.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]

[tool.hatch.build.targets.wheel]
packages = ["src/your_package"]

# Tool configurations
[tool.ruff]
line-length = 120
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "B", "A", "C4", "T20"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false  # Relaxed for rapid development
```

### Package Manager: UV vs PIP

**Use UV for:**

- Modern dependency resolution
- Fast installs and environment management
- Editable installs with `uv sync --dev`
- Lock file generation

**UV Commands:**

```bash
uv init                    # Initialize new project
uv add package-name        # Add dependency
uv sync --dev             # Install all dependencies including dev
uv run command            # Run command in project environment
uv build                  # Build package
```

## Development Tools

### Code Quality Tools

**Ruff (Recommended over Black + flake8):**

```toml
[tool.ruff]
line-length = 120
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "W",   # pycodestyle warnings
    "I",   # isort
    "N",   # pep8-naming
    "B",   # flake8-bugbear
    "A",   # flake8-builtins
    "C4",  # flake8-comprehensions
    "T20", # flake8-print
]

[tool.ruff.format]
quote-style = "double"
```

**MyPy Configuration:**

```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false  # Start relaxed, tighten over time
ignore_missing_imports = true  # For third-party libraries
```

### Task Automation with Justfile

**Justfile Benefits:**

- Simpler syntax than Makefiles
- Cross-platform compatibility
- Built-in help system
- Environment variable support

```justfile
# Justfile template
default: check test

# Install development dependencies
install:
    uv sync --dev

# Run all tests
test:
    uv run python -m pytest tests/ -v

# Run all checks (format, lint, type check)
check: format lint typecheck

# Format code and fix issues
format:
    uv run ruff check --fix src/ tests/
    uv run ruff format src/ tests/

# Lint code (without fixing)
lint:
    uv run ruff check src/ tests/

# Type check with mypy
typecheck:
    uv run mypy src/ tests/

# Run tests with coverage
test-cov:
    uv run python -m pytest tests/ --cov=package_name --cov-report=term-missing

# Build the package
build:
    uv build

# Clean build artifacts
clean:
    rm -rf dist/ build/ *.egg-info/ .pytest_cache/ .mypy_cache/ .ruff_cache/

# Generate outputs (project-specific)
generate:
    uv run python -m package_name --all-options
```

## Testing Strategies

### Modern Pytest-based Testing

**Prefer pytest over unittest for new projects:**

```python
# tests/test_module.py
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest

from package_name import function_to_test, CONSTANTS


def test_normal_case():
    """Test normal operation."""
    test_data = [...]
    result = function_to_test(test_data)
    assert result == expected_value


def test_edge_case():
    """Test edge cases."""
    result = function_to_test([])
    assert result == []


@pytest.mark.parametrize(
    "input_value,expected_output",
    [
        ("input1", "output1"),
        ("input2", "output2"),
        ("edge_case", "edge_result"),
    ],
)
def test_parametrized_cases(input_value, expected_output):
    """Test multiple cases with parametrization."""
    result = function_to_test(input_value)
    assert result == expected_output


def test_constants_validity():
    """Test that constants are properly defined."""
    assert isinstance(CONSTANTS, dict)
    assert len(CONSTANTS) > 0


def test_real_data_processing():
    """Test processing of real data files."""
    test_file_path = Path("test_data.pdf")
    if not test_file_path.exists():
        pytest.skip("Test data file not available")
    
    result = process_real_file(test_file_path)
    assert len(result) > 0


# Fixtures for reusable test data
@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return [
        {"date": datetime(2025, 6, 2), "types": ["organic"]},
        {"date": datetime(2025, 6, 3), "types": ["residual"]},
    ]


def test_with_fixture(sample_data):
    """Test using pytest fixture."""
    result = process_data(sample_data)
    assert len(result) == len(sample_data)


# Integration tests using real I/O with cleanup
def test_file_generation():
    """Test file generation with temporary files."""
    test_data = [{"date": datetime(2024, 1, 1), "icons": "Test"}]
    
    with tempfile.NamedTemporaryFile(suffix=".ics", delete=False) as tmp_file:
        tmp_path = tmp_file.name
    
    try:
        result = generate_calendar(test_data, tmp_path)
        assert result > 0
        
        # Verify file contents
        assert Path(tmp_path).exists()
        with open(tmp_path, "r") as f:
            content = f.read()
        assert "Test" in content
        
    finally:
        Path(tmp_path).unlink(missing_ok=True)
```

### Dependency Injection vs Mocking

**Prefer dependency injection over mocking when possible:**

```python
# Instead of mocking (harder to maintain)
@patch("external_service.api_call")
def test_with_mock(mock_api):
    mock_api.return_value = "mocked_result"
    result = function_that_calls_api()
    assert result == expected

# Use dependency injection (more testable)
def create_mock_api_service():
    """Create a mock API service for testing."""
    def mock_api_call(url):
        return "mocked_result"
    return mock_api_call

def test_with_dependency_injection():
    """Test using dependency injection."""
    mock_service = create_mock_api_service()
    result = function_that_accepts_service(mock_service)
    assert result == expected

# Real function designed for testability
def process_data_with_service(data, api_service=None):
    """Process data using provided or default API service."""
    if api_service is None:
        api_service = default_api_service
    
    return [api_service(item) for item in data]
```

### Testing Best Practices

1. **Use pytest over unittest** for new projects - simpler syntax, better parametrization
2. **Prefer dependency injection over mocking** when possible - more maintainable
3. **Use pytest.mark.parametrize** for testing multiple inputs efficiently
4. **Create fixtures** for reusable test data and setup
5. **Test with real I/O when practical** - use temporary files for file operations
6. **Use descriptive test function names** that explain the scenario being tested
7. **Group related tests** in separate modules (test_pdf_extraction.py, test_output_generation.py)
8. **Add path configuration** for VS Code test discovery compatibility
9. **Clean up resources** properly in tests (use try/finally or context managers)
10. **Skip tests gracefully** when dependencies aren't available using pytest.skip()

### Test Organization by Modules

```python
# tests/test_pdf_extraction.py - PDF processing functions
def test_group_elements_by_rows_empty(): ...
def test_detect_month_january(): ...

# tests/test_output_generation.py - Output generation functions  
def test_generate_calendar_with_events(): ...
def test_extract_language_from_waste_description_german(): ...

# tests/test_constants.py - Module constants
def test_month_numbers_mapping(): ...
def test_waste_type_keywords(): ...

# tests/test_integration.py - Integration and end-to-end tests
def test_full_workflow_with_real_data(): ...
def test_expected_extraction_results(): ...
```

## CLI Design Patterns

### Argument Parser Structure

```python
import argparse

def create_parser():
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="Clear description of what the tool does"
    )
    
    # Positional arguments with sensible defaults
    parser.add_argument(
        "input_file",
        nargs="?",  # Optional positional
        default="default_filename.ext",
        help="Input file (default: default_filename.ext)"
    )
    
    # Output options
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: auto-generated)"
    )
    
    # Behavior options with choices
    parser.add_argument(
        "-l", "--language",
        choices=["en", "fr", "de"],
        help="Output language"
    )
    
    # Boolean flags
    parser.add_argument(
        "--all-languages",
        action="store_true",
        help="Generate outputs for all languages"
    )
    
    parser.add_argument(
        "--download",
        action="store_true", 
        help="Download latest input file"
    )
    
    # Numeric arguments with validation
    parser.add_argument(
        "-y", "--year",
        type=int,
        default=2025,
        help="Year for processing (default: 2025)"
    )
    
    # Debugging options
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser

def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Set up logging based on verbosity
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level)
    
    try:
        # Main processing logic
        if args.download:
            download_input_file()
        
        result = process_input(args.input_file, args.year)
        
        if args.all_languages:
            generate_all_outputs(result)
        elif args.language:
            generate_language_output(result, args.language)
        else:
            generate_default_output(result, args.output)
            
    except Exception as e:
        logging.error(f"Error: {e}")
        return 1
    
    return 0
```

## Public API Design

### Module **init**.py Patterns

```python
# __init__.py - Define public API clearly
"""Package description."""

# Import external dependencies needed by public API
from external_lib import ExternalClass

# Import public functions and classes
from .core_module import main_function, important_class
from .constants import PUBLIC_CONSTANTS
from .utilities import helper_function

# Define what gets exported with "from package import *"
__all__ = [
    "main_function",
    "important_class", 
    "PUBLIC_CONSTANTS",
    "helper_function",
    "ExternalClass",  # Re-export for convenience
]
```

**API Design Principles:**

- Keep the public API minimal and stable
- Re-export commonly used external dependencies
- Use `__all__` to control what gets imported with `import *`
- Group imports logically (external, then internal)

## Internationalization Patterns

### Multi-language Support

```python
# Language-specific processing
def extract_language_content(multilingual_text: str, language: str) -> str:
    """Extract content for specific language from multilingual text."""
    parts = [part.strip() for part in multilingual_text.split("|") if part.strip()]
    
    if len(parts) <= 1:
        return multilingual_text.strip()
    
    # Language-specific extraction logic
    language_patterns = {
        "en": ["english", "terms", "here"],
        "fr": ["french", "terms", "here"], 
        "de": ["german", "terms", "here"],
    }
    
    # Try to find language-specific content
    if language in language_patterns:
        for part in parts:
            if any(term in part.lower() for term in language_patterns[language]):
                return part
    
    # Fallback strategies by language
    fallbacks = {
        "en": lambda parts: parts[-1],  # Last part often English
        "fr": lambda parts: parts[1] if len(parts) > 1 else parts[0],  # Middle part
        "de": lambda parts: parts[0],   # First part often German
    }
    
    return fallbacks.get(language, lambda p: p[0])(parts)

# Multi-language output generation
def generate_language_outputs(data: list, languages: list[str]) -> dict[str, int]:
    """Generate outputs for multiple languages."""
    results = {}
    
    for lang in languages:
        count = generate_single_language_output(data, lang)
        results[lang] = count
        logging.info(f"Generated {lang} output with {count} items")
    
    return results
```

## Error Handling Patterns

### Robust Error Handling

```python
import logging
from pathlib import Path

def robust_file_processing(file_path: str) -> list:
    """Process file with comprehensive error handling."""
    file_path = Path(file_path)
    
    # Validate inputs
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if not file_path.suffix.lower() == '.pdf':
        raise ValueError(f"Expected PDF file, got: {file_path.suffix}")
    
    try:
        # Main processing logic
        results = process_file_contents(file_path)
        
        if not results:
            logging.warning(f"No data extracted from {file_path}")
        
        return results
        
    except PermissionError:
        logging.error(f"Permission denied accessing {file_path}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error processing {file_path}: {e}")
        raise

def download_with_retry(url: str, output_path: str, max_retries: int = 3) -> bool:
    """Download file with retry logic."""
    for attempt in range(max_retries):
        try:
            urllib.request.urlretrieve(url, output_path)
            logging.info(f"Successfully downloaded {url} to {output_path}")
            return True
        except Exception as e:
            logging.warning(f"Download attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                logging.error(f"Failed to download after {max_retries} attempts")
                return False
    return False
```

## Logging Best Practices

### Structured Logging Setup

```python
import logging

def setup_logging(level: str = "INFO") -> None:
    """Configure logging with appropriate format and level."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S"
    )

# Usage throughout application
def process_data(data):
    logging.info(f"Processing {len(data)} items")
    
    for i, item in enumerate(data):
        logging.debug(f"Processing item {i}: {item}")
        
        try:
            result = process_item(item)
            logging.debug(f"Item {i} processed successfully")
        except Exception as e:
            logging.error(f"Error processing item {i}: {e}")
            continue
    
    logging.info("Data processing complete")
```

## Documentation Standards

### README Structure

```markdown
# Project Name

Brief description with clear value proposition.

## Quick Start

Minimal example to get users started immediately.

## Installation

### Using uv (recommended)

```bash
uv sync
```

### Using pip

```bash
pip install -e .
```

## Usage

### Basic Usage

```bash
command --help
```

### Advanced Usage

```bash
# Common patterns with explanations
command --option value
```

## Development

```bash
# Essential development commands
just test
just check
just build
```

## License

Clear license information.

### Inline Documentation

```python
def complex_function(data: list[dict], options: dict) -> tuple[list, int]:
    """
    Process data according to specified options.
    
    Args:
        data: List of dictionaries containing raw data
        options: Configuration dictionary with processing options
        
    Returns:
        Tuple of (processed_data, items_processed_count)
        
    Raises:
        ValueError: If data format is invalid
        TypeError: If options are not a dictionary
        
    Example:
        >>> data = [{"key": "value"}]
        >>> options = {"language": "en"}
        >>> result, count = complex_function(data, options)
        >>> print(f"Processed {count} items")
    """
    pass
```

## Version Control Patterns

### .gitignore Template

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project-specific
*.ics
*.pdf
/output/
/temp/

# Keep important examples
!examples/*.pdf
!examples/*.ics
```

## Performance Considerations

### Efficient Data Processing

```python
from functools import lru_cache
from typing import Generator

@lru_cache(maxsize=128)
def expensive_lookup(key: str) -> str:
    """Cache expensive lookup operations."""
    # Expensive computation here
    return result

def batch_process_generator(data: list, batch_size: int = 100) -> Generator:
    """Process data in batches to manage memory."""
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]

def process_large_dataset(data: list) -> list:
    """Process large datasets efficiently."""
    results = []
    
    for batch in batch_process_generator(data):
        batch_results = [process_item(item) for item in batch]
        results.extend(batch_results)
        
        # Optional: Log progress for long operations
        logging.info(f"Processed {len(results)}/{len(data)} items")
    
    return results
```

## Continuous Integration

### GitHub Actions Template

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
        
    steps:
    - uses: actions/checkout@v4
    
    - name: Install uv
      uses: astral-sh/setup-uv@v1
      
    - name: Set up Python ${{ matrix.python-version }}
      run: uv python install ${{ matrix.python-version }}
      
    - name: Install dependencies
      run: uv sync --dev
      
    - name: Run tests
      run: uv run python -m pytest tests/ -v
      
    - name: Run linting
      run: uv run ruff check src/ tests/
      
    - name: Run type checking  
      run: uv run mypy src/ tests/
```

## Summary

These patterns provide a solid foundation for modern Python projects with:

- **Clear project structure** with separation of concerns
- **Modern tooling** (uv, ruff, mypy, justfile)
- **Comprehensive testing** strategies
- **Robust error handling** and logging
- **Multi-language support** patterns
- **Professional documentation** standards
- **Automated quality assurance**

Apply these patterns consistently to create maintainable, professional Python projects.
