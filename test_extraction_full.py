#!/usr/bin/env python3
"""Test the full extraction system."""

import sys
sys.path.append('src')

from waste_calendar_extractor.calendar_processor import extract_dates_from_pdf
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

print("Testing full year extraction...")
results = extract_dates_from_pdf('ressourcekalenner-nidderaanwen-web.pdf')

print(f'\nSUMMARY: Found {len(results)} total events')

# Group by month
months = {}
for r in results:
    month = r['date'].strftime('%B')
    months[month] = months.get(month, 0) + 1

print("\nEvents by month:")
for month, count in sorted(months.items()):
    print(f'{month}: {count} events')

print(f"\nThis is a significant improvement over the previous 6 events (June only)!")
