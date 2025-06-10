#!/usr/bin/env python3
"""
Integration tests and extraction tests with given output.
"""

import os
import sys
import tempfile
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
        (6, 5, ["paper", "problematic"]),
        (6, 6, ["packaging"]),
        (6, 7, ["organic"]),
        (6, 8, []),  # No collection
        (6, 9, []),  # No collection
    ],
)
def test_2025_expected_dates(month, date, expected_types):
    """Test that the correct dates are extracted for specific months in 2025 using real PDF extraction."""
    from waste_calendar_extractor.calendar_processor import extract_dates_from_pdf

    # Path to the real PDF file
    pdf_path = "pdf/2025.pdf"

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
        "problematic": ["problematic", "problematesch", "problématique", "problemoff"],
        "packaging": ["packaging", "verpack", "emballage", "valorlux"],
        "special": ["special", "pluschtier", "speziell", "spécial"],
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


@pytest.mark.integration
def test_pdf_download_from_direct_url():
    """Test PDF download functionality using the known working direct URL."""
    from waste_calendar_extractor.output_generator import download_calendar_pdf

    # Use a temporary file for the download
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        temp_path = temp_file.name

    try:
        # Test download from the known working direct PDF URL
        direct_pdf_url = "https://www.niederanven.lu/media/aefb09c8-9716-4141-bee0-1c2ac3a7557b/ressourcekalenner-nidderaanwen-web.pdf"
        success = download_calendar_pdf(direct_pdf_url, temp_path)

        assert success, "PDF download should succeed from direct URL"

        # Verify the file exists and is not empty
        assert os.path.exists(temp_path), "Downloaded file should exist"
        assert os.path.getsize(temp_path) > 0, "Downloaded file should not be empty"

        # Verify it's actually a PDF file
        with open(temp_path, "rb") as f:
            header = f.read(4)
            assert header == b"%PDF", f"Downloaded file should be a valid PDF, but header is {header}"

        # Verify the file has reasonable size (should be several hundred KB)
        file_size = os.path.getsize(temp_path)
        assert file_size > 100000, f"PDF file seems too small ({file_size} bytes), might be corrupted"
        assert file_size < 10000000, f"PDF file seems too large ({file_size} bytes), might be wrong file"

    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@pytest.mark.integration
def test_pdf_download_with_fallback_strategy():
    """Test PDF download functionality using the fallback strategy from webpage scraping."""
    from waste_calendar_extractor.output_generator import download_calendar_pdf

    # Use a temporary file for the download
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        temp_path = temp_file.name

    try:
        # Test download from the main waste management page (should trigger scraping and fallback)
        website_url = "https://www.niederanven.lu/en/environment/waste-disposal-management"
        success = download_calendar_pdf(website_url, temp_path)

        assert success, "PDF download should succeed using fallback strategy"

        # Verify the file exists and is valid
        assert os.path.exists(temp_path), "Downloaded file should exist"
        assert os.path.getsize(temp_path) > 0, "Downloaded file should not be empty"

        # Verify it's actually a PDF file
        with open(temp_path, "rb") as f:
            header = f.read(4)
            assert header == b"%PDF", f"Downloaded file should be a valid PDF, but header is {header}"

        # Verify the file has reasonable size
        file_size = os.path.getsize(temp_path)
        assert file_size > 100000, f"PDF file seems too small ({file_size} bytes)"

    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@pytest.mark.integration
def test_pdf_download_failure_handling():
    """Test PDF download failure handling with invalid URLs."""
    from waste_calendar_extractor.output_generator import download_calendar_pdf

    # Use a temporary file for the download attempt
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        temp_path = temp_file.name

    try:
        # Test with completely invalid URL
        invalid_url = "https://invalid-domain-that-does-not-exist.com/nonexistent.pdf"
        success = download_calendar_pdf(invalid_url, temp_path)

        assert not success, "PDF download should fail for invalid URL"

        # Test with valid domain but non-existent PDF
        nonexistent_pdf = "https://www.google.com/nonexistent-file.pdf"
        success = download_calendar_pdf(nonexistent_pdf, temp_path)

        assert not success, "PDF download should fail for non-existent PDF"

    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


@pytest.mark.integration
def test_find_pdf_links_from_webpage():
    """Test the PDF link finding functionality on real websites."""
    from waste_calendar_extractor.output_generator import find_pdf_links_from_webpage

    # Test with a website that should have PDF links (using a test site with known PDFs)
    test_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/"
    pdf_links = find_pdf_links_from_webpage(test_url)

    # This test site should have some PDF files
    assert isinstance(pdf_links, list), "Should return a list of PDF links"

    # Test with Niederanven website (even if scraping fails, function should handle gracefully)
    niederanven_url = "https://www.niederanven.lu/en/environment/waste-disposal-management"
    niederanven_links = find_pdf_links_from_webpage(niederanven_url)

    assert isinstance(niederanven_links, list), "Should return a list even if scraping fails"
    # Note: May be empty if website blocks scraping, but function should not crash

    # Test with invalid URL - should return empty list and not crash
    invalid_url = "https://invalid-domain-that-does-not-exist.com"
    invalid_links = find_pdf_links_from_webpage(invalid_url)

    assert isinstance(invalid_links, list), "Should return empty list for invalid URLs"
    assert len(invalid_links) == 0, "Should return empty list for invalid URLs"

    # Test with non-HTML content (like a direct PDF)
    direct_pdf_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    direct_pdf_links = find_pdf_links_from_webpage(direct_pdf_url)

    assert isinstance(direct_pdf_links, list), "Should handle direct PDF URLs gracefully"
    # Should return empty list since it's not an HTML page with links


@pytest.mark.integration
def test_find_pdf_links_patterns():
    """Test PDF link pattern matching with real Niederanven website."""
    from waste_calendar_extractor.output_generator import find_pdf_links_from_webpage

    # Test with real Niederanven website pages that might contain PDF links
    test_urls = [
        "https://www.niederanven.lu/en/environment/waste-disposal-management",
        "https://www.niederanven.lu/fr/environnement/gestion-des-dechets",
        "https://www.niederanven.lu/lb/ëmwelt/offallverwaltung",
    ]

    for url in test_urls:
        pdf_links = find_pdf_links_from_webpage(url)

        # Should always return a list, even if empty (due to scraping restrictions)
        assert isinstance(pdf_links, list), f"Should return a list for {url}"

        # If links are found, they should be valid URLs
        for link in pdf_links:
            assert isinstance(link, str), "PDF links should be strings"
            assert link.startswith("http"), f"PDF link should be absolute URL: {link}"
            assert ".pdf" in link.lower(), f"Link should contain .pdf: {link}"

        # If we found links, check for Niederanven-specific patterns
        if pdf_links:
            # Look for ressourcekalenner or related waste calendar patterns
            relevant_links = [
                link
                for link in pdf_links
                if any(
                    pattern in link.lower() for pattern in ["ressource", "calendar", "waste", "offal", "nidderaanwen"]
                )
            ]

            # If we found relevant links, log them for debugging
            if relevant_links:
                print(f"Found relevant PDF links from {url}: {relevant_links}")

    # Test that the function handles the main website gracefully
    main_site_url = "https://www.niederanven.lu"
    main_site_links = find_pdf_links_from_webpage(main_site_url)
    assert isinstance(main_site_links, list), "Should handle main site gracefully"
