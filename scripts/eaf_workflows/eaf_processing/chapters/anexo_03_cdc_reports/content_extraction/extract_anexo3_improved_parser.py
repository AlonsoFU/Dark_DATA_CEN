#!/usr/bin/env python3
"""
ANEXO 3 Improved Parser
=======================

Improved extraction for ANEXO 3 page 97 with correct column structure:
['Fecha', 'Inicio Periodo', 'Fin Periodo', 'Instrucción - SSCC Requerida',
 'ID Configuración', 'Central / Subestación (PRS)', 'BARRA CT', 'Central-Unidad',
 'Configuración / Paño (PRS-EV)', 'Disponibilidad', 'BAJA', 'SUBE',
 '(kV, MVAr, MW)', 'Motivo', 'Comentario', 'Estado', 'Fecha de Edición']

Target: ~50 centrales from page 97
"""

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Project root
project_root = Path(__file__).parent.parent.parent.parent.parent.parent.parent

def extract_page_raw_text(page_num: int = 97) -> str:
    """Extract raw text from specific page using pdftotext"""
    pdf_path = project_root / "data" / "documents" / "anexos_EAF" / "source_documents" / "Anexos-EAF-089-2025.pdf"

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found at {pdf_path}")

    result = subprocess.run([
        'pdftotext', '-f', str(page_num), '-l', str(page_num), '-layout', str(pdf_path), '-'
    ], capture_output=True, text=True, encoding='utf-8')

    if result.returncode != 0:
        raise Exception(f"pdftotext failed: {result.stderr}")

    return result.stdout

def parse_table_structure(text: str) -> Tuple[List[str], List[List[str]]]:
    """Parse table with 17 columns structure"""

    # Expected column headers
    expected_headers = [
        'Fecha', 'Inicio Periodo', 'Fin Periodo', 'Instrucción - SSCC Requerida',
        'ID Configuración', 'Central / Subestación (PRS)', 'BARRA CT', 'Central-Unidad',
        'Configuración / Paño (PRS-EV)', 'Disponibilidad', 'BAJA', 'SUBE',
        '(kV, MVAr, MW)', 'Motivo', 'Comentario', 'Estado', 'Fecha de Edición'
    ]

    lines = text.split('\n')
    data_rows = []

    # Find lines that look like data rows (start with date pattern)
    date_pattern = r'^\s*(\d{2}-\d{2}-\d{4})'

    for line in lines:
        if re.match(date_pattern, line.strip()):
            # This looks like a data row
            # Try to split it into the 17 expected columns
            parsed_row = parse_data_row(line.strip())
            if parsed_row and len(parsed_row) >= 6:  # Minimum viable columns
                data_rows.append(parsed_row)

    return expected_headers, data_rows

def parse_data_row(line: str) -> Optional[List[str]]:
    """Parse a single data row into 17 columns"""

    # Initialize empty row
    row = [''] * 17

    try:
        # Use regex to extract main components
        # Pattern for: Date Time1 Time2 Instruction ID Central Unit Config ...
        main_pattern = r'^(\d{2}-\d{2}-\d{4})\s+(\d{1,2}:\d{2})\s+(\d{1,2}:\d{2})\s+(CPF\([+-]\)|CSF\([+-]\)|CTF\([+-]\))\s+(\d+)\s+([A-Z0-9\-_]+)\s+([A-Z0-9\-_]*)\s+([A-Z0-9\-_]+)\s+([A-Z0-9\-_\+\.]*)'

        match = re.match(main_pattern, line)
        if match:
            row[0] = match.group(1)  # Fecha
            row[1] = match.group(2)  # Inicio Periodo
            row[2] = match.group(3)  # Fin Periodo
            row[3] = match.group(4)  # Instrucción - SSCC Requerida
            row[4] = match.group(5)  # ID Configuración
            row[5] = match.group(6)  # Central / Subestación (PRS)
            row[6] = match.group(7)  # BARRA CT
            row[7] = match.group(8)  # Central-Unidad
            row[8] = match.group(9)  # Configuración / Paño (PRS-EV)

            # Extract remaining part for other fields
            remaining = line[match.end():].strip()

            # Try to extract numeric values, units, and status
            parts = remaining.split()
            part_idx = 0

            # Disponibilidad (numeric value)
            if part_idx < len(parts) and re.match(r'^\d+\.?\d*$', parts[part_idx]):
                row[9] = parts[part_idx]
                part_idx += 1

            # BAJA/SUBE direction
            if part_idx < len(parts) and parts[part_idx] in ['BAJA', 'SUBE']:
                row[10] = parts[part_idx] if parts[part_idx] == 'BAJA' else ''
                row[11] = parts[part_idx] if parts[part_idx] == 'SUBE' else ''
                part_idx += 1

            # Unit type (kV, MVAr, MW)
            if part_idx < len(parts) and parts[part_idx] in ['kV', 'MVAr', 'MW']:
                row[12] = parts[part_idx]
                part_idx += 1

            # Find status (CERRADA/ABIERTA + PENDIENTE/EJECUTADA)
            status_pattern = r'(CERRADA|ABIERTA)\s+(PENDIENTE|EJECUTADA)'
            status_match = re.search(status_pattern, remaining)
            if status_match:
                row[15] = f"{status_match.group(1)} {status_match.group(2)}"

                # Everything before status is description (Motivo + Comentario)
                description_text = remaining[:status_match.start()].strip()
                # Remove already parsed parts
                for parsed_part in parts[:part_idx]:
                    description_text = description_text.replace(parsed_part, '', 1).strip()

                # Split description into Motivo and Comentario (heuristic)
                if description_text:
                    # Look for common motivo patterns
                    if 'control' in description_text.lower() or 'participación' in description_text.lower():
                        row[13] = description_text  # Motivo
                        row[14] = ''  # Comentario
                    else:
                        row[13] = ''  # Motivo
                        row[14] = description_text  # Comentario

                # Look for edit date after status
                edit_date_match = re.search(r'(\d{2}-\d{2}-\d{4})', remaining[status_match.end():])
                if edit_date_match:
                    row[16] = edit_date_match.group(1)

        return row

    except Exception as e:
        print(f"Error parsing row: {line[:100]}... Error: {e}")
        return None

