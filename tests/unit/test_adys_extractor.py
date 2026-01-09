"""Unit tests for adys_extractor module."""

import pytest

from waste_cal.adys_extractor import extract_customer_id_from_filename


class TestExtractCustomerIdFromFilename:
    """Test extract_customer_id_from_filename function."""

    @pytest.mark.parametrize(
        "filename,expected_id",
        [
            ("sources/adys-019027-2026.pdf", "019027"),
            ("adys-019027-2026.pdf", "019027"),
            ("/path/to/adys-123456-2026.pdf", "123456"),
            ("adys-000001-2026.pdf", "000001"),
            ("adys-999999-2026.pdf", "999999"),
        ],
    )
    def test_extracts_customer_id(self, filename: str, expected_id: str):
        """Test that customer ID is correctly extracted from valid filenames."""
        result = extract_customer_id_from_filename(filename)
        assert result == expected_id

    @pytest.mark.parametrize(
        "filename",
        [
            "adys.pdf",
            "sources/adys.pdf",
            "waste-calendar.pdf",
            "adys-.pdf",
            "adys-abc.pdf",  # Non-numeric ID
            "19027.pdf",  # Missing adys- prefix
            "ADYS-019027.pdf",  # Uppercase (case-sensitive)
        ],
    )
    def test_returns_none_for_invalid_filenames(self, filename: str):
        """Test that None is returned for filenames without valid customer ID pattern."""
        result = extract_customer_id_from_filename(filename)
        assert result is None

    def test_handles_complex_paths(self):
        """Test that extraction works with complex paths."""
        result = extract_customer_id_from_filename("/home/user/documents/sources/adys-019027-2026.pdf")
        assert result == "019027"

    def test_handles_relative_paths(self):
        """Test that extraction works with relative paths."""
        result = extract_customer_id_from_filename("./sources/adys-019027-2026.pdf")
        assert result == "019027"
