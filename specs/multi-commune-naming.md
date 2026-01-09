# Multi-Commune Calendar Naming Scheme

## Overview

This specification describes the new naming scheme for waste collection calendars to support multiple communes and standalone ADYS calendars, while maintaining backward compatibility with existing subscribers.

## Current State

### Files
```
ics/
  waste-lu.ics          # Niederanven only
  waste-fr.ics
  waste-en.ics
  waste-lu-adys.ics     # Niederanven + ADYS combined
  waste-fr-adys.ics
  waste-en-adys.ics

sources/
  waste-niederanven-2026.pdf
  adys.pdf
```

### Problems
1. No support for multiple communes
2. ADYS is only available as combined calendar (side effect of `--include-adys`)
3. ADYS customer ID not visible in filename
4. Adding a new commune would require breaking changes

---

## New Naming Scheme

### Pattern
```
waste-{commune}-{lang}.ics           # Commune-specific waste calendars
waste-{lang}.ics                     # Legacy aliases (niederanven only, auto-generated)
adys-{customer_id}-{lang}.ics        # ADYS standalone per customer
```

### Target File Structure
```
ics/
  # Niederanven (with legacy duplicates)
  waste-niederanven-lu.ics
  waste-niederanven-fr.ics
  waste-niederanven-en.ics
  waste-lu.ics                       # duplicate of waste-niederanven-lu.ics
  waste-fr.ics                       # duplicate of waste-niederanven-fr.ics
  waste-en.ics                       # duplicate of waste-niederanven-en.ics

  # Schuttrange
  waste-schuttrange-lu.ics
  waste-schuttrange-fr.ics
  waste-schuttrange-en.ics

  # ADYS standalone
  adys-019027-lu.ics
  adys-019027-fr.ics
  adys-019027-en.ics

sources/
  waste-niederanven-2026.pdf
  adys-019027-2026.pdf                    # renamed from adys.pdf
```

### Files Removed
The combined `waste-{lang}-adys.ics` files will no longer be generated. Users needing both waste and ADYS events should subscribe to both calendars separately.

---

## CLI Changes

### Current CLI
```bash
uv run waste-cal [pdf_file] --language lu --include-adys
```

### New CLI

#### Waste Calendar Generation
```bash
# Generate for specific commune (required)
uv run waste-cal --commune niederanven --language lu
uv run waste-cal --commune schuttrange --language lu

# Generate all languages for a commune
uv run waste-cal --commune niederanven

# Specify year
uv run waste-cal --commune niederanven --language lu --year 2026

# Specify PDF (optional, defaults based on commune)
uv run waste-cal --commune niederanven --pdf sources/custom.pdf --language lu
```

#### ADYS Calendar Generation
```bash
# Generate ADYS calendar (customer ID derived from PDF filename)
uv run waste-cal --adys sources/adys-019027-2026.pdf --language lu

# Generate ADYS with explicit customer ID (overrides filename)
uv run waste-cal --adys sources/adys.pdf --customer-id 019027 --language lu

# Generate all languages
uv run waste-cal --adys sources/adys-019027-2026.pdf
```

### CLI Arguments

| Argument | Description |
|----------|-------------|
| `--commune` | Commune name (niederanven, schuttrange) |
| `--adys` | Path to ADYS PDF (mutually exclusive with --commune) |
| `--customer-id` | ADYS customer ID (optional, derived from PDF filename if not provided) |
| `--language` | Language code (lu, fr, en). If omitted, generates all languages |
| `--year` | Year for calendar (default: current year) |
| `--pdf` | Override default PDF path for commune |
| `--text` | Output as text instead of iCal |
| `-v, --verbose` | Enable verbose logging |

### Default PDF Paths by Commune
```python
COMMUNE_PDF_DEFAULTS = {
    "niederanven": "sources/waste-niederanven-2026.pdf",
    "schuttrange": "sources/ressourcekalenner-schuttrange-web.pdf",  # TBD
}
```

---

## Justfile Changes

### New Recipes

