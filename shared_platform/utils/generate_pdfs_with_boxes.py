#!/usr/bin/env python3
"""
Genera PDFs con boxes visualizados cada 50 páginas
"""
import fitz
from pathlib import Path


def draw_boxes_on_pdf(input_pdf: Path, output_pdf: Path, start_page: int, end_page: int):
    """
    Dibuja rectangulos alrededor de cada text block en el PDF.

    Args:
        input_pdf: PDF fuente
        output_pdf: PDF de salida con boxes
        start_page: Página inicial (1-indexed)
        end_page: Página final (1-indexed, inclusive)
    """
    with fitz.open(input_pdf) as doc:
        # Crear nuevo PDF solo con las páginas seleccionadas
        output_doc = fitz.open()

        for page_num in range(start_page - 1, end_page):
            if page_num >= len(doc):
                break

            page = doc[page_num]

            # Copiar la página al documento de salida
            output_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
            output_page = output_doc[-1]

            # Obtener todos los text blocks
            blocks = page.get_text('dict')['blocks']

            # Dibujar rectángulo alrededor de cada text block
            for block in blocks:
                if block.get('type') != 0:  # Solo text blocks
                    continue

                bbox = block.get('bbox')
                if not bbox:
                    continue

                # Crear rectángulo
                rect = fitz.Rect(bbox)

                # Dibujar borde rojo alrededor del block
                output_page.draw_rect(
                    rect,
                    color=(1, 0, 0),  # Rojo
                    width=0.5
                )

        # Guardar el PDF de salida
        output_doc.save(output_pdf)
        output_doc.close()

        print(f"✅ Generado: {output_pdf.name} (páginas {start_page}-{end_page})")


if __name__ == "__main__":
    # PDF fuente
    input_pdf = Path("../../domains/operaciones/eaf/shared/source/EAF-089-2025.pdf")
    output_dir = Path("outputs")

    if not input_pdf.exists():
        print(f"❌ Error: No se encuentra {input_pdf}")
        exit(1)

    # Obtener total de páginas
    with fitz.open(input_pdf) as doc:
        total_pages = len(doc)

    print("="*80)
    print("GENERANDO PDFs CON BOXES VISUALIZADOS")
    print("="*80)
    print(f"PDF fuente: {input_pdf.name}")
    print(f"Total páginas: {total_pages}")
    print(f"Dividiendo cada 50 páginas...")
    print()

    # Generar PDFs cada 50 páginas
    page_increment = 50

    for start in range(1, total_pages + 1, page_increment):
        end = min(start + page_increment - 1, total_pages)

        output_filename = f"EAF-089-2025_pages_{start}_to_{end}_ENHANCED.pdf"
        output_path = output_dir / output_filename

        draw_boxes_on_pdf(input_pdf, output_path, start, end)

    print()
    print("="*80)
    print(f"✅ Completado! {(total_pages // page_increment) + 1} archivos PDF generados")
    print("="*80)
