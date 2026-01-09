"""Unit tests for csv_extractor module."""

import datetime
import tempfile
from pathlib import Path

import pytest

from waste_cal.calendar_processor import CalendarData
from waste_cal.csv_extractor import (
    _csv_type_to_waste_type,
    _parse_csv,
    _parse_date,
    extract_calendar_data_from_csv,
    get_communes,
)
from waste_cal.waste_types import WasteType


class TestParseDate:
    """Test _parse_date function."""

    def test_parse_valid_date(self):
        """Test parsing valid DD/MM/YYYY format."""
        date = _parse_date("12/01/2026")
        assert date == datetime.date(2026, 1, 12)

    def test_parse_first_of_month(self):
        """Test parsing first day of month."""
        date = _parse_date("01/02/2026")
        assert date == datetime.date(2026, 2, 1)

    def test_parse_last_day_of_month(self):
        """Test parsing last day of month."""
        date = _parse_date("31/01/2026")
        assert date == datetime.date(2026, 1, 31)

    def test_parse_leap_year_date(self):
        """Test parsing date in leap year."""
        date = _parse_date("29/02/2024")
        assert date == datetime.date(2024, 2, 29)

    def test_parse_invalid_format(self):
        """Test parsing invalid date format."""
        with pytest.raises(ValueError, match="Invalid date format"):
            _parse_date("2026-01-12")

    def test_parse_invalid_date(self):
        """Test parsing invalid date (e.g., Feb 30)."""
        with pytest.raises(ValueError):
            _parse_date("30/02/2026")


class TestCsvTypeToWasteType:
    """Test _csv_type_to_waste_type function."""

    @pytest.mark.parametrize(
        "french_type,expected_waste_type",
        [
            ("Biodéchets", WasteType.ORGANIC),
            ("Déchets ménagers en mélange", WasteType.RESIDUAL),
            ("Papier/Carton", WasteType.PAPER),
            ("Papier/Carton (commerces)", WasteType.PAPER_COMMERCIAL),
            ("Valorlux", WasteType.PACKAGING),
            ("Verre", WasteType.GLASS),
            ("Verre (commerces)", WasteType.GLASS_COMMERCIAL),
            ("Déchets d’équipements électriques et électroniques", WasteType.ELECTRIC),
            ("Déchets de verdure", WasteType.HEDGE),
            ("SuperDrecksKëscht", WasteType.PROBLEMATIC),
            ("Déchets encombrants", WasteType.BULKY),
            ("Vieux vêtements", WasteType.CLOTHERS),
            ("Arbres de Noël", WasteType.CHRISTMAS_TREES),
            ("Ferraille", WasteType.SCRAP_METAL),
            ("Vieux bois", WasteType.OLD_WOOD),
            ("Déchets recyclables", WasteType.RECYCLABLE),
            ("Conteneur pour déchets ménagers", WasteType.CONTAINER),
        ],
    )
    def test_all_mapped_types(self, french_type, expected_waste_type):
        """Test all 17 collection types map correctly."""
        result = _csv_type_to_waste_type(french_type)
        assert result == expected_waste_type

    def test_unknown_type_returns_none(self):
        """Test unknown type returns None."""
        result = _csv_type_to_waste_type("Unknown Type")
        assert result is None

    def test_case_sensitive(self):
        """Test type mapping is case sensitive."""
        result = _csv_type_to_waste_type("biodéchets")  # lowercase
        assert result is None

    def test_electric_type_with_curly_apostrophe(self):
        """Test electric waste type with Unicode curly apostrophe (U+2019)."""
        # This test ensures the CSV mapping correctly handles the Unicode
        # right single quotation mark used in public.data.lu CSV exports
        result = _csv_type_to_waste_type("Déchets d’équipements électriques et électroniques")
        assert result == WasteType.ELECTRIC

    def test_electric_type_mapping_is_exact(self):
        """Test that the electric waste type requires exact match."""
        # Verify with slight variation (missing space) doesn't work
        result = _csv_type_to_waste_type("Déchets d'équipementséletriques et électroniques")
        assert result is None


class TestParseCsv:
    """Test _parse_csv function."""

    def test_parse_valid_csv(self):
        """Test parsing valid CSV with BOM."""
        csv_content = """\"Date\";\"Type de collecte\";\"Commune\";\"Localité\";\"Rue\"
\"12/01/2026\";\"Biodéchets\";\"Niederanven\";;\"Toutes les rues\"
\"13/01/2026\";\"Déchets encombrants\";\"Niederanven\";;\"Toutes les rues\"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8-sig") as f:
            f.write(csv_content)
            csv_path = f.name

        try:
            rows = _parse_csv(csv_path)
            assert len(rows) == 2
            assert rows[0]["Commune"] == "Niederanven"
            assert rows[0]["Type de collecte"] == "Biodéchets"
            assert rows[1]["Type de collecte"] == "Déchets encombrants"
        finally:
            Path(csv_path).unlink()

    def test_parse_csv_with_empty_fields(self):
        """Test parsing CSV with empty fields."""
        csv_content = """\"Date\";\"Type de collecte\";\"Commune\";\"Localité\";\"Rue\"
