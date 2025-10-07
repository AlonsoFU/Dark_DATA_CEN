#!/usr/bin/env python3
"""
Figure Extractor - Detecta figuras/gráficos y sus títulos/captions

Detecta:
- Imágenes en el PDF
- Títulos de figuras (pueden estar arriba o abajo de la imagen)
- Patrones: "Figura X:", "Gráfico X:", "Imagen X:", etc.

Desafíos:
- El título puede estar antes o después de la imagen
- Necesitamos asociar cada título con su imagen correspondiente
"""
import fitz
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional


class FigureExtractor:
    """
    Extrae figuras/imágenes y sus títulos del PDF.

    Patrones de título:
    - Figura 1: Descripción
    - Gráfico 2: Descripción
    - Imagen 3: Descripción
    - Fig. 4: Descripción
    """

    def __init__(self):
        # Patrones para detectar títulos de figuras
        self.caption_patterns = [
            r'^Figura\s+(\d+)[:\.\-\s]+(.+)',
            r'^Fig\.\s+(\d+)[:\.\-\s]+(.+)',
            r'^Gráfico\s+(\d+)[:\.\-\s]+(.+)',
            r'^Imagen\s+(\d+)[:\.\-\s]+(.+)',
            r'^Diagrama\s+(\d+)[:\.\-\s]+(.+)',
            r'^Tabla\s+(\d+)[:\.\-\s]+(.+)',  # Tablas también pueden tener caption
        ]

    def detect_caption(self, text: str) -> Tuple[bool, Optional[str], Optional[int], Optional[str]]:
        """
        Detecta si un texto es un caption de figura.

        Returns:
            (is_caption, caption_type, number, description)
        """
        for pattern in self.caption_patterns:
            match = re.match(pattern, text.strip(), re.IGNORECASE)
            if match:
                number = int(match.group(1))
                description = match.group(2).strip()
                caption_type = pattern.split(r'\s+')[0].replace('^', '')  # Extraer tipo
                return True, caption_type, number, description

        return False, None, None, None

    def extract_images(
        self,
        pdf_path: Path,
        start_page: int,
        end_page: int
    ) -> List[Dict]:
        """
        Extrae todas las imágenes de un rango de páginas.

        Returns:
            Lista de imágenes con su ubicación y metadatos
        """
        images = []

        with fitz.open(pdf_path) as doc:
            for page_num in range(start_page - 1, end_page):
                page = doc[page_num]

                # Obtener lista de imágenes en la página
                image_list = page.get_images(full=True)

                for img_index, img in enumerate(image_list):
                    xref = img[0]  # XREF del objeto imagen

                    # Obtener información de la imagen
                    try:
                        base_image = doc.extract_image(xref)
                        image_bbox = page.get_image_bbox(img)

                        image_info = {
                            'page': page_num + 1,
                            'xref': xref,
                            'bbox': [image_bbox.x0, image_bbox.y0, image_bbox.x1, image_bbox.y1],
                            'width': base_image.get('width', 0),
                            'height': base_image.get('height', 0),
                            'image_type': base_image.get('ext', 'unknown'),
                            'image_index': img_index
                        }

                        images.append(image_info)
                    except Exception as e:
                        # Si hay error extrayendo la imagen, continuar
                        continue

        return images

    def extract_captions(
        self,
        pdf_path: Path,
        start_page: int,
        end_page: int
    ) -> List[Dict]:
        """
        Extrae todos los captions/títulos de figuras.

        Returns:
            Lista de captions con su texto, número y ubicación
        """
        captions = []

        with fitz.open(pdf_path) as doc:
            for page_num in range(start_page - 1, end_page):
                page = doc[page_num]
                blocks = page.get_text('dict')['blocks']

                for block in blocks:
                    if block.get('type') != 0:  # Solo text blocks
                        continue

                    lines = block.get('lines', [])

                    for line in lines:
                        # Extraer texto de la línea
                        line_text = ''.join(
                            span.get('text', '')
                            for span in line.get('spans', [])
                        ).strip()

                        # Detectar si es caption
                        is_caption, caption_type, number, description = self.detect_caption(line_text)

                        if not is_caption:
                            continue

                        bbox = line.get('bbox', [0, 0, 0, 0])

                        caption_info = {
                            'text': line_text,
                            'caption_type': caption_type,
                            'number': number,
                            'description': description,
                            'page': page_num + 1,
                            'bbox': bbox,
                            'y_position': bbox[1]  # Posición vertical
                        }

                        captions.append(caption_info)

        return captions

    def associate_captions_with_images(
        self,
        images: List[Dict],
        captions: List[Dict],
        max_distance: float = 100
    ) -> List[Dict]:
        """
        Asocia cada caption con su imagen correspondiente.

        Estrategia:
        - Buscar la imagen más cercana al caption (arriba o abajo)
        - Que estén en la misma página
        - Distancia vertical < max_distance

        Returns:
            Lista de figuras con imagen y caption asociados
        """
        figures = []

        for caption in captions:
            caption_page = caption['page']
            caption_y = caption['y_position']

            # Buscar imágenes en la misma página
            page_images = [img for img in images if img['page'] == caption_page]

            if not page_images:
                # Caption sin imagen asociada
                figures.append({
                    'caption': caption,
                    'image': None,
                    'position': 'caption_only'
                })
                continue

            # Encontrar la imagen más cercana
            closest_image = None
            min_distance = float('inf')
            position = None

            for img in page_images:
                img_y_top = img['bbox'][1]
                img_y_bottom = img['bbox'][3]

                # Calcular distancia vertical
                # Caption puede estar arriba (antes) o abajo (después) de la imagen
                if caption_y < img_y_top:
                    # Caption está arriba de la imagen
                    distance = img_y_top - caption_y
                    pos = 'above'
                else:
                    # Caption está abajo de la imagen
                    distance = caption_y - img_y_bottom
                    pos = 'below'

                if distance < min_distance and distance <= max_distance:
                    min_distance = distance
                    closest_image = img
                    position = pos

            if closest_image:
                figures.append({
                    'caption': caption,
                    'image': closest_image,
                    'position': position,
                    'distance': min_distance
                })
            else:
                # Caption sin imagen cercana
                figures.append({
                    'caption': caption,
                    'image': None,
                    'position': 'caption_only'
                })

        # Agregar imágenes sin caption
        associated_image_xrefs = set(
            fig['image']['xref']
            for fig in figures
            if fig['image'] is not None
        )

        for img in images:
            if img['xref'] not in associated_image_xrefs:
                figures.append({
                    'caption': None,
                    'image': img,
                    'position': 'image_only'
                })

        # Asignar IDs
        for idx, fig in enumerate(figures, 1):
            fig['figure_id'] = idx

        return figures

    def extract_figures(
        self,
        pdf_path: Path,
        start_page: int,
        end_page: int
    ) -> List[Dict]:
        """
        Extrae todas las figuras (imágenes + captions) de un rango de páginas.
        """
        images = self.extract_images(pdf_path, start_page, end_page)
        captions = self.extract_captions(pdf_path, start_page, end_page)
        figures = self.associate_captions_with_images(images, captions)

        return figures

    def format_figures(
        self,
        figures: List[Dict],
        format_type: str = "text",
        show_metadata: bool = True
    ) -> str:
        """
        Formatea las figuras extraídas.
        """
        if format_type == "json":
            import json
            return json.dumps(figures, indent=2, ensure_ascii=False)

        output = []

        if format_type == "markdown":
            output.append("# Figuras Detectadas\n")
        else:
            output.append("FIGURAS DETECTADAS")
            output.append("="*80)
            output.append("")

        for fig in figures:
            caption = fig.get('caption')
            image = fig.get('image')

            if show_metadata:
                if caption and image:
                    output.append(f"[Figura {fig['figure_id']}] Página: {caption['page']} | Caption {fig['position']} imagen")
                    output.append("-"*80)
                    output.append(f"{caption['caption_type']} {caption['number']}: {caption['description']}")
                    output.append(f"Imagen: {image['width']}x{image['height']}px ({image['image_type']})")

                elif caption and not image:
                    output.append(f"[Figura {fig['figure_id']}] Página: {caption['page']} | Solo caption (sin imagen)")
                    output.append("-"*80)
                    output.append(f"{caption['caption_type']} {caption['number']}: {caption['description']}")

                elif image and not caption:
                    output.append(f"[Figura {fig['figure_id']}] Página: {image['page']} | Solo imagen (sin caption)")
                    output.append("-"*80)
                    output.append(f"Imagen sin título: {image['width']}x{image['height']}px ({image['image_type']})")

            else:
                # Solo mostrar el caption
                if caption:
                    output.append(f"{caption['caption_type']} {caption['number']}: {caption['description']}")

            output.append("")

        return "\n".join(output)


if __name__ == "__main__":
    # Test con Capítulo 1
    pdf_path = Path("../../domains/operaciones/eaf/shared/source/EAF-089-2025.pdf")

    print("="*80)
    print("EXTRACTOR DE FIGURAS - CAPÍTULO 1")
    print("="*80)
    print()

    extractor = FigureExtractor()
    figures = extractor.extract_figures(
        pdf_path,
        start_page=1,
        end_page=11
    )

    print(f"✅ Detectadas {len(figures)} figuras\n")

    # Mostrar resultados
    output = extractor.format_figures(
        figures,
        format_type="text",
        show_metadata=True
    )

    print(output)

    print("="*80)
    print("📊 Estadísticas:")
    print(f"   Total figuras: {len(figures)}")

    with_caption = sum(1 for f in figures if f['caption'] is not None)
    with_image = sum(1 for f in figures if f['image'] is not None)
    complete = sum(1 for f in figures if f['caption'] is not None and f['image'] is not None)

    print(f"   Con caption: {with_caption}")
    print(f"   Con imagen: {with_image}")
    print(f"   Completas (caption + imagen): {complete}")

    print("="*80)
