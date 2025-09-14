#!/usr/bin/env python3
"""
ANEXO 2 Real Generation Data Extractor
======================================

Extracts real generation data from ANEXO 2 (Pages 63-95)
Focus: Actual power generation values, real-time operational data

This script extracts:
- Real generation values by power plant
- Actual vs programmed generation comparison
- Operational performance metrics
- Time-series generation data

Usage:
    python extract_anexo2_real_generation.py [page_number]
    python extract_anexo2_real_generation.py --all  # Process all pages 63-95
"""

import sys
import re
import json
import io
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Add project root to path (go up 7 levels from scripts/eaf_workflows/eaf_processing/chapters/anexo_02_real_generation/content_extraction/)
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

def extract_date_info(raw_text: str) -> Dict:
    """Extract date information from the beginning of the page"""
    # Look for date patterns like "25-02-2025" or "RESUMEN DIARIO DE OPERACION DEL SEN"
    date_patterns = [
        r'(\d{2}-\d{2}-\d{4})\s+(\d{2}-\d{2}-\d{4})',  # "25-02-2025 25-02-2025"
        r'(\d{2}-\d{2}-\d{4})',  # Single date
        r'RESUMEN DIARIO DE OPERACION DEL SEN\s*(\d{2}-\d{2}-\d{4})'  # With header
    ]

    date_info = {}
    for pattern in date_patterns:
        match = re.search(pattern, raw_text[:200])  # Check first 200 chars
        if match:
            if len(match.groups()) == 2:  # Two dates
                date_info = {
                    "operation_date": match.group(1),
                    "report_date": match.group(2),
                    "date_format": "DD-MM-YYYY",
                    "source": "extracted_from_header"
                }
            else:  # Single date
                date_info = {
                    "operation_date": match.group(1),
                    "date_format": "DD-MM-YYYY",
                    "source": "extracted_from_header"
                }
            break

    # Also check for "RESUMEN DIARIO" to confirm this is a daily summary page
    if "RESUMEN DIARIO" in raw_text[:200]:
        date_info["document_type"] = "daily_operation_summary"

    return date_info

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
        if 1 <= page_num <= len(reader.pages):
            page = reader.pages[page_num - 1]
            return page.extract_text().strip()
        return ""
    except Exception as e:
        print(f"Error extracting page {page_num}: {e}")
        return ""

def is_system_summary_page(raw_text: str) -> bool:
    """Detect if page contains actual system-wide summary data (not just header)"""
    # Key indicators that distinguish true system summary pages from regular plant pages
    # These are specific data patterns that only appear on system summary pages
    specific_system_patterns = [
        "TOTAL HORA.",  # Must have the actual TOTAL HORA data line
        "TOTAL SEN",    # Must have TOTAL SEN data
        "FLUJO CHANGOS->CUMBRES",  # Power flow data - unique to system summary
        "PERDIDAS APROX.",  # System losses data
        "DEMANDA APROX.",   # System demand data
        "DMAX"  # Daily maximum indicator at the end
    ]

    # Check if multiple specific system data patterns are present
    # (not just the common header that appears on every page)
    pattern_count = sum(1 for pattern in specific_system_patterns if pattern in raw_text)

    # Also check for the characteristic data structure pattern of system summary pages
    # Look for lines with multiple numerical values (system data rows)
    system_data_lines = 0
    lines = raw_text.split('\n')
    for line in lines:
        # Look for lines that start with system categories and have multiple numbers
        if any(pattern in line for pattern in ["TOTAL HORA.", "TOTAL SEN", "CONS. PROPIOS", "PERDIDAS APROX.", "DEMANDA APROX."]):
            # Check if line has multiple numerical values (indicating hourly data)
            numbers = len([x for x in line.split() if x.replace(',', '').replace('.', '').replace('-', '').isdigit()])
            if numbers >= 10:  # System summary lines have ~24 hourly values
                system_data_lines += 1

    # Require both: multiple system patterns AND actual system data lines
    return pattern_count >= 4 and system_data_lines >= 3

