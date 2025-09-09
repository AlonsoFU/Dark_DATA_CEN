#!/usr/bin/env python3
"""
Generate detailed structure analysis report
"""

import json
from pathlib import Path
from typing import Dict, Any

def generate_detailed_report():
    # Read analysis results
    analysis_dir = Path("analysis_output")
    
    # Read individual analyses
    eaf_analysis_path = analysis_dir / "EAF-089-2025_reduc_analysis.json"
    anexos_analysis_path = analysis_dir / "Anexos-EAF-089-2025_reduc_analysis.json"
    comparison_path = analysis_dir / "document_comparison.json"
    
    with open(eaf_analysis_path, 'r') as f:
        eaf_analysis = json.load(f)
    
    with open(anexos_analysis_path, 'r') as f:
        anexos_analysis = json.load(f)
    
    with open(comparison_path, 'r') as f:
        comparison = json.load(f)
    
    print("📊 DETAILED DOCUMENT STRUCTURE ANALYSIS")
    print("=" * 60)
    
    # Document overview
    print(f"\n📄 DOCUMENT 1: {eaf_analysis['file_info']['name']}")
    print(f"   📏 Pages: {eaf_analysis['file_info']['total_pages']}")
    print(f"   💾 Size: {eaf_analysis['file_info']['file_size_mb']:.2f} MB")
    
    print(f"\n📄 DOCUMENT 2: {anexos_analysis['file_info']['name']}")
    print(f"   📏 Pages: {anexos_analysis['file_info']['total_pages']}")  
    print(f"   💾 Size: {anexos_analysis['file_info']['file_size_mb']:.2f} MB")
    
    # Pattern analysis
    print(f"\n🔍 PATTERN ANALYSIS")
    print(f"-" * 30)
    
    for pattern, data in comparison['common_patterns'].items():
        print(f"{pattern}:")
        print(f"   📈 Counts: {data['counts']} (avg: {data['avg_per_doc']:.1f})")
        print(f"   📊 Consistent: {'✅' if data['consistent'] else '❌'}")
    
    # Content type analysis  
    print(f"\n📋 CONTENT TYPE ANALYSIS")
    print(f"-" * 30)
    
    for doc_name, analysis in [("EAF Main", eaf_analysis), ("Anexos", anexos_analysis)]:
        print(f"\n{doc_name}:")
        content_types = analysis['summary']['content_types']
        for content_type, count in content_types.items():
            print(f"   {content_type}: {count} pages")
    
    # Key findings
    print(f"\n🎯 KEY FINDINGS")
    print(f"-" * 30)
    
    # Analyze EAF structure
    print("\n📄 EAF-089-2025 Structure:")
    eaf_pages = eaf_analysis['pages']
    for i, page in enumerate(eaf_pages[:5]):  # First 5 pages
        print(f"   Page {page['page_number']}: {page['content_type']}")
        if page['headers']:
            print(f"      Headers: {page['headers'][:2]}")  # First 2 headers
        key_patterns = [k for k, v in page['patterns_found'].items() if v]
        if key_patterns:
            print(f"      Patterns: {', '.join(key_patterns)}")
    
    print("\n📄 Anexos Structure:")
    anexos_pages = anexos_analysis['pages']  
    for i, page in enumerate(anexos_pages[:5]):  # First 5 pages
        print(f"   Page {page['page_number']}: {page['content_type']}")
        if page['headers']:
            print(f"      Headers: {page['headers'][:2]}")
        key_patterns = [k for k, v in page['patterns_found'].items() if v]
        if key_patterns:
            print(f"      Patterns: {', '.join(key_patterns)}")
    
    # Extraction strategy recommendations
    print(f"\n💡 EXTRACTION STRATEGY RECOMMENDATIONS")
    print(f"-" * 45)
    
    # Based on analysis, generate specific recommendations
    recommendations = []
    
    # Company extraction
    if comparison['common_patterns']['companies']['counts'][1] > 50:  # EAF has many companies
        recommendations.append("🏢 High company density in main report - prioritize company extraction")
    
    # Technical specs
    tech_specs_consistent = abs(comparison['common_patterns']['technical_specs']['counts'][0] - 
                               comparison['common_patterns']['technical_specs']['counts'][1]) < 10
    if tech_specs_consistent:
        recommendations.append("⚙️ Technical specs patterns are similar - create unified extractor")
    
    # Page-specific strategies
    eaf_has_tabular = any(page['content_type'] == 'tabular_data' for page in eaf_pages)
    anexos_has_tabular = any(page['content_type'] == 'tabular_data' for page in anexos_pages)
    
    if eaf_has_tabular or anexos_has_tabular:
        recommendations.append("📊 Tabular data detected - implement table extraction")
    
    # Document size considerations
    if eaf_analysis['file_info']['total_pages'] == 20:  # Truncated
        recommendations.append("📏 Documents are truncated at 20 pages - full documents likely have more sections")
    
    for rec in recommendations:
        print(f"   {rec}")
    
    # Proposed chunking strategy
    print(f"\n🔪 PROPOSED CHUNKING STRATEGY")
    print(f"-" * 35)
    
    print("1. 📄 Section-based chunking:")
    print("   - Split by numbered headers (1., 2., etc.)")  
    print("   - Preserve company information context")
    print("   - Keep technical specifications grouped")
    
    print("\n2. 🏢 Company-focused extraction:")
    print("   - Extract all company mentions with context")
    print("   - Group by company name")
    print("   - Track compliance status per company")
    
    print("\n3. ⚙️ Technical data extraction:")
    print("   - Extract all MW, kV, Hz specifications")
    print("   - Group by equipment type")  
    print("   - Link to responsible companies")
    
    print("\n4. 📅 Timeline reconstruction:")
    print("   - Extract all dates with context")
    print("   - Build chronological sequence")
    print("   - Link events to companies/equipment")

if __name__ == "__main__":
    generate_detailed_report()