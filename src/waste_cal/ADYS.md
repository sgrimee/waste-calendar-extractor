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

### Command Line

```bash
# Extract with auto-detected year (from PDF)
just extract-adys pdf/adys.pdf

# Or directly:
uv run python -m waste_cal.adys_extractor pdf/adys.pdf
```

### Python API

```python
from waste_cal.adys_extractor import extract_adys_dates

# Extract dates (auto-detect year from PDF)
dates = extract_adys_dates("pdf/adys.pdf")
for date in dates:
    print(date)  # Output: 2026-03-03, 2026-06-09, ...

# Extract with explicit year
dates = extract_adys_dates("pdf/adys.pdf", year=2027)
```

## Output

Returns a sorted list of ISO format dates (YYYY-MM-DD):

```
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

dates = extract_adys_dates("pdf/adys.pdf")

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