def extract_system_summary_data(raw_text: str) -> Dict:
    """Extract system-wide summary data (integrated from page 79 extractor)"""
    system_data = {}

    # System summary patterns
    patterns = {
        'total_hora': r'TOTAL HORA\.\s+([\d,\s.-]+?)\s+\d{3}\.?\d*',
        'total_hora_sing': r'TOTAL HORA\.\s+SING\s+([\d,\s.-]+?)(?:\s+TOTAL|\s+\d{2}\.?\d*\s*$)',
        'total_sen': r'TOTAL SEN\s+([\d,\s.-]+?)(?:\s+CONS\.|\s+\d{3}\.?\d*\s*$)',
        'cons_propios': r'CONS\.\s+PROPIOS\s+([\d,\s.-]+?)(?:\s+CONS\.|\s+\d\.?\d*\s*$)',
        'cons_propios_sing': r'CONS\.\s+PROPIOS\s+SING\s+([\d,\s.-]+?)(?:\s+FLUJO|\s+\d{3}\s*$)',
        'flujo_changos_cumbres': r'FLUJO\s+CHANGOS->CUMBRES\s+([\d,\s.-]+?)(?:\s+PERDIDAS|\s+-?\d\.?\d*\s*$)',
        'perdidas_aprox': r'PERDIDAS\s+APROX\.\s+([\d,\s.-]+?)(?:\s+PERDIDAS|\s+\d\.?\d*\s*$)',
        'perdidas_aprox_sing': r'PERDIDAS\s+APROX\.\s+SING\s+([\d,\s.-]+?)(?:\s+DEMANDA|\s+\d{3}\s*$)',
        'demanda_aprox': r'DEMANDA\s+APROX\.\s+([\d,\s.-]+?)(?:\s+DEMANDA|\s+\d{6}\.?\d*\s*$)',
        'demanda_aprox_sing': r'DEMANDA\s+APROX\.\s+SING\s+([\d,\s.-]+?)(?:\s+HORA|\s+\d{5}\.?\d*\s*$)',
        'dmax_total': r'DMAX\s*:\s*([\d,]+)'
    }

    for system_type, pattern in patterns.items():
        match = re.search(pattern, raw_text, re.IGNORECASE | re.DOTALL)
        if match:
            values_text = match.group(1).strip()

            # Handle DMAX specially (single value)
            if system_type == 'dmax_total':
                try:
                    dmax_value = float(values_text.replace(',', '.'))
                    system_data[system_type] = {
                        "value": dmax_value,
                        "system_category": "Daily Maximum Total",
                        "source": "system_summary_extraction",
                        "data_type": "single_value"
                    }
                except ValueError:
                    continue
            else:
                # Parse hourly values
                hourly_values = []
                value_parts = re.findall(r'-?\d+(?:,\d+)?', values_text)
                for part in value_parts[:24]:  # Only take first 24 hours
                    try:
                        clean_value = part.replace(',', '.')
                        value = float(clean_value)
                        hourly_values.append(value)
                    except ValueError:
                        continue

                if hourly_values:
                    # Build hourly data with hour numbers
                    hourly_data = []
                    for i, value in enumerate(hourly_values, 1):
                        hourly_data.append({
                            "hour": i,
                            "value": value
                        })

                    # Calculate metrics
                    daily_total = sum(hourly_values)
                    daily_max = max(hourly_values) if hourly_values else 0.0
                    daily_min = min(hourly_values) if hourly_values else 0.0
                    daily_avg = daily_total / len(hourly_values) if hourly_values else 0.0

                    system_data[system_type] = {
                        "hourly_data": hourly_data,
                        "daily_total": daily_total,
                        "daily_max": daily_max,
                        "daily_min": daily_min,
                        "daily_avg": daily_avg,
                        "operational_hours": len([v for v in hourly_values if v > 0]),
                        "system_category": system_type.replace('_', ' ').title(),
                        "data_points": len(hourly_values),
                        "source": "system_summary_extraction",
                        "data_type": "hourly_series"
                    }

    return system_data if system_data else None

def calculate_summary_metrics(generation_records: List[Dict]) -> Dict:
    """Calculate summary metrics for plant generation data"""
    if not generation_records:
        return {}

    # Calculate totals
    total_daily_mwh = sum(
        record['data'].get('daily_total_mwh', 0)
        for record in generation_records
        if isinstance(record['data'].get('daily_total_mwh'), (int, float))
    )
    max_capacity_mw = sum(
        record['data'].get('daily_max_mw', 0)
        for record in generation_records
        if isinstance(record['data'].get('daily_max_mw'), (int, float))
    )
    total_operational_hours = sum(
        record['data'].get('operational_hours', 0)
        for record in generation_records
        if isinstance(record['data'].get('operational_hours'), (int, float))
    )

    # Count by plant types
    plant_types = {}
    for record in generation_records:
        plant_type = record['data'].get('plant_type', 'UNKNOWN')
        plant_types[plant_type] = plant_types.get(plant_type, 0) + 1

    return {
        'total_plants': len(generation_records),
        'solar_pv_plants': plant_types.get('SOLAR_PV', 0),
        'distributed_solar_plants': plant_types.get('DISTRIBUTED_SOLAR_PV', 0) + plant_types.get('DISTRIBUTED_GENERATION', 0),
        'total_daily_generation_mwh': total_daily_mwh,
        'total_max_capacity_mw': max_capacity_mw,
        'avg_operational_hours': total_operational_hours / len(generation_records) if generation_records else 0,
        'system_type': 'RENEWABLE_SOLAR_FOCUSED'
    }

