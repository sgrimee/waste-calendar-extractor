#!/usr/bin/env python3
"""
Debug script to analyze PDF images/symbols for June 2025.
"""

import sys

sys.path.insert(0, "/Users/sgrimee/Documents/dev/commerce/waste-calendar/src")

import fitz


def debug_june_images():
    """Debug the June page for images and symbols."""
    pdf_path = "ressourcekalenner-nidderaanwen-web.pdf"
    doc = fitz.open(pdf_path)

    # Find June page (should be page 7 based on the logs)
    page = doc[6]  # 0-indexed, so page 7 is index 6

    print("=== IMAGES ON JUNE PAGE ===")
    image_list = page.get_images()
    print(f"Found {len(image_list)} images")

    for i, img in enumerate(image_list):
        print(f"Image {i}: {img}")

    print("\n=== DRAWINGS/SHAPES ON JUNE PAGE ===")
    drawings = page.get_drawings()
    print(f"Found {len(drawings)} drawings")

    for i, drawing in enumerate(drawings):
        print(f"Drawing {i}: {drawing}")

    print("\n=== EXTRACT WITH LAYOUT INFO ===")
    # Try to get text with more detailed layout information
    text_dict = page.get_text("dict")
    print("Blocks:")
    for block_idx, block in enumerate(text_dict["blocks"]):
        if "lines" in block:
            print(f"  Block {block_idx}: bbox={block['bbox']}")
            for line_idx, line in enumerate(block["lines"]):
                print(f"    Line {line_idx}: bbox={line['bbox']}")
                for span_idx, span in enumerate(line["spans"]):
                    if span["text"].strip():
                        print(f"      Span {span_idx}: '{span['text']}' bbox={span['bbox']} size={span['size']}")

    doc.close()


if __name__ == "__main__":
    debug_june_images()
