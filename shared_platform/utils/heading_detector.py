"""
Hierarchical Heading Detector for PDF Documents
================================================

Universal detector for generating table of contents from any PDF document.
Uses multi-strategy approach combining:
- Typographic features (font size, bold, style)
- Positional features (alignment, spacing)
- Text patterns (numbering, keywords)
- Scoring system for confidence

Based on research:
- Detect-Order-Construct (2024) - hierarchical structure
- Supervised learning approaches with 95%+ accuracy
- PyMuPDF font property analysis

Usage:
    from shared_platform.utils.heading_detector import HeadingDetector

    detector = HeadingDetector(pdf_path="document.pdf")
    toc = detector.generate_toc()

    for entry in toc:
        print(f"{'  ' * entry['level']}{entry['text']}")
"""

import fitz  # PyMuPDF
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import Counter


@dataclass
class HeadingCandidate:
    """Represents a potential heading."""
    text: str
    page: int
    bbox: Tuple[float, float, float, float]
    font_size: float
    is_bold: bool
    is_italic: bool
    is_uppercase: bool
    is_centered: bool
    has_numbering: bool
    numbering_pattern: Optional[str]
    vertical_gap_before: float
    vertical_gap_after: float
    score: float
    level: int = 0

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "text": self.text,
            "page": self.page,
            "bbox": self.bbox,
            "font_size": self.font_size,
            "is_bold": self.is_bold,
            "is_uppercase": self.is_uppercase,
            "is_centered": self.is_centered,
            "has_numbering": self.has_numbering,
            "numbering_pattern": self.numbering_pattern,
            "score": self.score,
            "level": self.level
        }


