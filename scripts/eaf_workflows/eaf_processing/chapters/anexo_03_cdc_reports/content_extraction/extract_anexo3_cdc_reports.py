#!/usr/bin/env python3
"""
ANEXO 3 CDC Reports Extractor
============================

Extracts CDC movement and daily report data from ANEXO 3 (Pages 96-100)
Focus: Centrales movement details and CDC daily operational reports

This script extracts:
- Plant movement details (start/stop operations)
- CDC operational status reports
- Central dispatch control information
- Plant operational changes and status

Usage:
    python extract_anexo3_cdc_reports.py [page_number]
    python extract_anexo3_cdc_reports.py --all  # Process all pages 96-100
"""

import sys
import re
import json
import io
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Add project root to path (go up 7 levels)
project_root = Path(__file__).parent.parent.parent.parent.parent.parent.parent
sys.path.append(str(project_root))

try:
    from PyPDF2 import PdfReader
    import pytesseract
    from PIL import Image
    import fitz  # PyMuPDF
    import cv2
    import numpy as np
except ImportError as e:
    print(f"Installing required packages: {e}")
    import os
    os.system("pip install PyPDF2 pytesseract pillow PyMuPDF opencv-python")
    from PyPDF2 import PdfReader
    import pytesseract
    from PIL import Image
    import fitz
    import cv2
    import numpy as np

def find_pdf_file():
    """Find the EAF PDF file in the project"""
    possible_paths = [
        project_root / "data" / "documents" / "anexos_EAF" / "source_documents" / "Anexos-EAF-089-2025.pdf",
        project_root / "data" / "documents" / "anexos_EAF" / "samples_and_tests" / "Anexos-EAF-089-2025.pdf",
        project_root / "data" / "documents" / "power_system_reports" / "anexos_EAF" / "Anexos-EAF-089-2025.pdf",
        project_root / "data_real" / "Anexos-EAF-089-2025.pdf",
        project_root / "Anexos-EAF-089-2025.pdf"
    ]

    for path in possible_paths:
        if path.exists():
            return str(path)
    return None

def extract_page_text(document_path: str, page_num: int) -> str:
    """Extract text from single page using PyPDF2"""
    try:
        reader = PdfReader(document_path)
        if page_num <= len(reader.pages):
            return reader.pages[page_num - 1].extract_text()
        else:
            print(f"Page {page_num} not found in document")
            return ""
    except Exception as e:
        print(f"Error extracting text from page {page_num}: {e}")
        return ""

def extract_ocr_text(document_path: str, page_num: int) -> str:
    """Extract text using OCR with PyMuPDF + Tesseract"""
    try:
        doc = fitz.open(document_path)
        page = doc[page_num - 1]

        # Convert page to image
        mat = fitz.Matrix(2.0, 2.0)  # Scale factor for better OCR
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")

        # Convert to PIL Image
        image = Image.open(io.BytesIO(img_data))

        # Perform OCR
        ocr_text = pytesseract.image_to_string(image, lang='spa+eng')

        doc.close()
        return ocr_text

    except Exception as e:
        print(f"OCR extraction failed for page {page_num}: {e}")
        return ""

def extract_date_info(raw_text: str) -> Dict:
    """Extract date information from page header"""
    date_patterns = [
        r'(\d{2}-\d{2}-\d{4})',  # DD-MM-YYYY format
        r'(\d{1,2})\s+de\s+(febrero|enero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+de\s+(\d{4})',
        r'(martes|miércoles|jueves|viernes|sábado|domingo|lunes)\s+(\d{1,2})\s+de\s+(febrero|enero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+de\s+(\d{4})'
    ]

    date_info = {}
    for pattern in date_patterns:
        match = re.search(pattern, raw_text[:300], re.IGNORECASE)
        if match:
            if len(match.groups()) == 1:  # DD-MM-YYYY format
                date_info = {
                    "operation_date": match.group(1),
                    "date_format": "DD-MM-YYYY",
                    "source": "extracted_from_header"
                }
            elif len(match.groups()) == 3:  # Day Month Year
                date_info = {
                    "day": match.group(1),
                    "month": match.group(2),
                    "year": match.group(3),
                    "source": "extracted_from_header"
                }
            elif len(match.groups()) == 4:  # Day of week + Date
                date_info = {
                    "day_name": match.group(1),
                    "day": match.group(2),
                    "month": match.group(3),
                    "year": match.group(4),
                    "source": "extracted_from_header"
                }
            break

    return date_info

