#!/usr/bin/env python3
"""
Quick analysis of symbol detection for debugging issue #9.
"""
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import fitz
from waste_calendar_extractor.pdf_extractor import (
    extract_date_positions,
    extract_waste_symbols_from_page
)

def quick_analysis():
    """Quick analysis of current symbol detection."""
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
    
    # Extract symbols using current implementation
    date_waste_map = extract_waste_symbols_from_page(june_page)
    
    print("Current extraction results:")
    print(f"Total days processed: {len(date_waste_map)}")
    
    # Show results for first 10 days and compare with expected
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
    }
    
    print("\nComparison with expected data (first 10 days):")
    correct_count = 0
    for day in range(1, 11):
        expected = expected_data.get(day, [])
        actual = date_waste_map.get(day, [])
        
        # Sort for comparison
        expected_sorted = sorted(expected)
        actual_sorted = sorted(actual)
        
        match = expected_sorted == actual_sorted
        if match:
            correct_count += 1
        
        status = "✓" if match else "✗"
        print(f"  Day {day:2d}: {status} Expected: {expected_sorted}, Actual: {actual_sorted}")
    
    print(f"\nAccuracy for first 10 days: {correct_count}/10 = {correct_count/10*100:.1f}%")
    
    # Show all detected symbols by day
    print("\nAll detected symbols by day:")
    for day in range(1, 31):
        if date_waste_map.get(day):
            print(f"  Day {day}: {date_waste_map[day]}")
    
    doc.close()

if __name__ == "__main__":
    quick_analysis()