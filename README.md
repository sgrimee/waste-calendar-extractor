# Waste Calendar Extractor

[![CI](https://github.com/sgrimee/waste-calendar-extractor/actions/workflows/ci.yml/badge.svg)](https://github.com/sgrimee/waste-calendar-extractor/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

A Python tool to extract waste collection dates from PDF calendars and generate iCal files.

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
# Extract from default PDF file
uv run python extract_dates_from_pdf.py

# Or if installed as package
extract-waste-dates
```

### Advanced usage

```bash
# Specify custom PDF file
uv run python extract_dates_from_pdf.py my-calendar.pdf

# Custom output file and year
uv run python extract_dates_from_pdf.py -o my-calendar.ics -y 2025

# Verbose logging
uv run python extract_dates_from_pdf.py -v

# Show help
uv run python extract_dates_from_pdf.py --help
```

## Command Line Options

- `pdf_file`: Path to PDF file (default: `ressourcekalenner-nidderaanwen-web.pdf`)
- `-o, --output`: Output iCal file path (default: `waste_collection_calendar.ics`)
- `-y, --year`: Year for the calendar (default: 2024)
- `-v, --verbose`: Enable verbose logging

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

### Running tests

```bash
# Run all tests
uv run python test_extract_dates.py

# Install development dependencies (if using pip)
pip install -e ".[dev]"
pytest
```

### Project structure

```
waste-calendar-extractor/
├── extract_dates_from_pdf.py  # Main extraction script
├── test_extract_dates.py      # Unit tests
├── pyproject.toml             # Project configuration
├── README.md                  # This file
├── LICENSE                    # MIT license
└── ressourcekalenner-*.pdf    # Example PDF file
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