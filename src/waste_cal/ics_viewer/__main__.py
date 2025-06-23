#!/usr/bin/env python3
"""
Entry point for running the iCS viewer as a module.

Usage:
    python -m waste_calendar_extractor.ics_viewer <ics_file>
"""

from waste_cal.ics_viewer.viewer import main

if __name__ == "__main__":
    main()
