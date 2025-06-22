"""
iCS File Viewer Module

A beautiful, colored command-line viewer for iCS calendar files.
Provides human-readable output to verify generated calendars are correct.

This module includes:
- Colored terminal output with waste type icons
- Monthly calendar view
- Event listing with details
- Summary statistics
- Verification utilities
"""

from .viewer import generate_calendar_view, main, view_ics_file

__all__ = ["main", "view_ics_file", "generate_calendar_view"]
