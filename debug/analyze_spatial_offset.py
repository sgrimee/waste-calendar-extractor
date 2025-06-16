#!/usr/bin/env python3
"""
Analyze the spatial offset causing off-by-one assignment errors.
"""
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import fitz
from waste_calendar_extractor.pdf_extractor import extract_date_positions, classify_waste_symbol

def analyze_spatial_offset():
    """Analyze why symbols are being assigned to wrong days."""
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
    print(f"\nDate positions for key days:")
    key_days = [4, 5, 6, 19, 20, 26]
    for day in key_days:
        if day in date_positions:
            print(f"  Day {day}: y={date_positions[day]:.1f}")
    
    # Get all drawings in calendar area
    drawings = june_page.get_drawings()
    
    # Filter to calendar area and classify
    problem_symbols = []
    for i, drawing in enumerate(drawings):
        rect = drawing["rect"]
        x, y = rect[0], rect[1]
        width, height = rect[2] - rect[0], rect[3] - rect[1]
        
        # Use same bounds as extractor
        if (
            x < 350  # Calendar area, excluding legend
            and 70 < y < 780  # Cover calendar from top dates to bottom dates
            and 2 < width < 60  # Reasonable symbol size range  
            and 2 < height < 60  # Reasonable symbol size range
        ):
            waste_type = classify_waste_symbol(drawing)
            if waste_type in ["electric", "paper", "problematic", "packaging", "bulky", "glass"]:
                center_y = (rect[1] + rect[3]) / 2
                
                # Find closest date
                closest_date = None
                min_distance = float('inf')
                for date_num, date_y in date_positions.items():
                    distance = abs(center_y - date_y)
                    if distance < min_distance:
                        min_distance = distance
                        closest_date = date_num
                
                problem_symbols.append({
                    'waste_type': waste_type,
                    'y': y,
                    'center_y': center_y,
                    'closest_date': closest_date,
                    'distance': min_distance,
                    'item_count': len(drawing['items'])
                })
    
    print(f"\nProblem symbols and their assignments:")
    for symbol in sorted(problem_symbols, key=lambda s: s['center_y']):
        print(f"  {symbol['waste_type']:>12} (items: {symbol['item_count']:>3}): y={symbol['center_y']:>6.1f} → Day {symbol['closest_date']} (dist: {symbol['distance']:.1f})")
    
    # Check expected vs actual mapping for problem cases
    expected_mapping = {
        4: ["electric"],
        5: ["paper", "problematic"], 
        6: ["packaging"],
        19: ["paper"],
        20: ["packaging"],
        26: ["glass"]
    }
    
    print(f"\n=== SPECIFIC PROBLEM ANALYSIS ===")
    
    for expected_day, expected_types in expected_mapping.items():
        if expected_day in date_positions:
            date_y = date_positions[expected_day]
            print(f"\nDay {expected_day} (y={date_y:.1f}) should have: {expected_types}")
            
            # Find symbols near this date
            nearby_symbols = [s for s in problem_symbols if abs(s['center_y'] - date_y) <= 15]
            if nearby_symbols:
                print(f"  Nearby symbols:")
                for symbol in nearby_symbols:
                    print(f"    {symbol['waste_type']} at y={symbol['center_y']:.1f} (assigned to day {symbol['closest_date']})")
            else:
                print(f"  No symbols found within 15px of this date!")
                
                # Look for expected types anywhere
                type_symbols = [s for s in problem_symbols if s['waste_type'] in expected_types]
                if type_symbols:
                    print(f"  But found expected types elsewhere:")
                    for symbol in type_symbols:
                        print(f"    {symbol['waste_type']} at y={symbol['center_y']:.1f} → assigned to day {symbol['closest_date']}")
    
    # Check if there's a systematic offset
    print(f"\n=== OFFSET ANALYSIS ===")
    offsets = []
    for symbol in problem_symbols:
        actual_day = symbol['closest_date']
        center_y = symbol['center_y']
        
        # Find what day this Y position should correspond to based on expected mapping
        for expected_day, expected_types in expected_mapping.items():
            if symbol['waste_type'] in expected_types:
                expected_date_y = date_positions.get(expected_day, 0)
                offset = center_y - expected_date_y
                offsets.append((symbol['waste_type'], expected_day, actual_day, offset))
                break
    
    if offsets:
        print("Symbol type → Expected day → Actual day → Y offset:")
        for waste_type, expected_day, actual_day, offset in offsets:
            print(f"  {waste_type:>12} → Day {expected_day:>2} → Day {actual_day:>2} → {offset:>+6.1f}px")
        
        avg_offset = sum(offset for _, _, _, offset in offsets) / len(offsets)
        print(f"\nAverage Y offset: {avg_offset:+.1f}px")
    
    doc.close()

if __name__ == "__main__":
    analyze_spatial_offset()