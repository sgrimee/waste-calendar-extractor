"""Unit tests for cli module."""

import datetime
import logging
from unittest.mock import Mock, patch

from waste_cal.cli import main, setup_logging
from waste_cal.waste_types import Languages


class TestSetupLogging:
    """Test setup_logging function."""

    @patch("logging.basicConfig")
    def test_setup_logging_default_level(self, mock_basic_config):
        """Test setup_logging with default INFO level."""
        setup_logging()

        mock_basic_config.assert_called_once_with(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
        )

    @patch("logging.basicConfig")
    def test_setup_logging_debug_level(self, mock_basic_config):
        """Test setup_logging with DEBUG level."""
        setup_logging("DEBUG")

        mock_basic_config.assert_called_once_with(
            level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
        )

    @patch("logging.basicConfig")
    def test_setup_logging_case_insensitive(self, mock_basic_config):
        """Test setup_logging handles lowercase level names."""
        setup_logging("info")

        mock_basic_config.assert_called_once_with(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
        )

    @patch("logging.basicConfig")
    def test_setup_logging_warning_level(self, mock_basic_config):
        """Test setup_logging with WARNING level."""
        setup_logging("WARNING")

        mock_basic_config.assert_called_once_with(
            level=logging.WARNING, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
        )


class TestMainCommuneMode:
    """Test main function in commune mode."""

    @patch("waste_cal.cli.setup_logging")
    @patch("waste_cal.cli.extract_calendar_data")
    @patch("waste_cal.cli.generate_all_commune_ical_files")
    @patch("sys.argv", ["cli.py", "--commune", "niederanven", "--pdf", "sources/waste-niederanven-2026.pdf"])
    @patch("builtins.print")
    def test_commune_mode_basic(self, mock_print, mock_generate_all, mock_extract, mock_setup_logging, tmp_path):
        """Test commune mode with basic arguments."""
        mock_calendar_data = Mock()
        mock_extract.return_value = mock_calendar_data
        mock_generate_all.return_value = [
            str(tmp_path / "waste-niederanven-en.ics"),
            str(tmp_path / "waste-en.ics"),
            str(tmp_path / "waste-niederanven-fr.ics"),
            str(tmp_path / "waste-fr.ics"),
            str(tmp_path / "waste-niederanven-lu.ics"),
            str(tmp_path / "waste-lu.ics"),
        ]

        result = main()

        assert result == 0
        mock_setup_logging.assert_called_once_with("INFO")
        mock_extract.assert_called_once_with("sources/waste-niederanven-2026.pdf", datetime.datetime.now().year)
        mock_generate_all.assert_called_once_with(mock_calendar_data, "niederanven", datetime.datetime.now().year)
        mock_print.assert_not_called()

    @patch("waste_cal.cli.setup_logging")
    @patch("waste_cal.cli.extract_calendar_data")
    @patch("waste_cal.cli.generate_commune_ical_file")
    @patch(
        "sys.argv",
        [
            "cli.py",
            "--commune",
            "niederanven",
            "--pdf",
            "sources/waste-niederanven-2025.pdf",
            "--language",
            "fr",
            "--year",
            "2025",
        ],
    )
    @patch("builtins.print")
    def test_commune_mode_with_options(
        self, mock_print, mock_generate_single, mock_extract, mock_setup_logging, tmp_path
    ):
        """Test commune mode with language and year options."""
        mock_calendar_data = Mock()
        mock_extract.return_value = mock_calendar_data
        mock_generate_single.return_value = [
            str(tmp_path / "waste-niederanven-fr.ics"),
            str(tmp_path / "waste-fr.ics"),
        ]

        result = main()

        assert result == 0
        mock_extract.assert_called_once_with("sources/waste-niederanven-2025.pdf", 2025)
        mock_generate_single.assert_called_once_with(mock_calendar_data, "niederanven", Languages.FR, 2025)
        mock_print.assert_not_called()

    @patch("waste_cal.cli.setup_logging")
    @patch("waste_cal.cli.extract_calendar_data")
    @patch("sys.argv", ["cli.py", "--commune", "niederanven", "--pdf", "sources/waste-niederanven-2026.pdf", "--text"])
    @patch("builtins.print")
    def test_commune_mode_text_output(self, mock_print, mock_extract, mock_setup_logging):
        """Test commune mode with text output flag."""
        mock_calendar_data = Mock()
        mock_calendar_data.to_text.return_value = "Mock calendar output"
        mock_extract.return_value = mock_calendar_data

        result = main()

        assert result == 0
        mock_print.assert_called_once_with("Mock calendar output")

    @patch("waste_cal.cli.setup_logging")
    @patch("waste_cal.cli.extract_calendar_data")
    @patch("waste_cal.cli.generate_all_commune_ical_files")
    @patch(
        "sys.argv", ["cli.py", "--commune", "niederanven", "--pdf", "sources/waste-niederanven-2026.pdf", "--verbose"]
    )
    @patch("builtins.print")
    def test_verbose_flag(self, mock_print, mock_generate_all, mock_extract, mock_setup_logging, tmp_path):
        """Test verbose flag."""
        mock_calendar_data = Mock()
        mock_extract.return_value = mock_calendar_data
        mock_generate_all.return_value = [str(tmp_path / "waste-niederanven-en.ics")]

        main()

        mock_setup_logging.assert_called_once_with("DEBUG")

    @patch("waste_cal.cli.setup_logging")
    @patch("waste_cal.cli.extract_calendar_data")
    @patch("waste_cal.cli.generate_commune_ical_file")
    @patch("sys.argv", ["cli.py", "--commune", "niederanven", "--pdf", "custom.pdf", "--language", "lu"])
    @patch("builtins.print")
    def test_custom_pdf_path(self, mock_print, mock_generate_single, mock_extract, mock_setup_logging, tmp_path):
        """Test custom PDF path override."""
        mock_calendar_data = Mock()
        mock_extract.return_value = mock_calendar_data
        mock_generate_single.return_value = [str(tmp_path / "waste-niederanven-lu.ics")]

        result = main()

        assert result == 0
        mock_extract.assert_called_once_with("custom.pdf", datetime.datetime.now().year)

    @patch("waste_cal.cli.setup_logging")
    @patch("waste_cal.cli.extract_calendar_data")
    @patch("sys.argv", ["cli.py", "--commune", "niederanven", "--pdf", "sources/waste-niederanven-2026.pdf"])
    @patch("logging.error")
    def test_exception_handling(self, mock_log_error, mock_extract, mock_setup_logging):
        """Test exception handling in commune mode."""
        mock_extract.side_effect = Exception("Test extraction error")

        result = main()

        assert result == 1
        mock_log_error.assert_called_once_with("Error: Test extraction error")


