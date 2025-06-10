#!/usr/bin/env python3
"""
Analyze the spatial layout of the PDF calendar to understand
how waste collection icons relate to date numbers.
"""

import sys

sys.path.append("src")

import fitz


def analyze_june_page_layout(pdf_path: str):
    """Analyze the June page layout to understand spatial relationships."""
    doc = fitz.open(pdf_path)

    # Find June page
    june_page = None
    june_page_num = None

    for page_num in range(len(doc)):
        page = doc[page_num]
        page_text = page.get_text()  # type: ignore
        if "JUNI" in page_text:
            june_page = page
            june_page_num = page_num
            break

    if not june_page:
        print("June page not found!")
        return

    print(f"Analyzing June page (page {june_page_num + 1 if june_page_num is not None else 'unknown'})")
    print("=" * 50)

    # Extract text elements with positions
    text_dict = june_page.get_text("dict")  # type: ignore
    date_numbers = []
    other_text = []

    for block in text_dict["blocks"]:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if text:
                        bbox = span["bbox"]
                        x, y, x2, y2 = bbox

                        # Check if it's a date number (1-31)
                        if text.isdigit() and 1 <= int(text) <= 31:
                            date_numbers.append(
                                {
                                    "text": text,
                                    "date": int(text),
                                    "bbox": bbox,
                                    "x": x,
                                    "y": y,
                                    "center_x": (x + x2) / 2,
                                    "center_y": (y + y2) / 2,
                                }
                            )
                        else:
                            other_text.append(
                                {
                                    "text": text,
                                    "bbox": bbox,
                                    "x": x,
                                    "y": y,
                                    "center_x": (x + x2) / 2,
                                    "center_y": (y + y2) / 2,
                                }
                            )

    # Sort dates by position for better understanding
    date_numbers.sort(key=lambda x: (x["y"], x["x"]))

    print(f"Found {len(date_numbers)} date numbers:")
    for date_info in date_numbers:
        print(
            f"  Date {date_info['date']:2d}: bbox={date_info['bbox']}, "
            f"center=({date_info['center_x']:.1f}, {date_info['center_y']:.1f})"
        )

    print(f"\nFound {len(other_text)} other text elements:")
    for text_info in other_text[:10]:  # Show first 10
        print(
            f"  '{text_info['text']}': bbox={text_info['bbox']}, "
            f"center=({text_info['center_x']:.1f}, {text_info['center_y']:.1f})"
        )
    if len(other_text) > 10:
        print(f"  ... and {len(other_text) - 10} more")

    # Get drawing objects (icons/symbols)
    drawings = june_page.get_drawings()
    print(f"\nFound {len(drawings)} drawing objects:")
    for i, drawing in enumerate(drawings):
        print(f"  Drawing {i}: bbox={drawing['rect']}, items={len(drawing['items'])}")
        if i < 5:  # Show details for first 5
            for j, item in enumerate(drawing["items"][:3]):  # First 3 items
                print(f"    Item {j}: {item}")

    # Get images
    image_list = june_page.get_images()
    print(f"\nFound {len(image_list)} images:")
    for i, img in enumerate(image_list):
        if i < 5:  # Show first 5
            print(f"  Image {i}: {img}")

    # Try to find spatial relationships
    print("\n" + "=" * 50)
    print("SPATIAL ANALYSIS")
    print("=" * 50)

    # For each date, find nearby text and drawings
    proximity_threshold = 50  # pixels

    for date_info in date_numbers:
        print(f"\nDate {date_info['date']} at ({date_info['center_x']:.1f}, {date_info['center_y']:.1f}):")

        # Find nearby text
        nearby_text = []
        for text_info in other_text:
            distance = (
                (date_info["center_x"] - text_info["center_x"]) ** 2
                + (date_info["center_y"] - text_info["center_y"]) ** 2
            ) ** 0.5
            if distance <= proximity_threshold:
                nearby_text.append((text_info, distance))

        nearby_text.sort(key=lambda x: x[1])  # Sort by distance

        if nearby_text:
            print(f"  Nearby text (within {proximity_threshold}px):")
            for text_info, distance in nearby_text[:3]:  # Show closest 3
                print(f"    '{text_info['text']}' at distance {distance:.1f}px")

        # Find nearby drawings
        nearby_drawings = []
        for i, drawing in enumerate(drawings):
            draw_rect = drawing["rect"]
            draw_center_x = (draw_rect[0] + draw_rect[2]) / 2
            draw_center_y = (draw_rect[1] + draw_rect[3]) / 2

            distance = (
                (date_info["center_x"] - draw_center_x) ** 2 + (date_info["center_y"] - draw_center_y) ** 2
            ) ** 0.5
            if distance <= proximity_threshold:
                nearby_drawings.append((i, drawing, distance))

        nearby_drawings.sort(key=lambda x: x[2])  # Sort by distance

        if nearby_drawings:
            print(f"  Nearby drawings (within {proximity_threshold}px):")
            for i, drawing, distance in nearby_drawings[:2]:  # Show closest 2
                print(f"    Drawing {i} at distance {distance:.1f}px, bbox={drawing['rect']}")

    doc.close()


if __name__ == "__main__":
    analyze_june_page_layout("ressourcekalenner-nidderaanwen-web.pdf")
