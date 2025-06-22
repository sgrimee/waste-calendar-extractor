#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / "src"))

from waste_calendar_extractor.calendar_processor import extract_dates_from_pdf

# Extract results from 2025 PDF
results = extract_dates_from_pdf("pdf/2025.pdf", year=2025)

# Filter for June 2025 and print all dates
june_results = [r for r in results if r["date"].month == 6 and r["date"].year == 2025]
print("June 2025 extracted data:")
for result in sorted(june_results, key=lambda x: x["date"].day):
    print(f"  {result['date'].strftime('%Y-%m-%d')}: {result['icons']}")
print()

# Check specific failing dates
print("Failing dates analysis:")
failing_dates = [4, 5, 6, 20, 30]
for day in failing_dates:
    matches = [r for r in june_results if r["date"].day == day]
    if matches:
        print(f"June {day}: {matches[0]['icons']}")
    else:
        print(f"June {day}: NO DATA FOUND")
