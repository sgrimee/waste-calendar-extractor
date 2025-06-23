"""Unit tests for cli module."""

import datetime
import logging
from unittest.mock import Mock, patch

from waste_cal.cli import main, setup_logging
from waste_cal.waste_types import Languages


class TestSetupLogging:
    """Test setup_logging function."""

    @patch('logging.basicConfig')
    def test_setup_logging_default_level(self, mock_basic_config):
        """Test setup_logging with default INFO level."""
        setup_logging()

        mock_basic_config.assert_called_once_with(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%H:%M:%S"
        )

    @patch('logging.basicConfig')
    def test_setup_logging_debug_level(self, mock_basic_config):
        """Test setup_logging with DEBUG level."""
        setup_logging("DEBUG")

        mock_basic_config.assert_called_once_with(
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%H:%M:%S"
        )

    @patch('logging.basicConfig')
    def test_setup_logging_case_insensitive(self, mock_basic_config):
        """Test setup_logging handles lowercase level names."""
        setup_logging("info")

        mock_basic_config.assert_called_once_with(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%H:%M:%S"
        )

    @patch('logging.basicConfig')
    def test_setup_logging_warning_level(self, mock_basic_config):
        """Test setup_logging with WARNING level."""
        setup_logging("WARNING")

        mock_basic_config.assert_called_once_with(
            level=logging.WARNING,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%H:%M:%S"
        )


