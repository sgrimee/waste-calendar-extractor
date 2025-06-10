#!/usr/bin/env python3
"""
Command-line interface for the waste calendar extractor.
"""

import argparse
import logging

from .calendar_processor import extract_dates_from_pdf
from .output_generator import download_calendar_pdf, generate_all_language_calendars, generate_ical_calendar


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
    parser.add_argument(
        "pdf_file",
        nargs="?",
        default="pdf/ressourcekalenner-nidderaanwen-web.pdf",
        help="Path to PDF file (default: pdf/ressourcekalenner-nidderaanwen-web.pdf)",
    )
    parser.add_argument("-o", "--output", help="Output iCal file path (default: waste-{year}.ics)")
    parser.add_argument("-y", "--year", type=int, default=2025, help="Year for the calendar (default: 2025)")
    parser.add_argument(
        "-l",
        "--language",
        choices=["de", "fr", "en"],
        help="Generate calendar for specific language (de=German, fr=French, en=English)",
    )
    parser.add_argument(
        "--all-languages", action="store_true", help="Generate calendars for all languages (de, fr, en)"
    )
    parser.add_argument(
        "--download", action="store_true", help="Download the latest calendar PDF from Niederanven website"
    )
    parser.add_argument(
        "--download-url",
        default="https://www.niederanven.lu/en/environment/waste-disposal-management",
        help="URL to download the calendar PDF from (default: Niederanven waste management page)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level)

    try:
        # Download PDF if requested
        if args.download:
            if not download_calendar_pdf(args.download_url, args.pdf_file):
                return 1

        # Extract dates from PDF
        results = extract_dates_from_pdf(args.pdf_file, args.year)

        if args.all_languages:
            # Generate calendars for all languages
            generated = generate_all_language_calendars(results, args.year)
            total_events = sum(generated.values())
            logging.info(
                f"Extraction complete. {len(results)} dates processed, "
                f"generated {len(generated)} language-specific calendars with {total_events} total events."
            )
        elif args.language:
            # Generate calendar for specific language
            events_added = generate_ical_calendar(results, args.output, args.year, args.language)
            logging.info(
                f"Extraction complete. {len(results)} dates processed with {events_added} "
                f"waste collection events found for {args.language}."
            )
        else:
            # Generate default multilingual calendar
            events_added = generate_ical_calendar(results, args.output, args.year)
            logging.info(
                f"Extraction complete. {len(results)} dates processed with {events_added} "
                f"waste collection events found."
            )

    except FileNotFoundError as e:
        logging.error(f"Error: {e}")
        return 1
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return 1

    return 0