def create_structured_data(headers: List[str], rows: List[List[str]]) -> Dict:
    """Create structured JSON from parsed table data"""

    centrales_data = []

    for i, row in enumerate(rows):
        if len(row) >= len(headers):
            row = row[:len(headers)]  # Trim to exact column count
        else:
            # Pad with empty strings if needed
            row.extend([''] * (len(headers) - len(row)))

        central_record = {}
        for j, header in enumerate(headers):
            central_record[header] = row[j] if j < len(row) else ''

        # Add metadata
        central_record['row_number'] = i + 1
        central_record['extraction_confidence'] = 'high' if row[0] and row[5] else 'medium'

        centrales_data.append(central_record)

    # Create summary
    summary = {
        "total_centrales_extracted": len(centrales_data),
        "expected_centrales": 50,
        "extraction_rate": f"{(len(centrales_data)/50)*100:.1f}%" if len(centrales_data) <= 50 else "100%+",
        "control_types": list(set(row[3] for row in rows if len(row) > 3 and row[3])),
        "centrales_list": list(set(row[5] for row in rows if len(row) > 5 and row[5])),
        "date_range": list(set(row[0] for row in rows if len(row) > 0 and row[0]))
    }

    return {
        "extraction_metadata": {
            "document_file": "Anexos-EAF-089-2025.pdf",
            "page_number": 97,
            "extraction_timestamp": datetime.now().isoformat(),
            "extraction_method": "improved_17_column_parser",
            "concept": "CDC frequency control table - complete central assignments",
            "target_structure": "17_columns_50_centrales"
        },
        "table_structure": {
            "column_headers": headers,
            "total_columns": len(headers),
            "total_rows": len(rows),
            "expected_rows": 50
        },
        "centrales_data": centrales_data,
        "extraction_summary": summary
    }

def main():
    """Main extraction function"""

    print("🔄 Extracting ANEXO 3 Page 97 with improved parser...")

    try:
        # Extract raw text
        raw_text = extract_page_raw_text(97)
        print(f"✅ Raw text extracted: {len(raw_text)} characters")

        # Parse table structure
        headers, rows = parse_table_structure(raw_text)
        print(f"✅ Table parsed: {len(headers)} columns, {len(rows)} rows")

        # Create structured data
        structured_data = create_structured_data(headers, rows)
        print(f"✅ Structured data created: {structured_data['extraction_summary']['total_centrales_extracted']} centrales")

        # Save results
        output_dir = project_root / "data" / "documents" / "anexos_EAF" / "extractions" / "anexo_03_cdc_reports"
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"anexo3_page97_improved_extraction_{timestamp}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(structured_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Results saved to: {output_file}")

        # Print summary
        summary = structured_data['extraction_summary']
        print(f"\n📊 Extraction Summary:")
        print(f"   Centrales extracted: {summary['total_centrales_extracted']}/50")
        print(f"   Extraction rate: {summary['extraction_rate']}")
        print(f"   Control types: {summary['control_types']}")
        print(f"   First 10 centrales: {summary['centrales_list'][:10]}")

        return structured_data

    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        raise

if __name__ == "__main__":
    main()