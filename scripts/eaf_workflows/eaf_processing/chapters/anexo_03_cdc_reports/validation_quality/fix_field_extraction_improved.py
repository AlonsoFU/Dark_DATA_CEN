#!/usr/bin/env python3
"""
Fix Field Extraction - Improved Parser
======================================

Fixes extraction for columns BAJA, SUBE, (kV, MVAr, MW) and Motivo
by using pattern matching approach similar to "Fecha de Edición".
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

project_root = Path(__file__).parent.parent.parent.parent.parent.parent.parent

def extract_field_patterns(text: str) -> Dict[str, str]:
    """Extract BAJA, SUBE, (kV, MVAr, MW) and Motivo using pattern matching"""

    fields = {
        "BAJA": "",
        "SUBE": "",
        "(kV, MVAr, MW)": "",
        "Motivo": ""
    }

    # BAJA/SUBE pattern - look for these exact words
    if re.search(r'\bBAJA\b', text, re.IGNORECASE):
        fields["BAJA"] = "BAJA"
    if re.search(r'\bSUBE\b', text, re.IGNORECASE):
        fields["SUBE"] = "SUBE"

    # (kV, MVAr, MW) pattern - look for units
    unit_pattern = r'\b(kV|MVAr|MW)\b'
    unit_match = re.search(unit_pattern, text, re.IGNORECASE)
    if unit_match:
        fields["(kV, MVAr, MW)"] = unit_match.group(1)

    # Motivo pattern - look for control frequency patterns
    control_patterns = [
        r'Participación en control Primario de frecuencia CPF \([+-]\)',
        r'Participación en control Secundario de frecuencia CSF \([+-]\)',
        r'Participación en control Terciario de frecuencia CTF \([+-]\)',
        r'control Primario de frecuencia CPF \([+-]\)',
        r'control Secundario de frecuencia CSF \([+-]\)',
        r'control Terciario de frecuencia CTF \([+-]\)',
        r'Primario de frecuencia CPF \([+-]\)',
        r'Secundario de frecuencia CSF \([+-]\)',
        r'Terciario de frecuencia CTF \([+-]\)'
    ]

    for pattern in control_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            control_text = match.group(0)
            if not control_text.lower().startswith('participación'):
                fields["Motivo"] = f"Participación en {control_text}"
            else:
                fields["Motivo"] = control_text
            break

    return fields

def clean_comentario_after_extraction(comentario_text: str, extracted_fields: Dict[str, str]) -> str:
    """Remove extracted field content from comentario"""

    if not comentario_text:
        return ""

    cleaned = comentario_text

    # Remove extracted patterns
    for field_value in extracted_fields.values():
        if field_value and field_value.strip():
            cleaned = cleaned.replace(field_value, "").strip()

    # Remove common artifacts
    patterns_to_remove = [
        r'\bBAJA\b',
        r'\bSUBE\b',
        r'\b(kV|MVAr|MW)\b',
        r'Participación en control \w+ de frecuencia \w+ \([+-]\)',
        r'control \w+ de frecuencia \w+ \([+-]\)',
        r'\w+ de frecuencia \w+ \([+-]\)',
        r'sinv\s+',
        r'vrucu_quill\s+',
        r'^\w+\s+\d*\s+'
    ]

    for pattern in patterns_to_remove:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

    # Clean up spacing and artifacts
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # If only symbols/numbers left, return empty
    if re.match(r'^[\(\)\+\-\.\s\d]*$', cleaned):
        return ""

    return cleaned

def fix_json_file(file_path: Path) -> Dict[str, Any]:
    """Fix field extraction in a JSON file"""

    print(f"🔄 Processing {file_path.name}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        fixes_applied = 0
        total_records = 0

        if 'centrales_data' in data:
            for record in data['centrales_data']:
                total_records += 1

                # Get full text from comentario to extract fields
                comentario_text = record.get('Comentario', '')

                if comentario_text.strip():
                    # Extract fields using pattern matching
                    extracted_fields = extract_field_patterns(comentario_text)

                    # Update fields if they were empty and we found content
                    for field_name, field_value in extracted_fields.items():
                        if field_value and not record.get(field_name, '').strip():
                            record[field_name] = field_value
                            fixes_applied += 1

                    # Clean comentario after extraction
                    cleaned_comentario = clean_comentario_after_extraction(comentario_text, extracted_fields)
                    if cleaned_comentario != comentario_text:
                        record['Comentario'] = cleaned_comentario
                        fixes_applied += 1

        # Add metadata
        if 'extraction_metadata' not in data:
            data['extraction_metadata'] = {}

        data['extraction_metadata']['field_extraction_fixes'] = {
            'timestamp': datetime.now().isoformat(),
            'fixes_count': fixes_applied,
            'total_records': total_records,
            'script_version': 'fix_field_extraction_improved_v1.0'
        }

        # Save file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✅ Fixed {fixes_applied} field extractions in {total_records} records")

        return {
            'file': str(file_path),
            'fixes_applied': fixes_applied,
            'total_records': total_records,
            'status': 'success'
        }

    except Exception as e:
        print(f"❌ Error processing {file_path.name}: {e}")
        return {
            'file': str(file_path),
            'fixes_applied': 0,
            'total_records': 0,
            'status': 'error',
            'error': str(e)
        }

def main():
    """Main function"""

    print("🔧 Fixing field extraction for BAJA, SUBE, (kV, MVAr, MW) and Motivo...")

    extraction_dir = project_root / "data" / "documents" / "anexos_EAF" / "extractions" / "anexo_03_cdc_reports"

    if not extraction_dir.exists():
        print(f"❌ Directory not found: {extraction_dir}")
        return

    json_files = list(extraction_dir.glob("*.json"))

    if not json_files:
        print(f"❌ No JSON files found in {extraction_dir}")
        return

    print(f"📁 Found {len(json_files)} JSON files to process")

    results = []
    total_fixes = 0

    for json_file in json_files:
        result = fix_json_file(json_file)
        results.append(result)
        total_fixes += result['fixes_applied']

    # Summary
    successful_files = [r for r in results if r['status'] == 'success']
    failed_files = [r for r in results if r['status'] == 'error']

    print(f"\n📊 Fix Summary:")
    print(f"   Files processed: {len(json_files)}")
    print(f"   Successful: {len(successful_files)}")
    print(f"   Failed: {len(failed_files)}")
    print(f"   Total fixes applied: {total_fixes}")

    # Save report
    report = {
        'fix_timestamp': datetime.now().isoformat(),
        'total_files_processed': len(json_files),
        'total_fixes_applied': total_fixes,
        'successful_files': len(successful_files),
        'failed_files': len(failed_files),
        'file_results': results
    }

    report_file = extraction_dir / f"field_extraction_fix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"📄 Fix report saved to: {report_file}")

if __name__ == "__main__":
    main()