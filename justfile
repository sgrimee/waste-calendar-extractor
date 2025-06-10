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
    PYTHONPATH=src uv run python -m pytest tests/ --cov=waste_calendar_extractor --cov-report=term-missing

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
    @echo "🗑️ Removing all waste-* calendar files..."
    rm -f ics/waste-*.ics
    @echo "✅ Cleaned all waste calendar files"

# Generate waste calendar for current year (all languages)
generate: clean-waste
    PYTHONPATH=src uv run python -m waste_calendar_extractor --all-languages
    cp ics/waste-$(date +%Y).ics ics/waste.ics
    cp ics/waste-$(date +%Y)-de.ics ics/waste-de.ics
    cp ics/waste-$(date +%Y)-fr.ics ics/waste-fr.ics
    cp ics/waste-$(date +%Y)-en.ics ics/waste-en.ics
    echo "✅ Generated all language-specific calendars and updated waste.ics"

# Generate waste calendar for specific year (all languages)
generate-year year: clean-waste
    PYTHONPATH=src uv run python -m waste_calendar_extractor -y {{year}} --all-languages
    cp ics/waste-{{year}}.ics ics/waste.ics
    cp ics/waste-{{year}}-de.ics ics/waste-de.ics
    cp ics/waste-{{year}}-fr.ics ics/waste-fr.ics
    cp ics/waste-{{year}}-en.ics ics/waste-en.ics
    echo "✅ Generated all language-specific calendars for {{year}} and updated waste.ics"

# Generate calendar for specific language
generate-lang lang:
    PYTHONPATH=src uv run python -m waste_calendar_extractor --language {{lang}}
    echo "✅ Generated ics/waste-{{lang}}.ics calendar"

# Generate calendar for specific language and year
generate-lang-year lang year:
    PYTHONPATH=src uv run python -m waste_calendar_extractor --language {{lang}} -y {{year}}
    echo "✅ Generated ics/waste-{{year}}-{{lang}}.ics calendar"

# Download latest calendar PDF from commune website
download:
    PYTHONPATH=src uv run python -m waste_calendar_extractor --download
    echo "✅ Downloaded latest calendar PDF"

# View iCS calendar files
view-main:
    @echo "📅 Viewing main waste.ics calendar:"
    PYTHONPATH=src uv run python -m waste_calendar_extractor.ics_viewer ics/waste.ics

view-all:
    @echo "📅 Viewing all generated calendars:"
    @echo "\n🇩🇪 German/Luxembourgish calendar:"
    @if [ -f ics/waste-2025-de.ics ]; then PYTHONPATH=src uv run python -m waste_calendar_extractor.ics_viewer ics/waste-2025-de.ics --format summary; else echo "File not found: ics/waste-2025-de.ics"; fi
    @echo "\n🇫🇷 French calendar:"
    @if [ -f ics/waste-2025-fr.ics ]; then PYTHONPATH=src uv run python -m waste_calendar_extractor.ics_viewer ics/waste-2025-fr.ics --format summary; else echo "File not found: ics/waste-2025-fr.ics"; fi
    @echo "\n🇬🇧 English calendar:"
    @if [ -f ics/waste-2025-en.ics ]; then PYTHONPATH=src uv run python -m waste_calendar_extractor.ics_viewer ics/waste-2025-en.ics --format summary; else echo "File not found: ics/waste-2025-en.ics"; fi

view-lang lang:
    @echo "📅 Viewing {{lang}} calendar:"
    PYTHONPATH=src uv run python -m waste_calendar_extractor.ics_viewer ics/waste-2025-{{lang}}.ics

view-file file:
    @echo "📅 Viewing calendar: {{file}}"
    PYTHONPATH=src uv run python -m waste_calendar_extractor.ics_viewer {{file}}

# View calendar with specific format
view-summary file:
    PYTHONPATH=src uv run python -m waste_calendar_extractor.ics_viewer {{file}} --format summary

view-calendar file:
    PYTHONPATH=src uv run python -m waste_calendar_extractor.ics_viewer {{file}} --format calendar

view-list file:
    PYTHONPATH=src uv run python -m waste_calendar_extractor.ics_viewer {{file}} --format list