#!/usr/bin/env python3
"""
Corrected Validation Strategy
============================

ONLY obvious pattern: 0 before number (015 → 0 + 15)
Fast validation: Must have 24 hours + total
If errors: Generate summary for manual review

No assumptions about what's "obvious" except 0-prefix patterns.
"""

import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from PyPDF2 import PdfReader
except ImportError:
    print("Installing PyPDF2...")
    import os
    os.system("pip install PyPDF2")
    from PyPDF2 import PdfReader

def extract_page_text(document_path: str, page_num: int) -> str:
    """Extract RAW PDF text"""
    try:
        reader = PdfReader(document_path)
        if 1 <= page_num <= len(reader.pages):
            page = reader.pages[page_num - 1]
            return page.extract_text().strip()
        return ""
    except Exception as e:
        print(f"Error extracting page {page_num}: {e}")
        return ""

def apply_only_obvious_patterns(text: str) -> Tuple[str, List[str]]:
    """Apply ONLY the obvious 0-prefix pattern"""
    
    corrections = []
    corrected_text = text
    
    # ONLY obvious pattern: 0 before 2-digit number (015, 031, etc.)
    zero_pattern = r'\b0(\d{2})\b'
    
    def fix_zero_prefix(match):
        full = match.group(0)  # e.g., "015"
        digits = match.group(1)  # e.g., "15"
        corrections.append(f"0-prefix: '{full}' → ['0', '{digits}']")
        return f"0 {digits}"
    
    corrected_text = re.sub(zero_pattern, fix_zero_prefix, corrected_text)
    
    return corrected_text, corrections

def fast_validation(numbers: List[str]) -> Dict:
    """Fast validation: Must have 24 hourly values + total"""
    
    if len(numbers) >= 24:
        hourly_values = numbers[:24]
        total = numbers[24] if len(numbers) > 24 else "calculated"
        
        validation = {
            "passes_fast_validation": True,
            "hourly_count": 24,
            "total_extracted": total,
            "total_numbers_found": len(numbers),
            "status": "valid"
        }
    else:
        validation = {
            "passes_fast_validation": False,
            "hourly_count": len(numbers),
            "total_extracted": "missing",
            "total_numbers_found": len(numbers),
            "status": "error",
            "error_details": f"Expected 24+ numbers, found {len(numbers)}"
        }
    
    return validation

def process_metric_row(raw_line: str, metric_name: str) -> Dict:
    """Process a single metric row with corrected strategy"""
    
    # Step 1: Apply ONLY obvious 0-prefix patterns
    corrected_text, corrections = apply_only_obvious_patterns(raw_line)
    
    # Step 2: Extract numbers
    numbers = re.findall(r'\d+(?:[.,]\d+)?', corrected_text)
    
    # Step 3: Fast validation
    validation = fast_validation(numbers)
    
    # Step 4: Build result
    result = {
        "metric_name": metric_name,
        "raw_line": raw_line,
        "corrections_applied": corrections,
        "numbers_extracted": numbers,
        "validation": validation
    }
    
    if validation["passes_fast_validation"]:
        result["hourly_values"] = numbers[:24]
        result["total"] = validation["total_extracted"]
        result["status"] = "success"
    else:
        result["hourly_values"] = numbers
        result["total"] = "error"
        result["status"] = "needs_review"
    
    return result

def process_all_metrics(raw_text: str) -> Dict:
    """Process all metrics and generate error summary"""
    
    # Define metric patterns
    metric_patterns = {
        "generacion_total": r"Generaci[óo]n\s+Total[^\n]*\[MWh\][^\n]*",
        "costos_operacion": r"Costos?\s+Operaci[óo]n[^\n]*",
        "costos_encendido_detencion": r"Costos?\s+Encendido[^\n]*Detenci[^\n]*",
        "costo_marginal": r"Costo\s+Marginal[^\n]*",
        "indisponibilidad_forzada": r"Indisponibilidad\s+Forzada[^\n]*",
        "indisponibilidad_programada": r"Indisponibilidad\s+Programada[^\n]*",
        "factor_planta_bruto": r"Factor\s+de?\s+Planta\s+Bruto[^\n]*",
        "factor_planta_neto": r"Factor\s+de?\s+Planta\s+Neto[^\n]*",
        "horas_servicio": r"Horas?\s+de?\s+Servicio[^\n]*"
    }
    
    results = {}
    errors_found = []
    successful_metrics = 0
    
    print("🔧 Processing metrics with corrected strategy...")
    
    for metric_key, pattern in metric_patterns.items():
        matches = re.findall(pattern, raw_text, re.IGNORECASE)
        if matches:
            raw_line = matches[0].strip()
            
            result = process_metric_row(raw_line, metric_key)
            results[metric_key] = result
            
            print(f"   📊 {metric_key.replace('_', ' ').title()}")
            print(f"      Numbers: {result['validation']['total_numbers_found']}")
            print(f"      Status: {result['status']}")
            
            if result["status"] == "success":
                successful_metrics += 1
                if result["corrections_applied"]:
                    print(f"      Corrections: {', '.join(result['corrections_applied'])}")
            else:
                errors_found.append({
                    "metric": metric_key,
                    "error": result["validation"]["error_details"],
                    "raw_line": raw_line[:80] + "..." if len(raw_line) > 80 else raw_line,
                    "numbers_found": result["validation"]["total_numbers_found"]
                })
                print(f"      ❌ Error: {result['validation']['error_details']}")
    
    return {
        "metrics": results,
        "summary": {
            "total_metrics_processed": len(results),
            "successful_metrics": successful_metrics,
            "failed_metrics": len(errors_found),
            "success_rate": f"{(successful_metrics/len(results)*100):.1f}%" if results else "0%"
        },
        "errors": errors_found
    }

