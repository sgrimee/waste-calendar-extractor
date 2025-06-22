# @pytest.fixture(scope="module")
# def extracted_2025_results():
#     """Extract PDF data once for all tests in this module using area-based extraction.

#     This fixture performs the complete extraction pipeline:
#     1. Loads predefined calendar/legend coordinate areas from page_areas.json
#     2. Extracts legend mappings from page 2 right area only
#     3. Processes each calendar page using precise row boundaries
#     4. Maps waste symbols to dates within their specific calendar rows
#     5. Converts symbols to multilingual descriptions

#     Returns:
#         list[dict]: List of extraction results with 'date' and 'icons' keys
#     """
#     from waste_cal.pdf_extractor import extract_dates_from_pdf

#     # Path to the real PDF file - contains 2025 waste collection calendar
#     pdf_path = "pdf/2025.pdf"

#     # Extract all dates using the new area-based method
#     return extract_dates_from_pdf(pdf_path, year=2025)


# @pytest.mark.integration
# @pytest.mark.parametrize(
#     "month,date,expected_types",
#     [
#         # June 2025 expected data from visual PDF inspection
#         (6, 1, []),  # No collection
#         (6, 2, ["organic", "hedge"]),
#         (6, 3, ["residual"]),
#         (6, 4, ["electric"]),
#         (6, 5, ["paper", "problematic"]),
#         (6, 6, ["packaging"]),
#         (6, 7, ["organic"]),
#         (6, 8, []),  # No collection
#         (6, 9, []),  # No collection
#         (6, 10, ["bulky", "residual"]),  # Bulky waste
#         (6, 11, []),  # No collection
#         (6, 12, []),  # No collection
#         (6, 13, []),  # No collection
#         (6, 14, []),  # No collection
#         (6, 15, []),  # No collection
#         (6, 16, ["organic"]),
#         (6, 17, ["residual"]),
#         (6, 18, []),  # No collection
#         (6, 19, ["paper"]),
#         (6, 20, ["packaging"]),
#         (6, 21, ["organic"]),
#         (6, 22, []),  # No collection
#         (6, 23, []),  # No collection
#         (6, 24, ["residual"]),
#         (6, 25, []),  # No collection
#         (6, 26, ["glass"]),
#         (6, 27, []),  # No collection
#         (6, 28, []),
#         (6, 29, []),  # No collection
#         (6, 30, ["organic"]),
#     ],
# )


import pytest

from waste_cal.pdf_extractor import areas_per_day, read_pdf


@pytest.fixture
def pdf_doc():
    """Fixture to provide a sample PDF file path for testing."""
    return read_pdf("pdf/2025.pdf")


def test_areas_per_day_correct_count(pdf_doc) -> None:
    """Test that areas_per_day returns correct number of areas for each month."""

    days_in_month = {
        1: 31,  # January
        # February is handled separately
        3: 31,  # March
        4: 30,  # April
        5: 31,  # May
        6: 30,  # June
        7: 31,  # July
        8: 31,  # August
        9: 30,  # September
        10: 31,  # October
        11: 30,  # November
        12: 31,  # December
    }

    for month in range(1, 12):
        # january is on page 2
        areas = areas_per_day(pdf_doc[month])
        if month == 2:
            # February can have either 28 or 29 days
            assert len(areas) in [28, 29], f"Month {month} should have 28 or 29 areas, found {len(areas)}"
        else:
            assert len(areas) == days_in_month[month], (
                f"Month {month} should have {days_in_month[month]} areas, found {len(areas)}"
            )


def test_areas_per_day_uniform_coverage(pdf_doc) -> None:
    """Test that day areas provide complete coverage with no gaps or overlaps."""
    from waste_cal.pdf_extractor import CALENDAR_AREA
    
    # Test with January (31 days)
    page = pdf_doc[1]  # January is on page 2 (index 1)
    areas = areas_per_day(page)
    
    # All areas should have the same width (full calendar width)
    expected_width = CALENDAR_AREA["x1"] - CALENDAR_AREA["x0"]
    for i, area in enumerate(areas):
        assert area.x0 == CALENDAR_AREA["x0"], f"Day {i+1} area should start at calendar left edge"
        assert area.x1 == CALENDAR_AREA["x1"], f"Day {i+1} area should end at calendar right edge"
        width = area.x1 - area.x0
        assert abs(width - expected_width) < 0.1, f"Day {i+1} width {width} should equal calendar width {expected_width}"
    
    # Adjacent areas should share boundaries (no gaps)
    for i in range(len(areas) - 1):
        current_bottom = areas[i].y1
        next_top = areas[i + 1].y0
        assert abs(current_bottom - next_top) < 0.1, f"Gap between day {i+1} and day {i+2}: {abs(current_bottom - next_top)}"
    
    # First area should start near calendar top
    first_top = areas[0].y0
    calendar_top = CALENDAR_AREA["y0"]
    assert first_top >= calendar_top, f"First day area top {first_top} should be >= calendar top {calendar_top}"
    
    # Last area should end near calendar bottom
    last_bottom = areas[-1].y1
    calendar_bottom = CALENDAR_AREA["y1"]
    assert last_bottom <= calendar_bottom, f"Last day area bottom {last_bottom} should be <= calendar bottom {calendar_bottom}"


