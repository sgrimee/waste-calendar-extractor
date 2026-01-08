"""
iCal generation module for waste collection calendars.

This module provides functionality to generate iCal calendar files
from extracted waste collection data, with optional ADYS bin cleaning dates.
"""

import os
import shutil
from datetime import date as date_class
from datetime import datetime, timedelta
from pathlib import Path

from ics import Calendar, Event
from ics.alarm import DisplayAlarm
from waste_cal.calendar_processor import CalendarData
from waste_cal.waste_types import AdysEventType, Languages


def generate_commune_ical_file(
    calendar_data: CalendarData,
    commune: str,
    language: Languages,
    year: int,
    output_dir: str = "ics",
) -> list[str]:
    """
    Generate iCal file for a commune.

    For niederanven, also generates legacy waste-{lang}.ics duplicates.

    Args:
        calendar_data: The extracted calendar data
        commune: Commune name (e.g., 'niederanven', 'schuttrange')
        language: Language for waste type descriptions
        year: Year for the calendar
        output_dir: Directory to save the iCal file

    Returns:
        List of generated file paths.
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
            # Convert date to datetime for ics library compatibility
            event.begin = datetime.combine(date, datetime.min.time())
            event.description = f"Waste collection: {waste_type.description(language)}"
            event.location = f"{commune.title()}, Luxembourg"
            event.make_all_day()

            # Add alarm for regular collection types
            if waste_type.has_alarm():
                alarm = DisplayAlarm()
                alarm.display_text = waste_type.alarm_message(language)
                # Trigger at 20:30 the day before collection
                alarm.trigger = timedelta(days=-1, hours=20, minutes=30)
                event.alarms.append(alarm)

            calendar.events.add(event)

    # Determine filename based on language
    language_codes = {
        Languages.LU: "lu",
        Languages.FR: "fr",
        Languages.EN: "en",
    }

    language_code = language_codes[language]
    filename = f"waste-{commune}-{language_code}.ics"
    filepath = os.path.join(output_dir, filename)

    # Write the calendar to file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(calendar.serialize())

    generated_files = [filepath]

    # For niederanven, also generate legacy duplicate files
    if commune == "niederanven":
        legacy_filename = f"waste-{language_code}.ics"
        legacy_filepath = os.path.join(output_dir, legacy_filename)
        shutil.copy2(filepath, legacy_filepath)
        generated_files.append(legacy_filepath)

    return generated_files


def generate_all_commune_ical_files(
    calendar_data: CalendarData, commune: str, year: int, output_dir: str = "ics"
) -> list[str]:
    """
    Generate iCal files for all supported languages for a commune.

    Args:
        calendar_data: The extracted calendar data
        commune: Commune name (e.g., 'niederanven', 'schuttrange')
        year: Year for the calendar
        output_dir: Directory to save the iCal files

    Returns:
        List of paths to generated iCal files
    """
    generated_files = []

    for language in [Languages.LU, Languages.FR, Languages.EN]:
        filepaths = generate_commune_ical_file(calendar_data, commune, language, year, output_dir)
        generated_files.extend(filepaths)

    return generated_files


def generate_adys_ical_file(
    adys_dates: list[str],
    customer_id: str,
    language: Languages,
    year: int,
    output_dir: str = "ics",
) -> str:
    """
    Generate standalone ADYS iCal file.

    Args:
        adys_dates: List of ADYS cleaning dates in ISO format (YYYY-MM-DD)
        customer_id: ADYS customer ID
        language: Language for event descriptions
        year: Year for the calendar
        output_dir: Directory to save the iCal file

    Returns:
        Path to generated file.
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True)

    # Create calendar
    calendar = Calendar()

    # Add ADYS cleaning events
    for date_str in adys_dates:
        # Parse ISO date string (YYYY-MM-DD)
        date_obj = date_class.fromisoformat(date_str)
        adys_event = _create_adys_event(date_obj, language)
        calendar.events.add(adys_event)

    # Determine filename based on language
    language_codes = {
        Languages.LU: "lu",
        Languages.FR: "fr",
        Languages.EN: "en",
    }

    language_code = language_codes[language]
    filename = f"adys-{customer_id}-{language_code}.ics"
    filepath = os.path.join(output_dir, filename)

    # Write the calendar to file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(calendar.serialize())

    return filepath


def generate_all_adys_ical_files(
    adys_dates: list[str], customer_id: str, year: int, output_dir: str = "ics"
) -> list[str]:
    """
    Generate ADYS iCal files for all supported languages.

    Args:
        adys_dates: List of ADYS cleaning dates in ISO format (YYYY-MM-DD)
        customer_id: ADYS customer ID
        year: Year for the calendar
        output_dir: Directory to save the iCal files

    Returns:
        List of paths to generated iCal files
    """
    generated_files = []

    for language in [Languages.LU, Languages.FR, Languages.EN]:
        filepath = generate_adys_ical_file(adys_dates, customer_id, language, year, output_dir)
        generated_files.append(filepath)

    return generated_files