class TestMainAdysMode:
    """Test main function in ADYS mode."""

    @patch("waste_cal.cli.setup_logging")
    @patch("waste_cal.cli.extract_adys_dates")
    @patch("waste_cal.cli.extract_customer_id_from_filename")
    @patch("waste_cal.cli.generate_all_adys_ical_files")
    @patch("sys.argv", ["cli.py", "--adys", "--pdf", "sources/adys-019027-2026.pdf"])
    @patch("builtins.print")
    def test_adys_mode_basic(
        self, mock_print, mock_generate_all, mock_extract_id, mock_extract_dates, mock_setup_logging, tmp_path
    ):
        """Test ADYS mode with basic arguments."""
        mock_extract_id.return_value = "019027"
        mock_extract_dates.return_value = ["2025-03-03", "2025-06-09"]
        mock_generate_all.return_value = [
            str(tmp_path / "adys-019027-lu.ics"),
            str(tmp_path / "adys-019027-fr.ics"),
            str(tmp_path / "adys-019027-en.ics"),
        ]

        result = main()

        assert result == 0
        mock_extract_id.assert_called_once_with("sources/adys-019027-2026.pdf")
        mock_extract_dates.assert_called_once_with("sources/adys-019027-2026.pdf")
        mock_generate_all.assert_called_once()
        mock_print.assert_not_called()

    @patch("waste_cal.cli.setup_logging")
    @patch("waste_cal.cli.extract_adys_dates")
    @patch("waste_cal.cli.extract_customer_id_from_filename")
    @patch("waste_cal.cli.generate_adys_ical_file")
    @patch("sys.argv", ["cli.py", "--adys", "--pdf", "sources/adys-019027-2026.pdf", "--language", "en"])
    @patch("builtins.print")
    def test_adys_mode_single_language(
        self, mock_print, mock_generate_single, mock_extract_id, mock_extract_dates, mock_setup_logging, tmp_path
    ):
        """Test ADYS mode with single language."""
        mock_extract_id.return_value = "019027"
        mock_extract_dates.return_value = ["2025-03-03"]
        mock_generate_single.return_value = str(tmp_path / "adys-019027-en.ics")

        result = main()

        assert result == 0
        mock_generate_single.assert_called_once()

    @patch("waste_cal.cli.setup_logging")
    @patch("waste_cal.cli.extract_adys_dates")
    @patch("waste_cal.cli.generate_all_adys_ical_files")
    @patch("sys.argv", ["cli.py", "--adys", "--pdf", "sources/adys-019027-2026.pdf", "--customer-id", "019027"])
    @patch("builtins.print")
    def test_adys_mode_explicit_customer_id(
        self, mock_print, mock_generate_all, mock_extract_dates, mock_setup_logging, tmp_path
    ):
        """Test ADYS mode with explicit customer ID."""
        mock_extract_dates.return_value = ["2025-03-03"]
        mock_generate_all.return_value = [str(tmp_path / "adys-019027-en.ics")]

        result = main()

        assert result == 0
        # Should use explicit customer ID, not extract from filename
        mock_generate_all.assert_called_once()
        call_args = mock_generate_all.call_args
        assert call_args[0][1] == "019027"  # customer_id argument

    @patch("waste_cal.cli.setup_logging")
    @patch("waste_cal.cli.extract_adys_dates")
    @patch("sys.argv", ["cli.py", "--adys", "--pdf", "sources/adys-019027-2026.pdf", "--text"])
    @patch("builtins.print")
    @patch("waste_cal.cli.extract_customer_id_from_filename")
    def test_adys_mode_text_output(self, mock_extract_id, mock_print, mock_extract_dates, mock_setup_logging):
        """Test ADYS mode with text output."""
        mock_extract_id.return_value = "019027"
        mock_extract_dates.return_value = ["2025-03-03", "2025-06-09"]

        result = main()

        assert result == 0
        # Should print dates to stdout
        assert mock_print.called

    @patch("waste_cal.cli.setup_logging")
    @patch("waste_cal.cli.extract_customer_id_from_filename")
    @patch("sys.argv", ["cli.py", "--adys", "--pdf", "sources/adys-019027-2026.pdf"])
    @patch("logging.error")
    def test_adys_mode_missing_customer_id(self, mock_log_error, mock_extract_id, mock_setup_logging):
        """Test ADYS mode fails gracefully when customer ID cannot be extracted."""
        mock_extract_id.return_value = None

        result = main()

        assert result == 1
        mock_log_error.assert_called()


