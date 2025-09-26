#!/usr/bin/env python3
"""
Page 79 System Summary Data Extractor
=====================================

Specialized extractor for page 79 system-wide operational summary data:
- TOTAL HORA (system total hours)
- TOTAL SEN (total national electric system)
- CONS. PROPIOS (own consumption)
- FLUJO CHANGOS->CUMBRES (power flow between substations)
- PERDIDAS APROX. (approximate losses)
- DEMANDA APROX. (approximate demand)

Usage:
    python extract_page79_system_summary.py
"""

import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add project root to path (go up 6 levels)
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.append(str(project_root))

try:
    from PyPDF2 import PdfReader
except ImportError:
    import os
    os.system("pip install PyPDF2")
    from PyPDF2 import PdfReader

def extract_date_info(raw_text: str) -> Dict:
    """Extract date information from the beginning of the page"""
    date_patterns = [
        r'(\d{2}-\d{2}-\d{4})\s+(\d{2}-\d{2}-\d{4})',  # "25-02-2025 25-02-2025"
        r'(\d{2}-\d{2}-\d{4})',  # Single date
        r'RESUMEN DIARIO DE OPERACION DEL SEN\s*(\d{2}-\d{2}-\d{4})'  # With header
    ]

    for pattern in date_patterns:
        match = re.search(pattern, raw_text)
        if match:
            if len(match.groups()) >= 2:
                return {
                    "operation_date": match.group(1),
                    "report_date": match.group(2),
                    "date_format": "DD-MM-YYYY",
                    "source": "extracted_from_header",
                    "document_type": "daily_operation_summary"
                }
            else:
                return {
                    "operation_date": match.group(1),
                    "date_format": "DD-MM-YYYY",
                    "source": "extracted_from_header",
                    "document_type": "daily_operation_summary"
                }

    return {}

def extract_system_summary_data(raw_text: str) -> Dict:
    """Extract system-wide summary data from page 79"""

    system_data = {}

    # System summary patterns - more flexible to match the actual data structure
    patterns = {
        'total_hora': r'TOTAL HORA\.\s+([\d,\s.-]+?)\s+121\.538',  # Main TOTAL HORA ending with total
        'total_hora_sing': r'TOTAL HORA\.\s+SING\s+([\d,\s.-]+?)(?:\s+TOTAL|\s+\d{2}\.?\d*\s*$)',
        'total_sen': r'TOTAL SEN\s+([\d,\s.-]+?)(?:\s+CONS\.|\s+\d{3}\.?\d*\s*$)',
        'cons_propios': r'CONS\.\s+PROPIOS\s+([\d,\s.-]+?)(?:\s+CONS\.|\s+\d\.?\d*\s*$)',
        'cons_propios_sing': r'CONS\.\s+PROPIOS\s+SING\s+([\d,\s.-]+?)(?:\s+FLUJO|\s+\d{3}\s*$)',
        'flujo_changos_cumbres': r'FLUJO\s+CHANGOS->CUMBRES\s+([\d,\s.-]+?)(?:\s+PERDIDAS|\s+-?\d\.?\d*\s*$)',
        'perdidas_aprox': r'PERDIDAS\s+APROX\.\s+([\d,\s.-]+?)(?:\s+PERDIDAS|\s+\d\.?\d*\s*$)',
        'perdidas_aprox_sing': r'PERDIDAS\s+APROX\.\s+SING\s+([\d,\s.-]+?)(?:\s+DEMANDA|\s+\d{3}\s*$)',
        'demanda_aprox': r'DEMANDA\s+APROX\.\s+([\d,\s.-]+?)(?:\s+DEMANDA|\s+\d{6}\.?\d*\s*$)',
        'demanda_aprox_sing': r'DEMANDA\s+APROX\.\s+SING\s+([\d,\s.-]+?)(?:\s+HORA|\s+\d{5}\.?\d*\s*$)',
        'dmax_total': r'DMAX\s*:\s*([\d,]+)'  # Final DMAX value
    }

    print("🔍 Extracting system summary data...")

    for system_type, pattern in patterns.items():
        match = re.search(pattern, raw_text, re.IGNORECASE | re.DOTALL)
        if match:
            values_text = match.group(1).strip()
            print(f"   📊 Found {system_type}: {values_text[:100]}...")

            # Handle DMAX specially (single value, not hourly)
            if system_type == 'dmax_total':
                try:
                    dmax_value = float(values_text.replace(',', '.'))
                    system_data[system_type] = {
                        "value": dmax_value,
                        "system_category": "Daily Maximum Total",
                        "source": "system_summary_extraction",
                        "data_type": "single_value"
                    }
                    print(f"   ✅ {system_type}: DMAX = {dmax_value}")
                except ValueError:
                    continue
            else:
                # Parse hourly values
                hourly_values = []

                # Split and clean values
                value_parts = re.findall(r'-?\d+(?:,\d+)?', values_text)
                for part in value_parts[:24]:  # Only take first 24 hours
                    try:
                        # Convert comma decimal to float
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

                    print(f"   ✅ {system_type}: {len(hourly_values)} data points, Total={daily_total:.1f}")

    return system_data

