"""Debug why 'b. Sistema de Transmisión' is not detected"""
import fitz
from pathlib import Path

pdf_path = Path("../../domains/operaciones/eaf/shared/source/EAF-089-2025.pdf")

with fitz.open(pdf_path) as pdf:
    page = pdf[19]  # Página 20
    blocks = page.get_text("dict")["blocks"]

    print(f"Total blocks in page 20: {len(blocks)}\n")

    for idx, block in enumerate(blocks):
        if block.get("type") != 0:  # Skip non-text blocks
            continue

        lines = block.get("lines", [])
        if not lines:
            continue

        # Get full text
        block_text = []
        for line in lines:
            for span in line.get("spans", []):
                block_text.append(span.get("text", ""))

        full_text = " ".join(block_text).strip()

        if "Sistema de Transmisión" in full_text or "sistema de transmisión" in full_text.lower():
            print(f"{'='*80}")
            print(f"Block {idx}: FOUND")
            print(f"Text: {full_text}")
            print(f"Text length: {len(full_text)}")
            print(f"BBox: {block.get('bbox', [])}")
            print()

            # Check all filters
            print("Checking filters:")

            # Length filter
            if len(full_text) < 5:
                print("  ❌ Too short (< 5 chars)")
            else:
                print("  ✅ Length OK")

            # Table content by pattern
            import re
            if re.search(r'\d+\s+informe?s?\s+(en|fuera de)\s+plazo', full_text.lower()):
                print("  ❌ Filtered: informe plazo pattern")
            elif 'no recibido por el cen' in full_text.lower():
                print("  ❌ Filtered: no recibido")
            else:
                print("  ✅ Not table content (by pattern)")

            # Numbering check
            patterns = [
                (r"^([A-Z]|\d+)(\.\d+){2,}\s+", "hierarchical_complex"),
                (r"^([A-Za-z]|\d+)\.\d+\s+", "hierarchical_two"),
                (r"^\d+[\.\)\-]\s+", "numbered"),
                (r"^[IVX]+[\.\)]\s+", "roman"),
                (r"^[a-z][\.\)\-]\s+(?![A-Z]\.)", "letter"),
            ]

            has_numbering = False
            for pattern, name in patterns:
                if re.match(pattern, full_text, re.IGNORECASE):
                    print(f"  ✅ Has numbering: {name}")
                    has_numbering = True
                    break

            if not has_numbering:
                print(f"  ❌ NO numbering pattern matches")

            print(f"{'='*80}\n")
