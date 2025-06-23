#!/usr/bin/env python3
"""
Command-line interface for the waste calendar extractor.
"""

import argparse
import datetime
import logging

from waste_cal.calendar_processor import extract_calendar_data
from waste_cal.ical_generator import generate_all_ical_files, generate_ical_file
from waste_cal.waste_types import Languages


def setup_logging(level: str = "INFO") -> None:
    """Configure logging with specified level."""
    logging.basicConfig(
        level=getattr(logging, level.upper()), format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
    )


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description=("Extract waste collection dates from PDF calendars and generate iCal files.")
    )

    # Main command arguments
    parser.add_argument(
        "pdf_file",
        nargs="?",
        default="pdf/ressourcekalenner-nidderaanwen-web.pdf",
        help="Path to PDF file (default: pdf/ressourcekalenner-nidderaanwen-web.pdf)",
    )
    parser.add_argument(
        "-l",
        "--language",
        choices=["lu", "fr", "en"],
        help=(
            "Language for output (lu=Luxembourgish, fr=French, en=English). "
            "For iCal: generates only specified language file. "
            "For text: uses specified language (default: en)"
        ),
    )
    parser.add_argument(
        "-y",
        "--year",
        type=int,
        default=datetime.datetime.now().year,
        help="Year for calendar extraction (default: current year)",
    )
    parser.add_argument(
        "--text",
        action="store_true",
        help="Output as text instead of generating iCal files (default: generate iCal files)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level)

    # Extract calendar
    try:
        logging.info(f"Extracting calendar data from {args.pdf_file} for year {args.year}")
        calendar_data = extract_calendar_data(args.pdf_file, args.year)

        if args.text:
            # Output as text
            language_map = {"lu": Languages.LU, "fr": Languages.FR, "en": Languages.EN}
            language = language_map.get(args.language, Languages.EN)
            print(calendar_data.to_text(language))
        else:
            # Generate iCal files
            if args.language:
                # Generate single language file
                language_map = {"lu": Languages.LU, "fr": Languages.FR, "en": Languages.EN}
                language = language_map[args.language]
                filepath = generate_ical_file(calendar_data, language, args.year)
                logging.info(f"Generated iCal file: {filepath}")
            else:
                # Generate all language files
                filepaths = generate_all_ical_files(calendar_data, args.year)
                for filepath in filepaths:
                    logging.info(f"Generated iCal file: {filepath}")

    except Exception as e:
        logging.error(f"Error extracting calendar: {e}")
        return 1

    return 0
