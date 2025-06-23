"""Research utilities for analyzing PDF drawings and waste type mapping."""

import os
from waste_cal.month import Month
from waste_cal.pdf_extractor import (
    load_pdf,
    areas_per_day,
    get_all_drawings,
    is_drawing_in_box,
    render_drawing_to_image,
    drawing_info
)


def extract_month_drawings(pdf_path: str, month_name: str, output_dir: str = "debug") -> None:
    """
    Extract all drawings from each day of a specified month and save as images.

    Args:
        pdf_path: Path to the PDF file.
        month_name: Name of the month to process.
        output_dir: Directory to save the drawing images.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Get month enum and page index
    try:
        month = Month(month_name.lower())
    except ValueError:
        raise ValueError(f"Invalid month name: {month_name}. Valid months: {', '.join([m.value for m in Month])}")

    page_index = month.page_index()

    # Open PDF and get the page
    doc = load_pdf(pdf_path)
    if page_index >= len(doc):
        raise ValueError(f"Page {page_index} not found in PDF (only {len(doc)} pages)")

    page = doc[page_index]

    # Get day areas for the month
    day_areas = areas_per_day(page)

    print(f"Processing {month_name.capitalize()} (page {page_index}) - found {len(day_areas)} days")

    total_drawings = 0

    for day_num, day_area in enumerate(day_areas, 1):
        # Get all drawings on the page
        all_drawings = get_all_drawings(page)
        # Filter drawings that are in this day's area
        day_drawings = [drawing for drawing in all_drawings if is_drawing_in_box(drawing, day_area)]

        print(f"\nDay {day_num}: {len(day_drawings)} drawings")

        for drawing_num, drawing in enumerate(day_drawings):
            # Create filename: month_day_drawing.png
            filename = f"{month_name.lower()}_{day_num:02d}_{drawing_num:03d}.png"
            filepath = os.path.join(output_dir, filename)

            # Render drawing to image
            try:
                render_drawing_to_image(page, drawing, filepath)
                print(f"  {filename}: {drawing_info(drawing).split(chr(10))[0]}")  # First line only
                total_drawings += 1
            except Exception as e:
                print(f"  Error rendering {filename}: {e}")

    print(f"\nTotal drawings extracted: {total_drawings}")
    doc.close()