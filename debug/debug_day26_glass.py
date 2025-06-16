#!/usr/bin/env python3
"""
Debug exactly what's happening with the Day 26 glass symbol.
"""
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import fitz
from waste_calendar_extractor.pdf_extractor import classify_waste_symbol, extract_date_positions

def debug_day26_glass():
    """Debug the Day 26 glass symbol classification."""
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
    
    # Get date positions
    date_positions = extract_date_positions(june_page)
    day26_y = date_positions[26]
    print(f"Day 26 position: y={day26_y}")
    
    # Get all drawings
    drawings = june_page.get_drawings()
    
    print(f"Looking for symbols near Day 26 (y={day26_y})...")
    
    found_symbols = []
    for i, drawing in enumerate(drawings):
        rect = drawing["rect"]
        x, y = rect[0], rect[1]
        width, height = rect[2] - rect[0], rect[3] - rect[1]
        center_y = (rect[1] + rect[3]) / 2
        
        # Check if this is near Day 26
        if abs(center_y - day26_y) <= 5:
            print(f"\nSymbol {i} near Day 26:")
            print(f"  Position: x={x:.1f}, y={y:.1f}, center_y={center_y:.1f}")
            print(f"  Size: {width:.1f} x {height:.1f}")
            print(f"  Items: {len(drawing['items'])}")
            
            # Analyze item types
            item_types = {}
            for item in drawing["items"]:
                item_type = item[0]
                item_types[item_type] = item_types.get(item_type, 0) + 1
            print(f"  Item types: {item_types}")
            
            # Test classification
            waste_type = classify_waste_symbol(drawing)
            print(f"  Classified as: {waste_type}")
            
            # Check if it passes the calendar area filter
            in_calendar_area = (
                x < 350  # Calendar area, excluding legend
                and 70 < y < 780  # Cover calendar from top dates to bottom dates
                and 2 < width < 60  # Reasonable symbol size range  
                and 2 < height < 60  # Reasonable symbol size range
            )
            print(f"  Passes calendar area filter: {in_calendar_area}")
            
            found_symbols.append({
                'drawing': drawing,
                'classification': waste_type,
                'in_area': in_calendar_area,
                'y': y,
                'center_y': center_y
            })
    
    if not found_symbols:
        print("No symbols found near Day 26!")
    else:
        print(f"\nFound {len(found_symbols)} symbols near Day 26")
        
        # Check which ones would make it through the full pipeline
        for i, symbol in enumerate(found_symbols):
            print(f"\nSymbol {i}:")
            print(f"  Classification: {symbol['classification']}")
            print(f"  In calendar area: {symbol['in_area']}")
            if symbol['classification'] and symbol['in_area']:
                print(f"  → WOULD BE INCLUDED in extraction")
            else:
                print(f"  → WOULD BE EXCLUDED from extraction")
                if not symbol['classification']:
                    print(f"    Reason: No classification")
                if not symbol['in_area']:
                    print(f"    Reason: Outside calendar area")
    
    doc.close()

if __name__ == "__main__":
    debug_day26_glass()