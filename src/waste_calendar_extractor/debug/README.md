# Debug and Analysis Tools

This directory contains development and debugging utilities for the waste calendar extractor. These scripts are not required for normal operation but are useful for:

## Available Scripts

### PDF Analysis
- **`debug_pdf.py`** - Basic PDF structure debugging
- **`debug_pdf_images.py`** - PDF image extraction and analysis
- **`analyze_calendar_layout.py`** - Calendar layout structure analysis

### Symbol and Legend Analysis  
- **`analyze_symbol_types.py`** - Waste type symbol analysis
- **`map_waste_symbols.py`** - Symbol to waste type mapping
- **`debug_legend_extraction.py`** - Legend extraction debugging

### Integration Testing
- **`test_legend_integration.py`** - Integration tests for legend processing

## Usage

Run these scripts from the project root with:

```bash
# Example: Run PDF debugging
PYTHONPATH=src python src/waste_calendar_extractor/debug/debug_pdf.py

# Example: Analyze calendar layout
PYTHONPATH=src python src/waste_calendar_extractor/debug/analyze_calendar_layout.py
```

## Purpose

These tools were created during development to:
- Understand the PDF structure and layout
- Debug text extraction issues
- Analyze symbol recognition patterns
- Test integration between different components
- Validate extraction logic against known data

They serve as reference implementations and debugging aids for future development work.