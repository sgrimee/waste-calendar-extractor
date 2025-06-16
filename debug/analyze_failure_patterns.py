#!/usr/bin/env python3
"""
Analyze the specific failure patterns in the integration tests.
"""
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from waste_calendar_extractor.calendar_processor import extract_dates_from_pdf

def analyze_failure_patterns():
    """Analyze what's causing the test failures."""
    
    # Extract the actual results
    pdf_path = "pdf/2025.pdf"
    results = extract_dates_from_pdf(pdf_path, year=2025)
    
    # Filter to June results
    june_results = [r for r in results if r["date"].month == 6]
    
    # Expected vs actual mapping
    expected_mapping = {
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
        11: [],  # No collection
        12: [],  # No collection
        13: [],  # No collection
        14: [],  # No collection
        15: [],  # No collection
        16: ["organic"],
        17: ["residual"],
        18: [],  # No collection
        19: ["paper"],
        20: ["packaging"],
        21: ["organic"],
        22: [],  # No collection
        23: [],  # No collection
        24: ["residual"],
        25: [],  # No collection
        26: ["glass"],
        27: [],  # No collection
        28: [],
        29: [],  # No collection
        30: ["organic"],
    }
    
    print("=== FAILURE ANALYSIS ===\n")
    
    # Group results by day
    actual_mapping = {}
    for result in june_results:
        day = result["date"].day
        icons = result["icons"].lower()
        if day not in actual_mapping:
            actual_mapping[day] = []
        actual_mapping[day].append(icons)
    
    # Analyze each failing day
    failing_days = []
    for day in range(1, 31):
        expected = expected_mapping.get(day, [])
        actual = actual_mapping.get(day, [])
        
        if len(expected) == 0 and len(actual) == 0:
            # Both empty - correct
            continue
        elif len(expected) == 0 and len(actual) > 0:
            # Expected empty but got something
            failing_days.append((day, "unexpected_collection", expected, actual))
        elif len(expected) > 0 and len(actual) == 0:
            # Expected something but got nothing
            failing_days.append((day, "missing_collection", expected, actual))
        else:
            # Both have collections - check if they match
            actual_icons = " | ".join(actual)
            expected_set = set(expected)
            
            # Check if expected types are found in actual icons
            found_types = []
            type_patterns = {
                "organic": ["organic", "organesch", "organique", "ressources"],
                "hedge": ["hedge", "hecken", "haies", "sapins", "gréngschtët", "grengschtet"],
                "residual": ["residual", "rescht", "ménager"],
                "electric": ["electric", "elektro", "électrique"],
                "paper": ["paper", "pabeier", "papier", "carton", "kartong"],
                "problematic": ["problematic", "problematesch", "problématique", "problemoff"],
                "packaging": ["packaging", "verpack", "emballage", "valorlux"],
                "special": ["special", "pluschtier", "speziell", "spécial"],
                "bulky": ["bulky", "sperrmüll", "encombrants"],
                "glass": ["glass", "glas", "verre"],
            }
            
            for expected_type in expected:
                patterns = type_patterns.get(expected_type, [expected_type])
                if any(pattern in actual_icons for pattern in patterns):
                    found_types.append(expected_type)
            
            if set(found_types) != expected_set:
                failing_days.append((day, "type_mismatch", expected, actual))
    
    print(f"Found {len(failing_days)} failing days:\n")
    
    # Categorize failures
    categories = {
        "unexpected_collection": [],
        "missing_collection": [], 
        "type_mismatch": []
    }
    
    for day, category, expected, actual in failing_days:
        categories[category].append((day, expected, actual))
    
    for category, days in categories.items():
        if days:
            print(f"{category.upper().replace('_', ' ')} ({len(days)} days):")
            for day, expected, actual in days:
                print(f"  Day {day}: Expected {expected}, Got {actual}")
            print()
    
    # Look for specific patterns
    print("=== PATTERN ANALYSIS ===\n")
    
    # Check if symbols are being assigned to wrong days (off-by-one errors)
    print("Checking for off-by-one assignment errors:")
    for day, category, expected, actual in failing_days:
        if category == "type_mismatch":
            # Check if expected types appear on neighboring days
            for neighbor_day in [day-1, day+1]:
                if neighbor_day in actual_mapping:
                    neighbor_icons = " | ".join(actual_mapping[neighbor_day])
                    # Simple check if any expected type appears in neighbor
                    for exp_type in expected:
                        if exp_type in neighbor_icons:
                            print(f"  Day {day} expected '{exp_type}' but it appears on day {neighbor_day}")
    
    # Check for systematic classification errors
    print("\nSystematic classification errors:")
    actual_types = set()
    expected_types = set()
    
    for day, category, expected, actual in failing_days:
        if category == "type_mismatch":
            expected_types.update(expected)
            for icons in actual:
                # Extract individual types from "type1 | type2" format
                types = [t.strip() for t in icons.split("|")]
                actual_types.update(types)
    
    print(f"Expected types in failures: {sorted(expected_types)}")
    print(f"Actual types in failures: {sorted(actual_types)}")
    
    # Look for common substitutions
    print(f"\nCommon wrong classifications:")
    for day, category, expected, actual in failing_days:
        if category == "type_mismatch" and len(actual) == 1:
            actual_icons = actual[0]
            print(f"  Day {day}: '{' | '.join(expected)}' → '{actual_icons}'")

if __name__ == "__main__":
    analyze_failure_patterns()