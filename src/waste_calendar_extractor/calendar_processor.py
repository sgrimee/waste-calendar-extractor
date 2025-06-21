#!/usr/bin/env python3
"""
Calendar processing functions for waste collection calendars.
"""

import logging
from datetime import datetime
from pathlib import Path

import fitz  # PyMuPDF

from .constants import MONTH_NUMBERS
from .pdf_extractor import detect_month, extract_date_and_waste_types, extract_legend_mapping, load_page_areas


def process_pdf_page(page: fitz.Page, current_month: str, year: int = 2025, legend_mapping: dict[str, str] | None = None) -> list[dict]:
    """Process a single PDF page and extract waste collection dates."""
    results = []

    # Extract all dates and waste types from the page using area-based extraction
    date_waste_map = extract_date_and_waste_types(page, current_month, legend_mapping)

    # Convert to results format
    for date_num, waste_descriptions in date_waste_map.items():
        if waste_descriptions and current_month and current_month in MONTH_NUMBERS:
            try:
                date_obj = datetime(year, MONTH_NUMBERS[current_month], date_num)
                icons = " | ".join(waste_descriptions)

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
    legend_mapping = {}

    # Extract legend from page 2 (index 1) if available
    if len(doc) > 1:
        page_2 = doc[1]
        areas = load_page_areas()
        legend_area = areas["legend_area"]
        legend_mapping = extract_legend_mapping(page_2, legend_area)
        logging.info(f"Extracted legend mapping with {len(legend_mapping)} waste types")

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
            page_results = process_pdf_page(page, current_month, year, legend_mapping)
            results.extend(page_results)

    doc.close()
    logging.info(f"PDF processing complete. Found {len(results)} total entries.")

    return results
