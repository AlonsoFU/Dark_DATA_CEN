"""
Multi-Page PDF Content Classification Visualizer - CLEAN VERSION
Creates visualization with colored boxes but filters out garbage (metadata, page numbers, etc.)
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
    "paragraph": (0, 0, 255),   # Blue
    "table": (0, 255, 0),       # Green
    "formula": (255, 0, 255),   # Magenta
    "image": (255, 165, 0),     # Orange
    "heading": (255, 0, 0),     # Red
    "list": (0, 255, 255),      # Cyan
    "metadata": (128, 0, 128),  # Purple
    "unknown": (128, 128, 128)  # Gray
}

ICONS = {
    "text": "📝",
    "paragraph": "📝",
    "table": "📊",
    "formula": "🔢",
    "image": "🖼️",
    "heading": "📌",
    "list": "📋",
    "metadata": "ℹ️",
    "unknown": "❓"
}


def filter_garbage(blocks):
    """
    Remove garbage content (metadata, page numbers, headers, footers).
    KEEP METADATA BLOCKS for separate display.

    Returns:
        Tuple: (clean_content_blocks, metadata_blocks)
    """
    clean_blocks = []
    metadata_blocks = []

    for block in blocks:
        # Separate metadata blocks
        if block.type == "metadata":
            metadata_blocks.append(block)
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

    return clean_blocks, metadata_blocks


def merge_consecutive_texts(blocks):
    """
    Merge consecutive TEXT blocks into single large text blocks.
    Keeps headings, tables, and other types separate.

    Returns:
        List of merged blocks
    """
    if not blocks:
        return []

    merged = []
    current_text = None

    for block in blocks:
        if block.type == "text":
            if current_text is None:
                # Start new text accumulation
                current_text = block
            else:
                # Merge with previous text
                # Combine text content
                current_text.content["text"] += " " + block.content.get("text", "")

                # Expand bounding box to include both blocks
                x0 = min(current_text.bbox[0], block.bbox[0])
                y0 = min(current_text.bbox[1], block.bbox[1])
                x1 = max(current_text.bbox[2], block.bbox[2])
                y1 = max(current_text.bbox[3], block.bbox[3])
                current_text.bbox = (x0, y0, x1, y1)
        else:
            # Not a text block - save accumulated text (if any) and add this block
            if current_text is not None:
                merged.append(current_text)
                current_text = None
            merged.append(block)

    # Don't forget last accumulated text
    if current_text is not None:
        merged.append(current_text)

    return merged


def create_classified_page_image(pdf_doc, page_num: int, classifier: ContentClassifier):
    """Create a classified image for a single page with garbage filtering and text merging."""

    # Classify content with universal detector
    blocks = classifier.classify_page(page_num)

    # FILTER GARBAGE and SEPARATE METADATA
    blocks_before = len(blocks)
    blocks, metadata_blocks = filter_garbage(blocks)
    garbage_removed = blocks_before - len(blocks) - len(metadata_blocks)

    # MERGE CONSECUTIVE TEXT BLOCKS
    blocks = merge_consecutive_texts(blocks)

    blocks_after = len(blocks)

    # Render page
    page = pdf_doc[page_num - 1]
    mat = fitz.Matrix(2, 2)  # 2x zoom
    pix = page.get_pixmap(matrix=mat)

    # Convert to PIL Image
    img = Image.open(io.BytesIO(pix.tobytes()))
    draw = ImageDraw.Draw(img, 'RGBA')

    # Draw bounding boxes for CONTENT blocks
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

    # Draw METADATA boxes (purple color, at bottom of page)
    for i, meta_block in enumerate(metadata_blocks, 1):
        x0, y0, x1, y1 = meta_block.bbox
        x0, y0, x1, y1 = x0 * 2, y0 * 2, x1 * 2, y1 * 2

        # Purple color for metadata
        meta_color = (128, 0, 128)  # Purple

        # Semi-transparent fill
        fill_color = meta_color + (60,)
        draw.rectangle([x0, y0, x1, y1], fill=fill_color)

        # Border
        border_color = meta_color + (200,)
        draw.rectangle([x0, y0, x1, y1], outline=border_color, width=3)

        # Label
        try:
            meta_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        except:
            meta_font = ImageFont.load_default()

        # Label background
        label_bg = [x0, y0 - 30, x0 + 140, y0]
        draw.rectangle(label_bg, fill=meta_color + (240,))
        draw.text((x0 + 8, y0 - 26), "METADATA", fill=(255, 255, 255), font=meta_font)

    # Add page number at top
    try:
        page_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        page_font = ImageFont.load_default()

    page_label = f"Page {page_num} [CLEAN - {garbage_removed} garbage removed]"
    draw.rectangle([10, 10, 600, 50], fill=(0, 128, 0, 200))
    draw.text((20, 18), page_label, fill=(255, 255, 255), font=page_font)

    # Add statistics at bottom
    stats = {}
    for block in blocks:
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

    return img, blocks, garbage_removed


def create_multi_page_document(pdf_path: str, start_page: int, end_page: int, output_dir: str = "outputs"):
    """
    Create a multi-page PDF with CLEAN classification visualization.
    Garbage (metadata, page numbers, headers) is filtered out.
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    print(f"🎨 Creating multi-page CLEAN classification document")
    print(f"📄 Pages: {start_page} to {end_page}")
    print(f"✅ Using PyMuPDF for accurate table detection")
    print(f"🗑️  Garbage filtering: ENABLED")
    print("=" * 80)

    # Open PDF and create classifier
    pdf_doc = fitz.open(pdf_path)
    classifier = ContentClassifier(pdf_path)

    # Process all pages
    all_images = []
    total_stats = {}
    total_garbage = 0
    total_blocks_raw = 0
    total_blocks_clean = 0

    for page_num in range(start_page, min(end_page + 1, len(pdf_doc) + 1)):
        print(f"📄 Processing page {page_num}...", end=" ")

        img, blocks, garbage_removed = create_classified_page_image(pdf_doc, page_num, classifier)
        all_images.append(img)

        total_garbage += garbage_removed
        total_blocks_raw += len(blocks) + garbage_removed
        total_blocks_clean += len(blocks)

        # Update total stats
        for block in blocks:
            block_type = block.type
            total_stats[block_type] = total_stats.get(block_type, 0) + 1

        print(f"✅ {len(blocks)} clean blocks ({garbage_removed} garbage removed)")

    # Create output PDF
    pdf_name = Path(pdf_path).stem
    output_pdf = output_path / f"{pdf_name}_pages_{start_page}_to_{end_page}_CLEAN.pdf"

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

    garbage_percent = (total_garbage / total_blocks_raw * 100) if total_blocks_raw > 0 else 0

    print("\n" + "=" * 80)
    print("📊 TOTAL STATISTICS (all pages)")
    print("=" * 80)
    print(f"📦 Total blocks (raw): {total_blocks_raw}")
    print(f"🗑️  Garbage removed: {total_garbage} ({garbage_percent:.1f}%)")
    print(f"✨ Clean blocks: {total_blocks_clean}")
    print("\n📊 CLEAN CONTENT BREAKDOWN:")

    for content_type, count in sorted(total_stats.items()):
        icon = ICONS.get(content_type, "")
        print(f"{icon} {content_type.upper()}: {count}")

    print("\n" + "=" * 80)
    print(f"✅ Output: {output_pdf}")
    print(f"📦 Size: {output_pdf.stat().st_size / 1024 / 1024:.2f} MB")
    print("=" * 80)


if __name__ == "__main__":
    # Parse command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python create_enhanced_pdf_clean.py <pdf_path> [start_page] [end_page]")
        exit(1)

    pdf_path = Path(sys.argv[1])
    start_page = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    end_page = int(sys.argv[3]) if len(sys.argv) > 3 else 15

    if not pdf_path.exists():
        print(f"❌ PDF not found: {pdf_path}")
        exit(1)

    output_dir = Path(__file__).parent / "outputs"

    # Create enhanced clean visualization
    create_multi_page_document(
        str(pdf_path),
        start_page=start_page,
        end_page=end_page,
        output_dir=str(output_dir)
    )
