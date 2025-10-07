"""
Debug script to analyze page 1 heading detection
"""
import fitz
import re
from pathlib import Path

pdf_path = Path("outputs/EAF-089-2025_pages_1_to_50_ENHANCED.pdf")

# Numbering patterns (same as heading_detector.py)
numbering_patterns = [
    (r"^([A-Z]|\d+)(\.\d+){2,}\s+", "hierarchical_complex"),  # 1.1.1
    (r"^([A-Z]|\d+)\.\d+[\.\)]\s+", "hierarchical_two"),      # 1.1, 7.2
    (r"^\d+[\.\)\-]\s+", "numbered"),                          # 1., 2)
    (r"^[IVX]+[\.\)]\s+", "roman"),                            # I., II.
    (r"^[A-Za-z][\.\)\-]\s+", "letter"),                       # a., b., A.
]

def has_numbering(text):
    """Check if text starts with numbering pattern"""
    for pattern, pattern_type in numbering_patterns:
        if re.match(pattern, text.strip()):
            return True, pattern_type
    return False, None

def is_centered(bbox, page_width):
    """Check if text is centered"""
    x0, y0, x1, y1 = bbox
    text_center = (x0 + x1) / 2
    page_center = page_width / 2

    is_near_center = abs(text_center - page_center) < 20
    has_margins = x0 > 60 and x1 < (page_width - 60)

    distance = abs(text_center - page_center)

    return is_near_center and has_margins, distance

print("="*80)
print("ANALYZING PAGE 1 - ALL TEXT BLOCKS")
print("="*80)

with fitz.open(pdf_path) as doc:
    page = doc[0]  # Page 1 (index 0)
    page_width = page.rect.width
    blocks = page.get_text("dict")["blocks"]

    print(f"\nPage width: {page_width}")
    print(f"Page center: {page_width/2}")
    print(f"\nTotal blocks: {len(blocks)}\n")

    for idx, block in enumerate(blocks):
        if block.get("type") != 0:  # Only text blocks
            continue

        lines = block.get("lines", [])
        if not lines:
            continue

        # Get full text
        full_text = ""
        for line in lines:
            for span in line.get("spans", []):
                full_text += span.get("text", "")

        full_text = full_text.strip()

        if len(full_text) < 5:
            continue

        # Check if it's one of the items we're interested in
        if any(keyword in full_text.lower() for keyword in ["fecha", "identificación", "nombre de la instalación", "elemento fallado"]):
            bbox = block.get("bbox", [0, 0, 0, 0])
            has_num, num_type = has_numbering(full_text)
            centered, distance = is_centered(bbox, page_width)

            print(f"\n{'='*80}")
            print(f"Block {idx}:")
            print(f"Text: {full_text[:100]}")
            print(f"BBox: {bbox}")
            print(f"Has numbering: {has_num} ({num_type})")
            print(f"Is centered: {centered} (distance from center: {distance:.2f}px)")
            print(f"X0: {bbox[0]:.2f}, X1: {bbox[2]:.2f}")
            print(f"Text center: {(bbox[0] + bbox[2])/2:.2f}")
