#!/usr/bin/env python3
"""
ADYS PDF extractor for trash can cleaning schedules.

Extracts cleaning dates from ADYS trash bin cleaning calendars.
The calendar displays 12 months with days 01-31 in a grid format,
with green squares indicating cleaning dates for organic waste bins.

Usage:
    from waste_cal.adys_extractor import extract_adys_dates

    dates = extract_adys_dates("path/to/adys.pdf")
    for date in dates:
        print(date)  # Output: 2026-03-03, 2026-06-09, etc.
"""

import logging
from typing import Optional

import fitz


def extract_adys_dates(pdf_path: str, year: Optional[int] = None) -> list[str]:
    """
    Extract cleaning dates from an ADYS PDF calendar.

    The extraction works by:
    1. Finding green-colored rectangles (RGB: 0.0, 0.5, 0.25)
    2. Extracting day numbers and month names with their positions
    3. Mapping each green rectangle to the nearest day and month
    4. Converting to ISO format dates (YYYY-MM-DD)

    Args:
        pdf_path (str): Path to the ADYS PDF calendar file.
        year (int, optional): Year to use in output dates. If None, extracts from PDF text.

    Returns:
        list[str]: List of dates in ISO format (YYYY-MM-DD), sorted chronologically.

    Raises:
        ValueError: If the PDF cannot be read or parsed.
        RuntimeError: If no cleaning dates or calendar structure could be found.

    Example:
        >>> dates = extract_adys_dates("pdf/adys.pdf")
        >>> print(dates)
        ['2026-03-03', '2026-06-09', '2026-09-01', '2026-12-08']
    """
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise ValueError(f"Could not read PDF file: {pdf_path}") from e

    if len(doc) < 1:
        raise ValueError("PDF contains no pages")

    page = doc[0]

    # Extract year from PDF if not provided
    if year is None:
        year = _extract_year_from_pdf(page)
        if year is None:
            raise RuntimeError("Could not extract year from PDF. Please provide year parameter.")

    # Find green rectangles (cleaning date markers)
    green_marks = _find_green_marks(page)
    if not green_marks:
        raise RuntimeError("No green markers found in PDF. This may not be a valid ADYS calendar.")

    logging.debug(f"Found {len(green_marks)} green markers")

    # Extract day and month positions
    day_positions = _extract_day_positions(page)
    if not day_positions:
        raise RuntimeError("Could not extract day numbers from calendar")

    month_positions = _extract_month_positions(page)
    if not month_positions:
        raise RuntimeError("Could not extract month names from calendar")

    logging.debug(f"Found {len(day_positions)} days and {len(month_positions)} months")

    # Map green marks to dates
    dates = _map_marks_to_dates(green_marks, day_positions, month_positions, year)

    return sorted(dates)


def _extract_year_from_pdf(page) -> Optional[int]:
    """Extract the year from the PDF text."""
    text = page.get_text()

    # Look for year in common patterns like "année 2026", "year 2026", etc.
    import re

    match = re.search(r"(?:année|year|annee)\s*(\d{4})", text, re.IGNORECASE)
    if match:
        return int(match.group(1))

    # Fallback: look for any 4-digit year that looks reasonable (2020-2050)
    match = re.search(r"\b(20[2-4]\d)\b", text)
    if match:
        return int(match.group(1))

    return None


def _find_green_marks(page) -> list[tuple[float, float]]:
    """
    Find all green-colored rectangles in the page.

    Green markers have RGB color (0.0, 0.5, 0.25) in the ADYS calendar.

    Returns:
        List of (x, y) tuples representing center coordinates of green marks.
    """
    green_marks = []
    drawings = page.get_drawings()

    for drawing in drawings:
        fill = drawing.get("fill")

        # Check if fill is green
        if not fill or not isinstance(fill, tuple) or len(fill) < 3:
            continue

        r, g, b = fill[0], fill[1], fill[2]

        # Green color check: match ADYS green (0.0, 0.5, 0.25) with small tolerance
        if abs(r - 0.0) < 0.1 and abs(g - 0.5) < 0.1 and abs(b - 0.25) < 0.1:
            rect = drawing.get("rect")
            if rect:
                center_x = (rect.x0 + rect.x1) / 2
                center_y = (rect.y0 + rect.y1) / 2
                green_marks.append((center_x, center_y))

    return green_marks


def _extract_day_positions(page) -> dict[int, dict[str, float]]:
    """
    Extract day numbers (1-31) and their positions from the left column.

    Returns:
        Dict mapping day number -> {"x": x_coord, "y": y_coord}
    """
    text_dict = page.get_text("dict")
    day_positions = {}

    for block in text_dict["blocks"]:
        if "lines" not in block:
            continue

        for line in block["lines"]:
            for span in line["spans"]:
                text = span["text"].strip()

                # Look for 2-digit day numbers
                if text.isdigit() and len(text) == 2:
                    day_num = int(text)
                    if 1 <= day_num <= 31:
                        bbox = span["bbox"]
                        x = (bbox[0] + bbox[2]) / 2
                        y = (bbox[1] + bbox[3]) / 2

                        # Only keep the leftmost occurrence (the day column)
                        if day_num not in day_positions or x < day_positions[day_num]["x"]:
                            day_positions[day_num] = {"x": x, "y": y}

    return day_positions


