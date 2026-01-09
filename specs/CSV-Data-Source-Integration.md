# CSV Data Source Integration Specification

**Status**: Planning  
**Date**: January 9, 2026  
**Author**: OpenCode  
**Scope**: Integrate public.data.lu waste collection CSV as alternative data source for calendar generation

---

## Executive Summary

This specification defines how to integrate Luxembourg's public waste collection dataset (CSV format from `data.public.lu`) as an alternative data source alongside the existing PDF-based extraction. The CSV provides rolling data for 86+ communes, updated continuously with upcoming collection dates.

### Key Characteristics

- **Coverage**: 86 communes vs. 2 communes (PDF-based)
- **Data type**: Rolling/live - contains only dates from today onwards
- **Granularity**: Commune-wide (deduplicatable street-level for larger cities)
- **Collection types**: 17 French waste types (vs. 11 in PDF)
- **Update frequency**: Real-time (as collections are scheduled)

---

## Background

### Current System (PDF-based)

- Supported communes: Niederanven, Schuttrange (via PDFs)
- Data source: Official PDF calendars from commune websites
- Extraction method: Area-based PDF analysis with predefined coordinates
- Output: Multi-language iCal files with reminders

### New Data Source (CSV-based)

- **Source URL**: https://data.public.lu/fr/datasets/r/c3805ec5-7836-49a4-9983-effaf81910d0
- **Format**: Semicolon-delimited CSV with BOM
- **Columns**: Date (DD/MM/YYYY), Collection Type (FR), Commune, Locality, Street
- **File size**: ~6.5MB (Q1 2026)
- **Update cadence**: TBD (appears to be updated as collections are scheduled)

### CSV Structure Example

```csv
"Date";"Type de collecte";"Commune";"Localité";"Rue"
"12/01/2026";"Biodéchets";"Niederanven";;"Toutes les rues"
"13/01/2026";"Déchets encombrants";"Niederanven";;"Toutes les rues"
"15/01/2026";"Papier/Carton";"Niederanven";;"Toutes les rues"
```

---

## Analysis: CSV vs PDF Data

### Commune Coverage Analysis

**Total communes in CSV**: 86 (excluding header)

**Street-level data communes** (rows replicated per street):
- Bech (167 rows → 47 unique date/type)
- Contern (123 rows → 29 unique date/type)
- Differdange (6,507 rows → 126 unique date/type)
- Dudelange (5,209 rows → 148 unique date/type)
- Echternach (151 rows → 48 unique date/type)
- Esch-sur-Alzette (19,057 rows → 134 unique date/type)
- Luxembourg (0 rows in Q1 data)

**Conclusion**: Street field is informational only. All streets on a given date/commune have identical collections. **Deduplication by (date, type, commune) is safe.**

### Collection Type Mapping

| CSV French Type | Current WasteType | Mapping Status | Icon | Alarm |
|-----------------|-------------------|----------------|------|-------|
| Biodéchets | ORGANIC | ✓ Direct | 🍌 | **Yes** |
| Déchets ménagers en mélange | RESIDUAL | ✓ Direct | 🗑️ | **Yes** |
| Papier/Carton | PAPER | ✓ Direct | 📦 | **Yes** |
| Valorlux | PACKAGING | ✓ Direct | ♻️ | **Yes** |
| Verre | GLASS | ✓ Direct | 🍾 | **Yes** |
| Déchets d'équipements électriques et électroniques | ELECTRIC | ✓ Direct | ⚡ | No |
| Déchets de verdure | HEDGE | ✓ Direct | 🌿 | No |
| SuperDrecksKëscht | PROBLEMATIC | ✓ Direct | ☢️ | No |
| Déchets encombrants | BULKY | ✓ Direct | 🪑 | No |
| Vieux vêtements | CLOTHERS | ✓ Direct | 👕 | No |
| Arbres de Noël | CHRISTMAS_TREES | ✓ Direct | 🎄 | No |
| **Ferraille** | — | **NEW** | 🔩 | **No** |
| **Vieux bois** | — | **NEW** | 🪵 | **No** |
| **Déchets recyclables** | — | **NEW** | ♻️ | **No** |
| **Conteneur pour déchets ménagers** | — | **NEW** | 🗑️ | **No** |
| Papier/Carton (commerces) | — | **NEW (Commercial)** | 📦 | No |
| Verre (commerces) | — | **NEW (Commercial)** | 🍾 | No |

