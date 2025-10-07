"""
Debug script to find "Nombre de la instalación" text
"""
import fitz
from pathlib import Path

pdf_path = Path("outputs/EAF-089-2025_pages_1_to_50_ENHANCED.pdf")

print("="*80)
print("SEARCHING FOR 'Nombre de la instalación'")
print("="*80)

with fitz.open(pdf_path) as doc:
    page = doc[0]  # Page 1
    page_width = page.rect.width
    page_center = page_width / 2

    print(f"\nPage width: {page_width}")
    print(f"Page center: {page_center}\n")

    blocks = page.get_text("dict")["blocks"]

    for block_idx, block in enumerate(blocks):
        if block.get("type") != 0:
            continue

        lines = block.get("lines", [])

        for line_idx, line in enumerate(lines):
            line_text = ""
            for span in line.get("spans", []):
                line_text += span.get("text", "")

            line_text = line_text.strip()

            if "Nombre de la instalación" in line_text or "Ambos circuitos" in line_text:
                line_bbox = line.get("bbox", [0, 0, 0, 0])
                text_center = (line_bbox[0] + line_bbox[2]) / 2
                distance = abs(text_center - page_center)

                print(f"\n{'-'*80}")
                print(f"FOUND:")
                print(f"Text: {line_text}")
                print(f"BBox: [{line_bbox[0]:.2f}, {line_bbox[1]:.2f}, {line_bbox[2]:.2f}, {line_bbox[3]:.2f}]")
                print(f"Text width: {line_bbox[2] - line_bbox[0]:.2f}px")
                print(f"Text center: {text_center:.2f}px")
                print(f"Page center: {page_center:.2f}px")
                print(f"Distance from center: {distance:.2f}px")
                print(f"Would be centered? {distance < 20}")
                print(f"Has margins? x0={line_bbox[0]:.2f} > 60 and x1={line_bbox[2]:.2f} < {page_width - 60:.2f}")

                # Check spans for formatting
                print(f"\nSpans in this line:")
                for span in line.get("spans", []):
                    flags = span.get("flags", 0)
                    is_bold = bool(flags & 2**4)
                    print(f"  - Text: '{span.get('text', '')}' | Bold: {is_bold} | Size: {span.get('size', 0):.1f} | Font: {span.get('font', '')}")
