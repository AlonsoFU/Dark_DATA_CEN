"""
Multi-Page PDF Content Classification Visualizer
Creates visualization showing detected content types (tables, headings, paragraphs, etc.)
General-purpose tool that works with any PDF.
"""

import sys
import fitz  # PyMuPDF
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io

# Use the universal ContentClassifier from shared_platform/utils
from content_classifier import ContentClassifier, ContentType


# Color mapping for content types (RGB)
COLORS = {
    "text": (0, 0, 255),        # Blue
    "table": (0, 255, 0),       # Green
    "formula": (255, 0, 255),   # Magenta
    "image": (255, 165, 0),     # Orange
    "metadata": (128, 0, 128),  # Purple
}

ICONS = {
    "text": "📝",
    "table": "📊",
    "formula": "🔢",
    "image": "🖼️",
    "metadata": "ℹ️",
}


def create_classified_page_image(pdf_doc, page_num: int, classifier: ContentClassifier):
    """Create a classified image for a single page."""

    # Classify content with universal detector
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

        # block.type is already a string in ContentClassifier
        block_type = block.type
        color = COLORS.get(block_type, (128, 128, 128))

        # Semi-transparent fill
        fill_color = color + (40,)
        draw.rectangle([x0, y0, x1, y1], fill=fill_color)

        # Border
        border_color = color + (200,)
        draw.rectangle([x0, y0, x1, y1], outline=border_color, width=3)

        # Label
        type_name = block_type.upper()
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

    page_label = f"Page {page_num} [ENHANCED MULTI-LINE]"
    draw.rectangle([10, 10, 400, 50], fill=(0, 128, 0, 200))
    draw.text((20, 18), page_label, fill=(255, 255, 255), font=page_font)

    # Add statistics at bottom
    stats = {}
    for block in blocks:
        # block.type is already a string in ContentClassifier
        block_type = block.type
        stats[block_type] = stats.get(block_type, 0) + 1

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
    Create a multi-page PDF with ENHANCED classification visualization.
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    print(f"🎨 Creating multi-page classification document")
    print(f"📄 Pages: {start_page} to {end_page}")
    print(f"✅ Using PyMuPDF for accurate table detection")
    print("=" * 80)

    # Open PDF and create classifier
    pdf_doc = fitz.open(pdf_path)
    classifier = ContentClassifier(pdf_path)

    # Process all pages
    all_images = []
    total_stats = {}

    for page_num in range(start_page, min(end_page + 1, len(pdf_doc) + 1)):
        print(f"📄 Processing page {page_num}...", end=" ")

        img, blocks = create_classified_page_image(pdf_doc, page_num, classifier)
        all_images.append(img)

        # Update total stats
        for block in blocks:
            # block.type is already a string in ContentClassifier
            block_type = block.type
            total_stats[block_type] = total_stats.get(block_type, 0) + 1

        print(f"✅ {len(blocks)} blocks")

    # Create output PDF
    pdf_name = Path(pdf_path).stem
    output_pdf = output_path / f"{pdf_name}_pages_{start_page}_to_{end_page}_ENHANCED.pdf"

    print(f"\n💾 Saving to: {output_pdf.name}")

    if all_images:
        all_images[0].save(
            output_pdf,
            "PDF",
            resolution=100.0,
            save_all=True,
            append_images=all_images[1:]
        )

    pdf_doc.close()

    print("\n" + "=" * 80)
    print("📊 TOTAL STATISTICS (all pages)")
    print("=" * 80)

    for content_type, count in sorted(total_stats.items()):
        icon = ICONS.get(content_type, "")
        print(f"{icon} {content_type.upper()}: {count}")

    print("\n" + "=" * 80)
    print(f"✅ Output: {output_pdf}")
    print(f"📦 Size: {output_pdf.stat().st_size / 1024:.1f} KB")
    print("=" * 80)


if __name__ == "__main__":
    # Parse command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python create_enhanced_pdf.py <pdf_path> [start_page] [end_page]")
        exit(1)

    pdf_path = Path(sys.argv[1])
    start_page = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    end_page = int(sys.argv[3]) if len(sys.argv) > 3 else 15

    if not pdf_path.exists():
        print(f"❌ PDF not found: {pdf_path}")
        exit(1)

    output_dir = Path(__file__).parent / "outputs"

    # Create enhanced visualization
    create_multi_page_document(
        str(pdf_path),
        start_page=start_page,
        end_page=end_page,
        output_dir=str(output_dir)
    )