def extract_plant_movements(text: str) -> Dict:
    """Extract plant movement information (starts, stops, status changes)"""
    movements = {
        "plant_operations": [],
        "status_changes": [],
        "operational_notes": []
    }

    # Look for common movement patterns
    movement_patterns = [
        r'([A-Z][A-Z0-9\-_]+)\s+(ENCENDIDA|DETENIDA|FUERA\s+DE\s+SERVICIO|EN\s+SERVICIO)',
        r'([A-Z][A-Z0-9\-_]+)\s+(START|STOP|ON|OFF)',
        r'CENTRAL\s+([A-Z][A-Z0-9\-_]+)\s+(.*)',
        r'([A-Z][A-Z0-9\-_]+)\s+(\d{1,2}:\d{2})\s+(.*)',
    ]

    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if len(line) < 5:
            continue

        for pattern in movement_patterns:
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 2:
                    plant_name = match.group(1)
                    status_info = match.group(2)

                    movement_info = {
                        "plant_name": plant_name,
                        "status_info": status_info,
                        "raw_line": line,
                        "line_context": line
                    }

                    if len(match.groups()) > 2:
                        movement_info["additional_info"] = match.group(3)

                    movements["plant_operations"].append(movement_info)

    return movements

def extract_cdc_reports(text: str) -> Dict:
    """Extract CDC (Centro de Despacho y Control) report information"""
    cdc_info = {
        "operational_status": [],
        "system_conditions": [],
        "alerts_warnings": [],
        "transmission_status": []
    }

    # Look for CDC-specific patterns
    cdc_patterns = [
        r'CDC\s+(.*)',
        r'CENTRO\s+DE\s+DESPACHO\s+(.*)',
        r'SISTEMA\s+ELECTRICO\s+(.*)',
        r'TRANSMISION\s+(.*)',
        r'ALERTA\s+(.*)|ADVERTENCIA\s+(.*)',
        r'CONDICION\s+(.*)',
        r'ESTADO\s+(.*)'
    ]

    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if len(line) < 5:
            continue

        for pattern in cdc_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                info = {
                    "category": pattern.split('\\s+')[0].replace('(', '').replace('?', ''),
                    "content": match.group(1) if match.group(1) else match.group(2) if len(match.groups()) > 1 and match.group(2) else line,
                    "raw_line": line
                }

                if 'CDC' in pattern.upper():
                    cdc_info["operational_status"].append(info)
                elif 'ALERTA' in pattern.upper() or 'ADVERTENCIA' in pattern.upper():
                    cdc_info["alerts_warnings"].append(info)
                elif 'TRANSMISION' in pattern.upper():
                    cdc_info["transmission_status"].append(info)
                elif 'SISTEMA' in pattern.upper():
                    cdc_info["system_conditions"].append(info)
                else:
                    cdc_info["operational_status"].append(info)

    return cdc_info

def extract_tables(text: str) -> Dict:
    """Extract any tabular data present in the page"""
    tables = {
        "detected_tables": [],
        "numeric_data": [],
        "structured_info": []
    }

    lines = text.split('\n')
    current_table = []

    for line in lines:
        line = line.strip()
        if len(line) < 3:
            if current_table and len(current_table) > 1:
                tables["detected_tables"].append({
                    "table_data": current_table.copy(),
                    "row_count": len(current_table)
                })
            current_table = []
            continue

        # Check if line looks like tabular data (contains multiple numbers or structured format)
        if re.search(r'\d+\s+\d+', line) or re.search(r'\|', line) or len(re.findall(r'\s+', line)) > 3:
            current_table.append(line)

        # Extract numeric sequences
        numbers = re.findall(r'\d+\.?\d*', line)
        if len(numbers) > 2:
            tables["numeric_data"].append({
                "line": line,
                "numbers": numbers,
                "count": len(numbers)
            })

    # Add final table if exists
    if current_table and len(current_table) > 1:
        tables["detected_tables"].append({
            "table_data": current_table.copy(),
            "row_count": len(current_table)
        })

    return tables

