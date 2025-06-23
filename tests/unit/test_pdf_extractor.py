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


from unittest.mock import Mock, patch

import fitz
import pytest

from waste_cal.pdf_extractor import (
    _calculate_day_spacing,
    _calculate_grid_lines,
    _extract_day_positions,
    _generate_day_areas,
    areas_per_day,
    drawing_info,
    is_drawing_in_box,
    read_pdf,
    render_drawing_to_image,
)


@pytest.fixture
def pdf_doc():
    """Fixture to provide a sample PDF file path for testing."""
    return read_pdf("pdf/2025.pdf")


@pytest.mark.integration
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


@pytest.mark.integration
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
        assert abs(width - expected_width) < 0.1, (
            f"Day {i+1} width {width} should equal calendar width {expected_width}"
        )

    # Adjacent areas should share boundaries (no gaps)
    for i in range(len(areas) - 1):
        current_bottom = areas[i].y1
        next_top = areas[i + 1].y0
        assert abs(current_bottom - next_top) < 0.1, (
            f"Gap between day {i+1} and day {i+2}: {abs(current_bottom - next_top)}"
        )

    # First area should start near calendar top
    first_top = areas[0].y0
    calendar_top = CALENDAR_AREA["y0"]
    assert first_top >= calendar_top, f"First day area top {first_top} should be >= calendar top {calendar_top}"

    # Last area should end near calendar bottom
    last_bottom = areas[-1].y1
    calendar_bottom = CALENDAR_AREA["y1"]
    assert last_bottom <= calendar_bottom, (
        f"Last day area bottom {last_bottom} should be <= calendar bottom {calendar_bottom}"
    )


@pytest.mark.integration
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
    assert abs(avg_height - expected_height) < 2.0, (
        f"Average height {avg_height} should be close to expected {expected_height}"
    )


@pytest.mark.integration
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
            assert len(areas) == expected_days, (
                f"Month {month_index} should have {expected_days} areas, found {len(areas)}"
            )

        # Check that areas are properly ordered (top to bottom)
        for i in range(len(areas) - 1):
            assert areas[i].y0 < areas[i + 1].y0, f"Area {i} should be above area {i+1}"
            assert areas[i].y1 <= areas[i + 1].y0, f"Area {i} should not overlap with area {i+1}"


@pytest.mark.integration
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
    from waste_cal.pdf_extractor import areas_per_day

    # Create a mock page with no day numbers
    # This is a simplified test - in practice we'd need a real PDF page without day numbers
    # For now, we'll test that the function exists and can be called
    # (Full error testing would require creating mock PDF pages, which is complex)

    # Test that the function is importable and callable
    assert callable(areas_per_day), "areas_per_day should be callable"


class TestReadPdf:
    """Test read_pdf function."""

    @pytest.mark.integration
    def test_read_pdf_success(self):
        """Test that read_pdf successfully opens a valid PDF file."""
        # This test uses the real PDF file - marked as integration test
        pdf_path = "pdf/2025.pdf"
        doc = read_pdf(pdf_path)

        assert isinstance(doc, fitz.Document)
        assert doc.page_count > 0
        doc.close()

    def test_read_pdf_nonexistent_file(self):
        """Test that read_pdf raises appropriate error for nonexistent file."""
        with pytest.raises(ValueError, match="Could not read PDF file"):
            read_pdf("nonexistent/file.pdf")

    @patch('fitz.open')
    def test_read_pdf_invalid_file(self, mock_fitz_open):
        """Test that read_pdf raises appropriate error for invalid file."""
        # Mock fitz.open to raise an exception as if the file is invalid
        mock_fitz_open.side_effect = Exception("Invalid PDF file")

        with pytest.raises(ValueError, match="Could not read PDF file"):
            read_pdf("invalid.pdf")