class TestMainLanguageMapping:
    """Test language string to enum mapping."""

    @patch("waste_cal.cli.setup_logging")
    @patch("waste_cal.cli.extract_calendar_data")
    @patch("waste_cal.cli.generate_commune_ical_file")
    @patch(
        "sys.argv",
        ["cli.py", "--commune", "niederanven", "--pdf", "sources/waste-niederanven-2026.pdf", "--language", "lu"],
    )
    @patch("builtins.print")
    def test_luxembourgish_mapping(self, mock_print, mock_generate_single, mock_extract, mock_setup_logging, tmp_path):
        """Test that 'lu' maps to Languages.LU."""
        mock_calendar_data = Mock()
        mock_extract.return_value = mock_calendar_data
        mock_generate_single.return_value = [str(tmp_path / "waste-niederanven-lu.ics")]

        result = main()

        assert result == 0
        mock_generate_single.assert_called_once()
        call_args = mock_generate_single.call_args
        assert call_args[0][2] == Languages.LU

    @patch("waste_cal.cli.setup_logging")
    @patch("waste_cal.cli.extract_calendar_data")
    @patch("waste_cal.cli.generate_commune_ical_file")
    @patch(
        "sys.argv",
        ["cli.py", "--commune", "niederanven", "--pdf", "sources/waste-niederanven-2026.pdf", "--language", "fr"],
    )
    @patch("builtins.print")
    def test_french_mapping(self, mock_print, mock_generate_single, mock_extract, mock_setup_logging, tmp_path):
        """Test that 'fr' maps to Languages.FR."""
        mock_calendar_data = Mock()
        mock_extract.return_value = mock_calendar_data
        mock_generate_single.return_value = [str(tmp_path / "waste-niederanven-fr.ics")]

        result = main()

        assert result == 0
        mock_generate_single.assert_called_once()
        call_args = mock_generate_single.call_args
        assert call_args[0][2] == Languages.FR

    @patch("waste_cal.cli.setup_logging")
    @patch("waste_cal.cli.extract_calendar_data")
    @patch("waste_cal.cli.generate_commune_ical_file")
    @patch(
        "sys.argv",
        ["cli.py", "--commune", "niederanven", "--pdf", "sources/waste-niederanven-2026.pdf", "--language", "en"],
    )
    @patch("builtins.print")
    def test_english_mapping(self, mock_print, mock_generate_single, mock_extract, mock_setup_logging, tmp_path):
        """Test that 'en' maps to Languages.EN."""
        mock_calendar_data = Mock()
        mock_extract.return_value = mock_calendar_data
        mock_generate_single.return_value = [str(tmp_path / "waste-niederanven-en.ics")]

        result = main()

        assert result == 0
        mock_generate_single.assert_called_once()
        call_args = mock_generate_single.call_args
        assert call_args[0][2] == Languages.EN