def extract_ocr_text(document_path: str, page_num: int) -> str:
    """Extract text using OCR on rendered PDF page"""
    try:
        doc = fitz.open(document_path)
        if 0 <= page_num - 1 < len(doc):
            page = doc[page_num - 1]
            
            # High DPI for better OCR accuracy
            mat = fitz.Matrix(2, 2)  # 144 DPI
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img_data = pix.tobytes("ppm")
            pil_image = Image.open(io.BytesIO(img_data))
            
            # OCR with Spanish + English
            ocr_text = pytesseract.image_to_string(
                pil_image,
                lang='spa+eng',
                config='--psm 6'
            )
            
            doc.close()
            return ocr_text.strip()
        
        doc.close()
        return ""
    except Exception as e:
        print(f"⚠️  OCR extraction failed: {e}")
        return ""

def extract_real_generation_data(page_text: str, ocr_text: str, page_num: int) -> Dict:
    """Extract real generation data from page text - handles both plant data and system summary"""

    # Check if this page has system summary data
    has_system_summary = is_system_summary_page(page_text)

    # Initialize extraction data structure
    extracted_data = {
        'page': page_num,
        'chapter': 'ANEXO_02_REAL_GENERATION',
        'extraction_timestamp': datetime.now().isoformat(),
        'extraction_quality': {
            'raw_text_length': len(page_text),
            'ocr_text_length': len(ocr_text),
            'has_system_data': has_system_summary,
            'patterns_found': 0
        }
    }

    # Extract system summary data if present
    if has_system_summary:
        print(f"   🔍 Detected system summary data on page {page_num}")
        system_summary = extract_system_summary_data(page_text)

        if system_summary:
            extracted_data['system_summary_data'] = system_summary
            summary_count = len([k for k, v in system_summary.items() if v.get('data_type') == 'hourly_series'])
            dmax_count = len([k for k, v in system_summary.items() if v.get('data_type') == 'single_value'])
            print(f"   ✅ Found {summary_count} system categories + {dmax_count} summary values")
            print(f"   🔧 DEBUG: System data keys = {list(system_summary.keys())[:5]}...")  # Debug line

    # Always try to extract plant data as well
    extracted_data['real_generation_records'] = []

    # ANEXO 2 specific patterns for tabular solar generation data
    patterns = {
        'solar_plant': [
            r'^(PFV-[A-ZÁÉÍÓÚÑ\-_0-9]+)',              # Solar plants: PFV-ELBOCO
            r'^(PMGD-PFV-[A-ZÁÉÍÓÚÑ\-_0-9]+)',        # Distributed solar: PMGD-PFV-QUEBRADA
            r'^(PMGD-[A-ZÁÉÍÓÚÑ\-_0-9]+)',            # Other distributed generation
        ],
        'tabular_generation': [
            # Pattern: PLANT_NAME + 24 hourly values + TOT.DIA + DMAX + DMED
            r'^([A-Z\-_0-9]+)\s+((?:\d+,\d+\s*){20,})\s*(\d+,\d+)\s+(\d+,\d+)\s+(\d+,\d+)\s*$',
            r'^([A-Z\-_0-9]+)\s+((?:\d+,\d+\s*){15,})\s*(\d+,\d+)\s+(\d+,\d+)\s+(\d+,\d+)',
        ],
        'hourly_values': [
            # Extract sequences of comma-decimal numbers
            r'(\d+,\d+)',
        ],
        'plant_name_clean': [
            # Clean extraction of plant names from start of line
            r'^([A-Z][A-Z\-_0-9]*[A-Z0-9])',
        ]
    }
    
    extracted_data = {
        'page': page_num,
        'chapter': 'ANEXO_02_REAL_GENERATION',
        'extraction_timestamp': datetime.now().isoformat(),
        'real_generation_records': [],
        'summary_metrics': {},
        'extraction_quality': {
            'raw_text_length': len(page_text),
            'ocr_text_length': len(ocr_text),
            'patterns_found': 0
        }
    }
    
    # Combine raw and OCR text for better coverage
    combined_text = page_text + "\n" + ocr_text
    lines = combined_text.split('\n')
    
    def convert_to_float(value_str):
        """Convert comma decimal to float"""
        try:
            return float(value_str.replace(',', '.'))
        except:
            return 0.0

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Try to extract tabular generation data (main pattern)
        for pattern in patterns['tabular_generation']:
            match = re.match(pattern, line)
            if match:
                plant_name = match.group(1)
                hourly_section = match.group(2)
                total_daily = convert_to_float(match.group(3))
                daily_max = convert_to_float(match.group(4))
                daily_avg = convert_to_float(match.group(5))
                
                # Extract hourly values
                hourly_values = []
                for hourly_match in re.finditer(r'(\d+,\d+)', hourly_section):
                    hourly_values.append(convert_to_float(hourly_match.group(1)))
                
                # Determine plant type
                plant_type = "UNKNOWN"
                if plant_name.startswith('PFV-'):
                    plant_type = "SOLAR_PV"
                elif plant_name.startswith('PMGD-PFV-'):
                    plant_type = "DISTRIBUTED_SOLAR_PV" 
                elif plant_name.startswith('PMGD-'):
                    plant_type = "DISTRIBUTED_GENERATION"
                
                # Calculate operational metrics
                operational_hours = sum(1 for v in hourly_values if v > 0.0)
                peak_hour = hourly_values.index(max(hourly_values)) + 1 if hourly_values else 0

                # Build hourly data with hour numbers
                hourly_data_with_hours = []
                for i, value in enumerate(hourly_values, 1):
                    hourly_data_with_hours.append({
                        "hour": i,
                        "value": value
                    })

                plant_data = {
                    'plant_name': plant_name,
                    'plant_type': plant_type,
                    'daily_total_mwh': total_daily,
                    'daily_max_mw': daily_max,
                    'daily_avg_mw': daily_avg,
                    'hourly_data': hourly_data_with_hours,
                    'operational_hours': operational_hours,
                    'peak_hour': peak_hour,
                    'source': 'tabular_extraction'
                }
                
                extracted_data['real_generation_records'].append({
                    'plant_name': plant_name,
                    'data': plant_data,
                    'source_line': i
                })
                extracted_data['extraction_quality']['patterns_found'] += 1
                break
        
        # Fallback: Try to extract just plant names for incomplete lines
        if not any(re.match(pattern, line) for pattern in patterns['tabular_generation']):
            for pattern in patterns['solar_plant']:
                match = re.match(pattern, line)
                if match:
                    plant_name = match.group(1)
                    
                    # Only add if not already found by tabular extraction
                    existing_names = [record['plant_name'] for record in extracted_data['real_generation_records']]
                    if plant_name not in existing_names:
                        plant_data = {
                            'plant_name': plant_name,
                            'plant_type': 'SOLAR_PV' if 'PFV' in plant_name else 'UNKNOWN',
                            'source': 'name_only_extraction'
                        }
                        
                        extracted_data['real_generation_records'].append({
                            'plant_name': plant_name,
                            'data': plant_data,
                            'source_line': i
                        })
                        extracted_data['extraction_quality']['patterns_found'] += 1
                    break
    
    # Calculate summary metrics for solar plant data
    if extracted_data['real_generation_records']:
        total_daily_mwh = sum(
            record['data'].get('daily_total_mwh', 0) 
            for record in extracted_data['real_generation_records']
            if isinstance(record['data'].get('daily_total_mwh'), (int, float))
        )
        max_capacity_mw = sum(
            record['data'].get('daily_max_mw', 0) 
            for record in extracted_data['real_generation_records']
            if isinstance(record['data'].get('daily_max_mw'), (int, float))
        )
        total_operational_hours = sum(
            record['data'].get('operational_hours', 0) 
            for record in extracted_data['real_generation_records']
            if isinstance(record['data'].get('operational_hours'), int)
        )
        
        # Classify plants by type
        solar_plants = [r for r in extracted_data['real_generation_records'] if r['data'].get('plant_type') == 'SOLAR_PV']
        distributed_solar = [r for r in extracted_data['real_generation_records'] if r['data'].get('plant_type') == 'DISTRIBUTED_SOLAR_PV']
        
        extracted_data['summary_metrics'] = {
            'total_plants': len(extracted_data['real_generation_records']),
            'solar_pv_plants': len(solar_plants),
            'distributed_solar_plants': len(distributed_solar),
            'total_daily_generation_mwh': total_daily_mwh,
            'total_max_capacity_mw': max_capacity_mw,
            'avg_operational_hours': total_operational_hours / len(extracted_data['real_generation_records']) if extracted_data['real_generation_records'] else 0,
            'system_type': 'RENEWABLE_SOLAR_FOCUSED'
        }
    
    # Determine data type and set summary metrics based on what was found
    has_plant_data = 'real_generation_records' in extracted_data and extracted_data['real_generation_records']
    has_system_data = 'system_summary_data' in extracted_data and extracted_data['system_summary_data']

    print(f"   🔧 DEBUG: Final check - extracted_data keys = {list(extracted_data.keys())}")  # Debug line
    print(f"   🔧 DEBUG: has_plant_data={has_plant_data}, has_system_data={has_system_data}")  # Debug line

    if has_plant_data and has_system_data:
        extracted_data['data_type'] = 'MIXED_DATA'
        print(f"   🔄 Mixed data page: {len(extracted_data['real_generation_records'])} plants + system summary")
        print(f"   🔧 DEBUG: has_system_data={has_system_data}, system_data_exists={'system_summary_data' in extracted_data}")  # Debug line
        # Add system summary metrics to existing plant metrics
        if has_system_data:
            system_metrics = {
                'system_categories': len(extracted_data['system_summary_data']),
                'has_total_sen': 'total_sen' in extracted_data['system_summary_data'],
                'has_demand_data': any('demanda' in k for k in extracted_data['system_summary_data'].keys()),
                'has_losses_data': any('perdidas' in k for k in extracted_data['system_summary_data'].keys()),
                'has_flow_data': 'flujo_changos_cumbres' in extracted_data['system_summary_data'],
                'data_completeness': 'COMPLETE' if len(extracted_data['system_summary_data']) >= 6 else 'PARTIAL'
            }
            if 'summary_metrics' in extracted_data:
                extracted_data['summary_metrics'].update(system_metrics)
            else:
                extracted_data['summary_metrics'] = system_metrics
    elif has_system_data:
        extracted_data['data_type'] = 'SYSTEM_OPERATIONAL_SUMMARY'
        extracted_data['chapter'] = 'ANEXO_02_SYSTEM_SUMMARY'
        extracted_data['summary_metrics'] = {
            'system_categories': len(extracted_data['system_summary_data']),
            'has_total_sen': 'total_sen' in extracted_data['system_summary_data'],
            'has_demand_data': any('demanda' in k for k in extracted_data['system_summary_data'].keys()),
            'has_losses_data': any('perdidas' in k for k in extracted_data['system_summary_data'].keys()),
            'has_flow_data': 'flujo_changos_cumbres' in extracted_data['system_summary_data'],
            'data_completeness': 'COMPLETE' if len(extracted_data['system_summary_data']) >= 6 else 'PARTIAL'
        }
    elif has_plant_data:
        extracted_data['data_type'] = 'PLANT_GENERATION'
    else:
        extracted_data['data_type'] = 'NO_DATA'

    # Set confidence level based on patterns found and data types
    confidence_score = extracted_data['extraction_quality']['patterns_found']
    if has_system_data:
        confidence_score += 5  # System data adds confidence

    if confidence_score >= 7:
        extracted_data['extraction_quality']['confidence'] = 'HIGH'
    elif confidence_score >= 3:
        extracted_data['extraction_quality']['confidence'] = 'MEDIUM'
    else:
        extracted_data['extraction_quality']['confidence'] = 'LOW'

    # Add date metadata
    date_metadata = extract_date_info(page_text)
    if date_metadata:
        extracted_data['date_metadata'] = date_metadata

    return extracted_data

