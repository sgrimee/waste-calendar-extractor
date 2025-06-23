"""Month utilities for waste calendar processing."""

from enum import StrEnum


class Month(StrEnum):
    """Enumeration of month names."""

    JANUARY = "january"
    FEBRUARY = "february"
    MARCH = "march"
    APRIL = "april"
    MAY = "may"
    JUNE = "june"
    JULY = "july"
    AUGUST = "august"
    SEPTEMBER = "september"
    OCTOBER = "october"
    NOVEMBER = "november"
    DECEMBER = "december"

    def page_index(self) -> int:
        """
        Get the PDF page index for this month.

        Returns:
            Page index (1-based) for the month. January is page 1, February is page 2, etc.
            There is a title page before the month pages.
        """
        month_order = [
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

        # Page index is 1-based: title page (0) + month index (1-12)
        return month_order.index(self) + 1
