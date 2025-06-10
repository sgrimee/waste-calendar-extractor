#!/usr/bin/env python3
import sys
sys.path.append('src')

from waste_calendar_extractor.calendar_processor import extract_dates_from_pdf

print("Starting extraction...")
# Extract all dates
results = extract_dates_from_pdf('ressourcekalenner-nidderaanwen-web.pdf', 2025)
print(f'Total events found: {len(results)}')

# Count by month
monthly_counts: dict[str, int] = {}
for result in results:
    month = result['date'].strftime('%B')
    monthly_counts[month] = monthly_counts.get(month, 0) + 1

print('\nEvents by month:')
for month, count in sorted(monthly_counts.items()):
    print(f'  {month}: {count} events')
