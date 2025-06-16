#!/usr/bin/env python3
"""
Analyze the characteristics of symbols that are being extracted to improve classification.
"""
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import fitz
from waste_calendar_extractor.pdf_extractor import extract_date_positions

def analyze_symbol_characteristics():
    """Analyze symbol characteristics for better classification."""
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
    print(f"Date positions: {sorted(date_positions.keys())}")
    
    # Get all drawings with detailed analysis
    drawings = june_page.get_drawings()
    
    # Filter to calendar area using our new bounds
    calendar_symbols = []
    for i, drawing in enumerate(drawings):
        rect = drawing["rect"]
        x, y = rect[0], rect[1]
        width, height = rect[2] - rect[0], rect[3] - rect[1]
        
        # Use the same bounds as in the extractor
        if (
            x < 350  # Calendar area, excluding legend
            and 70 < y < 780  # Cover calendar from top dates to bottom dates
            and 2 < width < 60  # Reasonable symbol size range  
            and 2 < height < 60  # Reasonable symbol size range
        ):
            items = drawing["items"]
            item_count = len(items)
            
            # Analyze item types
            item_types = {}
            for item in items:
                item_type = item[0]
                item_types[item_type] = item_types.get(item_type, 0) + 1
            
            # Find closest date
            center_y = (rect[1] + rect[3]) / 2
            closest_date = None
            min_distance = float('inf')
            for date_num, date_y in date_positions.items():
                distance = abs(center_y - date_y)
                if distance < min_distance:
                    min_distance = distance
                    closest_date = date_num
            
            calendar_symbols.append({
                'index': i,
                'x': x,
                'y': y,
                'center_y': center_y,
                'width': width,
                'height': height,
                'item_count': item_count,
                'item_types': item_types,
                'closest_date': closest_date,
                'distance_to_date': min_distance,
                'items_detail': items[:3]  # First 3 items for analysis
            })
    
    print(f"\nFound {len(calendar_symbols)} symbols in calendar area")
    
    # Group by item count for pattern analysis
    by_item_count = {}
    for symbol in calendar_symbols:
        count = symbol['item_count']
        if count not in by_item_count:
            by_item_count[count] = []
        by_item_count[count].append(symbol)
    
    print(f"\nSymbols grouped by item count:")
    for count in sorted(by_item_count.keys()):
        symbols = by_item_count[count]
        print(f"\n{count} items: {len(symbols)} symbols")
        
        # Show representative samples
        if len(symbols) <= 5:
            for symbol in symbols:
                print(f"  Date {symbol['closest_date']}: y={symbol['center_y']:.1f}, types={symbol['item_types']}")
        else:
            # Show a few samples from different dates
            sample_symbols = sorted(symbols, key=lambda s: s['closest_date'])[:5]
            for symbol in sample_symbols:
                print(f"  Date {symbol['closest_date']}: y={symbol['center_y']:.1f}, types={symbol['item_types']}")
        
        # Look for patterns in item types
        all_item_types = {}
        for symbol in symbols:
            for item_type, count in symbol['item_types'].items():
                all_item_types[item_type] = all_item_types.get(item_type, 0) + count
        print(f"  Common item types: {all_item_types}")
    
    # Focus on symbols close to expected dates (2, 3, 5, 7)
    expected_dates = [2, 3, 5, 7]
    print(f"\n=== SYMBOLS NEAR EXPECTED COLLECTION DATES ===")
    
    for expected_date in expected_dates:
        if expected_date in date_positions:
            date_y = date_positions[expected_date]
            nearby_symbols = [s for s in calendar_symbols if abs(s['center_y'] - date_y) <= 5]
            
            print(f"\nDay {expected_date} (y={date_y:.1f}):")
            print(f"  Found {len(nearby_symbols)} nearby symbols:")
            
            for symbol in nearby_symbols:
                print(f"    Items: {symbol['item_count']}, Types: {symbol['item_types']}, y={symbol['center_y']:.1f}")
                if symbol['items_detail']:
                    print(f"    First item: {symbol['items_detail'][0]}")
    
    doc.close()

if __name__ == "__main__":
    analyze_symbol_characteristics()