---

## Implementation Scope

### Phase 1: Core Integration (This Spec)

**Test Communes**:
1. **Niederanven** - Commune-wide; compare against existing PDF-generated calendars
2. **Sandweiler** - Commune-wide; Niederanven neighbor
3. **Contern** - Street-level data; tests deduplication

### Phase 2: Live HTTP Fetching (Future)

- Fetch CSV directly from data.public.lu URL on each run
- Implement local caching with timestamp validation
- Re-fetch if cache is older than 24 hours (TBD cadence)

### Phase 3: Scaling (Future)

- Generate calendars for all 86 communes
- Evaluate performance impact
- Create bulk generation recipes

---

## New Waste Types

### SCRAP_METAL (Ferraille)

| Aspect | Value |
|--------|-------|
| Icon | 🔩 |
| Luxembourgish | Schrottzäll |
| French | Ferraille |
| English | Scrap metal |
| Has Alarm | **No** |
| Notes | Special collection type, requires advance scheduling |

### OLD_WOOD (Vieux bois)

| Aspect | Value |
|--------|-------|
| Icon | 🪵 |
| Luxembourgish | Aalt Bréck |
| French | Vieux bois |
| English | Old wood |
| Has Alarm | **No** |
| Notes | Special collection type, requires advance scheduling |

### RECYCLABLE (Déchets recyclables)

| Aspect | Value |
|--------|-------|
| Icon | ♻️ |
| Luxembourgish | Dierbar Mëll |
| French | Déchets recyclables |
| English | Recyclable waste |
| Has Alarm | **No** |
| Notes | Treated as special collection (not regular weekly recycling) |

### CONTAINER (Conteneur pour déchets ménagers)

| Aspect | Value |
|--------|-------|
| Icon | 🗑️ |
| Luxembourgish | Container fir Huushaltsmüll |
| French | Conteneur pour déchets ménagers |
| English | Household waste container |
| Has Alarm | **No** |
| Notes | Special collection for containers, not regular residual waste |

### PAPER_COMMERCIAL (Papier/Carton - commerces)

| Aspect | Value |
|--------|-------|
| Icon | 📦 |
| Luxembourgish | Pabeier a Kartong (Handwierk) |
| French | Papier/Carton (commerces) |
| English | Paper/Cardboard (commercial) |
| Has Alarm | **No** |
| Notes | Commercial variant; separate from residential PAPER type |

### GLASS_COMMERCIAL (Verre - commerces)

| Aspect | Value |
|--------|-------|
| Icon | 🍾 |
| Luxembourgish | Glas (Handwierk) |
| French | Verre (commerces) |
| English | Glass (commercial) |
| Has Alarm | **No** |
| Notes | Commercial variant; separate from residential GLASS type |

---

## Module Design

### 1. Extended `waste_types.py`

**Changes**:
- Add 6 new enum values to `WasteType`
- Update `description()` method with translations for all 3 languages
- Update `icon()` method with icons for new types
- Update `has_alarm()` to return `False` for all new types (they are all special collections like HEDGE, ELECTRIC, etc.)
- Note: No new alarm messages needed for new types since none have alarms

**Backward Compatibility**: All existing enum values unchanged; new values appended.

### 2. New Module: `csv_extractor.py`

**Location**: `src/waste_cal/csv_extractor.py`

**Public API**:

```python
def get_communes(csv_path: str) -> list[str]:
    """
    Extract unique commune names from CSV.
    
    Args:
        csv_path: Path to the CSV file
        
    Returns:
        Sorted list of unique commune names (excluding 'Commune' header)
    """

def extract_calendar_data_from_csv(
    csv_path: str, 
    commune: str
) -> CalendarData:
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
```

**Private Functions**:

```python
def _parse_csv(csv_path: str) -> list[dict]:
    """
    Parse semicolon-delimited CSV with UTF-8 BOM.
    
    Handles:
    - UTF-8 BOM (as present in data.public.lu export)
    - Semicolon field delimiter
    - Quoted fields
    
    Returns:
        List of dicts with keys: date, type, commune, locality, street
    """

def _csv_type_to_waste_type(french_type: str) -> WasteType | None:
    """
    Map CSV French collection type to WasteType enum.
    
    Returns None for unknown types (logs warning).
    """

def _parse_date(date_str: str) -> datetime.date:
    """
    Parse DD/MM/YYYY format from CSV.
    
    Args:
        date_str: Date string in format "DD/MM/YYYY"
        
    Returns:
        datetime.date object
    """
```

**Type Mapping Table** (internal):

```python
CSV_TYPE_MAPPING = {
    "Biodéchets": WasteType.ORGANIC,
    "Déchets ménagers en mélange": WasteType.RESIDUAL,
    "Papier/Carton": WasteType.PAPER,
    "Papier/Carton (commerces)": WasteType.PAPER_COMMERCIAL,
    "Valorlux": WasteType.PACKAGING,
    "Verre": WasteType.GLASS,
    "Verre (commerces)": WasteType.GLASS_COMMERCIAL,
    "Déchets d'équipements électriques et électroniques": WasteType.ELECTRIC,
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
```

### 3. Updated `cli.py`

**New Options**:

```
--csv CSV_PATH           Path to CSV file (alternative to --pdf)
--list-communes          List all available communes in CSV (requires --csv)
```

**Usage Examples**:

```bash
# List communes in CSV
uv run waste-cal --csv sources/waste-data-public-2026q1.csv --list-communes

# Generate calendars from CSV
uv run waste-cal --csv sources/waste-data-public-2026q1.csv --commune niederanven
uv run waste-cal --csv sources/waste-data-public-2026q1.csv --commune contern --language fr
```

**Flow Logic**:

```
if args.csv:
    if args.list_communes:
        print(get_communes(args.csv))
    else:
        calendar_data = extract_calendar_data_from_csv(args.csv, args.commune)
        generate_all_commune_ical_files(calendar_data, args.commune, args.year)
elif args.pdf:
    # Existing PDF flow
else:
    raise error("Either --csv or --pdf required")
```

**Mutual Exclusivity**: `--csv` and `--pdf` options are mutually exclusive.

---

## Proposed File Changes

### Existing Files to Modify

1. **`src/waste_cal/waste_types.py`**
   - Add 6 new WasteType enum values
   - Add translations and icons in `description()`, `icon()` methods
   - Update `has_alarm()` logic
   - Add alarm messages in `alarm_message()` method

2. **`src/waste_cal/cli.py`**
   - Add `--csv` argument
   - Add `--list-communes` argument
   - Update argument validation to make `--pdf` and `--csv` mutually exclusive
   - Import and call `extract_calendar_data_from_csv()` when `--csv` used

### New Files

1. **`src/waste_cal/csv_extractor.py`**
   - CSV parsing logic
   - Type mapping
   - Deduplication and CalendarData generation

### Test Files

1. **`tests/test_csv_extractor.py`** (NEW)
   - Test CSV parsing with BOM and semicolon delimiters
   - Test `get_communes()` function
   - Test date parsing (DD/MM/YYYY format)
   - Test type mapping for all 17 collection types
   - Test deduplication behavior
   - Test CalendarData output structure
   - Test error handling (missing files, unknown communes)

### Documentation Files

1. **`specs/CSV-Data-Source-Integration.md`** (THIS FILE)
   - Specification and design documentation

### Cleanup Files

1. **Rename existing ICS files** (one-time, before testing)
   ```bash
   ics/waste-niederanven-lu.ics → ics/waste-niederanven-lu-old.ics
   ics/waste-niederanven-fr.ics → ics/waste-niederanven-fr-old.ics
   ics/waste-niederanven-en.ics → ics/waste-niederanven-en-old.ics
   ics/waste-lu.ics → ics/waste-lu-old.ics
   ics/waste-fr.ics → ics/waste-fr-old.ics
   ics/waste-en.ics → ics/waste-en-old.ics
   ```

---

## Testing Strategy

### Unit Tests (`tests/test_csv_extractor.py`)

