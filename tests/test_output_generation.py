#!/usr/bin/env python3
"""
Unit tests for output generation functions.
"""

import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from ics import Calendar

from waste_calendar_extractor import (
    extract_language_from_waste_description,
    generate_ical_calendar,
    get_waste_type_icon,
)


def test_generate_calendar_with_events():
    """Test generating calendar with events using real file I/O."""
    # Test data - includes multi-type entry that should be split
    results = [
        {"date": datetime(2024, 1, 1), "icons": "Residual waste"},
        {"date": datetime(2024, 1, 8), "icons": "Paper | Carton"},
    ]

    # Use temporary file for testing
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ics", delete=False) as tmp_file:
        tmp_path = tmp_file.name

    try:
        # Call function
        events_added = generate_ical_calendar(results, tmp_path, 2024)

        # Verify - should be 3 events: 1 for residual waste, 2 for paper and carton (split)
        assert events_added == 3

        # Verify file contents by parsing it back
        with open(tmp_path, encoding="utf-8") as f:
            calendar_content = f.read()

        # Parse the calendar to verify events were added
        calendar = Calendar(calendar_content)
        assert len(calendar.events) == 3

        # Verify event details - multi-type entries should be split into separate events
        events = list(calendar.events)
        assert any("Residual waste" in event.name for event in events)
        assert any("Paper" in event.name and "Carton" not in event.name for event in events)
        assert any("Carton" in event.name and "Paper" not in event.name for event in events)

    finally:
        # Clean up
        Path(tmp_path).unlink(missing_ok=True)


def test_generate_calendar_empty_icons():
    """Test generating calendar with empty icons (should skip)."""
    # Test data with empty icons
    results = [
        {"date": datetime(2024, 1, 1), "icons": ""},
        {"date": datetime(2024, 1, 2), "icons": "   "},  # Just whitespace
    ]

    # Use temporary file for testing
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ics", delete=False) as tmp_file:
        tmp_path = tmp_file.name

    try:
        # Call function
        events_added = generate_ical_calendar(results, tmp_path, 2024)

        # Verify no events added
        assert events_added == 0

        # Verify file was created but has no events
        with open(tmp_path, encoding="utf-8") as f:
            calendar_content = f.read()

        calendar = Calendar(calendar_content)
        assert len(calendar.events) == 0

    finally:
        # Clean up
        Path(tmp_path).unlink(missing_ok=True)


def test_multi_collection_days_generation():
    """Test that multi-collection days generate separate events for each waste type."""
    # Test data with multi-type entries matching the GitHub issue examples
    results = [
        {"date": datetime(2025, 6, 2), "icons": "Organesch Ressourcen | Gréngschtëtsammlung"},
        {"date": datetime(2025, 6, 5), "icons": "Pabeier a Kartong | Problemoffäll"},
        {"date": datetime(2025, 6, 10), "icons": "Single Type"},  # Single type for comparison
    ]

    # Use temporary file for testing
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ics", delete=False) as tmp_file:
        tmp_path = tmp_file.name

    try:
        # Call function
        events_added = generate_ical_calendar(results, tmp_path, 2025)

        # Verify - 5 events total: 2 + 2 + 1
        assert events_added == 5

        # Parse the calendar to verify events
        with open(tmp_path, encoding="utf-8") as f:
            calendar_content = f.read()
        calendar = Calendar(calendar_content)
        assert len(calendar.events) == 5

        # Group events by date
        events_by_date = {}
        for event in calendar.events:
            date_key = event.begin.date()
            if date_key not in events_by_date:
                events_by_date[date_key] = []
            events_by_date[date_key].append(event)

        # June 2: Should have 2 separate events
        june_2_events = events_by_date[datetime(2025, 6, 2).date()]
        assert len(june_2_events) == 2
        june_2_names = [event.name for event in june_2_events]
        assert any("Organesch Ressourcen" in name for name in june_2_names)
        assert any("Gréngschtëtsammlung" in name for name in june_2_names)

        # June 5: Should have 2 separate events
        june_5_events = events_by_date[datetime(2025, 6, 5).date()]
        assert len(june_5_events) == 2
        june_5_names = [event.name for event in june_5_events]
        assert any("Pabeier a Kartong" in name for name in june_5_names)
        assert any("Problemoffäll" in name for name in june_5_names)

        # June 10: Should have 1 event
        june_10_events = events_by_date[datetime(2025, 6, 10).date()]
        assert len(june_10_events) == 1
        assert "Single Type" in june_10_events[0].name

    finally:
        # Clean up
        Path(tmp_path).unlink(missing_ok=True)


def test_extract_language_from_waste_description_german():
    """Test extracting German/Luxembourgish text."""
    description = "Reschtoffäll | Déchets ménagers | Residual waste"
    result = extract_language_from_waste_description(description, "de")
    assert result == "Reschtoffäll"


def test_extract_language_from_waste_description_french():
    """Test extracting French text."""
    description = "Pabeier a Kartong | Papier et carton | Paper and carton"
    result = extract_language_from_waste_description(description, "fr")
    assert result == "Papier et carton"


def test_extract_language_from_waste_description_english():
    """Test extracting English text."""
    description = "Glas | Verre | Glass"
    result = extract_language_from_waste_description(description, "en")
    assert result == "Glass"


def test_extract_language_from_waste_description_fallback():
    """Test fallback to first part when language not found."""
    description = "Unknown term | Other term"
    result = extract_language_from_waste_description(description, "de")
    assert result == "Unknown term"


def test_extract_language_from_waste_description_single_part():
    """Test with single part description."""
    description = "Reschtoffäll"
    result = extract_language_from_waste_description(description, "de")
    assert result == "Reschtoffäll"


def test_extract_language_from_waste_description_valorlux_packaging():
    """Test VALORLUX packaging recognition."""
    description = "Verpackungen | (VALORLUX) | Packaging"
    result = extract_language_from_waste_description(description, "en")
    assert result == "Packaging"


def test_extract_language_from_waste_description_christmas_trees():
    """Test Christmas trees in German."""
    description = "Beemercher | Sapins de Noël | Christmas trees"
    result = extract_language_from_waste_description(description, "de")
    assert result == "Beemercher"


def test_extract_language_from_waste_description_old_clothes():
    """Test old clothes in French."""
    description = "Aalt Gezei | Vieux vêtements | Old clothes"
    result = extract_language_from_waste_description(description, "fr")
    assert result == "Vieux vêtements"


@pytest.mark.parametrize(
    "waste_type,expected_icon",
    [
        ("Reschtoffäll", "🗑️"),
        ("Déchets ménagers", "🗑️"),
        ("Residual waste", "🗑️"),
        ("Pabeier a Kartong", "📄"),
        ("Papier et carton", "📄"),
        ("Paper and carton", "📄"),
        ("Glas", "🪟"),
        ("Verre", "🪟"),
        ("Glass", "🪟"),
        ("(VALORLUX)", "📦"),
        ("Packaging", "📦"),
        ("Emballages", "📦"),
        ("Organesch Ressourcen", "🌱"),
        ("Ressources organiques", "🌱"),
        ("Aalt Gezei", "👕"),
        ("Vieux vêtements", "👕"),
        ("Old clothes", "👕"),
        ("Beemercher", "🎄"),
        ("Sapins de Noël", "🎄"),
        ("Christmas trees", "🎄"),
        ("Unknown waste type", "♻️"),
    ],
)
def test_get_waste_type_icon(waste_type, expected_icon):
    """Test icon mapping for various waste types."""
    assert get_waste_type_icon(waste_type) == expected_icon
