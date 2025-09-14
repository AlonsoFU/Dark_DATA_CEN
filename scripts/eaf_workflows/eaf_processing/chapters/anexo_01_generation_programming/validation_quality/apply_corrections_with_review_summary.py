
#!/usr/bin/env python3
"""
Apply Corrections with Review Summary
====================================

Strategy:
1. Apply ALL known corrections (including your validated patterns)
2. Generate review summary showing:
   - ✅ What was corrected successfully  
   - ❌ What still has errors after corrections
   - 📊 Overall success/failure status

This way you can see both what worked AND what still needs attention.
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

def apply_all_known_corrections(text: str) -> Tuple[str, List[Dict]]:
    """Apply all known correction patterns and track what was applied"""
    
    corrections_applied = []
    corrected_text = text
    
    # 1. Your validated specific corrections
    specific_corrections = {
        '198105': '1 98 105',      # Your validated correction
        '980310125': '9803 10125',  # 9-digit merge we worked on together
        '99210': '992 10'          # Operation costs merge
    }
    
    for wrong, correct in specific_corrections.items():
        if wrong in corrected_text:
            corrected_text = corrected_text.replace(wrong, correct)
            corrections_applied.append({
                "type": "specific_pattern",
                "original": wrong,
                "corrected": correct.split(),
                "description": f"Specific validated pattern: '{wrong}' → {correct.split()}"
            })
    
    # 2. Zero-prefix patterns (obviously wrong)
    zero_prefix_matches = list(re.finditer(r'\b0(\d{2})\b', corrected_text))
    for match in reversed(zero_prefix_matches):  # Reverse to avoid position shifts
        full = match.group(0)  # e.g., "015"
        digits = match.group(1)  # e.g., "15"
        replacement = f"0 {digits}"
        
        corrected_text = corrected_text[:match.start()] + replacement + corrected_text[match.end():]
        corrections_applied.append({
            "type": "zero_prefix",
            "original": full,
            "corrected": ["0", digits],
            "description": f"Zero-prefix: '{full}' → ['0', '{digits}']"
        })
    
    # 3. Decimal comma fixes
    comma_fixes = list(re.finditer(r'(\d),(\d)', corrected_text))
    for match in reversed(comma_fixes):
        original = match.group(0)
        replacement = f"{match.group(1)}.{match.group(2)}"
        corrected_text = corrected_text[:match.start()] + replacement + corrected_text[match.end():]
        corrections_applied.append({
            "type": "decimal_comma",
            "original": original,
            "corrected": [replacement],
            "description": f"Decimal comma: '{original}' → '{replacement}'"
        })
    
    return corrected_text, corrections_applied

def validate_metric_after_corrections(numbers: List[str]) -> Dict:
    """Validate metric after all corrections are applied"""
    
    if len(numbers) >= 24:
        validation = {
            "is_valid": True,
            "hourly_count": 24,
            "total_available": len(numbers) > 24,
            "total_value": numbers[24] if len(numbers) > 24 else "calculated",
            "extra_numbers": len(numbers) - 25 if len(numbers) > 25 else 0,
            "status": "success",
            "issues": []
        }
        
        if len(numbers) < 25:
            validation["issues"].append("No total value found")
        elif len(numbers) > 25:
            validation["issues"].append(f"Extra {len(numbers) - 25} numbers found")
            
    else:
        validation = {
            "is_valid": False,
            "hourly_count": len(numbers),
            "total_available": False,
            "total_value": "missing",
            "extra_numbers": 0,
            "status": "error",
            "issues": [f"Only {len(numbers)} numbers found, need 24+ for valid hourly data"]
        }
    
    return validation

def process_single_metric(raw_line: str, metric_name: str) -> Dict:
    """Process a single metric with corrections and validation"""
    
    # Step 1: Apply all known corrections
    corrected_text, corrections_applied = apply_all_known_corrections(raw_line)
    
    # Step 2: Extract numbers from corrected text
    numbers = re.findall(r'\d+(?:[.,]\d+)?', corrected_text)
    
    # Step 3: Validate after corrections
    validation = validate_metric_after_corrections(numbers)
    
    # Step 4: Build result
    result = {
        "metric_name": metric_name,
        "raw_line": raw_line,
        "corrected_text": corrected_text,
        "corrections_applied": corrections_applied,
        "numbers_extracted": numbers,
        "numbers_count": len(numbers),
        "validation": validation,
        "final_status": validation["status"]
    }
    
    # Add hourly values and total if valid
    if validation["is_valid"]:
        result["hourly_values"] = numbers[:24]
        result["total"] = validation["total_value"]
    else:
        result["hourly_values"] = numbers
        result["total"] = "error"
    
    return result

def generate_review_summary(all_results: Dict, page_num: int) -> Dict:
    """Generate comprehensive review summary"""
    
    # Categorize results
    successful_metrics = []
    corrected_metrics = []
    failed_metrics = []
    
    total_corrections = 0
    
    for metric_name, result in all_results.items():
        if result["final_status"] == "success":
            if result["corrections_applied"]:
                corrected_metrics.append(result)
                total_corrections += len(result["corrections_applied"])
            else:
                successful_metrics.append(result)
        else:
            failed_metrics.append(result)
    
    # Build summary
    summary = {
        "page_number": page_num,
        "timestamp": datetime.now().isoformat(),
        "processing_method": "apply_corrections_with_review",
        
        "overall_status": {
            "total_metrics": len(all_results),
            "successful_without_corrections": len(successful_metrics),
            "successful_with_corrections": len(corrected_metrics),
            "still_failed": len(failed_metrics),
            "overall_success_rate": f"{((len(successful_metrics) + len(corrected_metrics))/len(all_results)*100):.1f}%" if all_results else "0%"
        },
        
        "corrections_summary": {
            "total_corrections_applied": total_corrections,
            "metrics_that_needed_corrections": len(corrected_metrics),
            "correction_types": {}
        },
        
        "successful_corrections": [],
        "persistent_errors": [],
        
        "recommendations": []
    }
    
    # Analyze correction types
    correction_types = {}
    for result in corrected_metrics:
        for correction in result["corrections_applied"]:
            correction_type = correction["type"]
            if correction_type not in correction_types:
                correction_types[correction_type] = 0
            correction_types[correction_type] += 1
    
    summary["corrections_summary"]["correction_types"] = correction_types
    
    # Document successful corrections
    for result in corrected_metrics:
        summary["successful_corrections"].append({
            "metric": result["metric_name"],
            "corrections": [c["description"] for c in result["corrections_applied"]],
            "before_correction": f"{len(re.findall(r'd+(?:[.,]d+)?', result['raw_line']))} numbers",
            "after_correction": f"{result['numbers_count']} numbers",
            "final_result": f"{len(result['hourly_values'])} hourly + total: {result['total']}"
        })
    
    # Document persistent errors
    for result in failed_metrics:
        error_info = {
            "metric": result["metric_name"],
            "error": result["validation"]["issues"],
            "numbers_found": result["numbers_count"],
            "corrections_attempted": len(result["corrections_applied"]),
            "raw_sample": result["raw_line"][:80] + "..." if len(result["raw_line"]) > 80 else result["raw_line"]
        }
        
        # Suggest possible solutions
        if result["numbers_count"] < 24:
            error_info["suggested_action"] = "Possible merged numbers need additional splitting patterns"
        elif result["numbers_count"] > 30:
            error_info["suggested_action"] = "Possible over-splitting - review correction patterns"
        else:
            error_info["suggested_action"] = "Manual review required"
        
        summary["persistent_errors"].append(error_info)
    
    # Generate recommendations
    if not failed_metrics:
        summary["recommendations"].append("✅ All metrics processed successfully - no manual review needed")
    else:
        summary["recommendations"].append(f"⚠️  {len(failed_metrics)} metrics still need manual review")
        
        if correction_types:
            summary["recommendations"].append(f"✅ {total_corrections} corrections were applied successfully")
        
        # Specific recommendations based on patterns
        if any(error["numbers_found"] < 20 for error in summary["persistent_errors"]):
            summary["recommendations"].append("🔍 Some metrics have very few numbers - check for major OCR issues")
        
        if any(error["numbers_found"] > 30 for error in summary["persistent_errors"]):
            summary["recommendations"].append("🔧 Some metrics have too many numbers - may need refined correction patterns")
    
    return summary

def main():
    """Main processing with corrections and review summary"""
    
    if len(sys.argv) != 2:
        print("Usage: python scripts/apply_corrections_with_review_summary.py [page_number]")
        sys.exit(1)
    
    try:
        page_num = int(sys.argv[1])
    except ValueError:
        print("Error: Page number must be an integer")
        sys.exit(1)
    
    document_path = project_root / "data" / "documents" / "anexos_EAF" / "raw" / "Anexos-EAF-089-2025.pdf"
    
    print(f"🔧 APPLY CORRECTIONS WITH REVIEW SUMMARY - Page {page_num}")
    print("Strategy: Apply all corrections + Show what worked + Flag persistent errors")
    print("=" * 80)
    
    # Extract raw text
    raw_text = extract_page_text(str(document_path), page_num)
    
    if not raw_text:
        print(f"❌ No text extracted from page {page_num}")
        sys.exit(1)
    
    print(f"📄 RAW text: {len(raw_text)} chars")
    
    # Define metric patterns
    metric_patterns = {
        "generacion_total": r"Generaci[óo]n\s+Total[^\n]*\[MWh\][^\n]*",
        "costos_operacion": r"Costos?\s+Operaci[óo]n[^\n]*",
        "costos_encendido_detencion": r"Costos?\s+Encendido[^\n]*Detenci[^\n]*",
        "costo_marginal": r"Costo\s+Marginal[^\n]*",
        "indisponibilidad_forzada": r"Indisponibilidad\s+Forzada[^\n]*",
        "indisponibilidad_programada": r"Indisponibilidad\s+Programada[^\n]*"
    }
    
    # Process all metrics
    all_results = {}
    
    print("\n🔧 Processing metrics with all corrections...")
    
    for metric_key, pattern in metric_patterns.items():
        matches = re.findall(pattern, raw_text, re.IGNORECASE)
        if matches:
            raw_line = matches[0].strip()
            result = process_single_metric(raw_line, metric_key)
            all_results[metric_key] = result
            
            print(f"\n   📊 {metric_key.replace('_', ' ').title()}")
            print(f"      Numbers: {result['numbers_count']}")
            print(f"      Status: {result['final_status']}")
            
            if result["corrections_applied"]:
                print(f"      ✅ Corrections applied: {len(result['corrections_applied'])}")
                for correction in result["corrections_applied"]:
                    print(f"         • {correction['description']}")
            
            if result["final_status"] == "success":
                print(f"      ✅ Result: {len(result['hourly_values'])} hourly + total: {result['total']}")
            else:
                print(f"      ❌ Still has issues: {', '.join(result['validation']['issues'])}")
    
    # Generate review summary
    review_summary = generate_review_summary(all_results, page_num)
    
    # Build final output
    final_output = {
        "document_metadata": {
            "document_file": Path(document_path).name,
            "page_number": page_num,
            "extraction_timestamp": datetime.now().isoformat(),
            "extraction_method": "apply_corrections_with_review_summary"
        },
        "metrics_processed": all_results,
        "review_summary": review_summary
    }
    
    # Save full results
    output_file = project_root / "data" / "documents" / "anexos_EAF" / "development" / f"page_{page_num}_corrections_with_review.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)
    
    # Print summary
    print(f"\n📊 REVIEW SUMMARY:")
    print("=" * 80)
    
    status = review_summary["overall_status"]
    print(f"📈 Overall Success Rate: {status['overall_success_rate']}")
    print(f"✅ Successful without corrections: {status['successful_without_corrections']}")
    print(f"🔧 Successful with corrections: {status['successful_with_corrections']}")
    print(f"❌ Still failed: {status['still_failed']}")
    
    if review_summary["successful_corrections"]:
        print(f"\n✅ CORRECTIONS THAT WORKED:")
        for correction in review_summary["successful_corrections"]:
            print(f"   • {correction['metric']}: {correction['final_result']}")
            for desc in correction["corrections"]:
                print(f"     - {desc}")
    
    if review_summary["persistent_errors"]:
        print(f"\n❌ ERRORS THAT PERSIST:")
        for error in review_summary["persistent_errors"]:
            print(f"   • {error['metric']}: {', '.join(error['error'])}")
            print(f"     Numbers found: {error['numbers_found']}")
            print(f"     Suggested: {error['suggested_action']}")
    
    print(f"\n💡 RECOMMENDATIONS:")
    for rec in review_summary["recommendations"]:
        print(f"   {rec}")
    
    print(f"\n💾 Full results saved to: {output_file}")
    
    # Save review summary separately
    review_file = project_root / "data" / "documents" / "anexos_EAF" / "validation" / f"page_{page_num}_review_summary.json"
    with open(review_file, 'w', encoding='utf-8') as f:
        json.dump(review_summary, f, ensure_ascii=False, indent=2)
    
    print(f"📋 Review summary saved to: {review_file}")
    
    return len(review_summary["persistent_errors"])

if __name__ == "__main__":
    sys.exit(main())