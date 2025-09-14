#!/usr/bin/env python3
"""
ANEXO 2 Real Generation Data Validator
=====================================

Validates extracted real generation data for accuracy and consistency.
Ensures data quality before final processing.

Validation checks:
- Real vs programmed generation consistency
- Power plant name validation
- MW value range checks
- Deviation calculations
- Data completeness assessment

Usage:
    python validate_real_generation_data.py [json_file]
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime

# Known power plants in Chile (for validation)
KNOWN_POWER_PLANTS = {
    'hydroelectric': [
        'COLBUN', 'EL TORO', 'CANUTILLAR', 'LOMA ALTA', 'CIPRESES',
        'ISLA', 'SAUZAL', 'SAUZALITO', 'PEHUENCHE', 'CURILLINQUE',
        'LAJA', 'ANTUCO', 'EL ABANICO', 'QUELTEHUES'
    ],
    'thermal': [
        'SANTA MARIA', 'GUACOLDA', 'BOCAMINA', 'CAMPICHE',
        'NUEVA RENCA', 'SANTA LIDIA', 'SAN LORENZO', 'TALTAL'
    ],
    'wind': [
        'TOTORAL', 'PUNTA COLORADA', 'VALLE DE LOS VIENTOS',
        'TALINAY ORIENTE', 'MONTE REDONDO'
    ],
    'solar': [
        'SALVADOR', 'DIEGO DE ALMAGRO SOLAR', 'POZO ALMONTE SOLAR',
        'CALAMA SOLAR', 'JAVIERA', 'PAMPA SOLAR NORTE'
    ]
}

def load_extraction_data(file_path: str) -> Dict:
    """Load extracted data from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading file {file_path}: {e}")
        return {}

def validate_power_plant_name(plant_name: str) -> Dict[str, Any]:
    """Validate power plant name against known plants"""
    validation = {
        'is_valid': False,
        'plant_type': None,
        'confidence': 'LOW',
        'suggestions': []
    }
    
    if not plant_name:
        return validation
    
    plant_clean = plant_name.upper().strip()
    
    # Check exact matches
    for plant_type, plants in KNOWN_POWER_PLANTS.items():
        for known_plant in plants:
            if known_plant in plant_clean or plant_clean in known_plant:
                validation['is_valid'] = True
                validation['plant_type'] = plant_type
                validation['confidence'] = 'HIGH'
                return validation
    
    # Check partial matches
    best_matches = []
    for plant_type, plants in KNOWN_POWER_PLANTS.items():
        for known_plant in plants:
            # Simple similarity check
            common_words = set(plant_clean.split()) & set(known_plant.split())
            if common_words:
                similarity = len(common_words) / max(len(plant_clean.split()), len(known_plant.split()))
                if similarity > 0.3:
                    best_matches.append((known_plant, plant_type, similarity))
    
    if best_matches:
        best_matches.sort(key=lambda x: x[2], reverse=True)
        validation['suggestions'] = best_matches[:3]
        validation['confidence'] = 'MEDIUM'
    
    return validation

def validate_generation_values(data: Dict) -> Dict[str, Any]:
    """Validate generation MW values for reasonableness"""
    validation = {
        'real_gen_valid': False,
        'prog_gen_valid': False,
        'deviation_valid': False,
        'issues': []
    }
    
    real_gen = data.get('real_generation_mw')
    prog_gen = data.get('programmed_generation_mw')
    deviation = data.get('deviation_mw')
    
    # Validate real generation
    if isinstance(real_gen, (int, float)):
        if 0 <= real_gen <= 2000:  # Reasonable range for Chilean plants
            validation['real_gen_valid'] = True
        else:
            validation['issues'].append(f"Real generation {real_gen}MW outside reasonable range (0-2000MW)")
    else:
        validation['issues'].append(f"Real generation not numeric: {real_gen}")
    
    # Validate programmed generation
    if isinstance(prog_gen, (int, float)):
        if 0 <= prog_gen <= 2000:
            validation['prog_gen_valid'] = True
        else:
            validation['issues'].append(f"Programmed generation {prog_gen}MW outside reasonable range")
    else:
        validation['issues'].append(f"Programmed generation not numeric: {prog_gen}")
    
    # Validate deviation consistency
    if validation['real_gen_valid'] and validation['prog_gen_valid']:
        calculated_deviation = real_gen - prog_gen
        
        if isinstance(deviation, (int, float)):
            if abs(deviation - calculated_deviation) < 0.1:  # Allow small rounding errors
                validation['deviation_valid'] = True
            else:
                validation['issues'].append(
                    f"Deviation inconsistent: reported {deviation}MW, calculated {calculated_deviation}MW"
                )
        else:
            # If no deviation reported, calculate it
            data['deviation_mw'] = calculated_deviation
            validation['deviation_valid'] = True
    
    return validation

def validate_record_completeness(record: Dict) -> Dict[str, Any]:
    """Check if record has sufficient data for analysis"""
    validation = {
        'completeness_score': 0,
        'required_fields': ['plant_name', 'real_generation_mw'],
        'optional_fields': ['programmed_generation_mw', 'deviation_mw', 'timestamp'],
        'missing_required': [],
        'missing_optional': []
    }
    
    data = record.get('data', {})
    
    # Check required fields
    for field in validation['required_fields']:
        if field in data and data[field] is not None:
            validation['completeness_score'] += 40  # 80% for required fields
        else:
            validation['missing_required'].append(field)
    
    # Check optional fields
    for field in validation['optional_fields']:
        if field in data and data[field] is not None:
            validation['completeness_score'] += 5  # 20% for optional fields
        else:
            validation['missing_optional'].append(field)
    
    return validation

