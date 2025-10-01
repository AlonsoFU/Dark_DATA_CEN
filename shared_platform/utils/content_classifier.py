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
    HEADING = "heading"
    LIST = "list"
    UNKNOWN = "unknown"


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
        table_detection_threshold: float = 0.7
    ):
        """
        Initialize classifier.

        Args:
            pdf_path: Path to PDF file
            use_ocr: Enable OCR for scanned documents (requires Tesseract)
            ocr_language: Tesseract language codes (default: Spanish + English)
            table_detection_threshold: Minimum confidence for table detection (0-1)
        """
        self.pdf_path = Path(pdf_path)
        self.use_ocr = use_ocr
        self.ocr_language = ocr_language
        self.table_threshold = table_detection_threshold

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

        # Classify text regions (excluding text inside tables)
        i = 0
        while i < len(rows):
            block = self._classify_text_region(rows, i, page_num, drawings)

            if block:
                # Check if this block is inside a table region
                if not self._is_inside_any_table(block.bbox, table_bboxes):
                    content_blocks.append(block)
                # else: skip this block as it's already part of a table

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
                ContentType.HEADING.value: 0,
                ContentType.LIST.value: 0,
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
        image_list = page.get_images()

        for img_index, img in enumerate(image_list):
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
        drawings: List[Dict]
    ) -> Optional[ContentBlock]:
        """Classify a text region starting from start_idx."""
        if start_idx >= len(rows):
            return None

        current_row = rows[start_idx]
        text = " ".join([item["text"] for item in current_row])

        # Calculate bbox for this row
        x0 = min(item["x"] for item in current_row)
        y0 = min(item["y"] for item in current_row)
        x1 = max(item["x_end"] for item in current_row)
        y1 = max(item["y_end"] for item in current_row)
        bbox = (x0, y0, x1, y1)

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

        # Check for heading (check BEFORE grouping multi-line paragraphs)
        if self._is_heading(text, current_row):
            return ContentBlock(
                type=ContentType.HEADING.value,
                content={"text": text, "level": self._detect_heading_level(text, current_row)},
                bbox=bbox,
                confidence=0.9,
                page=page_num,
                metadata={"end_row_index": start_idx + 1, "style": "detected_heading"}
            )

        # Check for list item
        if self._is_list_item(text):
            return ContentBlock(
                type=ContentType.LIST.value,
                content={"text": text, "marker": self._extract_list_marker(text)},
                bbox=bbox,
                confidence=0.88,
                page=page_num,
                metadata={"end_row_index": start_idx + 1, "list_type": "detected"}
            )

        # Check for table (multi-row analysis)
        table_block = self._detect_table_region(rows, start_idx, drawings)
        if table_block:
            table_block.page = page_num
            return table_block

        # Default: text paragraph
        # Look ahead to group multi-line paragraphs
        end_idx = self._find_paragraph_end(rows, start_idx)
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
        for pattern in self.formula_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        # Check for high ratio of special characters
        special_chars = len(re.findall(r"[+\-*/=<>∫∑∏√]", text))
        if len(text) > 0 and special_chars / len(text) > 0.2:
            return True

        return False

    def _is_heading(self, text: str, items: List[Dict]) -> bool:
        """Check if text is a heading."""
        # Pattern matching
        for pattern in self.heading_keywords:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        # Font size analysis (headings usually larger)
        if items:
            avg_size = sum(item["size"] for item in items) / len(items)
            if avg_size > 14:  # Typical heading threshold
                return True

        # Bold and short text
        is_bold = all(item.get("is_bold", False) for item in items)
        is_short = len(text.split()) <= 10

        if is_bold and is_short:
            return True

        # Check for centered text (likely headings/titles)
        if items and self._is_centered_text(items):
            return True

        # Check for quoted text at top of document (document subtitles)
        # Handle both regular quotes and smart quotes
        has_quotes = (
            (text.startswith('"') and text.endswith('"')) or  # Regular quotes
            (text.startswith(chr(8220)) and text.endswith(chr(8221))) or  # Smart quotes
            (text.startswith('«') and text.endswith('»'))  # Guillemets
        )
        if has_quotes:
            # If it's in upper portion of page, likely a subtitle
            if items and items[0]["y"] < 150:  # Top 150 points of page
                return True

        # Check for document structure patterns (numbered sections)
        if re.match(r'^[a-z]\.\s+[A-Z]', text):  # "a. Something" pattern
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

    def _find_paragraph_end(self, rows: List[List[Dict]], start_idx: int) -> int:
        """Find where paragraph ends (continuous text)."""
        end_idx = start_idx

        for i in range(start_idx + 1, min(start_idx + 10, len(rows))):
            # Check if next row is likely continuation
            current_text = " ".join([item["text"] for item in rows[i - 1]])
            next_text = " ".join([item["text"] for item in rows[i]])

            # Stop if next row looks like heading, list, or table
            if self._is_heading(next_text, rows[i]) or self._is_list_item(next_text):
                break

            # Continue if similar x-position (same column)
            current_x = rows[i - 1][0]["x"] if rows[i - 1] else 0
            next_x = rows[i][0]["x"] if rows[i] else 0

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