# Legacy functions - kept for backward compatibility during transition


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
            # Convert date to datetime for ics library compatibility
            event.begin = datetime.combine(date, datetime.min.time())
            event.description = f"Waste collection: {waste_type.description(language)}"
            event.location = "Niederanven, Luxembourg"
            event.make_all_day()

            # Add alarm for regular collection types
            if waste_type.has_alarm():
                alarm = DisplayAlarm()
                alarm.display_text = waste_type.alarm_message(language)
                # Trigger at 20:30 the day before collection
                alarm.trigger = timedelta(days=-1, hours=20, minutes=30)
                event.alarms.append(alarm)

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


def _create_adys_event(date, language: Languages) -> Event:
    """
    Create an ADYS bin cleaning event.

    Args:
        date: The date of the cleaning event
        language: Language for event description

    Returns:
        An Event object with ADYS cleaning details
    """
    event = Event()
    event_type = AdysEventType.BIN_CLEANING
    event.name = f"{event_type.icon()} {event_type.description(language)}"
    # Convert date to datetime for ics library compatibility
    event.begin = datetime.combine(date, datetime.min.time())
    event.description = f"Bin cleaning: {event_type.description(language)}"
    # ADYS is regional, not commune-specific
    event.location = "Luxembourg"
    event.make_all_day()

    # Add alarm for day before
    alarm = DisplayAlarm()
    alarm.display_text = event_type.alarm_message(language)
    # Trigger at 20:30 the day before cleaning
    alarm.trigger = timedelta(days=-1, hours=20, minutes=30)
    event.alarms.append(alarm)

    return event


# Legacy combined functions - deprecated, will be removed in future versions


def generate_ical_file_with_adys(
    calendar_data: CalendarData,
    adys_dates: list[str],
    language: Languages,
    year: int,
    output_dir: str = "ics",
) -> str:
    """
    Generate an iCal file combining waste collection and ADYS bin cleaning dates.

    Args:
        calendar_data: The extracted waste collection calendar data
        adys_dates: List of ADYS cleaning dates in ISO format (YYYY-MM-DD)
        language: Language for event descriptions
        year: Year for the calendar
        output_dir: Directory to save the iCal file

    Returns:
        Path to the generated iCal file with -adys suffix
    """
    from datetime import date as date_class

    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(exist_ok=True)

    # Create calendar with standard waste collection events
    calendar = Calendar()

    # Add waste collection events
    for date in calendar_data.get_all_dates():
        waste_types = calendar_data.get_collections_for_date(date)

        for waste_type in waste_types:
            event = Event()
            event.name = f"{waste_type.icon()} {waste_type.description(language)}"
            event.begin = datetime.combine(date, datetime.min.time())
            event.description = f"Waste collection: {waste_type.description(language)}"
            event.location = "Niederanven, Luxembourg"
            event.make_all_day()

            # Add alarm for regular collection types
            if waste_type.has_alarm():
                alarm = DisplayAlarm()
                alarm.display_text = waste_type.alarm_message(language)
                alarm.trigger = timedelta(days=-1, hours=20, minutes=30)
                event.alarms.append(alarm)

            calendar.events.add(event)

    # Add ADYS cleaning events
    for date_str in adys_dates:
        # Parse ISO date string (YYYY-MM-DD)
        date_obj = date_class.fromisoformat(date_str)
        adys_event = _create_adys_event(date_obj, language)
        calendar.events.add(adys_event)

    # Determine filename based on language
    language_codes = {
        Languages.LU: "lu",
        Languages.FR: "fr",
        Languages.EN: "en",
    }

    language_code = language_codes[language]
    filename = f"waste-{language_code}-adys.ics"
    filepath = os.path.join(output_dir, filename)

    # Write the calendar to file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(calendar.serialize())

    return filepath


def generate_all_ical_files_with_adys(
    calendar_data: CalendarData, adys_dates: list[str], year: int, output_dir: str = "ics"
) -> list[str]:
    """
    Generate iCal files for all supported languages with ADYS dates.

    Args:
        calendar_data: The extracted calendar data
        adys_dates: List of ADYS cleaning dates in ISO format (YYYY-MM-DD)
        year: Year for the calendar
        output_dir: Directory to save the iCal files

    Returns:
        List of paths to generated iCal files with -adys suffix
    """
    generated_files = []

    for language in [Languages.LU, Languages.FR, Languages.EN]:
        filepath = generate_ical_file_with_adys(calendar_data, adys_dates, language, year, output_dir)
        generated_files.append(filepath)

    return generated_files
