#!/usr/bin/env python3
"""
Command-line interface for the waste calendar extractor.

Supports multiple communes and standalone ADYS calendar generation.
"""

import argparse
import datetime
import logging

from waste_cal.adys_extractor import extract_adys_dates, extract_customer_id_from_filename
from waste_cal.calendar_processor import extract_calendar_data
from waste_cal.ical_generator import (
    generate_adys_ical_file,
    generate_all_adys_ical_files,
    generate_all_commune_ical_files,
    generate_commune_ical_file,
)
from waste_cal.waste_types import Languages

# Supported communes
SUPPORTED_COMMUNES = ["niederanven", "schuttrange"]


def setup_logging(level: str = "INFO") -> None:
    """Configure logging with specified level."""
    logging.basicConfig(
        level=getattr(logging, level.upper()), format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
    )


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description="Extract waste collection dates from PDF calendars and generate iCal files."
    )

    # Mutually exclusive group for commune vs adys mode
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--commune",
        choices=SUPPORTED_COMMUNES,
        help="Commune name (e.g., niederanven, schuttrange)",
    )
    mode_group.add_argument(
        "--adys",
        action="store_true",
        help="Generate ADYS calendar (requires --pdf)",
    )

    # Common arguments
    parser.add_argument(
        "-l",
        "--language",
        choices=["lu", "fr", "en"],
        help=("Language for output (lu=Luxembourgish, fr=French, en=English). If omitted, generates all languages."),
    )
    parser.add_argument(
        "-y",
        "--year",
        type=int,
        default=datetime.datetime.now().year,
        help="Year for calendar extraction (default: current year)",
    )
    parser.add_argument(
        "--pdf",
        metavar="PDF_PATH",
        required=True,
        help="Path to PDF file",
    )
    parser.add_argument(
        "--customer-id",
        help="ADYS customer ID (optional, derived from PDF filename if not provided)",
    )
    parser.add_argument(
        "--text",
        action="store_true",
        help="Output as text instead of generating iCal files",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level)

    # Map language strings to enum
    language_map = {"lu": Languages.LU, "fr": Languages.FR, "en": Languages.EN}

    try:
        if args.commune:
            # Commune mode: generate waste calendar for a commune
            return _handle_commune_mode(args, language_map)
        else:
            # ADYS mode: generate standalone ADYS calendar
            return _handle_adys_mode(args, language_map)

    except Exception as e:
        logging.error(f"Error: {e}")
        return 1

    return 0


def _handle_commune_mode(args, language_map: dict) -> int:
    """Handle commune calendar generation mode."""
    commune = args.commune

    # PDF path is required
    pdf_path = args.pdf

    logging.info(f"Extracting calendar data from {pdf_path} for {commune}, year {args.year}")
    calendar_data = extract_calendar_data(pdf_path, args.year)

    if args.text:
        # Output as text
        language = language_map.get(args.language, Languages.EN)
        print(calendar_data.to_text(language))
    else:
        # Generate iCal files
        if args.language:
            language = language_map[args.language]
            filepaths = generate_commune_ical_file(calendar_data, commune, language, args.year)
            for filepath in filepaths:
                logging.info(f"Generated iCal file: {filepath}")
        else:
            filepaths = generate_all_commune_ical_files(calendar_data, commune, args.year)
            for filepath in filepaths:
                logging.info(f"Generated iCal file: {filepath}")

    return 0


def _handle_adys_mode(args, language_map: dict) -> int:
    """Handle ADYS calendar generation mode."""
    adys_pdf = args.pdf

    # Determine customer ID
    customer_id = args.customer_id
    if not customer_id:
        customer_id = extract_customer_id_from_filename(adys_pdf)
        if not customer_id:
            logging.error(
                f"Could not extract customer ID from filename '{adys_pdf}'. Use --customer-id to specify it explicitly."
            )
            return 1

    logging.info(f"Extracting ADYS dates from {adys_pdf} for customer {customer_id}")
    adys_dates = extract_adys_dates(adys_pdf)
    logging.info(f"Found {len(adys_dates)} ADYS cleaning dates")

    if args.text:
        # Output as text
        print(f"ADYS cleaning dates for customer {customer_id}:")
        for date in adys_dates:
            print(f"  {date}")
    else:
        # Generate iCal files
        if args.language:
            language = language_map[args.language]
            filepath = generate_adys_ical_file(adys_dates, customer_id, language, args.year)
            logging.info(f"Generated ADYS iCal file: {filepath}")
        else:
            filepaths = generate_all_adys_ical_files(adys_dates, customer_id, args.year)
            for filepath in filepaths:
                logging.info(f"Generated ADYS iCal file: {filepath}")

    return 0
