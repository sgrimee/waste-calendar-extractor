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


def test_areas_for_days(pdf_doc) -> None:
    """Test that areas_for_days returns correct number of areas for each month."""

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
