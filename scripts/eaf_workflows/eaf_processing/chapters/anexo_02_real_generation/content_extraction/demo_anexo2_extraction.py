#!/usr/bin/env python3
"""
Demo: ANEXO 2 Real Generation Data Extraction
============================================

Demonstrates how ANEXO 2 extraction works with simulated data.
Shows the difference between ANEXO 1 (Programming) and ANEXO 2 (Real Generation).
"""

import json
from datetime import datetime
from pathlib import Path

def demo_anexo2_extraction():
    """Demonstrate ANEXO 2 real generation data extraction"""
    
    print("🚀 ANEXO 2 EXTRACTION DEMO - Real Generation Data (Pages 63-95)")
    print("=" * 70)
    print("🎯 Focus: REAL vs PROGRAMMED generation comparison")
    print("📊 Data Type: Actual operational performance")
    print("=" * 70)
    
    # Simulate typical ANEXO 2 content (real generation data)
    sample_content = """
    GENERACION REAL DEL SISTEMA - COORDINADA POR EL CEN
    Fecha: 25 de Febrero 2025, Hora: 15:16
    
    CENTRAL HIDROELECTRICA COLBUN
    Generación Programada: 450 MW
    Generación Real: 437 MW
    Desviación: -13 MW
    Timestamp: 15:16
    
    CENTRAL TERMICA SANTA MARIA
    Generación Programada: 340 MW
    Generación Real: 365 MW
    Desviación: +25 MW
    Timestamp: 15:16
    
    CENTRAL HIDROELECTRICA EL TORO
    Generación Programada: 400 MW
    Generación Real: 390 MW
    Desviación: -10 MW
    Timestamp: 15:16
    
    CENTRAL TERMICA GUACOLDA
    Generación Programada: 680 MW
    Generación Real: 0 MW
    Desviación: -680 MW
    Estado: FUERA DE SERVICIO
    Timestamp: 15:16
    """
    
    print("📄 SIMULATED ANEXO 2 CONTENT (Page 65):")
    print("-" * 50)
    print(sample_content)
    
    # Process like the real extraction would
    lines = sample_content.strip().split('\n')
    
    print("\n🔍 EXTRACTION PROCESS:")
    print("-" * 30)
    
    extracted_data = {
        'page': 65,
        'chapter': 'ANEXO_02_REAL_GENERATION',
        'extraction_timestamp': datetime.now().isoformat(),
        'real_generation_records': [],
        'summary_metrics': {},
        'extraction_quality': {'patterns_found': 0, 'confidence': 'HIGH'}
    }
    
    current_plant = None
    plant_data = {}
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        print(f"[{i:2d}] Processing: {line}")
        
        # Look for power plant patterns
        if 'CENTRAL' in line:
            if current_plant and plant_data:
                # Save previous plant data
                extracted_data['real_generation_records'].append({
                    'plant_name': current_plant,
                    'data': plant_data.copy(),
                    'source_line': i
                })
                extracted_data['extraction_quality']['patterns_found'] += 1
            
            plant_type = 'HIDROELECTRICA' if 'HIDROELECTRICA' in line else 'TERMICA'
            plant_name = line.replace('CENTRAL', '').replace(plant_type, '').strip()
            current_plant = plant_name
            plant_data = {'plant_name': plant_name, 'plant_type': plant_type}
        
        # Extract real generation data for current plant
        elif current_plant:
            if 'Generación Programada:' in line:
                value = line.split(':')[1].strip().replace(' MW', '')
                plant_data['programmed_generation_mw'] = float(value)
                extracted_data['extraction_quality']['patterns_found'] += 1
            
            elif 'Generación Real:' in line:
                value = line.split(':')[1].strip().replace(' MW', '')
                plant_data['real_generation_mw'] = float(value)
                extracted_data['extraction_quality']['patterns_found'] += 1
            
            elif 'Desviación:' in line:
                value = line.split(':')[1].strip().replace(' MW', '').replace('+', '')
                plant_data['deviation_mw'] = float(value)
                extracted_data['extraction_quality']['patterns_found'] += 1
            
            elif 'Timestamp:' in line:
                plant_data['timestamp'] = line.split(':')[1].strip()
                extracted_data['extraction_quality']['patterns_found'] += 1
            
            elif 'Estado:' in line:
                plant_data['operational_status'] = line.split(':')[1].strip()
                extracted_data['extraction_quality']['patterns_found'] += 1
    
    # Save last plant data
    if current_plant and plant_data:
        extracted_data['real_generation_records'].append({
            'plant_name': current_plant,
            'data': plant_data.copy(),
            'source_line': len(lines)
        })
    
    print(f"\n📊 EXTRACTED DATA SUMMARY:")
    print("-" * 40)
    
    plants = extracted_data['real_generation_records']
    print(f"🏭 Power Plants Found: {len(plants)}")
    
    total_programmed = 0
    total_real = 0
    operational_plants = 0
    
    for plant in plants:
        data = plant['data']
        name = data['plant_name']
        plant_type = data.get('plant_type', 'Unknown')
        programmed = data.get('programmed_generation_mw', 0)
        real = data.get('real_generation_mw', 0)
        deviation = data.get('deviation_mw', 0)
        status = data.get('operational_status', 'OPERATIONAL')
        
        print(f"   - {plant_type}: {name}")
        print(f"     Programmed: {programmed} MW, Real: {real} MW, Deviation: {deviation:+} MW")
        print(f"     Status: {status}")
        
        total_programmed += programmed
        total_real += real
        if status != 'FUERA DE SERVICIO':
            operational_plants += 1
    
    # Calculate summary metrics
    total_deviation = total_real - total_programmed
    deviation_percentage = (total_deviation / total_programmed * 100) if total_programmed > 0 else 0
    
    extracted_data['summary_metrics'] = {
        'total_plants': len(plants),
        'operational_plants': operational_plants,
        'total_programmed_generation_mw': total_programmed,
        'total_real_generation_mw': total_real,
        'total_deviation_mw': total_deviation,
        'deviation_percentage': deviation_percentage,
        'system_performance': 'UNDERPERFORMING' if total_deviation < 0 else 'OVERPERFORMING'
    }
    
    print(f"\n⚡ GENERATION SUMMARY:")
    print("-" * 25)
    print(f"📈 Total Programmed: {total_programmed} MW")
    print(f"📊 Total Real: {total_real} MW")
    print(f"📉 Total Deviation: {total_deviation:+} MW ({deviation_percentage:+.1f}%)")
    print(f"🎯 System Performance: {extracted_data['summary_metrics']['system_performance']}")
    print(f"⚙️  Operational Plants: {operational_plants}/{len(plants)}")
    
    print(f"\n🎯 EXTRACTION RESULTS:")
    print("-" * 30)
    print(f"✅ Total data points extracted: {extracted_data['extraction_quality']['patterns_found']}")
    print(f"✅ Plants with complete data: {len(plants)}")
    print(f"✅ Confidence level: {extracted_data['extraction_quality']['confidence']}")
    
    # Show what JSON output looks like
    print(f"\n📋 SAMPLE JSON OUTPUT:")
    print("-" * 25)
    sample_output = {
        "page": 65,
        "chapter": "ANEXO_02_REAL_GENERATION", 
        "extraction_timestamp": "2024-09-08T21:30:00",
        "real_generation_records": [
            {
                "plant_name": "COLBUN",
                "data": {
                    "plant_type": "HIDROELECTRICA",
                    "programmed_generation_mw": 450,
                    "real_generation_mw": 437,
                    "deviation_mw": -13,
                    "timestamp": "15:16"
                }
            }
        ],
        "summary_metrics": {
            "total_programmed_generation_mw": 1870,
            "total_real_generation_mw": 1192,
            "total_deviation_mw": -678,
            "deviation_percentage": -36.3,
            "system_performance": "UNDERPERFORMING"
        }
    }
    
    print(json.dumps(sample_output, indent=2, ensure_ascii=False))
    
    print(f"\n🔄 ANEXO 1 vs ANEXO 2 COMPARISON:")
    print("-" * 40)
    print("📊 ANEXO 1 (Programming): What was PLANNED")
    print("   - Generation schedules and capacity planning")
    print("   - Future operational intentions")
    print("   - Resource allocation planning")
    print()
    print("📈 ANEXO 2 (Real Generation): What ACTUALLY happened")
    print("   - Real-time operational performance")
    print("   - Actual vs planned comparison")
    print("   - System reliability and deviation analysis")
    print("   - Operational status and outages")
    
    print(f"\n🎯 Next Steps for ANEXO 2:")
    print("1. Process all pages 63-95 to get complete real generation picture")
    print("2. Cross-reference with ANEXO 1 for comprehensive planning vs reality analysis")
    print("3. Identify patterns in generation deviations")
    print("4. Analyze system performance and reliability metrics")

if __name__ == "__main__":
    demo_anexo2_extraction()