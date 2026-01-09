"""
CSV data source extraction module for waste collection calendars.

This module extracts waste collection data from public.data.lu CSV files,
handles UTF-8 BOM, semicolon delimiters, and deduplicates street-level data.
"""

import csv
import datetime
import logging

from waste_cal.calendar_processor import CalendarData
from waste_cal.waste_types import WasteType

logger = logging.getLogger(__name__)

# Mapping from CSV French collection types to WasteType enum
CSV_TYPE_MAPPING = {
    "Biodéchets": WasteType.ORGANIC,
    "Déchets ménagers en mélange": WasteType.RESIDUAL,
    "Papier/Carton": WasteType.PAPER,
    "Papier/Carton (commerces)": WasteType.PAPER_COMMERCIAL,
    "Valorlux": WasteType.PACKAGING,
    "Verre": WasteType.GLASS,
    "Verre (commerces)": WasteType.GLASS_COMMERCIAL,
    "Déchets d’équipements électriques et électroniques": WasteType.ELECTRIC,
    "Déchets de verdure": WasteType.HEDGE,
    "SuperDrecksKëscht": WasteType.PROBLEMATIC,
    "Déchets encombrants": WasteType.BULKY,
    "Vieux vêtements": WasteType.CLOTHERS,
    "Arbres de Noël": WasteType.CHRISTMAS_TREES,
    "Ferraille": WasteType.SCRAP_METAL,
    "Vieux bois": WasteType.OLD_WOOD,
    "Déchets recyclables": WasteType.RECYCLABLE,
    "Conteneur pour déchets ménagers": WasteType.CONTAINER,
}


def _parse_csv(csv_path: str) -> list[dict]:
    """
    Parse semicolon-delimited CSV with UTF-8 BOM.

    Handles:
    - UTF-8 BOM (as present in data.public.lu export)
    - Semicolon field delimiter
    - Quoted fields

    Args:
        csv_path: Path to the CSV file

    Returns:
        List of dicts with keys: date, type, commune, locality, street
    """
    rows = []

    try:
        with open(csv_path, encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=";")
            if reader.fieldnames is None:
                raise ValueError("CSV file is empty or has no headers")

            for _, row in enumerate(reader, 1):
                # Normalize keys by stripping whitespace and quotes
                normalized_row = {}
                for key, value in row.items():
                    if key:
                        normalized_key = key.strip().strip('"')
                        normalized_value = value.strip().strip('"') if value else ""
                        normalized_row[normalized_key] = normalized_value

                rows.append(normalized_row)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"CSV file not found: {csv_path}") from e

    return rows


def _parse_date(date_str: str) -> datetime.date:
    """
    Parse DD/MM/YYYY format from CSV.

    Args:
        date_str: Date string in format "DD/MM/YYYY"

    Returns:
        datetime.date object

    Raises:
        ValueError: If date string is not in correct format or invalid
    """
    try:
        return datetime.datetime.strptime(date_str, "%d/%m/%Y").date()
    except ValueError as e:
        raise ValueError(f"Invalid date format '{date_str}', expected DD/MM/YYYY") from e


def _csv_type_to_waste_type(french_type: str) -> WasteType | None:
    """
    Map CSV French collection type to WasteType enum.

    Args:
        french_type: Collection type from CSV (in French)

    Returns:
        WasteType enum value, or None if unknown type (logs warning)
    """
    waste_type = CSV_TYPE_MAPPING.get(french_type)
    if waste_type is None:
        logger.warning(f"Unknown waste type from CSV: '{french_type}'")
    return waste_type


def get_communes(csv_path: str) -> list[str]:
    """
    Extract unique commune names from CSV.

    Args:
        csv_path: Path to the CSV file

    Returns:
        Sorted list of unique commune names (excluding 'Commune' header)
    """
    rows = _parse_csv(csv_path)
    communes = set()

    for row in rows:
        commune = row.get("Commune", "").strip()
        if commune and commune != "Commune":
            communes.add(commune)

    return sorted(communes)


def extract_calendar_data_from_csv(csv_path: str, commune: str) -> CalendarData:
    """
    Extract deduplicated waste collections for a commune from CSV.

    Deduplicates by (date, type, commune) - ignores street column.
    Handles both commune-wide ('Toutes les rues') and street-level data.

    Args:
        csv_path: Path to the CSV file
        commune: Commune name to extract (must be in CSV)

    Returns:
        CalendarData object compatible with ical_generator.py

    Raises:
        FileNotFoundError: If CSV file not found
        ValueError: If commune not found in CSV
    """
    rows = _parse_csv(csv_path)

    # Verify commune exists
    available_communes = get_communes(csv_path)
    if commune not in available_communes:
        raise ValueError(
            f"Commune '{commune}' not found in CSV. Available communes: {', '.join(available_communes[:10])}..."
        )

    # Extract and deduplicate collections for the commune
    calendar_data = CalendarData()
    seen_entries = set()

    for row in rows:
        row_commune = row.get("Commune", "").strip()

        # Only process rows for the requested commune
        if row_commune != commune:
            continue

        # Extract and parse date
        date_str = row.get("Date", "").strip()
        if not date_str:
            continue

        try:
            date = _parse_date(date_str)
        except ValueError as e:
            logger.warning(f"Skipping row with invalid date: {e}")
            continue

        # Extract and map waste type
        type_str = row.get("Type de collecte", "").strip()
        if not type_str:
            continue

        waste_type = _csv_type_to_waste_type(type_str)
        if waste_type is None:
            continue

        # Deduplicate by (date, type) - street column is ignored
        entry_key = (date, waste_type)
        if entry_key not in seen_entries:
            seen_entries.add(entry_key)
            calendar_data.add_collection(date, waste_type)

    return calendar_data
