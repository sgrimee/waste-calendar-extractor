# ADYS Trash Cleaning Calendar Extractor

## Overview

The `adys_extractor.py` module provides functionality to extract trash can cleaning dates from ADYS PDF calendars. ADYS is a waste management service provider in Luxembourg that publishes annual cleaning schedules for organic waste bins.

## How It Works

The extraction process analyzes the PDF structure to identify cleaning dates marked with green squares:

1. **Green Marker Detection**: Scans the PDF for green-colored rectangles (RGB: 0.0, 0.5, 0.25)
2. **Position Mapping**: Extracts day numbers (1-31) and month names with their coordinates
3. **Spatial Matching**: Maps each green mark to the nearest day and month using distance calculations
4. **Legend Filtering**: Removes false positives from the legend area using strict distance thresholds
5. **Date Conversion**: Converts matched positions to ISO format dates (YYYY-MM-DD)

## Calendar Structure

The ADYS PDF has a grid layout:
- **Rows**: Days 1-31 (labeled on the left column)
- **Columns**: 12 months (January through December)
- **Markers**: Green squares indicate cleaning dates for organic waste bins
- **Legend**: Bottom of page shows the color legend (filtered out during extraction)

## Usage

### Generating Combined Calendars (Recommended)

The easiest way to include ADYS dates in your calendar is to use the `--include-adys` flag. This generates **two files**:
- `ics/waste-{lang}.ics` - Standard waste calendar (without ADYS)
- `ics/waste-{lang}-adys.ics` - Combined calendar with waste collection + ADYS bin cleaning

#### Using Justfile (Easiest)

```bash
# Generate all languages with ADYS
just generate-with-adys

# Generate single language with ADYS
just generate-lang-with-adys en
just generate-lang-with-adys fr
just generate-lang-with-adys lu

# Generate for specific year with ADYS
just generate-lang-year-with-adys en 2027
```

#### Using CLI Directly

```bash
# Generate all languages with ADYS (uses default sources/adys-{customer_id}-{year}.pdf)
uv run waste-cal --include-adys

# Single language with default ADYS path
uv run waste-cal --language en --include-adys

# Single language with custom ADYS path
uv run waste-cal --language en --include-adys /path/to/custom-adys.pdf

# Single language and custom year
uv run waste-cal --language en --year 2027 --include-adys
```

### Extracting ADYS Dates Only

For standalone extraction without generating calendars:

```bash
# Extract with auto-detected year
just extract-adys sources/adys-019027-2026.pdf

# Or directly:
uv run python -m waste_cal.adys_extractor sources/adys-019027-2026.pdf
```

### Python API

```python
from waste_cal.adys_extractor import extract_adys_dates

# Extract dates (auto-detect year from PDF)
dates = extract_adys_dates("sources/adys-019027-2026.pdf")
for date in dates:
    print(date)  # Output: 2026-03-03, 2026-06-09, ...
```

## Calendar Events

When ADYS dates are included in the calendar, bin cleaning events appear with:

- **Icon**: 🚿 (shower - representing cleaning)
- **Names by language**:
  - English: "Organic bin cleaning"
  - French: "Nettoyage poubelle organique"
  - Luxembourgish: "Poubelle botzen"
- **Alarms**: Same as waste collection events (day before at 20:30)
- **Location**: Niederanven, Luxembourg

Example event in calendar:
```
🚿 Organic bin cleaning (2026-03-03)
Reminder: Organic bin cleaning will be performed tomorrow.
```

### Output Dates

Standalone extraction returns a sorted list of ISO format dates (YYYY-MM-DD):

```python
['2026-03-03', '2026-06-09', '2026-09-01', '2026-12-08']
```

Each date represents a scheduled cleaning for organic waste bins (typically 4 cleanings per year).

## Technical Details

### Green Color Detection
The extractor looks for rectangles with RGB values:
- **Exact**: (0.0, 0.5, 0.25)
- **Tolerance**: ±0.1 per channel

### Filtering Strategy
To distinguish calendar marks from legend marks, the extractor:
1. Calculates distance from each green mark to the nearest grid intersection
2. Keeps marks within 10 pixels (x) and 10 pixels (y) of a day/month intersection
3. Relaxes thresholds to 20/15 pixels if fewer than 3 valid marks found

### Error Handling
The module raises exceptions for:
- **ValueError**: If PDF cannot be read
- **RuntimeError**: If PDF structure cannot be parsed (no dates/months found)

## Limitations

- Only works with ADYS calendars that use the standard green marker color
- Requires year to be present in PDF text or specified as parameter
- Assumes the calendar grid follows the standard ADYS layout
- Single-page PDF expected

## Example: Extract and Save to CSV

```python
import csv
from waste_cal.adys_extractor import extract_adys_dates

dates = extract_adys_dates("sources/adys-019027-2026.pdf")

with open("cleaning_dates.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["date", "service", "description"])
    writer.writeheader()
    for date in dates:
        writer.writerow({
            "date": date,
            "service": "adys",
            "description": "Organic Waste Bin Cleaning"
        })
```
