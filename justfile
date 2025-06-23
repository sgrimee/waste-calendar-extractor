# Justfile for waste-calendar-extractor project

# Default recipe - run all checks and tests
default: check test

# Install development dependencies
install:
    uv sync --dev

# Run all tests including integration tests
test:
    PYTHONPATH=src uv run python -m pytest tests/ -v

# Run only unit tests (exclude integration tests) - for CI
test-unit:
    PYTHONPATH=src uv run python -m pytest tests/ -v -m 'not integration'

# Run only integration tests
test-integration:
    PYTHONPATH=src uv run python -m pytest tests/ -v -m integration

# Run tests with coverage
test-cov:
    PYTHONPATH=src uv run python -m pytest tests/ --cov=waste_cal --cov-report=term-missing

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
    PYTHONPATH=src uv run mypy src/ tests/

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
    rm -f ics/waste-*.ics ics/waste.ics
    @echo "✅ Cleaned all waste calendar files"

# Generate waste calendar for current year (all languages)
generate: clean-waste
    uv run waste-cal --language lu
    uv run waste-cal --language fr
    uv run waste-cal --language en
    echo "✅ Generated all language-specific calendars"

# Generate waste calendar for specific year (all languages)
generate-year year: clean-waste
    uv run waste-cal --language lu --year {{year}}
    uv run waste-cal --language fr --year {{year}}
    uv run waste-cal --language en --year {{year}}
    echo "✅ Generated all language-specific calendars for {{year}}"

# Generate calendar for specific language
generate-lang lang:
    uv run waste-cal --language {{lang}}
    echo "✅ Generated ics/waste-{{lang}}.ics calendar"

# Generate calendar for specific language and year
generate-lang-year lang year:
    uv run waste-cal --language {{lang}} --year {{year}}
    echo "✅ Generated ics/waste-{{lang}}.ics calendar"

# Download latest calendar PDF from commune website
download:
    PYTHONPATH=src uv run python -m waste_calendar_extractor --download
    echo "✅ Downloaded latest calendar PDF"

# View iCS calendar files
view-main:
    @echo "📅 Viewing main waste.ics calendar:"
    PYTHONPATH=src uv run python -m waste_cal.ics_viewer ics/waste.ics

view-all:
    @echo "📅 Viewing all generated calendars:"
    @echo "\n🇱🇺 Luxembourgish calendar:"
    @if [ -f ics/waste-lu.ics ]; then PYTHONPATH=src uv run python -m waste_cal.ics_viewer ics/waste-lu.ics --format summary; else echo "File not found: ics/waste-lu.ics"; fi
    @echo "\n🇫🇷 French calendar:"
    @if [ -f ics/waste-fr.ics ]; then PYTHONPATH=src uv run python -m waste_cal.ics_viewer ics/waste-fr.ics --format summary; else echo "File not found: ics/waste-fr.ics"; fi
    @echo "\n🇬🇧 English calendar:"
    @if [ -f ics/waste-en.ics ]; then PYTHONPATH=src uv run python -m waste_cal.ics_viewer ics/waste-en.ics --format summary; else echo "File not found: ics/waste-en.ics"; fi

view-lang lang:
    @echo "📅 Viewing {{lang}} calendar:"
    PYTHONPATH=src uv run python -m waste_cal.ics_viewer ics/waste-{{lang}}.ics

view-file file:
    @echo "📅 Viewing calendar: {{file}}"
    PYTHONPATH=src uv run python -m waste_cal.ics_viewer {{file}}

# View calendar with specific format
view-summary file:
    PYTHONPATH=src uv run python -m waste_cal.ics_viewer {{file}} --format summary

view-calendar file:
    PYTHONPATH=src uv run python -m waste_cal.ics_viewer {{file}} --format calendar

view-list file:
    PYTHONPATH=src uv run python -m waste_cal.ics_viewer {{file}} --format list