#!/usr/bin/env python3
"""
Find the missing bulky and glass symbols that aren't being classified.
"""
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import fitz
from waste_calendar_extractor.pdf_extractor import extract_date_positions

def find_missing_symbols():
    """Find bulky and glass symbols that aren't being classified."""
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
    
    # Get date positions
    date_positions = extract_date_positions(june_page)
    
    # Expected positions for missing symbols
    expected_missing = {
        10: ["bulky"],  # Day 10 should have bulky
        26: ["glass"]   # Day 26 should have glass
    }
    
    print("Looking for missing symbols near expected days:")
    for day, expected_types in expected_missing.items():
        if day in date_positions:
            date_y = date_positions[day]
            print(f"\nDay {day} (y={date_y:.1f}) should have: {expected_types}")
    
    # Get all drawings and analyze those near the problem days
    drawings = june_page.get_drawings()
    
    for day, expected_types in expected_missing.items():
        if day not in date_positions:
            continue
            
        date_y = date_positions[day]
        print(f"\n=== SYMBOLS NEAR DAY {day} (y={date_y:.1f}) ===")
        
        nearby_symbols = []
        for i, drawing in enumerate(drawings):
            rect = drawing["rect"]
            x, y = rect[0], rect[1]
            width, height = rect[2] - rect[0], rect[3] - rect[1]
            center_y = (rect[1] + rect[3]) / 2
            
            # Look for symbols near this date (within 20px)
            if (
                x < 350  # Calendar area
                and abs(center_y - date_y) <= 20  # Near the target date
                and 2 < width < 60  # Reasonable size
                and 2 < height < 60
            ):
                items = drawing["items"]
                item_count = len(items)
                
                # Analyze item types
                item_types = {}
                for item in items:
                    item_type = item[0]
                    item_types[item_type] = item_types.get(item_type, 0) + 1
                
                nearby_symbols.append({
                    'index': i,
                    'x': x,
                    'y': y,
                    'center_y': center_y,
                    'width': width,
                    'height': height,
                    'item_count': item_count,
                    'item_types': item_types,
                    'distance': abs(center_y - date_y)
                })
        
        # Sort by distance to date
        nearby_symbols.sort(key=lambda s: s['distance'])
        
        print(f"Found {len(nearby_symbols)} symbols within 20px:")
        for symbol in nearby_symbols:
            print(f"  Items: {symbol['item_count']:>3}, Types: {symbol['item_types']}, y={symbol['center_y']:>6.1f}, dist={symbol['distance']:>4.1f}")
        
        # Look for unclassified symbols that might be our target
        if day == 10:  # Looking for bulky
            print("  Potential bulky symbols (looking for unique patterns):")
            for symbol in nearby_symbols:
                # Bulky waste might have unique characteristics
                if symbol['item_count'] not in [4, 11, 23, 34, 41, 56, 96, 392]:  # Known types
                    print(f"    CANDIDATE: {symbol['item_count']} items, {symbol['item_types']}")
        
        elif day == 26:  # Looking for glass
            print("  Potential glass symbols (looking for unique patterns):")
            for symbol in nearby_symbols:
                # Glass might have unique characteristics  
                if symbol['item_count'] not in [4, 11, 23, 34, 41, 56, 96, 392]:  # Known types
                    print(f"    CANDIDATE: {symbol['item_count']} items, {symbol['item_types']}")
    
    # Also look at ALL unclassified symbols to see what we might be missing
    print(f"\n=== ALL UNCLASSIFIED SYMBOLS IN CALENDAR AREA ===")
    
    known_counts = {4, 7, 8, 10, 11, 12, 13, 23, 34, 37, 41, 56, 96, 392}
    unclassified = []
    
    for i, drawing in enumerate(drawings):
        rect = drawing["rect"]
        x, y = rect[0], rect[1]
        width, height = rect[2] - rect[0], rect[3] - rect[1]
        center_y = (rect[1] + rect[3]) / 2
        
        if (
            x < 350  # Calendar area
            and 70 < y < 780  # Calendar Y range
            and 2 < width < 60  # Reasonable size
            and 2 < height < 60
        ):
            item_count = len(drawing["items"])
            if item_count not in known_counts:
                # Analyze item types
                item_types = {}
                for item in drawing["items"]:
                    item_type = item[0]
                    item_types[item_type] = item_types.get(item_type, 0) + 1
                
                # Find closest date
                closest_date = None
                min_distance = float('inf')
                for date_num, date_y_pos in date_positions.items():
                    distance = abs(center_y - date_y_pos)
                    if distance < min_distance:
                        min_distance = distance
                        closest_date = date_num
                
                unclassified.append({
                    'item_count': item_count,
                    'item_types': item_types,
                    'center_y': center_y,
                    'closest_date': closest_date,
                    'distance': min_distance
                })
    
    # Group by item count
    by_count = {}
    for symbol in unclassified:
        count = symbol['item_count']
        if count not in by_count:
            by_count[count] = []
        by_count[count].append(symbol)
    
    print("Unclassified symbols by item count:")
    for count in sorted(by_count.keys()):
        symbols = by_count[count]
        print(f"\n{count} items: {len(symbols)} symbols")
        for symbol in symbols[:3]:  # Show first 3
            print(f"  Day {symbol['closest_date']}: y={symbol['center_y']:.1f}, types={symbol['item_types']}")
    
    doc.close()

if __name__ == "__main__":
    find_missing_symbols()