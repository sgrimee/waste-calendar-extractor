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

| Gemeng | Link |
|--------|------|
| Nidderaanwen | `https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/waste-niederanven-lu.ics` |
| Schëtter | `https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/waste-schuttrange-lu.ics` |

---

### 🇫🇷 Français

Calendrier des déchets pour votre commune. Copiez le lien dans votre application calendrier (Google Calendar, Apple Calendar, etc.) pour recevoir automatiquement toutes les dates de collecte avec des icônes et des rappels !

| Commune | Lien |
|---------|------|
| Niederanven | `https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/waste-niederanven-fr.ics` |
| Schuttrange | `https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/waste-schuttrange-fr.ics` |

---

### 🇬🇧 English

Waste collection calendar for your commune. Copy the link into your calendar app (Google Calendar, Apple Calendar, etc.) to automatically get all collection dates with icons and reminders!

| Commune | Link |
|---------|------|
| Niederanven | `https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/waste-niederanven-en.ics` |
| Schuttrange | `https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/waste-schuttrange-en.ics` |

---

**💡 Pro tip:** Subscribe to the URL in your calendar app for automatic updates when new calendars are published!

---

## About This Tool

A Python tool to extract waste collection dates from PDF calendars published by **Luxembourg communes** (currently Niederanven and Schuttrange) and generate iCal files for easy calendar integration.

### ⚠️ Important Disclaimer

**This is an unofficial hobby project and is not endorsed by, affiliated with, or maintained by any Luxembourg commune.** The data extracted from PDF calendars may be inaccurate or incomplete.

**No warranty or guarantee is provided regarding the accuracy, completeness, or reliability of the waste collection information.** Users are responsible for verifying collection dates independently and should not rely solely on this tool for waste collection scheduling.

**The developer assumes no responsibility or liability for any consequences arising from the use of this software or the calendar data it generates, including but not limited to missed collections, fines, or other damages.**

For official and authoritative waste collection information, always consult the official resources provided by your commune.

## Source Data

This tool extracts data from official waste collection calendars published by Luxembourg communes:

- **Niederanven**: [Official website](https://www.niederanven.lu/en/environment/waste-disposal-management)
- **Schuttrange**: [data.public.lu](https://data.public.lu/fr/datasets/r/c3805ec5-7836-49a4-9983-effaf81910d0)

## Features

- 📅 Extracts dates and collection types from PDF waste collection calendars
- 🇱🇺 Supports Luxembourgish month names and multilingual waste descriptions
- 📁 Generates iCal (.ics) files for calendar import
- ⏰ **Smart reminder alarms** - Get notified at 20:30 the day before regular waste collections (residual, organic, paper, packaging, glass)
- 🌍 **Multilingual alarms** - Reminder messages in Luxembourgish, French, and English
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

### 📱 Device Compatibility
Alarms work with most modern calendar applications:
- ✅ Google Calendar (Android/Web)
- ✅ Apple Calendar (iOS/macOS)
- ✅ Outlook (Windows/Web)
- ✅ Most other iCal-compatible calendar apps

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
just generate-commune schuttrange 2026

# Generate ADYS calendars for a customer and year
just generate-adys 019027 2026
```

## Usage

### Basic usage

```bash
# Generate calendars for a commune (all languages)
uv run waste-cal --commune niederanven --pdf pdf/waste-niederanven-2026.pdf
uv run waste-cal --commune schuttrange --pdf pdf/waste-schuttrange-2026.pdf

# Generate ADYS calendars
uv run waste-cal --adys --pdf pdf/adys-019027-2026.pdf
```

### Advanced usage

```bash
# Generate calendars with custom PDF file
uv run waste-cal --commune niederanven --pdf my-calendar.pdf

# Custom year (when PDF filename doesn't match)
uv run waste-cal --commune niederanven --pdf pdf/waste-niederanven-2026.pdf --year 2026

# Output as text instead of generating iCal files
uv run waste-cal --commune niederanven --pdf pdf/waste-niederanven-2026.pdf --text

# Verbose logging
uv run waste-cal --commune niederanven --pdf pdf/waste-niederanven-2026.pdf --verbose
```

## Command Line Options

- `--commune {niederanven,schuttrange}`: Commune to generate calendar for
- `--adys`: Generate ADYS calendar (requires --pdf)
- `--pdf PDF_PATH`: Path to PDF file (required)
- `-l, --language {lu,fr,en}`: Language for --text output. If omitted, shows all languages
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