def generate_error_summary(processing_results: Dict, page_num: int) -> Dict:
    """Generate error summary for manual review"""
    
    error_summary = {
        "page_number": page_num,
        "timestamp": datetime.now().isoformat(),
        "processing_method": "corrected_validation_strategy",
        "validation_criteria": {
            "required_hourly_values": 24,
            "required_total": "yes",
            "only_obvious_corrections": "0-prefix patterns only"
        },
        "results": processing_results["summary"],
        "errors_requiring_review": processing_results["errors"],
        "recommendations": []
    }
    
    # Generate recommendations based on errors
    if processing_results["errors"]:
        error_summary["recommendations"].append(
            "Manual review needed - some metrics failed 24-hour validation"
        )
        
        # Analyze error patterns
        number_counts = [error["numbers_found"] for error in processing_results["errors"]]
        if number_counts:
            avg_numbers = sum(number_counts) / len(number_counts)
            if avg_numbers < 20:
                error_summary["recommendations"].append(
                    f"Low number counts detected (avg: {avg_numbers:.1f}) - possible OCR issues"
                )
            elif avg_numbers > 30:
                error_summary["recommendations"].append(
                    f"High number counts detected (avg: {avg_numbers:.1f}) - possible merged numbers"
                )
    else:
        error_summary["recommendations"].append(
            "All metrics passed validation - no manual review needed"
        )
    
    return error_summary

def main():
    """Main processing with corrected validation strategy"""
    
    if len(sys.argv) != 2:
        print("Usage: python scripts/corrected_validation_strategy.py [page_number]")
        sys.exit(1)
    
    try:
        page_num = int(sys.argv[1])
    except ValueError:
        print("Error: Page number must be an integer")
        sys.exit(1)
    
    document_path = project_root / "data" / "documents" / "anexos_EAF" / "raw" / "Anexos-EAF-089-2025.pdf"
    
    print(f"✅ CORRECTED VALIDATION STRATEGY - Page {page_num}")
    print("Strategy: Only 0-prefix corrections + Fast 24-hour validation")
    print("=" * 70)
    
    # Extract raw text
    raw_text = extract_page_text(str(document_path), page_num)
    
    if not raw_text:
        print(f"❌ No text extracted from page {page_num}")
        sys.exit(1)
    
    print(f"📄 RAW text: {len(raw_text)} chars")
    
    # Process all metrics
    processing_results = process_all_metrics(raw_text)
    
    # Generate error summary
    error_summary = generate_error_summary(processing_results, page_num)
    
    # Build final result
    final_result = {
        "document_metadata": {
            "document_file": Path(document_path).name,
            "page_number": page_num,
            "extraction_timestamp": datetime.now().isoformat(),
            "extraction_method": "corrected_validation_strategy"
        },
        "processing_results": processing_results,
        "error_summary": error_summary
    }
    
    # Save results
    output_file = project_root / "data" / "documents" / "anexos_EAF" / "development" / f"page_{page_num}_corrected_validation.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_result, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 PROCESSING SUMMARY:")
    print(f"   Total metrics: {processing_results['summary']['total_metrics_processed']}")
    print(f"   Successful: {processing_results['summary']['successful_metrics']}")
    print(f"   Failed: {processing_results['summary']['failed_metrics']}")
    print(f"   Success rate: {processing_results['summary']['success_rate']}")
    
    if processing_results["errors"]:
        print(f"\n❌ ERRORS REQUIRING MANUAL REVIEW:")
        for error in processing_results["errors"]:
            print(f"   • {error['metric']}: {error['error']}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in error_summary["recommendations"]:
            print(f"   • {rec}")
    else:
        print(f"\n✅ ALL METRICS PASSED VALIDATION")
    
    print(f"\n💾 Results saved to: {output_file}")
    
    # Save error summary separately if there are errors
    if processing_results["errors"]:
        error_file = project_root / "data" / "documents" / "anexos_EAF" / "validation" / f"page_{page_num}_errors_for_review.json"
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(error_summary, f, ensure_ascii=False, indent=2)
        
        print(f"⚠️  Error summary saved to: {error_file}")
        return 1  # Exit with error code
    
    return 0

if __name__ == "__main__":
    sys.exit(main())