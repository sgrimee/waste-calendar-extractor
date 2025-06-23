"""
iCal generation module for waste collection calendars.

This module provides functionality to generate iCal calendar files
from extracted waste collection data.
"""

import os
from pathlib import Path

from ics import Calendar, Event
from waste_cal.calendar_processor import CalendarData
from waste_cal.waste_types import Languages


def generate_ical_file(calendar_data: CalendarData, language: Languages, year: int, output_dir: str = "ics") -> str:
    """
    Generate an iCal file for the specified language.

    Args:
        calendar_data: The extracted calendar data
        language: Language for waste type descriptions
        year: Year for the calendar
        output_dir: Directory to save the iCal file

    Returns:
        Path to the generated iCal file
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True)

    # Create calendar
    calendar = Calendar()

    # Add events for each collection date
    for date in calendar_data.get_all_dates():
        waste_types = calendar_data.get_collections_for_date(date)

        for waste_type in waste_types:
            event = Event()
            event.name = f"{waste_type.icon()} {waste_type.description(language)}"
            event.begin = date
            event.description = f"Waste collection: {waste_type.description(language)}"
            event.location = "Niederanven, Luxembourg"
            event.make_all_day()

            calendar.events.add(event)

    # Determine filename based on language
    language_codes = {
        Languages.LU: "lu",  # Luxembourgish uses lu file suffix
        Languages.FR: "fr",
        Languages.EN: "en",
    }

    language_code = language_codes[language]
    filename = f"waste-{language_code}.ics"
    filepath = os.path.join(output_dir, filename)

    # Write the calendar to file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(calendar.serialize())

    return filepath


def generate_all_ical_files(calendar_data: CalendarData, year: int, output_dir: str = "ics") -> list[str]:
    """
    Generate iCal files for all supported languages.

    Args:
        calendar_data: The extracted calendar data
        year: Year for the calendar
        output_dir: Directory to save the iCal files

    Returns:
        List of paths to generated iCal files
    """
    generated_files = []

    for language in [Languages.LU, Languages.FR, Languages.EN]:
        filepath = generate_ical_file(calendar_data, language, year, output_dir)
        generated_files.append(filepath)

    return generated_files
