#!/usr/bin/env python3
"""
Detailed Heading Detector - Detecta TODOS los títulos en un capítulo
Incluye títulos principales Y subtítulos intermedios (ej: d.1, d.2, d.3, d.4)
"""
import fitz
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional


class DetailedHeadingDetector:
    """
    Detecta todos los niveles de títulos en un capítulo específico.

    Regla principal: Texto con numeración al inicio = título

    Patrones detectados:
    - Principales: a., b., c., d., e., f., g., h., i.
    - Jerárquicos: d.1, d.2, d.3, d.4 (letra.número)
    - Numéricos jerárquicos: 7.1, 7.2, 9.1, 9.2 (número.número con texto)
    """

    def __init__(self):
        # Patrones de numeración para títulos (más permisivos que el índice general)
        self.numbering_patterns = [
            # Jerárquico complejo: "d.1.1", "a.2.3"
            (r"^[a-z]\.\d+\.\d+(?:\s|$)", "hierarchical_complex"),
            # Jerárquico simple: "d.1", "d.2", "e.1"
            (r"^[a-z]\.\d+(?:\s|$)", "hierarchical_simple"),
            # Letra con punto: "a.", "b.", "c."
            (r"^[a-z]\.(?:\s|$)", "letter"),
            # Número.Número con texto: "7.1 Texto", "9.2 Algo"
            (r"^\d+\.\d+\s+[A-Za-z]", "number_hierarchical"),
            # Número simple: "1.", "2.", "3."
            (r"^\d+\.(?!\d)\s*", "numbered"),
        ]

    def detect_numbering(self, text: str) -> Tuple[bool, Optional[str]]:
        """Detecta si el texto tiene numeración de título."""
        for pattern, pattern_type in self.numbering_patterns:
            if re.match(pattern, text.strip()):
                return True, pattern_type
        return False, None

    def is_table_content(self, text: str) -> bool:
        """Detecta si el texto es contenido de tabla, no un título."""
        text_lower = text.lower()

        # Filtros de contenido de tabla
        filters = [
            # Tiempos/horarios múltiples
            r'\d{1,2}:\d{2}\s+\d{1,2}:\d{2}',
            # Valores con unidades
            r'^\d+\.?\d*\s*(MW|MWh|kV|Hz|GW|kW)',
            # Patrones de cronología
            r'^[A-Z][a-zA-Z\s]+\d{1,2}:\d{2}\s+',
            # Eventos de cronología con numeración
            r'^(\d+|[a-z])[\.\)]\s+(CDC|Enel|AES|Colb[uú]n|Coordinador|STM|Minera)\s+(instruye|indica|informa)',
            # Referencias narrativas
            r'(del|en el|según)\s+(presente|mismo)\s+informe',
            # Años solos
            r'^(19|20)\d{2}[\.\)]?\s*$',
            # Nombres con iniciales
            r'^[A-Z]\.\s+[A-Z]\.\s+[A-Z]',
            # Eventos con acción
            r'^[A-Z]\.\s+[A-Z][a-zA-Z0-9\-\+\s]+\s+(inicia|disponible|energiza|cancelado)',
        ]

        for pattern in filters:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    def extract_headings(
        self,
        pdf_path: Path,
        start_page: int,
        end_page: int,
        chapter_number: Optional[int] = None
    ) -> List[Dict]:
        """
        Extrae todos los títulos de un rango de páginas.

        Args:
            pdf_path: Ruta al PDF
            start_page: Página inicial (1-indexed)
            end_page: Página final (1-indexed, inclusive)
            chapter_number: Número del capítulo para contexto (opcional)

        Returns:
            Lista de diccionarios con información de cada título
        """
        headings = []

        with fitz.open(pdf_path) as doc:
            for page_num in range(start_page - 1, end_page):  # Convert to 0-indexed
                page = doc[page_num]
                blocks = page.get_text('dict')['blocks']

                for block in blocks:
                    if block.get('type') != 0:  # Solo bloques de texto
                        continue

                    lines = block.get('lines', [])
                    if not lines:
                        continue

                    # Procesar línea por línea
                    for line in lines:
                        spans = line.get('spans', [])
                        if not spans:
                            continue

                        # Extraer texto de la línea
                        line_text = ''.join(span.get('text', '') for span in spans).strip()

                        if len(line_text) < 2:  # Muy corto
                            continue

                        # Caso especial: título de documento en página 1 (entre comillas, sin numeración)
                        if page_num == start_page - 1:  # Primera página
                            # Comillas tipográficas: " (8220) y " (8221) o ASCII " (34)
                            starts_with_quote = ord(line_text[0]) in [8220, 8221, 34] if line_text else False
                            contains_closing_quote = any(ord(c) in [8220, 8221, 34] for c in line_text)

                            if starts_with_quote and contains_closing_quote and len(line_text) > 20:
                                # Es el título principal del documento
                                heading = {
                                    'text': line_text.strip(),
                                    'page': page_num + 1,
                                    'pattern_type': 'document_title',
                                    'level': 0,  # Nivel 0 = título de documento
                                    'font_size': spans[0].get('size', 0),
                                    'font_name': spans[0].get('font', ''),
                                    'is_bold': bool(spans[0].get('flags', 0) & 2**4),
                                    'bbox': line.get('bbox', [0, 0, 0, 0])
                                }
                                headings.append(heading)
                                continue

                        # Detectar numeración
                        has_numbering, pattern_type = self.detect_numbering(line_text)

                        if not has_numbering:
                            continue

                        # Filtrar contenido de tablas
                        if self.is_table_content(line_text):
                            continue

                        # Extraer información de formato
                        first_span = spans[0]
                        font_size = first_span.get('size', 0)
                        font_name = first_span.get('font', '')
                        flags = first_span.get('flags', 0)
                        is_bold = bool(flags & 2**4)

                        # Determinar nivel jerárquico
                        level = self._determine_level(line_text, pattern_type)

                        heading = {
                            'text': line_text,
                            'page': page_num + 1,
                            'pattern_type': pattern_type,
                            'level': level,
                            'font_size': font_size,
                            'font_name': font_name,
                            'is_bold': is_bold,
                            'bbox': line.get('bbox', [0, 0, 0, 0])
                        }

                        headings.append(heading)

        return headings

    def _determine_level(self, text: str, pattern_type: str) -> int:
        """
        Determina el nivel jerárquico del título.

        Niveles:
        1 - Capítulo principal (1., 2., 3.)
        2 - Subsección letra (a., b., c.)
        3 - Subsección jerárquica simple (d.1, d.2)
        4 - Subsección jerárquica compleja (d.1.1, d.1.2)
        """
        if pattern_type == "numbered":
            # Capítulo principal: "1.", "2."
            return 1
        elif pattern_type == "number_hierarchical":
            # Numérico jerárquico: "7.1", "9.2"
            return 2
        elif pattern_type == "letter":
            # Letra simple: "a.", "b."
            return 2
        elif pattern_type == "hierarchical_simple":
            # Jerárquico simple: "d.1", "d.2"
            return 3
        elif pattern_type == "hierarchical_complex":
            # Jerárquico complejo: "d.1.1"
            return 4
        else:
            return 5

    def format_headings(self, headings: List[Dict], format_type: str = "markdown") -> str:
        """
        Formatea la lista de títulos.

        Args:
            headings: Lista de títulos detectados
            format_type: "markdown", "text", o "json"
        """
        if format_type == "markdown":
            output = ["# Títulos Detallados\n"]

            for h in headings:
                indent = "  " * (h['level'] - 1)
                marker = "-" if h['level'] > 1 else "**"

                if h['level'] == 1:
                    output.append(f"{marker}{h['text']}{marker} (p. {h['page']})")
                else:
                    output.append(f"{indent}- {h['text']} (p. {h['page']})")

            return "\n".join(output)

        elif format_type == "text":
            output = ["TÍTULOS DETALLADOS", "="*80, ""]

            for h in headings:
                indent = "  " * (h['level'] - 1)
                output.append(f"{indent}{h['text']} (página {h['page']}, nivel {h['level']})")

            return "\n".join(output)

        else:  # json
            import json
            return json.dumps(headings, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    import sys

    # Test con Capítulo 1
    detector = DetailedHeadingDetector()

    pdf_path = Path("../../domains/operaciones/eaf/shared/source/EAF-089-2025.pdf")

    print("="*80)
    print("DETECTOR DE TÍTULOS DETALLADOS - CAPÍTULO 1")
    print("="*80)
    print()

    # Capítulo 1: páginas 1-11
    headings = detector.extract_headings(pdf_path, start_page=1, end_page=11, chapter_number=1)

    print(f"✅ Encontrados {len(headings)} títulos en Capítulo 1\n")

    # Mostrar en formato texto
    output = detector.format_headings(headings, format_type="text")
    print(output)

    print("\n" + "="*80)
    print("📊 Estadísticas:")
    print(f"   Total títulos: {len(headings)}")

    # Contar por nivel
    levels = {}
    for h in headings:
        levels[h['level']] = levels.get(h['level'], 0) + 1

    for level in sorted(levels.keys()):
        print(f"   Nivel {level}: {levels[level]} títulos")
    print("="*80)
