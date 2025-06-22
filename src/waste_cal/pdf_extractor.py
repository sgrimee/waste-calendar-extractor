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
                            "y": bbox[1],  # Top coordinate of the day number
                        }
                    )

    # Sort by day number to ensure correct order
    day_positions.sort(key=lambda x: x["day"])

    if not day_positions:
        raise ValueError("No day numbers found in the calendar area.")

    num_days = len(day_positions)
    logger.debug(f"Found {num_days} days in calendar")

    # Calculate row height based on day number positions
    # The calendar has consistent vertical spacing between days
    total_height = day_positions[-1]["y"] - day_positions[0]["y"]
    row_height = total_height / (num_days - 1)

    # Create rectangular areas for each day
    areas = []
    for i, day_pos in enumerate(day_positions):
        # Each day gets a horizontal strip across the calendar width
        # The height extends from halfway above to halfway below the day number
        y_top = day_pos["y"] - (row_height / 2)
        y_bottom = day_pos["y"] + (row_height / 2)

        # For the first and last days, extend to the calendar boundaries
        if i == 0:
            y_top = CALENDAR_AREA["y0"]
        if i == num_days - 1:
            y_bottom = CALENDAR_AREA["y1"]

        day_area = fitz.Rect(
            CALENDAR_AREA["x0"],  # Left edge of calendar
            y_top,  # Top of day area
            CALENDAR_AREA["x1"],  # Right edge of calendar
            y_bottom,  # Bottom of day area
        )
        areas.append(day_area)

        logger.debug(
            f"Day {day_pos['day']:2d}: y={day_pos['y']:6.1f}, area=({day_area.x0:.1f}, {day_area.y0:.1f}, {day_area.x1:.1f}, {day_area.y1:.1f})"
        )

    logger.debug(f"Generated {len(areas)} day areas for {num_days} days")
    return areas
