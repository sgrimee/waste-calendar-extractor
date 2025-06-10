#!/usr/bin/env python3
"""
Find ALL symbols in the June page to understand the layout better.
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

def find_all_symbols():
    """Find all potential symbols across the entire June page."""
    pdf_path = "pdf/2025.pdf"
    
    # Open PDF and find June page
    doc = fitz.open(pdf_path)
    june_page = None
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        if "JUNI" in text:
            june_page = page
            break
    
    if not june_page:
        print("Could not find June page!")
        return
    
    # Get date positions for reference
    date_positions = extract_date_positions(june_page)
    print("Date positions for reference:")
    for day in range(1, 10):
        if day in date_positions:
            print(f"  Day {day}: y={date_positions[day]:.1f}")
    
    # Get all drawings
    drawings = june_page.get_drawings()
    
    # Find all symbols that could be waste types (broader search)
    all_symbols = []
    
    for i, drawing in enumerate(drawings):
        rect = drawing["rect"]
        x, y = rect[0], rect[1]
        width, height = rect[2] - rect[0], rect[3] - rect[1]
        
        # Much broader search - look everywhere except obvious legend area (x > 350)
        if x < 350 and 80 < y < 320 and 3 < width < 50 and 3 < height < 50:
            waste_type = classify_waste_symbol(drawing)
            item_count = len(drawing["items"])
            
            # Include both classified and unclassified symbols for analysis
            center_y = (rect[1] + rect[3]) / 2
            all_symbols.append({
                "waste_type": waste_type,
                "center_y": center_y,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "item_count": item_count,
                "rect": rect
            })
    
    print(f"\nFound {len(all_symbols)} potential symbols (x < 350):")
    all_symbols.sort(key=lambda s: s["center_y"])
    
    # Group by approximate Y positions (within 5 units = same row)
    y_groups = []
    current_group = []
    last_y = -999
    
    for symbol in all_symbols:
        if abs(symbol["center_y"] - last_y) > 5:
            if current_group:
                y_groups.append(current_group)
            current_group = [symbol]
            last_y = symbol["center_y"]
        else:
            current_group.append(symbol)
    
    if current_group:
        y_groups.append(current_group)
    
    print(f"\nSymbols grouped by Y position ({len(y_groups)} groups):")
    for i, group in enumerate(y_groups):
        avg_y = sum(s["center_y"] for s in group) / len(group)
        print(f"\nGroup {i+1} (avg_y={avg_y:.1f}):")
        
        # Find closest date
        closest_date = None
        min_distance = float('inf')
        for day, day_y in date_positions.items():
            if 1 <= day <= 9:
                distance = abs(avg_y - day_y)
                if distance < min_distance:
                    min_distance = distance
                    closest_date = day
        
        print(f"  Closest to day {closest_date} (distance={min_distance:.1f})")
        
        for symbol in group:
            classified = symbol["waste_type"] or "unclassified"
            print(f"    x={symbol['x']:5.1f}, y={symbol['center_y']:5.1f}, "
                  f"items={symbol['item_count']:3d}, type={classified}")
    
    doc.close()

if __name__ == "__main__":
    find_all_symbols()