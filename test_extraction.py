#!/usr/bin/env python3
import sys
sys.path.append('src')

try:
    from waste_calendar_extractor.calendar_processor import extract_dates_from_pdf
    print("Successfully imported extraction module")
    
    print("Testing PDF extraction...")
    results = extract_dates_from_pdf('ressourcekalenner-nidderaanwen-web.pdf')
    print(f"Found {len(results)} events")

    # Show first few results
    for i, result in enumerate(results[:10]):
        print(f"  {i+1}. {result['date']} -> {result['icons']}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