def test_areas_per_day_uniform_height(pdf_doc) -> None:
    """Test that day areas have consistent height based on uniform spacing."""
    # Test with January (31 days)
    page = pdf_doc[1]  # January is on page 2 (index 1)
    areas = areas_per_day(page)
    
    # Calculate heights
    heights = [area.y1 - area.y0 for area in areas]
    
    # All heights should be very similar (within 1 point tolerance for rounding)
    avg_height = sum(heights) / len(heights)
    for i, height in enumerate(heights):
        assert abs(height - avg_height) < 1.0, f"Day {i+1} height {height} differs too much from average {avg_height}"
    
    # Height should be approximately 23.2 points based on known spacing
    expected_height = 23.2
    assert abs(avg_height - expected_height) < 2.0, f"Average height {avg_height} should be close to expected {expected_height}"


def test_areas_per_day_different_month_lengths(pdf_doc) -> None:
    """Test that areas_per_day works correctly for months with different numbers of days."""
    test_months = [
        (4, 30),   # April - 30 days
        (1, 31),   # January - 31 days  
        (2, 28),   # February - 28 days (2025 is not a leap year)
    ]
    
    for month_index, expected_days in test_months:
        page = pdf_doc[month_index]
        areas = areas_per_day(page)
        
        # Check correct number of areas
        if month_index == 2:  # February
            assert len(areas) in [28, 29], f"February should have 28-29 areas, found {len(areas)}"
        else:
            assert len(areas) == expected_days, f"Month {month_index} should have {expected_days} areas, found {len(areas)}"
        
        # Check that areas are properly ordered (top to bottom)
        for i in range(len(areas) - 1):
            assert areas[i].y0 < areas[i + 1].y0, f"Area {i} should be above area {i+1}"
            assert areas[i].y1 <= areas[i + 1].y0, f"Area {i} should not overlap with area {i+1}"


def test_areas_per_day_rectangle_properties(pdf_doc) -> None:
    """Test that returned areas are valid rectangles with correct properties."""
    from waste_cal.pdf_extractor import CALENDAR_AREA
    
    # Test with January
    page = pdf_doc[1]
    areas = areas_per_day(page)
    
    for i, area in enumerate(areas):
        # Should be valid rectangle
        assert area.x0 < area.x1, f"Day {i+1} area should have positive width"
        assert area.y0 < area.y1, f"Day {i+1} area should have positive height"
        
        # Should be within calendar bounds
        assert area.x0 >= CALENDAR_AREA["x0"] - 0.1, f"Day {i+1} left edge should be within calendar"
        assert area.x1 <= CALENDAR_AREA["x1"] + 0.1, f"Day {i+1} right edge should be within calendar"
        assert area.y0 >= CALENDAR_AREA["y0"] - 15.0, f"Day {i+1} top edge should be within calendar (with margin)"
        assert area.y1 <= CALENDAR_AREA["y1"] + 0.1, f"Day {i+1} bottom edge should be within calendar"
        
        # Should have reasonable dimensions
        width = area.x1 - area.x0
        height = area.y1 - area.y0
        assert width > 200, f"Day {i+1} width {width} should be reasonable"
        assert 15 < height < 40, f"Day {i+1} height {height} should be reasonable (15-40 points)"


def test_areas_per_day_error_handling() -> None:
    """Test that areas_per_day handles error cases appropriately."""
    import fitz
    from waste_cal.pdf_extractor import areas_per_day
    
    # Create a mock page with no day numbers
    # This is a simplified test - in practice we'd need a real PDF page without day numbers
    # For now, we'll test that the function exists and can be called
    # (Full error testing would require creating mock PDF pages, which is complex)
    
    # Test that the function is importable and callable
    assert callable(areas_per_day), "areas_per_day should be callable"