def process_page(document_path: str, page_num: int) -> Dict:
    """Process a single page and extract all relevant information"""
    print(f"Processing ANEXO 3 page {page_num}...")

    # Extract text using both methods
    raw_text = extract_page_text(document_path, page_num)
    ocr_text = extract_ocr_text(document_path, page_num)

    # Combine texts for better extraction
    combined_text = raw_text + "\n" + ocr_text

    # Extract information
    date_info = extract_date_info(combined_text)
    plant_movements = extract_plant_movements(combined_text)
    cdc_reports = extract_cdc_reports(combined_text)
    tables = extract_tables(combined_text)

    # Build result
    result = {
        "document_metadata": {
            "document_file": "Anexos-EAF-089-2025.pdf",
            "document_path": document_path,
            "page_number": page_num,
            "extraction_timestamp": datetime.now().isoformat(),
            "document_type": "ANEXO_EAF_CDC_REPORTS",
            "extraction_method": "combined_text_ocr",
            "concept": "CDC movement and daily operation reports - plant status changes and dispatch control information"
        },
        "date_information": date_info,
        "plant_movements": plant_movements,
        "cdc_reports": cdc_reports,
        "tabular_data": tables,
        "raw_content": {
            "pdf_text_length": len(raw_text),
            "ocr_text_length": len(ocr_text),
            "combined_length": len(combined_text),
            "pdf_preview": raw_text[:500] if raw_text else "",
            "ocr_preview": ocr_text[:500] if ocr_text else ""
        },
        "extraction_summary": {
            "plant_operations_found": len(plant_movements["plant_operations"]),
            "cdc_reports_found": len(cdc_reports["operational_status"]),
            "tables_detected": len(tables["detected_tables"]),
            "has_date_info": bool(date_info),
            "extraction_quality": "preliminary"
        }
    }

    return result

def save_extraction(result: Dict, page_num: int):
    """Save extraction result to JSON file"""
    output_dir = project_root / "data" / "documents" / "anexos_EAF" / "extractions" / "anexo_03_cdc_reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"anexo3_page_{page_num:02d}_{timestamp}.json"
    output_path = output_dir / filename

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Extraction saved to: {output_path}")
    return output_path

def main():
    """Main extraction function"""
    # Find PDF file
    pdf_path = find_pdf_file()
    if not pdf_path:
        print("ERROR: Could not find Anexos-EAF-089-2025.pdf file")
        print("Please ensure the PDF file is in one of the expected locations")
        return

    print(f"Found PDF: {pdf_path}")

    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            pages = range(96, 101)  # Pages 96-100 for ANEXO 3
        else:
            try:
                page = int(sys.argv[1])
                if 96 <= page <= 100:
                    pages = [page]
                else:
                    print("ERROR: Page must be between 96-100 for ANEXO 3")
                    return
            except ValueError:
                print("ERROR: Invalid page number")
                return
    else:
        # Default: process first page of ANEXO 3
        pages = [96]

    # Process pages
    results = []
    for page_num in pages:
        try:
            result = process_page(pdf_path, page_num)
            save_path = save_extraction(result, page_num)
            results.append((page_num, save_path, result))
            print(f"✅ Page {page_num} processed successfully")

        except Exception as e:
            print(f"❌ Error processing page {page_num}: {e}")

    # Summary
    print(f"\n📊 ANEXO 3 Extraction Summary:")
    print(f"   Processed pages: {len(results)}")
    print(f"   Page range: 96-100 (CDC Reports)")
    print(f"   Content focus: Plant movements and CDC operational reports")

    for page_num, save_path, result in results:
        summary = result["extraction_summary"]
        print(f"   Page {page_num}: {summary['plant_operations_found']} operations, "
              f"{summary['cdc_reports_found']} CDC reports, "
              f"{summary['tables_detected']} tables")

if __name__ == "__main__":
    main()