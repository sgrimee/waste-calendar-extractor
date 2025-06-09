# Justfile for waste-calendar-extractor project

# Default recipe - run all checks and tests
default: check test

# Install development dependencies
install:
    uv sync --dev

# Run all tests
test:
    PYTHONPATH=src uv run python -m pytest tests/ -v

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

# Run tests with coverage
test-cov:
    PYTHONPATH=src uv run python -m pytest tests/ --cov=waste_calendar_extractor --cov-report=term-missing

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

# Generate waste calendar for current year (all languages)
generate:
    PYTHONPATH=src uv run python -m waste_calendar_extractor --all-languages
    cp waste-$(date +%Y).ics waste.ics
    echo "✅ Generated all language-specific calendars and updated waste.ics"

# Generate waste calendar for specific year (all languages)
generate-year year:
    PYTHONPATH=src uv run python -m waste_calendar_extractor -y {{year}} --all-languages
    cp waste-{{year}}.ics waste.ics
    echo "✅ Generated all language-specific calendars for {{year}} and updated waste.ics"

# Generate calendar for specific language
generate-lang lang:
    PYTHONPATH=src uv run python -m waste_calendar_extractor --language {{lang}}
    echo "✅ Generated waste-{{lang}}.ics calendar"

# Generate calendar for specific language and year
generate-lang-year lang year:
    PYTHONPATH=src uv run python -m waste_calendar_extractor --language {{lang}} -y {{year}}
    echo "✅ Generated waste-{{year}}-{{lang}}.ics calendar"

# Download latest calendar PDF from commune website
download:
    PYTHONPATH=src uv run python -m waste_calendar_extractor --download
    echo "✅ Downloaded latest calendar PDF"