#!/usr/bin/env python3
"""
Output generation functions for waste collection calendars.
"""

import logging
import re
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


def find_pdf_links_from_webpage(url: str) -> list[str]:
    """
    Scrape webpage to find PDF links related to waste calendar.
    Returns list of found PDF URLs.
    """
    try:
        # Add headers to mimic a browser request
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                )
            },
        )

        with urllib.request.urlopen(request, timeout=10) as response:
            html_content = response.read().decode("utf-8")

        # Look for PDF links in the HTML content with specific patterns for Niederanven
        pdf_patterns = [
            r'href=["\']([^"\']*ressourcekalenner[^"\']*\.pdf[^"\']*)["\']',  # ressourcekalenner PDF (priority)
            r'href=["\']([^"\']*ressource[^"\']*\.pdf[^"\']*)["\']',  # ressource calendar PDF
            r'href=["\']([^"\']*calendar[^"\']*\.pdf[^"\']*)["\']',  # calendar PDF
            r'href=["\']([^"\']*waste[^"\']*\.pdf[^"\']*)["\']',  # waste PDF
            r'href=["\']([^"\']*nidderaanwen[^"\']*\.pdf[^"\']*)["\']',  # Niederanven-specific PDF
            r'href=["\']([^"\']*\.pdf[^"\']*)["\']',  # any PDF
        ]

        # Find all links first for debugging
        all_links = re.findall(r'href=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
        pdf_links = [link for link in all_links if ".pdf" in link.lower()]
        logging.debug(f"Found {len(all_links)} total links, {len(pdf_links)} PDF links")

        found_pdfs = []

        # Try patterns in order of priority
        for pattern in pdf_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                # Make URL absolute if needed
                if match.startswith("/"):
                    base_url = "/".join(url.split("/")[:3])  # https://domain.com
                    match = base_url + match
                elif not match.startswith("http"):
                    base_url = "/".join(url.split("/")[:-1])  # Remove last part
                    match = base_url + "/" + match

                if match not in found_pdfs:
                    found_pdfs.append(match)

        logging.debug(f"Found {len(found_pdfs)} potential PDF URLs: {found_pdfs}")
        return found_pdfs

    except Exception as e:
        logging.warning(f"Failed to scrape webpage for PDF links: {e}")
        return []


def download_calendar_pdf(url: str, output_path: str) -> bool:
    """
    Download the waste calendar PDF using a robust multi-strategy approach.

    Strategy:
    1. Try direct PDF download if URL ends with .pdf
    2. Try scraping the webpage for PDF links
    3. Fall back to known working PDF URLs for Niederanven
    """

    # Known working PDF URLs as fallbacks (can be updated as needed)
    fallback_urls = [
        "https://www.niederanven.lu/media/aefb09c8-9716-4141-bee0-1c2ac3a7557b/ressourcekalenner-nidderaanwen-web.pdf",
        # Add more known URLs here as they are discovered
    ]

    urls_to_try = []

    # Strategy 1: Direct PDF download
    if url.endswith(".pdf"):
        urls_to_try.append(url)
        logging.info(f"Attempting direct PDF download from: {url}")
    else:
        # Strategy 2: Scrape webpage for PDF links
        logging.info(f"Scraping webpage for PDF links: {url}")
        scraped_pdfs = find_pdf_links_from_webpage(url)
        urls_to_try.extend(scraped_pdfs)

        # Strategy 3: Add fallback URLs if scraping didn't find anything
        if not scraped_pdfs:
            logging.info("No PDF links found by scraping, trying fallback URLs")
            urls_to_try.extend(fallback_urls)

    # Remove duplicates while preserving order
    seen = set()
    unique_urls = []
    for u in urls_to_try:
        if u not in seen:
            seen.add(u)
            unique_urls.append(u)
    urls_to_try = unique_urls

    if not urls_to_try:
        logging.error("No PDF URLs to try")
        return False

    # Try each URL until one works
    for i, pdf_url in enumerate(urls_to_try):
        try:
            logging.info(f"Attempting download {i + 1}/{len(urls_to_try)}: {pdf_url}")

            # Add headers to mimic browser request
            request = urllib.request.Request(
                pdf_url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    )
                },
            )

            # Download the PDF
            with urllib.request.urlopen(request, timeout=30) as response:
                with open(output_path, "wb") as f:
                    f.write(response.read())

            # Verify it's actually a PDF file
            with open(output_path, "rb") as f:
                header = f.read(4)
                if header != b"%PDF":
                    logging.warning(f"Downloaded file is not a valid PDF (header: {header!r}), trying next URL")
                    continue

            logging.info(f"Successfully downloaded PDF to: {output_path}")
            logging.info(f"Working PDF URL: {pdf_url}")
            return True

        except Exception as e:
            logging.warning(f"Failed to download from {pdf_url}: {e}")
            continue

    # If we get here, all URLs failed
    logging.error("Failed to download PDF from any of the attempted URLs")
    logging.error("Manual intervention required:")
    logging.error("1. Visit https://www.niederanven.lu/en/environment/waste-disposal-management")
    logging.error("2. Look for the waste calendar PDF download")
    logging.error("3. Copy the direct PDF URL and use --download-url parameter")
    logging.error(
        "Example: python -m waste_calendar_extractor --download --download-url 'https://..../ressourcekalenner.pdf'"
    )
    return False