def _extract_month_positions(page) -> dict[str, float]:
    """
    Extract month names and their x-coordinates from the top row.

    Returns:
        Dict mapping month name (lowercase) -> x_coord
    """
    months = [
        "janvier",
        "février",
        "mars",
        "avril",
        "mai",
        "juin",
        "juillet",
        "août",
        "septembre",
        "octobre",
        "novembre",
        "décembre",
    ]

    text_dict = page.get_text("dict")
    month_positions = {}

    for block in text_dict["blocks"]:
        if "lines" not in block:
            continue

        for line in block["lines"]:
            for span in line["spans"]:
                text = span["text"].strip().lower()

                if text in months:
                    bbox = span["bbox"]
                    x = (bbox[0] + bbox[2]) / 2

                    # Only keep the topmost occurrence
                    if (
                        text not in month_positions
                        or bbox[1] < page.get_text("dict")["blocks"][0]["lines"][0]["spans"][0]["bbox"][1]
                    ):
                        month_positions[text] = x

    return month_positions


def _map_marks_to_dates(
    green_marks: list[tuple[float, float]],
    day_positions: dict[int, dict[str, float]],
    month_positions: dict[str, float],
    year: int,
) -> list[str]:
    """
    Map green mark coordinates to calendar dates.

    For each green mark, find the closest day (by y-coordinate) and
    closest month (by x-coordinate), then convert to ISO format date.

    Filters out legend marks by requiring marks to be close to actual grid positions.
    """
    month_map = {
        "janvier": 1,
        "février": 2,
        "mars": 3,
        "avril": 4,
        "mai": 5,
        "juin": 6,
        "juillet": 7,
        "août": 8,
        "septembre": 9,
        "octobre": 10,
        "novembre": 11,
        "décembre": 12,
    }

    dates = []

    # First pass: collect all candidates
    candidates = []

    for mark_x, mark_y in green_marks:
        # Find closest day by y-coordinate
        closest_day = None
        min_y_dist = float("inf")

        for day_num, pos in day_positions.items():
            dist = abs(mark_y - pos["y"])
            if dist < min_y_dist:
                min_y_dist = dist
                closest_day = day_num

        # Find closest month by x-coordinate
        closest_month = None
        min_x_dist = float("inf")

        for month_name, month_x in month_positions.items():
            dist = abs(mark_x - month_x)
            if dist < min_x_dist:
                min_x_dist = dist
                closest_month = month_name

        if closest_day is not None and closest_month is not None:
            candidates.append(
                {
                    "x": mark_x,
                    "y": mark_y,
                    "day": closest_day,
                    "month": closest_month,
                    "x_dist": min_x_dist,
                    "y_dist": min_y_dist,
                }
            )

    # Filter candidates: legend marks are outliers
    # Keep marks that are very close to grid intersections
    valid_candidates = [c for c in candidates if c["x_dist"] < 10 and c["y_dist"] < 10]

    # If we have very few valid candidates, relax constraints slightly
    if len(valid_candidates) < 3 and len(candidates) > 0:
        valid_candidates = [c for c in candidates if c["x_dist"] < 20 and c["y_dist"] < 15]

    for candidate in valid_candidates:
        month_num = month_map[candidate["month"]]
        iso_date = f"{year:04d}-{month_num:02d}-{candidate['day']:02d}"
        dates.append(iso_date)
        logging.debug(
            f"Mark at ({candidate['x']:.0f}, {candidate['y']:.0f}) -> "
            f"{candidate['month']} {candidate['day']} "
            f"(distances: x={candidate['x_dist']:.1f}, y={candidate['y_dist']:.1f})"
        )

    # Log rejected candidates
    for candidate in candidates:
        if candidate not in valid_candidates:
            logging.debug(
                f"Rejected mark at ({candidate['x']:.0f}, {candidate['y']:.0f}) "
                f"(x_dist={candidate['x_dist']:.1f}, y_dist={candidate['y_dist']:.1f}) - "
                f"likely legend or noise"
            )

    return dates


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python adys_extractor.py <pdf_path> [year]")
        print("\nExample:")
        print("  python adys_extractor.py pdf/adys.pdf")
        print("  python adys_extractor.py pdf/adys.pdf 2026")
        sys.exit(1)

    pdf_path = sys.argv[1]
    year = int(sys.argv[2]) if len(sys.argv) > 2 else None

    logging.basicConfig(level=logging.INFO)

    try:
        dates = extract_adys_dates(pdf_path, year=year)
        print(f"Found {len(dates)} cleaning dates:")
        for date in dates:
            print(f"  {date}")
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
