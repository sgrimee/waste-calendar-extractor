<div align="center">
  <img src="icons/icon.png" alt="Waste Calendar Extractor" width="128" height="128">
  
# Waste Calendar Extractor for Luxembourg Communes 🇱🇺

</div>

[![CI](https://github.com/sgrimee/waste-calendar-extractor/actions/workflows/ci.yml/badge.svg)](https://github.com/sgrimee/waste-calendar-extractor/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## 📅 Quick Start

### 🇱🇺 Lëtzebuergesch

Offall-Kalenner fir Är Gemeng. Kopéiert de Link an Är Kalenner-App (Google Calendar, Apple Calendar, etc.) fir automatesch all d'Offall-Datumer mat Ikouen an Erënnerungen ze kréien!

Wéi maacht een :

Kopéiert dëse Link ☝️
Op Är Kalenner-App opmaachen (Google Calendar, Apple Calendar, etc.)
Sicht "Kalenner importéieren" oder "Am Kalenner abonnéieren"
De Link derbäisetzen - Är Apparat kritt automatesch all d'Offall-Datumer mat Ikouen an Erënnerungen op Lëtzebuergesch !

| Gemeng | Link |
|--------|------|
| Nidderaanwen | `https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/waste-niederanven-lu.ics` |

**[➜ Alle Gemeinden (86+)](COMMUNES.md)** - Available via public CSV data source

---

### 🇫🇷 Français

Calendrier des déchets pour votre commune. Copiez le lien dans votre application calendrier (Google Calendar, Apple Calendar, etc.) pour recevoir automatiquement toutes les dates de collecte avec des icônes et des rappels !

Comment faire :

Copiez ce lien ☝️
Ouvrez votre app calendrier (Google Calendar, Apple Calendar, etc.)
Cherchez "Importer calendrier" ou "S'abonner au calendrier"
Ajoutez le lien - votre appareil recevra automatiquement toutes les dates de collecte avec des icônes et des rappels en français !

| Commune | Lien |
|---------|------|
| Niederanven | `https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/waste-niederanven-fr.ics` |

**[➜ Toutes les communes (86+)](COMMUNES.md)** - Disponibles via la source de données publique CSV

---

### 🇬🇧 English

Waste collection calendar for your commune. Copy the link into your calendar app (Google Calendar, Apple Calendar, etc.) to automatically get all collection dates with icons and reminders!

How to do it:

Copy this link ☝️
Open your calendar app (Google Calendar, Apple Calendar, etc.)
Look for "Import calendar" or "Subscribe to calendar"
Add the link - your device will automatically receive all collection dates with icons and reminders in English!

| Commune | Link |
|---------|------|
| Niederanven | `https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/waste-niederanven-en.ics` |

**[➜ See all available communes (86+)](COMMUNES.md)** - Available via public CSV data source

---

**💡 Pro tip:** Subscribe to the URL in your calendar app for automatic updates when new calendars are published!

---

## About This Tool

A Python tool to extract waste collection dates from official sources published by **Luxembourg communes** and generate iCal files for easy calendar integration. Supports two data sources:

- **PDF-based extraction** (Niederanven) - Extracts from official PDF calendars
- **CSV data source** (86+ communes) - Integrates with Luxembourg's public waste collection dataset from [data.public.lu](https://data.public.lu/fr/datasets/r/c3805ec5-7836-49a4-9983-effaf81910d0)

### ⚠️ Important Disclaimer

**This is an unofficial hobby project and is not endorsed by, affiliated with, or maintained by any Luxembourg commune.** The data extracted from PDF calendars may be inaccurate or incomplete.

**No warranty or guarantee is provided regarding the accuracy, completeness, or reliability of the waste collection information.** Users are responsible for verifying collection dates independently and should not rely solely on this tool for waste collection scheduling.

**The developer assumes no responsibility or liability for any consequences arising from the use of this software or the calendar data it generates, including but not limited to missed collections, fines, or other damages.**

For official and authoritative waste collection information, always consult the official resources provided by your commune.

## Source Data

This tool integrates data from official sources:

### PDF-based Source (1 commune)
- **Niederanven**: [Official website](https://www.niederanven.lu/en/environment/waste-disposal-management)

### CSV Data Source (86+ communes)
- **Luxembourg Public Waste Data**: [data.public.lu](https://data.public.lu/fr/datasets/r/c3805ec5-7836-49a4-9983-effaf81910d0)
- **Coverage**: All Luxembourg communes with rolling collection schedules
- **Update frequency**: Automatic weekly regeneration via GitHub Actions

⚠️ **Note on data completeness**: Some communes do not publish all collection types in the CSV data source. For example, Contern publishes electrical waste (Déchets d'équipements électriques et électroniques), bulky waste (Déchets encombrants), and tree/hedge trimmings (Tailles d'arbres et de haies) on their official PDF calendar, but these collection types are missing from the data.public.lu CSV feed. For complete collection information, always verify against your commune's official calendar.

## Features

- 📄 **Dual data sources**: Extract from PDF calendars or CSV data feeds
- 📅 Extracts dates and collection types from official waste collection sources
- 🇱🇺 Supports Luxembourgish month names and multilingual waste descriptions
- 📁 Generates iCal (.ics) files for calendar import
- ⏰ **Smart reminder alarms** - Get notified at 20:30 the day before regular waste collections (residual, organic, paper, packaging, glass)
- 🌍 **Multilingual alarms** - Reminder messages in Luxembourgish, French, and English
- 🔄 **86+ communes supported** via public CSV data source with automatic weekly updates
- 🔍 Real-time logging shows extraction progress
- 🧪 Comprehensive unit tests
- 📦 Modular, well-documented code

## 🔔 Reminder Alarms

The generated calendars include **smart reminder alarms** to help you never miss a collection day:

### ⏰ When You'll Be Reminded
- **Time**: 20:30 (8:30 PM) the day before collection
- **Which collections**: Only regular waste types that require preparation:
  - 🗑️ Residual waste (Reschtoffäll / Déchets ménagers)
  - 🥬 Organic waste (Organesch Ressourcen / Déchets organiques) 
  - 📄 Paper and cardboard (Pabeier a Kartong / Papier et carton)
  - 📦 Packaging (Verpackungen / Emballages)
  - 🍾 Glass (Glas / Verre)

### 🚫 No Alarms For
Special collections that require advance preparation:
- 🔌 Electric waste, 🌿 Hedge trimmings, ☣️ Problematic waste, 🛏️ Bulky items, 👕 Clothes, 🎄 Christmas trees

### 🌍 Multilingual Messages
Alarm messages are automatically localized:
- **🇱🇺 Luxembourgish**: "Moien! Denkt drun: [waste type] gëtt muer ofgeholl."
- **🇫🇷 French**: "Rappel: [waste type] sera collecté demain."
- **🇬🇧 English**: "Reminder: [waste type] will be collected tomorrow."

### 📱 Calendar Compatibility
Alarms work with most modern calendar applications:
- Google Calendar (Android/Web)
- Apple Calendar (iOS/macOS)
- Outlook (Windows/Web)
- Most other iCal-compatible calendar apps

---

## For Developers

Everything below this line is **not required** if you just want to use the pre-generated calendars above. The following instructions are for developers who want to customize the tool, regenerate calendars from new PDFs, or contribute to the project.

---

## Installation

```bash
git clone https://github.com/yourusername/waste-calendar-extractor.git
cd waste-calendar-extractor
uv sync
```

## Justfile Recipes

For convenience, this project includes justfile recipes that handle the CLI commands for you:

```bash
# Generate all languages for a commune and year
just generate-commune niederanven 2026

# Generate ADYS calendars for a customer and year
just generate-adys 019027 2026

# Generate calendars from CSV data source
just list-csv-communes sources/waste-data-public.csv
just generate-csv-commune sources/waste-data-public.csv niederanven
just generate-all-csv sources/waste-data-public.csv
```

## Usage

### PDF-based extraction

```bash
# Generate calendars for Niederanven (all languages)
uv run waste-cal --commune niederanven --pdf sources/waste-niederanven-2026.pdf

# Generate ADYS calendars
uv run waste-cal --adys --pdf sources/adys-019027-2026.pdf
```

### CSV-based extraction (86+ communes)

```bash
# List available communes in CSV
uv run waste-cal --csv sources/waste-data-public.csv --list-communes

# Generate calendars for a specific commune
uv run waste-cal --csv sources/waste-data-public.csv --commune niederanven

# Generate calendars for a specific commune in a specific language
uv run waste-cal --csv sources/waste-data-public.csv --commune niederanven --language fr

# Generate calendars for all communes in CSV
uv run waste-cal --csv sources/waste-data-public.csv --all-communes
```

### Advanced usage

```bash
# Generate calendars with custom PDF file
uv run waste-cal --commune niederanven --pdf my-calendar.pdf

# Custom year (when PDF filename doesn't match)
uv run waste-cal --commune niederanven --pdf sources/waste-niederanven-2026.pdf --year 2026

# Output as text instead of generating iCal files
uv run waste-cal --commune niederanven --pdf sources/waste-niederanven-2026.pdf --text

# Verbose logging
uv run waste-cal --commune niederanven --pdf sources/waste-niederanven-2026.pdf --verbose

# Text output from CSV
uv run waste-cal --csv sources/waste-data-public.csv --commune niederanven --text --language en
```

## Command Line Options

### Data Source (mutually exclusive)
- `--pdf PDF_PATH`: Path to PDF file (for Niederanven)
- `--csv CSV_PATH`: Path to CSV file (for 86+ communes via data.public.lu)

### Mode Selection
- `--commune COMMUNE_NAME`: Generate calendar for specific commune
- `--all-communes`: Generate calendars for all communes in CSV
- `--list-communes`: List all available communes in CSV
- `--adys`: Generate ADYS calendar (requires --pdf)

### Options
- `-l, --language {lu,fr,en}`: Language for output (default: all languages)
- `-y, --year YEAR`: Year for calendar extraction (default: current year)
- `--text`: Output as text instead of generating iCal files
- `-v, --verbose`: Enable verbose logging
- `-h, --help`: Show help message and exit

### Drawings Subcommand

This is used only for debugging.

- `month`: Month name to extract drawings from (january, february, march, april, may, june, july, august, september, october, november, december)
- `--pdf PDF_PATH`: Path to PDF file (required)
- `-o, --output-dir OUTPUT_DIR`: Output directory for drawing images (default: debug)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
