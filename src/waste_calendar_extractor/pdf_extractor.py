#!/usr/bin/env python3
"""
PDF extraction utilities for waste collection calendars.
"""

import fitz  # PyMuPDF

from .constants import MONTH_NAMES, WASTE_TYPE_KEYWORDS


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
