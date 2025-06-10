#!/usr/bin/env python3
"""
Analyze the complete June 2025 page to understand full layout and all symbols.
"""
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import fitz
from waste_calendar_extractor.pdf_extractor import (
    extract_date_positions,
    classify_waste_symbol
)

def analyze_full_june_page():
    """Analyze the complete June 2025 page."""
    pdf_path = "pdf/2025.pdf"
    
    # Open PDF and find June page
    doc = fitz.open(pdf_path)
    june_page = None
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        if "JUNI" in text:
            june_page = page
            print(f"Found June page: {page_num}")
            break
    
    if not june_page:
        print("Could not find June page!")
        return
    
    # Get page dimensions
    page_rect = june_page.rect
    print(f"Page dimensions: {page_rect}")
    
    # Extract date positions for full month
    date_positions = extract_date_positions(june_page)
    print(f"\nDate positions found for {len(date_positions)} days:")
    for day in sorted(date_positions.keys()):
        print(f"  Day {day}: y={date_positions[day]:.1f}")
    
    # Get all drawings and analyze the full page
    drawings = june_page.get_drawings()
    print(f"\nTotal drawings: {len(drawings)}")
    
    # Find all potential symbols across the entire page (excluding obvious legend)
    calendar_symbols = []
    for i, drawing in enumerate(drawings):
        rect = drawing["rect"]
        x, y = rect[0], rect[1]
        width, height = rect[2] - rect[0], rect[3] - rect[1]
        
        # Much broader search - exclude only legend area on far right
        if x < 360 and 3 < width < 50 and 3 < height < 50:
            waste_type = classify_waste_symbol(drawing)
            item_count = len(drawing["items"])
            
            # Analyze item types
            item_types = {}
            for item in drawing["items"]:
                item_type = item[0]
                item_types[item_type] = item_types.get(item_type, 0) + 1
            
            calendar_symbols.append({
                "index": i,
                "rect": rect,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "center_y": (rect[1] + rect[3]) / 2,
                "item_count": item_count,
                "item_types": item_types,
                "waste_type": waste_type
            })
    
    print(f"\nFound {len(calendar_symbols)} potential symbols across full page")
    
    # Sort by Y position for easier analysis
    calendar_symbols.sort(key=lambda s: s["center_y"])
    
    # Group symbols by Y position ranges corresponding to calendar weeks
    y_ranges = []
    current_range = []
    last_y = -999
    
    for symbol in calendar_symbols:
        # Use larger tolerance for week grouping
        if abs(symbol["center_y"] - last_y) > 20:
            if current_range:
                y_ranges.append(current_range)
            current_range = [symbol]
            last_y = symbol["center_y"]
        else:
            current_range.append(symbol)
            last_y = max(last_y, symbol["center_y"])
    
    if current_range:
        y_ranges.append(current_range)
    
    print(f"\nSymbols grouped into {len(y_ranges)} Y-ranges (likely weeks):")
    
    for i, range_symbols in enumerate(y_ranges):
        avg_y = sum(s["center_y"] for s in range_symbols) / len(range_symbols)
        min_y = min(s["center_y"] for s in range_symbols)
        max_y = max(s["center_y"] for s in range_symbols)
        
        print(f"\nRange {i+1}: y={min_y:.1f}-{max_y:.1f} (avg={avg_y:.1f}), {len(range_symbols)} symbols")
        
        # Find closest dates for this range
        closest_dates = []
        for day, day_y in date_positions.items():
            if min_y - 30 <= day_y <= max_y + 30:  # Allow some tolerance
                closest_dates.append((day, abs(avg_y - day_y)))
        
        closest_dates.sort(key=lambda x: x[1])
        date_range = [d[0] for d in closest_dates[:7]]  # Get up to 7 closest days (week)
        print(f"  Likely corresponds to days: {sorted(date_range)}")
        
        # Show classified symbols in this range
        classified_symbols = [(s["waste_type"], s["center_y"]) for s in range_symbols if s["waste_type"]]
        print(f"  Classified symbols: {len(classified_symbols)}")
        for waste_type, symbol_y in classified_symbols:
            print(f"    {waste_type} at y={symbol_y:.1f}")
    
    # Look for new waste types we haven't seen before
    all_waste_types = set()
    unclassified_by_items = {}
    
    for symbol in calendar_symbols:
        if symbol["waste_type"]:
            all_waste_types.add(symbol["waste_type"])
        else:
            # Track unclassified symbols by item count for new type discovery
            items = symbol["item_count"]
            if items not in unclassified_by_items:
                unclassified_by_items[items] = []
            unclassified_by_items[items].append(symbol)
    
    print(f"\nAll classified waste types found: {sorted(all_waste_types)}")
    print(f"\nUnclassified symbols by item count:")
    for item_count in sorted(unclassified_by_items.keys()):
        symbols = unclassified_by_items[item_count]
        print(f"  {item_count} items: {len(symbols)} symbols")
        if len(symbols) <= 5:  # Show details for smaller groups
            for symbol in symbols:
                print(f"    y={symbol['center_y']:.1f}, types={symbol['item_types']}")
    
    doc.close()

if __name__ == "__main__":
    analyze_full_june_page()