class TestMain:
    """Test main function."""

    @patch('waste_cal.cli.setup_logging')
    @patch('waste_cal.cli.extract_calendar_data')
    @patch('sys.argv', ['cli.py', 'extract', 'test.pdf'])
    @patch('builtins.print')
    def test_main_extract_command_basic(self, mock_print, mock_extract, mock_setup_logging):
        """Test main function with basic extract command."""
        # Setup mock calendar data
        mock_calendar_data = Mock()
        mock_calendar_data.to_text.return_value = "Mock calendar output"
        mock_extract.return_value = mock_calendar_data

        result = main()

        assert result == 0
        mock_setup_logging.assert_called_once_with("INFO")
        mock_extract.assert_called_once_with("test.pdf", datetime.datetime.now().year)
        mock_calendar_data.to_text.assert_called_once_with(Languages.EN)
        mock_print.assert_called_once_with("Mock calendar output")

    @patch('waste_cal.cli.setup_logging')
    @patch('waste_cal.cli.extract_calendar_data')
    @patch('sys.argv', ['cli.py', 'extract', 'test.pdf', '--language', 'fr', '--year', '2025'])
    @patch('builtins.print')
    def test_main_extract_with_options(self, mock_print, mock_extract, mock_setup_logging):
        """Test main function with language and year options."""
        mock_calendar_data = Mock()
        mock_calendar_data.to_text.return_value = "Mock calendar output"
        mock_extract.return_value = mock_calendar_data

        result = main()

        assert result == 0
        mock_extract.assert_called_once_with("test.pdf", 2025)
        mock_calendar_data.to_text.assert_called_once_with(Languages.FR)

    @patch('waste_cal.cli.setup_logging')
    @patch('waste_cal.cli.extract_calendar_data')
    @patch('sys.argv', ['cli.py', 'extract', '--text-output'])
    @patch('builtins.print')
    def test_main_extract_text_output(self, mock_print, mock_extract, mock_setup_logging):
        """Test main function with text output flag."""
        mock_calendar_data = Mock()
        mock_calendar_data.to_text.return_value = "Mock calendar output"
        mock_extract.return_value = mock_calendar_data

        result = main()

        assert result == 0
        # Should print the calendar data directly
        mock_print.assert_called_once_with("Mock calendar output")

    @patch('waste_cal.cli.setup_logging')
    @patch('waste_cal.cli.extract_month_drawings')
    @patch('sys.argv', ['cli.py', 'drawings', 'january', 'test.pdf'])
    def test_main_drawings_command(self, mock_extract_drawings, mock_setup_logging):
        """Test main function with drawings extraction command."""
        result = main()

        assert result == 0
        mock_setup_logging.assert_called_once_with("INFO")
        mock_extract_drawings.assert_called_once_with("test.pdf", "january", "debug")

    @patch('waste_cal.cli.setup_logging')
    @patch('waste_cal.cli.extract_month_drawings')
    @patch('sys.argv', ['cli.py', 'drawings', 'february', 'test.pdf', '--output-dir', 'custom'])
    def test_main_drawings_with_output_dir(self, mock_extract_drawings, mock_setup_logging):
        """Test main function with drawings command and custom output directory."""
        result = main()

        assert result == 0
        mock_extract_drawings.assert_called_once_with("test.pdf", "february", "custom")

    @patch('waste_cal.cli.setup_logging')
    @patch('sys.argv', ['cli.py', '--verbose'])
    @patch('builtins.print')
    def test_main_verbose_flag(self, mock_print, mock_setup_logging):
        """Test main function with verbose flag."""
        main()

        mock_setup_logging.assert_called_once_with("DEBUG")

    @patch('waste_cal.cli.setup_logging')
    @patch('waste_cal.cli.extract_calendar_data')
    @patch('sys.argv', ['cli.py', 'extract'])  # Need to specify extract command explicitly
    @patch('builtins.print')
    def test_main_no_command_defaults_to_extract(self, mock_print, mock_extract, mock_setup_logging):
        """Test main function with extract command (default behavior)."""
        mock_calendar_data = Mock()
        mock_calendar_data.to_text.return_value = "Mock calendar output"
        mock_extract.return_value = mock_calendar_data

        result = main()

        assert result == 0
        # Should use default PDF file
        default_pdf = "pdf/ressourcekalenner-nidderaanwen-web.pdf"
        mock_extract.assert_called_once_with(default_pdf, datetime.datetime.now().year)

    @patch('waste_cal.cli.setup_logging')
    @patch('waste_cal.cli.extract_calendar_data')
    @patch('sys.argv', ['cli.py', 'extract'])
    @patch('logging.error')
    def test_main_extract_exception_handling(self, mock_log_error, mock_extract, mock_setup_logging):
        """Test main function handles exceptions during extraction."""
        mock_extract.side_effect = Exception("Test extraction error")

        result = main()

        assert result == 1
        mock_log_error.assert_called_once_with("Error extracting calendar: Test extraction error")

    @patch('waste_cal.cli.setup_logging')
    @patch('waste_cal.cli.extract_month_drawings')
    @patch('sys.argv', ['cli.py', 'drawings', 'march'])
    @patch('logging.error')
    def test_main_drawings_exception_handling(self, mock_log_error, mock_extract_drawings, mock_setup_logging):
        """Test main function handles exceptions during drawings extraction."""
        mock_extract_drawings.side_effect = Exception("Test drawings error")

        result = main()

        assert result == 1
        mock_log_error.assert_called_once_with("Error extracting drawings: Test drawings error")

    @patch('waste_cal.cli.setup_logging')
    @patch('waste_cal.cli.extract_calendar_data')
    @patch('sys.argv', ['cli.py', 'extract', '--language', 'de'])
    @patch('builtins.print')
    def test_main_language_mapping(self, mock_print, mock_extract, mock_setup_logging):
        """Test that language strings are correctly mapped to enum values."""
        mock_calendar_data = Mock()
        mock_calendar_data.to_text.return_value = "Mock calendar output"
        mock_extract.return_value = mock_calendar_data

        # Test German -> Luxembourgish mapping
        result = main()

        assert result == 0
        mock_calendar_data.to_text.assert_called_once_with(Languages.LU)

    @patch('waste_cal.cli.setup_logging')
    @patch('waste_cal.cli.extract_calendar_data')
    @patch('sys.argv', ['cli.py', 'extract', '--language', 'en'])
    @patch('builtins.print')
    def test_main_english_language(self, mock_print, mock_extract, mock_setup_logging):
        """Test English language selection."""
        mock_calendar_data = Mock()
        mock_calendar_data.to_text.return_value = "Mock calendar output"
        mock_extract.return_value = mock_calendar_data

        result = main()

        assert result == 0
        mock_calendar_data.to_text.assert_called_once_with(Languages.EN)

    @patch('waste_cal.cli.setup_logging')
    @patch('waste_cal.cli.extract_calendar_data')
    @patch('sys.argv', ['cli.py', 'extract', '--language', 'fr'])
    @patch('builtins.print')
    def test_main_french_language(self, mock_print, mock_extract, mock_setup_logging):
        """Test French language selection."""
        mock_calendar_data = Mock()
        mock_calendar_data.to_text.return_value = "Mock calendar output"
        mock_extract.return_value = mock_calendar_data

        result = main()

        assert result == 0
        mock_calendar_data.to_text.assert_called_once_with(Languages.FR)
