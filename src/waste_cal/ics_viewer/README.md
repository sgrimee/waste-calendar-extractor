# iCS Calendar Viewer

A beautiful, colored command-line viewer for iCS calendar files that provides human-readable output for verification and debugging purposes.

## Features

- 🌈 **Colored terminal output** with waste type-specific colors
- 📅 **Monthly calendar grid view** showing events by day
- 📋 **Detailed event listings** with chronological ordering
- 📊 **Summary statistics** with event counts by type
- 🎨 **Emoji icons** for different waste types (🗑️📄🪟📦🌱👕🎄♻️)
- 🎛️ **Multiple output formats** (full, summary, calendar, list)
- 🎨 **Color disable option** for non-terminal output

## Usage

### Command Line

```bash
# View full calendar (all sections)
PYTHONPATH=src uv run python -m waste_calendar_extractor.ics_viewer waste.ics

# View only summary statistics
PYTHONPATH=src uv run python -m waste_calendar_extractor.ics_viewer waste.ics --format summary

# View only calendar grid
PYTHONPATH=src uv run python -m waste_calendar_extractor.ics_viewer waste.ics --format calendar

# View only event list
PYTHONPATH=src uv run python -m waste_calendar_extractor.ics_viewer waste.ics --format list

# Disable colors (for redirecting to files)
PYTHONPATH=src uv run python -m waste_calendar_extractor.ics_viewer waste.ics --no-color
```

### Justfile Commands

The project includes convenient justfile commands for viewing calendars:

```bash
# View main calendar
just view-main

# View all language-specific calendars (summary)
just view-all

# View specific language calendar
just view-lang lu    # Luxembourgish
just view-lang fr    # French
just view-lang en    # English

# View any calendar file
just view-file my-calendar.ics

# View with specific formats
just view-summary waste.ics
just view-calendar waste.ics
just view-list waste.ics
```

## Output Format

### Summary Section
Shows calendar overview:
- Total number of events
- Date range covered
- Event counts by waste type with emoji icons

### Calendar Grid Section
Monthly calendar view with:
- Traditional calendar layout
- Bold highlighting for days with events
- Month and year headers

### Event List Section
Chronological listing with:
- Date headers for each day
- Colored event names with emoji icons
- Location information
- Event descriptions

## Color Coding

The viewer uses intuitive color coding for different waste types:

- 🗑️ **Red**: Residual/household waste
- 📄 **Blue**: Paper and cardboard
- 🪟 **Green**: Glass collections
- 📦 **Yellow**: Packaging/VALORLUX
- 🌱 **Green**: Organic waste
- 👕 **Magenta**: Old clothes/textiles
- 🎄 **Green**: Christmas trees
- ♻️ **Cyan**: General recycling

## Examples

### Summary Output
```
📊 Calendar Summary
Total events: 108
Date range: 2025-01-01 to 2025-12-31

Events by type:
  🗑️ Residual waste: 52
  📄 Paper: 24
  🪟 Glass: 12
  📦 Packaging: 12
  🌱 Organic: 8
```

### Event List Output
```
📋 Event Details

Monday, June 02, 2025
  • 🌱 Organic waste (Niederanven, Luxembourg)
  • 🌲 Hedge trimming (Niederanven, Luxembourg)

Tuesday, June 03, 2025
  • 🗑️ Residual waste (Niederanven, Luxembourg)

Wednesday, June 04, 2025
  • ⚡ Electric waste (Niederanven, Luxembourg)
```

## Integration

The viewer can be imported and used programmatically:

```python
from waste_calendar_extractor.ics_viewer import view_ics_file, generate_calendar_view

# Generate full view
output = view_ics_file("my-calendar.ics", "full")
print(output)

# Generate summary only
summary = view_ics_file("my-calendar.ics", "summary")
print(summary)
```

## Purpose

This viewer is designed for:

- **Verification**: Quickly check if generated calendars contain expected events
- **Debugging**: Identify issues with date extraction or event formatting
- **Human review**: Provide readable output for manual validation
- **Documentation**: Generate examples for documentation or reporting
- **Quality assurance**: Ensure calendar files are properly formatted

The colored, emoji-rich output makes it easy to spot patterns, missing events, or formatting issues at a glance.