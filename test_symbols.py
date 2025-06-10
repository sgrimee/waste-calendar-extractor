#!/usr/bin/env python3
import sys
sys.path.append('src')

print("Starting test...")

try:
    from waste_calendar_extractor.pdf_extractor import extract_waste_symbols_from_page
    import fitz
    
    print("Opening PDF...")
    doc = fitz.open('ressourcekalenner-nidderaanwen-web.pdf')
    print(f"PDF has {len(doc)} pages")
    
    # Test on just June page (page 6, 0-indexed)
    june_page = doc[6]
    print("Extracting symbols from June page...")
    
    date_waste_map = extract_waste_symbols_from_page(june_page)
    print(f"Found waste data for {len(date_waste_map)} dates")
    
    for date, waste_types in sorted(date_waste_map.items()):
        if waste_types:  # Only show dates with waste collection
            print(f"  Date {date}: {waste_types}")
    
    doc.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
