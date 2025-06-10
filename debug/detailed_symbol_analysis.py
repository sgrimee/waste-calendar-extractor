#!/usr/bin/env python3
"""
Detailed debug script to analyze symbol positions against expected results.
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

def detailed_analysis():
    """Analyze symbols with exact coordinates for days 1-9."""
    pdf_path = "pdf/2025.pdf"
    
    # Expected from visual inspection
    expected = {
        1: [],  # No collection
        2: ["organic", "hedge"],
        3: ["residual"], 
        4: ["electric"],
        5: ["paper", "problematic"],
        6: ["packaging"],
        7: ["organic"],
        8: [],  # No collection
        9: [],  # No collection
    }
    
    # Luxembourgish to English mapping
    lux_to_eng = {
        "Organesch Ressourcen": "organic",
        "Gréngschtëtsammlung": "hedge", 
        "Reschtoffäll": "residual",
        "Elektro- an Elektronikapparater": "electric",
        "Pabeier a Kartong": "paper",
        "Problemoffäll": "problematic",
        "Verpackungen": "packaging"
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
    print("Date positions:")
    for day in range(1, 10):
        if day in date_positions:
            print(f"  Day {day}: y={date_positions[day]:.1f}")
    
    # Get all drawings in calendar area, excluding legend
    drawings = june_page.get_drawings()
    calendar_symbols = []
    
    for i, drawing in enumerate(drawings):
        rect = drawing["rect"]
        x, y = rect[0], rect[1]
        width, height = rect[2] - rect[0], rect[3] - rect[1]
        
        # Calendar area only (exclude legend on right)
        if 270 < x < 320 and 80 < y < 320 and 5 < width < 50 and 5 < height < 50:
            waste_type = classify_waste_symbol(drawing)
            if waste_type:  # Only classified symbols
                center_y = (rect[1] + rect[3]) / 2
                calendar_symbols.append({
                    "waste_type": waste_type,
                    "waste_type_eng": lux_to_eng.get(waste_type, waste_type),
                    "center_y": center_y,
                    "x": x,
                    "item_count": len(drawing["items"])
                })
    
    print(f"\nFound {len(calendar_symbols)} calendar symbols:")
    calendar_symbols.sort(key=lambda s: s["center_y"])
    
    for symbol in calendar_symbols:
        print(f"  {symbol['waste_type_eng']:>12} (y={symbol['center_y']:5.1f}, x={symbol['x']:5.1f}, items={symbol['item_count']:3d})")
    
    print("\nMapping with different tolerances:")
    
    for tolerance in [10.0, 15.0, 20.0, 25.0]:
        print(f"\nTolerance: {tolerance}")
        date_waste_map = {}
        
        for day in range(1, 10):
            if day not in date_positions:
                continue
                
            date_y = date_positions[day]
            date_waste_map[day] = []
            
            for symbol in calendar_symbols:
                y_distance = abs(date_y - symbol["center_y"])
                if y_distance <= tolerance:
                    date_waste_map[day].append(symbol["waste_type_eng"])
            
            # Remove duplicates
            date_waste_map[day] = list(set(date_waste_map[day]))
            
            expected_types = expected[day]
            actual_types = sorted(date_waste_map[day])
            expected_sorted = sorted(expected_types)
            
            match = "✓" if actual_types == expected_sorted else "✗"
            print(f"  Day {day}: {match} Expected: {expected_sorted}, Got: {actual_types}")
    
    doc.close()

if __name__ == "__main__":
    detailed_analysis()