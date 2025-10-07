"""
Universal PDF Content Classifier
=================================

General-purpose classifier for identifying content types in PDF documents:
- Text paragraphs
- Tables (structured data)
- Formulas/Equations
- Images/Graphics
- Headings/Titles
- Lists (bulleted/numbered)

Uses PyMuPDF for layout analysis and optional Tesseract OCR for scanned documents.

Usage:
    from shared_platform.utils.content_classifier import ContentClassifier

    classifier = ContentClassifier(pdf_path="document.pdf")
    results = classifier.classify_page(page_num=1)

    for block in results:
        print(f"Type: {block['type']}, Confidence: {block['confidence']}")
"""

import fitz  # PyMuPDF
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum


class ContentType(Enum):
    """Standard content types found in documents."""
    TEXT = "text"
    TABLE = "table"
    FORMULA = "formula"
    IMAGE = "image"
    METADATA = "metadata"


@dataclass
class ContentBlock:
    """Represents a classified content block."""
    type: str  # ContentType as string
    content: Union[str, Dict]
    bbox: Tuple[float, float, float, float]  # (x0, y0, x1, y1)
    confidence: float
    page: int
    metadata: Dict

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "type": self.type,
            "content": self.content,
            "bbox": self.bbox,
            "confidence": self.confidence,
            "page": self.page,
            "metadata": self.metadata
        }


