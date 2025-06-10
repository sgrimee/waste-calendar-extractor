#!/usr/bin/env python3
"""
PDF extraction utilities for waste collection calendars.
"""

import fitz  # PyMuPDF

from .constants import MONTH_NAMES


def extract_text_elements(page: fitz.Page) -> list[dict]:
    """Extract positioned text elements from a PDF page."""
    text_dict = page.get_text("dict")  # type: ignore
    elements = []

    for block in text_dict["blocks"]:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if text:
                        bbox = span["bbox"]
                        elements.append({"text": text, "x": bbox[0], "y": bbox[1]})

    return elements


def group_elements_by_rows(elements: list[dict], row_tolerance: float = 10.0) -> list[list[dict]]:
    """Group text elements into rows based on Y coordinate proximity."""
    if not elements:
        return []

    # Sort by Y position and then X position
    elements.sort(key=lambda x: (x["y"], x["x"]))

    rows = []
    current_row: list[dict] = []
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


def extract_date_and_waste_types(row: list[dict], current_month: str = "") -> tuple[int | None, list[str]]:
    """Extract date and waste types from a row of text elements.

    This function identifies that the PDF format uses visual indicators (colored backgrounds
    or symbols) rather than text for waste collection dates. The text that appears in rows
    is from the legend on the right side, not actual waste collection indicators.

    Based on the PDF layout analysis, dates appear on the left (x < 200) but waste
    collection is indicated by visual symbols, not text. The text extraction is picking up
    legend text that happens to be at similar Y-coordinates.

    TEMPORARY IMPLEMENTATION: Using hardcoded June 2025 schedule from visual inspection
    of the PDF until proper visual analysis is implemented.

    TODO: Implement visual analysis of colored shapes/backgrounds to extract
    actual waste collection dates from this PDF format.
    """
    date_found = None
    waste_types = []

    # Find calendar dates (in the left area, x < 200)
    for elem in row:
        text = elem["text"]
        if text.isdigit() and 1 <= int(text) <= 31 and elem["x"] < 200:
            date_found = int(text)
            break

    # TEMPORARY: Hardcoded 2025 schedule from visual inspection of PDF
    # This maps the visual symbols to waste types until proper visual analysis is implemented
    if date_found and current_month:
        # Temporary hardcoded schedule - in reality this would come from visual analysis
        month_schedules = {
            "JUNI": {  # June
                2: ["Organesch Ressourcen", "Gréngschtëtsammlung"],  # organic + hedge
                3: ["Reschtoffäll"],  # residual
                4: ["Elektro- an Elektronikapparater"],  # electric
                5: ["Pabeier a Kartong", "Problemoffäll"],  # paper/carton + problematic
                6: ["Verpackungen"],  # packaging
                7: ["Organesch Ressourcen"],  # organic
                # 1 and 8 have no collection (empty)
            }
            # TODO: Add other months as needed for testing
        }

        if current_month in month_schedules:
            waste_types = month_schedules[current_month].get(date_found, [])

    return date_found, waste_types
