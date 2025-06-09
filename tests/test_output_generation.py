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
    # Test data
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

        # Verify
        assert events_added == 2

        # Verify file contents by parsing it back
        with open(tmp_path, "r", encoding="utf-8") as f:
            calendar_content = f.read()

        # Parse the calendar to verify events were added
        calendar = Calendar(calendar_content)
        assert len(calendar.events) == 2

        # Verify event details
        events = list(calendar.events)
        assert any("Residual waste" in event.name for event in events)
        assert any("Paper | Carton" in event.name for event in events)

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
        with open(tmp_path, "r", encoding="utf-8") as f:
            calendar_content = f.read()

        calendar = Calendar(calendar_content)
        assert len(calendar.events) == 0

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