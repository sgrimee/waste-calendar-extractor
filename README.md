<div align="center">
  <img src="icons/icon.png" alt="Waste Calendar Extractor" width="128" height="128">
  
# Waste Calendar Extractor for Niederanven, Luxembourg 🇱🇺

</div>

[![CI](https://github.com/sgrimee/waste-calendar-extractor/actions/workflows/ci.yml/badge.svg)](https://github.com/sgrimee/waste-calendar-extractor/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## 📅 Quick Start

**Choose your preferred language for the calendar / Wielt Är gewënschte Sprooch / Wählen Sie Ihre Sprache / Choisissez votre langue :**

📋 **[🇱🇺 Lëtzebuergesch](#-lëtzebuergesch)** | **[🇩🇪 Deutsch](#-deutsch)** | **[🇫🇷 Français](#-français)** | **[🇬🇧 English / All Languages](#-english--all-languages)**

---

### 🇱🇺 **Lëtzebuergesch**

**Link fir den Offall-Kalenner op Lëtzebuergesch:**

```link
https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/waste-de.ics
```

**Wéi maachen:**

1. Kopéiert dësen Link ☝️
2. Gitt an Är Kalenner-App (Google Calendar, Apple Calendar, etc.)
3. Sicht no "Kalenner importéieren" oder "Kalenner abonnéieren"
4. Fügt den Link an - Är Telefon gëtt automatesch all d'Offall-Datumer mat Ikouen!

---

### 🇩🇪 **Deutsch**

**Link für den Müllkalender auf Deutsch:**

```link
https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/waste-de.ics
```

**So geht's:**

1. Kopieren Sie diesen Link ☝️
2. Öffnen Sie Ihre Kalender-App (Google Kalender, Apple Kalender, etc.)
3. Suchen Sie nach "Kalender importieren" oder "Kalender abonnieren"
4. Fügen Sie den Link hinzu - Ihr Handy bekommt automatisch alle Mülltermine mit Icons auf Deutsch!

---

### 🇫🇷 **Français**

**Lien pour le calendrier des déchets en français :**

```link
https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/waste-fr.ics
```

**Comment faire :**

1. Copiez ce lien ☝️
2. Ouvrez votre app calendrier (Google Calendar, Apple Calendar, etc.)
3. Cherchez "Importer calendrier" ou "S'abonner au calendrier"
4. Ajoutez le lien - votre téléphone recevra automatiquement toutes les dates de collecte avec des icônes en français !

---

### 🇬🇧 **English**

**Link for the waste collection calendar in English:**

```link
https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/waste-en.ics
```

**How to use:**

1. Copy this link ☝️
2. Open your calendar app (Google Calendar, Apple Calendar, etc.)
3. Look for "Import Calendar" or "Subscribe to Calendar"
4. Add the link - your phone will automatically get all waste collection dates with helpful emoji icons in English!

---

**💡 Pro tip:** Subscribe to the URL in your calendar app for automatic updates when new calendars are published!

---

## About This Tool

A Python tool to extract waste collection dates from PDF calendars published by the **Commune of Niederanven** and generate iCal files for easy calendar integration.

### ⚠️ Important Disclaimer

**This is an unofficial hobby project and is not endorsed by, affiliated with, or maintained by the Commune of Niederanven.** The data extracted from PDF calendars may be inaccurate or incomplete.

**No warranty or guarantee is provided regarding the accuracy, completeness, or reliability of the waste collection information.** Users are responsible for verifying collection dates independently and should not rely solely on this tool for waste collection scheduling.

**The developer assumes no responsibility or liability for any consequences arising from the use of this software or the calendar data it generates, including but not limited to missed collections, fines, or other damages.**

For official and authoritative waste collection information, always consult the official resources provided by the Commune of Niederanven.

## Source Data

This tool extracts data from the official waste collection calendar published by the **Commune of Niederanven**.

The original PDF calendar ("Ressourcekalenner") can be found on the [official Niederanven website](https://www.niederanven.lu/en/environment/waste-disposal-management). Visit their waste management section for the latest calendar updates.

## Features

- 📅 Extracts dates and collection types from PDF waste collection calendars
- 🇱🇺 Supports Luxembourgish month names and multilingual waste descriptions
- 📁 Generates iCal (.ics) files for calendar import
- 🔍 Real-time logging shows extraction progress
- 🧪 Comprehensive unit tests
- 📦 Modular, well-documented code

## Installation

### Using uv (recommended)

```bash
git clone https://github.com/yourusername/waste-calendar-extractor.git
cd waste-calendar-extractor
uv sync
```

### Using pip

```bash
git clone https://github.com/yourusername/waste-calendar-extractor.git
cd waste-calendar-extractor
pip install -e .
```

## Usage

### Basic usage

```bash
# Extract calendar from default PDF file (generates iCal files)
PYTHONPATH=src uv run python -m waste_cal extract

# Or use the shorthand
PYTHONPATH=src uv run python -m waste_cal
```

### Advanced usage

```bash
# Generate language-specific calendars
PYTHONPATH=src uv run python -m waste_cal extract --language de  # German/Luxembourgish
PYTHONPATH=src uv run python -m waste_cal extract --language fr  # French
PYTHONPATH=src uv run python -m waste_cal extract --language en  # English

# Specify custom PDF file
PYTHONPATH=src uv run python -m waste_cal extract my-calendar.pdf

# Custom year
PYTHONPATH=src uv run python -m waste_cal extract --year 2026

# Output as text instead of generating iCal files
PYTHONPATH=src uv run python -m waste_cal extract --text

# Text output in specific language
PYTHONPATH=src uv run python -m waste_cal extract --text --language de

# Extract drawings from specific month for analysis
PYTHONPATH=src uv run python -m waste_cal drawings january
PYTHONPATH=src uv run python -m waste_cal drawings march --output-dir my-debug

# Verbose logging
PYTHONPATH=src uv run python -m waste_cal extract --verbose

# Show help
PYTHONPATH=src uv run python -m waste_cal --help
PYTHONPATH=src uv run python -m waste_cal extract --help
PYTHONPATH=src uv run python -m waste_cal drawings --help
```

## Command Line Options

### Main Command

- `-v, --verbose`: Enable verbose logging
- `-h, --help`: Show help message and exit

### Extract Subcommand

- `pdf_file`: Path to PDF file (default: `pdf/ressourcekalenner-nidderaanwen-web.pdf`)
- `-l, --language {de,fr,en}`: Language for output (de=German/Luxembourgish, fr=French, en=English). For iCal: generates only specified language file. For text: uses specified language (default: en)
- `-y, --year YEAR`: Year for calendar extraction (default: current year)
- `--text`: Output as text instead of generating iCal files (default: generate iCal files)

### Drawings Subcommand

- `month`: Month name to extract drawings from (january, february, march, april, may, june, july, august, september, october, november, december)
- `pdf_file`: Path to PDF file (default: `pdf/ressourcekalenner-nidderaanwen-web.pdf`)
- `-o, --output-dir OUTPUT_DIR`: Output directory for drawing images (default: debug)

## Supported Waste Types

The extractor recognizes various waste collection types in multiple languages:

- **Residual waste** (Reschtoffäll, Déchets ménagers)
- **Paper & Carton** (Pabeier a Kartong, Papier et carton)
- **Glass** (Glas, Verre)
- **Packaging** (Verpackungen, Emballages, VALORLUX)
- **Organic waste** (Organesch Ressourcen, Ressources organiques)
- **Old clothes** (Aalt Gezei, Vieux vêtements)
- **Christmas trees** (Beemercher, Sapins de Noël)

## Development

This project uses [just](https://github.com/casey/just) for development commands:

```bash
# Install development dependencies
just install

# Run all tests
just test

# Run all checks (format, lint, type check)
just check

# Format code and fix issues
just format

# Lint code
just lint

# Type check with mypy
just typecheck

# Build package
just build

# Generate calendar for current year
just generate

# Generate calendar for specific year
just generate-year 2026
```

### Manual testing (without just)

```bash
# Run tests
PYTHONPATH=src uv run python -m pytest tests/ -v

# Run checks
uv run ruff check src/ tests/
PYTHONPATH=src uv run mypy src/ tests/
```

### Project structure

```bash
waste-calendar-extractor/
├── src/
│   └── waste_cal/
│       ├── __init__.py            # Package initialization
│       ├── __main__.py            # CLI entry point
│       ├── calendar_processor.py  # Calendar processing logic
│       ├── cli.py                 # Command line interface
│       ├── drawing.py             # Drawing analysis and classification
│       ├── ical_generator.py      # iCal file generation
│       ├── month.py               # Month processing
│       ├── pdf_extractor.py       # PDF text extraction
│       ├── waste_types.py         # Waste type definitions
│       ├── ics_viewer/            # Calendar viewing utilities
│       └── py.typed               # Type checking marker
├── tests/
│   └── unit/                     # Unit tests
│       ├── test_calendar_processor.py
│       ├── test_cli.py
│       ├── test_drawing.py
│       ├── test_ics_viewer.py
│       ├── test_month.py
│       ├── test_pdf_extractor.py
│       └── test_waste_types.py
├── RFC/                          # Technical documentation
│   ├── RFC-01-PDF_Areas_Documentation.md
│   ├── RFC-02-Waste-Type-Classification.md
│   └── best_practices.md
├── icons/
│   └── icon.png                  # Project icon
├── ics/
│   └── waste-*.ics               # Generated calendar files
├── pdf/
│   └── *.pdf                     # PDF source files
├── debug/
│   └── *.py                      # Debug and analysis scripts
├── justfile                      # Development commands
├── pyproject.toml                # Project configuration
├── CLAUDE.md                     # Claude Code instructions
├── README.md                     # This file
└── LICENSE                       # MIT license
```

## How it works

1. **PDF Analysis**: Uses PyMuPDF to extract positioned text elements from each page
2. **Month Detection**: Identifies Luxembourgish month names to track calendar progression
3. **Row Grouping**: Groups text elements by Y-coordinate to identify calendar rows
4. **Pattern Matching**: Matches dates (1-31) with waste type keywords in the same row
5. **iCal Generation**: Creates calendar events using the `ics` library

## Requirements

- Python >=3.11
- PyMuPDF for PDF processing
- ics for calendar generation

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
