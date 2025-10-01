"""
Multi-Page PDF Classification Visualizer
=========================================

Creates a single multi-page PDF document showing classification for multiple pages.

Usage:
    python visualize_multi_page.py /path/to/document.pdf [start_page] [end_page]

Example:
    python visualize_multi_page.py document.pdf 1 20
"""

import sys
import fitz  # PyMuPDF
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io
from content_classifier import ContentClassifier, ContentType


# Color mapping for content types (RGB)
COLORS = {
    ContentType.TEXT.value: (0, 0, 255),        # Blue
    ContentType.TABLE.value: (0, 255, 0),       # Green
    ContentType.FORMULA.value: (255, 0, 255),   # Magenta
    ContentType.IMAGE.value: (255, 165, 0),     # Orange
    ContentType.HEADING.value: (255, 0, 0),     # Red
    ContentType.LIST.value: (0, 255, 255),      # Cyan
    ContentType.UNKNOWN.value: (128, 128, 128)  # Gray
}

ICONS = {
    ContentType.TEXT.value: "📝",
    ContentType.TABLE.value: "📊",
    ContentType.FORMULA.value: "🔢",
    ContentType.IMAGE.value: "🖼️",
    ContentType.HEADING.value: "📌",
    ContentType.LIST.value: "📋",
    ContentType.UNKNOWN.value: "❓"
}


def create_classified_page_image(pdf_doc, page_num: int, classifier: ContentClassifier):
    """Create a classified image for a single page."""

    # Classify content
    blocks = classifier.classify_page(page_num)

    # Render page
    page = pdf_doc[page_num - 1]
    mat = fitz.Matrix(2, 2)  # 2x zoom
    pix = page.get_pixmap(matrix=mat)

    # Convert to PIL Image
    img = Image.open(io.BytesIO(pix.tobytes()))
    draw = ImageDraw.Draw(img, 'RGBA')

    # Draw bounding boxes
    for i, block in enumerate(blocks, 1):
        x0, y0, x1, y1 = block.bbox
        x0, y0, x1, y1 = x0 * 2, y0 * 2, x1 * 2, y1 * 2

        color = COLORS.get(block.type, (128, 128, 128))

        # Semi-transparent fill
        fill_color = color + (40,)
        draw.rectangle([x0, y0, x1, y1], fill=fill_color)

        # Border
        border_color = color + (200,)
        draw.rectangle([x0, y0, x1, y1], outline=border_color, width=3)

        # Label
        type_name = block.type.upper()
        confidence_label = f"{block.confidence:.2f}"
        label_width = max(120, len(type_name) * 10)

        # Label background
        label_bg = [x0, y0 - 35, x0 + label_width, y0]
        draw.rectangle(label_bg, fill=color + (240,))

        # Text
        try:
            type_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
            conf_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            type_font = ImageFont.load_default()
            conf_font = ImageFont.load_default()

        draw.text((x0 + 8, y0 - 32), type_name, fill=(255, 255, 255), font=type_font)
        draw.text((x0 + 8, y0 - 14), f"#{i} conf:{confidence_label}", fill=(255, 255, 255), font=conf_font)

    # Add page number at top
    try:
        page_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        page_font = ImageFont.load_default()

    page_label = f"Page {page_num}"
    draw.rectangle([10, 10, 200, 50], fill=(0, 0, 0, 200))
    draw.text((20, 18), page_label, fill=(255, 255, 255), font=page_font)

    # Add statistics at bottom
    stats = {ct.value: 0 for ct in ContentType}
    for block in blocks:
        if block.type in stats:
            stats[block.type] += 1

    stats_text = " | ".join([f"{ICONS.get(ct, '')} {ct.upper()}:{count}"
                             for ct, count in stats.items() if count > 0])

    try:
        stats_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        stats_font = ImageFont.load_default()

    stats_bg = [10, img.height - 50, img.width - 10, img.height - 10]
    draw.rectangle(stats_bg, fill=(255, 255, 255, 230), outline=(0, 0, 0), width=2)
    draw.text((20, img.height - 42), stats_text, fill=(0, 0, 0), font=stats_font)

    return img, blocks


