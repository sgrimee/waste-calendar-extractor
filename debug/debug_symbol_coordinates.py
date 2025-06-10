#!/usr/bin/env python3
"""
Detailed analysis of symbol coordinates in June 2025 page.
"""

import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

import fitz  # PyMuPDF
from waste_calendar_extractor.pdf_extractor import detect_month


def analyze_all_drawings():
    """Analyze all drawings on the June page to find symbol positions."""
    pdf_path = "tests/2025.pdf"
    
    if not Path(pdf_path).exists():
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    print("🔍 Analyzing all drawing coordinates...")
    doc = fitz.open(pdf_path)
    june_page = None
    
    # Find the June page
    for page_num in range(len(doc)):
        page = doc[page_num]
        page_text = page.get_text()
        month = detect_month(page_text)
        if month == "JUNI":
            june_page = page
            break
    
    if not june_page:
        print("❌ June page not found")
        doc.close()
        return
    
    drawings = june_page.get_drawings()
    print(f"Total drawings: {len(drawings)}")
    
    # Group drawings by X coordinate ranges
    x_ranges = {
        "0-100": [],
        "100-200": [],
        "200-300": [],
        "300-400": [],
        "400-500": [],
        "500-600": [],
        "600+": []
    }
    
    for i, drawing in enumerate(drawings):
        rect = drawing["rect"]
        x = rect[0]
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]
        y_center = (rect[1] + rect[3]) / 2
        
        # Skip very small or very large drawings
        if width < 3 or height < 3 or width > 100 or height > 100:
            continue
            
        # Categorize by X position
        if x < 100:
            x_ranges["0-100"].append((i, rect, len(drawing["items"])))
        elif x < 200:
            x_ranges["100-200"].append((i, rect, len(drawing["items"])))
        elif x < 300:
            x_ranges["200-300"].append((i, rect, len(drawing["items"])))
        elif x < 400:
            x_ranges["300-400"].append((i, rect, len(drawing["items"])))
        elif x < 500:
            x_ranges["400-500"].append((i, rect, len(drawing["items"])))
        elif x < 600:
            x_ranges["500-600"].append((i, rect, len(drawing["items"])))
        else:
            x_ranges["600+"].append((i, rect, len(drawing["items"])))
    
    print("\n📊 Drawings by X coordinate ranges:")
    for range_name, drawings_in_range in x_ranges.items():
        print(f"\n{range_name}: {len(drawings_in_range)} drawings")
        
        if len(drawings_in_range) > 0:
            print("  Index | X      | Y      | Width | Height | Items | Y-center")
            print("  ------|--------|--------|-------|--------|-------|--------")
            
            # Sort by Y position for easier calendar row identification
            drawings_in_range.sort(key=lambda d: d[1][1])
            
            for idx, rect, item_count in drawings_in_range[:20]:  # Show first 20
                x, y, x2, y2 = rect
                width = x2 - x
                height = y2 - y
                y_center = (y + y2) / 2
                print(f"  {idx:5d} | {x:6.1f} | {y:6.1f} | {width:5.1f} | {height:6.1f} | {item_count:5d} | {y_center:6.1f}")
            
            if len(drawings_in_range) > 20:
                print(f"  ... and {len(drawings_in_range) - 20} more")
    
    # Focus on potential calendar symbol areas
    print("\n🎯 Likely calendar symbol candidates:")
    print("Looking for small symbols (5-30px) in the calendar area (Y: 100-700)")
    
    candidates = []
    for i, drawing in enumerate(drawings):
        rect = drawing["rect"]
        x, y, x2, y2 = rect
        width = x2 - x
        height = y2 - y
        y_center = (y + y2) / 2
        
        # Filter for likely calendar symbols
        if (100 < y < 700 and  # Calendar Y range
            5 < width < 30 and  # Small symbol size
            5 < height < 30 and
            100 < x < 600):  # Reasonable X range
            
            candidates.append({
                "index": i,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "y_center": y_center,
                "items": len(drawing["items"])
            })
    
    candidates.sort(key=lambda c: c["y_center"])
    
    print(f"\nFound {len(candidates)} potential calendar symbols:")
    print("Index | X      | Y      | Width | Height | Items | Y-center")
    print("------|--------|--------|-------|--------|-------|--------")
    
    for candidate in candidates:
        print(f"{candidate['index']:5d} | {candidate['x']:6.1f} | {candidate['y']:6.1f} | "
              f"{candidate['width']:5.1f} | {candidate['height']:6.1f} | "
              f"{candidate['items']:5d} | {candidate['y_center']:6.1f}")
    
    # Map to potential dates
    print("\n📅 Mapping symbols to calendar dates:")
    date_positions = {
        1: 89.6, 2: 112.8, 3: 136.1, 4: 159.3, 5: 182.5,
        6: 205.7, 7: 229.0, 8: 252.2, 9: 275.4
    }
    
    tolerance = 15.0
    for date_num, date_y in date_positions.items():
        print(f"\nDay {date_num} (Y: {date_y:.1f}):")
        matching_symbols = []
        
        for candidate in candidates:
            y_distance = abs(date_y - candidate["y_center"])
            if y_distance <= tolerance:
                matching_symbols.append((candidate, y_distance))
        
        matching_symbols.sort(key=lambda x: x[1])  # Sort by distance
        
        if matching_symbols:
            for candidate, distance in matching_symbols:
                print(f"  Symbol at ({candidate['x']:.1f}, {candidate['y_center']:.1f}) "
                      f"- distance: {distance:.1f}, items: {candidate['items']}")
        else:
            print("  No symbols within tolerance")
    
    doc.close()


if __name__ == "__main__":
    analyze_all_drawings()