def process_page(page_num: int, document_path: str) -> Dict:
    """Process a single page from ANEXO 2"""
    print(f"🔍 Processing ANEXO 2 page {page_num} (Real Generation Data)")
    
    # Extract text using both methods
    raw_text = extract_page_text(document_path, page_num)
    ocr_text = extract_ocr_text(document_path, page_num)
    
    if not raw_text and not ocr_text:
        print(f"⚠️  No text extracted from page {page_num}")
        return {}
    
    # Extract date information
    date_info = extract_date_info(raw_text)

    # Extract generation data
    extracted_data = extract_real_generation_data(raw_text, ocr_text, page_num)

    # Check if extraction was successful
    if not extracted_data:
        print(f"⚠️  No data extracted from page {page_num}")
        return {}

    # Add date information to metadata
    if date_info:
        extracted_data['date_metadata'] = date_info
    
    # Print results based on data type
    print(f"📊 Results for page {page_num}:")

    if extracted_data.get('system_summary_data'):
        system_data = extracted_data['system_summary_data']
        summary_count = len([k for k, v in system_data.items() if v.get('data_type') == 'hourly_series'])
        dmax_count = len([k for k, v in system_data.items() if v.get('data_type') == 'single_value'])
        print(f"   📈 System Summary: {summary_count} categories + {dmax_count} summary values")

    if extracted_data.get('real_generation_records'):
        print(f"   ✅ Found {len(extracted_data['real_generation_records'])} solar generation records")
        for record in extracted_data['real_generation_records'][:10]:  # Show first 10 only
            plant = record['plant_name']
            data = record['data']
            daily_total = data.get('daily_total_mwh', 'N/A')
            daily_max = data.get('daily_max_mw', 'N/A')
            op_hours = data.get('operational_hours', 'N/A')
            plant_type = data.get('plant_type', 'Unknown')
            print(f"      - {plant} ({plant_type}): Total={daily_total}MWh, Max={daily_max}MW, OpHours={op_hours}")
        if len(extracted_data['real_generation_records']) > 10:
            print(f"      ... and {len(extracted_data['real_generation_records']) - 10} more plants")
    elif not extracted_data.get('system_summary_data'):
        print(f"   ⚠️  No generation records found")

    print(f"   📈 Confidence: {extracted_data['extraction_quality']['confidence']}")
    print(f"   🏷️  Data Type: {extracted_data.get('data_type', 'UNKNOWN')}")

    return extracted_data

