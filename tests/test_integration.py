#!/usr/bin/env python3
"""
Integration tests and extraction tests with given output.
"""

import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest


@pytest.mark.integration
@pytest.mark.parametrize(
    "month,date,expected_types",
    [
        # June 2025 expected data from visual PDF inspection
        (6, 1, []),  # No collection
        (6, 2, ["organic", "hedge"]),
        (6, 3, ["residual"]),
        (6, 4, ["electric"]),
        (6, 5, ["paper", "carton", "problematic"]),
        (6, 6, ["packaging"]),
        (6, 7, ["organic"]),
        (6, 8, []),  # No collection
    ],
)
def test_2025_expected_dates(month, date, expected_types):
    """Test that the correct dates are extracted for specific months in 2025 using real PDF extraction."""
    from waste_calendar_extractor.calendar_processor import extract_dates_from_pdf

    # Path to the real PDF file
    pdf_path = "tests/2025.pdf"

    # Extract all dates from the PDF
    all_results = extract_dates_from_pdf(pdf_path, year=2025)

    # Filter to only specific month/date results
    month_results = [
        result
        for result in all_results
        if result["date"].month == month and result["date"].year == 2025 and result["date"].day == date
    ]

    # Handle case where no collection is expected for this date
    if len(expected_types) == 0:
        assert len(month_results) == 0, (
            f"Expected no collection on {month}/{date}, but found: {[r['icons'] for r in month_results]}"
        )
        return

    assert len(month_results) > 0, f"No results found for {month}/{date}, 2025 in the PDF."

    # Test the first (and likely only) result for this date
    result = month_results[0]
    assert result["date"].day == date
    assert result["date"].month == month
    assert result["date"].year == 2025

    # Flexible matching for waste types since the actual PDF may use different languages/formats
    result_icons = result["icons"].lower()
    type_patterns = {
        "organic": ["organic", "organesch", "organique", "ressources"],
        "hedge": ["hedge", "hecken", "haies", "sapins", "gréngschtët", "grengschtet"],
        "residual": ["residual", "rescht", "ménager"],
        "electric": ["electric", "elektro", "électrique"],
        "paper": ["paper", "pabeier", "papier", "carton", "kartong"],
        "carton": ["carton", "kartong", "papier"],
        "problematic": ["problematic", "problematesch", "problématique", "problemoff"],
        "packaging": ["packaging", "verpack", "emballage", "valorlux"],
    }

    # Check that all expected types are found and no unexpected types are present
    found_types = []
    for expected_type in expected_types:
        patterns = type_patterns.get(expected_type, [expected_type])
        if any(pattern in result_icons for pattern in patterns):
            found_types.append(expected_type)

    # Verify all expected types were found
    assert len(found_types) == len(expected_types), (
        f"Expected {expected_types} but only found {found_types} in result icons: {result['icons']}"
    )

    # Verify no unexpected types are present by checking if any other type patterns match
    unexpected_types = []
    all_other_types = set(type_patterns.keys()) - set(expected_types)
    for other_type in all_other_types:
        patterns = type_patterns.get(other_type, [other_type])
        if any(pattern in result_icons for pattern in patterns):
            unexpected_types.append(other_type)

    assert len(unexpected_types) == 0, (
        f"Found unexpected waste types {unexpected_types} in result icons: {result['icons']}"
    )
