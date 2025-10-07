"""
Batch PDF Content Extraction - Process PDFs in 50-page chunks
Automatically divides large PDFs and creates enhanced visualization outputs
"""

import sys
import fitz  # PyMuPDF
from pathlib import Path
from create_enhanced_pdf import create_multi_page_document


def batch_process_pdf(pdf_path: str, batch_size: int = 50, output_dir: str = "outputs"):
    """
    Process a PDF in batches of N pages.

    Args:
        pdf_path: Path to the PDF file
        batch_size: Number of pages per batch (default: 50)
        output_dir: Output directory for results
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        print(f"❌ PDF not found: {pdf_path}")
        return

    # Open PDF to get page count
    pdf_doc = fitz.open(str(pdf_path))
    total_pages = len(pdf_doc)
    pdf_doc.close()

    print("=" * 80)
    print(f"📄 PDF BATCH PROCESSOR")
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

    print(f"\n📊 Processing {len(batches)} batches:")
    for i, (start, end) in enumerate(batches, 1):
        print(f"   Batch {i}: Pages {start}-{end} ({end - start + 1} pages)")

    print("\n" + "=" * 80)

    # Process each batch
    for i, (start_page, end_page) in enumerate(batches, 1):
        print(f"\n🔄 Processing Batch {i}/{len(batches)}: Pages {start_page}-{end_page}")
        print("-" * 80)

        try:
            create_multi_page_document(
                str(pdf_path),
                start_page=start_page,
                end_page=end_page,
                output_dir=output_dir
            )
            print(f"✅ Batch {i} completed successfully")
        except Exception as e:
            print(f"❌ Error processing batch {i}: {str(e)}")
            continue

    print("\n" + "=" * 80)
    print("🎉 ALL BATCHES COMPLETED")
    print("=" * 80)

    # List output files
    output_path = Path(output_dir)
    pdf_name = pdf_path.stem
    output_files = sorted(output_path.glob(f"{pdf_name}_pages_*_ENHANCED.pdf"))

    if output_files:
        print(f"\n📦 Generated {len(output_files)} output files:")
        total_size = 0
        for file in output_files:
            size_mb = file.stat().st_size / (1024 * 1024)
            total_size += size_mb
            print(f"   • {file.name} ({size_mb:.2f} MB)")

        print(f"\n💾 Total size: {total_size:.2f} MB")
        print(f"📂 Location: {output_path.absolute()}")


def list_existing_outputs(pdf_path: str, output_dir: str = "outputs"):
    """List existing output files for a PDF."""
    pdf_path = Path(pdf_path)
    output_path = Path(output_dir)
    pdf_name = pdf_path.stem

    if not output_path.exists():
        print(f"❌ Output directory not found: {output_dir}")
        return

    output_files = sorted(output_path.glob(f"{pdf_name}_pages_*_ENHANCED.pdf"))

    if not output_files:
        print(f"No existing outputs found for {pdf_name}")
        return

    print("=" * 80)
    print(f"📦 EXISTING OUTPUTS FOR: {pdf_name}")
    print("=" * 80)

    total_size = 0
    for i, file in enumerate(output_files, 1):
        size_mb = file.stat().st_size / (1024 * 1024)
        total_size += size_mb
        # Extract page range from filename
        print(f"{i}. {file.name} ({size_mb:.2f} MB)")

    print("-" * 80)
    print(f"Total files: {len(output_files)}")
    print(f"Total size: {total_size:.2f} MB")
    print("=" * 80)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
Usage:
    python batch_process_pdf.py <pdf_path> [batch_size]
    python batch_process_pdf.py <pdf_path> --list

Examples:
    # Process PDF in 50-page batches (default)
    python batch_process_pdf.py document.pdf

    # Process PDF in 100-page batches
    python batch_process_pdf.py document.pdf 100

    # List existing outputs
    python batch_process_pdf.py document.pdf --list
        """)
        exit(1)

    pdf_path = sys.argv[1]

    # Check for --list flag
    if len(sys.argv) > 2 and sys.argv[2] == "--list":
        output_dir = Path(__file__).parent / "outputs"
        list_existing_outputs(pdf_path, str(output_dir))
    else:
        batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        output_dir = Path(__file__).parent / "outputs"
        batch_process_pdf(pdf_path, batch_size, str(output_dir))