```just
# Generate all calendars for all communes and ADYS
generate-all: generate-niederanven generate-schuttrange generate-adys-019027

# Niederanven (includes legacy duplicates automatically)
generate-niederanven:
    uv run waste-cal --commune niederanven
    @echo "Generated waste-niederanven-*.ics and legacy waste-*.ics files"

# Schuttrange
generate-schuttrange:
    uv run waste-cal --commune schuttrange
    @echo "Generated waste-schuttrange-*.ics files"

# ADYS standalone
generate-adys customer_id:
    uv run waste-cal --adys --pdf sources/adys-{{customer_id}}-2026.pdf
    @echo "Generated adys-{{customer_id}}-*.ics files"

# Convenience alias for known customer
generate-adys-019027:
    just generate-adys 019027

# Generate specific commune + language
generate-commune-lang commune lang:
    uv run waste-cal --commune {{commune}} --language {{lang}}

# Generate ADYS for specific customer + language
generate-adys-lang customer_id lang:
    uv run waste-cal --adys --pdf sources/adys-{{customer_id}}-2026.pdf --language {{lang}}
```

### Backward Compatibility
Keep existing recipes as aliases:
```just
# Legacy aliases (deprecated, use generate-niederanven instead)
generate: generate-niederanven

# Remove: generate-with-adys (no longer applicable)
# Remove: generate-lang-with-adys (no longer applicable)
```

---

## Code Changes

### 1. Rename PDF File
```bash
mv sources/adys.pdf sources/adys-019027-2026.pdf
```

### 2. Update `cli.py`

- Add `--commune` argument (choices: niederanven, schuttrange)
- Add `--adys` argument (path to ADYS PDF, mutually exclusive with --commune)
- Add `--customer-id` argument (optional, for ADYS)
- Remove `--include-adys` argument
- Update logic to generate appropriate files based on mode

### 3. Update `ical_generator.py`

#### New Functions
```python
def generate_commune_ical_file(
    calendar_data: CalendarData,
    commune: str,
    language: Languages,
    year: int,
    output_dir: str = "ics",
) -> list[str]:
    """
    Generate iCal file for a commune.
    For niederanven, also generates legacy waste-{lang}.ics duplicates.
    Returns list of generated file paths.
    """

def generate_adys_ical_file(
    adys_dates: list[str],
    customer_id: str,
    language: Languages,
    year: int,
    output_dir: str = "ics",
) -> str:
    """
    Generate standalone ADYS iCal file.
    Returns path to generated file.
    """
```

#### Remove Functions
- `generate_ical_file_with_adys()`
- `generate_all_ical_files_with_adys()`

### 4. Update `adys_extractor.py`

Add function to extract customer ID from PDF filename:
```python
def extract_customer_id_from_filename(pdf_path: str) -> str | None:
    """
    Extract customer ID from ADYS PDF filename.
    e.g., 'sources/adys-019027-2026.pdf' -> '019027'
    Returns None if pattern not found.
    """
```

### 5. Update Event Location

Currently hardcoded to "Niederanven, Luxembourg". Update to use commune name:
```python
event.location = f"{commune.title()}, Luxembourg"
```

---

## Migration Steps

### For Existing Users

Users currently subscribing to:
- `waste-lu.ics` → No change needed (legacy duplicate maintained)
- `waste-lu-adys.ics` → Subscribe to both `waste-lu.ics` AND `adys-019027-lu.ics`

### Implementation Order

1. Rename `sources/adys.pdf` to `sources/adys-019027-2026.pdf`
2. Update `ical_generator.py` with new functions
3. Update `adys_extractor.py` with customer ID extraction
4. Update `cli.py` with new arguments
5. Update `justfile` with new recipes
6. Update tests
7. Generate new calendars and verify
8. Update AGENTS.md with new conventions
9. Remove old combined files from `ics/`

---

## Testing

### Unit Tests
- Test customer ID extraction from various filename patterns
- Test commune-specific file naming
- Test legacy duplicate generation for niederanven only
- Test ADYS standalone file generation

### Integration Tests
- Generate niederanven calendars, verify 6 files created (3 commune + 3 legacy)
- Generate schuttrange calendars, verify 3 files created (no legacy)
- Generate ADYS calendars, verify 3 files created with customer ID in name

---

## Future Considerations

1. **Additional Communes**: Add new communes by:
   - Adding PDF to `sources/` folder
   - Adding entry to `COMMUNE_PDF_DEFAULTS`
   - Adding justfile recipe

2. **Additional ADYS Customers**: Simply use different customer ID:
   ```bash
   just generate-adys 019028
   ```

3. **Commune-Specific ADYS**: If needed, naming could extend to:
   ```
   adys-{commune}-{customer_id}-{lang}.ics
   ```
   But not needed currently since ADYS is regional, not commune-specific.

