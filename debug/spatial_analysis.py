#!/usr/bin/env python3
"""
Comprehensive spatial analysis of June 2025 symbols for issue #9.
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

def spatial_analysis():
    """Comprehensive spatial analysis of symbol placement."""
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
    print("Date positions (Y-coordinates):")
    for day in sorted(date_positions.keys())[:15]:  # First 15 days
        print(f"  Day {day:2d}: y={date_positions[day]:6.1f}")
    
    # Get all drawings and analyze spatial distribution
    drawings = june_page.get_drawings()
    print(f"\nTotal drawings: {len(drawings)}")
    
    # Find all potential symbols across entire page
    calendar_symbols = []
    for i, drawing in enumerate(drawings):
        rect = drawing["rect"]
        x, y = rect[0], rect[1]
        width, height = rect[2] - rect[0], rect[3] - rect[1]
        
        # Use same bounds as current implementation
        if (
            x < 360  # Calendar area, excluding legend
            and 80 < y < 800  # Cover entire calendar
            and 3 < width < 50  # Reasonable symbol size
            and 3 < height < 50
        ):
            waste_type = classify_waste_symbol(drawing)
            if waste_type:  # Only classified symbols
                center_y = (rect[1] + rect[3]) / 2
                calendar_symbols.append({
                    "waste_type": waste_type,
                    "center_y": center_y,
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height
                })
    
    print(f"\nFound {len(calendar_symbols)} classified symbols")
    
    # Sort by Y position for analysis
    calendar_symbols.sort(key=lambda s: s["center_y"])
    
    print("\nAll classified symbols (sorted by Y position):")
    for symbol in calendar_symbols:
        print(f"  {symbol['waste_type']:12s} at y={symbol['center_y']:6.1f}, x={symbol['x']:6.1f}")
    
    # Analyze distance between symbols and dates
    print("\nSymbol-to-date distance analysis:")
    for symbol in calendar_symbols:
        closest_date = None
        min_distance = float('inf')
        distances = []
        
        for date_num, date_y in date_positions.items():
            if 1 <= date_num <= 30:
                distance = abs(date_y - symbol["center_y"])
                distances.append((date_num, distance))
                if distance < min_distance:
                    min_distance = distance
                    closest_date = date_num
        
        # Sort distances to see closest options
        distances.sort(key=lambda x: x[1])
        top_3 = distances[:3]
        
        print(f"  {symbol['waste_type']:12s} y={symbol['center_y']:6.1f} -> closest: day {closest_date} (dist={min_distance:.1f})")
        print(f"    Top 3 options: {top_3}")
    
    # Test different tolerance values
    print("\nTesting different tolerance values:")
    for tolerance in [2.0, 3.0, 4.0, 5.0, 7.0, 10.0]:
        assignments = {}
        for day in range(1, 31):
            assignments[day] = []
        
        for symbol in calendar_symbols:
            closest_date = None
            min_distance = float('inf')
            
            for date_num, date_y in date_positions.items():
                if 1 <= date_num <= 30:
                    distance = abs(date_y - symbol["center_y"])
                    if distance < min_distance and distance <= tolerance:
                        min_distance = distance
                        closest_date = date_num
            
            if closest_date is not None:
                assignments[closest_date].append(symbol["waste_type"])
        
        # Count days with assignments
        assigned_days = sum(1 for day_list in assignments.values() if day_list)
        total_symbols_assigned = sum(len(day_list) for day_list in assignments.values())
        
        print(f"  Tolerance {tolerance:4.1f}: {assigned_days} days assigned, {total_symbols_assigned} symbols total")
        
        # Show clustering issues
        clustered_days = [(day, symbols) for day, symbols in assignments.items() if len(symbols) > 1]
        if clustered_days:
            print(f"    Clustering issues: {len(clustered_days)} days with multiple symbols")
            for day, symbols in clustered_days[:3]:  # Show first 3
                print(f"      Day {day}: {symbols}")
    
    doc.close()

if __name__ == "__main__":
    spatial_analysis()