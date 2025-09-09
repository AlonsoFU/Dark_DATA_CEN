#!/usr/bin/env python3
"""
Document Structure Analyzer for Large PDF Reports
Analyzes document structure to understand information patterns
"""

import PyPDF2
import re
from pathlib import Path
import json
from typing import Dict, List, Any, Tuple
import argparse

class DocumentStructureAnalyzer:
    def __init__(self):
        self.patterns = {
            'headers': [
                r'^[A-Z\s]{3,}$',  # All caps headers
                r'^\d+\.\s+[A-Z][^\.]+$',  # Numbered sections
                r'^[A-Z][^\.]+:$',  # Colon-ended headers
            ],
            'dates': r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}-\d{2}-\d{2}',
            'companies': r'[A-Z][a-zA-Z\s]*S\.A\.|LTDA\.|SPA\.|ENEL|COLBÚN|AES|ENGIE',
            'technical_specs': r'\d+[,.]?\d*\s*(MW|kV|Hz|A|V|Ω|km)',
            'report_codes': r'EAF-\d{3}/\d{4}|[A-Z]{2,4}-\d{3}-\d{4}',
            'tables': r'\|.*\||\t.*\t',
            'references': r'\[\d+\]|Ref\.\s*\d+|Figura\s*\d+|Tabla\s*\d+'
        }
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Tuple[int, str]]:
        """Extract text from PDF with page numbers"""
        pages_text = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        text = page.extract_text()
                        pages_text.append((page_num, text))
                    except Exception as e:
                        print(f"⚠️  Error extracting page {page_num}: {e}")
                        pages_text.append((page_num, ""))
                        
        except Exception as e:
            print(f"❌ Error reading PDF {pdf_path}: {e}")
            
        return pages_text
    
    def analyze_page_structure(self, page_text: str) -> Dict[str, Any]:
        """Analyze structure of a single page"""
        lines = page_text.split('\n')
        
        structure = {
            'line_count': len(lines),
            'char_count': len(page_text),
            'headers': [],
            'patterns_found': {},
            'content_type': 'unknown'
        }
        
        # Find headers
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            for pattern in self.patterns['headers']:
                if re.match(pattern, line):
                    structure['headers'].append(line)
                    break
        
        # Find other patterns
        for pattern_name, pattern in self.patterns.items():
            if pattern_name == 'headers':
                continue
                
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                structure['patterns_found'][pattern_name] = matches
        
        # Determine content type
        structure['content_type'] = self.classify_content_type(structure)
        
        return structure
    
    def classify_content_type(self, structure: Dict[str, Any]) -> str:
        """Classify the type of content on the page"""
        patterns = structure['patterns_found']
        
        if 'tables' in patterns and len(patterns['tables']) > 3:
            return 'tabular_data'
        elif 'technical_specs' in patterns and len(patterns['technical_specs']) > 5:
            return 'technical_specifications'
        elif 'companies' in patterns and len(patterns['companies']) > 2:
            return 'company_information'
        elif len(structure['headers']) > 3:
            return 'structured_sections'
        elif structure['char_count'] < 500:
            return 'sparse_content'
        else:
            return 'narrative_text'
    
    def analyze_document(self, pdf_path: str) -> Dict[str, Any]:
        """Analyze complete document structure"""
        print(f"📄 Analyzing {Path(pdf_path).name}...")
        
        pages_text = self.extract_text_from_pdf(pdf_path)
        total_pages = len(pages_text)
        
        document_analysis = {
            'file_info': {
                'name': Path(pdf_path).name,
                'path': pdf_path,
                'total_pages': total_pages,
                'file_size_mb': Path(pdf_path).stat().st_size / 1024 / 1024
            },
            'pages': [],
            'summary': {
                'content_types': {},
                'all_headers': [],
                'pattern_summary': {},
                'section_boundaries': []
            }
        }
        
        # Analyze each page
        for page_num, page_text in pages_text:
            page_analysis = self.analyze_page_structure(page_text)
            page_analysis['page_number'] = page_num
            
            document_analysis['pages'].append(page_analysis)
            
            # Update summary
            content_type = page_analysis['content_type']
            document_analysis['summary']['content_types'][content_type] = \
                document_analysis['summary']['content_types'].get(content_type, 0) + 1
            
            document_analysis['summary']['all_headers'].extend(page_analysis['headers'])
            
            # Aggregate patterns
            for pattern_name, matches in page_analysis['patterns_found'].items():
                if pattern_name not in document_analysis['summary']['pattern_summary']:
                    document_analysis['summary']['pattern_summary'][pattern_name] = []
                document_analysis['summary']['pattern_summary'][pattern_name].extend(matches)
        
        # Find section boundaries
        document_analysis['summary']['section_boundaries'] = self.find_section_boundaries(document_analysis)
        
        return document_analysis
    
    def find_section_boundaries(self, document_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find major section boundaries in the document"""
        boundaries = []
        
        for page in document_analysis['pages']:
            if len(page['headers']) > 2:  # Pages with many headers likely start sections
                boundaries.append({
                    'page': page['page_number'],
                    'headers': page['headers'],
                    'content_type': page['content_type']
                })
        
        return boundaries
    
    def compare_documents(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare structure across multiple documents"""
        comparison = {
            'documents': [analysis['file_info']['name'] for analysis in analyses],
            'common_patterns': {},
            'structure_differences': {},
            'recommendations': []
        }
        
        # Find common patterns
        all_pattern_types = set()
        for analysis in analyses:
            all_pattern_types.update(analysis['summary']['pattern_summary'].keys())
        
        for pattern_type in all_pattern_types:
            pattern_counts = []
            for analysis in analyses:
                count = len(analysis['summary']['pattern_summary'].get(pattern_type, []))
                pattern_counts.append(count)
            
            comparison['common_patterns'][pattern_type] = {
                'counts': pattern_counts,
                'avg_per_doc': sum(pattern_counts) / len(pattern_counts),
                'consistent': max(pattern_counts) - min(pattern_counts) < 5
            }
        
        # Add recommendations
        comparison['recommendations'] = self.generate_recommendations(comparison, analyses)
        
        return comparison
    
    def generate_recommendations(self, comparison: Dict[str, Any], analyses: List[Dict[str, Any]]) -> List[str]:
        """Generate extraction strategy recommendations"""
        recommendations = []
        
        # Page count recommendations
        page_counts = [analysis['file_info']['total_pages'] for analysis in analyses]
        if max(page_counts) > 50:
            recommendations.append("Documents are large (>50 pages) - recommend chunking strategy")
        
        # Pattern-based recommendations
        if comparison['common_patterns'].get('technical_specs', {}).get('consistent', False):
            recommendations.append("Technical specifications are consistent - create structured extractor")
        
        if comparison['common_patterns'].get('companies', {}).get('consistent', False):
            recommendations.append("Company information patterns are consistent - prioritize company extraction")
        
        # Content type recommendations  
        for analysis in analyses:
            tabular_pages = analysis['summary']['content_types'].get('tabular_data', 0)
            if tabular_pages > 5:
                recommendations.append(f"Document has {tabular_pages} tabular pages - consider table extraction tools")
        
        return recommendations
    
    def save_analysis(self, analysis: Dict[str, Any], output_path: str):
        """Save analysis to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        print(f"💾 Analysis saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Analyze document structure")
    parser.add_argument('--input-dir', default='data_prueba', help='Input directory')
    parser.add_argument('--output-dir', default='analysis_output', help='Output directory')
    args = parser.parse_args()
    
    analyzer = DocumentStructureAnalyzer()
    
    # Create output directory
    Path(args.output_dir).mkdir(exist_ok=True)
    
    # Find PDF files
    input_path = Path(args.input_dir)
    pdf_files = list(input_path.glob('*.pdf'))
    
    if not pdf_files:
        print(f"❌ No PDF files found in {input_path}")
        return
    
    print(f"📁 Found {len(pdf_files)} PDF files")
    
    # Analyze each document
    analyses = []
    for pdf_file in pdf_files:
        analysis = analyzer.analyze_document(str(pdf_file))
        analyses.append(analysis)
        
        # Save individual analysis
        output_file = Path(args.output_dir) / f"{pdf_file.stem}_analysis.json"
        analyzer.save_analysis(analysis, str(output_file))
    
    # Compare documents if multiple
    if len(analyses) > 1:
        comparison = analyzer.compare_documents(analyses)
        comparison_file = Path(args.output_dir) / "document_comparison.json"
        analyzer.save_analysis(comparison, str(comparison_file))
        
        print("\n📊 STRUCTURE COMPARISON SUMMARY")
        print("=" * 50)
        for rec in comparison['recommendations']:
            print(f"💡 {rec}")
    
    # Print summary
    print(f"\n✅ Analysis complete! Check {args.output_dir}/ for results")

if __name__ == "__main__":
    main()