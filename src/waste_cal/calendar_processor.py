"""
Calendar processing module for extracting waste collection data from PDF calendars.

This module orchestrates the extraction workflow, processing pages sequentially
to build a complete calendar of waste collection dates and types.
"""

import datetime

from waste_cal.drawing import detect_waste_type_from_drawing
from waste_cal.month import Month
from waste_cal.pdf_extractor import areas_per_day, is_drawing_in_box, read_pdf
from waste_cal.waste_types import Languages, WasteType


class CalendarData:
    """Container for extracted calendar data mapping dates to waste types."""

    def __init__(self) -> None:
        """Initialize empty calendar data."""
        self._collections: dict[datetime.date, list[WasteType]] = {}

    def add_collection(self, date: datetime.date, waste_type: WasteType) -> None:
        """Add a waste collection for a specific date."""
        if date not in self._collections:
            self._collections[date] = []
        if waste_type not in self._collections[date]:
            self._collections[date].append(waste_type)

    def get_collections_for_date(self, date: datetime.date) -> list[WasteType]:
        """Get list of waste collections for a specific date."""
        return self._collections.get(date, [])

    def get_all_dates(self) -> list[datetime.date]:
        """Get all dates with collections, sorted chronologically."""
        return sorted(self._collections.keys())

    def to_text(self, language: Languages = Languages.EN) -> str:
        """
        Convert calendar data to human-readable text format.

        Args:
            language: Language for waste type descriptions.

        Returns:
            Formatted string with dates and waste types.
        """
        if not self._collections:
            return "No waste collections found."

        lines = []
        current_month = None

        for date in self.get_all_dates():
            # Add month header when month changes
            if current_month != date.month:
                current_month = date.month
                month_name = date.strftime("%B %Y")
                lines.append(f"\n=== {month_name} ===")

            waste_types = self._collections[date]
            if waste_types:
                # Format date and waste types
                date_str = date.strftime("%Y-%m-%d (%A)")
                waste_strs = []
                for waste_type in sorted(waste_types, key=lambda w: w.value):
                    description = waste_type.description(language)
                    icon = waste_type.icon()
                    waste_strs.append(f"{description} {icon}")

                waste_list = ", ".join(waste_strs)
                lines.append(f"{date_str}: {waste_list}")

        return "\n".join(lines)

    def to_ical(self, language: Languages, year: int) -> str:
        """
        Convert calendar data to iCal format.

        Args:
            language: Language for waste type descriptions
            year: Year for the calendar

        Returns:
            iCal format string
        """
        from ics import Calendar, Event

        calendar = Calendar()

        for date in self.get_all_dates():
            waste_types = self._collections[date]

            for waste_type in waste_types:
                event = Event()
                event.name = f"{waste_type.icon()} {waste_type.description(language)}"
                # Convert date to datetime for icalendar compatibility
                event.begin = datetime.datetime.combine(date, datetime.time())
                event.description = f"Waste collection: {waste_type.description(language)}"
                event.location = "Niederanven, Luxembourg"
                event.make_all_day()

                calendar.events.add(event)

        return calendar.serialize()


def extract_calendar_data(pdf_path: str, year: int) -> CalendarData:
    """
    Extract waste collection calendar data from a PDF file.

    Args:
        pdf_path: Path to the PDF calendar file.
        year: Year for date calculations.

    Returns:
        CalendarData object containing all extracted collections.
    """
    calendar_data = CalendarData()
    doc = read_pdf(pdf_path)

    try:
        # Process each month
        for month in Month:
            page_index = month.page_index()

            # Skip if page doesn't exist
            if page_index >= len(doc):
                continue

            page = doc[page_index]

            # Get day areas for this month
            day_areas = areas_per_day(page)
            all_drawings = page.get_drawings()

            # Get month number (1-12) from month enum
            month_number = list(Month).index(month) + 1

            # Process each day in the month
            for day_num, day_area in enumerate(day_areas, 1):
                # Check if this day exists in the specified month/year
                try:
                    date = datetime.date(year, month_number, day_num)
                except ValueError:
                    # Invalid date (e.g., February 30th)
                    continue

                # Find drawings in this day's area
                day_drawings = [d for d in all_drawings if is_drawing_in_box(d, day_area)]

                # Classify each drawing as a waste type
                for drawing in day_drawings:
                    waste_type = detect_waste_type_from_drawing(drawing)
                    if waste_type:
                        calendar_data.add_collection(date, waste_type)

    finally:
        doc.close()

    return calendar_data
