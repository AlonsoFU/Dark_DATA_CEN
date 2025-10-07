"""
Batch Content Extraction - Extract structured data from PDFs in batches
Extracts text, tables, headings, etc. and saves to JSON files
"""

import sys
import json
import fitz  # PyMuPDF
from pathlib import Path
from datetime import datetime
from content_classifier import ContentClassifier


def extract_batch_to_json(pdf_path: str, start_page: int, end_page: int, output_dir: str = "outputs"):
    """
    Extract content from a page range and save to JSON.

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
    results = classifier.classify_document(start_page=start_page, end_page=end_page)

    # Add extraction metadata
    results["extraction_metadata"] = {
        "source_file": str(pdf_path),
        "page_range": f"{start_page}-{end_page}",
        "extraction_date": datetime.now().isoformat(),
        "total_blocks_extracted": sum(
            page_data["block_count"] for page_data in results["pages"].values()
        )
    }

    # Save to JSON
    pdf_name = pdf_path.stem
    output_file = output_path / f"{pdf_name}_pages_{start_page}_to_{end_page}_content.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    classifier.close()

    # Print summary
    print(f"✅ Extracted {results['extraction_metadata']['total_blocks_extracted']} content blocks")
    print(f"📊 Statistics:")
    for content_type, count in results["statistics"].items():
        if count > 0:
            print(f"   • {content_type}: {count}")

    file_size_kb = output_file.stat().st_size / 1024
    print(f"💾 Saved to: {output_file.name} ({file_size_kb:.1f} KB)")

    return output_file


def batch_extract_content(pdf_path: str, batch_size: int = 50, output_dir: str = "outputs"):
    """
    Extract content from PDF in batches and save to JSON files.

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
    print(f"📊 BATCH CONTENT EXTRACTION")
    print("=" * 80)
    print(f"File: {pdf_path.name}")
    print(f"Total pages: {total_pages}")
    print(f"Batch size: {batch_size} pages")
    print(f"Output directory: {output_dir}")
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
    total_blocks = 0

    for i, (start_page, end_page) in enumerate(batches, 1):
        print(f"\n🔄 Processing Batch {i}/{len(batches)}")
        print("-" * 80)

        try:
            output_file = extract_batch_to_json(
                str(pdf_path),
                start_page=start_page,
                end_page=end_page,
                output_dir=output_dir
            )
            output_files.append(output_file)

            # Read back to get block count
            with open(output_file, 'r') as f:
                data = json.load(f)
                total_blocks += data["extraction_metadata"]["total_blocks_extracted"]

        except Exception as e:
            print(f"❌ Error processing batch {i}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue

    print("\n" + "=" * 80)
    print("🎉 EXTRACTION COMPLETED")
    print("=" * 80)
    print(f"📦 Generated {len(output_files)} JSON files")
    print(f"📊 Total content blocks extracted: {total_blocks}")

    if output_files:
        total_size = sum(f.stat().st_size for f in output_files) / (1024 * 1024)
        print(f"💾 Total size: {total_size:.2f} MB")
        print(f"📂 Location: {Path(output_dir).absolute()}")


def merge_batch_jsons(pdf_path: str, output_dir: str = "outputs"):
    """
    Merge all batch JSON files into a single complete extraction.

    Args:
        pdf_path: Path to original PDF
        output_dir: Directory containing batch JSON files
    """
    pdf_path = Path(pdf_path)
    output_path = Path(output_dir)
    pdf_name = pdf_path.stem

    # Find all batch JSON files
    batch_files = sorted(output_path.glob(f"{pdf_name}_pages_*_content.json"))

    if not batch_files:
        print(f"❌ No batch JSON files found for {pdf_name}")
        return

    print("=" * 80)
    print(f"🔄 MERGING BATCH FILES")
    print("=" * 80)
    print(f"Found {len(batch_files)} batch files")

    # Merge data
    merged_data = {
        "document_path": str(pdf_path),
        "total_pages": 0,
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
            "extraction_date": datetime.now().isoformat(),
            "merged_from_batches": len(batch_files),
            "batch_files": [f.name for f in batch_files]
        }
    }

    total_blocks = 0

    for batch_file in batch_files:
        print(f"   • Merging {batch_file.name}")

        with open(batch_file, 'r') as f:
            batch_data = json.load(f)

        # Merge pages
        merged_data["pages"].update(batch_data["pages"])

        # Merge statistics
        for content_type, count in batch_data["statistics"].items():
            if content_type in merged_data["statistics"]:
                merged_data["statistics"][content_type] += count

        total_blocks += batch_data["extraction_metadata"]["total_blocks_extracted"]

    merged_data["total_pages"] = len(merged_data["pages"])
    merged_data["extraction_metadata"]["total_blocks_extracted"] = total_blocks

    # Save merged file
    output_file = output_path / f"{pdf_name}_complete_extraction.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)

    file_size_mb = output_file.stat().st_size / (1024 * 1024)

    print("\n" + "=" * 80)
    print("✅ MERGE COMPLETED")
    print("=" * 80)
    print(f"📄 Total pages: {merged_data['total_pages']}")
    print(f"📊 Total blocks: {total_blocks}")
    print(f"💾 Output: {output_file.name} ({file_size_mb:.2f} MB)")
    print("=" * 80)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
Usage:
    python batch_extract_content.py <pdf_path> [batch_size]
    python batch_extract_content.py <pdf_path> --merge

Examples:
    # Extract content in 50-page batches (default)
    python batch_extract_content.py document.pdf

    # Extract content in 100-page batches
    python batch_extract_content.py document.pdf 100

    # Merge all batch JSON files into single file
    python batch_extract_content.py document.pdf --merge
        """)
        exit(1)

    pdf_path = sys.argv[1]
    output_dir = Path(__file__).parent / "outputs"

    # Check for --merge flag
    if len(sys.argv) > 2 and sys.argv[2] == "--merge":
        merge_batch_jsons(pdf_path, str(output_dir))
    else:
        batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        batch_extract_content(pdf_path, batch_size, str(output_dir))
