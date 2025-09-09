#!/usr/bin/env python3
"""
Validate document structure across all pages
Check if patterns from first 20 pages hold throughout entire document
"""

import PyPDF2
import json
from pathlib import Path
import re
from typing import Dict, List, Any, Tuple

def analyze_structure_evolution(pdf_path: str) -> Dict[str, Any]:
    """Analyze how document structure changes across all pages"""
    
    print(f"🔍 Analyzing structure evolution: {Path(pdf_path).name}")
    
    patterns = {
        'section_headers': r'^(\d+)\.\s+(.+)$',
        'companies': r'(ENEL|COLBÚN|AES|INTERCHILE|Colbún|Enel)',
        'technical_specs': r'(\d+[,.]?\d*)\s*(MW|kV|Hz|A|V)',
        'dates': r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})'
    }
    
    # Extract all pages
    pages_analysis = []
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            
            print(f"📄 Total pages: {total_pages}")
            
            # Analyze structure in chunks of 50 pages
            chunk_size = 50
            for start_page in range(0, total_pages, chunk_size):
                end_page = min(start_page + chunk_size, total_pages)
                
                print(f"   Analyzing pages {start_page + 1}-{end_page}...")
                
                chunk_analysis = {
                    'page_range': f"{start_page + 1}-{end_page}",
                    'patterns_found': {pattern: [] for pattern in patterns.keys()},
                    'content_types': [],
                    'structure_changes': []
                }
                
                for page_num in range(start_page, end_page):
                    try:
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        
                        # Analyze patterns in this page
                        page_patterns = {}
                        for pattern_name, pattern in patterns.items():
                            matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)
                            if matches:
                                page_patterns[pattern_name] = len(matches)
                                chunk_analysis['patterns_found'][pattern_name].extend(matches)
                        
                        # Detect content type
                        content_type = classify_page_content(text, page_patterns)
                        chunk_analysis['content_types'].append(content_type)
                        
                    except Exception as e:
                        print(f"      ⚠️  Error on page {page_num + 1}: {e}")
                
                pages_analysis.append(chunk_analysis)
                
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
        return {}
    
    # Analyze structure evolution
    evolution_analysis = analyze_evolution_patterns(pages_analysis)
    
    return {
        'total_pages': total_pages,
        'chunk_analysis': pages_analysis,
        'evolution_summary': evolution_analysis
    }

def classify_page_content(text: str, patterns_found: Dict[str, int]) -> str:
    """Classify page content type based on patterns"""
    
    lines = text.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    
    if len(non_empty_lines) < 5:
        return 'sparse_content'
    elif patterns_found.get('companies', 0) > 5:
        return 'company_listing'  
    elif patterns_found.get('technical_specs', 0) > 10:
        return 'technical_specifications'
    elif patterns_found.get('section_headers', 0) > 0:
        return 'structured_section'
    elif len(text) > 2000:
        return 'narrative_text'
    else:
        return 'mixed_content'

def analyze_evolution_patterns(pages_analysis: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze how patterns evolve across document"""
    
    evolution = {
        'pattern_consistency': {},
        'content_type_distribution': {},
        'structure_changes': [],
        'recommendations': []
    }
    
    # Analyze pattern consistency across chunks
    all_patterns = ['section_headers', 'companies', 'technical_specs', 'dates']
    
    for pattern in all_patterns:
        pattern_counts = []
        for chunk in pages_analysis:
            count = len(chunk['patterns_found'][pattern])
            pattern_counts.append(count)
        
        # Calculate consistency metrics
        if pattern_counts:
            avg_count = sum(pattern_counts) / len(pattern_counts)
            max_count = max(pattern_counts)
            min_count = min(pattern_counts)
            variation = max_count - min_count if max_count > 0 else 0
            
            evolution['pattern_consistency'][pattern] = {
                'average_per_chunk': avg_count,
                'max_per_chunk': max_count,
                'min_per_chunk': min_count,
                'variation': variation,
                'consistent': variation < (avg_count * 0.5) if avg_count > 0 else True
            }
    
    # Analyze content type distribution
    all_content_types = []
    for chunk in pages_analysis:
        all_content_types.extend(chunk['content_types'])
    
    content_type_counts = {}
    for content_type in all_content_types:
        content_type_counts[content_type] = content_type_counts.get(content_type, 0) + 1
    
    evolution['content_type_distribution'] = content_type_counts
    
    # Generate recommendations
    recommendations = []
    
    # Check for structural consistency
    for pattern, data in evolution['pattern_consistency'].items():
        if not data['consistent']:
            recommendations.append(f"⚠️  {pattern} pattern varies significantly across document")
        else:
            recommendations.append(f"✅ {pattern} pattern is consistent throughout")
    
    # Check content type diversity
    if len(content_type_counts) > 5:
        recommendations.append("📊 Document has diverse content types - multi-strategy extraction needed")
    else:
        recommendations.append("📋 Document has consistent content types - single strategy sufficient")
    
    evolution['recommendations'] = recommendations
    
    return evolution

def main():
    """Analyze structure of real large documents"""
    
    data_real_path = Path("data_real")
    if not data_real_path.exists():
        print("❌ data_real directory not found")
        return
    
    # Analyze both documents
    pdf_files = list(data_real_path.glob("*.pdf"))
    
    for pdf_file in pdf_files:
        print(f"\n{'='*80}")
        analysis = analyze_structure_evolution(str(pdf_file))
        
        if analysis:
            # Save detailed analysis
            output_file = f"structure_validation_{pdf_file.stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            
            # Print summary
            print(f"\n📊 STRUCTURE EVOLUTION SUMMARY")
            print(f"📄 Document: {pdf_file.name}")
            print(f"📏 Total pages: {analysis['total_pages']}")
            
            evolution = analysis['evolution_summary']
            
            print(f"\n🔍 Pattern Consistency:")
            for pattern, data in evolution['pattern_consistency'].items():
                status = "✅ Consistent" if data['consistent'] else "⚠️  Varies"
                print(f"   {pattern}: {status} (avg: {data['average_per_chunk']:.1f}/chunk)")
            
            print(f"\n📋 Content Types Found:")
            for content_type, count in evolution['content_type_distribution'].items():
                print(f"   {content_type}: {count} pages")
            
            print(f"\n💡 Recommendations:")
            for rec in evolution['recommendations']:
                print(f"   {rec}")
            
            print(f"\n💾 Detailed analysis saved: {output_file}")

if __name__ == "__main__":
    main()