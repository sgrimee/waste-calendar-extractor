"""Unit tests for month module."""

import pytest

from waste_cal.month import Month


class TestMonthEnum:
    """Test Month enum."""

    def test_month_enum_values(self):
        """Test that Month enum has expected string values."""
        expected_months = {
            "JANUARY": "january",
            "FEBRUARY": "february",
            "MARCH": "march",
            "APRIL": "april",
            "MAY": "may",
            "JUNE": "june",
            "JULY": "july",
            "AUGUST": "august",
            "SEPTEMBER": "september",
            "OCTOBER": "october",
            "NOVEMBER": "november",
            "DECEMBER": "december",
        }

        for name, value in expected_months.items():
            month = getattr(Month, name)
            assert month.value == value

    def test_month_enum_completeness(self):
        """Test that we have exactly 12 months."""
        actual_count = len(list(Month))
        assert actual_count == 12


class TestMonthPageIndex:
    """Test Month.page_index() method."""

    @pytest.mark.parametrize(
        "month,expected_page",
        [
            (Month.JANUARY, 1),
            (Month.FEBRUARY, 2),
            (Month.MARCH, 3),
            (Month.APRIL, 4),
            (Month.MAY, 5),
            (Month.JUNE, 6),
            (Month.JULY, 7),
            (Month.AUGUST, 8),
            (Month.SEPTEMBER, 9),
            (Month.OCTOBER, 10),
            (Month.NOVEMBER, 11),
            (Month.DECEMBER, 12),
        ],
    )
    def test_page_index_returns_correct_page(self, month: Month, expected_page: int):
        """Test that page_index returns correct 1-based page number for each month."""
        result = month.page_index()
        assert result == expected_page

    def test_page_index_is_one_based(self):
        """Test that page indices start from 1, not 0."""
        # January should be page 1 (not 0)
        assert Month.JANUARY.page_index() == 1

    def test_page_index_sequential(self):
        """Test that page indices are sequential from 1 to 12."""
        months = [
            Month.JANUARY,
            Month.FEBRUARY,
            Month.MARCH,
            Month.APRIL,
            Month.MAY,
            Month.JUNE,
            Month.JULY,
            Month.AUGUST,
            Month.SEPTEMBER,
            Month.OCTOBER,
            Month.NOVEMBER,
            Month.DECEMBER,
        ]

        for i, month in enumerate(months, start=1):
            assert month.page_index() == i

    def test_page_index_covers_all_months(self):
        """Test that page_index method works for all months."""
        for month in Month:
            page_index = month.page_index()
            assert isinstance(page_index, int)
            assert 1 <= page_index <= 12

    def test_page_index_no_duplicates(self):
        """Test that each month has a unique page index."""
        page_indices = [month.page_index() for month in Month]
        assert len(page_indices) == len(set(page_indices))  # No duplicates
        assert set(page_indices) == set(range(1, 13))  # Covers 1-12 exactly