1. **CSV Parsing**
   - Test UTF-8 BOM handling
   - Test semicolon field delimiter
   - Test quoted field handling
   - Test row count for test data

2. **Date Parsing**
   - Test DD/MM/YYYY format conversion
   - Test edge cases (1st, 31st, leap year)
   - Test invalid date handling

3. **Type Mapping**
   - Test all 17 CSV types map to correct WasteType
   - Test unknown types return None with warning
   - Test case sensitivity

4. **Deduplication**
   - For commune-wide data (Sandweiler): verify 1 entry per (date, type)
   - For street-level data (Contern): verify street column ignored, deduplication occurs
   - Verify sorted output by date

5. **CalendarData Compatibility**
   - Verify returned object has `get_all_dates()` method
   - Verify `get_collections_for_date()` returns list of WasteType
   - Verify event creation works with ical_generator

6. **Error Handling**
   - FileNotFoundError for missing CSV
   - ValueError for unknown commune
   - Graceful handling of malformed rows

### Integration Tests

1. **Niederanven Comparison**
   - Generate ICS files from CSV
   - Compare dates with PDF-generated files (Jan 12-31)
   - Verify all dates match

2. **Three Test Communes**
   - Generate ICS files for Niederanven, Sandweiler, Contern
   - All 3 languages
   - Verify no errors
   - Manual spot-check of a few dates in output

---

## Data Validation

### Niederanven Validation (Jan 12-Mar 31, 2026)

**CSV Dates** (39 unique date/type combos):
```
Jan: 12, 13, 15, 16, 19, 20, 22, 26, 30
Feb: 02, 03, 04, 05, 09, 10, 13, 16, 17, 19, 23, 26, 27
Mar: 02, 03, 04, 05, 06, 09, 10, 13, 16, 17, 19, 23, 26, 27, 30, 31
```

**PDF-Generated ICS Dates** (Feb-Mar match, Jan 2-7 extra):
```
Jan: 02, 03, 05, 06, 07, 12, 13, 15, 16, 19, 20, 22, 26, 30 (Jan 2-7 are pre-cutoff)
Feb: 02, 03, 04, 05, 09, 10, 13, 16, 17, 19, 23, 26, 27
Mar: 02, 03, 04, 05, 06, 09, 10, 13, 16, 17, 19, 23, 26, 27, 30, 31
```

**Expected Match**: CSV Jan 12-31 exactly matches PDF Jan 12-31 ✓

---

## Dynamic README: Auto-Generated Commune Links File

Since the list of communes (86+) is dynamic and may grow, the README will link to a separate auto-generated file rather than maintaining a hardcoded list.

### Approach: Auto-Generated `COMMUNES.md`

1. **Separate file**: `COMMUNES.md` in repository root
2. **Auto-generated**: Script creates/updates this file based on available ICS files
3. **README links**: Main README links to COMMUNES.md for full commune list
4. **Three language sections**: Luxembourgish, French, English (matching README structure)

### Generator Script: `scripts/generate_communes_md.py`

```python
def generate_communes_md(ics_dir: str = "ics", output_file: str = "COMMUNES.md") -> None:
    """
    Generate COMMUNES.md with links to all available ICS files.
    
    Scans ics/ directory for waste-{commune}-{lang}.ics files,
    extracts commune names, and generates markdown tables.
    
    Args:
        ics_dir: Directory containing ICS files
        output_file: Output markdown file path
    """
```

**Logic**:
1. Scan `ics/` for files matching `waste-*.ics` pattern
2. Extract commune names from filenames (`waste-{commune}-{lang}.ics`)
3. Group by commune and language
4. Generate markdown tables for each language
5. Write to COMMUNES.md with timestamp
6. Sort communes alphabetically

**Output Format** (`COMMUNES.md`):

