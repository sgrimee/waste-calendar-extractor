"""Unit tests for drawing analysis module."""

from unittest.mock import Mock

import pytest

from waste_cal.drawing import detect_waste_type_from_drawing
from waste_cal.waste_types import WasteType


class TestDetectWasteTypeFromDrawing:
    """Test waste type detection from drawing objects."""

    def create_mock_drawing(self, fill_color, width, height, item_count, first_item_type="l"):
        """Create a mock drawing object for testing."""
        mock_drawing = Mock()
        mock_drawing.get.side_effect = lambda key, default=None: {
            "fill": fill_color,
            "rect": Mock(width=width, height=height),
            "items": [(first_item_type, "mock_data")] * item_count,
        }.get(key, default)
        return mock_drawing

    def test_detect_paper_waste_type(self):
        """Test detection of PAPER waste type."""
        drawing = self.create_mock_drawing(
            fill_color=(0.327, 0.757, 0.939), width=7.7, height=13.2, item_count=4, first_item_type="l"
        )

        result = detect_waste_type_from_drawing(drawing)
        assert result == WasteType.PAPER

    def test_detect_packaging_waste_type(self):
        """Test detection of PACKAGING waste type."""
        drawing = self.create_mock_drawing(
            fill_color=(0.729, 0.884, 0.977), width=10.2, height=10.6, item_count=23, first_item_type="c"
        )

        result = detect_waste_type_from_drawing(drawing)
        assert result == WasteType.PACKAGING

    def test_detect_organic_waste_type(self):
        """Test detection of ORGANIC waste type."""
        drawing = self.create_mock_drawing(
            fill_color=(0.201, 0.570, 0.252), width=7.7, height=13.2, item_count=4, first_item_type="l"
        )

        result = detect_waste_type_from_drawing(drawing)
        assert result == WasteType.ORGANIC

    def test_detect_residual_waste_type(self):
        """Test detection of RESIDUAL waste type."""
        drawing = self.create_mock_drawing(
            fill_color=(0.343, 0.341, 0.339), width=7.7, height=13.2, item_count=4, first_item_type="l"
        )

        result = detect_waste_type_from_drawing(drawing)
        assert result == WasteType.RESIDUAL

    def test_detect_electric_waste_type(self):
        """Test detection of ELECTRIC waste type."""
        drawing = self.create_mock_drawing(
            fill_color=(0.114, 0.116, 0.111), width=12.4, height=15.9, item_count=34, first_item_type="l"
        )

        result = detect_waste_type_from_drawing(drawing)
        assert result == WasteType.ELECTRIC

    def test_detect_christmas_trees_waste_type(self):
        """Test detection of CHRISTMAS_TREES waste type."""
        drawing = self.create_mock_drawing(
            fill_color=(0.201, 0.570, 0.252), width=11.6, height=15.1, item_count=34, first_item_type="l"
        )

        result = detect_waste_type_from_drawing(drawing)
        assert result == WasteType.CHRISTMAS_TREES

    def test_detect_bulky_waste_type(self):
        """Test detection of BULKY waste type."""
        drawing = self.create_mock_drawing(
            fill_color=(0.585, 0.418, 0.264), width=10.4, height=5.8, item_count=12, first_item_type="l"
        )

        result = detect_waste_type_from_drawing(drawing)
        assert result == WasteType.BULKY

    def test_detect_glass_waste_type(self):
        """Test detection of GLASS waste type."""
        drawing = self.create_mock_drawing(
            fill_color=(0.985, 0.736, 0.201), width=7.7, height=13.2, item_count=4, first_item_type="l"
        )

        result = detect_waste_type_from_drawing(drawing)
        assert result == WasteType.GLASS

    def test_detect_hedge_waste_type(self):
        """Test detection of HEDGE waste type."""
        drawing = self.create_mock_drawing(
            fill_color=(0.585, 0.418, 0.264), width=12.2, height=12.2, item_count=56, first_item_type="c"
        )

        result = detect_waste_type_from_drawing(drawing)
        assert result == WasteType.HEDGE

    def test_detect_problematic_waste_type(self):
        """Test detection of PROBLEMATIC waste type."""
        drawing = self.create_mock_drawing(
            fill_color=(0.385, 0.632, 0.261), width=11.8, height=15.7, item_count=392, first_item_type="c"
        )

        result = detect_waste_type_from_drawing(drawing)
        assert result == WasteType.PROBLEMATIC

    def test_detect_clothers_waste_type(self):
        """Test detection of CLOTHERS waste type."""
        drawing = self.create_mock_drawing(
            fill_color=(0.939, 0.490, 0.000), width=14.7, height=6.0, item_count=9, first_item_type="l"
        )

        result = detect_waste_type_from_drawing(drawing)
        assert result == WasteType.CLOTHERS

    def test_no_match_returns_none(self):
        """Test that unrecognized drawings return None."""
        drawing = self.create_mock_drawing(
            fill_color=(0.5, 0.5, 0.5),  # Gray color not in training data
            width=20.0,
            height=20.0,
            item_count=5,
            first_item_type="unknown",
        )

        result = detect_waste_type_from_drawing(drawing)
        assert result is None

    def test_missing_fill_returns_none(self):
        """Test that drawings without fill color return None."""
        mock_drawing = Mock()
        mock_drawing.get.side_effect = lambda key, default=None: {
            "fill": None,
            "rect": Mock(width=10.0, height=10.0),
            "items": [("l", "data")],
        }.get(key, default)

        result = detect_waste_type_from_drawing(mock_drawing)
        assert result is None

    def test_missing_rect_returns_none(self):
        """Test that drawings without rect return None."""
        mock_drawing = Mock()
        mock_drawing.get.side_effect = lambda key, default=None: {
            "fill": (0.5, 0.5, 0.5),
            "rect": None,
            "items": [("l", "data")],
        }.get(key, default)

        result = detect_waste_type_from_drawing(mock_drawing)
        assert result is None

    def test_missing_items_returns_none(self):
        """Test that drawings without items return None."""
        mock_drawing = Mock()
        mock_drawing.get.side_effect = lambda key, default=None: {
            "fill": (0.5, 0.5, 0.5),
            "rect": Mock(width=10.0, height=10.0),
            "items": [],
        }.get(key, default)

        result = detect_waste_type_from_drawing(mock_drawing)
        assert result is None

    def test_color_tolerance(self):
        """Test that color matching works with slight variations."""
        # Test PAPER with slightly different blue color (within tolerance)
        drawing = self.create_mock_drawing(
            fill_color=(0.330, 0.760, 0.940),  # Slightly different from exact (0.327, 0.757, 0.939)
            width=7.7,
            height=13.2,
            item_count=4,
            first_item_type="l",
        )

        result = detect_waste_type_from_drawing(drawing)
        assert result == WasteType.PAPER

    def test_size_tolerance(self):
        """Test that size matching works with slight variations."""
        # Test PAPER with slightly different size (within tolerance)
        drawing = self.create_mock_drawing(
            fill_color=(0.327, 0.757, 0.939),
            width=7.5,  # Slightly different from exact 7.7
            height=13.0,  # Slightly different from exact 13.2
            item_count=4,
            first_item_type="l",
        )

        result = detect_waste_type_from_drawing(drawing)
        assert result == WasteType.PAPER

    def test_problematic_priority(self):
        """Test that PROBLEMATIC type takes priority based on item count."""
        # Even if color/size might match other types, high item count should classify as PROBLEMATIC
        drawing = self.create_mock_drawing(
            fill_color=(0.201, 0.570, 0.252),  # Green color (could be ORGANIC)
            width=7.7,
            height=13.2,  # Size matches ORGANIC
            item_count=350,  # But very high item count
            first_item_type="l",
        )

        result = detect_waste_type_from_drawing(drawing)
        assert result == WasteType.PROBLEMATIC

    @pytest.mark.parametrize(
        "waste_type,color,size,items,item_type",
        [
            (WasteType.PAPER, (0.327, 0.757, 0.939), (7.7, 13.2), 4, "l"),
            (WasteType.PACKAGING, (0.729, 0.884, 0.977), (10.2, 10.6), 23, "c"),
            (WasteType.ORGANIC, (0.201, 0.570, 0.252), (7.7, 13.2), 4, "l"),
            (WasteType.RESIDUAL, (0.343, 0.341, 0.339), (7.7, 13.2), 4, "l"),
            (WasteType.ELECTRIC, (0.114, 0.116, 0.111), (12.4, 15.9), 34, "l"),
            (WasteType.CHRISTMAS_TREES, (0.201, 0.570, 0.252), (11.6, 15.1), 34, "l"),
            (WasteType.BULKY, (0.585, 0.418, 0.264), (10.4, 5.8), 12, "l"),
            (WasteType.GLASS, (0.985, 0.736, 0.201), (7.7, 13.2), 4, "l"),
            (WasteType.HEDGE, (0.585, 0.418, 0.264), (12.2, 12.2), 56, "c"),
            (WasteType.PROBLEMATIC, (0.385, 0.632, 0.261), (11.8, 15.7), 392, "c"),
            (WasteType.CLOTHERS, (0.939, 0.490, 0.000), (14.7, 6.0), 9, "l"),
        ],
    )
    def test_all_waste_types_parametrized(self, waste_type, color, size, items, item_type):
        """Parametrized test for all waste types using training data."""
        width, height = size
        drawing = self.create_mock_drawing(
            fill_color=color, width=width, height=height, item_count=items, first_item_type=item_type
        )

        result = detect_waste_type_from_drawing(drawing)
        assert result == waste_type
