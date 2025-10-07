"""
Clean Batch Content Extraction - Extract content with garbage filtering
Removes metadata, page numbers, headers/footers, and other noise
"""

import sys
import json
import fitz  # PyMuPDF
from pathlib import Path
from datetime import datetime
from content_classifier import ContentClassifier


def filter_garbage(blocks):
    """
    Remove garbage content (metadata, page numbers, headers, footers).

    Returns:
        List of clean content blocks
    """
    clean_blocks = []

    for block in blocks:
        # Skip metadata blocks
        if block.type == "metadata":
            continue

        # Skip very short text blocks (likely garbage)
        if block.type == "text":
            content_text = block.content.get("text", "")
            if len(content_text.strip()) < 15:  # Less than 15 chars
                continue

            # Skip if it's just a number (page number)
            if content_text.strip().isdigit():
                continue

            # Skip common footer/header patterns
            garbage_patterns = [
                "página",
                "page",
                "pág.",
                "de fecha",
                "informe",
                "coordinador eléctrico nacional",
                "coordinador eléctrico",
            ]

            text_lower = content_text.lower().strip()

            # Skip if entire text is a garbage pattern
            if any(text_lower == pattern for pattern in garbage_patterns):
                continue

            # Skip if text is very short and contains garbage keywords
            if len(content_text) < 50 and any(pattern in text_lower for pattern in garbage_patterns):
                continue

        # Keep this block
        clean_blocks.append(block)

    return clean_blocks


def extract_batch_clean(pdf_path: str, start_page: int, end_page: int, output_dir: str = "outputs"):
    """
    Extract clean content from a page range and save to JSON.

    Args:
        pdf_path: Path to PDF file
        start_page: Starting page (1-indexed)
        end_page: Ending page (1-indexed)
        output_dir: Output directory
    """
    pdf_path = Path(pdf_path)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    print(f"\n📄 Extracting pages {start_page}-{end_page} from {pdf_path.name}")

    # Create classifier
    classifier = ContentClassifier(str(pdf_path))

    # Extract content for page range
    results = {
        "document_path": str(pdf_path),
        "page_range": f"{start_page}-{end_page}",
        "total_pages": end_page - start_page + 1,
        "pages": {},
        "statistics": {
            "text": 0,
            "table": 0,
            "formula": 0,
            "image": 0,
            "heading": 0,
            "list": 0,
        },
        "extraction_metadata": {
            "source_file": str(pdf_path),
            "page_range": f"{start_page}-{end_page}",
            "extraction_date": datetime.now().isoformat(),
            "garbage_filtered": True
        }
    }

    total_blocks_raw = 0
    total_blocks_clean = 0

    for page_num in range(start_page, end_page + 1):
        # Classify page
        blocks = classifier.classify_page(page_num)
        total_blocks_raw += len(blocks)

        # Filter garbage
        clean_blocks = filter_garbage(blocks)
        total_blocks_clean += len(clean_blocks)

        # Convert to dict
        results["pages"][page_num] = {
            "page_number": page_num,
            "blocks": [block.to_dict() for block in clean_blocks],
            "block_count": len(clean_blocks),
            "blocks_removed": len(blocks) - len(clean_blocks)
        }

        # Update statistics
        for block in clean_blocks:
            if block.type in results["statistics"]:
                results["statistics"][block.type] += 1

    results["extraction_metadata"]["total_blocks_extracted"] = total_blocks_clean
    results["extraction_metadata"]["total_blocks_raw"] = total_blocks_raw
    results["extraction_metadata"]["garbage_blocks_removed"] = total_blocks_raw - total_blocks_clean

    # Save to JSON
    pdf_name = pdf_path.stem
    output_file = output_path / f"{pdf_name}_pages_{start_page}_to_{end_page}_CLEAN.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    classifier.close()

    # Print summary
    garbage_percent = (total_blocks_raw - total_blocks_clean) / total_blocks_raw * 100 if total_blocks_raw > 0 else 0
    print(f"✅ Raw blocks: {total_blocks_raw}")
    print(f"🗑️  Garbage removed: {total_blocks_raw - total_blocks_clean} ({garbage_percent:.1f}%)")
    print(f"✨ Clean blocks: {total_blocks_clean}")
    print(f"📊 Statistics:")
    for content_type, count in results["statistics"].items():
        if count > 0:
            print(f"   • {content_type}: {count}")

    file_size_kb = output_file.stat().st_size / 1024
    print(f"💾 Saved to: {output_file.name} ({file_size_kb:.1f} KB)")

    return output_file


