"""
Visualize Enhanced Detection with Multi-line Cells
Creates a PDF showing detected content with boxes highlighting cDoubleLinea
"""

import sys
import fitz
from pathlib import Path

# Add processors to path
processors_path = Path(__file__).parent.parent.parent / "domains" / "operaciones" / "eaf" / \
                  "chapters" / "capitulo_01_descripcion_perturbacion" / "processors"
sys.path.insert(0, str(processors_path))

from smart_content_classifier import SmartContentClassifier, ContentType
from enhanced_table_detector import patch_smart_classifier


def visualize_enhanced_detection(pdf_path: Path, output_path: Path, max_pages: int = 15):
    """
    Creates a PDF with boxes showing detected content using enhanced detector.

    Args:
        pdf_path: Source PDF path
        output_path: Output PDF path
        max_pages: Maximum pages to process
    """

    print("🎨 VISUALIZANDO DETECCIÓN MEJORADA CON CELDAS MULTI-LÍNEA")
    print("=" * 70)
    print(f"📄 PDF: {pdf_path.name}")
    print(f"📊 Páginas: {max_pages}")
    print("=" * 70)

    # Create enhanced classifier
    classifier = SmartContentClassifier(str(pdf_path))
    patch_smart_classifier(classifier)  # 🔧 Apply enhanced detection

    # Open PDFs
    src_doc = fitz.open(pdf_path)
    out_doc = fitz.open()

    # Colors for different content types
    colors = {
        ContentType.TABLE: (0, 0.5, 0),      # Dark green
        ContentType.HEADING: (0.8, 0, 0),    # Dark red
        ContentType.PARAGRAPH: (0, 0, 0.8),  # Dark blue
        ContentType.LIST: (0.8, 0.5, 0),     # Orange
        ContentType.IMAGE: (0.5, 0, 0.5),    # Purple
    }

    labels = {
        ContentType.TABLE: "📊 TABLA (multi-línea)",
        ContentType.HEADING: "📌 ENCABEZADO",
        ContentType.PARAGRAPH: "📝 PÁRRAFO",
        ContentType.LIST: "📋 LISTA",
        ContentType.IMAGE: "🖼️ IMAGEN",
    }

    pages_to_process = min(max_pages, len(src_doc))

    for page_num in range(1, pages_to_process + 1):
        print(f"📄 Procesando página {page_num}...", end=" ")

        # Get page
        page = src_doc[page_num - 1]

        # Classify content with enhanced detector
        blocks = classifier.classify_page_content(page_num)

        # Count by type
        counts = {}
        for block in blocks:
            type_name = block.type.value
            counts[type_name] = counts.get(type_name, 0) + 1

        # Draw boxes on page
        for block in blocks:
            if block.type in colors:
                color = colors[block.type]
                label = labels[block.type]

                # Draw rectangle
                rect = fitz.Rect(block.bbox)
                page.draw_rect(rect, color=color, width=2)

                # Add label at top-left corner
                label_rect = fitz.Rect(
                    block.bbox[0],
                    block.bbox[1] - 15,
                    block.bbox[0] + 150,
                    block.bbox[1]
                )
                page.draw_rect(label_rect, color=color, fill=color, width=0)
                page.insert_text(
                    (block.bbox[0] + 2, block.bbox[1] - 3),
                    label,
                    fontsize=8,
                    color=(1, 1, 1)
                )

        # Add page to output
        out_doc.insert_pdf(src_doc, from_page=page_num - 1, to_page=page_num - 1)

        # Show stats
        stats = " | ".join([f"{k}:{v}" for k, v in counts.items()])
        print(f"✅ {stats}")

    # Save output
    out_doc.save(output_path)
    out_doc.close()
    src_doc.close()

    print("\n" + "=" * 70)
    print(f"💾 Guardado en: {output_path.name}")
    print(f"📦 Tamaño: {output_path.stat().st_size / 1024:.1f} KB")
    print("=" * 70)

    print("\n✨ ¡Las tablas ahora incluyen celdas multi-línea (cDoubleLinea)!")


if __name__ == "__main__":
    # Paths
    pdf_source = Path(__file__).parent.parent.parent / "domains" / "operaciones" / "eaf" / \
                 "shared" / "source" / "EAF-089-2025.pdf"

    pdf_output = Path(__file__).parent / "outputs" / "EAF-089-2025_pages_1_to_15_enhanced_boxes.pdf"
    pdf_output.parent.mkdir(parents=True, exist_ok=True)

    if not pdf_source.exists():
        print(f"❌ PDF no encontrado: {pdf_source}")
        exit(1)

    # Visualize with enhanced detection
    visualize_enhanced_detection(pdf_source, pdf_output, max_pages=15)
