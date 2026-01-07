<div align="center">
  <img src="icons/icon.png" alt="Waste Calendar Extractor" width="128" height="128">
  
# Waste Calendar Extractor for Niederanven, Luxembourg 🇱🇺

</div>

[![CI](https://github.com/sgrimee/waste-calendar-extractor/actions/workflows/ci.yml/badge.svg)](https://github.com/sgrimee/waste-calendar-extractor/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## 📅 Quick Start

### 🇱🇺 **Lëtzebuergesch**

**Link fir den Offall-Kalenner op Lëtzebuergesch:**

```link
https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/waste-lu.ics
```

**Wéi maachen:**

1. Kopéiert dësen Link ☝️
2. Gitt an Är Kalenner-App (Google Calendar, Apple Calendar, etc.)
3. Sicht no "Kalenner importéieren" oder "Kalenner abonnéieren"
4. Fügt den Link an - Är Telefon gëtt automatesch all d'Offall-Datumer mat Ikouen an Erënnerungen!

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
4. Ajoutez le lien - votre téléphone recevra automatiquement toutes les dates de collecte avec des icônes et des rappels en français !

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
4. Add the link - your phone will automatically get all waste collection dates with helpful emoji icons and reminder alarms in English!

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
Special collections that don't require advance preparation:
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

## Usage

### Basic usage

```bash
# Extract calendar from default PDF file (generates iCal files)
uv run waste-cal

# Traditional method (also works)
uv run python -m waste_cal
```

### Advanced usage

```bash
# Generate language-specific calendars
uv run waste-cal --language lu  # Luxembourgish
uv run waste-cal --language fr  # French
uv run waste-cal --language en  # English

# Specify custom PDF file
uv run waste-cal my-calendar.pdf

# Custom year
uv run waste-cal --year 2026

# Output as text instead of generating iCal files
uv run waste-cal --text

# Text output in specific language
uv run waste-cal --text --language lu

# Verbose logging
uv run waste-cal --verbose

# Show help
uv run waste-cal --help
```

## Command Line Options

- `pdf_file`: Path to PDF file (default: `pdf/ressourcekalenner-nidderaanwen-web.pdf`)
- `-l, --language {lu,fr,en}`: Language for output (lu=Luxembourgish, fr=French, en=English). For iCal: generates only specified language file. For text: uses specified language (default: en)
- `-y, --year YEAR`: Year for calendar extraction (default: current year)
- `--text`: Output as text instead of generating iCal files (default: generate iCal files)
- `-v, --verbose`: Enable verbose logging
- `-h, --help`: Show help message and exit

### Drawings Subcommand

This is used only for debugging.

- `month`: Month name to extract drawings from (january, february, march, april, may, june, july, august, september, october, november, december)
- `pdf_file`: Path to PDF file (default: `pdf/ressourcekalenner-nidderaanwen-web.pdf`)
- `-o, --output-dir OUTPUT_DIR`: Output directory for drawing images (default: debug)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
