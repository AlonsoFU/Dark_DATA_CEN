"""
Test script for Hierarchical Heading Detector
==============================================

Tests the heading detector on PDF documents and displays results.

Usage:
    python test_heading_detector.py <pdf_path> [--min-score 15.0] [--format markdown|json|dict]

Example:
    python test_heading_detector.py document.pdf --min-score 12.0 --format markdown
"""

import sys
import json
from pathlib import Path
from heading_detector import HeadingDetector


def test_heading_detector(
    pdf_path: str,
    min_score: float = 15.0,
    export_format: str = "dict",
    show_all_candidates: bool = False
):
    """
    Test heading detector on a PDF file.

    Args:
        pdf_path: Path to PDF file
        min_score: Minimum heading score
        export_format: Output format (dict, markdown, json)
        show_all_candidates: Show all candidates with scores (debugging)
    """
    print(f"\n{'='*60}")
    print(f"Hierarchical Heading Detector - Test")
    print(f"{'='*60}\n")

    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        print(f"❌ Error: PDF not found: {pdf_path}")
        return

    print(f"📄 PDF: {pdf_path.name}")
    print(f"📊 Min Score: {min_score}")
    print(f"📋 Format: {export_format}\n")

    try:
        with HeadingDetector(pdf_path, min_heading_score=min_score) as detector:
            # Generate TOC first (this triggers typography learning)
            print("🔍 Analyzing document typography and extracting headings...")

            if show_all_candidates:
                # Show ALL candidates with scores for debugging
                all_candidates = detector.generate_toc(return_raw_candidates=True)
                print(f"\n📋 All Candidates (Total: {len(all_candidates)}):")
                print(f"{'Score':<8} {'Page':<6} {'Text':<60}")
                print("-" * 80)

                for candidate in sorted(all_candidates, key=lambda x: x['score'], reverse=True):
                    score = candidate['score']
                    page = candidate['page']
                    text = candidate['text'][:60]
                    mark = "✅" if score >= min_score else "  "
                    print(f"{mark} {score:<6.1f} {page:<6} {text}")

                print("\n")

            # Generate actual TOC
            toc = detector.generate_toc()

            if not toc:
                print("⚠️  No headings detected with current threshold.")
                print("   Try lowering --min-score or use --show-all to see candidates.")
                return

            print(f"✅ Found {len(toc)} headings\n")

            # Display based on format
            if export_format == "markdown":
                markdown = detector.export_toc_markdown(toc, grouped_by_chapter=True)
                print(markdown)

            elif export_format == "json":
                json_output = detector.export_toc_json(toc)
                print(json.dumps(json_output, indent=2, ensure_ascii=False))

            else:  # dict format (default)
                print("📖 Table of Contents:")
                print("-" * 80)
                for entry in toc:
                    level = entry['level']
                    indent = "  " * (level - 1)
                    page = entry['page']
                    text = entry['text']
                    score = entry['score']
                    numbering = entry.get('numbering', 'none')

                    # Format with level indicator
                    level_mark = "●" if level == 1 else "○" if level == 2 else "·"
                    print(f"{indent}{level_mark} {text}")
                    print(f"{indent}  └─ Page {page} | Score: {score:.1f} | Pattern: {numbering}")

            # Statistics
            print(f"\n{'='*60}")
            print("📊 Statistics:")
            print(f"   Total headings: {len(toc)}")

            levels = {}
            for entry in toc:
                level = entry['level']
                levels[level] = levels.get(level, 0) + 1

            for level in sorted(levels.keys()):
                print(f"   Level {level}: {levels[level]} headings")

            print(f"{'='*60}\n")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Command-line interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Test Hierarchical Heading Detector on PDF documents"
    )
    parser.add_argument("pdf_path", help="Path to PDF file")
    parser.add_argument(
        "--min-score",
        type=float,
        default=15.0,
        help="Minimum heading score threshold (default: 15.0)"
    )
    parser.add_argument(
        "--format",
        choices=["dict", "markdown", "json"],
        default="dict",
        help="Output format (default: dict)"
    )
    parser.add_argument(
        "--show-all",
        action="store_true",
        help="Show all candidates with scores (debugging)"
    )

    args = parser.parse_args()

    test_heading_detector(
        pdf_path=args.pdf_path,
        min_score=args.min_score,
        export_format=args.format,
        show_all_candidates=args.show_all
    )


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: python test_heading_detector.py <pdf_path> [options]")
        print("\nOptions:")
        print("  --min-score FLOAT    Minimum heading score (default: 15.0)")
        print("  --format FORMAT      Output format: dict, markdown, json (default: dict)")
        print("  --show-all           Show all candidates with scores")
        print("\nExample:")
        print("  python test_heading_detector.py document.pdf --min-score 12.0")
        sys.exit(1)

    main()
