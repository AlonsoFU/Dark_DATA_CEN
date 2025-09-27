#!/usr/bin/env python3
"""
Fix Motivo Extraction Errors
============================

This script fixes OCR extraction errors in the "Motivo" field where text from multiple
columns gets incorrectly merged together.

Common error patterns:
- "sinv MW Participación en control Primario de frecuencia CPF (+)."
- "vrucu_quill MW Participación en control Primario de frecuencia CPF (-)."

Expected clean format:
- "Participación en control Primario de frecuencia CPF (+)."
- "Participación en control Primario de frecuencia CPF (-)."
- "Participación en control Secundario de frecuencia CSF (+)."
- "Participación en control Terciario de frecuencia CTF (-)."
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Project root
project_root = Path(__file__).parent.parent.parent.parent.parent.parent.parent

def clean_motivo_field(motivo_text: str) -> str:
    """Clean the motivo field by removing OCR artifacts and invalid text"""

    if not motivo_text or motivo_text.strip() == "":
        return ""

    # Remove common OCR artifacts at the beginning
    artifacts = [
        r'^sinv\s+',
        r'^vrucu_quill\s+',
        r'^\w+\s+\d*\.\d*\s+',  # Remove plant names followed by numbers
        r'^\w+\s+\d+\s+',       # Remove plant names followed by integers
        r'^[A-Z0-9_]+\s+\d*\s+', # Remove uppercase codes
    ]

    cleaned = motivo_text.strip()

    for artifact_pattern in artifacts:
        cleaned = re.sub(artifact_pattern, '', cleaned, flags=re.IGNORECASE)

    # Remove excessive whitespace and MW units that don't belong
    cleaned = re.sub(r'\s*MW\s+', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # Extract valid control participation patterns
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
        match = re.search(pattern, cleaned, re.IGNORECASE)
        if match:
            # Return the clean control participation text
            control_text = match.group(0)
            # Ensure proper capitalization
            if control_text.lower().startswith('participación'):
                return f"Participación en {control_text[15:]}"
            elif control_text.lower().startswith('control'):
                return f"Participación en {control_text}"
            else:
                return f"Participación en control {control_text}"

    # If no control pattern found but has valid content, clean and return
    if len(cleaned) > 5 and not re.match(r'^[\(\)\+\-\.\s]*$', cleaned):
        return cleaned

    # If nothing meaningful left, return empty
    return ""

def clean_comentario_field(comentario_text: str) -> str:
    """Clean the comentario field by removing OCR artifacts"""

    if not comentario_text or comentario_text.strip() == "":
        return ""

    cleaned = comentario_text.strip()

    # Remove common OCR artifacts
    artifacts = [
        r'^sinv\s+',
        r'^vrucu_quill\s+',
        r'^\w+\s+\d+\s+MW\s+',  # Remove plant names with MW values
    ]

    for artifact_pattern in artifacts:
        cleaned = re.sub(artifact_pattern, '', cleaned, flags=re.IGNORECASE)

    # Clean up spacing
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # If only symbols left, return empty
    if re.match(r'^[\(\)\+\-\.\s]*$', cleaned):
        return ""

    return cleaned

def fix_json_file(file_path: Path) -> Dict[str, Any]:
    """Fix a single JSON file by cleaning Motivo and Comentario fields"""

    print(f"🔄 Processing {file_path.name}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        fixes_applied = 0
        total_records = 0

        # Process centrales_data if it exists
        if 'centrales_data' in data:
            for record in data['centrales_data']:
                total_records += 1

                # Fix Motivo field
                if 'Motivo' in record:
                    original_motivo = record['Motivo']
                    cleaned_motivo = clean_motivo_field(original_motivo)
                    if cleaned_motivo != original_motivo:
                        record['Motivo'] = cleaned_motivo
                        fixes_applied += 1

                # Fix Comentario field
                if 'Comentario' in record:
                    original_comentario = record['Comentario']
                    cleaned_comentario = clean_comentario_field(original_comentario)
                    if cleaned_comentario != original_comentario:
                        record['Comentario'] = cleaned_comentario
                        fixes_applied += 1

        # Add fix metadata
        if 'extraction_metadata' not in data:
            data['extraction_metadata'] = {}

        data['extraction_metadata']['motivo_fixes_applied'] = {
            'timestamp': datetime.now().isoformat(),
            'fixes_count': fixes_applied,
            'total_records': total_records,
            'script_version': 'fix_motivo_extraction_errors_v1.0'
        }

        # Save fixed file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✅ Fixed {fixes_applied} issues in {total_records} records")

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
    """Main function to fix all JSON files in anexo_03_cdc_reports"""

    print("🔧 Fixing Motivo extraction errors in ANEXO 3 CDC Reports...")

    # Find all JSON files in anexo_03_cdc_reports
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

    # Print summary
    successful_files = [r for r in results if r['status'] == 'success']
    failed_files = [r for r in results if r['status'] == 'error']

    print(f"\n📊 Fix Summary:")
    print(f"   Files processed: {len(json_files)}")
    print(f"   Successful: {len(successful_files)}")
    print(f"   Failed: {len(failed_files)}")
    print(f"   Total fixes applied: {total_fixes}")

    if failed_files:
        print(f"\n❌ Failed files:")
        for failed in failed_files:
            print(f"   - {Path(failed['file']).name}: {failed['error']}")

    # Save fix report
    report = {
        'fix_timestamp': datetime.now().isoformat(),
        'total_files_processed': len(json_files),
        'total_fixes_applied': total_fixes,
        'successful_files': len(successful_files),
        'failed_files': len(failed_files),
        'file_results': results
    }

    report_file = extraction_dir / f"motivo_fix_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"📄 Fix report saved to: {report_file}")

if __name__ == "__main__":
    main()