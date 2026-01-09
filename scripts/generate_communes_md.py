#!/usr/bin/env python3
"""
Generate COMMUNES.md with links to all available waste calendar ICS files.

This script scans the ics/ directory for waste-{commune}-{lang}.ics files,
extracts commune names, and generates markdown tables with download links
for each supported language.
"""

import re
from datetime import datetime
from pathlib import Path


def generate_communes_md(ics_dir: str = "ics", output_file: str = "COMMUNES.md") -> None:
    """
    Generate COMMUNES.md with links to all available ICS files.

    Scans ics/ directory for waste-{commune}-{lang}.ics files,
    extracts commune names, and generates markdown tables.

    Args:
        ics_dir: Directory containing ICS files
        output_file: Output markdown file path
    """
    ics_path = Path(ics_dir)

    if not ics_path.exists():
        print(f"Error: {ics_dir} directory not found")
        return

    # Pattern to match waste-{commune}-{lang}.ics files
    pattern = re.compile(r"waste-(.+)-(lu|fr|en)\.ics")

    # Collect files: {commune: {lang: filepath}}
    communes_data = {}

    for ics_file in ics_path.glob("waste-*.ics"):
        match = pattern.match(ics_file.name)
        if match:
            commune = match.group(1)
            lang = match.group(2)

            if commune not in communes_data:
                communes_data[commune] = {}

            communes_data[commune][lang] = ics_file.name

    if not communes_data:
        print(f"No waste calendar files found in {ics_dir}")
        return

    # Sort communes alphabetically
    sorted_communes = sorted(communes_data.keys())

    # Generate markdown content
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d")

    lines = [
        "# Available Waste Calendars by Commune",
        "",
        f"Last updated: {timestamp}",
        "",
        "## 🇱🇺 Lëtzebuergesch",
        "",
        "| Gemeng | Link |",
        "|--------|------|",
    ]

    # Luxembourgish table
    for commune in sorted_communes:
        if "lu" in communes_data[commune]:
            filename = communes_data[commune]["lu"]
            url = f"https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/{filename}"
            lines.append(f"| {commune} | [`{filename}`]({url}) |")

    lines.extend(["", "## 🇫🇷 Français", "", "| Commune | Lien |", "|---------|------|"])

    # French table
    for commune in sorted_communes:
        if "fr" in communes_data[commune]:
            filename = communes_data[commune]["fr"]
            url = f"https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/{filename}"
            lines.append(f"| {commune} | [`{filename}`]({url}) |")

    lines.extend(["", "## 🇬🇧 English", "", "| Commune | Link |", "|---------|------|"])

    # English table
    for commune in sorted_communes:
        if "en" in communes_data[commune]:
            filename = communes_data[commune]["en"]
            url = f"https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/{filename}"
            lines.append(f"| {commune} | [`{filename}`]({url}) |")

    # Write to file
    output_path = Path(output_file)
    output_path.write_text("\n".join(lines) + "\n")
    print(f"Generated {output_file} with {len(sorted_communes)} communes")


if __name__ == "__main__":
    generate_communes_md()