---

## README.md Updates

The README needs significant updates to reflect multi-commune support.

### Title Change
```markdown
# Waste Calendar Extractor for Luxembourg Communes
```
(Remove "Niederanven" from title, make it generic)

### Quick Start Section

Restructure to show calendars by commune:

```markdown
## Quick Start

### Niederanven

#### Luxembourgish
```link
https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/waste-niederanven-lu.ics
```

#### French
```link
https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/waste-niederanven-fr.ics
```

#### English
```link
https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/waste-niederanven-en.ics
```

### Schuttrange

#### Luxembourgish
```link
https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/waste-schuttrange-lu.ics
```

#### French
```link
https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/waste-schuttrange-fr.ics
```

#### English
```link
https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/waste-schuttrange-en.ics
```

### ADYS Bin Cleaning (Customer 019027)

#### Luxembourgish
```link
https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/adys-019027-lu.ics
```
(etc.)
```

### Legacy Links Note

Add a note about legacy URLs:

```markdown
> **Note for existing subscribers**: The original `waste-lu.ics`, `waste-fr.ics`, and `waste-en.ics` 
> URLs continue to work and point to Niederanven calendars for backward compatibility.
```

### About Section

Update to mention multiple communes:

```markdown
## About This Tool

A Python tool to extract waste collection dates from PDF calendars published by 
**Luxembourg communes** (currently Niederanven and Schuttrange) and generate iCal 
files for easy calendar integration.
```

### Disclaimer Update

Make disclaimer generic for all communes:

```markdown
### Important Disclaimer

**This is an unofficial hobby project and is not endorsed by, affiliated with, 
or maintained by any Luxembourg commune.** The data extracted from PDF calendars 
may be inaccurate or incomplete.
...
For official and authoritative waste collection information, always consult the 
official resources provided by your commune.
```

### Source Data Section

Update to list multiple sources:

```markdown
## Source Data

This tool extracts data from official waste collection calendars published by Luxembourg communes:

- **Niederanven**: [Official website](https://www.niederanven.lu/en/environment/waste-disposal-management)
- **Schuttrange**: [Official website](https://www.schuttrange.lu/...) <!-- TBD: add actual URL -->
- **ADYS**: [ADYS website](https://www.adys.lu/) for bin cleaning services
```

### Usage Section Updates

Update CLI examples:

```markdown
## Usage

### Basic usage

```bash
# Generate calendars for a commune
uv run waste-cal --commune niederanven
uv run waste-cal --commune schuttrange

# Generate ADYS calendar
uv run waste-cal --adys sources/adys-019027-2026.pdf
```

### Advanced usage

```bash
# Generate specific language for a commune
uv run waste-cal --commune niederanven --language lu

# Specify custom PDF file
uv run waste-cal --commune niederanven --pdf my-calendar.pdf

# Generate ADYS with explicit customer ID
uv run waste-cal --adys sources/adys.pdf --customer-id 019027

# Custom year
uv run waste-cal --commune niederanven --year 2026

# Output as text instead of generating iCal files
uv run waste-cal --commune niederanven --text

# Verbose logging
uv run waste-cal --commune niederanven --verbose
```
```

### Command Line Options Update

```markdown
## Command Line Options

- `--commune {niederanven,schuttrange}`: Commune to generate calendar for
- `--adys PDF_PATH`: Generate ADYS calendar from PDF (mutually exclusive with --commune)
- `--customer-id ID`: ADYS customer ID (optional, derived from PDF filename)
- `-l, --language {lu,fr,en}`: Language for output. If omitted, generates all languages
- `-y, --year YEAR`: Year for calendar extraction (default: current year)
- `--pdf PDF_PATH`: Override default PDF path for commune
- `--text`: Output as text instead of generating iCal files
- `-v, --verbose`: Enable verbose logging
- `-h, --help`: Show help message and exit
```

### Implementation Order Update

Add README update step:

```markdown
### Implementation Order

1. Rename `sources/adys.pdf` to `sources/adys-019027-2026.pdf`
2. Update `ical_generator.py` with new functions
3. Update `adys_extractor.py` with customer ID extraction
4. Update `cli.py` with new arguments
5. Update `justfile` with new recipes
6. Update tests
7. Generate new calendars and verify
8. Update AGENTS.md with new conventions
9. **Update README.md with new structure and examples**
10. Remove old combined files from `ics/`
```
