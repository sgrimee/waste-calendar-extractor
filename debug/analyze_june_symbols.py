#!/usr/bin/env python3
"""
Debug script to analyze waste symbols in June 2025 page.
"""
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import fitz
from waste_calendar_extractor.pdf_extractor import (
    extract_date_positions,
    extract_waste_symbols_from_page,
    classify_waste_symbol
)

def analyze_june_page():
    """Analyze the June 2025 page to understand symbol extraction."""
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
    
    # Extract date positions
    date_positions = extract_date_positions(june_page)
    print(f"Date positions found: {date_positions}")
    
    # Get all drawings
    drawings = june_page.get_drawings()
    print(f"Total drawings: {len(drawings)}")
    
    # Analyze symbols in the calendar area
    calendar_symbols = []
    for i, drawing in enumerate(drawings):
        rect = drawing["rect"]
        x, y, width, height = rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]
        
        # Look for symbols in the calendar area (broader search initially)
        if 200 < x < 400 and 50 < y < 400 and 3 < width < 50 and 3 < height < 50:
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
    
    print(f"\nCalendar symbols found: {len(calendar_symbols)}")
    
    # Sort by Y position for easier analysis
    calendar_symbols.sort(key=lambda s: s["center_y"])
    
    for symbol in calendar_symbols:
        print(f"Symbol at y={symbol['center_y']:.1f}, x={symbol['x']:.1f}: "
              f"items={symbol['item_count']}, types={symbol['item_types']}, "
              f"waste_type={symbol['waste_type']}")
    
    # Map symbols to dates
    print("\nMapping symbols to dates:")
    tolerance = 15.0
    
    for date_num in range(1, 10):  # Focus on days 1-9
        if date_num in date_positions:
            date_y = date_positions[date_num]
            matching_symbols = []
            
            for symbol in calendar_symbols:
                y_distance = abs(date_y - symbol["center_y"])
                if y_distance <= tolerance:
                    matching_symbols.append(symbol)
            
            print(f"Day {date_num} (y={date_y:.1f}): {len(matching_symbols)} symbols")
            for symbol in matching_symbols:
                print(f"  - {symbol['waste_type']} (y={symbol['center_y']:.1f}, "
                      f"distance={abs(date_y - symbol['center_y']):.1f})")
        else:
            print(f"Day {date_num}: No date position found")
    
    # Test the actual extraction function
    print("\nTesting extract_waste_symbols_from_page function:")
    date_waste_map = extract_waste_symbols_from_page(june_page)
    for date_num in range(1, 10):
        waste_types = date_waste_map.get(date_num, [])
        print(f"Day {date_num}: {waste_types}")
    
    doc.close()

if __name__ == "__main__":
    analyze_june_page()