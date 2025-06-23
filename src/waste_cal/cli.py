#!/usr/bin/env python3
"""
Command-line interface for the waste calendar extractor.
"""

import argparse
import datetime
import logging

from waste_cal.calendar_processor import extract_calendar_data
from waste_cal.month import Month
from waste_cal.research import extract_month_drawings
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

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Default extraction command
    extract_parser = subparsers.add_parser("extract", help="Extract waste calendar (default)")
    extract_parser.add_argument(
        "pdf_file",
        nargs="?",
        default="pdf/ressourcekalenner-nidderaanwen-web.pdf",
        help="Path to PDF file (default: pdf/ressourcekalenner-nidderaanwen-web.pdf)",
    )
    extract_parser.add_argument(
        "-l",
        "--language",
        choices=["de", "fr", "en"],
        default="en",
        help="""Language for text output (de=German, fr=French, en=English). Default: en""",
    )
    extract_parser.add_argument(
        "-y",
        "--year",
        type=int,
        default=datetime.datetime.now().year,
        help="Year for calendar extraction (default: current year)"
    )
    extract_parser.add_argument(
        "--text-output",
        action="store_true",
        help="Output as text instead of generating iCal files"
    )

    # Drawings extraction command
    drawings_parser = subparsers.add_parser("drawings", help="Extract drawings from a specific month")
    drawings_parser.add_argument(
        "month",
        choices=[month.value for month in Month],
        help="Month name to extract drawings from"
    )
    drawings_parser.add_argument(
        "pdf_file",
        nargs="?",
        default="pdf/ressourcekalenner-nidderaanwen-web.pdf",
        help="Path to PDF file (default: pdf/ressourcekalenner-nidderaanwen-web.pdf)",
    )
    drawings_parser.add_argument(
        "-o", "--output-dir",
        default="debug",
        help="Output directory for drawing images (default: debug)"
    )

    # Global options
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level)

    # Handle commands
    if args.command == "drawings":
        try:
            extract_month_drawings(args.pdf_file, args.month, args.output_dir)
        except Exception as e:
            logging.error(f"Error extracting drawings: {e}")
            return 1
    elif args.command == "extract" or args.command is None:
        # Default behavior - extract calendar
        try:
            # Map language string to enum
            language_map = {"de": Languages.LU, "fr": Languages.FR, "en": Languages.EN}
            language = language_map[args.language]

            logging.info(f"Extracting calendar data from {args.pdf_file} for year {args.year}")
            calendar_data = extract_calendar_data(args.pdf_file, args.year)

            if args.text_output:
                # Output as text
                print(calendar_data.to_text(language))
            else:
                # Future: generate iCal files
                logging.info("iCal generation not yet implemented - use --text-output for now")
                print(calendar_data.to_text(language))

        except Exception as e:
            logging.error(f"Error extracting calendar: {e}")
            return 1

    return 0