```markdown
# Available Waste Calendars by Commune

Last updated: 2026-01-09

## 🇱🇺 Lëtzebuergesch

| Gemeng | Link |
|--------|------|
| Contern | `https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/waste-contern-lu.ics` |
| Niederanven | `https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/waste-niederanven-lu.ics` |
| Sandweiler | `https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/waste-sandweiler-lu.ics` |

## 🇫🇷 Français

| Commune | Lien |
|---------|------|
| Contern | `https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/waste-contern-fr.ics` |
| Niederanven | `https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/waste-niederanven-fr.ics` |
| Sandweiler | `https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/waste-sandweiler-fr.ics` |

## 🇬🇧 English

| Commune | Link |
|---------|------|
| Contern | `https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/waste-contern-en.ics` |
| Niederanven | `https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/waste-niederanven-en.ics` |
| Sandweiler | `https://raw.githubusercontent.com/sgrimee/waste-calendar-extractor/main/ics/waste-sandweiler-en.ics` |
```

### README Changes

Update main README.md to:
1. Keep a few example communes in the Quick Start tables (e.g., Niederanven)
2. Add line after each language table: "**[➜ See all available communes](COMMUNES.md)**"
3. Update "About This Tool" section to mention CSV data source and 86+ communes support

---

## Automated Calendar Regeneration (GitHub Actions)

GitHub Actions supports scheduled workflows using cron syntax. This enables automatic calendar regeneration without needing external cron job services.

### Schedule: Weekly

- **Frequency**: Every Monday at 6:00 AM UTC
- **Rationale**: Balances data freshness with CI resource usage; runs before work week begins in Europe
- **Cron expression**: `0 6 * * 1` (minute, hour, day-of-month, month, day-of-week)
- **Manual trigger**: `workflow_dispatch` allows on-demand runs from GitHub UI

### Workflow: `.github/workflows/regenerate-calendars.yml`

**Location**: Create new file `.github/workflows/regenerate-calendars.yml`

```yaml
name: Regenerate Calendars

on:
  schedule:
    # Run every Monday at 6:00 AM UTC
    - cron: '0 6 * * 1'
  workflow_dispatch:  # Allow manual trigger from GitHub UI

jobs:
  regenerate:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install uv
      uses: astral-sh/setup-uv@v3
      with:
        version: "latest"
    
    - name: Install dependencies
      run: uv sync
    
    - name: Download latest CSV from data.public.lu
      run: |
        curl -L "https://data.public.lu/fr/datasets/r/c3805ec5-7836-49a4-9983-effaf81910d0" \
          -o sources/waste-data-public.csv
        echo "CSV downloaded successfully"
        wc -l sources/waste-data-public.csv
    
    - name: Generate calendars for all communes
      run: |
        PYTHONPATH=src uv run python -m waste_cal --csv sources/waste-data-public.csv --all-communes
    
    - name: Generate COMMUNES.md
      run: |
        PYTHONPATH=src uv run python scripts/generate_communes_md.py
    
    - name: Commit and push changes
      run: |
        git config user.name "github-actions[bot]"
        git config user.email "github-actions[bot]@users.noreply.github.com"
        git add ics/ COMMUNES.md
        
        # Only commit if there are changes
        if ! git diff --staged --quiet; then
          git commit -m "chore: regenerate calendars from latest CSV data"
          git push
        else
          echo "No changes to commit"
        fi
```

### Key Features

1. **Scheduled trigger**: Runs every Monday at 6am UTC (`cron: '0 6 * * 1'`)
2. **Manual trigger**: `workflow_dispatch` allows users to trigger from GitHub UI (Actions → Regenerate Calendars → Run workflow)
3. **Fresh data**: Downloads CSV directly from data.public.lu each run
4. **All communes**: Generates calendars for all communes found in CSV
5. **Auto-commit**: Only commits if files changed (prevents empty commits with `git diff --staged --quiet`)
6. **Bot attribution**: Commits attributed to `github-actions[bot]@users.noreply.github.com`
7. **Logging**: Includes output to verify CSV download and commune count

### CLI Support: `--all-communes` Flag

New CLI option to generate calendars for all communes in CSV:

```bash
uv run waste-cal --csv sources/waste-data-public.csv --all-communes
```

**Implementation in `cli.py`**:
- Add `--all-communes` flag (mutually exclusive with `--commune`)
- When set, iterate through all communes from `get_communes(csv_path)`
- Generate ICS files for each commune
- Log progress

**Usage Logic**:
```
if args.csv:
    if args.all_communes:
        # Generate for all communes
        communes = get_communes(args.csv)
        for commune in communes:
            calendar_data = extract_calendar_data_from_csv(args.csv, commune)
            generate_all_commune_ical_files(calendar_data, commune, args.year)
    elif args.commune:
        # Generate for specific commune
        calendar_data = extract_calendar_data_from_csv(args.csv, args.commune)
        generate_all_commune_ical_files(calendar_data, args.commune, args.year)
    elif args.list_communes:
        # List available communes
        communes = get_communes(args.csv)
        print("\n".join(communes))
