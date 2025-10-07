#!/usr/bin/env python3
"""
List Detector - Detecta y extrae listas del PDF

Tipos de listas a detectar:
1. Listas numeradas: 1., 2., 3.
2. Listas con letras: a), b), c) o a., b., c.
3. Listas con viñetas: •, -, *, ◦
4. Listas jerárquicas (sub-listas)

Desafíos:
- Una lista puede abarcar múltiples páginas
- Necesitamos detectar jerarquía (lista principal vs sub-lista)
- Distinguir listas de títulos (que también usan numeración)
"""
import fitz
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional


class ListDetector:
    """
    Detecta y extrae listas estructuradas del PDF.

    Diferencia entre título y lista:
    - Título: Generalmente corto, conceptual, puede no tener continuación inmediata
    - Lista: Múltiples ítems consecutivos con el mismo patrón de numeración
    """

    def __init__(self):
        # Patrones de numeración/viñetas para listas
        self.list_patterns = [
            # Listas con paréntesis - típicamente listas, NO títulos
            (r"^([a-z])\)\s+", "letter_paren", 1),      # a) b) c)
            (r"^([0-9]+)\)\s+", "number_paren", 1),     # 1) 2) 3)
            (r"^([ivxIVX]+)\)\s+", "roman_paren", 1),   # i) ii) iii)

            # Viñetas
            (r"^[•●○◦]\s+", "bullet", 1),               # • texto
            (r"^[-–—]\s+", "dash", 1),                  # - texto
            (r"^[*]\s+", "asterisk", 1),                # * texto

            # Listas con punto (más difícil distinguir de títulos)
            # SOLO si hay múltiples consecutivos
            (r"^([a-z])\.\s+", "letter_dot", 2),        # a. b. c.
            (r"^([0-9]+)\.\s+", "number_dot", 2),       # 1. 2. 3.

            # Sub-listas con indentación
            (r"^\s{2,}([a-z])\)\s+", "sublevel_letter_paren", 2),
            (r"^\s{2,}([0-9]+)\)\s+", "sublevel_number_paren", 2),
            (r"^\s{2,}[•○◦]\s+", "sublevel_bullet", 2),
        ]

    def detect_list_item(self, text: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Detecta si un texto es un ítem de lista.

        Returns:
            (is_list_item, pattern_type, marker)
            - is_list_item: True si es ítem de lista
            - pattern_type: tipo de patrón (bullet, number_paren, etc.)
            - marker: el marcador extraído (a, 1, •, etc.)
        """
        for pattern, pattern_type, min_consecutive in self.list_patterns:
            match = re.match(pattern, text)
            if match:
                # Extraer el marcador si existe (para a), 1), etc.)
                marker = match.group(1) if match.groups() else None
                return True, pattern_type, marker

        return False, None, None

    def is_likely_title(self, text: str, is_first_occurrence: bool = False) -> bool:
        """
        Determina si un texto con numeración es más probable que sea título que lista.

        Heurísticas:
        - Si tiene formato "a.1" o "d.2" -> título
        - Si es muy corto (< 5 palabras) y es la primera ocurrencia -> puede ser título
        - Si tiene formato específico de título del documento
        """
        # Títulos jerárquicos: d.1, d.2, etc.
        if re.match(r'^[a-z]\.\d+', text):
            return True

        # Títulos numéricos jerárquicos: 7.1, 9.2, etc.
        if re.match(r'^\d+\.\d+\s+[A-Za-z]', text):
            return True

        # Si es el primer ítem con "a." o "1." y es muy corto, podría ser título
        # Esto lo validaremos después mirando si hay ítems consecutivos
        return False

    def get_indentation_level(self, bbox: List[float]) -> int:
        """
        Determina el nivel de indentación basado en la posición x.

        Returns:
            0 - Sin indentación (margen izquierdo)
            1 - Primera indentación
            2 - Segunda indentación
            etc.
        """
        x_start = bbox[0]

        # Definir rangos de indentación (ajustar según el documento)
        if x_start < 80:
            return 0  # Margen izquierdo
        elif x_start < 100:
            return 1  # Primera indentación
        elif x_start < 130:
            return 2  # Segunda indentación
        else:
            return 3  # Más indentado

    def extract_lists(
        self,
        pdf_path: Path,
        start_page: int,
        end_page: int
    ) -> List[Dict]:
        """
        Extrae todas las listas de un rango de páginas.

        Returns:
            Lista de listas detectadas, cada una con sus ítems
        """
        all_list_items = []

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

                        if not line_text:
                            continue

                        # Detectar si es ítem de lista
                        is_list, pattern_type, marker = self.detect_list_item(line_text)

                        if not is_list:
                            continue

                        # Verificar que no sea título
                        if self.is_likely_title(line_text):
                            continue

                        # Determinar nivel de indentación
                        bbox = line.get('bbox', [0, 0, 0, 0])
                        indent_level = self.get_indentation_level(bbox)

                        # Extraer el contenido (texto sin el marcador)
                        content = re.sub(
                            r'^(\s*([a-z0-9ivxIVX]+)[.\)]\s*|[•●○◦\-–—*]\s*)',
                            '',
                            line_text
                        ).strip()

                        list_item = {
                            'text': line_text,
                            'content': content,
                            'marker': marker,
                            'pattern_type': pattern_type,
                            'indent_level': indent_level,
                            'page': page_num + 1,
                            'bbox': bbox
                        }

                        all_list_items.append(list_item)

        # Agrupar ítems consecutivos en listas
        lists = self._group_items_into_lists(all_list_items)

        return lists

    def _group_items_into_lists(self, items: List[Dict]) -> List[Dict]:
        """
        Agrupa ítems consecutivos en listas completas.

        Una lista termina cuando:
        - Cambia el patrón de numeración
        - Hay un gran salto de página sin continuidad
        - Aparece un título o texto narrativo entre medio
        """
        if not items:
            return []

        lists = []
        current_list = {
            'items': [items[0]],
            'pattern_type': items[0]['pattern_type'],
            'start_page': items[0]['page'],
            'end_page': items[0]['page'],
            'indent_level': items[0]['indent_level']
        }

        for i in range(1, len(items)):
            prev_item = items[i - 1]
            curr_item = items[i]

            # Verificar si continúa la misma lista
            same_pattern = (curr_item['pattern_type'] == current_list['pattern_type'])
            same_indent = (curr_item['indent_level'] == current_list['indent_level'])
            consecutive_page = (curr_item['page'] <= prev_item['page'] + 1)

            # Si es consecutivo con el ítem anterior (mismo patrón, nivel, página cercana)
            if same_pattern and same_indent and consecutive_page:
                # Continuar la lista actual
                current_list['items'].append(curr_item)
                current_list['end_page'] = curr_item['page']
            else:
                # Guardar lista actual y empezar una nueva
                lists.append(current_list)
                current_list = {
                    'items': [curr_item],
                    'pattern_type': curr_item['pattern_type'],
                    'start_page': curr_item['page'],
                    'end_page': curr_item['page'],
                    'indent_level': curr_item['indent_level']
                }

        # Agregar la última lista
        if current_list['items']:
            lists.append(current_list)

        # Filtrar listas con un solo ítem (probablemente no son listas reales)
        # EXCEPTO si es una viñeta (bullet) que puede ser ítem único
        lists = [
            lst for lst in lists
            if len(lst['items']) >= 2 or 'bullet' in lst['pattern_type']
        ]

        # Asignar IDs
        for idx, lst in enumerate(lists, 1):
            lst['list_id'] = idx

        return lists

    def format_lists(
        self,
        lists: List[Dict],
        format_type: str = "text",
        show_metadata: bool = True
    ) -> str:
        """
        Formatea las listas extraídas.

        Args:
            lists: Lista de listas detectadas
            format_type: "text", "markdown", o "json"
            show_metadata: Si mostrar metadatos
        """
        if format_type == "json":
            import json
            return json.dumps(lists, indent=2, ensure_ascii=False)

        output = []

        if format_type == "markdown":
            output.append("# Listas Detectadas\n")
        else:
            output.append("LISTAS DETECTADAS")
            output.append("="*80)
            output.append("")

        for lst in lists:
            if show_metadata:
                page_info = f"Página: {lst['start_page']}"
                if lst['start_page'] != lst['end_page']:
                    page_info += f"-{lst['end_page']}"

                output.append(f"[Lista {lst['list_id']}] {page_info} | Tipo: {lst['pattern_type']} | Items: {len(lst['items'])} | Nivel: {lst['indent_level']}")
                output.append("-"*80)

            # Mostrar ítems
            for item in lst['items']:
                indent = "  " * item['indent_level']
                # Reconstruir el formato original de la lista
                if item['marker']:
                    if 'paren' in item['pattern_type']:
                        prefix = f"{item['marker']}) "
                    else:
                        prefix = f"{item['marker']}. "
                else:
                    # Viñetas
                    if 'bullet' in item['pattern_type']:
                        prefix = "• "
                    elif 'dash' in item['pattern_type']:
                        prefix = "- "
                    else:
                        prefix = "* "

                output.append(f"{indent}{prefix}{item['content']}")

            output.append("")

        return "\n".join(output)


if __name__ == "__main__":
    # Test con Capítulo 1
    pdf_path = Path("../../domains/operaciones/eaf/shared/source/EAF-089-2025.pdf")

    print("="*80)
    print("DETECTOR DE LISTAS - CAPÍTULO 1")
    print("="*80)
    print()

    detector = ListDetector()
    lists = detector.extract_lists(
        pdf_path,
        start_page=1,
        end_page=11
    )

    print(f"✅ Detectadas {len(lists)} listas\n")

    # Mostrar resultados
    output = detector.format_lists(
        lists,
        format_type="text",
        show_metadata=True
    )

    print(output)

    print("="*80)
    print("📊 Estadísticas:")
    print(f"   Total listas: {len(lists)}")

    total_items = sum(len(lst['items']) for lst in lists)
    print(f"   Total ítems: {total_items}")

    # Por tipo
    by_type = {}
    for lst in lists:
        by_type[lst['pattern_type']] = by_type.get(lst['pattern_type'], 0) + 1

    print("\n   Por tipo:")
    for ptype, count in by_type.items():
        print(f"      {ptype}: {count}")

    print("="*80)