class ContentClassifier:
    """
    Universal PDF content classifier using layout analysis and pattern recognition.

    Features:
    - Multi-strategy detection (layout + text patterns + visual features)
    - OCR support for scanned documents
    - Table detection with alignment analysis
    - Formula detection with mathematical notation
    - Confidence scoring for each classification
    """

    def __init__(
        self,
        pdf_path: str,
        use_ocr: bool = False,
        ocr_language: str = "spa+eng",
        table_detection_threshold: float = 0.7,
        detect_vector_graphics: bool = True
    ):
        """
        Initialize classifier.

        Args:
            pdf_path: Path to PDF file
            use_ocr: Enable OCR for scanned documents (requires Tesseract)
            ocr_language: Tesseract language codes (default: Spanish + English)
            table_detection_threshold: Minimum confidence for table detection (0-1)
            detect_vector_graphics: Detect charts/diagrams as images (slower but more complete)
        """
        self.pdf_path = Path(pdf_path)
        self.use_ocr = use_ocr
        self.ocr_language = ocr_language
        self.table_threshold = table_detection_threshold
        self.detect_vector_graphics = detect_vector_graphics

        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        self.pdf_doc = fitz.open(str(self.pdf_path))

        # Table detection patterns
        self.table_indicators = {
            "has_grid_lines": 0.4,
            "has_aligned_columns": 0.3,
            "has_numeric_data": 0.2,
            "has_tabular_keywords": 0.1
        }

        # Formula patterns (mathematical notation)
        self.formula_patterns = [
            r"[∫∑∏√∂∇]",  # Mathematical operators
            r"[α-ωΑ-Ω]",  # Greek letters
            r"\d+\s*[±×÷≈≠≤≥]",  # Math operators with numbers
            r"\^|\{|\}|_\{",  # LaTeX-like notation
            r"=\s*\d+",  # Equations
        ]

        # Heading indicators
        self.heading_keywords = [
            r"^capítulo\s+\d+",
            r"^sección\s+\d+",
            r"^\d+\.(\d+\.)*\s+[A-Z]",  # Numbered headings
            r"^(introducción|conclusión|resumen|abstract)",
        ]

        # List patterns
        self.list_patterns = [
            r"^[•\-\*]\s+",  # Bullet points
            r"^\d+\.\s+",  # Numbered lists
            r"^[a-z]\)\s+",  # Lettered lists
        ]

    def classify_page(self, page_num: int) -> List[ContentBlock]:
        """
        Classify all content on a page.

        Args:
            page_num: Page number (1-indexed)

        Returns:
            List of classified content blocks
        """
        if page_num < 1 or page_num > len(self.pdf_doc):
            raise ValueError(f"Invalid page number: {page_num}")

        page = self.pdf_doc[page_num - 1]

        # Extract page elements
        if self.use_ocr:
            text_dict = page.get_textpage_ocr(language=self.ocr_language).extractDICT()
        else:
            text_dict = page.get_text("dict")

        # Get images
        images = self._extract_images(page)

        # Get drawing elements (lines, rectangles - table indicators)
        drawings = self._extract_drawings(page)

        # Get text items with coordinates
        text_items = self._extract_text_items(text_dict.get("blocks", []))

        # Group text into rows
        rows = self._group_into_rows(text_items)

        # Detect tables using PyMuPDF's built-in detector
        tables = self._detect_tables_with_pymupdf(page)

        # Classify content blocks
        content_blocks = []

        # Add images first
        for img in images:
            content_blocks.append(ContentBlock(
                type=ContentType.IMAGE.value,
                content=img,
                bbox=img["bbox"],
                confidence=1.0,
                page=page_num,
                metadata={
                    "width": img.get("width", 0),
                    "height": img.get("height", 0),
                    "extraction_method": "pymupdf_image_list"
                }
            ))

        # Add detected tables
        table_bboxes = []  # Keep track of table regions
        for table in tables:
            table_bbox = table["bbox"]
            table_bboxes.append(table_bbox)
            content_blocks.append(ContentBlock(
                type=ContentType.TABLE.value,
                content=table["data"],
                bbox=table_bbox,
                confidence=table["confidence"],
                page=page_num,
                metadata={
                    "rows": table.get("rows", 0),
                    "cols": table.get("cols", 0),
                    "extraction_method": "pymupdf_find_tables"
                }
            ))

        # Detect vector graphics (charts, diagrams) FIRST before classifying text
        # This way we can exclude text that's part of the graphic
        image_bboxes = [img["bbox"] for img in images]  # Start with embedded images

        if self.detect_vector_graphics:
            existing_bboxes = [b.bbox for b in content_blocks]  # Tables so far
            # Pass text rows as well to calculate real page occupancy
            vector_images = self._detect_vector_graphics(page, existing_bboxes, rows)
            content_blocks.extend(vector_images)
            # Add vector image bboxes to exclusion list
            image_bboxes.extend([vi.bbox for vi in vector_images])

        # Classify text regions (excluding text inside tables AND images)
        i = 0
        while i < len(rows):
            # Check if this row is inside a table or image BEFORE processing
            current_row = rows[i]
            x0 = min(item["x"] for item in current_row)
            y0 = min(item["y"] for item in current_row)
            x1 = max(item["x_end"] for item in current_row)
            y1 = max(item["y_end"] for item in current_row)
            row_bbox = (x0, y0, x1, y1)

            # Skip if inside table
            if self._is_inside_any_table(row_bbox, table_bboxes):
                i += 1
                continue

            # Skip if inside image/graphic
            if self._is_inside_any_image(row_bbox, image_bboxes):
                i += 1
                continue

            block = self._classify_text_region(rows, i, page_num, drawings, table_bboxes)

            if block:
                content_blocks.append(block)
                i = block.metadata.get("end_row_index", i + 1)
            else:
                i += 1

        return content_blocks

    def classify_document(self, start_page: int = 1, end_page: Optional[int] = None) -> Dict:
        """
        Classify entire document or page range.

        Args:
            start_page: Starting page (1-indexed)
            end_page: Ending page (1-indexed), None = last page

        Returns:
            Dictionary with classified content and statistics
        """
        if end_page is None:
            end_page = len(self.pdf_doc)

        results = {
            "document_path": str(self.pdf_path),
            "total_pages": end_page - start_page + 1,
            "pages": {},
            "statistics": {
                ContentType.TEXT.value: 0,
                ContentType.TABLE.value: 0,
                ContentType.FORMULA.value: 0,
                ContentType.IMAGE.value: 0,
                ContentType.METADATA.value: 0,
            }
        }

        for page_num in range(start_page, end_page + 1):
            blocks = self.classify_page(page_num)

            results["pages"][page_num] = {
                "page_number": page_num,
                "blocks": [block.to_dict() for block in blocks],
                "block_count": len(blocks)
            }

            # Update statistics
            for block in blocks:
                if block.type in results["statistics"]:
                    results["statistics"][block.type] += 1

        return results

    def _extract_text_items(self, blocks: List[Dict]) -> List[Dict]:
        """Extract text items with coordinates and formatting."""
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
                            "width": bbox[2] - bbox[0],
                            "height": bbox[3] - bbox[1],
                            "font": span.get("font", ""),
                            "size": span.get("size", 0),
                            "flags": span.get("flags", 0),
                            "is_bold": bool(span.get("flags", 0) & 2**4),
                            "is_italic": bool(span.get("flags", 0) & 2**1),
                            "color": span.get("color", 0)
                        })

        return items

    def _extract_images(self, page) -> List[Dict]:
        """Extract image information from page."""
        images = []

        # Método robusto: obtener imágenes con bboxes buscando en el diccionario de la página
        image_list = page.get_images(full=True)

        if not image_list:
            return images

        # Obtener información de imágenes desde el diccionario de página
        try:
            for img_index, img in enumerate(image_list):
                xref = img[0]
                name = img[7] if len(img) > 7 else None

                # Buscar la imagen en el contenido de la página por nombre
                if name:
                    # Buscar todas las referencias a esta imagen en la página
                    img_rects = page.get_image_rects(name)
                    if img_rects:
                        for rect in img_rects:
                            images.append({
                                "image_id": img_index,
                                "xref": xref,
                                "bbox": tuple(rect),
                                "width": img[2],
                                "height": img[3]
                            })
        except Exception:
            pass

        return images

    def _extract_drawings(self, page) -> List[Dict]:
        """Extract drawing elements (lines, rectangles - table indicators)."""
        drawings = []

        try:
            drawing_list = page.get_drawings()

            for draw in drawing_list:
                drawings.append({
                    "type": draw.get("type", "unknown"),
                    "bbox": draw.get("rect", (0, 0, 0, 0)),
                    "items": len(draw.get("items", []))
                })
        except Exception:
            pass

        return drawings

    def _detect_tables_with_pymupdf(self, page) -> List[Dict]:
        """Detect tables using PyMuPDF's built-in table finder."""
        tables = []

        try:
            # PyMuPDF table detection
            table_finder = page.find_tables()

            for table_obj in table_finder:
                table_data = table_obj.extract()
                bbox = table_obj.bbox

                if table_data:
                    tables.append({
                        "bbox": bbox,
                        "data": table_data,
                        "rows": len(table_data),
                        "cols": len(table_data[0]) if table_data else 0,
                        "confidence": 0.9  # High confidence for PyMuPDF detection
                    })
        except Exception:
            pass

        return tables

    def _group_into_rows(self, items: List[Dict], tolerance: float = 3.0) -> List[List[Dict]]:
        """Group text items into horizontal rows."""
        if not items:
            return []

        sorted_items = sorted(items, key=lambda x: x["y"])
        rows = []
        current_row = [sorted_items[0]]
        current_y = sorted_items[0]["y"]

        for item in sorted_items[1:]:
            if abs(item["y"] - current_y) <= tolerance:
                current_row.append(item)
            else:
                # Sort row by x-coordinate
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
        drawings: List[Dict],
        table_bboxes: List[Tuple] = None
    ) -> Optional[ContentBlock]:
        """Classify a text region starting from start_idx."""
        if start_idx >= len(rows):
            return None

        if table_bboxes is None:
            table_bboxes = []

        current_row = rows[start_idx]
        text = " ".join([item["text"] for item in current_row])

        # Calculate bbox for this row
        x0 = min(item["x"] for item in current_row)
        y0 = min(item["y"] for item in current_row)
        x1 = max(item["x_end"] for item in current_row)
        y1 = max(item["y_end"] for item in current_row)
        bbox = (x0, y0, x1, y1)

        # Check for page number/metadata (e.g., "Página 10 de 399")
        if self._is_page_number(text):
            return ContentBlock(
                type=ContentType.METADATA.value,
                content={"text": text, "type": "page_number"},
                bbox=bbox,
                confidence=0.95,
                page=page_num,
                metadata={"end_row_index": start_idx + 1, "pattern": "page_number"}
            )

        # Check for formula
        if self._is_formula(text, current_row):
            return ContentBlock(
                type=ContentType.FORMULA.value,
                content={"text": text, "latex": self._extract_latex_notation(text)},
                bbox=bbox,
                confidence=0.85,
                page=page_num,
                metadata={"end_row_index": start_idx + 1, "pattern": "mathematical_notation"}
            )

        # Default: text paragraph
        # Look ahead to group multi-line paragraphs
        end_idx = self._find_paragraph_end(rows, start_idx, table_bboxes)
        paragraph_text = []

        for i in range(start_idx, end_idx + 1):
            row_text = " ".join([item["text"] for item in rows[i]])
            paragraph_text.append(row_text)

        # Recalculate bbox for entire paragraph
        all_items = [item for i in range(start_idx, end_idx + 1) for item in rows[i]]
        if all_items:
            x0 = min(item["x"] for item in all_items)
            y0 = min(item["y"] for item in all_items)
            x1 = max(item["x_end"] for item in all_items)
            y1 = max(item["y_end"] for item in all_items)
            bbox = (x0, y0, x1, y1)

        return ContentBlock(
            type=ContentType.TEXT.value,
            content={"text": " ".join(paragraph_text)},
            bbox=bbox,
            confidence=0.95,
            page=page_num,
            metadata={
                "end_row_index": end_idx + 1,
                "line_count": end_idx - start_idx + 1,
                "char_count": len(" ".join(paragraph_text))
            }
        )

    def _is_formula(self, text: str, items: List[Dict]) -> bool:
        """Check if text contains mathematical formula."""
        # Solo detectar fórmulas matemáticas reales, no texto con símbolos
        # Una fórmula debe tener símbolos matemáticos avanzados (integral, sumatorias, etc.)
        # o patrones muy específicos de ecuaciones

        # Símbolos matemáticos avanzados
        advanced_math_symbols = r"[∫∑∏√∂∇±×÷≈≠≤≥∞∈∉⊂⊃∪∩]"
        if re.search(advanced_math_symbols, text):
            return True

        # Patrón de ecuación matemática pura: variable = expresión con paréntesis/exponentes
        # Ejemplo: "f(x) = x^2 + 2x + 1" o "E = mc^2"
        if re.match(r'^[a-zA-Z]\([a-zA-Z]+\)\s*=\s*.+', text):
            return True
        if re.search(r'\^[0-9]', text):  # exponentes como x^2
            return True

        # NO detectar texto descriptivo con símbolos (como "I+II+III = X")
        return False

    def _is_page_number(self, text: str) -> bool:
        """Detect page numbers and metadata patterns."""
        # Pattern: "Página X de Y" or "Page X of Y"
        if re.match(r'^P[aá]gina\s+\d+\s+de\s+\d+', text, re.IGNORECASE):
            return True
        if re.match(r'^Page\s+\d+\s+of\s+\d+', text, re.IGNORECASE):
            return True
        # Pattern: just numbers at bottom/top of page
        if re.match(r'^\d+$', text.strip()) and len(text.strip()) <= 4:
            return True
        return False

    def _is_heading(self, text: str, items: List[Dict]) -> bool:
        """
        Conservative heading detection - only strong patterns.
        """

        # FILTER OUT: Table totals/labels and "Total Con..."
        if re.match(r'^Total\s', text, re.IGNORECASE):
            return False
        if re.match(r'^Subtotal\s', text, re.IGNORECASE):
            return False

        # FILTER OUT: Quoted text (document titles, NOT headings)
        if text.startswith('"') or text.startswith(chr(8220)):
            return False

        # PATTERN 1: Enumerations (ONLY THESE are reliable headings)
        # Letter enumerations: "a. Text", "e. Text"
        if re.match(r'^[a-z][\.)]\s+\w', text, re.IGNORECASE):
            return True

        # Numeric enumerations: "1. Text", "2. Text"
        if re.match(r'^\d{1,2}[\.)]\s+\w', text):
            return True

        # Complex enumerations: "d.4 Text", "1.1 Text"
        if re.match(r'^[a-z]\.\d+\s+\w', text, re.IGNORECASE):
            return True
        if re.match(r'^\d+\.\d+\s+\w', text):
            return True

        # PATTERN 2: Text ending with colon (ONLY if short AND starts with capital)
        if text.rstrip().endswith(':') and len(text.split()) <= 5 and text[0].isupper():
            # Reject if it's lowercase start (likely continuation)
            return True

        # PATTERN 3: Very large font (MUST be >16, not 14)
        if items:
            avg_size = sum(item["size"] for item in items) / len(items)
            if avg_size > 16:
                return True

        return False

    def _is_list_item(self, text: str) -> bool:
        """Check if text is a list item."""
        for pattern in self.list_patterns:
            if re.match(pattern, text):
                return True
        return False

    def _detect_table_region(
        self,
        rows: List[List[Dict]],
        start_idx: int,
        drawings: List[Dict]
    ) -> Optional[ContentBlock]:
        """Detect table by analyzing alignment and structure."""
        # Need at least 3 rows for table
        if start_idx + 2 >= len(rows):
            return None

        # Analyze next 5 rows for table patterns
        analyze_rows = rows[start_idx:min(start_idx + 5, len(rows))]

        # Check column alignment
        column_alignment = self._check_column_alignment(analyze_rows)

        if column_alignment < self.table_threshold:
            return None

        # Find table extent
        end_idx = self._find_table_end(rows, start_idx, column_alignment)
        table_rows = rows[start_idx:end_idx + 1]

        # Extract table data
        table_data = []
        for row in table_rows:
            row_text = [item["text"] for item in row]
            table_data.append(row_text)

        # Calculate bbox
        all_items = [item for row in table_rows for item in row]
        x0 = min(item["x"] for item in all_items)
        y0 = min(item["y"] for item in all_items)
        x1 = max(item["x_end"] for item in all_items)
        y1 = max(item["y_end"] for item in all_items)

        return ContentBlock(
            type=ContentType.TABLE.value,
            content={"data": table_data},
            bbox=(x0, y0, x1, y1),
            confidence=column_alignment,
            page=0,  # Will be set by caller
            metadata={
                "end_row_index": end_idx + 1,
                "rows": len(table_data),
                "cols": max(len(row) for row in table_data) if table_data else 0,
                "detection_method": "alignment_analysis"
            }
        )

    def _check_column_alignment(self, rows: List[List[Dict]]) -> float:
        """Check if rows have aligned columns (table indicator)."""
        if len(rows) < 2:
            return 0.0

        # Collect x-coordinates
        x_coords = []
        for row in rows:
            for item in row:
                x_coords.append(item["x"])

        if len(x_coords) < 4:
            return 0.0

        # Group similar x-coordinates (columns)
        tolerance = 5.0
        x_coords.sort()
        columns = []
        current_col = [x_coords[0]]

        for x in x_coords[1:]:
            if x - current_col[-1] <= tolerance:
                current_col.append(x)
            else:
                columns.append(current_col)
                current_col = [x]

        if current_col:
            columns.append(current_col)

        # Table needs at least 2 columns with multiple items each
        substantial_columns = [col for col in columns if len(col) >= len(rows)]

        if len(substantial_columns) >= 2:
            return min(0.95, 0.5 + (len(substantial_columns) * 0.1))

        return 0.0

    def _find_table_end(self, rows: List[List[Dict]], start_idx: int, alignment: float) -> int:
        """Find where table ends."""
        end_idx = start_idx

        for i in range(start_idx + 1, len(rows)):
            test_rows = rows[start_idx:i + 1]
            test_alignment = self._check_column_alignment(test_rows)

            if test_alignment >= self.table_threshold:
                end_idx = i
            else:
                break

        return end_idx

    def _find_paragraph_end(self, rows: List[List[Dict]], start_idx: int, table_bboxes: List[Tuple] = None) -> int:
        """Find where paragraph ends (continuous text)."""
        if table_bboxes is None:
            table_bboxes = []

        end_idx = start_idx

        for i in range(start_idx + 1, min(start_idx + 10, len(rows))):
            # Check if next row is inside a table - if so, stop here
            next_row = rows[i]
            x0 = min(item["x"] for item in next_row)
            y0 = min(item["y"] for item in next_row)
            x1 = max(item["x_end"] for item in next_row)
            y1 = max(item["y_end"] for item in next_row)
            next_bbox = (x0, y0, x1, y1)

            if self._is_inside_any_table(next_bbox, table_bboxes):
                break

            # Check if next row is likely continuation
            current_text = " ".join([item["text"] for item in rows[i - 1]])
            next_text = " ".join([item["text"] for item in next_row])

            # Stop if next row is page number/metadata
            if self._is_page_number(next_text):
                break

            # Check vertical spacing - if there's a large gap, it's a new block
            current_row = rows[i - 1]
            current_y_end = max(item["y_end"] for item in current_row)
            next_y_start = min(item["y"] for item in next_row)
            vertical_gap = next_y_start - current_y_end

            # If vertical gap is more than 12 points, it's a separate block
            if vertical_gap > 12:
                break

            # Also break if next text looks like a section header (a., b., 1., 2., etc.)
            if re.match(r'^[a-z][\.)]\s+\w', next_text, re.IGNORECASE):
                break
            if re.match(r'^\d{1,2}[\.)]\s+\w', next_text):
                break

            # Continue if similar x-position (same column)
            current_x = rows[i - 1][0]["x"] if rows[i - 1] else 0
            next_x = next_row[0]["x"] if next_row else 0

            if abs(current_x - next_x) < 20:
                end_idx = i
            else:
                break

        return end_idx

    def _detect_heading_level(self, text: str, items: List[Dict]) -> int:
        """Detect heading level (1-6)."""
        if items:
            avg_size = sum(item["size"] for item in items) / len(items)

            if avg_size > 20:
                return 1
            elif avg_size > 16:
                return 2
            elif avg_size > 14:
                return 3
            else:
                return 4

        return 3

    def _extract_list_marker(self, text: str) -> str:
        """Extract list marker from text."""
        match = re.match(r"^([•\-\*\d+\.\w+\)])\s+", text)
        if match:
            return match.group(1)
        return ""

    def _extract_latex_notation(self, text: str) -> str:
        """Extract potential LaTeX notation from formula."""
        # This is a simplified version - could be enhanced
        return text

    def _is_centered_text(self, items: List[Dict]) -> bool:
        """
        Check if text is centered on the page.

        Args:
            items: List of text items

        Returns:
            True if text appears to be centered
        """
        if not items:
            return False

        # Get leftmost and rightmost x coordinates
        min_x = min(item["x"] for item in items)
        max_x = max(item["x_end"] for item in items)

        # Typical page width for A4 is ~595 points
        page_width = 595
        page_center = page_width / 2

        # Calculate text center
        text_center = (min_x + max_x) / 2

        # Check if text is within 50 points of page center
        # and has significant margins on both sides
        is_near_center = abs(text_center - page_center) < 50
        has_left_margin = min_x > 80
        has_right_margin = max_x < (page_width - 80)

        return is_near_center and has_left_margin and has_right_margin

    def _is_inside_any_image(self, bbox: Tuple[float, float, float, float], image_bboxes: List[Tuple]) -> bool:
        """
        Check if a bounding box is inside any image region.

        Args:
            bbox: Bounding box to check (x0, y0, x1, y1)
            image_bboxes: List of image bounding boxes

        Returns:
            True if bbox is inside or significantly overlaps with any image
        """
        x0, y0, x1, y1 = bbox
        block_area = (x1 - x0) * (y1 - y0)

        if block_area <= 0:
            return False

        for img_bbox in image_bboxes:
            ix0, iy0, ix1, iy1 = img_bbox

            # Check if bbox is inside image bbox
            if x0 >= ix0 and y0 >= iy0 and x1 <= ix1 and y1 <= iy1:
                return True

            # Also check for significant overlap (>50%)
            overlap_x0 = max(x0, ix0)
            overlap_y0 = max(y0, iy0)
            overlap_x1 = min(x1, ix1)
            overlap_y1 = min(y1, iy1)

            if overlap_x0 < overlap_x1 and overlap_y0 < overlap_y1:
                overlap_area = (overlap_x1 - overlap_x0) * (overlap_y1 - overlap_y0)
                if overlap_area / block_area > 0.5:
                    return True

        return False

    def _is_inside_any_table(self, bbox: Tuple[float, float, float, float], table_bboxes: List[Tuple]) -> bool:
        """
        Check if a bounding box is inside any table region.

        Args:
            bbox: Bounding box to check (x0, y0, x1, y1)
            table_bboxes: List of table bounding boxes

        Returns:
            True if bbox is inside or significantly overlaps with any table
        """
        x0, y0, x1, y1 = bbox
        block_area = (x1 - x0) * (y1 - y0)

        if block_area <= 0:
            return False

        for table_bbox in table_bboxes:
            tx0, ty0, tx1, ty1 = table_bbox

            # Calculate intersection
            ix0 = max(x0, tx0)
            iy0 = max(y0, ty0)
            ix1 = min(x1, tx1)
            iy1 = min(y1, ty1)

            # Check if there's an intersection
            if ix0 < ix1 and iy0 < iy1:
                intersection_area = (ix1 - ix0) * (iy1 - iy0)
                overlap_ratio = intersection_area / block_area

                # If more than 70% of the block is inside the table, consider it part of the table
                if overlap_ratio > 0.7:
                    return True

        return False

    def _detect_vector_graphics(self, page, existing_bboxes: List[Tuple], text_rows: List[List[Dict]] = None) -> List[ContentBlock]:
        """Detect visual content (charts, diagrams) - FAST version using empty space detection."""
        vector_images = []

        try:
            page_rect = page.rect
            grid_size = 100  # Grilla para detectar espacios vacíos

            # PASO 1: Verificar si hay suficiente espacio vacío (RÁPIDO - sin llamar get_drawings)
            total_cells_x = int(page_rect.width // grid_size) + 1
            total_cells_y = int(page_rect.height // grid_size) + 1
            occupied_cells = set()

            # Marcar celdas ocupadas por contenido existente (tablas, imágenes)
            for bbox in existing_bboxes:
                x0, y0, x1, y1 = bbox
                min_cell_x = int(x0 // grid_size)
                min_cell_y = int(y0 // grid_size)
                max_cell_x = int(x1 // grid_size)
                max_cell_y = int(y1 // grid_size)

                for cx in range(min_cell_x, max_cell_x + 1):
                    for cy in range(min_cell_y, max_cell_y + 1):
                        occupied_cells.add((cx, cy))

            # TAMBIÉN marcar celdas ocupadas por TEXTO (para calcular ocupación real)
            if text_rows:
                for row in text_rows:
                    if row:
                        x0 = min(item["x"] for item in row)
                        y0 = min(item["y"] for item in row)
                        x1 = max(item["x_end"] for item in row)
                        y1 = max(item["y_end"] for item in row)

                        min_cell_x = int(x0 // grid_size)
                        min_cell_y = int(y0 // grid_size)
                        max_cell_x = int(x1 // grid_size)
                        max_cell_y = int(y1 // grid_size)

                        for cx in range(min_cell_x, max_cell_x + 1):
                            for cy in range(min_cell_y, max_cell_y + 1):
                                occupied_cells.add((cx, cy))

            # Verificar ratio de espacio vacío
            total_cells = total_cells_x * total_cells_y
            occupied_ratio = len(occupied_cells) / total_cells if total_cells > 0 else 0

            # Si más del 50% de la página está ocupada por tablas/imágenes, NO hay gráficos (salir rápido)
            # Esto evita llamar get_drawings() en páginas con muchas tablas
            if occupied_ratio > 0.50:
                return vector_images

            # PASO 2: AHORA SÍ llamar get_drawings() (solo si hay espacio vacío significativo)
            paths = page.get_drawings()

            # Filtrar paths dentro de contenido existente
            paths_outside = 0
            for path in paths:
                rect = path.get('rect')
                if rect and rect.width > 0.5 and rect.height > 0.5:
                    center_x = (rect.x0 + rect.x1) / 2
                    center_y = (rect.y0 + rect.y1) / 2

                    is_inside = False
                    for ex0, ey0, ex1, ey1 in existing_bboxes:
                        if ex0 <= center_x <= ex1 and ey0 <= center_y <= ey1:
                            is_inside = True
                            break

                    if not is_inside:
                        paths_outside += 1

            # Requiere MUCHOS paths fuera de tablas para considerar gráfico
            if paths_outside < 500:
                return vector_images

            # PASO 3: Crear grilla de paths (solo los que están fuera)
            grid_size = 50  # Grilla más fina para precisión
            path_cells = set()

            for path in paths:
                rect = path.get('rect')
                if rect and rect.width > 0.5 and rect.height > 0.5:
                    center_x = (rect.x0 + rect.x1) / 2
                    center_y = (rect.y0 + rect.y1) / 2

                    # Skip if inside existing
                    is_inside = False
                    for ex0, ey0, ex1, ey1 in existing_bboxes:
                        if ex0 <= center_x <= ex1 and ey0 <= center_y <= ey1:
                            is_inside = True
                            break

                    if is_inside:
                        continue

                    # Marcar celdas
                    min_cell_x = int(rect.x0 // grid_size)
                    min_cell_y = int(rect.y0 // grid_size)
                    max_cell_x = int(rect.x1 // grid_size)
                    max_cell_y = int(rect.y1 // grid_size)

                    for cx in range(min_cell_x, max_cell_x + 1):
                        for cy in range(min_cell_y, max_cell_y + 1):
                            path_cells.add((cx, cy))

            # Agrupar en clusters
            if len(path_cells) >= 20:
                clusters = self._cluster_cells(path_cells)

                for cluster_cells in clusters:
                    if len(cluster_cells) < 20:
                        continue

                    # Calcular bbox preciso
                    actual_min_x, actual_min_y = float('inf'), float('inf')
                    actual_max_x, actual_max_y = 0, 0
                    paths_in_cluster = 0

                    for path in paths:
                        rect = path.get('rect')
                        if rect:
                            cell_x = int(rect.x0 // grid_size)
                            cell_y = int(rect.y0 // grid_size)
                            if (cell_x, cell_y) in cluster_cells:
                                actual_min_x = min(actual_min_x, rect.x0)
                                actual_min_y = min(actual_min_y, rect.y0)
                                actual_max_x = max(actual_max_x, rect.x1)
                                actual_max_y = max(actual_max_y, rect.y1)
                                paths_in_cluster += 1

                    # Mínimo 50 paths en el cluster
                    if paths_in_cluster < 50:
                        continue

                    # Crear bbox con margen
                    margin = 30
                    bbox = (
                        max(0, actual_min_x - margin),
                        max(0, actual_min_y - margin),
                        min(page_rect.width, actual_max_x + margin),
                        min(page_rect.height, actual_max_y + margin)
                    )

                    width = bbox[2] - bbox[0]
                    height = bbox[3] - bbox[1]

                    if width > 200 and height > 150:
                        vector_images.append(ContentBlock(
                            type=ContentType.IMAGE.value,
                            content={"type": "visual_region"},
                            bbox=bbox,
                            confidence=0.80,
                            page=page.number + 1,
                            metadata={
                                "extraction_method": "empty_space_then_paths",
                                "path_count": paths_in_cluster,
                                "grid_cells": len(cluster_cells)
                            }
                        ))

        except Exception:
            pass

        return vector_images

    def _cluster_cells(self, cells: set) -> List[set]:
        """Agrupar celdas adyacentes en clusters."""
        if not cells:
            return []

        visited = set()
        clusters = []

        for cell in cells:
            if cell in visited:
                continue

            # BFS para encontrar todas las celdas conectadas
            cluster = set()
            queue = [cell]
            visited.add(cell)

            while queue:
                cx, cy = queue.pop(0)
                cluster.add((cx, cy))

                # Verificar 8 vecinos
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        neighbor = (cx + dx, cy + dy)
                        if neighbor in cells and neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)

            if len(cluster) >= 4:  # Mínimo 4 celdas para un gráfico
                clusters.append(cluster)

        return clusters

    def _cluster_rects(self, rects: List, min_cluster_size: int = 20) -> List:
        """Group rectangles into clusters using grid-based approach (faster)."""
        import fitz
        from collections import defaultdict

        if not rects:
            return []

        # Use grid-based clustering for speed (O(n) instead of O(n²))
        # Divide page into 50x50 pixel cells
        cell_size = 50
        grid = defaultdict(list)

        # Assign each rect to grid cells it overlaps
        for i, rect in enumerate(rects):
            min_cell_x = int(rect.x0 // cell_size)
            min_cell_y = int(rect.y0 // cell_size)
            max_cell_x = int(rect.x1 // cell_size)
            max_cell_y = int(rect.y1 // cell_size)

            for cx in range(min_cell_x, max_cell_x + 1):
                for cy in range(min_cell_y, max_cell_y + 1):
                    grid[(cx, cy)].append(i)

        # Find connected components in grid
        visited_cells = set()
        clusters = []

        for cell_key in grid.keys():
            if cell_key in visited_cells:
                continue

            # BFS to find all connected cells
            queue = [cell_key]
            visited_cells.add(cell_key)
            cluster_indices = set(grid[cell_key])
            cluster_rect = None

            while queue:
                cx, cy = queue.pop(0)

                # Check 8 neighbors
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        neighbor = (cx + dx, cy + dy)
                        if neighbor in grid and neighbor not in visited_cells:
                            visited_cells.add(neighbor)
                            queue.append(neighbor)
                            cluster_indices.update(grid[neighbor])

            # Build cluster rect from all indices
            if len(cluster_indices) >= min_cluster_size:
                for idx in cluster_indices:
                    if cluster_rect is None:
                        cluster_rect = fitz.Rect(rects[idx])
                    else:
                        cluster_rect.include_rect(rects[idx])

                if cluster_rect:
                    clusters.append(cluster_rect)

        return clusters

    def _boxes_overlap_significantly(self, bbox1: Tuple, bbox2: Tuple, threshold: float = 0.5) -> bool:
        """Check if two bboxes overlap significantly."""
        x0_1, y0_1, x1_1, y1_1 = bbox1
        x0_2, y0_2, x1_2, y1_2 = bbox2

        # Calculate intersection
        ix0 = max(x0_1, x0_2)
        iy0 = max(y0_1, y0_2)
        ix1 = min(x1_1, x1_2)
        iy1 = min(y1_1, y1_2)

        if ix0 >= ix1 or iy0 >= iy1:
            return False

        intersection_area = (ix1 - ix0) * (iy1 - iy0)
        bbox1_area = (x1_1 - x0_1) * (y1_1 - y0_1)

        if bbox1_area == 0:
            return False

        overlap_ratio = intersection_area / bbox1_area
        return overlap_ratio > threshold

    def close(self):
        """Close PDF document."""
        if self.pdf_doc:
            self.pdf_doc.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Convenience function
def classify_pdf(
    pdf_path: str,
    page_num: Optional[int] = None,
    use_ocr: bool = False
) -> Union[List[ContentBlock], Dict]:
    """
    Quick classification function.

    Args:
        pdf_path: Path to PDF
        page_num: Specific page to classify (None = entire document)
        use_ocr: Enable OCR

    Returns:
        List of ContentBlock if page_num specified, else full document dict
    """
    with ContentClassifier(pdf_path, use_ocr=use_ocr) as classifier:
        if page_num:
            return classifier.classify_page(page_num)
        else:
            return classifier.classify_document()