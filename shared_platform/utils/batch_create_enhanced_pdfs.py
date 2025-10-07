"""
Batch Create Enhanced PDFs - Generate PDFs with visual bounding boxes in batches
Creates PDF files showing classified content (text, tables, images, etc.) with colored boxes
"""

import sys
import fitz  # PyMuPDF
from pathlib import Path
from create_enhanced_pdf import create_multi_page_document


def batch_create_enhanced_pdfs(pdf_path: str, batch_size: int = 50, output_dir: str = "outputs"):
    """
    Create enhanced PDFs in batches with visual classification boxes.

    Args:
        pdf_path: Path to source PDF file
        batch_size: Number of pages per batch (default: 50)
        output_dir: Output directory for enhanced PDFs
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        print(f"❌ PDF not found: {pdf_path}")
        return

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Get page count
    pdf_doc = fitz.open(str(pdf_path))
    total_pages = len(pdf_doc)
    pdf_doc.close()

    print("=" * 80)
    print(f"📊 BATCH ENHANCED PDF CREATION")
    print("=" * 80)
    print(f"Source PDF: {pdf_path.name}")
    print(f"Total pages: {total_pages}")
    print(f"Batch size: {batch_size} pages")
    print(f"Output directory: {output_dir}")
    print("=" * 80)

    # Calculate batches
    batches = []
    for start_page in range(1, total_pages + 1, batch_size):
        end_page = min(start_page + batch_size - 1, total_pages)
        batches.append((start_page, end_page))

    print(f"\n📦 Will create {len(batches)} enhanced PDFs:")
    for i, (start, end) in enumerate(batches, 1):
        print(f"   Batch {i}: Pages {start}-{end} ({end - start + 1} pages)")

    print("\n" + "=" * 80)

    # Create each batch
    for i, (start_page, end_page) in enumerate(batches, 1):
        print(f"\n🔄 Processing Batch {i}/{len(batches)}")
        print("-" * 80)

        try:
            create_multi_page_document(
                str(pdf_path),
                start_page=start_page,
                end_page=end_page,
                output_dir=output_dir
            )
        except Exception as e:
            print(f"❌ Error processing batch {i}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue

    print("\n" + "=" * 80)
    print("🎉 BATCH CREATION COMPLETED")
    print("=" * 80)
    print(f"📂 Location: {output_path.absolute()}")
    print("=" * 80)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
Usage:
    python batch_create_enhanced_pdfs.py <pdf_path> [batch_size] [output_dir]

Examples:
    # Create enhanced PDFs in 50-page batches (default)
    python batch_create_enhanced_pdfs.py document.pdf

    # Create enhanced PDFs in 100-page batches
    python batch_create_enhanced_pdfs.py document.pdf 100

    # Specify custom output directory
    python batch_create_enhanced_pdfs.py document.pdf 50 outputs/enhanced_pdfs
        """)
        sys.exit(1)

    pdf_path = sys.argv[1]
    batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "outputs"

    batch_create_enhanced_pdfs(pdf_path, batch_size, output_dir)
