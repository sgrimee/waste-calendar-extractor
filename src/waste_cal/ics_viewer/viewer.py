#!/usr/bin/env python3
"""
Beautiful iCS File Viewer

A command-line tool that displays iCS calendar files in a human-readable,
colored format for verification and debugging purposes.

Features:
- Colored output with emoji icons
- Monthly calendar grid view
- Chronological event listing
- Summary statistics
- Multiple output formats
"""

import argparse
import calendar
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

try:
    from ics import Calendar
    from ics.event import Event
except ImportError:
    print("Error: ics library not found. Install with: uv add ics")
    sys.exit(1)


def get_event_date(event_begin: date | datetime | None) -> date | None:
    """Extract date from event begin property, handling both date and datetime objects."""
    if event_begin is None:
        return None
    if isinstance(event_begin, datetime):
        return event_begin.date()
    elif isinstance(event_begin, date):
        return event_begin
    else:
        # Handle Mock objects or other types that might have a date() method
        if hasattr(event_begin, "date") and callable(event_begin.date):
            return event_begin.date()
        return event_begin


# Color codes for terminal output
class Colors:
    """ANSI color codes for terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Text colors
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"

    # Background colors
    BG_RED = "\033[101m"
    BG_GREEN = "\033[102m"
    BG_YELLOW = "\033[103m"
    BG_BLUE = "\033[104m"
    BG_MAGENTA = "\033[105m"
    BG_CYAN = "\033[106m"


# Waste type color mapping
WASTE_TYPE_COLORS = {
    "🗑️": Colors.RED,  # Residual waste - red
    "📄": Colors.BLUE,  # Paper - blue
    "🪟": Colors.GREEN,  # Glass - green
    "📦": Colors.YELLOW,  # Packaging - yellow
    "🌱": Colors.GREEN,  # Organic - green
    "👕": Colors.MAGENTA,  # Clothes - magenta
    "🎄": Colors.GREEN,  # Christmas trees - green
    "♻️": Colors.CYAN,  # General recycling - cyan
}


def colorize_text(text: str, color: str, bold: bool = False) -> str:
    """Apply color and formatting to text."""
    formatting = Colors.BOLD if bold else ""
    return f"{formatting}{color}{text}{Colors.RESET}"


def get_waste_type_color(event_name: str) -> str:
    """Get color for waste type based on emoji in event name."""
    for emoji, color in WASTE_TYPE_COLORS.items():
        if emoji in event_name:
            return color
    return Colors.WHITE


def format_event_name(event_name: str) -> str:
    """Format event name with appropriate colors."""
    color = get_waste_type_color(event_name)
    return colorize_text(event_name, color, bold=True)


def load_ics_file(file_path: str) -> Calendar:
    """Load and parse iCS file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        return Calendar(content)
    except FileNotFoundError:
        print(colorize_text(f"Error: File not found: {file_path}", Colors.RED))
        sys.exit(1)
    except Exception as e:
        print(colorize_text(f"Error reading iCS file: {e}", Colors.RED))
        sys.exit(1)


def group_events_by_month(events: list[Event]) -> dict[tuple, list[Event]]:
    """Group events by year and month."""
    events_by_month = defaultdict(list)

    for event in events:
        if event.begin:
            event_date = get_event_date(event.begin)
            if event_date:
                month_key = (event_date.year, event_date.month)
                events_by_month[month_key].append(event)

    # Sort events within each month
    for month_events in events_by_month.values():
        month_events.sort(key=lambda e: get_event_date(e.begin) or date.min)

    return dict(events_by_month)


def generate_monthly_calendar(year: int, month: int, events: list[Event]) -> str:
    """Generate a monthly calendar view with events."""
    # Group events by day
    events_by_day = defaultdict(list)
    for event in events:
        if event.begin:
            event_date = get_event_date(event.begin)
            if event_date and event_date.year == year and event_date.month == month:
                events_by_day[event_date.day].append(event)

    # Generate calendar
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]

    # Header
    header = f"\n{colorize_text(f'{month_name} {year}', Colors.CYAN, bold=True)}\n"
    header += colorize_text("Mo Tu We Th Fr Sa Su", Colors.GRAY) + "\n"

    # Calendar grid
    calendar_lines = []
    for week in cal:
        week_line = ""
        for day in week:
            if day == 0:
                week_line += "   "
            else:
                day_str = f"{day:2d}"
                if day in events_by_day:
                    # Highlight days with events
                    day_str = colorize_text(day_str, Colors.WHITE, bold=True)
                else:
                    day_str = colorize_text(day_str, Colors.GRAY)
                week_line += day_str + " "
        calendar_lines.append(week_line)

    return header + "\n".join(calendar_lines) + "\n"


def generate_event_listing(events: list[Event]) -> str:
    """Generate a detailed listing of events."""
    if not events:
        return colorize_text("No events found", Colors.GRAY)

    lines = []
    current_date = None

    # Sort events by date
    sorted_events = sorted(events, key=lambda e: get_event_date(e.begin) or date.min)

    for event in sorted_events:
        if not event.begin:
            continue

        event_date = get_event_date(event.begin)
        if not event_date:
            continue

        # Add date header if it's a new date
        if current_date != event_date:
            current_date = event_date
            date_str = event_date.strftime("%A, %B %d, %Y")
            lines.append(f"\n{colorize_text(date_str, Colors.BLUE, bold=True)}")

        # Format event
        event_name = event.name or "Unnamed Event"
        colored_name = format_event_name(event_name)

        # Add location if available
        location_info = ""
        if event.location:
            location_info = f" ({colorize_text(event.location, Colors.GRAY)})"

        lines.append(f"  • {colored_name}{location_info}")

        # Add description if available and different from name
        if event.description and event.description != f"Waste collection: {event.name}":
            lines.append(f"    {colorize_text(event.description, Colors.DIM)}")

    return "\n".join(lines)