def find_pdf_file():
    """Find the PDF file in the expected location"""
    possible_paths = [
        project_root / "data" / "documents" / "anexos_EAF" / "source_documents" / "Anexos-EAF-089-2025.pdf",
        project_root / "data_real" / "Anexos-EAF-089-2025.pdf",
    ]

    for path in possible_paths:
        if path.exists():
            return path

    raise FileNotFoundError("Could not find Anexos-EAF-089-2025.pdf in expected locations")

def main():
    print("🚀 PAGE 79 SYSTEM SUMMARY EXTRACTOR")
    print("=" * 60)
    print("📄 Target: Page 79 - System-wide operational summary")
    print("🎯 Focus: TOTAL HORA, TOTAL SEN, CONS. PROPIOS, FLUJO, PERDIDAS, DEMANDA")
    print("=" * 60)

    # Find PDF file
    try:
        document_path = find_pdf_file()
        print(f"📁 Found PDF: {document_path}")
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return

    # Extract page 79 (index 78)
    try:
        reader = PdfReader(document_path)
        page = reader.pages[78]  # Page 79 (0-indexed)
        raw_text = page.extract_text()

        print(f"🔍 Processing page 79 - System Summary Data")

        # Extract date metadata
        date_metadata = extract_date_info(raw_text)

        # Extract system summary data
        system_summary = extract_system_summary_data(raw_text)

        if system_summary:
            # Build final result
            result = {
                "page": 79,
                "chapter": "ANEXO_02_SYSTEM_SUMMARY",
                "extraction_timestamp": datetime.now().isoformat(),
                "data_type": "SYSTEM_OPERATIONAL_SUMMARY",
                "system_summary_data": system_summary,
                "summary_metrics": {
                    "system_categories": len(system_summary),
                    "has_total_sen": "total_sen" in system_summary,
                    "has_demand_data": any("demanda" in k for k in system_summary.keys()),
                    "has_losses_data": any("perdidas" in k for k in system_summary.keys()),
                    "has_flow_data": "flujo_changos_cumbres" in system_summary,
                    "data_completeness": "COMPLETE" if len(system_summary) >= 6 else "PARTIAL"
                },
                "extraction_quality": {
                    "raw_text_length": len(raw_text),
                    "system_categories_found": len(system_summary),
                    "confidence": "HIGH" if len(system_summary) >= 4 else "MEDIUM"
                }
            }

            # Add date metadata if available
            if date_metadata:
                result["date_metadata"] = date_metadata

            # Save results
            output_file = project_root / "extractions" / "anexo_02_real_generation" / f"anexo2_page79_system_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            print(f"📊 Results for page 79:")
            print(f"   ✅ Found {len(system_summary)} system categories")
            for category in system_summary.keys():
                if system_summary[category].get('data_type') == 'single_value':
                    value = system_summary[category]['value']
                    print(f"      - {category.replace('_', ' ').title()}: DMAX = {value:.1f}")
                else:
                    data_points = len(system_summary[category]['hourly_data'])
                    total = system_summary[category]['daily_total']
                    print(f"      - {category.replace('_', ' ').title()}: {data_points} hours, Total={total:.1f}")

            print(f"💾 Saved results to: {output_file}")

        else:
            print("❌ No system summary data found on page 79")

    except Exception as e:
        print(f"❌ Error processing page 79: {e}")

if __name__ == "__main__":
    main()