#!/usr/bin/env python3
"""
Command-line interface for the waste calendar extractor.
"""

import argparse
import logging
from waste_cal.research import extract_month_drawings
from waste_cal.month import Month


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
    parser.add_argument(
        "-l",
        "--language",
        choices=["de", "fr", "en"],
        help="""Generate only the calendar for a specific language (de=German, fr=French, en=English). If not specified,
        all languages will be generated.""",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level)

    pass
