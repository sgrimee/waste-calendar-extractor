#!/usr/bin/env python3
"""
Test the adjusted PDF extraction area focusing on calendar content only.
"""
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import fitz
from waste_calendar_extractor.pdf_extractor import extract_waste_symbols_from_page

def test_adjusted_extraction():
    """Test the adjusted extraction area."""
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
    
    # Test the extraction with new boundaries
    print("Testing adjusted extraction...")
    date_waste_map = extract_waste_symbols_from_page(june_page)
    
    print(f"\nExtracted waste collection data for {len([d for d in date_waste_map.values() if d])} days:")
    
    for day in range(1, 31):
        waste_types = date_waste_map.get(day, [])
        if waste_types:
            print(f"  Day {day}: {', '.join(waste_types)}")
        else:
            print(f"  Day {day}: No collection")
    
    # Compare with expected results for June 2025
    expected_data = {
        2: ["organic", "hedge"],  # June 2
        3: ["residual"],  # June 3
        5: ["paper", "problematic"],  # June 5
        7: ["organic"],  # June 7
        # Days 1 and 8 should have no collection
    }
    
    print(f"\n=== COMPARISON WITH EXPECTED DATA ===")
    matches = 0
    total_expected = len(expected_data)
    
    for day, expected_types in expected_data.items():
        actual_types = sorted(date_waste_map.get(day, []))
        expected_types_sorted = sorted(expected_types)
        
        if actual_types == expected_types_sorted:
            print(f"✓ Day {day}: MATCH - {actual_types}")
            matches += 1
        else:
            print(f"✗ Day {day}: MISMATCH")
            print(f"    Expected: {expected_types_sorted}")
            print(f"    Actual:   {actual_types}")
    
    # Check days that should be empty
    empty_days = [1, 8]
    for day in empty_days:
        actual_types = date_waste_map.get(day, [])
        if not actual_types:
            print(f"✓ Day {day}: CORRECT - No collection")
            matches += 1
        else:
            print(f"✗ Day {day}: INCORRECT - Should be empty but got: {actual_types}")
        total_expected += 1
    
    print(f"\nOverall accuracy: {matches}/{total_expected} ({matches/total_expected*100:.1f}%)")
    
    doc.close()

if __name__ == "__main__":
    test_adjusted_extraction()