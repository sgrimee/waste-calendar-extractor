#!/usr/bin/env python3
"""
Debug script to analyze PDF structure for June 2025.
"""

import sys

sys.path.insert(0, "/Users/sgrimee/Documents/dev/commerce/waste-calendar/src")

import fitz

from waste_calendar_extractor.pdf_extractor import extract_text_elements, group_elements_by_rows


def debug_june_page():
    """Debug the June page specifically."""
    pdf_path = "ressourcekalenner-nidderaanwen-web.pdf"
    doc = fitz.open(pdf_path)

    # Find June page (should be page 7 based on the logs)
    page = doc[6]  # 0-indexed, so page 7 is index 6

    print("=== RAW TEXT FROM JUNE PAGE ===")
    text = page.get_text()
    print(text)
    print("\n=== POSITIONED TEXT ELEMENTS ===")

    elements = extract_text_elements(page)
    for i, elem in enumerate(elements):
        print(f"{i:3}: x={elem['x']:6.1f} y={elem['y']:6.1f} text='{elem['text']}'")

    print("\n=== GROUPED BY ROWS ===")
    rows = group_elements_by_rows(elements)
    for i, row in enumerate(rows):
        texts = [elem["text"] for elem in row]
        y_coords = [elem["y"] for elem in row]
        print(f"Row {i:2}: y~{y_coords[0]:6.1f} -> {' | '.join(texts)}")

    doc.close()


if __name__ == "__main__":
    debug_june_page()
