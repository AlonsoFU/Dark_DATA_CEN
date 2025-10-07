"""
Extract PDF content WITH metadata preservation
Extracts content blocks AND page metadata (page numbers, footers) to JSON
"""

import sys
import json
import fitz
from pathlib import Path
from datetime import datetime
from content_classifier import ContentClassifier


def extract_page_metadata(pdf_doc, page_num: int):
    """Extract metadata from bottom of page (page number, footer info)."""
    page = pdf_doc[page_num - 1]
    blocks = page.get_text('dict')['blocks']

    metadata = {
        "page_number_text": None,
        "footer_text": None,
        "page_height": page.rect.height
    }

    # Find text blocks at bottom of page (Y > 700 typically)
    bottom_threshold = page.rect.height * 0.9  # Bottom 10% of page

    for block in blocks:
        if block['type'] == 0:  # Text block
            bbox = block['bbox']
            if bbox[1] > bottom_threshold:  # In bottom region
                text = ''
                for line in block.get('lines', []):
                    for span in line.get('spans', []):
                        text += span.get('text', '')

                text = text.strip()

                # Check if it's page number
                if 'página' in text.lower() or ('de' in text.lower() and any(c.isdigit() for c in text)):
                    metadata["page_number_text"] = text
                # Check if it's footer info
                elif len(text) > 10:
                    metadata["footer_text"] = text

    return metadata


def filter_garbage(blocks):
    """
    Remove garbage content (metadata, page numbers, headers, footers).
    Same as in batch_extract_clean.py
    """
    clean_blocks = []

    for block in blocks:
        # Skip metadata blocks
        if block.type == "metadata":
            continue

        # Skip very short text blocks (likely garbage)
        if block.type == "text":
            content_text = block.content.get("text", "")
            if len(content_text.strip()) < 15:
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


def extract_with_metadata(pdf_path: str, start_page: int, end_page: int, output_dir: str = "outputs"):
    """
    Extract clean content AND metadata from PDF pages.

    Args:
        pdf_path: Path to PDF file
        start_page: Starting page (1-indexed)
        end_page: Ending page (1-indexed)
        output_dir: Output directory
    """
    pdf_path = Path(pdf_path)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    print(f"\n📄 Extracting pages {start_page}-{end_page} WITH METADATA from {pdf_path.name}")

    # Open PDF
    pdf_doc = fitz.open(str(pdf_path))
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
            "garbage_filtered": True,
            "metadata_extracted": True
        }
    }

    total_blocks_raw = 0
    total_blocks_clean = 0

    for page_num in range(start_page, end_page + 1):
        # Extract page metadata (page numbers, footers)
        page_metadata = extract_page_metadata(pdf_doc, page_num)

        # Classify page content
        blocks = classifier.classify_page(page_num)
        total_blocks_raw += len(blocks)

        # Filter garbage
        clean_blocks = filter_garbage(blocks)
        total_blocks_clean += len(clean_blocks)

        # Convert to dict
        results["pages"][page_num] = {
            "page_number": page_num,
            "metadata": page_metadata,  # ADD METADATA HERE
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
    output_file = output_path / f"{pdf_name}_pages_{start_page}_to_{end_page}_WITH_METADATA.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    pdf_doc.close()
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

    # Show sample metadata
    print(f"\n📋 Sample metadata from page {start_page}:")
    sample_meta = results["pages"][start_page]["metadata"]
    for key, value in sample_meta.items():
        if value:
            print(f"   • {key}: {value}")

    return output_file


def batch_extract_with_metadata(pdf_path: str, batch_size: int = 50, output_dir: str = "outputs"):
    """
    Extract content WITH metadata from entire PDF in batches.
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
    print(f"📋 BATCH EXTRACTION WITH METADATA")
    print("=" * 80)
    print(f"File: {pdf_path.name}")
    print(f"Total pages: {total_pages}")
    print(f"Batch size: {batch_size} pages")
    print(f"Output directory: {output_dir}")
    print(f"🗑️  Garbage filtering: ENABLED")
    print(f"📋 Metadata extraction: ENABLED")
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

    for i, (start_page, end_page) in enumerate(batches, 1):
        print(f"\n🔄 Processing Batch {i}/{len(batches)}")
        print("-" * 80)

        try:
            output_file = extract_with_metadata(
                str(pdf_path),
                start_page=start_page,
                end_page=end_page,
                output_dir=output_dir
            )
            output_files.append(output_file)

        except Exception as e:
            print(f"❌ Error processing batch {i}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue

    print("\n" + "=" * 80)
    print("🎉 EXTRACTION WITH METADATA COMPLETED")
    print("=" * 80)
    print(f"📦 Generated {len(output_files)} JSON files with metadata")

    if output_files:
        total_size = sum(f.stat().st_size for f in output_files) / (1024 * 1024)
        print(f"💾 Total size: {total_size:.2f} MB")
        print(f"📂 Location: {Path(output_dir).absolute()}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
📋 Extract PDF Content WITH Metadata - Includes page numbers and footer info

Usage:
    python extract_with_metadata.py <pdf_path> [batch_size]

Examples:
    # Extract all pages in 50-page batches (default)
    python extract_with_metadata.py document.pdf

    # Extract all pages in 100-page batches
    python extract_with_metadata.py document.pdf 100

Features:
    ✨ Extracts clean content (garbage filtered)
    ✨ Preserves page metadata (page numbers, footers)
    ✨ JSON output with metadata embedded in each page
        """)
        exit(1)

    pdf_path = sys.argv[1]
    batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    output_dir = Path(__file__).parent / "outputs"

    batch_extract_with_metadata(pdf_path, batch_size, str(output_dir))
