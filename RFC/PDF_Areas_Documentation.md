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

## Technical Notes

- Page dimensions are approximately 596 × 842 points (A4 size)
- Calendar area covers roughly 46% of page width
- Legend area covers roughly 37% of page width
- Small gap (≈44 points) separates calendar and legend areas
- Areas span nearly the full page height with minimal top/bottom margins
