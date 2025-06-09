#!/usr/bin/env python3
"""
Calendar processing functions for waste collection calendars.
"""

import logging
from datetime import datetime
from pathlib import Path

import fitz  # PyMuPDF

from .constants import MONTH_NUMBERS
from .pdf_extractor import detect_month, extract_date_and_waste_types, extract_text_elements, group_elements_by_rows


def process_pdf_page(page: fitz.Page, current_month: str, year: int = 2025) -> list[dict]:
    """Process a single PDF page and extract waste collection dates."""
    results = []

    # Extract and group text elements
    elements = extract_text_elements(page)
    rows = group_elements_by_rows(elements)

    # Process each row to find date + waste type combinations
    for row in rows:
        date_found, waste_types = extract_date_and_waste_types(row)

        if date_found and waste_types and current_month and current_month in MONTH_NUMBERS:
            try:
                date_obj = datetime(year, MONTH_NUMBERS[current_month], date_found)
                icons = " | ".join(waste_types)

                logging.info(f"Extracted: {date_obj.strftime('%Y-%m-%d')} -> '{icons}'")

                results.append({"date": date_obj, "icons": icons})

            except ValueError:
                # Invalid day for this month
                continue

    return results


def extract_dates_from_pdf(pdf_path: str, year: int = 2025) -> list[dict]:
    """Extract all waste collection dates from PDF file."""
    import logging

    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    logging.info(f"Opening PDF file: {pdf_path}")
    doc = fitz.open(str(pdf_path))
    logging.info(f"PDF opened successfully. Found {len(doc)} pages.")

    results = []
    current_month = ""

    import logging

    for page_num in range(len(doc)):
        page = doc[page_num]
        logging.info(f"Processing page {page_num + 1}/{len(doc)}")

        # Get simple text for month detection
        page_text = page.get_text()  # type: ignore
        month = detect_month(page_text)
        if month:
            current_month = month
            logging.info(f"Found month: {current_month} on page {page_num + 1}")

        if current_month:
            page_results = process_pdf_page(page, current_month, year)
            results.extend(page_results)

    doc.close()
    logging.info(f"PDF processing complete. Found {len(results)} total entries.")

    return results