\"12/01/2026\";\"Biodéchets\";\"Niederanven\";;\"Toutes les rues\"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8-sig") as f:
            f.write(csv_content)
            csv_path = f.name

        try:
            rows = _parse_csv(csv_path)
            assert len(rows) == 1
            assert rows[0]["Localité"] == ""
            assert rows[0]["Rue"] == "Toutes les rues"
        finally:
            Path(csv_path).unlink()

    def test_parse_nonexistent_file(self):
        """Test parsing nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="CSV file not found"):
            _parse_csv("/nonexistent/path/file.csv")


class TestGetCommunes:
    """Test get_communes function."""

    def test_get_communes_from_test_file(self):
        """Test extracting communes from test CSV."""
        csv_path = Path(__file__).parent.parent / "data" / "test_waste_data.csv"
        communes = get_communes(str(csv_path))

        assert "Niederanven" in communes
        assert "Contern" in communes
        assert "Sandweiler" in communes
        assert len(communes) == 3
        # Verify sorted
        assert communes == sorted(communes)

    def test_get_communes_no_duplicates(self):
        """Test communes list has no duplicates."""
        csv_content = """\"Date\";\"Type de collecte\";\"Commune\";\"Localité\";\"Rue\"
\"12/01/2026\";\"Biodéchets\";\"Niederanven\";;\"Toutes les rues\"
\"13/01/2026\";\"Biodéchets\";\"Niederanven\";;\"Toutes les rues\"
\"14/01/2026\";\"Biodéchets\";\"Niederanven\";;\"Rue A\"
\"15/01/2026\";\"Biodéchets\";\"Niederanven\";;\"Rue B\"
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8-sig") as f:
            f.write(csv_content)
            csv_path = f.name

        try:
            communes = get_communes(csv_path)
            assert communes == ["Niederanven"]
            assert len(communes) == 1
        finally:
            Path(csv_path).unlink()


class TestExtractCalendarDataFromCsv:
    """Test extract_calendar_data_from_csv function."""

    def test_extract_niederanven_data(self):
        """Test extracting calendar data for Niederanven."""
        csv_path = Path(__file__).parent.parent / "data" / "test_waste_data.csv"
        calendar_data = extract_calendar_data_from_csv(str(csv_path), "Niederanven")

        # Verify it returns CalendarData object
        assert isinstance(calendar_data, CalendarData)

        # Verify dates are extracted
        dates = calendar_data.get_all_dates()
        assert len(dates) == 9

        # Verify dates are sorted
        assert dates == sorted(dates)

    def test_extract_contern_data_deduplicates(self):
        """Test that street-level data is deduplicated."""
        csv_path = Path(__file__).parent.parent / "data" / "test_waste_data.csv"
        calendar_data = extract_calendar_data_from_csv(str(csv_path), "Contern")

        # Contern has 5 rows but only 2 unique (date, type) combinations:
        # - Jan 10: Arbres de Noël (3 streets)
        # - Jan 12: Valorlux (2 streets)
        dates = calendar_data.get_all_dates()
        assert len(dates) == 2

        # Verify collections on each date
        jan_10 = datetime.date(2026, 1, 10)
        jan_12 = datetime.date(2026, 1, 12)

        assert WasteType.CHRISTMAS_TREES in calendar_data.get_collections_for_date(jan_10)
        assert WasteType.PACKAGING in calendar_data.get_collections_for_date(jan_12)

    def test_extract_all_new_waste_types(self):
        """Test extracting all new waste types."""
        csv_path = Path(__file__).parent.parent / "data" / "test_waste_data.csv"
        calendar_data = extract_calendar_data_from_csv(str(csv_path), "Sandweiler")

        collections = calendar_data.get_all_dates()
        assert len(collections) == 6

        # Verify each new type appears
        all_waste_types = set()
        for date in collections:
            all_waste_types.update(calendar_data.get_collections_for_date(date))

        assert WasteType.SCRAP_METAL in all_waste_types
        assert WasteType.OLD_WOOD in all_waste_types
        assert WasteType.RECYCLABLE in all_waste_types
        assert WasteType.CONTAINER in all_waste_types
        assert WasteType.PAPER_COMMERCIAL in all_waste_types
        assert WasteType.GLASS_COMMERCIAL in all_waste_types

    def test_extract_unknown_commune_raises_error(self):
        """Test extracting unknown commune raises ValueError."""
        csv_path = Path(__file__).parent.parent / "data" / "test_waste_data.csv"

        with pytest.raises(ValueError, match="Commune 'UnknownCommune' not found"):
            extract_calendar_data_from_csv(str(csv_path), "UnknownCommune")

    def test_extract_nonexistent_file_raises_error(self):
        """Test extracting from nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            extract_calendar_data_from_csv("/nonexistent/path.csv", "Niederanven")

    def test_calendar_data_compatibility(self):
        """Test returned CalendarData is compatible with ical_generator."""
        csv_path = Path(__file__).parent.parent / "data" / "test_waste_data.csv"
        calendar_data = extract_calendar_data_from_csv(str(csv_path), "Niederanven")

        # Verify CalendarData has required methods
        assert hasattr(calendar_data, "get_all_dates")
        assert callable(calendar_data.get_all_dates)

        assert hasattr(calendar_data, "get_collections_for_date")
        assert callable(calendar_data.get_collections_for_date)

        # Verify methods work correctly
        dates = calendar_data.get_all_dates()
        assert len(dates) > 0

        for date in dates:
            collections = calendar_data.get_collections_for_date(date)
            assert isinstance(collections, list)
            assert len(collections) > 0


class TestCsvExtractorIntegration:
    """Integration tests for CSV extractor."""

    def test_extract_and_convert_to_text(self):
        """Test extracting and converting to text format."""
        csv_path = Path(__file__).parent.parent / "data" / "test_waste_data.csv"
        calendar_data = extract_calendar_data_from_csv(str(csv_path), "Niederanven")

        from waste_cal.waste_types import Languages

        text = calendar_data.to_text(Languages.EN)
        assert "Organic waste" in text or "🍌" in text
        assert len(text) > 0
