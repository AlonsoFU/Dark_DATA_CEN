#!/usr/bin/env python3
"""
ANEXO 3 Complete Parser - All Pages
====================================

Extracts all table content from ANEXO 3 pages 97-100 with the same column structure:
['Fecha', 'Inicio Periodo', 'Fin Periodo', 'Instrucción - SSCC Requerida',
 'ID Configuración', 'Central / Subestación (PRS)', 'BARRA CT', 'Central-Unidad',
 'Configuración / Paño (PRS-EV)', 'Disponibilidad', 'BAJA', 'SUBE',
 '(kV, MVAr, MW)', 'Motivo', 'Comentario', 'Estado', 'Fecha de Edición']

Processes pages 97, 98, 99, and 100 to capture all CDC control instructions.
"""

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Project root
project_root = Path(__file__).parent.parent.parent.parent.parent.parent.parent

def extract_page_raw_text(page_num: int) -> str:
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

def parse_table_structure(text: str, page_num: int) -> Tuple[List[str], List[List[str]]]:
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
            parsed_row = parse_data_row(line.strip(), page_num)
            if parsed_row and len(parsed_row) >= 6:  # Minimum viable columns
                data_rows.append(parsed_row)

    return expected_headers, data_rows

def parse_data_row(line: str, page_num: int) -> Optional[List[str]]:
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

        # Add source page metadata
        row.append(f"page_{page_num}")

        return row

    except Exception as e:
        print(f"Error parsing row from page {page_num}: {line[:100]}... Error: {e}")
        return None

def process_multiple_pages(pages: List[int]) -> Dict:
    """Process multiple pages and consolidate results"""

    all_centrales_data = []
    page_summaries = {}
    consolidated_stats = {
        "total_centrales": 0,
        "by_page": {},
        "control_types": set(),
        "centrales_list": set(),
        "date_ranges": set()
    }

    # Expected column headers
    headers = [
        'Fecha', 'Inicio Periodo', 'Fin Periodo', 'Instrucción - SSCC Requerida',
        'ID Configuración', 'Central / Subestación (PRS)', 'BARRA CT', 'Central-Unidad',
        'Configuración / Paño (PRS-EV)', 'Disponibilidad', 'BAJA', 'SUBE',
        '(kV, MVAr, MW)', 'Motivo', 'Comentario', 'Estado', 'Fecha de Edición'
    ]

    for page_num in pages:
        try:
            print(f"🔄 Processing page {page_num}...")

            # Extract text for this page
            raw_text = extract_page_raw_text(page_num)

            # Parse table structure
            page_headers, page_rows = parse_table_structure(raw_text, page_num)

            # Convert to structured data
            for i, row in enumerate(page_rows):
                if len(row) >= len(headers):
                    row = row[:len(headers)]  # Trim to exact column count
                else:
                    # Pad with empty strings if needed
                    row.extend([''] * (len(headers) - len(row)))

                central_record = {}
                for j, header in enumerate(headers):
                    central_record[header] = row[j] if j < len(row) else ''

                # Add metadata
                central_record['source_page'] = page_num
                central_record['row_number'] = i + 1
                central_record['global_row_id'] = len(all_centrales_data) + 1
                central_record['extraction_confidence'] = 'high' if row[0] and row[5] else 'medium'

                all_centrales_data.append(central_record)

                # Update consolidated stats
                if row[3]:  # Control type
                    consolidated_stats["control_types"].add(row[3])
                if row[5]:  # Central name
                    consolidated_stats["centrales_list"].add(row[5])
                if row[0]:  # Date
                    consolidated_stats["date_ranges"].add(row[0])

            # Page summary
            page_summaries[f"page_{page_num}"] = {
                "centrales_count": len(page_rows),
                "text_length": len(raw_text),
                "extraction_status": "success"
            }

            consolidated_stats["by_page"][f"page_{page_num}"] = len(page_rows)
            consolidated_stats["total_centrales"] += len(page_rows)

            print(f"✅ Page {page_num}: {len(page_rows)} centrales extracted")

        except Exception as e:
            print(f"❌ Error processing page {page_num}: {e}")
            page_summaries[f"page_{page_num}"] = {
                "centrales_count": 0,
                "extraction_status": f"error: {e}"
            }

    # Convert sets to lists for JSON serialization
    consolidated_stats["control_types"] = sorted(list(consolidated_stats["control_types"]))
    consolidated_stats["centrales_list"] = sorted(list(consolidated_stats["centrales_list"]))
    consolidated_stats["date_ranges"] = sorted(list(consolidated_stats["date_ranges"]))

    return {
        "extraction_metadata": {
            "document_file": "Anexos-EAF-089-2025.pdf",
            "pages_processed": pages,
            "extraction_timestamp": datetime.now().isoformat(),
            "extraction_method": "improved_17_column_parser_multi_page",
            "concept": "CDC frequency control table - complete central assignments from all pages",
            "target_structure": "17_columns_all_centrales"
        },
        "table_structure": {
            "column_headers": headers,
            "total_columns": len(headers),
            "pages_processed": len(pages),
            "total_rows_all_pages": consolidated_stats["total_centrales"]
        },
        "page_summaries": page_summaries,
        "consolidated_centrales_data": all_centrales_data,
        "consolidated_summary": consolidated_stats
    }

def main():
    """Main extraction function for all pages"""

    print("🔄 Extracting ANEXO 3 Pages 97-100 with improved parser...")

    # Pages to process
    pages_to_process = [97, 98, 99, 100]

    try:
        # Process all pages
        complete_results = process_multiple_pages(pages_to_process)

        # Save consolidated results
        output_dir = project_root / "data" / "documents" / "anexos_EAF" / "extractions" / "anexo_03_cdc_reports"
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"anexo3_complete_all_pages_extraction_{timestamp}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(complete_results, f, indent=2, ensure_ascii=False)

        print(f"✅ Complete results saved to: {output_file}")

        # Print summary
        stats = complete_results['consolidated_summary']
        print(f"\n📊 Complete ANEXO 3 Extraction Summary:")
        print(f"   Pages processed: {pages_to_process}")
        print(f"   Total centrales: {stats['total_centrales']}")
        print(f"   By page: {stats['by_page']}")
        print(f"   Control types: {stats['control_types']}")
        print(f"   Unique centrales: {len(stats['centrales_list'])}")
        print(f"   Date range: {stats['date_ranges']}")

        # Save individual page files too
        for page_num in pages_to_process:
            page_data = [record for record in complete_results['consolidated_centrales_data']
                        if record['source_page'] == page_num]

            if page_data:
                page_file = output_dir / f"anexo3_page{page_num}_individual_extraction_{timestamp}.json"
                page_result = {
                    "extraction_metadata": {
                        **complete_results['extraction_metadata'],
                        "page_number": page_num,
                        "concept": f"CDC frequency control table - page {page_num} centrales"
                    },
                    "table_structure": complete_results['table_structure'],
                    "centrales_data": page_data,
                    "page_summary": {
                        "centrales_count": len(page_data),
                        "page_number": page_num
                    }
                }

                with open(page_file, 'w', encoding='utf-8') as f:
                    json.dump(page_result, f, indent=2, ensure_ascii=False)

                print(f"   Page {page_num}: {len(page_data)} centrales → {page_file.name}")

        return complete_results

    except Exception as e:
        print(f"❌ Error during complete extraction: {e}")
        raise

if __name__ == "__main__":
    main()