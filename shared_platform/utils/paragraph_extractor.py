#!/usr/bin/env python3
"""
Paragraph Extractor - Extrae párrafos de texto narrativo del PDF

Desafíos:
- Un párrafo puede estar dividido en múltiples blocks/boxes
- Necesitamos unir los blocks que pertenecen al mismo párrafo
- Distinguir párrafos de tablas, listas y títulos

Estrategia:
1. Extraer todos los text blocks en orden de lectura (top-to-bottom, left-to-right)
2. Identificar qué blocks son texto narrativo (no tablas, no listas, no títulos)
3. Unir blocks consecutivos que forman un mismo párrafo
4. Asociar cada párrafo a su sección/título correspondiente
"""
import fitz
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from detailed_heading_detector import DetailedHeadingDetector


class ParagraphExtractor:
    """
    Extrae párrafos de texto narrativo del PDF.

    Un párrafo se define como:
    - Texto continuo (no tabla, no lista)
    - Puede abarcar múltiples boxes/blocks
    - Separado de otros párrafos por saltos de línea o cambios de sección
    """

    def __init__(self):
        self.heading_detector = DetailedHeadingDetector()

        # Patrones que indican que NO es un párrafo narrativo
        self.non_paragraph_patterns = [
            # Títulos con numeración
            r'^[a-z]\.\d+(?:\s|$)',  # d.1, d.2
            r'^[a-z]\.(?:\s|$)',      # a., b., c.
            r'^\d+\.(?!\d)\s*',       # 1., 2., 3.
            r'^\d+\.\d+\s+[A-Za-z]',  # 7.1 Texto

            # Listas
            r'^[•\-\*]\s+',           # Viñetas
            r'^[a-z]\)\s+',           # a) b) c)
            r'^\d+\)\s+',             # 1) 2) 3)

            # Headers/metadata
            r'^Página\s+\d+',
            r'^Estudio para análisis',
            r'^Fecha de Emisión:',
            r'^Plazo Máximo:',
            r'^Informe de fallas',

            # Tablas con datos numéricos
            r'\d{1,2}:\d{2}\s+\d{1,2}:\d{2}',  # Tiempos múltiples
            r'^\d+\.?\d*\s*(MW|MWh|kV|Hz)',     # Valores con unidades

            # Patrones de tablas estructuradas
            r'^(Nombre|Tipo|Tensión|Segmento|Propietario|RUT|Representante|Dirección)\s+(de |del |elemento )?',  # Labels de tabla
            r'^\d{2}/\d{2}/\d{4}$',  # Solo fecha
            r'^\d{2}-\d{2}-\d{4}$',  # Solo fecha formato DD-MM-YYYY
            r'^\d{1,3}%$',  # Solo porcentaje
            r'^(Fecha|Hora|Consumos|Demanda|Porcentaje|Calificación|Apagón|Empresa)\s+',  # Headers de tabla
            r'\d+\s+informe?s?\s+(en|fuera de)\s+plazo',  # Filas de tabla de informes
            r'no recibido por el CEN',  # Contenido de tabla de cumplimiento
            r'^[A-Z][A-Z\s\.\-]+(S\.A\.|SPA|Ltda\.?)$',  # Nombres de empresas sueltos (todo mayúsculas)
            r'^\d{4}:\s*[A-Z]',  # Códigos como "4102: Coquimbo"
        ]

    def is_narrative_text(self, text: str, detected_headings: List[str] = None) -> bool:
        """
        Determina si el texto es narrativo (párrafo normal).

        Args:
            text: Texto a evaluar
            detected_headings: Lista de textos ya detectados como títulos

        Returns:
            True si es texto narrativo, False si es título/lista/tabla
        """
        text = text.strip()

        if len(text) < 10:  # Muy corto, probablemente no es párrafo
            return False

        # (Removido filtro de minúsculas - permite continuaciones válidas)

        # Verificar si este texto ya fue detectado como título
        if detected_headings and text in detected_headings:
            return False

        # Filtrar títulos de documento (texto completo entre comillas)
        if text.startswith('"') and text.endswith('"'):
            return False

        # Verificar patrones de NO-párrafo
        for pattern in self.non_paragraph_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return False

        # Detectar si tiene numeración de título
        has_numbering, _ = self.heading_detector.detect_numbering(text)
        if has_numbering:
            return False

        # Detectar contenido de tabla por densidad de palabras clave
        # Solo keywords que aparecen casi exclusivamente en tablas (no en texto narrativo)
        table_only_keywords = [
            'informes en plazo',
            'informes fuera de plazo',
            'no recibido por el CEN',
            'Informe de fallas de',
        ]

        keyword_count = sum(1 for keyword in table_only_keywords if keyword in text)
        # Si hay 1+ palabra clave exclusiva de tabla, es tabla
        if keyword_count >= 1:
            return False

        # Si tiene múltiples nombres de empresas (2+ sufijos legales), es tabla
        company_suffixes = len(re.findall(r'\b(S\.A\.|SPA|Ltda\.?|S\.p\.A\.)\b', text, re.IGNORECASE))
        if company_suffixes >= 2:
            return False

        # Si es solo un nombre de empresa (termina en sufijo legal y es corto)
        if len(text.split()) <= 6 and re.search(r'(S\.A\.|SPA|Ltda\.?|S\.p\.A\.)$', text, re.IGNORECASE):
            return False

        # Si tiene MUCHAS referencias a subestaciones (5+), es una lista de subestaciones
        subestacion_count = len(re.findall(r'S/E\s+[A-Za-z]', text))
        if subestacion_count >= 5:
            return False

        # (Removido filtro de campos de formulario - se incluyen como párrafos válidos)

        # Si el texto tiene formato "palabra clave: valor" múltiples veces, es tabla
        key_value_pairs = len(re.findall(r'^(\w+[\w\s]*?):\s+', text, re.MULTILINE))
        if key_value_pairs >= 2:
            return False

        # Si llegamos aquí, es probable que sea texto narrativo
        return True

    def should_merge_blocks(
        self,
        block1: Dict,
        block2: Dict,
        page_height: float
    ) -> bool:
        """
        Determina si dos blocks consecutivos deben unirse en un mismo párrafo.

        REGLA SIMPLE: Si hay CUALQUIER salto de línea (gap > 3px), son párrafos DIFERENTES.
        Solo se unen si están prácticamente pegados (continuación de la misma línea).
        """
        bbox1 = block1['bbox']
        bbox2 = block2['bbox']

        x1_start, y1_end = bbox1[0], bbox1[3]
        x2_start, y2_start = bbox2[0], bbox2[1]

        # 1. Verificar que estén en la misma columna (tolerancia 20px)
        if abs(x1_start - x2_start) > 20:
            return False

        # 2. Calcular distancia vertical entre blocks
        vertical_gap = y2_start - y1_end

        # REGLA NUEVA: Si hay gap > 3px, considerarlo un salto de línea = NUEVO PÁRRAFO
        # Solo unir si están prácticamente pegados (gap <= 3px)
        if vertical_gap > 3:
            return False

        # 3. Si hay gap negativo (overlap), definitivamente NO unir
        if vertical_gap < -2:
            return False

        return True

    def extract_text_blocks(
        self,
        pdf_path: Path,
        start_page: int,
        end_page: int
    ) -> List[Dict]:
        """
        Extrae todos los text blocks de un rango de páginas en orden de lectura.

        Returns:
            Lista de blocks con su texto, bbox, página, etc.
        """
        all_blocks = []

        with fitz.open(pdf_path) as doc:
            for page_num in range(start_page - 1, end_page):
                page = doc[page_num]
                page_height = page.rect.height
                blocks = page.get_text('dict')['blocks']

                for block_idx, block in enumerate(blocks):
                    if block.get('type') != 0:  # Solo text blocks
                        continue

                    lines = block.get('lines', [])
                    if not lines:
                        continue

                    # Extraer texto del block
                    block_text_parts = []
                    for line in lines:
                        line_text = ''.join(
                            span.get('text', '')
                            for span in line.get('spans', [])
                        )
                        block_text_parts.append(line_text.strip())

                    full_text = ' '.join(block_text_parts).strip()

                    if not full_text:
                        continue

                    # Extraer información de formato del primer span
                    first_span = lines[0]['spans'][0] if lines[0].get('spans') else {}

                    block_info = {
                        'text': full_text,
                        'bbox': block.get('bbox', [0, 0, 0, 0]),
                        'page': page_num + 1,
                        'page_height': page_height,
                        'block_idx': block_idx,
                        'font_size': first_span.get('size', 0),
                        'font_name': first_span.get('font', ''),
                    }

                    all_blocks.append(block_info)

        # Ordenar blocks por página, luego por posición vertical (top-to-bottom)
        all_blocks.sort(key=lambda b: (b['page'], b['bbox'][1]))

        return all_blocks

    def merge_blocks_into_paragraphs(
        self,
        blocks: List[Dict]
    ) -> List[Dict]:
        """
        Une blocks consecutivos que forman el mismo párrafo.

        Returns:
            Lista de párrafos, cada uno con su texto completo y metadatos
        """
        if not blocks:
            return []

        paragraphs = []
        current_paragraph = {
            'text': blocks[0]['text'],
            'start_page': blocks[0]['page'],
            'end_page': blocks[0]['page'],
            'bbox_start': blocks[0]['bbox'],
            'bbox_end': blocks[0]['bbox'],
            'blocks': [blocks[0]]
        }

        for i in range(1, len(blocks)):
            prev_block = blocks[i - 1]
            curr_block = blocks[i]

            # Verificar si están en la misma página
            same_page = (prev_block['page'] == curr_block['page'])

            # Decidir si unir
            should_merge = False
            if same_page:
                should_merge = self.should_merge_blocks(
                    prev_block,
                    curr_block,
                    curr_block['page_height']
                )

            if should_merge:
                # Unir al párrafo actual (solo si están MUY pegados, sin salto de línea)
                current_paragraph['text'] += ' ' + curr_block['text']
                current_paragraph['end_page'] = curr_block['page']
                current_paragraph['bbox_end'] = curr_block['bbox']
                current_paragraph['blocks'].append(curr_block)
            else:
                # Guardar párrafo actual y empezar uno nuevo
                paragraphs.append(current_paragraph)
                current_paragraph = {
                    'text': curr_block['text'],
                    'start_page': curr_block['page'],
                    'end_page': curr_block['page'],
                    'bbox_start': curr_block['bbox'],
                    'bbox_end': curr_block['bbox'],
                    'blocks': [curr_block]
                }

        # Agregar el último párrafo
        if current_paragraph['text']:
            paragraphs.append(current_paragraph)

        return paragraphs

    def extract_paragraphs(
        self,
        pdf_path: Path,
        start_page: int,
        end_page: int,
        headings: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """
        Extrae todos los párrafos narrativos de un rango de páginas.

        Args:
            pdf_path: Ruta al PDF
            start_page: Página inicial (1-indexed)
            end_page: Página final (1-indexed)
            headings: Lista de títulos detectados (para asociar párrafos a secciones)

        Returns:
            Lista de párrafos con texto, ubicación y metadatos
        """
        # 1. Extraer todos los text blocks
        all_blocks = self.extract_text_blocks(pdf_path, start_page, end_page)

        # 2. Crear lista de textos de títulos ya detectados
        detected_heading_texts = []
        if headings:
            detected_heading_texts = [h['text'].strip() for h in headings]

        # 3. Filtrar solo texto narrativo (eliminar títulos, listas, tablas)
        narrative_blocks = [
            block for block in all_blocks
            if self.is_narrative_text(block['text'], detected_heading_texts)
        ]

        # 4. Unir blocks que forman el mismo párrafo
        paragraphs = self.merge_blocks_into_paragraphs(narrative_blocks)

        # 5. Si tenemos headings, asociar cada párrafo a su sección
        if headings:
            paragraphs = self._associate_paragraphs_to_sections(paragraphs, headings)

        # 6. Agregar ID secuencial
        for idx, para in enumerate(paragraphs, 1):
            para['paragraph_id'] = idx

        return paragraphs

    def _associate_paragraphs_to_sections(
        self,
        paragraphs: List[Dict],
        headings: List[Dict]
    ) -> List[Dict]:
        """
        Asocia cada párrafo a la sección/título más cercano anterior.
        """
        for para in paragraphs:
            para_page = para['start_page']
            para_y = para['bbox_start'][1]  # Posición vertical

            # Encontrar el título más cercano ANTES de este párrafo
            closest_heading = None
            for heading in headings:
                h_page = heading['page']
                h_y = heading['bbox'][1]

                # El heading debe estar antes del párrafo
                if h_page < para_page or (h_page == para_page and h_y < para_y):
                    closest_heading = heading
                else:
                    break  # Ya pasamos el párrafo

            if closest_heading:
                para['section'] = closest_heading['text']
                para['section_level'] = closest_heading['level']
            else:
                para['section'] = None
                para['section_level'] = None

        return paragraphs

    def format_paragraphs(
        self,
        paragraphs: List[Dict],
        format_type: str = "text",
        show_metadata: bool = False,
        max_line_width: int = 100
    ) -> str:
        """
        Formatea los párrafos extraídos.

        Args:
            paragraphs: Lista de párrafos
            format_type: "text", "markdown", o "json"
            show_metadata: Si mostrar metadatos (página, sección, etc.)
            max_line_width: Ancho máximo de línea en caracteres
        """
        if format_type == "json":
            import json
            return json.dumps(paragraphs, indent=2, ensure_ascii=False)

        import textwrap

        output = []

        if format_type == "markdown":
            output.append("# Párrafos Extraídos\n")
        else:
            output.append("PÁRRAFOS EXTRAÍDOS")
            output.append("="*80)
            output.append("")

        for para in paragraphs:
            if show_metadata:
                # Mostrar metadatos
                section_info = f"Sección: {para.get('section', 'N/A')}"
                page_info = f"Página: {para['start_page']}"
                if para['start_page'] != para['end_page']:
                    page_info += f"-{para['end_page']}"
                blocks_info = f"Blocks: {len(para['blocks'])}"

                output.append(f"[Párrafo {para['paragraph_id']}] {page_info} | {section_info} | {blocks_info}")
                output.append("-"*80)

            # Mostrar texto del párrafo con word wrap
            wrapped_text = textwrap.fill(para['text'], width=max_line_width)
            output.append(wrapped_text)
            output.append("")

        return "\n".join(output)


if __name__ == "__main__":
    # Test con Capítulo 1
    pdf_path = Path("../../domains/operaciones/eaf/shared/source/EAF-089-2025.pdf")

    print("="*80)
    print("EXTRACTOR DE PÁRRAFOS - CAPÍTULO 1")
    print("="*80)
    print()

    # 1. Detectar títulos primero
    heading_detector = DetailedHeadingDetector()
    headings = heading_detector.extract_headings(
        pdf_path,
        start_page=1,
        end_page=11,
        chapter_number=1
    )

    print(f"✅ Detectados {len(headings)} títulos")

    # 2. Extraer párrafos
    extractor = ParagraphExtractor()
    paragraphs = extractor.extract_paragraphs(
        pdf_path,
        start_page=1,
        end_page=11,
        headings=headings
    )

    print(f"✅ Extraídos {len(paragraphs)} párrafos\n")

    # 3. Mostrar resultados
    output = extractor.format_paragraphs(
        paragraphs,
        format_type="text",
        show_metadata=True
    )

    print(output)

    print("\n" + "="*80)
    print("📊 Estadísticas:")
    print(f"   Total párrafos: {len(paragraphs)}")
    print(f"   Total títulos: {len(headings)}")

    # Contar párrafos por sección
    sections = {}
    for para in paragraphs:
        section = para.get('section', 'Sin sección')
        sections[section] = sections.get(section, 0) + 1

    print(f"\n   Párrafos por sección:")
    for section, count in sections.items():
        if section is None:
            section_name = "Sin sección"
        else:
            section_name = section[:50] + "..." if len(section) > 50 else section
        print(f"      {section_name}: {count}")

    print("="*80)