def create_multi_page_document(pdf_path: str, start_page: int, end_page: int, output_dir: str = "outputs"):
    """
    Create a multi-page PDF with classification visualization.

    Args:
        pdf_path: Path to input PDF
        start_page: Starting page number (1-indexed)
        end_page: Ending page number (1-indexed)
        output_dir: Output directory
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    print(f"🎨 Creating multi-page classification document")
    print(f"📄 Pages: {start_page} to {end_page}")
    print("=" * 80)

    # Open PDF and classifier
    pdf_doc = fitz.open(pdf_path)
    classifier = ContentClassifier(pdf_path)

    # Process all pages
    all_images = []
    total_stats = {ct.value: 0 for ct in ContentType}

    for page_num in range(start_page, min(end_page + 1, len(pdf_doc) + 1)):
        print(f"📄 Processing page {page_num}...")

        img, blocks = create_classified_page_image(pdf_doc, page_num, classifier)
        all_images.append(img)

        # Update statistics
        for block in blocks:
            if block.type in total_stats:
                total_stats[block.type] += 1

        # Print summary for this page
        page_stats = {ct.value: 0 for ct in ContentType}
        for block in blocks:
            if block.type in page_stats:
                page_stats[block.type] += 1

        stats_str = " | ".join([f"{ICONS.get(ct, '')}{count}"
                                for ct, count in page_stats.items() if count > 0])
        print(f"   ✅ {stats_str}")

    # Create multi-page PDF
    pdf_name = Path(pdf_path).stem
    output_file = output_path / f"{pdf_name}_pages_{start_page}_to_{end_page}_classified.pdf"

    if all_images:
        # Convert PIL images to PDF
        all_images[0].save(
            output_file,
            "PDF",
            resolution=100.0,
            save_all=True,
            append_images=all_images[1:]
        )

    print("\n" + "=" * 80)
    print("📊 TOTAL STATISTICS (All Pages):")
    print("=" * 80)
    for content_type, count in total_stats.items():
        if count > 0:
            icon = ICONS.get(content_type, "")
            print(f"{icon} {content_type.upper()}: {count}")

    print(f"\n💾 Multi-page PDF saved to: {output_file}")
    print(f"📄 Total pages: {len(all_images)}")

    # Also create a summary text file
    summary_file = output_path / f"{pdf_name}_pages_{start_page}_to_{end_page}_summary.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"Classification Summary: {pdf_name}\n")
        f.write(f"Pages: {start_page} to {end_page}\n")
        f.write("=" * 80 + "\n\n")

        f.write("TOTAL STATISTICS:\n")
        f.write("-" * 40 + "\n")
        for content_type, count in total_stats.items():
            if count > 0:
                icon = ICONS.get(content_type, "")
                f.write(f"{icon} {content_type.upper()}: {count}\n")

        f.write(f"\nTotal classified blocks: {sum(total_stats.values())}\n")

    print(f"📝 Summary saved to: {summary_file}")

    classifier.close()
    pdf_doc.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python visualize_multi_page.py <pdf_path> [start_page] [end_page]")
        print("\nExamples:")
        print("  python visualize_multi_page.py document.pdf 1 20")
        print("  python visualize_multi_page.py document.pdf 1 10")
        sys.exit(1)

    pdf_path = sys.argv[1]

    if not Path(pdf_path).exists():
        print(f"❌ PDF not found: {pdf_path}")
        sys.exit(1)

    # Check for PIL/Pillow
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("❌ Pillow not installed. Install with: pip install Pillow")
        sys.exit(1)

    start_page = int(sys.argv[2]) if len(sys.argv) >= 3 else 1
    end_page = int(sys.argv[3]) if len(sys.argv) >= 4 else start_page + 9  # Default 10 pages

    create_multi_page_document(pdf_path, start_page, end_page)