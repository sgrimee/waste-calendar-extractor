#!/usr/bin/env python3
"""
Create a spatial map of waste collection symbols to calendar dates.
"""

import sys

sys.path.append("src")

import fitz


def create_waste_calendar_map(pdf_path: str):
    """Create a spatial mapping between dates and waste collection symbols."""
    doc = fitz.open(pdf_path)

    # Find June page
    june_page = None
    for page_num in range(len(doc)):
        page = doc[page_num]
        page_text = page.get_text()  # type: ignore
        if "JUNI" in page_text:
            june_page = page
            break

    if not june_page:
        print("June page not found!")
        return

    # Extract date positions (left column)
    text_dict = june_page.get_text("dict")  # type: ignore
    date_positions = []

    for block in text_dict["blocks"]:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if text.isdigit() and 1 <= int(text) <= 31:
                        bbox = span["bbox"]
                        date_positions.append(
                            {
                                "date": int(text),
                                "bbox": bbox,
                                "y": bbox[1],  # top y coordinate
                                "center_y": (bbox[1] + bbox[3]) / 2,
                            }
                        )

    # Sort dates by Y position
    date_positions.sort(key=lambda x: x["y"])

    # Get all drawings (potential waste collection symbols)
    drawings = june_page.get_drawings()

    # Filter drawings to find those that look like waste collection symbols
    # Based on the analysis, these are in the right side of the calendar
    symbol_drawings = []
    for i, drawing in enumerate(drawings):
        draw_rect = drawing["rect"]
        # Look for drawings in the right side of the calendar (x > 200)
        # and that have reasonable size (not just calendar grid lines)
        if (
            draw_rect[0] > 200
            and (draw_rect[2] - draw_rect[0]) > 5  # width > 5
            and (draw_rect[3] - draw_rect[1]) > 5
        ):  # height > 5
            symbol_drawings.append(
                {
                    "index": i,
                    "drawing": drawing,
                    "rect": draw_rect,
                    "center_x": (draw_rect[0] + draw_rect[2]) / 2,
                    "center_y": (draw_rect[1] + draw_rect[3]) / 2,
                    "items_count": len(drawing["items"]),
                }
            )

    print(f"Found {len(date_positions)} dates and {len(symbol_drawings)} potential waste symbols")
    print("\nDates and their Y positions:")
    for date_info in date_positions:
        print(f"  Date {date_info['date']:2d}: Y={date_info['center_y']:.1f}")

    print("\nPotential waste collection symbols:")
    for symbol in symbol_drawings:
        print(
            f"  Drawing {symbol['index']:3d}: center=({symbol['center_x']:.1f}, {symbol['center_y']:.1f}), "
            f"size=({symbol['rect'][2] - symbol['rect'][0]:.1f}x{symbol['rect'][3] - symbol['rect'][1]:.1f}), "
            f"items={symbol['items_count']}"
        )

    # Create spatial mapping between dates and symbols
    print("\n" + "=" * 60)
    print("SPATIAL MAPPING")
    print("=" * 60)

    mappings = []
    tolerance = 15  # Y-coordinate tolerance for matching

    for date_info in date_positions:
        nearby_symbols = []
        for symbol in symbol_drawings:
            y_distance = abs(date_info["center_y"] - symbol["center_y"])
            if y_distance <= tolerance:
                nearby_symbols.append((symbol, y_distance))

        # Sort by distance
        nearby_symbols.sort(key=lambda x: x[1])

        if nearby_symbols:
            print(f"\nDate {date_info['date']} (Y={date_info['center_y']:.1f}):")
            for symbol, distance in nearby_symbols:
                print(
                    f"  → Drawing {symbol['index']} at Y={symbol['center_y']:.1f} "
                    f"(distance={distance:.1f}px, items={symbol['items_count']})"
                )

                mappings.append(
                    {
                        "date": date_info["date"],
                        "drawing_index": symbol["index"],
                        "distance": distance,
                        "items_count": symbol["items_count"],
                    }
                )

    print("\n" + "=" * 60)
    print("SUMMARY MAPPING")
    print("=" * 60)

    # Group by date for summary
    date_mappings: dict[int, list[dict]] = {}
    for mapping in mappings:
        date = mapping["date"]
        if date not in date_mappings:
            date_mappings[date] = []
        date_mappings[date].append(mapping)

    for date in sorted(date_mappings.keys()):
        symbols = date_mappings[date]
        print(f"Date {date:2d}: {len(symbols)} symbols")
        for symbol in symbols:
            print(f"  Drawing {symbol['drawing_index']} ({symbol['items_count']} items)")

    doc.close()
    return date_mappings


if __name__ == "__main__":
    create_waste_calendar_map("ressourcekalenner-nidderaanwen-web.pdf")
