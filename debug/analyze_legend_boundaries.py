#!/usr/bin/env python3
"""
Analyze the legend boundaries to understand what should be excluded from extraction.
"""
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import fitz

def analyze_legend_boundaries():
    """Analyze where the legend is located on the June 2025 page."""
    pdf_path = "pdf/2025.pdf"
    
    # Open PDF and find June page
    doc = fitz.open(pdf_path)
    june_page = None
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        if "JUNI" in text:
            june_page = page
            print(f"Found June page: {page_num}")
            break
    
    if not june_page:
        print("Could not find June page!")
        return
    
    # Get page dimensions
    page_rect = june_page.rect
    print(f"Page dimensions: {page_rect}")
    print(f"Page width: {page_rect.width}, height: {page_rect.height}")
    
    # Extract all text elements with positions
    text_dict = june_page.get_text("dict")
    text_elements = []
    
    for block in text_dict["blocks"]:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if text:
                        bbox = span["bbox"]
                        text_elements.append({
                            "text": text,
                            "x": bbox[0],
                            "y": bbox[1],
                            "x2": bbox[2],
                            "y2": bbox[3]
                        })
    
    # Find legend-related text
    legend_texts = []
    for elem in text_elements:
        text = elem["text"].lower()
        # Look for waste type names and legend indicators
        if any(keyword in text for keyword in [
            "organesch", "rescht", "pabeier", "verpack", "elektro", 
            "problem", "gréngscht", "glas", "sperreg", "legend",
            "zeichenerklärung", "erklärung"
        ]):
            legend_texts.append(elem)
    
    print(f"\nFound {len(legend_texts)} legend-related text elements:")
    
    # Analyze X positions to find legend boundary
    x_positions = [elem["x"] for elem in legend_texts]
    if x_positions:
        min_legend_x = min(x_positions)
        max_legend_x = max(x_positions)
        avg_legend_x = sum(x_positions) / len(x_positions)
        
        print(f"Legend X positions range: {min_legend_x:.1f} to {max_legend_x:.1f}")
        print(f"Average legend X position: {avg_legend_x:.1f}")
    
    # Look at all text elements in the right portion of the page
    right_side_elements = [elem for elem in text_elements if elem["x"] > 300]
    print(f"\nText elements on right side (x > 300): {len(right_side_elements)}")
    
    # Group by X position ranges
    x_ranges = {
        "300-350": [],
        "350-400": [],
        "400-450": [],
        "450-500": [],
        "500+": []
    }
    
    for elem in right_side_elements:
        x = elem["x"]
        if 300 <= x < 350:
            x_ranges["300-350"].append(elem)
        elif 350 <= x < 400:
            x_ranges["350-400"].append(elem)
        elif 400 <= x < 450:
            x_ranges["400-450"].append(elem)
        elif 450 <= x < 500:
            x_ranges["450-500"].append(elem)
        else:
            x_ranges["500+"].append(elem)
    
    for range_name, elements in x_ranges.items():
        if elements:
            print(f"\nX range {range_name}: {len(elements)} elements")
            sample_texts = [elem["text"] for elem in elements[:5]]  # Show first 5
            print(f"  Sample texts: {sample_texts}")
    
    # Get all drawings and analyze by X position
    drawings = june_page.get_drawings()
    print(f"\nTotal drawings: {len(drawings)}")
    
    # Analyze drawings by X position
    drawing_x_ranges = {
        "0-100": 0,
        "100-200": 0, 
        "200-300": 0,
        "300-400": 0,
        "400-500": 0,
        "500+": 0
    }
    
    for drawing in drawings:
        x = drawing["rect"][0]
        if x < 100:
            drawing_x_ranges["0-100"] += 1
        elif x < 200:
            drawing_x_ranges["100-200"] += 1
        elif x < 300:
            drawing_x_ranges["200-300"] += 1
        elif x < 400:
            drawing_x_ranges["300-400"] += 1
        elif x < 500:
            drawing_x_ranges["400-500"] += 1
        else:
            drawing_x_ranges["500+"] += 1
    
    print(f"\nDrawings by X position:")
    for range_name, count in drawing_x_ranges.items():
        print(f"  {range_name}: {count} drawings")
    
    # Look at drawings in potential legend area (x > 350)
    legend_drawings = [d for d in drawings if d["rect"][0] > 350]
    print(f"\nPotential legend drawings (x > 350): {len(legend_drawings)}")
    
    if legend_drawings:
        print("Sample legend drawing positions:")
        for i, drawing in enumerate(legend_drawings[:10]):  # Show first 10
            rect = drawing["rect"]
            items = len(drawing["items"])
            print(f"  Drawing {i}: x={rect[0]:.1f}, y={rect[1]:.1f}, items={items}")
    
    # Recommend optimal extraction boundary
    print(f"\n=== RECOMMENDATION ===")
    if x_positions:
        suggested_boundary = min(min_legend_x - 20, 360)  # Leave some margin
        print(f"Suggested extraction boundary: x < {suggested_boundary:.0f}")
        print(f"This excludes legend starting around x={min_legend_x:.0f}")
    else:
        print("Could not determine legend boundary from text analysis")
        print("Using current boundary of x < 360")
    
    doc.close()

if __name__ == "__main__":
    analyze_legend_boundaries()