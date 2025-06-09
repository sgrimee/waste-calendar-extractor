#!/usr/bin/env python3
"""
Waste Collection Calendar Extractor

Extracts waste collection dates and types from PDF calendars and generates iCal files.
Supports Luxembourgish month names and multilingual waste type descriptions.
"""

import argparse
import logging
from datetime import datetime
from pathlib import Path

import fitz  # PyMuPDF
from ics import Calendar, Event

# Luxembourgish month names mapping
MONTH_NAMES = [
    "JANUAR", "FEBRUAR", "MÄERZ", "ABRËLL", "MEE", "JUNI",
    "JULI", "AUGUST", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DEZEMBER"
]
MONTH_NUMBERS = {month: index + 1 for index, month in enumerate(MONTH_NAMES)}

# Waste collection type keywords for detection
WASTE_TYPE_KEYWORDS = [
    "reschtoffäll", "déchets ménagers", "residual waste",
    "pabeier", "papier", "paper", "carton",
    "glas", "verre", "glass",
    "verpackungen", "emballages", "packaging", "valorlux",
    "organesch", "organiques", "organic",
    "aalt gezei", "vieux vêtements", "old clothes",
    "beemercher", "sapins", "christmas trees"
]


def setup_logging(level: str = "INFO") -> None:
    """Configure logging with specified level."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )


def extract_text_elements(page) -> list[dict]:
    """Extract positioned text elements from a PDF page."""
    text_dict = page.get_text("dict")
    elements = []

    for block in text_dict["blocks"]:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if text:
                        bbox = span["bbox"]
                        elements.append({
                            "text": text,
                            "x": bbox[0],
                            "y": bbox[1]
                        })

    return elements


def group_elements_by_rows(
    elements: list[dict], row_tolerance: float = 10.0
) -> list[list[dict]]:
    """Group text elements into rows based on Y coordinate proximity."""
    if not elements:
        return []

    # Sort by Y position and then X position
    elements.sort(key=lambda x: (x["y"], x["x"]))

    rows = []
    current_row = []
    last_y = -1

    for elem in elements:
        if abs(elem["y"] - last_y) > row_tolerance:
            if current_row:
                rows.append(current_row)
            current_row = [elem]
            last_y = elem["y"]
        else:
            current_row.append(elem)

    if current_row:
        rows.append(current_row)

    return rows


def detect_month(page_text: str) -> str:
    """Detect month name in page text."""
    lines = page_text.split("\n")
    for line in lines:
        for month in MONTH_NAMES:
            if month in line:
                return month
    return ""


def extract_date_and_waste_types(row: list[dict]) -> tuple[int | None, list[str]]:
    """Extract date and waste types from a row of text elements."""
    date_found = None
    waste_types = []

    for elem in row:
        text = elem["text"]

        # Check if it's a date (1-31)
        if text.isdigit() and 1 <= int(text) <= 31:
            date_found = int(text)

        # Look for waste collection indicators
        elif any(keyword in text.lower() for keyword in WASTE_TYPE_KEYWORDS):
            waste_types.append(text)

    return date_found, waste_types


def process_pdf_page(page, current_month: str, year: int = 2025) -> list[dict]:
    """Process a single PDF page and extract waste collection dates."""
    results = []

    # Extract and group text elements
    elements = extract_text_elements(page)
    rows = group_elements_by_rows(elements)

    # Process each row to find date + waste type combinations
    for row in rows:
        date_found, waste_types = extract_date_and_waste_types(row)

        if (
            date_found
            and waste_types
            and current_month
            and current_month in MONTH_NUMBERS
        ):
            try:
                date_obj = datetime(year, MONTH_NUMBERS[current_month], date_found)
                icons = " | ".join(waste_types)

                logging.info(
                    f"Extracted: {date_obj.strftime('%Y-%m-%d')} -> '{icons}'"
                )

                results.append({
                    "date": date_obj,
                    "icons": icons
                })

            except ValueError:
                # Invalid day for this month
                continue

    return results


def extract_dates_from_pdf(pdf_path: str, year: int = 2025) -> list[dict]:
    """Extract all waste collection dates from PDF file."""
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    logging.info(f"Opening PDF file: {pdf_path}")
    doc = fitz.open(str(pdf_path))
    logging.info(f"PDF opened successfully. Found {len(doc)} pages.")

    results = []
    current_month = ""

    for page_num, page in enumerate(doc, 1):
        logging.info(f"Processing page {page_num}/{len(doc)}")

        # Get simple text for month detection
        page_text = page.get_text()
        month = detect_month(page_text)
        if month:
            current_month = month
            logging.info(f"Found month: {current_month} on page {page_num}")

        if current_month:
            page_results = process_pdf_page(page, current_month, year)
            results.extend(page_results)

    doc.close()
    logging.info(f"PDF processing complete. Found {len(results)} total entries.")

    return results


def generate_ical_calendar(
    results: list[dict], output_path: str | None = None, year: int = 2025
) -> int:
    """Generate iCal calendar file from extraction results."""
    if output_path is None:
        output_path = f"waste-{year}.ics"

    logging.info("Generating iCal calendar...")
    calendar = Calendar()

    events_added = 0
    for entry in results:
        if entry['icons'].strip():  # Only add events with actual content
            event = Event()
            event.name = entry['icons']

            # Set as all-day event using date (not datetime)
            event.begin = entry['date'].date()
            event.make_all_day()

            # Add description with waste type details
            event.description = f"Waste collection: {entry['icons']}"

            # Set location (optional - can be customized)
            event.location = "Niederanven, Luxembourg"

            calendar.events.add(event)
            events_added += 1

    logging.info(f"Added {events_added} events to calendar.")

    with open(output_path, "w", encoding='utf-8') as f:
        f.writelines(calendar)

    logging.info(f"Calendar saved as '{output_path}'")
    return events_added


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description=(
            "Extract waste collection dates from PDF calendars "
            "and generate iCal files."
        )
    )
    parser.add_argument(
        "pdf_file",
        nargs="?",
        default="ressourcekalenner-nidderaanwen-web.pdf",
        help="Path to PDF file (default: ressourcekalenner-nidderaanwen-web.pdf)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output iCal file path (default: waste-{year}.ics)"
    )
    parser.add_argument(
        "-y", "--year",
        type=int,
        default=2025,
        help="Year for the calendar (default: 2025)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level)

    try:
        # Extract dates from PDF
        results = extract_dates_from_pdf(args.pdf_file, args.year)

        # Generate iCal calendar
        events_added = generate_ical_calendar(results, args.output, args.year)

        # Final summary
        logging.info(
            f"Extraction complete. {len(results)} dates processed "
            f"with {events_added} waste collection events found."
        )

    except FileNotFoundError as e:
        logging.error(f"Error: {e}")
        return 1
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