def generate_summary_statistics(events: list[Event]) -> str:
    """Generate summary statistics for the calendar."""
    if not events:
        return colorize_text("No events to analyze", Colors.GRAY)

    # Count events by type
    event_counts: defaultdict[str, int] = defaultdict(int)
    total_events = 0
    date_range: list[date | None] = [None, None]

    for event in events:
        if not event.begin:
            continue

        total_events += 1
        event_date = get_event_date(event.begin)
        if not event_date:
            continue

        # Update date range
        if date_range[0] is None or event_date < date_range[0]:
            date_range[0] = event_date
        if date_range[1] is None or event_date > date_range[1]:
            date_range[1] = event_date

        # Count by emoji/type
        event_name = event.name or "Unknown"
        for emoji in WASTE_TYPE_COLORS.keys():
            if emoji in event_name:
                event_counts[emoji] += 1
                break
        else:
            event_counts["Other"] += 1

    # Generate summary
    lines = [
        colorize_text("📊 Calendar Summary", Colors.CYAN, bold=True),
        f"Total events: {colorize_text(str(total_events), Colors.WHITE, bold=True)}",
    ]

    if date_range[0] and date_range[1]:
        start_date = date_range[0].strftime("%Y-%m-%d")
        end_date = date_range[1].strftime("%Y-%m-%d")
        lines.append(
            f"Date range: {colorize_text(start_date, Colors.YELLOW)} to {colorize_text(end_date, Colors.YELLOW)}"
        )

    if event_counts:
        lines.append("\nEvents by type:")
        for event_type, count in sorted(event_counts.items(), key=lambda x: x[1], reverse=True):
            if event_type == "Other":
                type_display = colorize_text("Other", Colors.GRAY)
            else:
                color = WASTE_TYPE_COLORS.get(event_type, Colors.WHITE)
                type_display = colorize_text(f"{event_type} {event_type}", color)
            lines.append(f"  {type_display}: {colorize_text(str(count), Colors.WHITE, bold=True)}")

    return "\n".join(lines)


def view_ics_file(file_path: str, format_type: str = "full") -> str:
    """View iCS file in specified format."""
    # Load calendar
    cal = load_ics_file(file_path)
    events = list(cal.events)

    if not events:
        return colorize_text("No events found in calendar", Colors.YELLOW)

    # Generate output based on format
    output_parts = []

    # File header
    file_name = Path(file_path).name
    output_parts.append(colorize_text(f"📅 Calendar: {file_name}", Colors.MAGENTA, bold=True))
    output_parts.append("=" * 60)

    if format_type in ["full", "summary"]:
        output_parts.append(generate_summary_statistics(events))

    if format_type in ["full", "calendar"]:
        # Group events by month and show calendar view
        events_by_month = group_events_by_month(events)
        for (year, month), month_events in sorted(events_by_month.items()):
            output_parts.append(generate_monthly_calendar(year, month, month_events))

    if format_type in ["full", "list"]:
        output_parts.append(colorize_text("\n📋 Event Details", Colors.CYAN, bold=True))
        output_parts.append("-" * 40)
        output_parts.append(generate_event_listing(events))

    return "\n".join(output_parts)


def generate_calendar_view(file_path: str) -> str:
    """Generate a comprehensive calendar view (alias for view_ics_file)."""
    return view_ics_file(file_path, "full")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Beautiful iCS calendar file viewer for verification and debugging",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s waste.ics                    # Full view of calendar
  %(prog)s waste.ics --format summary   # Show only summary
  %(prog)s waste.ics --format calendar  # Show only calendar grid
  %(prog)s waste.ics --format list      # Show only event list
  %(prog)s waste.ics --no-color         # Disable colored output
        """,
    )

    parser.add_argument("ics_file", help="Path to iCS calendar file to view")

    parser.add_argument(
        "-f",
        "--format",
        choices=["full", "summary", "calendar", "list"],
        default="full",
        help="Output format (default: full)",
    )

    parser.add_argument("--no-color", action="store_true", help="Disable colored output")

    args = parser.parse_args()

    # Disable colors if requested or if output is not a terminal
    if args.no_color or not sys.stdout.isatty():
        # Clear all color codes
        for attr_name in dir(Colors):
            if not attr_name.startswith("_"):
                setattr(Colors, attr_name, "")
        WASTE_TYPE_COLORS.clear()

    try:
        output = view_ics_file(args.ics_file, args.format)
        print(output)
    except KeyboardInterrupt:
        print(colorize_text("\nViewing cancelled", Colors.YELLOW))
        sys.exit(1)
    except Exception as e:
        print(colorize_text(f"Error: {e}", Colors.RED))
        sys.exit(1)


if __name__ == "__main__":
    main()
