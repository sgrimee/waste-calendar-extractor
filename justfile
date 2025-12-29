# Justfile for waste-calendar-extractor project

# Default recipe - list all available targets
default:
    @just --list

# Install development dependencies
install:
    uv sync --dev

# Run all tests including integration tests
test:
    uv run python -m pytest tests/ -v

# Run only unit tests (exclude integration tests) - for CI
test-unit:
    uv run python -m pytest tests/ -v -m 'not integration'

# Run only integration tests
test-integration:
    uv run python -m pytest tests/ -v -m integration

# Run tests with coverage
test-cov:
    uv run python -m pytest tests/ --cov=waste_cal --cov-report=term-missing

# Run all checks (format, lint, type check)
check: format lint typecheck

# Format code with ruff and fix issues
format:
    uv run ruff check --fix src/ tests/
    uv run ruff format src/ tests/

# Lint code with ruff (without fixing)
lint:
    uv run ruff check src/ tests/

# Type check with mypy
typecheck:
    uv run mypy src/ tests/

# Build the package
build:
    uv build

# Clean build artifacts
clean:
    rm -rf dist/
    rm -rf build/
    rm -rf *.egg-info/
    rm -rf .pytest_cache/
    rm -rf .mypy_cache/
    rm -rf .ruff_cache/

# Clean all waste calendar files
clean-waste:
    @echo "🗑️ Removing all waste calendar files..."
    rm -f ics/waste-*.ics
    @echo "✅ Cleaned all waste calendar files"

# Generate waste calendar for current year (all languages, without ADYS)
generate: clean-waste
    uv run waste-cal --language lu
    uv run waste-cal --language fr
    uv run waste-cal --language en
    @echo "✅ Generated all language-specific calendars"

# Generate waste calendar with ADYS bin cleaning dates (all languages)
generate-with-adys: clean-waste
    uv run waste-cal --language lu --include-adys
    uv run waste-cal --language fr --include-adys
    uv run waste-cal --language en --include-adys
    @echo "✅ Generated calendars with ADYS cleaning dates (both standard and -adys files)"

# Generate waste calendar for specific year (all languages)
generate-year year: clean-waste
    uv run waste-cal --language lu --year {{year}}
    uv run waste-cal --language fr --year {{year}}
    uv run waste-cal --language en --year {{year}}
    echo "✅ Generated all language-specific calendars for {{year}}"

# Generate calendar for specific language (without ADYS)
generate-lang lang:
    uv run waste-cal --language {{lang}}
    @echo "✅ Generated ics/waste-{{lang}}.ics calendar"

# Generate calendar for specific language and year (without ADYS)
generate-lang-year lang year:
    uv run waste-cal --language {{lang}} --year {{year}}
    @echo "✅ Generated ics/waste-{{lang}}.ics calendar"

# Generate calendar for specific language with ADYS
generate-lang-with-adys lang:
    uv run waste-cal --language {{lang}} --include-adys
    @echo "✅ Generated ics/waste-{{lang}}.ics and ics/waste-{{lang}}-adys.ics calendars"

# Generate calendar for specific language and year with ADYS
generate-lang-year-with-adys lang year:
    uv run waste-cal --language {{lang}} --year {{year}} --include-adys
    @echo "✅ Generated ics/waste-{{lang}}.ics and ics/waste-{{lang}}-adys.ics calendars"

view-lang lang:
    @echo "📅 Viewing {{lang}} calendar:"
    uv run python -m waste_cal.ics_viewer ics/waste-{{lang}}.ics

view-file file:
    @echo "📅 Viewing calendar: {{file}}"
    uv run python -m waste_cal.ics_viewer {{file}}

# View calendar with specific format
view-summary file:
    uv run python -m waste_cal.ics_viewer {{file}} --format summary

view-calendar file:
    uv run python -m waste_cal.ics_viewer {{file}} --format calendar

view-list file:
    uv run python -m waste_cal.ics_viewer {{file}} --format list

# Extract ADYS cleaning dates from PDF (year auto-detected from PDF title)
extract-adys pdf:
    @echo "Extracting ADYS cleaning dates from {{pdf}}..."
    uv run python -m waste_cal.adys_extractor {{pdf}}