def main():
    """Main extraction function"""
    print("🚀 ANEXO 2 REAL GENERATION DATA EXTRACTOR")
    print("=" * 60)
    print("📄 Target: ANEXO 2 (Pages 63-95) - Real Generation Data")
    print("🎯 Focus: Actual generation vs programmed generation")
    print("=" * 60)
    
    # Find PDF file
    document_path = find_pdf_file()
    if not document_path:
        # Try direct path
        direct_path = "/home/alonso/Documentos/Github/Proyecto Dark Data CEN/data/documents/anexos_EAF/source_documents/Anexos-EAF-089-2025.pdf"
        if Path(direct_path).exists():
            document_path = direct_path
        else:
            print("❌ EAF PDF file not found!")
            print("   Please place Anexos-EAF-089-2025.pdf in:")
            print("   - data/documents/anexos_EAF/source_documents/")
            print("   - data/documents/anexos_EAF/samples_and_tests/")
            return
    
    print(f"📁 Found PDF: {document_path}")
    
    # Process pages
    if len(sys.argv) > 1 and sys.argv[1] == '--all':
        # Process all ANEXO 2 pages (63-95)
        print("📊 Processing all ANEXO 2 pages (63-95)...")
        all_results = []
        
        for page_num in range(63, 96):  # Pages 63-95
            try:
                result = process_page(page_num, document_path)
                if result:
                    all_results.append(result)
                print()  # Empty line between pages
            except Exception as e:
                print(f"❌ Error processing page {page_num}: {e}")
        
        # Save combined results
        if all_results:
            output_file = project_root / "data" / "documents" / "anexos_EAF" / "extractions" / "anexo_02_real_generation" / f"anexo2_real_generation_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved complete results to: {output_file}")
    
    else:
        # Process single page
        page_num = int(sys.argv[1]) if len(sys.argv) > 1 else 65  # Default to page 65
        
        if not (63 <= page_num <= 95):
            print(f"⚠️  Page {page_num} is outside ANEXO 2 range (63-95)")
            print("   Using default page 65...")
            page_num = 65
        
        result = process_page(page_num, document_path)
        
        if result:
            # Save single page result
            output_file = project_root / "data" / "documents" / "anexos_EAF" / "extractions" / "anexo_02_real_generation" / f"anexo2_page_{page_num}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved results to: {output_file}")

if __name__ == "__main__":
    main()