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

# Clean all waste and adys calendar files
clean-waste:
    @echo "Removing all waste and adys calendar files..."
    rm -f ics/waste-*.ics
    rm -f ics/adys-*.ics
    @echo "Cleaned all calendar files"

# === CALENDAR GENERATION ===

# Generate all languages for a commune and year
generate-commune commune year:
    uv run waste-cal --commune {{commune}} --pdf sources/waste-{{commune}}-{{year}}.pdf --year {{year}}
    @echo "Generated waste-{{commune}}-*.ics files"

# === ADYS GENERATION ===

# ADYS standalone for specific customer and year
generate-adys customer_id year:
    uv run waste-cal --adys --pdf sources/adys-{{customer_id}}-{{year}}.pdf --year {{year}}
    @echo "Generated adys-{{customer_id}}-*.ics files"

# Convenience alias for known customer
generate-adys-019027:
    just generate-adys 019027 2026

# === VIEWING ===

view-summary file:
    uv run python -m waste_cal.ics_viewer {{file}} --format summary

view-calendar file:
    uv run python -m waste_cal.ics_viewer {{file}} --format calendar

view-list file:
    uv run python -m waste_cal.ics_viewer {{file}} --format list

# === UTILITIES ===

# Extract ADYS cleaning dates from PDF (year auto-detected from PDF title)
extract-adys pdf:
    @echo "Extracting ADYS cleaning dates from {{pdf}}..."
    uv run python -m waste_cal.adys_extractor {{pdf}}
