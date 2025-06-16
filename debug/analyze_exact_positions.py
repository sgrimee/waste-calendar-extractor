#!/usr/bin/env python3
"""
Analyze the exact positions of symbols causing off-by-one errors.
"""
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import fitz
from waste_calendar_extractor.pdf_extractor import extract_date_positions, classify_waste_symbol

def analyze_exact_positions():
    """Analyze exact symbol positions vs expected days."""
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
    
    # Problem days with expected vs actual
    problem_mapping = {
        4: ["electric"],           # Getting hedge+residual 
        5: ["paper", "problematic"], # Getting electric+residual
        6: ["packaging"],          # Getting problematic+paper
        7: ["organic"],            # Getting residual
        16: ["organic"],           # Getting residual
        19: ["paper"],             # Getting residual
        20: ["packaging"],         # Getting problematic+paper
        21: ["organic"],           # Getting residual
        30: ["organic"],           # Getting residual
    }
    
    print("=== EXACT POSITION ANALYSIS ===\n")
    
    # Get all drawings and classify
    drawings = june_page.get_drawings()
    
    all_symbols = []
    for i, drawing in enumerate(drawings):
        rect = drawing["rect"]
        x, y = rect[0], rect[1]
        width, height = rect[2] - rect[0], rect[3] - rect[1]
        center_y = (rect[1] + rect[3]) / 2
        
        # Filter to calendar area
        if (
            x < 350  # Calendar area
            and 70 < y < 780  # Calendar Y range
            and 2 < width < 60  # Reasonable size
            and 2 < height < 60
        ):
            waste_type = classify_waste_symbol(drawing)
            if waste_type:
                # Find closest date
                closest_date = None
                min_distance = float('inf')
                for date_num, date_y in date_positions.items():
                    distance = abs(center_y - date_y)
                    if distance < min_distance:
                        min_distance = distance
                        closest_date = date_num
                
                all_symbols.append({
                    'waste_type': waste_type,
                    'y': y,
                    'center_y': center_y,
                    'closest_date': closest_date,
                    'distance': min_distance,
                    'item_count': len(drawing['items'])
                })
    
    # Show where each expected type is actually found
    for day, expected_types in problem_mapping.items():
        if day in date_positions:
            date_y = date_positions[day]
            print(f"Day {day} (y={date_y:.1f}) expects: {expected_types}")
            
            # Find symbols assigned to this day
            assigned_here = [s for s in all_symbols if s['closest_date'] == day]
            if assigned_here:
                print(f"  Actually assigned to Day {day}:")
                for symbol in assigned_here:
                    print(f"    {symbol['waste_type']} at y={symbol['center_y']:.1f} (dist: {symbol['distance']:.1f})")
            
            # Find where the expected types actually are
            for expected_type in expected_types:
                found_elsewhere = [s for s in all_symbols if s['waste_type'] == expected_type and s['closest_date'] != day]
                if found_elsewhere:
                    print(f"  But '{expected_type}' is assigned to:")
                    for symbol in found_elsewhere:
                        other_day_y = date_positions.get(symbol['closest_date'], 0)
                        print(f"    Day {symbol['closest_date']} at y={symbol['center_y']:.1f} (day {symbol['closest_date']} is at y={other_day_y:.1f})")
            print()
    
    # Check specific problem cases
    print("=== SPECIFIC ANALYSIS ===\n")
    
    # Day 4 should have electric but gets hedge+residual
    print("Day 4 issue: Should have ELECTRIC")
    electric_symbols = [s for s in all_symbols if s['waste_type'] == 'electric']
    for symbol in electric_symbols:
        expected_day = 4
        actual_day = symbol['closest_date'] 
        expected_y = date_positions[expected_day]
        actual_y = symbol['center_y']
        distance_to_expected = abs(actual_y - expected_y)
        print(f"  Electric symbol: y={actual_y:.1f} → Day {actual_day} (distance to Day 4: {distance_to_expected:.1f})")
    
    # Days 5,6 confusion with paper/problematic/packaging
    print("\nDays 5-6 confusion: paper/problematic/packaging")
    relevant_types = ['paper', 'problematic', 'packaging']
    day5_y = date_positions[5]
    day6_y = date_positions[6]
    
    for waste_type in relevant_types:
        symbols = [s for s in all_symbols if s['waste_type'] == waste_type]
        for symbol in symbols:
            dist_to_5 = abs(symbol['center_y'] - day5_y)
            dist_to_6 = abs(symbol['center_y'] - day6_y)
            print(f"  {waste_type:>12}: y={symbol['center_y']:>6.1f} → Day {symbol['closest_date']} (dist to Day 5: {dist_to_5:.1f}, to Day 6: {dist_to_6:.1f})")
    
    print(f"  Day 5 position: y={day5_y:.1f}")
    print(f"  Day 6 position: y={day6_y:.1f}")
    
    doc.close()

if __name__ == "__main__":
    analyze_exact_positions()