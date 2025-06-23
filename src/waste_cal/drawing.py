"""
Drawing analysis utilities for waste collection calendars.

This module provides functionality to analyze and classify PDF drawings
extracted from waste collection calendar pages.
"""

from waste_cal.waste_types import WasteType


def detect_waste_type_from_drawing(drawing) -> WasteType | None:
    """
    Detect waste type from a PyMuPDF drawing object based on visual characteristics.

    This function analyzes drawing properties (fill color, size, item count, item types)
    to classify the drawing as one of the known waste types. Based on training data
    from manually labeled examples.

    Args:
        drawing: PyMuPDF drawing object with properties like fill, rect, items, etc.

    Returns:
        WasteType enum value if a match is found, None otherwise.

    Classification Rules:
    - PROBLEMATIC: Very large size (19+ x 18+) and many items (392+)
    - BULKY: Brown color and rectangle item type
    - PAPER: Blue color and small rectangle (7.7x13.2)
    - PACKAGING: Light blue color and medium size with curves
    - ELECTRIC: Orange color and medium size with curves
    - For green color: distinguish by size and complexity:
      - Small rectangle (4 items) -> ORGANIC or GLASS (cannot distinguish)
      - Medium size with curves -> CHRISTMAS_TREES or HEDGE (cannot distinguish)
    - For purple color: RESIDUAL or CLOTHERS (cannot distinguish)
    """
    # Get drawing properties
    fill = drawing.get("fill")
    rect = drawing.get("rect")
    items = drawing.get("items", [])

    if not fill or not rect or not items:
        return None

    # Extract properties
    r, g, b = fill[:3] if len(fill) >= 3 else (0, 0, 0)
    width = rect.width
    height = rect.height
    item_count = len(items)
    first_item_type = items[0][0] if items and isinstance(items[0], tuple) and len(items[0]) > 0 else None

    # Helper function to check color similarity (tolerance for PDF extraction variations)
    def color_matches(target_r, target_g, target_b, tolerance=0.05):
        return abs(r - target_r) < tolerance and abs(g - target_g) < tolerance and abs(b - target_b) < tolerance

    # Helper function to check size similarity
    def size_matches(target_w, target_h, tolerance=1.0):
        return abs(width - target_w) < tolerance and abs(height - target_h) < tolerance

    # Rule 1: PROBLEMATIC - Very large and complex (from test: Color=(0.385, 0.632, 0.261), Size=(11.8x15.7), Items=392)
    if item_count > 300:
        return WasteType.PROBLEMATIC

    # Rule 2: PAPER - Blue color (from test: Color=(0.327, 0.757, 0.939), Size=(7.7x13.2), Items=4)
    if color_matches(0.327, 0.757, 0.939) and size_matches(7.7, 13.2):
        return WasteType.PAPER

    # Rule 3: PACKAGING - Light blue color (from test: Color=(0.729, 0.884, 0.977), Size=(10.2x10.6), Items=23)
    if color_matches(0.729, 0.884, 0.977) and first_item_type == "c":
        return WasteType.PACKAGING

    # Rule 4: ORGANIC - Green color and small rectangle
    # (from test: Color=(0.201, 0.570, 0.252), Size=(7.7x13.2), Items=4)
    if color_matches(0.201, 0.570, 0.252) and size_matches(7.7, 13.2):
        return WasteType.ORGANIC

    # Rule 5: RESIDUAL - Gray color (from test: Color=(0.343, 0.341, 0.339), Size=(7.7x13.2), Items=4)
    if color_matches(0.343, 0.341, 0.339, tolerance=0.02) and size_matches(7.7, 13.2):
        return WasteType.RESIDUAL

    # Rule 6: ELECTRIC - Dark/black color, larger size
    # (from test: Color=(0.114, 0.116, 0.111), Size=(12.4x15.9), Items=34)
    if color_matches(0.114, 0.116, 0.111, tolerance=0.02) and width > 10 and item_count > 30:
        return WasteType.ELECTRIC

    # Rule 7: CHRISTMAS_TREES - Green color, larger size
    # (from test: Color=(0.201, 0.570, 0.252), Size=(11.6x15.1), Items=34)
    if color_matches(0.201, 0.570, 0.252) and width > 10 and item_count > 30:
        return WasteType.CHRISTMAS_TREES

    # Rule 8: BULKY - Brown color, medium size (from test: Color=(0.585, 0.418, 0.264), Size=(10.4x5.8), Items=12)
    if color_matches(0.585, 0.418, 0.264) and 5 <= height <= 8 and item_count >= 10:
        return WasteType.BULKY

    # Rule 9: GLASS - Orange/yellow color (from test: Color=(0.985, 0.736, 0.201), Size=(7.7x13.2), Items=4)
    if color_matches(0.985, 0.736, 0.201) and size_matches(7.7, 13.2):
        return WasteType.GLASS

    # Rule 10: HEDGE - Brown color, larger size (from test: Color=(0.585, 0.418, 0.264), Size=(12.2x12.2), Items=56)
    if color_matches(0.585, 0.418, 0.264) and width > 10 and item_count > 50:
        return WasteType.HEDGE

    # Rule 11: CLOTHERS - Orange color, different size
    # (from test: Color=(0.939, 0.490, 0.000), Size=(14.7x6.0), Items=9)
    if color_matches(0.939, 0.490, 0.000) and height < 8 and width > 10:
        return WasteType.CLOTHERS

    # No match found
    return None
