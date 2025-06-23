# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a waste collection calendar extractor that extracts dates and waste types from PDF calendars published by the Commune of Niederanven, Luxembourg, and generates multilingual iCal calendar files.

## Architecture

### Core Processing Pipeline

The extraction follows a clear pipeline:

1. **PDF Analysis** (`pdf_extractor.py`) - Uses area-based extraction with predefined calendar and legend coordinates
2. **Calendar Processing** (`calendar_processor.py`) - Orchestrates the extraction workflow, processes pages sequentially  
3. **Output Generation** (`output_generator.py`) - Creates iCal files with language filtering and emoji icons
4. **CLI Interface** (`cli.py`) - Handles argument parsing and user interaction

### Key Architectural Patterns

**Area-Based PDF Extraction**: Uses predefined coordinate areas (`page_areas.json`) to separate calendar content (left side) from legend information (right side). This eliminates confusion between calendar symbols and legend text.

**Symbol Classification**: TBD

**Dependency Injection for Testing**: Tests use factory functions to create mock services rather than patching, making them more maintainable.

## Development Commands

**Essential commands (using justfile):**

```bash
# Development setup
just install                    # Install dev dependencies with uv

# Testing
just test                      # Run all tests including integration tests
just test-unit                 # Run only unit tests (exclude integration) - for CI
just test-integration          # Run only integration tests
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
just generate-lang lu          # Generate Luxembourgish only
just clean-waste              # Remove all generated ics/waste-*.ics files

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

# Running the extractor
PYTHONPATH=src uv run python -m waste_cal

# Type checking and linting
PYTHONPATH=src uv run mypy src/ tests/
uv run ruff check src/ tests/
```

## Important Development Notes

**Imports**: All imports should be absolute and ordered as per ruff standard.

**PYTHONPATH Requirements**: All commands that import the package require `PYTHONPATH=src` due to the src-layout structure. The justfile handles this automatically.

**Test Organization**: Tests are split into logical modules following the name and path of the modules they test.

**Package Management**: Project uses `uv` for fast dependency management. Fallback to `pip install -e .` if uv unavailable.

**Calendar File Naming**: Generated files follow pattern `ics/waste-{year}-{lang}.ics` (e.g., `ics/waste-2025-de.ics`). PDF files are stored in the `pdf/` folder.

**CI Configuration**: GitHub Actions workflow (`.github/workflows/ci.yml`) runs unit tests only, excluding integration tests that require the PDF file. Use `just test-unit` locally to replicate CI behavior.

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

## Conventions

- pdf files should be saved in the pdf/ folder
- ics files should be saved in the ics/ folder

## Memories

- The telephone icon and the arrow icon do not represent collection types, they just mean the user need to book the collection by phone or web in advance for the collection type represented by the icon that follows.
- The `test_2025_expected_dates` test validates specific expected outcomes. The test must be considered correct and must not be changed.
- Create all your temporary scripts in the debug/ folder.
- Save temporary pdf to the debug folder, not the pdf/ folder. That one is for persistent pdfs.
- The areas for each day have the same exact dimensions. For monthes with less than 31 days, there are empty rows at the bottom, so the total height of a month calendar is always 31 times the height of the box for one day