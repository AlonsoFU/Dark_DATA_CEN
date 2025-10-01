"""
Table Cell Merger Utility
Handles multi-line table cells (cDoubleLinea, cTripleLinea, etc.)
where cell content spans multiple rows in the PDF.
"""

from typing import List, Dict, Tuple, Optional
from pathlib import Path


class TableCellMerger:
    """
    Merges multi-line table cells that were split during PDF extraction.

    Common patterns:
    - cDoubleLinea: Cell content spans 2 lines
    - cTripleLinea: Cell content spans 3 lines
    - Continuation lines starting with "/" or indented text
    """

    def __init__(self):
        # Patterns that indicate a continuation line
        self.continuation_indicators = [
            "/",  # Common in technical IDs
            "y ",  # Continuation conjunction
            "-",  # Continuation dash
        ]

        # Minimum indentation (spaces) to consider as continuation
        self.min_continuation_indent = 2

    def is_continuation_line(self, line: str) -> bool:
        """
        Determines if a line is a continuation of the previous cell.

        Args:
            line: Text line to check

        Returns:
            True if line is likely a continuation
        """
        stripped = line.strip()

        # Empty line is not a continuation
        if not stripped:
            return False

        # Section headers are NOT continuations
        if self.is_section_header(stripped):
            return False

        # Starts with continuation indicator
        for indicator in self.continuation_indicators:
            if stripped.startswith(indicator):
                return True

        # Very short line (< 5 chars) with special chars
        if len(stripped) < 5 and any(c in stripped for c in ["(", ")", "/", "-"]):
            return True

        # Line starts with lowercase (likely continuation of sentence)
        if stripped[0].islower():
            return True

        return False

    def is_section_header(self, campo: str) -> bool:
        """
        Determines if a campo is a section header (1., a., b., etc.)

        Args:
            campo: Field text to check

        Returns:
            True if it's a section header marker
        """
        stripped = campo.strip()

        # Single char + period: "1.", "a.", "b."
        if len(stripped) <= 3 and stripped[-1:] == ".":
            if stripped[0].isalnum():
                return True

        # Pattern like "d.1", "d.2"
        if len(stripped) <= 4 and "." in stripped:
            parts = stripped.split(".")
            if len(parts) == 2 and parts[0].isalpha() and parts[1].isdigit():
                return True

        return False

    def is_field_line(self, line: str) -> bool:
        """
        Determines if a line is a field label (campo).

        Common field patterns:
        - "Nombre de la instalación"
        - "Tipo de instalación"
        - "Fecha"
        - Ends with descriptive text, not values
        """
        stripped = line.strip()

        # Empty
        if not stripped:
            return False

        # Don't treat section headers as field lines
        if self.is_section_header(stripped):
            return False

        # Contains common field keywords
        field_keywords = [
            "nombre", "tipo", "tensión", "segmento", "propietario",
            "rut", "representante", "dirección", "fecha", "hora",
            "ubicación", "coordenadas", "elemento", "origen", "causa",
            "fenómeno", "detalles", "comuna", "calificación", "consumos",
            "demanda", "porcentaje"
        ]

        lower_line = stripped.lower()
        for keyword in field_keywords:
            if keyword in lower_line:
                return True

        return False

    def merge_table_rows(
        self,
        table_rows: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """
        Merges multi-line cells in table rows.

        Expected input format:
        [
            {"campo": "Nombre de la instalación", "valor": "Línea 2x500 kV..."},
            {"campo": "/ LT002...", "valor": "y LT002..."},  # <- continuation
            ...
        ]

        Args:
            table_rows: List of row dicts with 'campo' and 'valor' keys

        Returns:
            Merged rows with continuations combined
        """
        if not table_rows:
            return []

        merged = []
        i = 0

        while i < len(table_rows):
            current_row = table_rows[i].copy()
            campo = current_row.get("campo", "").strip()
            valor = current_row.get("valor", "").strip()

            # Skip empty rows
            if not campo and not valor:
                i += 1
                continue

            # If this is a section header (1., a., etc.), keep it as-is
            if self.is_section_header(campo):
                merged.append({
                    "row_id": current_row.get("row_id", len(merged) + 1),
                    "campo": campo,
                    "valor": valor
                })
                i += 1
                continue

            # Check if this row is a proper field row
            is_field = self.is_field_line(campo)

            # If campo is a continuation indicator, merge with previous
            if merged and self.is_continuation_line(campo):
                # Don't merge with section headers
                prev_row = merged[-1]
                if not self.is_section_header(prev_row["campo"]):
                    # Append to previous row's valor
                    if prev_row["valor"]:
                        prev_row["valor"] += " " + campo
                    else:
                        prev_row["valor"] = campo

                    # Also merge current valor if exists
                    if valor:
                        prev_row["valor"] += " " + valor

                    i += 1
                    continue

            # Look ahead for continuation rows
            j = i + 1
            while j < len(table_rows):
                next_row = table_rows[j]
                next_campo = next_row.get("campo", "").strip()
                next_valor = next_row.get("valor", "").strip()

                # Check if next row is a continuation
                if self.is_continuation_line(next_campo):
                    # Merge into current valor
                    if valor:
                        valor += " " + next_campo
                    else:
                        valor = next_campo

                    if next_valor:
                        valor += " " + next_valor

                    j += 1
                else:
                    # Not a continuation, stop looking ahead
                    break

            # Add merged row
            merged.append({
                "row_id": current_row.get("row_id", len(merged) + 1),
                "campo": campo,
                "valor": valor.strip()
            })

            # Skip the rows we merged
            i = j

        # Re-number row IDs
        for idx, row in enumerate(merged, 1):
            row["row_id"] = idx

        return merged

    def merge_raw_text_lines(
        self,
        lines: List[str]
    ) -> List[Tuple[str, str]]:
        """
        Merges multi-line cells from raw PDF text extraction.

        Expects alternating lines of:
        Campo  Valor
        Campo  Valor
        / continuation

        Args:
            lines: List of text lines from PDF

        Returns:
            List of (campo, valor) tuples
        """
        result = []
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines
            if not line:
                i += 1
                continue

            # Skip section markers (a., b., 1., etc.)
            if len(line) <= 3 and line[-1] == ".":
                i += 1
                continue

            # Try to split line into campo and valor
            parts = line.split(maxsplit=1)

            if len(parts) == 0:
                i += 1
                continue

            # Check if this is a continuation line
            if self.is_continuation_line(line):
                # Append to previous row
                if result:
                    prev_campo, prev_valor = result[-1]
                    result[-1] = (prev_campo, prev_valor + " " + line)
                i += 1
                continue

            # Split into campo and valor (look for multiple spaces)
            if "  " in line:  # Two or more spaces indicate column separation
                parts = line.split("  ", 1)
                campo = parts[0].strip()
                valor = parts[1].strip() if len(parts) > 1 else ""
            else:
                # Single column, treat as campo
                campo = line
                valor = ""

            # Look ahead for continuation lines
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()

                if self.is_continuation_line(next_line):
                    # Merge into valor
                    if valor:
                        valor += " " + next_line
                    else:
                        valor = next_line
                    j += 1
                else:
                    break

            result.append((campo, valor))
            i = j if j > i + 1 else i + 1

        return result

    def clean_merged_text(self, text: str) -> str:
        """
        Cleans up merged text by removing extra spaces and formatting.

        Args:
            text: Merged text with potential formatting issues

        Returns:
            Cleaned text
        """
        # Remove multiple spaces
        text = " ".join(text.split())

        # Fix spacing around slashes
        text = text.replace(" / ", "/")

        # Fix spacing around dashes in technical IDs
        text = text.replace(" - ", "-")

        return text.strip()


# Example usage
if __name__ == "__main__":
    # Test data from EAF capitulo 01
    test_rows = [
        {"row_id": 1, "campo": "1.", "valor": "Descripción pormenorizada de la perturbación"},
        {"row_id": 2, "campo": "a.", "valor": "Fecha y Hora de la falla"},
        {"row_id": 3, "campo": "Fecha", "valor": "25/02/2025"},
        {"row_id": 10, "campo": "Nombre de la instalación", "valor": "Ambos circuitos de la línea 2x500 kV Nueva Maitencillo - Nueva Pan de Azúcar"},
        {"row_id": 11, "campo": "/ LT002CI1TR01T0022ST01T0022", "valor": "y LT002CI2TR01T0022ST01T0022"},
        {"row_id": 12, "campo": "Tipo de instalación", "valor": "Línea"},
    ]

    merger = TableCellMerger()
    merged = merger.merge_table_rows(test_rows)

    print("🔧 MERGED ROWS:")
    for row in merged:
        print(f"  {row['row_id']}: {row['campo']} → {row['valor']}")
