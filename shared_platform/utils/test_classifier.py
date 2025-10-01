"""
Test script for ContentClassifier
==================================

Usage:
    python test_classifier.py /path/to/document.pdf [page_number]

Example:
    python test_classifier.py ../../../domains/operaciones/eaf/source_docs/EAF-089-2025.pdf 1
"""

import sys
import json
from pathlib import Path
from content_classifier import ContentClassifier, ContentType


def test_single_page(pdf_path: str, page_num: int):
    """Test classifier on a single page."""
    print(f"📄 Testing ContentClassifier on: {pdf_path}")
    print(f"📄 Page: {page_num}")
    print("=" * 80)

    try:
        with ContentClassifier(pdf_path) as classifier:
            blocks = classifier.classify_page(page_num)

            print(f"\n✅ Found {len(blocks)} content blocks:\n")

            # Statistics
            stats = {ct.value: 0 for ct in ContentType}

            for i, block in enumerate(blocks, 1):
                stats[block.type] += 1

                print(f"Block {i}: {block.type.upper()}")
                print(f"  Confidence: {block.confidence:.2f}")
                print(f"  BBox: ({block.bbox[0]:.1f}, {block.bbox[1]:.1f}, {block.bbox[2]:.1f}, {block.bbox[3]:.1f})")

                if block.type == ContentType.TEXT.value:
                    text_preview = block.content.get("text", "")[:80]
                    print(f"  Text: {text_preview}...")

                elif block.type == ContentType.TABLE.value:
                    rows = block.metadata.get("rows", 0)
                    cols = block.metadata.get("cols", 0)
                    print(f"  Size: {rows} rows × {cols} cols")

                elif block.type == ContentType.FORMULA.value:
                    formula = block.content.get("text", "")
                    print(f"  Formula: {formula}")

                elif block.type == ContentType.HEADING.value:
                    heading = block.content.get("text", "")
                    level = block.content.get("level", 0)
                    print(f"  Heading (L{level}): {heading}")

                elif block.type == ContentType.LIST.value:
                    list_text = block.content.get("text", "")[:60]
                    marker = block.content.get("marker", "")
                    print(f"  Marker: {marker}")
                    print(f"  Text: {list_text}...")

                elif block.type == ContentType.IMAGE.value:
                    width = block.metadata.get("width", 0)
                    height = block.metadata.get("height", 0)
                    print(f"  Size: {width} × {height} px")

                print()

            # Summary
            print("=" * 80)
            print("📊 SUMMARY:")
            print("=" * 80)
            for content_type, count in stats.items():
                if count > 0:
                    icon = {
                        "text": "📝",
                        "table": "📊",
                        "formula": "🔢",
                        "image": "🖼️",
                        "heading": "📌",
                        "list": "📋",
                        "unknown": "❓"
                    }.get(content_type, "")
                    print(f"{icon} {content_type.upper()}: {count}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def test_document(pdf_path: str, start_page: int = 1, end_page: int = 3):
    """Test classifier on document range."""
    print(f"📄 Testing ContentClassifier on document: {pdf_path}")
    print(f"📄 Pages: {start_page}-{end_page}")
    print("=" * 80)

    try:
        with ContentClassifier(pdf_path) as classifier:
            results = classifier.classify_document(start_page, end_page)

            print(f"\n✅ Processed {results['total_pages']} pages\n")

            # Statistics
            print("=" * 80)
            print("📊 DOCUMENT STATISTICS:")
            print("=" * 80)

            for content_type, count in results["statistics"].items():
                if count > 0:
                    icon = {
                        "text": "📝",
                        "table": "📊",
                        "formula": "🔢",
                        "image": "🖼️",
                        "heading": "📌",
                        "list": "📋"
                    }.get(content_type, "")
                    print(f"{icon} {content_type.upper()}: {count}")

            # Save to JSON
            output_path = Path("classifier_results.json")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            print(f"\n💾 Results saved to: {output_path}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_classifier.py <pdf_path> [page_number]")
        print("\nExamples:")
        print("  python test_classifier.py document.pdf 1")
        print("  python test_classifier.py document.pdf    # Tests pages 1-3")
        sys.exit(1)

    pdf_path = sys.argv[1]

    if not Path(pdf_path).exists():
        print(f"❌ PDF not found: {pdf_path}")
        sys.exit(1)

    if len(sys.argv) >= 3:
        page_num = int(sys.argv[2])
        test_single_page(pdf_path, page_num)
    else:
        test_document(pdf_path)