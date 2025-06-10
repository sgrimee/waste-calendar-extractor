#!/usr/bin/env python3
"""
Analyze why only 20 symbols are being detected when we expect many more.
"""
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import fitz
from waste_calendar_extractor.pdf_extractor import classify_waste_symbol

def analyze_symbol_detection():
    """Analyze why we're missing so many symbols."""
    pdf_path = "pdf/2025.pdf"
    
    # Open PDF and find June page
    doc = fitz.open(pdf_path)
    june_page = None
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        if "JUNI" in text:
            june_page = page
            break
    
    if not june_page:
        print("Could not find June page!")
        return
    
    # Get all drawings
    drawings = june_page.get_drawings()
    print(f"Total drawings on page: {len(drawings)}")
    
    # Analyze all drawings in calendar area
    calendar_drawings = []
    for i, drawing in enumerate(drawings):
        rect = drawing["rect"]
        x, y = rect[0], rect[1]
        width, height = rect[2] - rect[0], rect[3] - rect[1]
        
        # Use same bounds as current implementation
        if (
            x < 360  # Calendar area, excluding legend
            and 80 < y < 800  # Cover entire calendar
            and 3 < width < 50  # Reasonable symbol size
            and 3 < height < 50
        ):
            calendar_drawings.append({
                "index": i,
                "rect": rect,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "item_count": len(drawing["items"]),
                "drawing": drawing
            })
    
    print(f"Drawings in calendar area: {len(calendar_drawings)}")
    
    # Classify all calendar drawings
    classified = 0
    unclassified = 0
    classification_results = {}
    
    for draw_info in calendar_drawings:
        waste_type = classify_waste_symbol(draw_info["drawing"])
        if waste_type:
            classified += 1
            if waste_type not in classification_results:
                classification_results[waste_type] = []
            classification_results[waste_type].append(draw_info)
        else:
            unclassified += 1
    
    print(f"\nClassification results:")
    print(f"  Classified: {classified}")
    print(f"  Unclassified: {unclassified}")
    
    print(f"\nBy waste type:")
    for waste_type, symbols in classification_results.items():
        print(f"  {waste_type}: {len(symbols)} symbols")
        for symbol in symbols:
            print(f"    y={symbol['y']:6.1f}, items={symbol['item_count']:3d}")
    
    # Analyze unclassified symbols by item count
    unclassified_by_count = {}
    for draw_info in calendar_drawings:
        waste_type = classify_waste_symbol(draw_info["drawing"])
        if not waste_type:
            count = draw_info["item_count"]
            if count not in unclassified_by_count:
                unclassified_by_count[count] = []
            unclassified_by_count[count].append(draw_info)
    
    print(f"\nUnclassified symbols by item count:")
    for count in sorted(unclassified_by_count.keys()):
        symbols = unclassified_by_count[count]
        print(f"  {count} items: {len(symbols)} symbols")
        
        # Show item type analysis for first few
        for i, symbol in enumerate(symbols[:3]):
            drawing = symbol["drawing"]
            item_types = {}
            for item in drawing["items"]:
                item_type = item[0]
                item_types[item_type] = item_types.get(item_type, 0) + 1
            print(f"    Symbol {i+1}: y={symbol['y']:6.1f}, types={item_types}")
    
    # Look for patterns in unclassified symbols that might be waste types
    print(f"\nAnalyzing large unclassified groups for potential waste types:")
    for count, symbols in unclassified_by_count.items():
        if len(symbols) >= 3:  # Groups with multiple similar symbols
            print(f"\n{count}-item symbols ({len(symbols)} total):")
            
            # Group by Y position to see if they form rows
            symbols.sort(key=lambda s: s["y"])
            y_groups = []
            current_group = []
            last_y = -999
            
            for symbol in symbols:
                if abs(symbol["y"] - last_y) > 20:  # New row
                    if current_group:
                        y_groups.append(current_group)
                    current_group = [symbol]
                    last_y = symbol["y"]
                else:
                    current_group.append(symbol)
            
            if current_group:
                y_groups.append(current_group)
            
            print(f"  Forms {len(y_groups)} Y-groups:")
            for i, group in enumerate(y_groups):
                avg_y = sum(s["y"] for s in group) / len(group)
                print(f"    Group {i+1}: {len(group)} symbols at avg_y={avg_y:.1f}")
    
    doc.close()

if __name__ == "__main__":
    analyze_symbol_detection()