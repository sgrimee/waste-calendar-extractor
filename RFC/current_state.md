# Waste Calendar Extractor - Current State

## Project Overview

A Python tool that extracts waste collection dates from PDF calendars published by the Commune of Niederanven, Luxembourg, and generates iCal files for easy calendar integration. The project has been significantly refactored with modular architecture.

## Current Architecture

### Module Structure

The codebase has been refactored from a monolithic file into a modular structure:

```bash
src/waste_calendar_extractor/
├── __init__.py          # Main module with public API exports
├── calendar_processor.py # PDF processing and date extraction logic
├── cli.py              # Command-line interface
├── constants.py        # Constants (month names, waste type keywords)
├── output_generator.py # iCal generation, language filtering, icons
└── pdf_extractor.py    # Low-level PDF text extraction utilities
```

### Key Components

#### 1. PDF Processing (`calendar_processor.py`)

- `extract_dates_from_pdf()`: Main function to process entire PDF
- `process_pdf_page()`: Process individual PDF pages
- Handles Luxembourgish month detection and date extraction

#### 2. Text Extraction (`pdf_extractor.py`)

- `extract_text_elements()`: Extract positioned text from PDF pages
- `group_elements_by_rows()`: Group text elements by Y-coordinate
- `detect_month()`: Find Luxembourgish month names
- `extract_date_and_waste_types()`: Extract dates and waste types from rows

#### 3. Output Generation (`output_generator.py`)

- `generate_ical_calendar()`: Create iCal files with emoji icons
- `generate_all_language_calendars()`: Generate de/fr/en language-specific calendars
- `extract_language_from_waste_description()`: Filter multilingual descriptions
- `get_waste_type_icon()`: Map waste types to emoji icons (🗑️📄🪟📦🌱👕🎄♻️)
- `download_calendar_pdf()`: Download PDFs from commune website

#### 4. CLI Interface (`cli.py`)

- Argument parsing for all options
- Language-specific generation (--language de/fr/en)
- PDF download capability (--download)
- All-languages generation (--all-languages)

## Language Support

- **German/Luxembourgish** (`de`): Primary language in PDF
- **French** (`fr`): Secondary language in PDF  
- **English** (`en`): Tertiary language in PDF
- Each language gets its own calendar file with filtered content and appropriate emoji icons

## Features Implemented

1. ✅ Modular architecture with separated concerns
2. ✅ Language-specific calendar generation (de/fr/en)
3. ✅ Emoji icons for different waste types
4. ✅ PDF download from commune website
5. ✅ Comprehensive test suite
6. ✅ Development automation with justfile
7. ✅ Multilingual README with user instructions

## Known Issues

### Critical Issue: Date Extraction Logic

**Problem**: The current extraction logic assumes one waste type per date, but the PDF actually has multiple collections per day.

**Current Behavior**:

- June 1: Only extracts first waste type found
- Creates separate events for each waste type instead of combining them

**Expected Behavior** (from user feedback):

```bash
June 2: organic and hedge
June 3: residual  
June 4: electric
June 5: paper and carton
June 6: packaging
June 7: organic
```

**Root Cause**:

- `extract_date_and_waste_types()` in `pdf_extractor.py` processes rows individually
- `process_pdf_page()` in `calendar_processor.py` creates separate events per row
- Need to group all waste types for the same date into single events

### Secondary Issues

1. Some language extraction returns empty strings
2. Test mocks need updating for new module structure
3. Need proper test data validation against real June 2025 dates

## Project Configuration

### Dependencies (`pyproject.toml`)

- **Runtime**: PyMuPDF (fitz), ics
- **Development**: pytest, ruff, mypy, build tools
- **Package manager**: uv (preferred), pip (fallback)

### Development Tools

- **Linting**: ruff (120 char line length, no black)
- **Type checking**: mypy with relaxed configuration
- **Testing**: pytest with coverage
- **Automation**: justfile for common tasks

### Git Status

- Significant refactoring completed
- Ready for date extraction logic fixes
- Test files updated for new architecture

## Next Steps (Priority Order)

### 1. Fix Date Extraction (HIGH PRIORITY)

- Modify `process_pdf_page()` to group waste types by date
- Update `extract_date_and_waste_types()` to handle multiple types per date
- Create combined calendar events instead of separate ones

### 2. Validate Against Real Data

- Test extraction against June 2025 expected results
- Fix any remaining language extraction issues
- Ensure all waste types are properly recognized

### 3. Update Tests

- Fix mock imports for new module structure
- Add integration tests for date grouping
- Implement the June 2025 validation test

### 4. Documentation

- Update command examples in README
- Document the date grouping behavior
- Add troubleshooting section

## File Locations

- **Main module**: `src/waste_calendar_extractor/`
- **Tests**: `tests/test_extract_dates.py`
- **Config**: `pyproject.toml`, `justfile`
- **Documentation**: `README.md`
- **Generated calendars**: `waste-2025-{de,fr,en}.ics`

## Commands

```bash
# Development
just test          # Run tests
just check         # Run all checks
just generate      # Generate all language calendars

# Manual testing
uv run python -m waste_calendar_extractor --all-languages
uv run python -m waste_calendar_extractor --download
```

This state reflects a well-architected project that needs critical date extraction logic fixes to properly handle multiple waste collections per day.
