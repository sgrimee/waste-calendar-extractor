#!/usr/bin/env python3
"""
Analyze and classify waste collection symbols by examining their properties.
"""

import sys

sys.path.append("src")

import fitz


def analyze_symbol_types(pdf_path: str):
    """Analyze the different types of waste collection symbols."""
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

    # Get all drawings
    drawings = june_page.get_drawings()

    # Group symbols by item count to identify patterns
    symbol_groups: dict[int, list[dict]] = {}

    for i, drawing in enumerate(drawings):
        draw_rect = drawing["rect"]
        # Focus on waste collection symbols (right side, reasonable size)
        if draw_rect[0] > 200 and (draw_rect[2] - draw_rect[0]) > 5 and (draw_rect[3] - draw_rect[1]) > 5:
            item_count = len(drawing["items"])
            if item_count not in symbol_groups:
                symbol_groups[item_count] = []

            symbol_groups[item_count].append(
                {
                    "index": i,
                    "drawing": drawing,
                    "rect": draw_rect,
                    "center_x": (draw_rect[0] + draw_rect[2]) / 2,
                    "center_y": (draw_rect[1] + draw_rect[3]) / 2,
                    "width": draw_rect[2] - draw_rect[0],
                    "height": draw_rect[3] - draw_rect[1],
                    "items": drawing["items"],
                }
            )

    print("Symbol types by item count:")
    print("=" * 50)

    for item_count in sorted(symbol_groups.keys()):
        symbols = symbol_groups[item_count]
        print(f"\n{item_count} items: {len(symbols)} symbols")

        # Show details for first few symbols of each type
        for symbol in symbols[:3]:
            print(
                f"  Symbol {symbol['index']}: size=({symbol['width']:.1f}x{symbol['height']:.1f}), "
                f"center=({symbol['center_x']:.1f}, {symbol['center_y']:.1f})"
            )

            # Show first few drawing items
            for j, item in enumerate(symbol["items"][:5]):
                print(f"    Item {j}: {item}")
            if len(symbol["items"]) > 5:
                print(f"    ... and {len(symbol['items']) - 5} more items")

        if len(symbols) > 3:
            print(f"  ... and {len(symbols) - 3} more symbols with {item_count} items")

    # Let's also analyze specific known symbols to understand their structure
    print("\n" + "=" * 60)
    print("DETAILED ANALYSIS OF SPECIFIC SYMBOLS")
    print("=" * 60)

    # Look at some interesting symbols from our mapping
    interesting_symbols = [
        46,  # Date 1-3 (4 items)
        217,  # Date 2 (56 items) - complex symbol
        196,  # Date 4 (34 items)
        206,  # Date 5 (392 items) - very complex
        179,  # Date 10 (41 items)
    ]

    for symbol_idx in interesting_symbols:
        if symbol_idx < len(drawings):
            drawing = drawings[symbol_idx]
            print(f"\nSymbol {symbol_idx} ({len(drawing['items'])} items):")
            print(f"  Rect: {drawing['rect']}")

            # Categorize items by type
            item_types = {}
            for item in drawing["items"]:
                item_type = item[0]  # First element is the drawing command
                if item_type not in item_types:
                    item_types[item_type] = 0
                item_types[item_type] += 1

            print(f"  Item types: {item_types}")

            # Show some items
            for i, item in enumerate(drawing["items"][:8]):
                print(f"    {i}: {item}")
            if len(drawing["items"]) > 8:
                print(f"    ... and {len(drawing['items']) - 8} more")

    doc.close()


if __name__ == "__main__":
    analyze_symbol_types("ressourcekalenner-nidderaanwen-web.pdf")