class TestExtractDayPositions:
    """Test _extract_day_positions function."""

    def test_extract_day_positions_with_mock_page(self):
        """Test _extract_day_positions with mock page data."""
        # Create mock page with text data
        mock_page = Mock()
        mock_text_dict = {
            "blocks": [
                {
                    "lines": [
                        {
                            "spans": [
                                {
                                    "text": "1",
                                    "bbox": [50, 100, 60, 110]  # x0, y0, x1, y1
                                },
                                {
                                    "text": "2",
                                    "bbox": [50, 125, 60, 135]
                                },
                                {
                                    "text": "not_a_day",
                                    "bbox": [50, 150, 60, 160]
                                }
                            ]
                        }
                    ]
                },
                {
                    "lines": [
                        {
                            "spans": [
                                {
                                    "text": "3",
                                    "bbox": [50, 175, 60, 185]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        mock_page.get_text.return_value = mock_text_dict

        positions = _extract_day_positions(mock_page)

        assert len(positions) == 3
        assert positions[0]["day"] == 1
        assert positions[1]["day"] == 2
        assert positions[2]["day"] == 3

        # Check position calculations
        assert positions[0]["y_top"] == 100
        assert positions[0]["y_bottom"] == 110
        assert positions[0]["y_center"] == 105

    def test_extract_day_positions_no_days_found(self):
        """Test _extract_day_positions when no day numbers are found."""
        mock_page = Mock()
        mock_text_dict = {
            "blocks": [
                {
                    "lines": [
                        {
                            "spans": [
                                {"text": "No days here", "bbox": [50, 100, 60, 110]},
                                {"text": "Just text", "bbox": [50, 125, 60, 135]}
                            ]
                        }
                    ]
                }
            ]
        }
        mock_page.get_text.return_value = mock_text_dict

        with pytest.raises(ValueError, match="No day numbers found in the calendar area"):
            _extract_day_positions(mock_page)

    def test_extract_day_positions_filters_invalid_days(self):
        """Test that _extract_day_positions filters out invalid day numbers."""
        mock_page = Mock()
        mock_text_dict = {
            "blocks": [
                {
                    "lines": [
                        {
                            "spans": [
                                {"text": "0", "bbox": [50, 100, 60, 110]},  # Invalid (too low)
                                {"text": "1", "bbox": [50, 125, 60, 135]},  # Valid
                                {"text": "32", "bbox": [50, 150, 60, 160]},  # Invalid (too high)
                                {"text": "15", "bbox": [50, 175, 60, 185]}  # Valid
                            ]
                        }
                    ]
                }
            ]
        }
        mock_page.get_text.return_value = mock_text_dict

        positions = _extract_day_positions(mock_page)

        assert len(positions) == 2
        assert positions[0]["day"] == 1
        assert positions[1]["day"] == 15


class TestCalculateDaySpacing:
    """Test _calculate_day_spacing function."""

    def test_calculate_day_spacing_multiple_days(self):
        """Test spacing calculation with multiple days."""
        day_positions = [
            {"day": 1, "y_center": 100.0},
            {"day": 2, "y_center": 125.0},
            {"day": 3, "y_center": 150.0},
            {"day": 4, "y_center": 175.0}
        ]

        spacing = _calculate_day_spacing(day_positions)

        # Expected: (25 + 25 + 25) / 3 = 25
        assert spacing == 25.0

    def test_calculate_day_spacing_two_days(self):
        """Test spacing calculation with two days."""
        day_positions = [
            {"day": 1, "y_center": 100.0},
            {"day": 2, "y_center": 130.0}
        ]

        spacing = _calculate_day_spacing(day_positions)
        assert spacing == 30.0

    def test_calculate_day_spacing_single_day(self):
        """Test spacing calculation with single day returns default."""
        day_positions = [{"day": 1, "y_center": 100.0}]

        spacing = _calculate_day_spacing(day_positions)
        assert spacing == 23.2  # Default value

    def test_calculate_day_spacing_empty_list(self):
        """Test spacing calculation with empty list returns default."""
        day_positions = []

        spacing = _calculate_day_spacing(day_positions)
        assert spacing == 23.2  # Default value


class TestCalculateGridLines:
    """Test _calculate_grid_lines function."""

    def test_calculate_grid_lines_basic(self):
        """Test grid line calculation with basic day positions."""
        day_positions = [
            {"day": 1, "y_center": 100.0},
            {"day": 2, "y_center": 125.0},
            {"day": 3, "y_center": 150.0}
        ]
        spacing = 25.0

        grid_lines = _calculate_grid_lines(day_positions, spacing)

        # Expected grid lines:
        # Line 0: 100 - 25/2 = 87.5 (above day 1)
        # Line 1: (100 + 125) / 2 = 112.5 (between days 1 and 2)
        # Line 2: (125 + 150) / 2 = 137.5 (between days 2 and 3)
        # Line 3: 150 + 25/2 = 162.5 (below day 3)

        expected = [87.5, 112.5, 137.5, 162.5]
        assert grid_lines == expected

    def test_calculate_grid_lines_single_day(self):
        """Test grid line calculation with single day."""
        day_positions = [{"day": 1, "y_center": 100.0}]
        spacing = 25.0

        grid_lines = _calculate_grid_lines(day_positions, spacing)

        expected = [87.5, 112.5]  # Above and below the single day
        assert grid_lines == expected


class TestGenerateDayAreas:
    """Test _generate_day_areas function."""

    def test_generate_day_areas_basic(self):
        """Test day area generation with basic inputs."""
        day_positions = [
            {"day": 1, "y_center": 100.0},
            {"day": 2, "y_center": 125.0}
        ]
        grid_lines = [87.5, 112.5, 137.5]

        areas = _generate_day_areas(day_positions, grid_lines)

        assert len(areas) == 2

        # Check first area
        area1 = areas[0]
        assert area1.y0 == 87.5
        assert area1.y1 == 112.5

        # Check second area
        area2 = areas[1]
        assert area2.y0 == 112.5
        assert area2.y1 == 137.5

        # Both areas should span full calendar width
        from waste_cal.pdf_extractor import CALENDAR_AREA
        for area in areas:
            assert area.x0 == CALENDAR_AREA["x0"]
            assert area.x1 == CALENDAR_AREA["x1"]


class TestIsDrawingInBox:
    """Test is_drawing_in_box function."""

    def test_is_drawing_in_box_contained(self):
        """Test drawing that is completely contained in box."""
        drawing = {"rect": fitz.Rect(10, 10, 20, 20)}
        box = fitz.Rect(5, 5, 25, 25)

        result = is_drawing_in_box(drawing, box)
        assert result is True

    def test_is_drawing_in_box_not_contained(self):
        """Test drawing that extends outside box."""
        drawing = {"rect": fitz.Rect(10, 10, 30, 30)}
        box = fitz.Rect(5, 5, 25, 25)

        result = is_drawing_in_box(drawing, box)
        assert result is False

    def test_is_drawing_in_box_no_rect(self):
        """Test drawing without rect information."""
        drawing = {"type": "some_drawing"}
        box = fitz.Rect(5, 5, 25, 25)

        result = is_drawing_in_box(drawing, box)
        assert result is False

    def test_is_drawing_in_box_edge_case_exact_fit(self):
        """Test drawing that exactly fits the box."""
        drawing = {"rect": fitz.Rect(5, 5, 25, 25)}
        box = fitz.Rect(5, 5, 25, 25)

        result = is_drawing_in_box(drawing, box)
        assert result is True


class TestDrawingInfo:
    """Test drawing_info function."""

    def test_drawing_info_basic(self):
        """Test drawing_info with basic drawing data."""
        drawing = {
            "type": "path",
            "rect": fitz.Rect(10, 20, 30, 40),
            "fill": "red",
            "stroke": "black",
            "width": 2,
            "items": []
        }

        info = drawing_info(drawing)

        assert "Type: path" in info
        assert "Position: (10.0, 20.0) to (30.0, 40.0)" in info
        assert "Size: 20.0 x 20.0" in info
        assert "Fill: red" in info
        assert "Stroke: black" in info
        assert "Width: 2" in info
        assert "Items count: 0" in info

    def test_drawing_info_with_items(self):
        """Test drawing_info with items."""
        drawing = {
            "type": "path",
            "items": [
                ("line", 10, 20, 30, 40),
                ("curve", 50, 60)
            ]
        }

        info = drawing_info(drawing)

        assert "Items count: 2" in info
        assert "Item 0: line (tuple with 5 elements)" in info
        assert "Item 1: curve (tuple with 3 elements)" in info

    def test_drawing_info_missing_fields(self):
        """Test drawing_info with missing fields."""
        drawing = {}

        info = drawing_info(drawing)

        assert "Type: unknown" in info
        assert "Fill: None" in info
        assert "Stroke: None" in info
        assert "Width: 0" in info
        assert "Items count: 0" in info


class TestRenderDrawingToImage:
    """Test render_drawing_to_image function."""

    def test_render_drawing_to_image_no_rect(self, capsys):
        """Test rendering drawing without rect information."""
        mock_page = Mock()
        drawing = {"type": "some_drawing"}

        render_drawing_to_image(mock_page, drawing, "test_output.png")

        captured = capsys.readouterr()
        assert "Warning: Drawing has no rect information" in captured.out

    @patch('fitz.Matrix')
    @patch('builtins.print')
    def test_render_drawing_to_image_success(self, mock_print, mock_matrix):
        """Test successful rendering of drawing to image."""
        mock_page = Mock()
        mock_pixmap = Mock()
        mock_pixmap.width = 100
        mock_pixmap.height = 200
        mock_page.get_pixmap.return_value = mock_pixmap

        drawing = {"rect": fitz.Rect(10, 20, 30, 40)}
        output_path = "test_output.png"

        render_drawing_to_image(mock_page, drawing, output_path)

        # Verify the page.get_pixmap was called with correct parameters
        mock_page.get_pixmap.assert_called_once()
        mock_pixmap.save.assert_called_once_with(output_path)
