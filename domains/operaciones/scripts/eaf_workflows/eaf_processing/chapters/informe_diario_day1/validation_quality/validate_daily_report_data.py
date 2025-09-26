#!/usr/bin/env python3
"""
INFORME DIARIO Day 1 Validation & Quality Assurance
===================================================

Validates and ensures quality of extracted daily report data
- Validates operational metrics and ranges
- Checks data consistency and completeness
- Identifies potential extraction errors
- Provides quality scores and recommendations

Usage:
    python validate_daily_report_data.py
    python validate_daily_report_data.py --strict  # Apply strict validation rules
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

def validate_operational_summary(summary: Dict) -> Tuple[bool, List[str]]:
    """Validate operational summary data"""
    issues = []
    is_valid = True

    # Check peak demand range (Chile's typical range: 7,000-12,000 MW)
    peak_demand = summary.get("peak_demand_mw")
    if peak_demand is not None:
        if not (5000 <= peak_demand <= 15000):
            issues.append(f"Peak demand {peak_demand} MW outside expected range (5,000-15,000 MW)")
            is_valid = False

    # Check peak demand time format
    peak_time = summary.get("peak_demand_time")
    if peak_time is not None:
        if not isinstance(peak_time, str) or ":" not in peak_time:
            issues.append(f"Invalid peak demand time format: {peak_time}")
            is_valid = False

    # Validate system status
    valid_statuses = ["operational", "alert", "emergency", "maintenance"]
    status = summary.get("system_status", "").lower()
    if status and status not in valid_statuses:
        issues.append(f"Invalid system status: {status}")
        is_valid = False

    return is_valid, issues

def validate_generation_data(generation_data: List[Dict]) -> Tuple[bool, List[str]]:
    """Validate generation data entries"""
    issues = []
    is_valid = True

    valid_sources = [
        "hidro", "hidroeléctrica", "térmica", "termoelectrica",
        "solar", "fotovoltaica", "eólica", "biomasa", "geotérmica"
    ]

    for i, gen in enumerate(generation_data):
        # Check source type
        source = gen.get("source_type", "").lower()
        if source not in valid_sources:
            issues.append(f"Generation entry {i}: Unknown source type '{source}'")
            is_valid = False

        # Check capacity range (0-1000 MW typical for individual plants)
        capacity = gen.get("capacity_mw")
        if capacity is not None:
            if not (0 <= capacity <= 2000):
                issues.append(f"Generation entry {i}: Capacity {capacity} MW outside reasonable range")
                is_valid = False

    return is_valid, issues

def validate_system_metrics(metrics: Dict) -> Tuple[bool, List[str]]:
    """Validate system performance metrics"""
    issues = []
    is_valid = True

    # Check frequency (Chile: 50 Hz ± 0.5 Hz)
    frequency = metrics.get("frequency_hz")
    if frequency is not None:
        if not (49.5 <= frequency <= 50.5):
            issues.append(f"Frequency {frequency} Hz outside normal range (49.5-50.5 Hz)")
            is_valid = False

    # Check voltage levels (common Chilean transmission levels)
    voltage_levels = metrics.get("voltage_levels", [])
    valid_voltages = [13.2, 23, 33, 66, 110, 154, 220, 345, 500]

    for voltage in voltage_levels:
        if voltage not in valid_voltages:
            # Allow ±10% tolerance
            is_close = any(abs(voltage - v) / v <= 0.1 for v in valid_voltages)
            if not is_close:
                issues.append(f"Unusual voltage level: {voltage} kV")

    return is_valid, issues

def validate_incidents(incidents: List[Dict]) -> Tuple[bool, List[str]]:
    """Validate incident and event data"""
    issues = []
    is_valid = True

    valid_types = [
        "falla", "incidente", "emergencia", "alerta", "desconexión",
        "reconexión", "mantenimiento", "indisponibilidad", "salida"
    ]

    for i, incident in enumerate(incidents):
        # Check incident type
        incident_type = incident.get("type", "").lower()
        if incident_type not in valid_types:
            issues.append(f"Incident {i}: Unknown type '{incident_type}'")

        # Check description length
        description = incident.get("description", "")
        if len(description.strip()) < 10:
            issues.append(f"Incident {i}: Description too short")
            is_valid = False

        # Validate time format if present
        time_str = incident.get("time")
        if time_str:
            try:
                hour, minute = map(int, time_str.split(":"))
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    issues.append(f"Incident {i}: Invalid time '{time_str}'")
                    is_valid = False
            except ValueError:
                issues.append(f"Incident {i}: Invalid time format '{time_str}'")
                is_valid = False

    return is_valid, issues

def calculate_quality_score(extraction_data: Dict) -> Dict:
    """Calculate overall quality score for the extraction"""
    score_components = {
        "data_completeness": 0,
        "content_richness": 0,
        "validation_passed": 0,
        "extraction_success": 0
    }

    # Data completeness (40% of score)
    required_fields = ["operational_summary", "generation_data", "system_metrics", "incidents_and_events"]
    present_fields = sum(1 for field in required_fields if extraction_data.get(field))
    score_components["data_completeness"] = (present_fields / len(required_fields)) * 40

    # Content richness (30% of score)
    generation_count = len(extraction_data.get("generation_data", []))
    incidents_count = len(extraction_data.get("incidents_and_events", []))
    richness_score = min((generation_count * 5 + incidents_count * 3) / 20, 1.0) * 30
    score_components["content_richness"] = richness_score

    # Validation passed (20% of score)
    all_validations = [
        validate_operational_summary(extraction_data.get("operational_summary", {})),
        validate_generation_data(extraction_data.get("generation_data", [])),
        validate_system_metrics(extraction_data.get("system_metrics", {})),
        validate_incidents(extraction_data.get("incidents_and_events", []))
    ]

    validation_pass_rate = sum(1 for is_valid, _ in all_validations if is_valid) / len(all_validations)
    score_components["validation_passed"] = validation_pass_rate * 20

    # Extraction success (10% of score)
    if extraction_data.get("status") == "extracted" and not extraction_data.get("error"):
        score_components["extraction_success"] = 10

    total_score = sum(score_components.values())

    return {
        "total_score": round(total_score, 2),
        "score_components": score_components,
        "grade": get_grade(total_score)
    }

def get_grade(score: float) -> str:
    """Convert numeric score to letter grade"""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"

def validate_extraction_file(file_path: Path, strict_mode: bool = False) -> Dict:
    """Validate a single extraction file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        validation_result = {
            "file": str(file_path),
            "page": data.get("page"),
            "validation_timestamp": datetime.now().isoformat(),
            "is_valid": True,
            "issues": [],
            "warnings": []
        }

        # Run all validations
        summary_valid, summary_issues = validate_operational_summary(data.get("operational_summary", {}))
        gen_valid, gen_issues = validate_generation_data(data.get("generation_data", []))
        metrics_valid, metrics_issues = validate_system_metrics(data.get("system_metrics", {}))
        incidents_valid, incidents_issues = validate_incidents(data.get("incidents_and_events", []))

        all_issues = summary_issues + gen_issues + metrics_issues + incidents_issues
        validation_result["issues"] = all_issues

        # Overall validation status
        if not all([summary_valid, gen_valid, metrics_valid, incidents_valid]):
            validation_result["is_valid"] = False

        # Calculate quality score
        quality_score = calculate_quality_score(data)
        validation_result["quality_score"] = quality_score

        # Additional checks for strict mode
        if strict_mode:
            text_length = data.get("text_length", 0)
            if text_length < 500:
                validation_result["warnings"].append(f"Short text extraction: {text_length} characters")

            if not data.get("generation_data"):
                validation_result["warnings"].append("No generation data extracted")

            if not data.get("incidents_and_events"):
                validation_result["warnings"].append("No incidents or events extracted")

        return validation_result

    except Exception as e:
        return {
            "file": str(file_path),
            "validation_timestamp": datetime.now().isoformat(),
            "is_valid": False,
            "error": str(e),
            "quality_score": {"total_score": 0, "grade": "F"}
        }

