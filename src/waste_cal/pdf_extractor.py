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
        raise ValueError(f"Could not read PDF file: {file_path}") from e


def _extract_day_positions(page) -> list[dict[str, int | float]]:
    """
    Extract day numbers and their positions from the calendar area.

    Args:
        page: The PDF page containing the calendar.

    Returns:
        List of dictionaries containing day number and position information.
    """
    calendar_rect = fitz.Rect(CALENDAR_AREA["x0"], CALENDAR_AREA["y0"], CALENDAR_AREA["x1"], CALENDAR_AREA["y1"])
    text_dict = page.get_text("dict", clip=calendar_rect)

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
                            "y_top": bbox[1],
                            "y_bottom": bbox[3],
                            "y_center": (bbox[1] + bbox[3]) / 2,
                        }
                    )

    # Sort by day number to ensure correct order
    day_positions.sort(key=lambda x: x["day"])

    if not day_positions:
        raise ValueError("No day numbers found in the calendar area.")

    return day_positions


def _calculate_day_spacing(day_positions: list[dict[str, int | float]]) -> float:
    """
    Calculate the average spacing between consecutive day centers.

    Args:
        day_positions: List of day position dictionaries.

    Returns:
        Average spacing between day centers in pixels.
    """
    if len(day_positions) > 1:
        total_spacing = sum(
            day_positions[i]["y_center"] - day_positions[i - 1]["y_center"] for i in range(1, len(day_positions))
        )
        return total_spacing / (len(day_positions) - 1)
    else:
        return 23.2  # Default based on observed pattern


def _calculate_grid_lines(day_positions: list[dict[str, int | float]], spacing: float) -> list[float]:
    """
    Calculate horizontal grid line positions that separate day rows.

    Args:
        day_positions: List of day position dictionaries.
        spacing: Average spacing between day centers.

    Returns:
        List of y-coordinates for grid lines.
    """
    grid_lines = []

    # First grid line: half spacing above day 1 center
    first_day_center = day_positions[0]["y_center"]
    grid_lines.append(first_day_center - (spacing / 2))

    # Grid lines between days: positioned halfway between consecutive day centers
    for i in range(len(day_positions) - 1):
        curr_center = day_positions[i]["y_center"]
        next_center = day_positions[i + 1]["y_center"]
        grid_line = (curr_center + next_center) / 2
        grid_lines.append(grid_line)

    # Last grid line: half spacing below last day center
    last_day_center = day_positions[-1]["y_center"]
    grid_lines.append(last_day_center + (spacing / 2))

    return grid_lines


def _generate_day_areas(day_positions: list[dict[str, int | float]], grid_lines: list[float]) -> list[fitz.Rect]:
    """
    Generate rectangular areas for each day based on grid line positions.

    Args:
        day_positions: List of day position dictionaries.
        grid_lines: List of y-coordinates for grid lines.

    Returns:
        List of rectangular areas for each day.
    """
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
            f"""Day {day_positions[i]["day"]:2d}: day_y_center={day_positions[i]["y_center"]:6.1f},
            area=({day_area.x0:.1f}, {day_area.y0:.1f}, {day_area.x1:.1f}, {day_area.y1:.1f})
            height={y_bottom - y_top:.1f}"""
        )

    return areas


def areas_per_day(page) -> list[fitz.Rect]:
    """
    Get the rectangular areas for each day in the calendar.

    Args:
        page: The PDF page containing the calendar for a specific month.

    Returns:
        List of rectangles representing each day's area.
    """
    day_positions = _extract_day_positions(page)
    num_days = len(day_positions)
    logger.debug(f"Found {num_days} days in calendar")

    spacing = _calculate_day_spacing(day_positions)
    grid_lines = _calculate_grid_lines(day_positions, spacing)
    areas = _generate_day_areas(day_positions, grid_lines)

    logger.debug(f"Generated {len(areas)} day areas for {num_days} days")
    return areas


def is_drawing_in_box(drawing, box: fitz.Rect) -> bool:
    """
    Check if a drawing is completely contained within a specified rectangular area.

    Args:
        drawing: Native fitz drawing object.
        box: The rectangular area to check against (fitz.Rect).

    Returns:
        True if the drawing is completely contained in the box, False otherwise.
    """
    drawing_rect = drawing.get("rect")
    if not drawing_rect:
        return False

    return box.contains(drawing_rect)


def drawing_info(drawing) -> str:
    """
    Get detailed information about a drawing object as a string.

    Args:
        drawing: Native fitz drawing object.

    Returns:
        String containing detailed drawing information.
    """
    lines = []
    lines.append(f"Type: {drawing.get('type', 'unknown')}")

    rect = drawing.get("rect")
    if rect:
        lines.append(f"Position: ({rect.x0:.1f}, {rect.y0:.1f}) to ({rect.x1:.1f}, {rect.y1:.1f})")
        lines.append(f"Size: {rect.width:.1f} x {rect.height:.1f}")

    lines.append(f"Fill: {drawing.get('fill', 'None')}")
    lines.append(f"Stroke: {drawing.get('stroke', 'None')}")
    lines.append(f"Width: {drawing.get('width', 0)}")

    items = drawing.get("items", [])
    lines.append(f"Items count: {len(items)}")

    for i, item in enumerate(items):
        # Items are tuples, not dictionaries
        if isinstance(item, tuple) and len(item) > 0:
            item_type = item[0] if len(item) > 0 else 'unknown'
            lines.append(f"  Item {i}: {item_type} (tuple with {len(item)} elements)")
            lines.append(f"    Content: {item}")
        else:
            # Handle case where item might be a dictionary (for compatibility)
            item_type = item.get('type', 'unknown') if hasattr(item, 'get') else str(type(item))
            lines.append(f"  Item {i}: {item_type}")
            if hasattr(item, 'get') and "p" in item:  # Path data
                points = item["p"]
                lines.append(f"    Points: {len(points)} coordinates")
                if points:
                    lines.append(f"    First point: ({points[0][0]:.1f}, {points[0][1]:.1f})")
                    if len(points) > 1:
                        lines.append(f"    Last point: ({points[-1][0]:.1f}, {points[-1][1]:.1f})")

    return "\n".join(lines)


def render_drawing_to_image(page, drawing, output_path: str, scale: float = 4.0) -> None:
    """
    Render a drawing to a PNG image file for visual inspection.

    Args:
        page: The PDF page containing the drawing.
        drawing: Native fitz drawing object.
        output_path: Path where to save the PNG image.
        scale: Scaling factor for the output image (higher = larger/clearer).
    """
    rect = drawing.get("rect")
    if not rect:
        print("Warning: Drawing has no rect information")
        return

    # Create a matrix for scaling
    matrix = fitz.Matrix(scale, scale)

    # Render the cropped area to a pixmap
    pixmap = page.get_pixmap(matrix=matrix, clip=rect)

    # Save as PNG
    pixmap.save(output_path)
    pixmap = None  # Free memory

    print(f"Drawing rendered to: {output_path}")
    print(f"Image size: {pixmap.width if pixmap else 'unknown'} x {pixmap.height if pixmap else 'unknown'}")



