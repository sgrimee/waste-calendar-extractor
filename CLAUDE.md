# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a waste collection calendar extractor that extracts dates and waste types from PDF calendars published by the Commune of Niederanven, Luxembourg, and generates multilingual iCal calendar files.

## Architecture

### Core Processing Pipeline

The extraction follows a clear pipeline:

1. **PDF Analysis** (`pdf_extractor.py`) - Uses PyMuPDF to extract positioned text elements
2. **Calendar Processing** (`calendar_processor.py`) - Orchestrates the extraction workflow, processes pages sequentially  
3. **Output Generation** (`output_generator.py`) - Creates iCal files with language filtering and emoji icons
4. **CLI Interface** (`cli.py`) - Handles argument parsing and user interaction

### Key Architectural Patterns

**Multilingual Support**: Each waste type description contains multiple languages separated by `|` (e.g., "Reschtoffäll | Déchets ménagers | Residual waste"). The `extract_language_from_waste_description()` function filters these based on language-specific patterns and fallback strategies.

**Month Detection**: Uses Luxembourgish month names (`JANUAR`, `MÄERZ`, etc.) to track calendar progression across PDF pages.

**Spatial Text Processing**: Groups text elements by Y-coordinate proximity to identify calendar rows, then matches dates (1-31) with waste type keywords in the same row.

**Dependency Injection for Testing**: Tests use factory functions to create mock services rather than patching, making them more maintainable.

## Development Commands

**Essential commands (using justfile):**

```bash
# Development setup
just install                    # Install dev dependencies with uv

# Testing
just test                      # Run all tests with pytest
just test-cov                  # Run tests with coverage report
pytest tests/test_constants.py # Run specific test module

# Code quality  
just check                     # Run all checks (format, lint, typecheck)
just format                    # Auto-fix code with ruff
just lint                      # Check code without fixing
just typecheck                 # Run mypy type checking

# Calendar generation
just generate                  # Generate all language calendars for current year
just generate-year 2026        # Generate for specific year
just generate-lang de          # Generate German/Luxembourgish only
just clean-waste              # Remove all generated waste-*.ics files

# Calendar viewing
just view-all                  # View all generated calendars in summary
just view-main                 # View main waste.ics calendar
just view-file myfile.ics     # View specific calendar file

# Build and cleanup
just build                     # Build package with uv
just clean                     # Remove build artifacts
```

**Manual commands (without justfile):**

```bash
# Testing
PYTHONPATH=src uv run python -m pytest tests/ -v
PYTHONPATH=src uv run python -m pytest tests/test_integration.py::test_june_2025_expected_dates -v

# Running the extractor
PYTHONPATH=src uv run python -m waste_calendar_extractor --help
PYTHONPATH=src uv run python -m waste_calendar_extractor --all-languages -v
PYTHONPATH=src uv run python -m waste_calendar_extractor --download

# Type checking and linting
PYTHONPATH=src uv run mypy src/ tests/
uv run ruff check src/ tests/
```

## Important Development Notes

**PYTHONPATH Requirements**: All commands that import the package require `PYTHONPATH=src` due to the src-layout structure. The justfile handles this automatically.

**Test Organization**: Tests are split into logical modules:
- `test_constants.py` - Module constants validation
- `test_pdf_extraction.py` - PDF processing functions  
- `test_output_generation.py` - Calendar generation and language filtering
- `test_integration.py` - End-to-end scenarios and expected extraction results

**Expected Extraction Results**: The `test_june_2025_expected_dates` test validates specific expected outcomes for June 2025, including verification that days 1 and 8 have no waste collection.

**Package Management**: Project uses `uv` for fast dependency management. Fallback to `pip install -e .` if uv unavailable.

**Calendar File Naming**: Generated files follow pattern `waste-{year}-{lang}.ics` (e.g., `waste-2025-de.ics`). The main multilingual file is `waste.ics`.

## Module Dependencies

**Core Dependencies**:
- `PyMuPDF>=1.23.0` - PDF text extraction
- `ics>=0.7` - iCal calendar generation

**Development Dependencies**:
- `pytest>=8.4.0` - Testing framework (uses pytest, not unittest)
- `ruff>=0.11.13` - Code formatting and linting
- `mypy>=1.16.0` - Type checking

## Testing Approach

Tests use **pytest with dependency injection** rather than mocking where possible. For example, `create_mock_extraction_function()` creates test doubles instead of using `@patch`. File I/O tests use real temporary files with proper cleanup.

Use `@pytest.mark.parametrize` for efficient testing of multiple inputs (e.g., waste type icon mappings).