def main():
    """Main validation function"""
    # Setup paths
    project_root = Path(__file__).parent.parent.parent.parent.parent.parent
    input_dir = project_root / "extractions" / "informe_diario_day1"

    strict_mode = "--strict" in sys.argv

    if not input_dir.exists():
        print(f"❌ Input directory not found: {input_dir}")
        return

    # Find all extraction files
    json_files = list(input_dir.glob("*.json"))

    if not json_files:
        print(f"❌ No extraction files found in: {input_dir}")
        return

    print(f"🔍 Validating INFORME DIARIO Day 1 extractions")
    print(f"📁 Input directory: {input_dir}")
    print(f"📊 Files to validate: {len(json_files)}")
    print(f"🔒 Strict mode: {'ON' if strict_mode else 'OFF'}")
    print("-" * 60)

    validation_results = []
    total_score = 0
    valid_files = 0

    for json_file in sorted(json_files):
        print(f"\n📄 Validating: {json_file.name}")

        result = validate_extraction_file(json_file, strict_mode)
        validation_results.append(result)

        if result["is_valid"]:
            print(f"   ✅ Valid")
            valid_files += 1
        else:
            print(f"   ❌ Invalid")

        quality = result.get("quality_score", {})
        score = quality.get("total_score", 0)
        grade = quality.get("grade", "F")
        total_score += score

        print(f"   📊 Quality Score: {score}/100 (Grade: {grade})")

        if result.get("issues"):
            for issue in result["issues"][:3]:  # Show first 3 issues
                print(f"   ⚠️  {issue}")
            if len(result["issues"]) > 3:
                print(f"   ... and {len(result['issues']) - 3} more issues")

        if result.get("warnings"):
            for warning in result["warnings"][:2]:  # Show first 2 warnings
                print(f"   🟡 {warning}")

    # Summary
    print("-" * 60)
    print(f"📊 Validation Summary:")
    print(f"   Valid files: {valid_files}/{len(json_files)}")
    print(f"   Average quality score: {total_score / len(json_files):.1f}/100")
    print(f"   Overall grade: {get_grade(total_score / len(json_files))}")

    # Save validation report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = input_dir / f"validation_report_{timestamp}.json"

    report = {
        "validation_timestamp": datetime.now().isoformat(),
        "total_files": len(json_files),
        "valid_files": valid_files,
        "average_score": total_score / len(json_files),
        "strict_mode": strict_mode,
        "results": validation_results
    }

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"📋 Validation report saved: {report_path}")

if __name__ == "__main__":
    main()