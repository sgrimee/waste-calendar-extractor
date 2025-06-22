# PDF Areas Documentation

## Overview

This document describes the detected calendar and legend areas from the waste collection PDF calendar. The coordinates are extracted from page 2 and used as a template for all subsequent pages to ensure consistent area detection.

## Page Layout Analysis

The PDF pages (2-14) contain:

- **Left Side**: Monthly calendar grid with dates and waste collection icons
- **Right Side**: Legend explaining waste types and collection instructions

## Detected Coordinates (Page 2 Template)

### Calendar Area (Left Side)

- **Top-left corner**: (54.5, 39.0)
- **Bottom-right corner**: (328.4, 808.3)
- **Dimensions**: 273.9 × 769.3 pixels
- **Content**: Monthly calendar grid, dates, weekday names, waste collection icons

### Legend Area (Right Side)

- **Top-left corner**: (373.0, 15.6)
- **Bottom-right corner**: (593.0, 812.5)
- **Dimensions**: 220.1 × 796.9 pixels
- **Content**: Waste type descriptions, icons legend, collection service information

## Coordinate System

- **Origin**: Top-left corner of the page (0, 0)
- **X-axis**: Increases from left to right
- **Y-axis**: Increases from top to bottom
- **Units**: PDF coordinate points

## Template File

The coordinates are saved in `debug/page_areas.json` for reuse:

```json
{
  "calendar_area": {
    "x0": 54.50779724121094,
    "y0": 39.008888244628906,
    "x1": 328.43017578125,
    "y1": 808.2675170898438
  },
  "legend_area": {
    "x0": 372.9606018066406,
    "y0": 15.598304748535156,
    "x1": 593.017822265625,
    "y1": 812.4893798828125
  }
}
```

## areas_per_day Function Algorithm

### Purpose

The `areas_per_day` function is the core algorithm responsible for dividing the monthly calendar area into precise rectangular regions for each individual day. This enables accurate extraction of waste collection symbols associated with specific dates.

### Algorithm Overview

The function operates in four distinct phases:

1. **Day Number Detection**: Scans the calendar area to locate all day numbers (1-31) and their precise coordinates
2. **Spatial Analysis**: Calculates the center positions and spacing patterns of detected day numbers
3. **Grid Line Calculation**: Determines horizontal boundaries between day rows using uniform spacing
4. **Area Generation**: Creates rectangular regions for each day bounded by consecutive grid lines

### Detailed Algorithm Steps

#### Phase 1: Day Number Detection

```
FOR each text block in calendar_area:
    FOR each text span:
        IF text is digit AND 1 <= digit <= 31:
            EXTRACT bounding box coordinates
            CALCULATE y_center = (bbox_top + bbox_bottom) / 2
            STORE {day_number, y_top, y_bottom, y_center}
SORT day_positions by day_number
```

**Key insight**: Day numbers are reliably present and positioned at the vertical center of each day's row.

#### Phase 2: Spacing Analysis

```
IF multiple days detected:
    total_spacing = SUM(day[i].y_center - day[i-1].y_center) for i=1 to n-1
    avg_spacing = total_spacing / (n-1)
ELSE:
    avg_spacing = 23.2  // Default based on calendar format analysis
```

**Key insight**: Days are arranged in a uniform grid with consistent vertical spacing of ~23.2 points between row centers.

#### Phase 3: Grid Line Positioning

Grid lines are the horizontal boundaries that separate day rows:

```
grid_lines = []

// First boundary: half-spacing above day 1
grid_lines[0] = day[0].y_center - (avg_spacing / 2)

// Inter-day boundaries: midpoint between consecutive day centers  
FOR i = 0 to n-2:
    midpoint = (day[i].y_center + day[i+1].y_center) / 2
    grid_lines[i+1] = midpoint

// Final boundary: half-spacing below last day
grid_lines[n] = day[n-1].y_center + (avg_spacing / 2)
```

**Key insight**: Grid lines are positioned to equally divide the space between day centers, ensuring each day gets uniform vertical space.

#### Phase 4: Area Rectangle Generation

```
FOR each day i from 0 to n-1:
    y_top = grid_lines[i]
    y_bottom = grid_lines[i+1]
    
    day_area = Rectangle(
        left = CALENDAR_AREA.x0,
        top = y_top,
        right = CALENDAR_AREA.x1, 
        bottom = y_bottom
    )
```

### Critical Properties

1. **Uniform Coverage**: Every pixel in the calendar area belongs to exactly one day area
2. **No Gaps**: Adjacent day areas share boundaries with no space between them
3. **No Overlaps**: Day areas are mutually exclusive rectangular regions
4. **Consistent Width**: All day areas span the full calendar width (273.9 points)
5. **Variable Height**: Day area height equals the uniform spacing (~23.2 points)

### Robustness Features

- **Flexible Month Lengths**: Automatically adapts to months with 28-31 days
- **Spacing Tolerance**: Uses actual detected spacing rather than hardcoded values
- **Error Handling**: Raises ValueError if no day numbers are detected
- **Debug Logging**: Provides detailed coordinates for verification

### Usage in Extraction Pipeline

```
calendar_areas = areas_per_day(page)
FOR each day_area in calendar_areas:
    symbols = extract_symbols_from_area(page, day_area)
    date = calculate_date(month, day_number)
    associate_symbols_with_date(date, symbols)
```

### Performance Characteristics

- **Time Complexity**: O(n) where n is the number of text spans in calendar area
- **Space Complexity**: O(d) where d is the number of days in month (≤31)
- **Typical Runtime**: <10ms for processing a monthly calendar page

## Technical Notes

- Page dimensions are approximately 596 × 842 points (A4 size)
- Calendar area covers roughly 46% of page width
- Legend area covers roughly 37% of page width
- Small gap (≈44 points) separates calendar and legend areas
- Areas span nearly the full page height with minimal top/bottom margins
