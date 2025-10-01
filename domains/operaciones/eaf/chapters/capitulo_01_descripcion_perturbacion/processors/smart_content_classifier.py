"""
Clasificador Inteligente de Contenido
Detecta el tipo de contenido ANTES de procesarlo:
- Tablas estructuradas
- Texto narrativo/párrafos
- Listas
- Encabezados/títulos
- Imágenes/gráficos
- Fórmulas/ecuaciones
"""

import json
import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class ContentType(Enum):
    """Tipos de contenido posibles."""
    TABLE = "table"
    PARAGRAPH = "paragraph"
    LIST = "list"
    HEADING = "heading"
    IMAGE = "image"
    FORMULA = "formula"
    METADATA = "metadata"
    UNKNOWN = "unknown"


@dataclass
class ContentBlock:
    """Bloque de contenido clasificado."""
    type: ContentType
    content: any
    bbox: Tuple[float, float, float, float]
    confidence: float
    page: int
    metadata: Dict


class SmartContentClassifier:
    """
    Clasificador inteligente que detecta tipos de contenido
    usando características visuales y estructurales.
    """

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.pdf_doc = fitz.open(pdf_path)

    def classify_page_content(self, page_num: int) -> List[ContentBlock]:
        """Clasifica todo el contenido de una página."""
        print(f"📄 Analizando página {page_num}...")

        page = self.pdf_doc[page_num - 1]
        text_dict = page.get_text("dict")

        # Extraer elementos con coordenadas
        text_items = self._extract_text_items(text_dict["blocks"])
        images = self._extract_images(page)
        drawings = self._extract_drawings(page)

        # Agrupar en filas
        rows = self._group_into_rows(text_items)

        # Clasificar cada región
        content_blocks = []

        # PASO 1: Detectar imágenes
        for img in images:
            content_blocks.append(ContentBlock(
                type=ContentType.IMAGE,
                content=img,
                bbox=img["bbox"],
                confidence=1.0,
                page=page_num,
                metadata={"image_info": img}
            ))

        # PASO 1.5: Detectar tablas con PyMuPDF primero (más preciso)
        pymupdf_tables = self._detect_tables_with_pymupdf(page, page_num)
        table_regions = [t.bbox for t in pymupdf_tables]
        content_blocks.extend(pymupdf_tables)

        # PASO 2: Clasificar texto por regiones (excluir regiones ya clasificadas como tablas)
        # IMPORTANTE: SIEMPRE usar PyMuPDF para tablas, nunca detección manual
        i = 0
        while i < len(rows):
            # Skip rows that are inside table regions
            if rows[i] and self._row_in_table_region(rows[i], table_regions):
                i += 1
                continue

            # Analizar región actual (SIEMPRE skip manual table detection)
            block_type, block_content, block_end = self._classify_text_region(
                rows, i, page_num, skip_table_detection=True
            )

            if block_type != ContentType.UNKNOWN:
                content_blocks.append(block_content)

            i = block_end

        return content_blocks

    def _row_in_table_region(self, row: List[Dict], table_regions: List[Tuple]) -> bool:
        """Check if a row is inside any table region."""
        if not row or not table_regions:
            return False

        # Get row bbox
        x0 = min(item["x"] for item in row)
        y0 = min(item["y"] for item in row)
        x1 = max(item["x_end"] for item in row)
        y1 = max(item["y_end"] for item in row)

        # Check overlap with any table region
        for t_bbox in table_regions:
            if (x0 >= t_bbox[0] - 10 and x1 <= t_bbox[2] + 10 and
                y0 >= t_bbox[1] - 10 and y1 <= t_bbox[3] + 10):
                return True

        return False

    def _detect_tables_with_pymupdf(self, page, page_num: int) -> List[ContentBlock]:
        """Detect tables using PyMuPDF's built-in find_tables()."""
        tables = []

        try:
            table_finder = page.find_tables()

            for table_obj in table_finder:
                table_data = table_obj.extract()
                bbox = table_obj.bbox

                if table_data:
                    tables.append(ContentBlock(
                        type=ContentType.TABLE,
                        content={"data": table_data},
                        bbox=bbox,
                        confidence=0.95,
                        page=page_num,
                        metadata={
                            "rows": len(table_data),
                            "cols": len(table_data[0]) if table_data else 0,
                            "method": "pymupdf_find_tables"
                        }
                    ))
        except Exception:
            pass

        return tables

    def _extract_text_items(self, blocks: List) -> List[Dict]:
        """Extrae items de texto con metadatos."""
        items = []

        for block in blocks:
            if "lines" not in block:
                continue

            for line in block["lines"]:
                for span in line["spans"]:
                    bbox = span["bbox"]
                    text = span["text"].strip()

                    if text:
                        items.append({
                            "text": text,
                            "x": bbox[0],
                            "y": bbox[1],
                            "x_end": bbox[2],
                            "y_end": bbox[3],
                            "bbox": bbox,
                            "font": span["font"],
                            "size": span["size"],
                            "flags": span["flags"],
                            "is_bold": bool(span["flags"] & 2**4),
                            "is_italic": bool(span["flags"] & 2**1),
                            "color": span.get("color", 0)
                        })

        return items

    def _extract_images(self, page) -> List[Dict]:
        """Extrae información de imágenes."""
        images = []
        image_list = page.get_images()

        for img_index, img in enumerate(image_list):
            # Obtener bbox de la imagen
            xref = img[0]
            try:
                bbox = page.get_image_bbox(xref)
                images.append({
                    "image_id": img_index,
                    "xref": xref,
                    "bbox": tuple(bbox),
                    "width": img[2],
                    "height": img[3]
                })
            except:
                pass

        return images

    def _extract_drawings(self, page) -> List[Dict]:
        """Extrae líneas y formas (pueden indicar tablas)."""
        drawings = []

        try:
            drawing_list = page.get_drawings()

            for draw in drawing_list:
                drawings.append({
                    "type": draw.get("type", "unknown"),
                    "bbox": draw["rect"],
                    "items": len(draw.get("items", []))
                })

        except:
            pass

        return drawings

    def _group_into_rows(self, items: List[Dict]) -> List[List[Dict]]:
        """Agrupa items en filas."""
        if not items:
            return []

        sorted_items = sorted(items, key=lambda x: x["y"])
        rows = []
        current_row = [sorted_items[0]]
        current_y = sorted_items[0]["y"]
        tolerance = 3.0

        for item in sorted_items[1:]:
            if abs(item["y"] - current_y) <= tolerance:
                current_row.append(item)
            else:
                current_row.sort(key=lambda x: x["x"])
                rows.append(current_row)
                current_row = [item]
                current_y = item["y"]

        if current_row:
            current_row.sort(key=lambda x: x["x"])
            rows.append(current_row)

        return rows

    def _classify_text_region(
        self,
        rows: List[List[Dict]],
        start_idx: int,
        page_num: int,
        skip_table_detection: bool = False
    ) -> Tuple[ContentType, Optional[ContentBlock], int]:
        """
        Clasifica una región de texto.

        Args:
            skip_table_detection: Si True, no detectar tablas manualmente (ya se detectaron con PyMuPDF)

        Returns:
            (tipo, content_block, next_index)
        """
        if start_idx >= len(rows):
            return ContentType.UNKNOWN, None, start_idx + 1

        current_row = rows[start_idx]

        # DETECTOR 1: Encabezado (título, sección)
        if self._is_heading(current_row):
            block = self._create_heading_block(current_row, page_num)
            return ContentType.HEADING, block, start_idx + 1

        # DETECTOR 2: Lista (bullets, numeración)
        if self._is_list_item(current_row):
            # Agrupar todos los items de lista consecutivos
            list_items, end_idx = self._extract_list(rows, start_idx)
            block = self._create_list_block(list_items, page_num)
            return ContentType.LIST, block, end_idx

        # DETECTOR 3: Tabla (múltiples columnas alineadas) - Skip if PyMuPDF already detected tables
        if not skip_table_detection and start_idx + 2 < len(rows):
            is_table, table_data, end_idx = self._detect_table(rows, start_idx)
            if is_table:
                block = self._create_table_block(table_data, page_num)
                return ContentType.TABLE, block, end_idx

        # DETECTOR 4: Párrafo (texto continuo)
        para_rows, end_idx = self._extract_paragraph(rows, start_idx)
        if para_rows:
            block = self._create_paragraph_block(para_rows, page_num)
            return ContentType.PARAGRAPH, block, end_idx

        # Si no se puede clasificar
        return ContentType.UNKNOWN, None, start_idx + 1

    def _is_heading(self, row: List[Dict]) -> bool:
        """Detecta si es un encabezado."""
        if not row:
            return False

        row_text = " ".join(item["text"] for item in row).strip()

        # Criterios:
        # 1. Texto corto (< 80 caracteres)
        # 2. Fuente más grande o negrita
        # 3. Patrones de encabezado (números, letras)

        if len(row_text) > 80:
            return False

        # Verificar si tiene fuente grande o negrita
        avg_size = sum(item["size"] for item in row) / len(row)
        has_bold = any(item["is_bold"] for item in row)

        if avg_size > 12 or has_bold:
            # Verificar patrones comunes
            if any(pattern in row_text.lower() for pattern in [
                "capítulo", "sección", "descripción", "análisis",
                "identificación", "conclusión"
            ]):
                return True

            # Numeración de sección (1., a., i., etc.)
            # Verificar si empieza con letra minúscula + punto (a. b. c. ... z.)
            if len(row_text) >= 2 and row_text[1] == ".":
                if row_text[0].islower() or row_text[0].isdigit():
                    return True

            # También verificar subsecciones (d.1, d.2, e.1, etc.)
            if len(row_text) >= 4 and "." in row_text[:4]:
                parts = row_text[:4].split(".")
                if len(parts) >= 2:
                    if parts[0].isalpha() and (parts[1].isdigit() or parts[1] == ""):
                        return True

        return False

    def _is_list_item(self, row: List[Dict]) -> bool:
        """Detecta si es un item de lista."""
        if not row:
            return False

        row_text = " ".join(item["text"] for item in row).strip()

        # Bullets reales (•, -, *, etc.)
        if row_text.startswith(("•", "-", "*", "○", "▪")):
            return True

        # Numeración con paréntesis: 1), a), i), etc.
        if len(row_text) > 2:
            if row_text[0].isdigit() and row_text[1] == ")":
                return True
            if row_text[0].isalpha() and row_text[1] == ")":
                return True

        # NO detectar marcadores de sección (a., b., f., etc.) como listas
        # Estos son HEADINGS de sección

        return False

    def _detect_table(
        self,
        rows: List[List[Dict]],
        start_idx: int
    ) -> Tuple[bool, Optional[Dict], int]:
        """
        Detecta si es una tabla usando múltiples heurísticas.

        Criterios para ser tabla:
        1. Al menos 2 columnas consistentes
        2. Al menos 3 filas con estructura similar
        3. Contenido mixto (texto + números)
        4. Alineación vertical de columnas
        """
        if start_idx + 2 >= len(rows):
            return False, None, start_idx + 1

        # Analizar 3-5 filas
        sample_size = min(5, len(rows) - start_idx)
        sample_rows = rows[start_idx:start_idx + sample_size]

        # CRITERIO 1: Detectar columnas
        columns = self._detect_columns_smart(sample_rows)

        if len(columns) < 2:
            return False, None, start_idx + 1

        # CRITERIO 2: Verificar consistencia de columnas
        consistency_score = self._measure_column_consistency(sample_rows, columns)

        if consistency_score < 0.6:  # Al menos 60% de consistencia
            return False, None, start_idx + 1

        # CRITERIO 3: Verificar contenido mixto (indica tabla de datos)
        has_mixed_content = self._has_mixed_content(sample_rows)

        # CRITERIO 4: Buscar marcadores de tabla ("Campo", "Valor", etc.)
        has_table_markers = self._has_table_markers(sample_rows)

        # Decidir si es tabla
        is_table = (
            (consistency_score > 0.7) or  # Alta consistencia
            (has_table_markers) or         # Tiene marcadores explícitos
            (consistency_score > 0.6 and has_mixed_content)  # Moderada + datos mixtos
        )

        if not is_table:
            return False, None, start_idx + 1

        # Encontrar final de la tabla
        end_idx = start_idx + sample_size
        empty_row_count = 0  # Track consecutive empty/non-matching rows

        while end_idx < len(rows):
            current_row = rows[end_idx]

            # Check if row is essentially empty (few items or short text)
            total_text = "".join([item.get("text", "") for item in current_row]).strip()
            is_empty_row = len(current_row) < 2 or len(total_text) < 5

            if self._row_fits_columns(current_row, columns, tolerance=0.7):
                end_idx += 1
                empty_row_count = 0  # Reset counter
            elif is_empty_row and empty_row_count < 2:
                # Allow up to 2 consecutive empty rows (might be spacing)
                end_idx += 1
                empty_row_count += 1
            else:
                break

        # Construir tabla
        table_rows = rows[start_idx:end_idx]
        table_data = self._build_table_data(table_rows, columns)

        return True, table_data, end_idx

    def _detect_columns_smart(self, rows: List[List[Dict]]) -> List[float]:
        """Detecta columnas usando clustering de posiciones X."""
        all_x = []
        for row in rows:
            for item in row:
                all_x.append(item["x"])

        if not all_x:
            return []

        # Clustering simple
        columns = []
        tolerance = 8.0

        for x in sorted(set(all_x)):
            is_new = True
            for col_x in columns:
                if abs(x - col_x) <= tolerance:
                    is_new = False
                    break
            if is_new:
                columns.append(x)

        return sorted(columns)

    def _measure_column_consistency(
        self,
        rows: List[List[Dict]],
        columns: List[float]
    ) -> float:
        """Mide qué tan consistente es la alineación de columnas."""
        if not rows or not columns:
            return 0.0

        total_items = 0
        aligned_items = 0

        for row in rows:
            for item in row:
                total_items += 1
                # Verificar si está cerca de alguna columna
                for col_x in columns:
                    if abs(item["x"] - col_x) <= 10:
                        aligned_items += 1
                        break

        return aligned_items / total_items if total_items > 0 else 0.0

    def _has_mixed_content(self, rows: List[List[Dict]]) -> bool:
        """Verifica si hay contenido mixto (texto + números)."""
        has_text = False
        has_numbers = False

        for row in rows:
            for item in row:
                text = item["text"]
                if any(c.isalpha() for c in text):
                    has_text = True
                if any(c.isdigit() for c in text):
                    has_numbers = True

                if has_text and has_numbers:
                    return True

        return False

    def _has_table_markers(self, rows: List[List[Dict]]) -> bool:
        """Busca marcadores comunes de tablas."""
        markers = [
            "campo", "valor", "descripción", "cantidad",
            "fecha", "hora", "nombre", "tipo", "rut"
        ]

        for row in rows[:2]:  # Solo primeras 2 filas
            row_text = " ".join(item["text"] for item in row).lower()
            if any(marker in row_text for marker in markers):
                return True

        return False

    def _row_fits_columns(
        self,
        row: List[Dict],
        columns: List[float],
        tolerance: float = 0.7
    ) -> bool:
        """Verifica si una fila encaja con las columnas."""
        if not row:
            return False

        matches = 0
        for item in row:
            for col_x in columns:
                if abs(item["x"] - col_x) <= 10:
                    matches += 1
                    break

        fit_ratio = matches / len(row) if row else 0
        return fit_ratio >= tolerance

    def _build_table_data(
        self,
        rows: List[List[Dict]],
        columns: List[float]
    ) -> Dict:
        """Construye datos estructurados de tabla."""
        table_matrix = []

        for row in rows:
            row_data = [""] * len(columns)

            for item in row:
                # Asignar a columna más cercana
                closest_col = None
                min_dist = float('inf')

                for i, col_x in enumerate(columns):
                    dist = abs(item["x"] - col_x)
                    if dist < min_dist and dist <= 10:
                        min_dist = dist
                        closest_col = i

                if closest_col is not None:
                    if row_data[closest_col]:
                        row_data[closest_col] += " " + item["text"]
                    else:
                        row_data[closest_col] = item["text"]

            table_matrix.append(row_data)

        # Calcular bbox
        all_items = [item for row in rows for item in row]
        bbox = self._calculate_bbox(all_items)

        return {
            "columns": columns,
            "data": table_matrix,
            "bbox": bbox,
            "row_count": len(table_matrix),
            "col_count": len(columns)
        }

    def _extract_paragraph(
        self,
        rows: List[List[Dict]],
        start_idx: int
    ) -> Tuple[List[List[Dict]], int]:
        """Extrae un párrafo completo."""
        para_rows = []
        i = start_idx

        prev_x = None
        prev_y_end = None

        while i < len(rows):
            row = rows[i]

            if not row:
                break

            row_text = " ".join(item["text"] for item in row)

            # Filtrar líneas muy cortas o marcadores
            if len(row_text) < 10 or row_text.strip() in ["a.", "b.", "c.", "d."]:
                break

            # Verificar continuidad
            row_x = min(item["x"] for item in row)
            row_y = min(item["y"] for item in row)
            row_y_end = max(item["y_end"] for item in row)

            if para_rows:
                x_diff = abs(row_x - prev_x)
                y_gap = row_y - prev_y_end

                # Si cambia mucho el margen o hay gap grande, terminar
                if x_diff > 15 or y_gap > 20:
                    break

            para_rows.append(row)
            prev_x = row_x
            prev_y_end = row_y_end
            i += 1

        # Verificar longitud mínima
        if para_rows:
            total_text = " ".join(
                " ".join(item["text"] for item in row)
                for row in para_rows
            )

            if len(total_text) < 50:
                return [], start_idx + 1

        return para_rows, i

    def _extract_list(
        self,
        rows: List[List[Dict]],
        start_idx: int
    ) -> Tuple[List[List[Dict]], int]:
        """Extrae items de lista consecutivos."""
        list_items = []
        i = start_idx

        while i < len(rows):
            if self._is_list_item(rows[i]):
                list_items.append(rows[i])
                i += 1
            else:
                break

        return list_items, i

    def _calculate_bbox(self, items: List[Dict]) -> Tuple[float, float, float, float]:
        """Calcula bounding box."""
        if not items:
            return (0, 0, 0, 0)

        return (
            min(item["x"] for item in items),
            min(item["y"] for item in items),
            max(item["x_end"] for item in items),
            max(item["y_end"] for item in items)
        )

    def _create_heading_block(self, row: List[Dict], page_num: int) -> ContentBlock:
        """Crea bloque de encabezado."""
        text = " ".join(item["text"] for item in row)
        bbox = self._calculate_bbox(row)

        return ContentBlock(
            type=ContentType.HEADING,
            content={"text": text},
            bbox=bbox,
            confidence=0.85,
            page=page_num,
            metadata={"font_size": row[0]["size"] if row else 0}
        )

    def _create_list_block(self, list_rows: List[List[Dict]], page_num: int) -> ContentBlock:
        """Crea bloque de lista."""
        items = []
        all_items = []

        for row in list_rows:
            text = " ".join(item["text"] for item in row)
            items.append(text)
            all_items.extend(row)

        bbox = self._calculate_bbox(all_items)

        return ContentBlock(
            type=ContentType.LIST,
            content={"items": items},
            bbox=bbox,
            confidence=0.90,
            page=page_num,
            metadata={"item_count": len(items)}
        )

    def _create_table_block(self, table_data: Dict, page_num: int) -> ContentBlock:
        """Crea bloque de tabla."""
        return ContentBlock(
            type=ContentType.TABLE,
            content=table_data,
            bbox=table_data["bbox"],
            confidence=0.90,
            page=page_num,
            metadata={
                "rows": table_data["row_count"],
                "cols": table_data["col_count"]
            }
        )

    def _create_paragraph_block(self, para_rows: List[List[Dict]], page_num: int) -> ContentBlock:
        """Crea bloque de párrafo."""
        all_items = []
        texts = []

        for row in para_rows:
            texts.append(" ".join(item["text"] for item in row))
            all_items.extend(row)

        full_text = " ".join(texts)
        bbox = self._calculate_bbox(all_items)

        return ContentBlock(
            type=ContentType.PARAGRAPH,
            content={"text": full_text},
            bbox=bbox,
            confidence=0.85,
            page=page_num,
            metadata={"char_count": len(full_text), "line_count": len(para_rows)}
        )


def main():
    """Demo del clasificador."""
    print("🔍 CLASIFICADOR INTELIGENTE DE CONTENIDO")
    print("=" * 70)

    pdf_path = Path(__file__).parent.parent.parent.parent / "shared" / "source" / "EAF-089-2025.pdf"

    if not pdf_path.exists():
        print(f"❌ PDF no encontrado: {pdf_path}")
        return

    classifier = SmartContentClassifier(str(pdf_path))

    # Analizar páginas 1-3
    for page_num in [1, 2, 3]:
        print(f"\n{'=' * 70}")
        blocks = classifier.classify_page_content(page_num)

        print(f"\n📊 Página {page_num}: {len(blocks)} bloques detectados")
        print("-" * 70)

        type_counts = {}
        for block in blocks:
            type_name = block.type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1

        for content_type, count in sorted(type_counts.items()):
            icon = {"table": "📊", "paragraph": "📝", "heading": "📌",
                   "list": "📋", "image": "🖼️"}.get(content_type, "❓")
            print(f"   {icon} {content_type}: {count}")

    print(f"\n{'=' * 70}")
    print("✅ Análisis completado")


if __name__ == "__main__":
    main()