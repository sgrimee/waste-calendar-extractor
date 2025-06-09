#!/usr/bin/env python3
"""
Waste Collection Calendar Extractor

Extracts waste collection dates and types from PDF calendars and generates iCal files.
Supports Luxembourgish month names and multilingual waste type descriptions.
"""

# Import main entry point for CLI
# Import ics classes needed for tests
from ics import Calendar, Event

# Import public functions and constants
from .calendar_processor import extract_dates_from_pdf, process_pdf_page
from .cli import main
from .constants import MONTH_NAMES, MONTH_NUMBERS, WASTE_TYPE_KEYWORDS
from .output_generator import (
    download_calendar_pdf,
    extract_language_from_waste_description,
    generate_all_language_calendars,
    generate_ical_calendar,
    get_waste_type_icon,
)
from .pdf_extractor import detect_month, extract_date_and_waste_types, group_elements_by_rows

__all__ = [
    "MONTH_NAMES",
    "MONTH_NUMBERS",
    "WASTE_TYPE_KEYWORDS",
    "Calendar",
    "Event",
    "detect_month",
    "download_calendar_pdf",
    "extract_date_and_waste_types",
    "extract_dates_from_pdf",
    "extract_language_from_waste_description",
    "generate_all_language_calendars",
    "generate_ical_calendar",
    "get_waste_type_icon",
    "group_elements_by_rows",
    "main",
    "process_pdf_page",
]