```

### GitHub Actions Permissions

- **Token**: `GITHUB_TOKEN` is automatically provided by GitHub Actions
- **Permissions**: Workflow automatically has write access to the repository
- **No secrets needed**: The data.public.lu URL is public; no authentication required
- **Branch protection**: If main branch requires PR reviews, commits will wait for approval

### Manual Trigger from UI

Users can manually trigger the workflow:
1. Go to repository → Actions tab
2. Select "Regenerate Calendars" workflow
3. Click "Run workflow" button
4. Select branch (usually `main`) and click "Run workflow"
5. Monitor execution in the Actions tab

---

## Implementation Checklist

- [ ] Document spec (this file)
- [ ] Extend `WasteType` enum with 6 new types
- [ ] Implement `csv_extractor.py` module
- [ ] Update `cli.py` with `--csv` option
- [ ] Update `cli.py` with `--all-communes` option
- [ ] Write unit tests in `tests/test_csv_extractor.py`
- [ ] Run all tests and verify pass
- [ ] Rename existing Niederanven ICS files with `-old` suffix
- [ ] Generate test calendars for Niederanven, Sandweiler, Contern
- [ ] Compare Niederanven CSV vs PDF outputs
- [ ] Create `scripts/generate_communes_md.py` script
- [ ] Generate `COMMUNES.md` (initial)
- [ ] Update `README.md` to link to COMMUNES.md
- [ ] Create `.github/workflows/regenerate-calendars.yml`
- [ ] Add justfile recipes for CSV operations
- [ ] Test manual workflow trigger

---

## Future Enhancements

### Phase 2: Live HTTP Fetching

- Add `fetch_csv_from_url()` function
- Implement local cache with timestamp
- Add `--fetch-latest` CLI option
- Update AGENTS.md with new workflow

### Phase 3: Scaling

- Generate calendars for all 86 communes
- Batch generation recipe: `just generate-all-csv`
- Performance profiling
- Consider splitting output by region

### Phase 4: Hybrid Mode

- Option to combine PDF + CSV data
- Fallback to CSV if PDF unavailable
- Merge collections from both sources

---

## Appendix: CSV Sample Data

```csv
"Date";"Type de collecte";"Commune";"Localité";"Rue"
"12/01/2026";"Biodéchets";"Niederanven";;"Toutes les rues"
"13/01/2026";"Déchets encombrants";"Niederanven";;"Toutes les rues"
"15/01/2026";"Papier/Carton";"Niederanven";;"Toutes les rues"
"16/01/2026";"Valorlux";"Niederanven";;"Toutes les rues"
"19/01/2026";"Biodéchets";"Niederanven";;"Toutes les rues"
"20/01/2026";"Déchets ménagers en mélange";"Niederanven";;"Toutes les rues"
"22/01/2026";"Verre";"Niederanven";;"Toutes les rues"
"26/01/2026";"Biodéchets";"Niederanven";;"Toutes les rues"
"30/01/2026";"Valorlux";"Niederanven";;"Toutes les rues"
"10/01/2026";"Arbres de Noël";"Contern";"Contern";"Allée Klaus-Michael Kühne"
"10/01/2026";"Arbres de Noël";"Contern";"Contern";"Am Bongert"
"10/01/2026";"Arbres de Noël";"Contern";"Contern";"Am Daerchen"
"12/01/2026";"Valorlux";"Contern";"Contern";"Allée Klaus-Michael Kühne"
"12/01/2026";"Valorlux";"Contern";"Contern";"Am Bongert"
```

All streets of a commune on the same date/type have identical collections.