def batch_extract_clean_all(pdf_path: str, batch_size: int = 50, output_dir: str = "outputs"):
    """
    Extract clean content from entire PDF in batches.

    Args:
        pdf_path: Path to PDF file
        batch_size: Number of pages per batch (default: 50)
        output_dir: Output directory for JSON files
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        print(f"❌ PDF not found: {pdf_path}")
        return

    # Get page count
    pdf_doc = fitz.open(str(pdf_path))
    total_pages = len(pdf_doc)
    pdf_doc.close()

    print("=" * 80)
    print(f"🧹 CLEAN BATCH CONTENT EXTRACTION")
    print("=" * 80)
    print(f"File: {pdf_path.name}")
    print(f"Total pages: {total_pages}")
    print(f"Batch size: {batch_size} pages")
    print(f"Output directory: {output_dir}")
    print(f"🗑️  Garbage filtering: ENABLED")
    print("=" * 80)

    # Calculate batches
    batches = []
    for start_page in range(1, total_pages + 1, batch_size):
        end_page = min(start_page + batch_size - 1, total_pages)
        batches.append((start_page, end_page))

    print(f"\n📦 Will extract {len(batches)} batches:")
    for i, (start, end) in enumerate(batches, 1):
        print(f"   Batch {i}: Pages {start}-{end} ({end - start + 1} pages)")

    print("\n" + "=" * 80)

    # Extract each batch
    output_files = []
    total_blocks_clean = 0
    total_blocks_raw = 0
    total_garbage = 0

    for i, (start_page, end_page) in enumerate(batches, 1):
        print(f"\n🔄 Processing Batch {i}/{len(batches)}")
        print("-" * 80)

        try:
            output_file = extract_batch_clean(
                str(pdf_path),
                start_page=start_page,
                end_page=end_page,
                output_dir=output_dir
            )
            output_files.append(output_file)

            # Read back to get stats
            with open(output_file, 'r') as f:
                data = json.load(f)
                total_blocks_clean += data["extraction_metadata"]["total_blocks_extracted"]
                total_blocks_raw += data["extraction_metadata"]["total_blocks_raw"]
                total_garbage += data["extraction_metadata"]["garbage_blocks_removed"]

        except Exception as e:
            print(f"❌ Error processing batch {i}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue

    print("\n" + "=" * 80)
    print("🎉 CLEAN EXTRACTION COMPLETED")
    print("=" * 80)
    print(f"📦 Generated {len(output_files)} JSON files")
    print(f"📊 Raw blocks: {total_blocks_raw}")
    print(f"🗑️  Garbage removed: {total_garbage} ({total_garbage/total_blocks_raw*100:.1f}%)")
    print(f"✨ Clean blocks: {total_blocks_clean}")

    if output_files:
        total_size = sum(f.stat().st_size for f in output_files) / (1024 * 1024)
        print(f"💾 Total size: {total_size:.2f} MB")
        print(f"📂 Location: {Path(output_dir).absolute()}")


def create_summary_report(pdf_path: str, output_dir: str = "outputs"):
    """
    Create a summary report of all clean extractions.

    Args:
        pdf_path: Path to original PDF
        output_dir: Directory containing clean JSON files
    """
    pdf_path = Path(pdf_path)
    output_path = Path(output_dir)
    pdf_name = pdf_path.stem

    # Find all clean JSON files
    clean_files = sorted(output_path.glob(f"{pdf_name}_pages_*_CLEAN.json"))

    if not clean_files:
        print(f"❌ No clean JSON files found for {pdf_name}")
        return

    print("=" * 80)
    print(f"📊 CLEAN EXTRACTION SUMMARY REPORT")
    print("=" * 80)
    print(f"Document: {pdf_name}")
    print(f"Batches: {len(clean_files)}")
    print("=" * 80)

    # Aggregate statistics
    total_stats = {
        "total_pages": 0,
        "total_blocks_raw": 0,
        "total_blocks_clean": 0,
        "total_garbage": 0,
        "content_types": {
            "text": 0,
            "table": 0,
            "formula": 0,
            "image": 0,
            "heading": 0,
            "list": 0,
        }
    }

    batch_summaries = []

    for clean_file in clean_files:
        with open(clean_file, 'r') as f:
            data = json.load(f)

        batch_summary = {
            "file": clean_file.name,
            "page_range": data["page_range"],
            "pages": data["total_pages"],
            "blocks_raw": data["extraction_metadata"]["total_blocks_raw"],
            "blocks_clean": data["extraction_metadata"]["total_blocks_extracted"],
            "garbage_removed": data["extraction_metadata"]["garbage_blocks_removed"],
            "garbage_percent": (data["extraction_metadata"]["garbage_blocks_removed"] /
                              data["extraction_metadata"]["total_blocks_raw"] * 100
                              if data["extraction_metadata"]["total_blocks_raw"] > 0 else 0)
        }

        batch_summaries.append(batch_summary)

        # Update totals
        total_stats["total_pages"] += data["total_pages"]
        total_stats["total_blocks_raw"] += data["extraction_metadata"]["total_blocks_raw"]
        total_stats["total_blocks_clean"] += data["extraction_metadata"]["total_blocks_extracted"]
        total_stats["total_garbage"] += data["extraction_metadata"]["garbage_blocks_removed"]

        for content_type, count in data["statistics"].items():
            if content_type in total_stats["content_types"]:
                total_stats["content_types"][content_type] += count

    # Print batch summaries
    print("\n📦 BATCH SUMMARIES:")
    print("-" * 80)
    for i, summary in enumerate(batch_summaries, 1):
        print(f"\nBatch {i}: {summary['page_range']}")
        print(f"  • Raw blocks: {summary['blocks_raw']}")
        print(f"  • Clean blocks: {summary['blocks_clean']}")
        print(f"  • Garbage removed: {summary['garbage_removed']} ({summary['garbage_percent']:.1f}%)")

    # Print totals
    print("\n" + "=" * 80)
    print("📊 TOTAL STATISTICS")
    print("=" * 80)
    print(f"Total pages: {total_stats['total_pages']}")
    print(f"Total raw blocks: {total_stats['total_blocks_raw']}")
    print(f"Total clean blocks: {total_stats['total_blocks_clean']}")
    garbage_percent = (total_stats['total_garbage'] / total_stats['total_blocks_raw'] * 100
                      if total_stats['total_blocks_raw'] > 0 else 0)
    print(f"Total garbage removed: {total_stats['total_garbage']} ({garbage_percent:.1f}%)")

    print(f"\n📊 CONTENT BREAKDOWN:")
    for content_type, count in sorted(total_stats["content_types"].items(), key=lambda x: -x[1]):
        if count > 0:
            percent = count / total_stats['total_blocks_clean'] * 100
            print(f"  • {content_type.upper()}: {count} ({percent:.1f}%)")

    print("=" * 80)

    # Save report to file
    report_file = output_path / f"{pdf_name}_CLEAN_SUMMARY.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "document": pdf_name,
            "total_statistics": total_stats,
            "batch_summaries": batch_summaries,
            "report_date": datetime.now().isoformat()
        }, f, indent=2, ensure_ascii=False)

    print(f"💾 Summary saved to: {report_file.name}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
🧹 Clean Batch Content Extraction - Remove garbage and extract clean content

Usage:
    python batch_extract_clean.py <pdf_path> [batch_size]
    python batch_extract_clean.py <pdf_path> --summary

Examples:
    # Extract clean content in 50-page batches (default)
    python batch_extract_clean.py document.pdf

    # Extract clean content in 100-page batches
    python batch_extract_clean.py document.pdf 100

    # Generate summary report of all clean extractions
    python batch_extract_clean.py document.pdf --summary

Features:
    ✨ Removes metadata (page numbers, headers, footers)
    ✨ Filters out very short text fragments
    ✨ Removes common garbage patterns
    ✨ Provides garbage removal statistics
        """)
        exit(1)

    pdf_path = sys.argv[1]
    output_dir = Path(__file__).parent / "outputs"

    # Check for --summary flag
    if len(sys.argv) > 2 and sys.argv[2] == "--summary":
        create_summary_report(pdf_path, str(output_dir))
    else:
        batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        batch_extract_clean_all(pdf_path, batch_size, str(output_dir))
