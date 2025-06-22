#!/usr/bin/env python3
"""
PDF extraction utilities for waste collection calendars.

Key Features:
- Predefined coordinate areas eliminate calendar/legend confusion
- Precise row boundaries based on actual day number positions
- Symbol classification within calendar areas only
- Multilingual output with fallback descriptions

The extraction pipeline:
1. Extract calendar dates with precise row boundaries
2. Classify waste symbols within calendar area only
3. Map symbols to dates using row-based spatial matching
"""

import fitz
from loguru import logger

# Calendar area coordinates (left side of page where calendar content is located)
CALENDAR_AREA = {"x0": 54.5, "y0": 39.0, "x1": 328.4, "y1": 808.3}


def read_pdf(file_path: str) -> fitz.Document:
    """
    Read a PDF file and return a PyMuPDF Document object.

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        fitz.Document: Document object representing the PDF.
    """
    try:
        doc = fitz.open(file_path)
        logger.debug(f"PDF opened successfully: {file_path}")
        return doc
    except Exception as e:
        logger.error(f"Failed to open PDF file {file_path}: {e}")
        raise


def areas_per_day(page: fitz.Page) -> list[fitz.Rect]:
    """
    Get the rectangular areas for each day in the calendar.

    Args:
        page: The PDF page containing the calendar for a specific month.

    Returns:
        List of rectangles representing each day's area.
    """
    # Extract day numbers from the calendar area to determine how many days this month has
    calendar_rect = fitz.Rect(CALENDAR_AREA["x0"], CALENDAR_AREA["y0"], CALENDAR_AREA["x1"], CALENDAR_AREA["y1"])

    text_dict = page.get_text("dict", clip=calendar_rect)

    # Find all day numbers and their positions
    day_positions = []
    for block in text_dict["blocks"]:
        if "lines" not in block:
            continue

        for line in block["lines"]:
            for span in line["spans"]:
                text = span["text"].strip()
                # Look for day numbers (1-31)
                if text.isdigit() and 1 <= int(text) <= 31:
                    bbox = span["bbox"]
                    day_positions.append(
                        {
                            "day": int(text),
                            "y_top": bbox[1],  # Top coordinate of the day number
                            "y_bottom": bbox[3],  # Bottom coordinate of the day number
                            "y_center": (bbox[1] + bbox[3]) / 2,
                        }
                    )

    # Sort by day number to ensure correct order
    day_positions.sort(key=lambda x: x["day"])

    if not day_positions:
        raise ValueError("No day numbers found in the calendar area.")

    num_days = len(day_positions)
    logger.debug(f"Found {num_days} days in calendar")

    # Calculate day areas based on uniform row spacing
    # From the analysis, we know that days have consistent 23.2 spacing between centers
    # and the day number text is centered within each row

    # Calculate row boundaries based on day number positions and consistent spacing
    if not day_positions:
        return []

    # Calculate average spacing between consecutive day centers
    if len(day_positions) > 1:
        total_spacing = sum(
            day_positions[i]["y_center"] - day_positions[i - 1]["y_center"] for i in range(1, len(day_positions))
        )
        avg_spacing = total_spacing / (len(day_positions) - 1)
    else:
        avg_spacing = 23.2  # Default based on observed pattern

    # Calculate grid line positions - these are the horizontal separators between rows
    grid_lines = []

    # First grid line: half spacing above day 1 center
    first_day_center = day_positions[0]["y_center"]
    grid_lines.append(first_day_center - (avg_spacing / 2))

    # Grid lines between days: positioned halfway between consecutive day centers
    for i in range(len(day_positions) - 1):
        curr_center = day_positions[i]["y_center"]
        next_center = day_positions[i + 1]["y_center"]
        grid_line = (curr_center + next_center) / 2
        grid_lines.append(grid_line)

    # Last grid line: half spacing below last day center
    last_day_center = day_positions[-1]["y_center"]
    grid_lines.append(last_day_center + (avg_spacing / 2))

    # Create day areas spanning between consecutive grid lines
    areas = []
    for i in range(len(day_positions)):
        y_top = grid_lines[i]  # Start at grid line above day
        y_bottom = grid_lines[i + 1]  # End at grid line below day

        day_area = fitz.Rect(
            CALENDAR_AREA["x0"],  # Left edge of calendar
            y_top,  # Top of day area
            CALENDAR_AREA["x1"],  # Right edge of calendar
            y_bottom,  # Bottom of day area
        )
        areas.append(day_area)

        logger.debug(
            f"Day {day_positions[i]['day']:2d}: day_y_center={day_positions[i]['y_center']:6.1f}, area=({day_area.x0:.1f}, {day_area.y0:.1f}, {day_area.x1:.1f}, {day_area.y1:.1f}) height={y_bottom - y_top:.1f}"
        )

    logger.debug(f"Generated {len(areas)} day areas for {num_days} days")
    return areas
