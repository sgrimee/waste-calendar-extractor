#!/usr/bin/env python3
"""
Map expected test data to actual symbol positions to improve classification.
"""
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import fitz
from waste_calendar_extractor.pdf_extractor import extract_date_positions

def map_expected_to_actual():
    """Map expected test data to actual symbol positions."""
    pdf_path = "pdf/2025.pdf"
    
    # Expected data from the test
    expected_data = {
        1: [],  # No collection
        2: ["organic", "hedge"],
        3: ["residual"],
        4: ["electric"],
        5: ["paper", "problematic"],
        6: ["packaging"],
        7: ["organic"],
        8: [],  # No collection
        9: [],  # No collection
        10: ["bulky", "residual"],
        11: [],
        12: [],
        13: [],
        14: [],
        15: [],
        16: ["organic"],
        17: ["residual"],
        18: [],
        19: ["paper"],
        20: ["packaging"],
        21: ["organic"],
        22: [],
        23: [],
        24: ["residual"],
        25: [],
        26: ["glass"],
        27: [],
        28: [],
        29: [],
        30: ["organic"],
    }
    
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
    
    print("Expected vs Date Position Analysis:")
    print("="*50)
    
    for day in range(1, 31):
        expected = expected_data.get(day, [])
        date_y = date_positions.get(day, "N/A")
        
        if expected:  # Only show days with expected collections
            print(f"Day {day:2d} (y={date_y:6.1f}): Expected {expected}")
    
    # Analyze 4-item symbols and their positions
    print("\n" + "="*50)
    print("4-item Symbol Positions vs Expected Collections:")
    
    drawings = june_page.get_drawings()
    four_item_symbols = []
    
    for drawing in drawings:
        rect = drawing["rect"]
        x, y = rect[0], rect[1]
        item_count = len(drawing["items"])
        
        if (item_count == 4 and x < 360 and 80 < y < 750):
            four_item_symbols.append({
                "y": y,
                "center_y": (rect[1] + rect[3]) / 2,
                "x": x
            })
    
    four_item_symbols.sort(key=lambda s: s["center_y"])
    
    print(f"\nFound {len(four_item_symbols)} 4-item symbols:")
    for i, symbol in enumerate(four_item_symbols):
        # Find closest expected collection day
        closest_day = None
        min_distance = float('inf')
        
        for day, date_y in date_positions.items():
            if expected_data.get(day, []):  # Only consider days with expected collections
                distance = abs(date_y - symbol["center_y"])
                if distance < min_distance:
                    min_distance = distance
                    closest_day = day
        
        expected_types = expected_data.get(closest_day, [])
        print(f"  Symbol {i+1}: y={symbol['center_y']:6.1f} -> closest day {closest_day} (dist={min_distance:.1f})")
        print(f"    Expected types for day {closest_day}: {expected_types}")
    
    doc.close()

if __name__ == "__main__":
    map_expected_to_actual()