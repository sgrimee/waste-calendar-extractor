#!/usr/bin/env python3
"""
Output generation functions for waste collection calendars.
"""

import logging
import urllib.request

from ics import Calendar, Event


def extract_language_from_waste_description(description: str, language: str) -> str:
    """Extract language-specific part from multilingual waste description, preserving additional information."""
    # Split by | to get different language variants
    parts = [part.strip() for part in description.split("|") if part.strip()]

    # If no parts or only one part, return original description
    if len(parts) <= 1:
        return description.strip()

    # Language-specific patterns - prefer parts that contain language-specific terms
    if language == "de":  # German/Luxembourgish
        # Look for German/Luxembourgish terms first
        for part in parts:
            if any(
                de_term in part.lower()
                for de_term in [
                    "reschtoffäll",
                    "pabeier",
                    "kartong",
                    "glas",
                    "verpackungen",
                    "organesch",
                    "ressourcen",
                    "aalt",
                    "gezei",
                    "beemercher",
                ]
            ):
                return part
        # Look for terms that are NOT clearly French or English
        for part in parts:
            if not any(
                fr_term in part.lower()
                for fr_term in [
                    "déchets",
                    "ménagers",
                    "papier et carton",
                    "verre",
                    "emballages",
                    "organiques",
                    "vêtements",
                    "sapins de noël",
                ]
            ) and not any(
                en_term in part.lower()
                for en_term in ["residual waste", "paper and carton", "old clothes", "christmas trees"]
            ):
                return part
        # Fallback to first non-empty part
        return parts[0] if parts else description.strip()

    elif language == "fr":  # French
        # Look for French terms
        for part in parts:
            if any(
                fr_term in part.lower()
                for fr_term in [
                    "déchets",
                    "ménagers",
                    "papier et carton",
                    "verre",
                    "emballages",
                    "ressources",
                    "organiques",
                    "vêtements",
                    "sapins de noël",
                ]
            ):
                return part
        # Fallback to middle part if available, then first
        return parts[1] if len(parts) > 1 else parts[0] if parts else description.strip()

    elif language == "en":  # English
        # Look for English terms
        for part in parts:
            if any(
                en_term in part.lower()
                for en_term in [
                    "residual waste",
                    "paper and carton",
                    "glass",
                    "packaging",
                    "organic",
                    "resources",
                    "old clothes",
                    "christmas trees",
                ]
            ):
                return part
        # Look for terms that are clearly English (not French/German)
        for part in parts:
            if (
                any(
                    en_word in part.lower() for en_word in ["waste", "paper", "carton", "glass", "packaging", "clothes"]
                )
                and not any(
                    fr_term in part.lower() for fr_term in ["déchets", "papier et", "verre", "emballages", "vêtements"]
                )
                and not any(de_term in part.lower() for de_term in ["reschtoffäll", "pabeier", "glas"])
            ):
                return part
        # Fallback to last non-empty part
        return parts[-1] if parts else description.strip()

    # Default fallback
    return description.strip()


def get_waste_type_icon(description: str) -> str:
    """Get an appropriate emoji icon for the waste collection type."""
    description_lower = description.lower()

    # Residual/household waste
    if any(term in description_lower for term in ["reschtoffäll", "déchets ménagers", "residual waste", "hausmüll"]):
        return "🗑️"

    # Paper and cardboard
    elif any(term in description_lower for term in ["pabeier", "papier", "paper", "carton", "kartong"]):
        return "📄"

    # Glass
    elif any(term in description_lower for term in ["glas", "verre", "glass"]):
        return "🪟"

    # Packaging/VALORLUX
    elif any(term in description_lower for term in ["verpackungen", "emballages", "packaging", "valorlux"]):
        return "📦"

    # Organic waste
    elif any(
        term in description_lower for term in ["organesch", "organiques", "organic", "bio", "ressourcen", "resources"]
    ):
        return "🌱"

    # Old clothes/textiles
    elif any(term in description_lower for term in ["aalt gezei", "vêtements", "clothes", "textile"]):
        return "👕"

    # Christmas trees
    elif any(term in description_lower for term in ["beemercher", "sapins", "christmas trees", "tannen"]):
        return "🎄"

    # Default waste icon
    else:
        return "♻️"


def generate_ical_calendar(
    results: list[dict], output_path: str | None = None, year: int = 2025, language: str | None = None
) -> int:
    """Generate iCal calendar file from extraction results."""

    if output_path is None:
        if language:
            output_path = f"waste-{year}-{language}.ics"
        else:
            output_path = f"waste-{year}.ics"

    logging.info(f"Generating iCal calendar{' for ' + language if language else ''}...")
    calendar = Calendar()

    events_added = 0
    for entry in results:
        if entry["icons"].strip():  # Only add events with actual content
            event = Event()

            # Extract language-specific description if language is specified
            if language:
                localized_name = extract_language_from_waste_description(entry["icons"], language)
                # Get appropriate icon for the waste type
                icon = get_waste_type_icon(localized_name)
                event.name = f"{icon} {localized_name}"
                event.description = f"Waste collection: {localized_name}"
            else:
                # Get appropriate icon for the waste type
                icon = get_waste_type_icon(entry["icons"])
                event.name = f"{icon} {entry['icons']}"
                event.description = f"Waste collection: {entry['icons']}"

            # Set as all-day event using date (not datetime)
            event.begin = entry["date"].date()
            event.make_all_day()

            # Set location (optional - can be customized)
            event.location = "Niederanven, Luxembourg"

            calendar.events.add(event)
            events_added += 1

    logging.info(f"Added {events_added} events to calendar.")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(str(calendar))

    logging.info(f"Calendar saved as '{output_path}'")
    return events_added


def generate_all_language_calendars(results: list[dict], year: int = 2025) -> dict[str, int]:
    """Generate calendar files for all supported languages."""
    languages = ["de", "fr", "en"]  # German, French, English
    generated = {}

    for lang in languages:
        events_added = generate_ical_calendar(results, None, year, lang)
        generated[lang] = events_added
        logging.info(f"Generated waste-{year}-{lang}.ics with {events_added} events")

    return generated


def download_calendar_pdf(url: str, output_path: str) -> bool:
    """Download the waste calendar PDF from the commune website."""
    try:
        logging.info(f"Downloading calendar PDF from: {url}")
        urllib.request.urlretrieve(url, output_path)
        logging.info(f"Successfully downloaded PDF to: {output_path}")
        return True
    except Exception as e:
        logging.error(f"Failed to download PDF: {e}")
        return False