class HeadingDetector:
    """
    Universal heading detector for generating table of contents.

    Multi-strategy approach:
    1. Font analysis (size, weight, style)
    2. Position analysis (alignment, spacing)
    3. Pattern matching (numbering, keywords)
    4. Confidence scoring
    5. Hierarchical level detection
    """

    def __init__(
        self,
        pdf_path: str,
        min_heading_score: float = 15.0,
        detect_unnumbered: bool = True,
        language: str = "es"
    ):
        """
        Initialize heading detector.

        Args:
            pdf_path: Path to PDF file
            min_heading_score: Minimum score to consider as heading (default: 15.0)
            detect_unnumbered: Detect headings without numbering (default: True)
            language: Document language for keyword matching (es/en)
        """
        self.pdf_path = Path(pdf_path)
        self.min_heading_score = min_heading_score
        self.detect_unnumbered = detect_unnumbered
        self.language = language

        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        self.pdf_doc = fitz.open(str(self.pdf_path))

        # Heading keywords by language
        self.heading_keywords = {
            "es": [
                r"^capítulo\s+\d+",
                r"^sección\s+\d+",
                r"^anexo\s+n?º?\s*\d+",
                r"^parte\s+\d+",
                r"^título\s+\d+",
                r"^introducción$",
                r"^conclusión$",
                r"^resumen$",
                r"^abstract$",
                r"^índice$",
                r"^referencias$",
                r"^bibliografía$",
                r"^apéndice",
                r"otros\s+antecedentes\s+relevantes",
                r"^otros\s+antecedentes",
                r"antecedentes\s+relevantes",
            ],
            "en": [
                r"^chapter\s+\d+",
                r"^section\s+\d+",
                r"^appendix\s+[a-z]",
                r"^part\s+\d+",
                r"^introduction$",
                r"^conclusion$",
                r"^abstract$",
                r"^references$",
                r"^bibliography$",
                r"^index$",
            ]
        }

        # Numbering patterns (ordered by specificity)
        # IMPORTANTE: El orden importa - patrones más específicos primero
        self.numbering_patterns = [
            # Complex hierarchical: "1.1.1", "A.1.2", "a.1.1"
            (r"^([A-Z]|\d+)(\.\d+){2,}\s*", "hierarchical_complex"),
            # Letter + number hierarchical: "d.1", "e.2", "f.3" (space optional)
            # These are always titles when they start with a letter
            (r"^[A-Za-z]\.\d+(?:\s|$)", "hierarchical_letter"),
            # Number + number hierarchical: "7.2 Text", "1.1 Something"
            # DEBE tener texto alfabético después (no solo números o tiempos)
            # Evita "94.64 15:16" pero permite "7.2 Apertura"
            (r"^\d+\.\d+\s+[A-Za-z]", "hierarchical_number"),
            # Simple numbered: "1.", "2.", "3."
            # SOLO punto (.), NO paréntesis - los paréntesis son típicamente listas
            # NO debe ser seguido por más dígitos (para no capturar "7" de "7.2")
            (r"^\d+\.(?!\d)\s*", "numbered"),
            # Roman numerals: "I.", "II.", "III."
            (r"^[IVX]+[\.\)]\s*", "roman"),
            # Letter enumeration: "a.", "b.", "c." (lowercase only for subtitles)
            # SOLO punto (.), NO paréntesis - los paréntesis son típicamente listas
            # Uppercase letters (A., B., H.) are typically table headers/columns
            # Space is optional to handle "a." alone on a line
            (r"^[a-z]\.(?:\s|$)", "letter"),
        ]

        # Will be populated during analysis
        self.body_font_size = None
        self.common_fonts = None

    def generate_toc(
        self,
        start_page: int = 1,
        end_page: Optional[int] = None,
        return_raw_candidates: bool = False
    ) -> List[Dict]:
        """
        Generate table of contents for document.

        Args:
            start_page: Starting page (1-indexed)
            end_page: Ending page (1-indexed), None = last page
            return_raw_candidates: Return all candidates with scores (for debugging)

        Returns:
            List of heading entries with hierarchical structure
        """
        if end_page is None:
            end_page = len(self.pdf_doc)

        # Step 1: Learn document typography (body font size, common fonts)
        self._learn_document_typography(start_page, end_page)

        # Step 2: Extract heading candidates from all pages
        candidates = []
        for page_num in range(start_page, end_page + 1):
            page_candidates = self._extract_heading_candidates(page_num)
            candidates.extend(page_candidates)

        if return_raw_candidates:
            return [c.to_dict() for c in candidates]

        # Step 3: Filter by minimum score
        headings = [c for c in candidates if c.score >= self.min_heading_score]

        # Step 3.5: Filter repetitive table content and data
        # Count text frequency across all headings
        text_counts = {}
        for h in headings:
            text_counts[h.text] = text_counts.get(h.text, 0) + 1

        # Remove texts that appear more than 1 time (table headers/data repeat)
        # Real titles are unique
        headings = [h for h in headings if text_counts[h.text] == 1]

        # Step 3.6: Simple filters for obvious non-titles
        filtered_headings = []
        for h in headings:
            # Skip obvious table content
            if re.match(r'^\d{1,2}:\d{2}', h.text):  # Starts with time
                continue
            if re.match(r'^\d{1,2}[-/]\d{1,2}[-/]\d{2,4}', h.text):  # Starts with date
                continue
            if h.text.rstrip().endswith('/'):  # Ends with / (table header)
                continue

            filtered_headings.append(h)

        headings = filtered_headings

        # Step 4: Assign hierarchical levels
        headings = self._assign_hierarchical_levels(headings)

        # Step 5: Format as table of contents
        toc = []
        for heading in headings:
            toc.append({
                "text": heading.text,
                "page": heading.page,
                "level": heading.level,
                "score": round(heading.score, 2),
                "numbering": heading.numbering_pattern,
                "bbox": heading.bbox
            })

        return toc

    def _learn_document_typography(self, start_page: int, end_page: int):
        """
        Learn common typography patterns in document.
        Identifies most common body font size and font families.
        """
        font_sizes = []
        font_names = []

        # Sample first 5 pages to learn typography
        sample_pages = min(5, end_page - start_page + 1)

        for page_num in range(start_page, start_page + sample_pages):
            page = self.pdf_doc[page_num - 1]
            text_dict = page.get_text("dict")

            for block in text_dict.get("blocks", []):
                if "lines" not in block:
                    continue

                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text and len(text) > 3:  # Skip very short text
                            font_sizes.append(span["size"])
                            font_names.append(span["font"])

        # Find most common font size (body text)
        if font_sizes:
            size_counter = Counter(font_sizes)
            # Most common size is likely body text
            self.body_font_size = size_counter.most_common(1)[0][0]
        else:
            self.body_font_size = 11.0  # Default

        # Find common fonts
        if font_names:
            font_counter = Counter(font_names)
            self.common_fonts = [f[0] for f in font_counter.most_common(3)]
        else:
            self.common_fonts = []

    def _extract_heading_candidates(self, page_num: int) -> List[HeadingCandidate]:
        """Extract potential headings from a page."""
        page = self.pdf_doc[page_num - 1]
        text_dict = page.get_text("dict")

        candidates = []
        blocks = text_dict.get("blocks", [])

        for block_idx, block in enumerate(blocks):
            if "lines" not in block:
                continue

            # ENFOQUE: Procesar línea por línea para detectar títulos
            # Esto es crucial porque bloques pueden contener múltiples líneas
            # donde solo UNA es un título (ej: "nota... b. Sistema de Transmisión")

            lines_to_process = []

            for line in block["lines"]:
                line_text_parts = []
                line_items = []
                for span in line["spans"]:
                    text = span["text"].strip()
                    if text:
                        line_text_parts.append(text)
                        line_items.append({
                            "text": text,
                            "bbox": span["bbox"],
                            "font": span["font"],
                            "size": span["size"],
                            "flags": span.get("flags", 0),
                            "color": span.get("color", 0)
                        })

                if line_text_parts:
                    line_full_text = " ".join(line_text_parts).strip()
                    lines_to_process.append({
                        "text": line_full_text,
                        "items": line_items,
                        "bbox": line.get("bbox", [0, 0, 0, 0])
                    })

            # COMBINAR líneas cortas con numeración con la siguiente línea
            # Ejemplo: "a." en una línea + "Fecha y Hora..." en la siguiente
            combined_lines = []
            i = 0
            while i < len(lines_to_process):
                current = lines_to_process[i]

                # Si la línea es corta (< 5 chars) Y tiene numeración válida
                if len(current["text"]) < 5:
                    # Verificar si tiene numeración
                    has_num, _ = self._detect_numbering(current["text"])

                    if has_num and i + 1 < len(lines_to_process):
                        # Combinar con la siguiente línea
                        next_line = lines_to_process[i + 1]
                        combined_text = current["text"] + " " + next_line["text"]
                        combined_items = current["items"] + next_line["items"]

                        # Usar bbox de la primera línea (la que tiene numeración)
                        combined_lines.append({
                            "text": combined_text,
                            "items": combined_items,
                            "bbox": current["bbox"]
                        })
                        i += 2  # Saltar la siguiente línea
                        continue

                # Si no se combinó, agregar normalmente
                combined_lines.append(current)
                i += 1

            # Procesar cada línea del bloque como candidato potencial
            for line_data in combined_lines:
                full_text = line_data["text"]
                block_items_data = line_data["items"]
                bbox = line_data["bbox"]

                # FILTROS BÁSICOS
                if len(full_text) < 5:
                    continue

                if self._is_page_metadata(full_text):
                    continue

                # Excluir contenido de tablas y datos (crítico)
                if self._is_table_or_data_content(full_text):
                    continue

                # Excluir líneas que son solo valores numéricos + unidades
                # Ejemplos: "11066.23 MW", "50297.9 MWh", "49.5 Hz, -0.9 Hz/s"
                if re.match(r'^\d+\.?\d*\s*(MW|MWh|kV|Hz|GW|kW)', full_text, re.IGNORECASE):
                    continue
                if re.match(r'^\d+\.?\d+\s+Hz[,\s]', full_text):  # Frequency data
                    continue

                # Excluir contenido de tablas por estructura bbox (crítico)
                if self._is_table_content(bbox, blocks, block_idx):
                    continue

                # FILTRO DE LONGITUD: Títulos son conceptos (cortos), no descripciones largas
                # Excluir textos muy largos (>100 chars) a menos que sean capítulos principales
                if len(full_text) > 100:
                    # Permitir solo si empieza con numeración de capítulo principal (1., 2., 3., etc.)
                    if not re.match(r'^\d+[\.\)]\s+', full_text):
                        continue

                # Calculate features
                avg_font_size = sum(item["size"] for item in block_items_data) / len(block_items_data)
                is_bold = any(bool(item["flags"] & 2**4) for item in block_items_data)
                is_italic = any(bool(item["flags"] & 2**1) for item in block_items_data)
                is_underline = any(bool(item["flags"] & 2**0) for item in block_items_data)  # Underline detection
                is_uppercase = full_text.isupper() and len(full_text) > 3
                is_centered = self._is_centered(bbox, page.rect.width)

                # Check numbering
                has_numbering, numbering_pattern = self._detect_numbering(full_text)

                # Calculate vertical gaps
                gap_before = self._get_vertical_gap_before(blocks, block_idx)
                gap_after = self._get_vertical_gap_after(blocks, block_idx)

                # Calculate score
                score = self._calculate_heading_score(
                    text=full_text,
                    font_size=avg_font_size,
                    is_bold=is_bold,
                    is_underline=is_underline,
                    is_uppercase=is_uppercase,
                    is_centered=is_centered,
                    has_numbering=has_numbering,
                    gap_before=gap_before,
                    gap_after=gap_after
                )

                # Check if this is document metadata (level 0)
                is_metadata = self._is_document_metadata(full_text, page_num)
                if is_metadata:
                    # Boost score for metadata and mark as level 0
                    score += 5.0

                candidate = HeadingCandidate(
                    text=full_text,
                    page=page_num,
                    bbox=bbox,
                    font_size=avg_font_size,
                    is_bold=is_bold,
                    is_italic=is_italic,
                    is_uppercase=is_uppercase,
                    is_centered=is_centered,
                    has_numbering=has_numbering,
                    numbering_pattern=numbering_pattern,
                    vertical_gap_before=gap_before,
                    vertical_gap_after=gap_after,
                    score=score,
                    level=0 if is_metadata else 0  # Will be set later
                )

                candidates.append(candidate)

        return candidates

    def _is_document_metadata(self, text: str, page: int) -> bool:
        """
        Check if text is document metadata (title, date, etc.).
        These should be level 0 (above all sections).
        """
        # Only on first page
        if page != 1:
            return False

        # Document title patterns
        if re.search(r'estudio\s+para\s+an[aá]lisis\s+de\s+falla', text, re.IGNORECASE):
            return True
        if re.search(r'EAF\s+\d+/\d{4}', text):
            return True

        # Date patterns
        if re.match(r'^Fecha\s+de\s+(Emisi[oó]n|Publicaci[oó]n):', text, re.IGNORECASE):
            return True

        # Quoted document titles
        if text.startswith('"') and len(text) > 20:
            return True

        return False

    def _calculate_heading_score(
        self,
        text: str,
        font_size: float,
        is_bold: bool,
        is_underline: bool,
        is_uppercase: bool,
        is_centered: bool,
        has_numbering: bool,
        gap_before: float,
        gap_after: float
    ) -> float:
        """
        Calculate heading confidence score.

        Based on research: base score = font_size, then add bonuses.
        Higher score = more likely to be heading.
        """
        score = font_size  # Base score

        # Font style bonuses
        if is_bold:
            score += 3.0

        if is_uppercase:
            score += 2.0

        # Numbering bonus (strong indicator)
        if has_numbering:
            score += 3.0

        # Position bonuses
        if is_centered:
            score += 2.0

        # REGLA SIMPLE: SOLO 1 CONDICIÓN
        # DEBE TENER NUMERACIÓN (1., a., 7.2, etc.) → ES TÍTULO
        # NADA MÁS. Centrado solo NO es suficiente. Negrita sola NO es título.

        # ÚNICAMENTE textos con numeración son títulos
        if has_numbering:
            return 20.0  # Numerado → título

        # SIN numeración → NO es título (aunque esté centrado, en negrita, etc.)
        return 0.0

    def _detect_numbering(self, text: str) -> Tuple[bool, Optional[str]]:
        """Detect if text has numbering pattern."""
        for pattern, pattern_name in self.numbering_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return True, pattern_name

        return False, None

    def _matches_heading_keyword(self, text: str) -> bool:
        """Check if text matches heading keywords."""
        keywords = self.heading_keywords.get(self.language, [])

        for pattern in keywords:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    def _is_table_content(self, bbox: tuple, all_blocks: list, current_idx: int) -> bool:
        """
        Detect if a block is part of a table based on bounding boxes.

        Tables have:
        - Multiple blocks (3+) horizontally aligned (same y-coordinate) = table row
        - Small width blocks repeatedly at same x-position = table columns
        - Regular grid patterns
        """
        x0, y0, x1, y1 = bbox
        block_width = x1 - x0
        block_height = y1 - y0

        # Check for horizontally aligned blocks (same row)
        aligned_count = 0
        for i, other_block in enumerate(all_blocks):
            if i == current_idx or "bbox" not in other_block:
                continue

            other_bbox = other_block["bbox"]
            other_y0 = other_bbox[1]
            other_y1 = other_bbox[3]

            # Same vertical position (±8 pixels tolerance)
            if abs(y0 - other_y0) < 8 and abs(y1 - other_y1) < 8:
                aligned_count += 1

        # Need at least 2 blocks aligned horizontally to suggest table row
        if aligned_count >= 2:
            # But check if there are rows below (confirms it's a table)
            rows_below = 0
            for i, other_block in enumerate(all_blocks):
                if i <= current_idx or "bbox" not in other_block:
                    continue

                other_bbox = other_block["bbox"]
                other_y0 = other_bbox[1]

                # Block below current one
                if other_y0 > y1 + 5:
                    # Check if aligned with current block's x-position
                    if abs(other_bbox[0] - x0) < 10:
                        rows_below += 1

            # If 3+ rows below at same x → this is table
            if rows_below >= 3:
                return True

        # Also check: 4+ blocks aligned = definite table row
        if aligned_count >= 4:
            return True

        # Check for vertical column pattern: same x-position repeated
        # BUT: Ignore common document margins and indentations
        # Common margins: ~56-72 (left), ~92-96 (first indent), ~128-132 (second indent)
        common_margins = [
            (50, 80),    # Left margin
            (88, 100),   # First indent level
            (120, 140),  # Second indent level
        ]

        is_common_margin = any(start <= x0 <= end for start, end in common_margins)

        if not is_common_margin:
            same_x_count = 0
            for i, other_block in enumerate(all_blocks):
                if i == current_idx or "bbox" not in other_block:
                    continue

                other_bbox = other_block["bbox"]
                other_x0 = other_bbox[0]

                # Same x-position (±5 pixels) = column alignment
                if abs(x0 - other_x0) < 5:
                    same_x_count += 1

            # If 6+ blocks at same x-position (not left margin) → table column
            if same_x_count >= 6:
                return True

        return False

    def _is_page_metadata(self, text: str) -> bool:
        """Check if text is page number or metadata."""
        # Page numbers
        if re.match(r'^P[aá]gina\s+\d+', text, re.IGNORECASE):
            return True
        if re.match(r'^\d+$', text.strip()) and len(text.strip()) <= 4:
            return True

        return False

    def _is_table_or_data_content(self, text: str) -> bool:
        """
        Check if text is table/data content, not a structural heading.

        Table content indicators:
        - Contains "informe(s) en plazo" or "informe(s) fuera de plazo"
        - Contains "no recibido por el CEN"
        - Company legal suffixes: S.A., SPA, Ltda, S.p.A.
        - Multiple company names in one line
        - Lists of substations (S/E ...)
        - Generation plant tables: PFV/TER/PE/HP + numbers + times
        """
        text_lower = text.lower()

        # Informe status patterns (very common in tables)
        if re.search(r'\d+\s+informe?s?\s+(en|fuera de)\s+plazo', text_lower):
            return True
        if 'no recibido por el cen' in text_lower:
            return True

        # Company legal suffixes (multiple in same line = table row)
        company_suffix_count = len(re.findall(r'\b(S\.A\.|SPA|S\.p\.A\.|Ltda\.?)', text, re.IGNORECASE))
        if company_suffix_count >= 2:
            return True

        # Multiple S/E (substations) = list/table
        if text.count('S/E') >= 2:
            return True

        # Generation plant tables: starts with plant type + has time pattern
        # Examples: "PFV Valle Escondido 1, 2, 3, 4, 5, 6, 7 y 8 71 15:20 16:28"
        if re.match(r'^(PFV|TER|PE|HP|PMG)\s+', text, re.IGNORECASE):
            # Check if has time pattern (HH:MM) or capacity numbers
            if re.search(r'\d{1,2}:\d{2}', text):  # Time pattern
                return True
            # Or has numbers followed by asterisk (NI marker)
            if re.search(r'\d+\.\d+\s+\d{2}:\d{2}', text):  # capacity + time
                return True
            if text.strip().endswith('*') or ' NI' in text:  # Data markers
                return True

        # Transmission line tables: "Línea 2x500 kV ..." with time patterns
        if re.match(r'^L[ií]nea\s+', text, re.IGNORECASE):
            if re.search(r'\d{1,2}:\d{2}', text):  # Has time
                return True

        # Total/summary rows in tables
        if re.match(r'^Total:\s+\d+', text, re.IGNORECASE):
            return True

        # Data rows with time patterns (HH:MM HH:MM or HH:MM followed by *)
        # But NOT if it's just a time reference in narrative text
        if re.search(r'\d{1,2}:\d{2}\s+\d{1,2}:\d{2}', text):  # Two times = data row
            return True
        if re.search(r'\d{1,2}:\d{2}\s+\*\s*$', text):  # Time + asterisk at end
            return True

        # ENS/Energy data tables: "name / code COMPANY type num num num num"
        # Pattern: text "/" text "COMPANY_TYPE" "Regulado/Libre" multiple_numbers
        # Example: "Nueva Imperial Carahue / E6 FRONTEL Regulado 2.91 3.12 3.12 9.08"
        # Also: "Cemento Melón NI MELON Libre 15.00 8.35 8.35 125.25" (with NI instead of /)
        if re.search(r'\s+(Regulado|Libre)\s+', text, re.IGNORECASE):
            # Check if ends with multiple numbers (3+ numbers at end)
            if re.search(r'(\d+\.\d+\s+){2,}\d+\.\d+\s*$', text):
                return True

        # Percentage summary rows: "Primer 80 %", "Último 20 %", "100 % Total"
        if re.search(r'^\s*(Primer|[ÚU]ltimo|\d+\s*%)', text, re.IGNORECASE):
            if re.search(r'\d+\.\d+', text):  # Has decimal numbers
                return True

        # Annexure references (not titles, but content pointers)
        if re.match(r'^En Anexo N[oº°]\d+\s+se\s+adjunta', text, re.IGNORECASE):
            return True

        # Chronology/log entries: "Company HH:MM Description" or "Name Time event"
        # Examples: "Codelco 08:54 Se cierra...", "Spence 11:09 Se energiza..."
        # Also: "C. CTM-3 inicia...", "C. CTM3 TG+TV disponible..."
        if re.search(r'^[A-Z][a-zA-Z\s]+\d{1,2}:\d{2}\s+', text):
            return True
        if re.search(r'^[A-Z]\.\s+[A-Z][a-zA-Z0-9\-\+\s]+\s+(inicia|disponible|energiza|cancelado)', text, re.IGNORECASE):
            return True

        # Chronology entries that start with numbering: "1. CDC instruye...", "2. CDC informa..."
        # These are event descriptions in chronology tables, NOT structural titles
        # Pattern: number/letter + period + space + action verbs
        if re.search(r'^(\d+|[a-z])[\.\)]\s+(CDC|Enel|AES|Colb[uú]n|Gener|Coordinador|STM|Minera)\s+(instruye|indica|informa|consulta|reporta|señala)', text, re.IGNORECASE):
            return True

        # Event log entries starting with location/company and event description
        # Example: "Sarco Desconexión del PE Sarco sin información..."
        if re.search(r'^[A-Z][a-zA-Z]+\s+(Desconexión|Conexión|Apertura|Cierre)', text, re.IGNORECASE):
            return True

        # Narrative references: "Company indica lo siguiente en su Informe..."
        # Also: "Según se detalla en el título 7.2 del presente informe..."
        if re.search(r'(indica|informa|señala)\s+lo\s+siguiente', text, re.IGNORECASE):
            return True
        if re.search(r'(del|en el|según)\s+(presente|mismo)\s+informe', text, re.IGNORECASE):
            return True
        if re.search(r'según\s+se\s+detalla\s+en', text, re.IGNORECASE):
            return True

        # Years as standalone numbers: "2024.", "2025." (table cells)
        if re.match(r'^(19|20)\d{2}[\.\)]?\s*$', text):
            return True

        # Company names with initials: "E. E. Puente Alto", "S. E. Antofagasta"
        # Pattern: single capital letter, period, space, single capital letter, period
        if re.match(r'^[A-Z]\.\s+[A-Z]\.\s+[A-Z]', text):
            return True

        # Incomplete fragments (very short text without proper structure)
        # Example: "sur de dichas SS/EE"
        if len(text) < 30 and not re.match(r'^[a-z][\.\)]\s+', text, re.IGNORECASE):
            # If short and doesn't start with letter numbering (a., b., etc.)
            # and doesn't start with digit numbering (1., 2., etc.)
            if not re.match(r'^\d+[\.\)]\s+', text):
                # Likely a fragment if it's all lowercase start or has connecting words
                if text.split()[0].islower() or text.startswith(('de ', 'en ', 'con ', 'por ')):
                    return True

        return False

    def _is_centered(self, bbox: Tuple, page_width: float) -> bool:
        """Check if text is centered on page."""
        x0, y0, x1, y1 = bbox
        text_center = (x0 + x1) / 2
        page_center = page_width / 2

        # Must be VERY close to center (within 20 points)
        # Titles are truly centered, not just "somewhat centered"
        is_near_center = abs(text_center - page_center) < 20

        # Has margins on both sides
        has_margins = x0 > 60 and x1 < (page_width - 60)

        return is_near_center and has_margins

    def _get_vertical_gap_before(self, blocks: List, block_idx: int) -> float:
        """Get vertical spacing before this block."""
        if block_idx == 0:
            return 0.0

        current_block = blocks[block_idx]
        prev_block = blocks[block_idx - 1]

        if "bbox" not in current_block or "bbox" not in prev_block:
            return 0.0

        current_y = current_block["bbox"][1]  # y0
        prev_y = prev_block["bbox"][3]  # y1

        return max(0.0, current_y - prev_y)

    def _get_vertical_gap_after(self, blocks: List, block_idx: int) -> float:
        """Get vertical spacing after this block."""
        if block_idx >= len(blocks) - 1:
            return 0.0

        current_block = blocks[block_idx]
        next_block = blocks[block_idx + 1]

        if "bbox" not in current_block or "bbox" not in next_block:
            return 0.0

        current_y = current_block["bbox"][3]  # y1
        next_y = next_block["bbox"][1]  # y0

        return max(0.0, next_y - current_y)

    def _assign_hierarchical_levels(self, headings: List[HeadingCandidate]) -> List[HeadingCandidate]:
        """
        Assign hierarchical levels to headings.

        Strategy:
        1. Group by numbering pattern (1. -> 1.1 -> 1.1.1)
        2. Use font size (larger = higher level)
        3. Use position (earlier in doc = potentially higher)
        4. Detect sub-items under chapters (e.g., items after "4." are level 4)
        """
        if not headings:
            return headings

        # Track the current hierarchical context
        # Rule: Maintain current level until a superior level appears
        current_context_level = None

        # Extract numbering for level detection
        for heading in headings:
            # Check if already marked as metadata (level 0)
            if self._is_document_metadata(heading.text, heading.page):
                heading.level = 0
                continue

            # Detect level from numbering pattern
            detected_level = self._detect_level_from_numbering(heading.text)

            if detected_level > 0:
                # Clear numbering detected - use it and update context
                heading.level = detected_level
                current_context_level = detected_level

            else:
                # No clear numbering - inherit from current hierarchical context
                if current_context_level is not None:
                    # Unnumbered items are children of the current context
                    if current_context_level == 1:
                        heading.level = 2  # Direct child of main chapter
                    elif current_context_level == 2:
                        heading.level = 3  # Child of subsection
                    elif current_context_level == 3:
                        heading.level = 4  # Child of sub-subsection
                    else:
                        heading.level = min(current_context_level + 1, 5)
                else:
                    # No context yet - estimate from font size
                    heading.level = self._estimate_level_from_font_size(heading.font_size, headings)

        return headings

    def _detect_level_from_numbering(self, text: str) -> int:
        """
        Detect hierarchical level from numbering pattern.

        Hierarchy:
        Level 1: "1.", "2.", "10." - Main chapters (Capítulo 1, 2, etc.)
        Level 2: "1.1", "2.3", "7.2" - Subsections (numbered)
        Level 3: "1.1.1", "1.2.3" - Sub-subsections (triple numbering)
        Level 4: "a.", "b.", "d.1", "d.2" - Items (letter-based, same level)
        Level 5: "a)", "b)", "c)" - Sub-items with parenthesis

        Note: "d.1", "d.2" are treated as level 4 (same as "a.", "b.")
        because there's no parent "d." section - they're alternatives to simple letters.
        """
        # Level 3: Complex hierarchical "1.1.1", "1.2.3" (triple numbering)
        if re.match(r"^\d+\.\d+\.\d+", text):
            return 3

        # Level 2: Two-level numbering "1.1", "2.3", "7.2" (digits only)
        if re.match(r"^\d+\.\d+[\.\)\s]", text):
            return 2

        # Level 1: Main sections "1.", "2.", "10."
        # Must be digit(s) + dot/paren + space + Capital letter
        if re.match(r"^\d{1,2}[\.\)]\s+[A-Z]", text):
            return 1

        # Level 5: Letter enumeration in parentheses "a)", "b)", "c)"
        if re.match(r"^[a-z]\)\s+", text):
            return 5

        # Level 4: Letter patterns (ALL at same level)
        # Includes: "a.", "b.", "c." AND "d.1", "d.2", "e.3"
        # These are alternative notations, not hierarchical
        if re.match(r"^[a-z]\.", text):
            return 4

        # Level 1: Roman numerals "I.", "II.", "III."
        if re.match(r"^[IVX]+[\.\)]\s+", text):
            return 1

        # Level 2: Capital letters "A.", "B." (less common, usually subsections)
        if re.match(r"^[A-Z][\.\)]\s+", text):
            return 2

        return 0  # No clear numbering

    def _estimate_level_from_font_size(self, font_size: float, all_headings: List[HeadingCandidate]) -> int:
        """Estimate level based on font size relative to other headings."""
        if not all_headings:
            return 1

        # Get all font sizes
        sizes = sorted(set(h.font_size for h in all_headings), reverse=True)

        if len(sizes) == 1:
            return 1

        # Assign levels based on size ranking
        for idx, size in enumerate(sizes):
            if abs(font_size - size) < 0.5:
                return min(idx + 1, 6)  # Max 6 levels

        return 1

    def export_toc_markdown(self, toc: List[Dict], grouped_by_chapter: bool = True) -> str:
        """
        Export table of contents as Markdown.

        Args:
            toc: List of TOC entries
            grouped_by_chapter: If True, group items under their parent chapters (Word-style)
        """
        lines = ["# Índice del Documento\n"]

        if not grouped_by_chapter:
            # Simple flat list with indentation
            for entry in toc:
                indent = "  " * max(0, entry["level"] - 1)
                page = entry["page"]
                text = entry["text"]
                lines.append(f"{indent}- {text} (p. {page})")
        else:
            # Grouped by chapters (Word-style)
            current_chapter = None

            for entry in toc:
                level = entry["level"]
                page = entry["page"]
                text = entry["text"]

                # Level 0: Document metadata (no indentation, bold)
                if level == 0:
                    lines.append(f"\n**{text}** (p. {page})\n")

                # Level 1: Main chapters (no indentation, add spacing before)
                elif level == 1:
                    if current_chapter is not None:
                        lines.append("")  # Blank line between chapters
                    lines.append(f"**{text}** (p. {page})")
                    current_chapter = text

                # Level 2+: Sub-items (indented under chapter)
                else:
                    # Calculate indentation (level 2 = 2 spaces, level 3 = 4, etc.)
                    indent = "  " * (level - 2)
                    lines.append(f"{indent}- {text} (p. {page})")

        return "\n".join(lines)

    def export_toc_json(self, toc: List[Dict]) -> Dict:
        """Export table of contents as structured JSON."""
        return {
            "document": str(self.pdf_path),
            "total_entries": len(toc),
            "toc": toc
        }

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
def generate_toc(
    pdf_path: str,
    min_score: float = 15.0,
    export_format: str = "dict"
) -> Dict:
    """
    Quick TOC generation function.

    Args:
        pdf_path: Path to PDF
        min_score: Minimum heading score
        export_format: "dict", "markdown", or "json"

    Returns:
        Table of contents in requested format
    """
    with HeadingDetector(pdf_path, min_heading_score=min_score) as detector:
        toc = detector.generate_toc()

        if export_format == "markdown":
            return detector.export_toc_markdown(toc)
        elif export_format == "json":
            return detector.export_toc_json(toc)
        else:
            return toc