def validate_extraction_results(extraction_data: Dict) -> Dict[str, Any]:
    """Validate complete extraction results"""
    validation_report = {
        'overall_quality': 'UNKNOWN',
        'total_records': 0,
        'valid_records': 0,
        'validation_details': [],
        'summary_metrics': {},
        'recommendations': []
    }
    
    if not extraction_data:
        validation_report['overall_quality'] = 'FAILED'
        validation_report['recommendations'].append("No data to validate")
        return validation_report
    
    # Handle both single page and multi-page results
    if isinstance(extraction_data, list):
        # Multi-page results
        all_records = []
        for page_data in extraction_data:
            all_records.extend(page_data.get('real_generation_records', []))
    else:
        # Single page results
        all_records = extraction_data.get('real_generation_records', [])
    
    validation_report['total_records'] = len(all_records)
    
    for i, record in enumerate(all_records):
        record_validation = {
            'record_index': i,
            'plant_name': record.get('plant_name', 'Unknown'),
            'plant_validation': validate_power_plant_name(record.get('plant_name', '')),
            'values_validation': validate_generation_values(record.get('data', {})),
            'completeness_validation': validate_record_completeness(record),
            'is_valid': False
        }
        
        # Determine if record is valid overall
        plant_ok = record_validation['plant_validation']['is_valid'] or record_validation['plant_validation']['confidence'] != 'LOW'
        values_ok = record_validation['values_validation']['real_gen_valid']
        complete_ok = record_validation['completeness_validation']['completeness_score'] >= 40
        
        record_validation['is_valid'] = plant_ok and values_ok and complete_ok
        
        if record_validation['is_valid']:
            validation_report['valid_records'] += 1
        
        validation_report['validation_details'].append(record_validation)
    
    # Calculate overall quality
    if validation_report['total_records'] == 0:
        validation_report['overall_quality'] = 'NO_DATA'
    else:
        validity_ratio = validation_report['valid_records'] / validation_report['total_records']
        if validity_ratio >= 0.8:
            validation_report['overall_quality'] = 'HIGH'
        elif validity_ratio >= 0.6:
            validation_report['overall_quality'] = 'MEDIUM'
        else:
            validation_report['overall_quality'] = 'LOW'
    
    # Generate recommendations
    if validation_report['valid_records'] < validation_report['total_records']:
        invalid_count = validation_report['total_records'] - validation_report['valid_records']
        validation_report['recommendations'].append(
            f"Review {invalid_count} invalid records for data quality issues"
        )
    
    if validation_report['overall_quality'] in ['LOW', 'MEDIUM']:
        validation_report['recommendations'].append(
            "Consider re-running extraction with improved OCR or manual validation"
        )
    
    # Summary metrics
    if all_records:
        valid_records = [r for r in validation_report['validation_details'] if r['is_valid']]
        if valid_records:
            # Calculate generation totals from valid records only
            total_real = sum(
                r['record_index'] < len(all_records) and 
                isinstance(all_records[r['record_index']].get('data', {}).get('real_generation_mw'), (int, float))
                and all_records[r['record_index']]['data']['real_generation_mw'] or 0
                for r in valid_records
            )
            
            validation_report['summary_metrics'] = {
                'total_valid_generation_mw': total_real,
                'average_generation_per_plant': total_real / len(valid_records) if valid_records else 0,
                'data_quality_score': (validation_report['valid_records'] / validation_report['total_records']) * 100
            }
    
    return validation_report

def print_validation_report(report: Dict):
    """Print formatted validation report"""
    print("\n" + "="*60)
    print("📋 ANEXO 2 REAL GENERATION DATA VALIDATION REPORT")
    print("="*60)
    
    print(f"📊 Overall Quality: {report['overall_quality']}")
    print(f"📈 Valid Records: {report['valid_records']}/{report['total_records']}")
    
    if report['summary_metrics']:
        metrics = report['summary_metrics']
        print(f"⚡ Total Valid Generation: {metrics.get('total_valid_generation_mw', 0):.1f} MW")
        print(f"📊 Data Quality Score: {metrics.get('data_quality_score', 0):.1f}%")
    
    print("\n🔍 Detailed Validation Results:")
    for detail in report['validation_details']:
        status = "✅" if detail['is_valid'] else "❌"
        plant = detail['plant_name']
        plant_conf = detail['plant_validation']['confidence']
        
        print(f"{status} {plant} (Plant: {plant_conf})")
        
        if detail['values_validation']['issues']:
            for issue in detail['values_validation']['issues']:
                print(f"     ⚠️  {issue}")
    
    if report['recommendations']:
        print("\n💡 Recommendations:")
        for rec in report['recommendations']:
            print(f"   • {rec}")

def main():
    """Main validation function"""
    print("🔍 ANEXO 2 REAL GENERATION DATA VALIDATOR")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Usage: python validate_real_generation_data.py <json_file>")
        print("\nExample:")
        print("  python validate_real_generation_data.py anexo2_page_65_20241201_120000.json")
        return
    
    file_path = sys.argv[1]
    
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return
    
    print(f"📁 Loading: {file_path}")
    
    # Load and validate data
    extraction_data = load_extraction_data(file_path)
    validation_report = validate_extraction_results(extraction_data)
    
    # Print report
    print_validation_report(validation_report)
    
    # Save validation report
    output_file = Path(file_path).parent / f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(validation_report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Validation report saved to: {output_file}")

if __name__ == "__main__":
    main()