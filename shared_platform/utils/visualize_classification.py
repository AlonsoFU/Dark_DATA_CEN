"""
Visual Classification Tool
===========================

Creates visual output with bounding boxes showing how content is classified.

Usage:
    python visualize_classification.py /path/to/document.pdf [page_number]

Output:
    - PNG image with colored bounding boxes for each content type
    - Legend showing what each color represents
"""

import sys
import fitz  # PyMuPDF
from pathlib import Path
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

# Color names for legend
COLOR_NAMES = {
    ContentType.TEXT.value: "Blue",
    ContentType.TABLE.value: "Green",
    ContentType.FORMULA.value: "Magenta",
    ContentType.IMAGE.value: "Orange",
    ContentType.HEADING.value: "Red",
    ContentType.LIST.value: "Cyan",
    ContentType.UNKNOWN.value: "Gray"
}

# Icons for legend
ICONS = {
    ContentType.TEXT.value: "📝",
    ContentType.TABLE.value: "📊",
    ContentType.FORMULA.value: "🔢",
    ContentType.IMAGE.value: "🖼️",
    ContentType.HEADING.value: "📌",
    ContentType.LIST.value: "📋",
    ContentType.UNKNOWN.value: "❓"
}


def visualize_classification(pdf_path: str, page_num: int, output_dir: str = "outputs"):
    """
    Create visualization of classified content with bounding boxes.

    Args:
        pdf_path: Path to PDF file
        page_num: Page number to visualize (1-indexed)
        output_dir: Output directory for images
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    print(f"🎨 Visualizing classification for: {pdf_path}")
    print(f"📄 Page: {page_num}")
    print("=" * 80)

    # Classify content
    with ContentClassifier(pdf_path) as classifier:
        blocks = classifier.classify_page(page_num)

    # Open PDF for rendering
    pdf_doc = fitz.open(pdf_path)
    page = pdf_doc[page_num - 1]

    # Render page as pixmap (image)
    mat = fitz.Matrix(2, 2)  # 2x zoom for better quality
    pix = page.get_pixmap(matrix=mat)

    # Convert to PIL Image for drawing
    import io
    from PIL import Image, ImageDraw, ImageFont

    img = Image.open(io.BytesIO(pix.tobytes()))
    draw = ImageDraw.Draw(img, 'RGBA')

    # Statistics
    stats = {ct.value: 0 for ct in ContentType}

    # Draw bounding boxes for each block
    for i, block in enumerate(blocks, 1):
        stats[block.type] += 1

        # Get bbox coordinates (scaled by matrix)
        x0, y0, x1, y1 = block.bbox
        x0, y0, x1, y1 = x0 * 2, y0 * 2, x1 * 2, y1 * 2

        # Get color for this content type
        color = COLORS.get(block.type, (128, 128, 128))

        # Draw semi-transparent filled rectangle
        fill_color = color + (40,)  # Add alpha channel (40 = ~16% opacity)
        draw.rectangle([x0, y0, x1, y1], fill=fill_color)

        # Draw border
        border_color = color + (200,)  # More opaque border
        draw.rectangle([x0, y0, x1, y1], outline=border_color, width=3)

        # Draw label with content type name (full, not abbreviated)
        type_name = block.type.upper()
        confidence_label = f"{block.confidence:.2f}"

        # Calculate label size based on text
        label_width = max(120, len(type_name) * 10)

        # Draw label background (larger, at top of bbox)
        label_bg = [x0, y0 - 35, x0 + label_width, y0]
        draw.rectangle(label_bg, fill=color + (240,))

        # Draw text (try to load font, fallback to default)
        try:
            type_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
            conf_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            type_font = ImageFont.load_default()
            conf_font = ImageFont.load_default()

        # Draw content type name prominently
        draw.text((x0 + 8, y0 - 32), type_name, fill=(255, 255, 255), font=type_font)
        # Draw confidence below
        draw.text((x0 + 8, y0 - 14), f"#{i} conf:{confidence_label}", fill=(255, 255, 255), font=conf_font)

        # Print block info
        print(f"Block {i:2d} | {block.type.upper():8s} | Conf: {block.confidence:.2f} | BBox: ({x0/2:.0f},{y0/2:.0f},{x1/2:.0f},{y1/2:.0f})")

    # Draw legend
    legend_height = len([c for c in stats.values() if c > 0]) * 35 + 60
    legend_width = 250
    legend_x = img.width - legend_width - 20
    legend_y = 20

    # Legend background
    draw.rectangle(
        [legend_x, legend_y, legend_x + legend_width, legend_y + legend_height],
        fill=(255, 255, 255, 230),
        outline=(0, 0, 0, 255),
        width=2
    )

    # Legend title
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        legend_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        title_font = ImageFont.load_default()
        legend_font = ImageFont.load_default()

    draw.text((legend_x + 10, legend_y + 10), "Classification Legend", fill=(0, 0, 0), font=title_font)

    # Legend entries
    y_offset = legend_y + 45
    for content_type, count in stats.items():
        if count > 0:
            color = COLORS.get(content_type, (128, 128, 128))
            icon = ICONS.get(content_type, "")
            color_name = COLOR_NAMES.get(content_type, "Unknown")

            # Color box
            draw.rectangle(
                [legend_x + 10, y_offset, legend_x + 30, y_offset + 20],
                fill=color,
                outline=(0, 0, 0),
                width=1
            )

            # Text
            text = f"{icon} {content_type.upper()}: {count}"
            draw.text((legend_x + 40, y_offset + 2), text, fill=(0, 0, 0), font=legend_font)

            y_offset += 30

    # Total blocks
    total_text = f"Total: {len(blocks)} blocks"
    draw.text((legend_x + 10, y_offset), total_text, fill=(0, 0, 0), font=legend_font)

    # Save image
    pdf_name = Path(pdf_path).stem
    output_file = output_path / f"{pdf_name}_page_{page_num}_classification.png"
    img.save(output_file, "PNG")

    print("\n" + "=" * 80)
    print("📊 SUMMARY:")
    print("=" * 80)
    for content_type, count in stats.items():
        if count > 0:
            icon = ICONS.get(content_type, "")
            print(f"{icon} {content_type.upper()}: {count}")

    print(f"\n💾 Visualization saved to: {output_file}")
    print(f"🖼️  Image size: {img.width}x{img.height} pixels")

    # Also create a side-by-side comparison (original + classified)
    create_comparison_view(pdf_path, page_num, blocks, output_path)

    pdf_doc.close()


def create_comparison_view(pdf_path: str, page_num: int, blocks, output_path: Path):
    """Create side-by-side comparison of original and classified."""
    from PIL import Image, ImageDraw, ImageFont
    import io

    pdf_doc = fitz.open(pdf_path)
    page = pdf_doc[page_num - 1]

    # Render original page
    mat = fitz.Matrix(2, 2)
    pix = page.get_pixmap(matrix=mat)
    original_img = Image.open(io.BytesIO(pix.tobytes()))

    # Create classified version (just boxes, no fill)
    classified_img = original_img.copy()
    draw = ImageDraw.Draw(classified_img)

    for i, block in enumerate(blocks, 1):
        x0, y0, x1, y1 = block.bbox
        x0, y0, x1, y1 = x0 * 2, y0 * 2, x1 * 2, y1 * 2

        color = COLORS.get(block.type, (128, 128, 128))

        # Draw thick border only
        draw.rectangle([x0, y0, x1, y1], outline=color, width=4)

        # Draw content type label
        type_name = block.type.upper()
        try:
            type_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        except:
            type_font = ImageFont.load_default()

        # Calculate label width
        label_width = max(100, len(type_name) * 11)

        # Label background with content type
        draw.rectangle([x0, y0, x0 + label_width, y0 + 25], fill=color + (240,))
        draw.text((x0 + 5, y0 + 4), type_name, fill=(255, 255, 255), font=type_font)

    # Create side-by-side image
    total_width = original_img.width * 2 + 40
    total_height = original_img.height + 80

    comparison = Image.new('RGB', (total_width, total_height), (240, 240, 240))

    # Add title
    draw_comp = ImageDraw.Draw(comparison)
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        title_font = ImageFont.load_default()

    draw_comp.text((20, 20), "Original", fill=(0, 0, 0), font=title_font)
    draw_comp.text((original_img.width + 60, 20), "Classified", fill=(0, 0, 0), font=title_font)

    # Paste images
    comparison.paste(original_img, (20, 60))
    comparison.paste(classified_img, (original_img.width + 40, 60))

    # Save comparison
    pdf_name = Path(pdf_path).stem
    comparison_file = output_path / f"{pdf_name}_page_{page_num}_comparison.png"
    comparison.save(comparison_file, "PNG")

    print(f"🔍 Comparison saved to: {comparison_file}")

    pdf_doc.close()


def visualize_multiple_pages(pdf_path: str, start_page: int, end_page: int, output_dir: str = "outputs"):
    """Visualize multiple pages."""
    print(f"🎨 Visualizing pages {start_page}-{end_page}")
    print("=" * 80)

    for page_num in range(start_page, end_page + 1):
        print(f"\n📄 Processing page {page_num}...")
        visualize_classification(pdf_path, page_num, output_dir)
        print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python visualize_classification.py <pdf_path> [page_number] [--range start end]")
        print("\nExamples:")
        print("  python visualize_classification.py document.pdf 1")
        print("  python visualize_classification.py document.pdf --range 1 3")
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

    if "--range" in sys.argv:
        range_idx = sys.argv.index("--range")
        start_page = int(sys.argv[range_idx + 1])
        end_page = int(sys.argv[range_idx + 2])
        visualize_multiple_pages(pdf_path, start_page, end_page)
    elif len(sys.argv) >= 3:
        page_num = int(sys.argv[2])
        visualize_classification(pdf_path, page_num)
    else:
        visualize_classification(pdf_path, 1)