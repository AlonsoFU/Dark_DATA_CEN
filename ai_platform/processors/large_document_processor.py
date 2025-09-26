#!/usr/bin/env python3
"""
Large Document Processing Strategy
Based on structure analysis of EAF reports
"""

import PyPDF2
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime

class LargeDocumentProcessor:
    def __init__(self, max_chunk_size: int = 4000):
        self.max_chunk_size = max_chunk_size
        self.extraction_patterns = {
            'section_headers': [
                r'^(\d+)\.\s+(.+)$',  # Numbered sections: "1. Description"
                r'^([A-Z\s]{5,})$',   # All caps headers
                r'^([A-Z][^\.]+):$',  # Colon-ended headers
            ],
            'companies': [
                r'([A-Z][A-Za-z\s]*(?:S\.A\.|LTDA\.|SPA))',  # Standard company suffixes
                r'(ENEL|COLBÚN|AES|ENGIE|INTERCHILE)\s*(?:S\.A\.|LTDA\.|SPA)?',  # Known companies
            ],
            'technical_specs': r'(\d+[,.]?\d*)\s*(MW|kV|Hz|A|V|Ω|km)',
            'dates': r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}-\d{2}-\d{2})',
            'report_codes': r'(EAF-\d{3}/\d{4})',
            'compliance_status': r'(informe\s+(?:en\s+plazo|no\s+recibido|fuera\s+de\s+plazo))',
        }
    
    def extract_document_sections(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract major sections from document based on structure analysis"""
        
        pages_text = self._extract_all_text(pdf_path)
        sections = []
        current_section = None
        
        for page_num, page_text in pages_text:
            # Look for section headers
            lines = page_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check for numbered sections (primary structure)
                for pattern in self.extraction_patterns['section_headers']:
                    match = re.match(pattern, line)
                    if match:
                        # Save previous section
                        if current_section:
                            sections.append(current_section)
                        
                        # Start new section
                        current_section = {
                            'header': line,
                            'section_number': match.group(1) if '.' in pattern else None,
                            'title': match.group(2) if len(match.groups()) > 1 else line,
                            'start_page': page_num,
                            'content': [],
                            'extracted_data': {
                                'companies': set(),
                                'technical_specs': [],
                                'dates': [],
                                'compliance_info': []
                            }
                        }
                        break
            
            # Add page content to current section
            if current_section:
                current_section['content'].append({
                    'page': page_num,
                    'text': page_text
                })
                
                # Extract structured data from this page
                self._extract_page_data(page_text, current_section['extracted_data'])
        
        # Don't forget the last section
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def _extract_all_text(self, pdf_path: str) -> List[Tuple[int, str]]:
        """Extract text from all pages"""
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
            print(f"❌ Error reading PDF: {e}")
        
        return pages_text
    
    def _extract_page_data(self, page_text: str, extracted_data: Dict[str, Any]):
        """Extract structured data from page text"""
        
        # Extract companies
        for pattern in self.extraction_patterns['companies']:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]  # Take first group if tuple
                extracted_data['companies'].add(match.strip())
        
        # Extract technical specifications
        tech_matches = re.findall(self.extraction_patterns['technical_specs'], page_text)
        extracted_data['technical_specs'].extend([
            {'value': float(match[0].replace(',', '.')), 'unit': match[1]}
            for match in tech_matches
        ])
        
        # Extract dates
        date_matches = re.findall(self.extraction_patterns['dates'], page_text)
        extracted_data['dates'].extend(date_matches)
        
        # Extract compliance information
        compliance_matches = re.findall(self.extraction_patterns['compliance_status'], page_text, re.IGNORECASE)
        extracted_data['compliance_info'].extend(compliance_matches)
    
    def create_intelligent_chunks(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create intelligent chunks that respect document structure"""
        
        chunks = []
        
        for section in sections:
            section_text = self._combine_section_text(section)
            
            # If section is small enough, keep as single chunk
            if len(section_text) <= self.max_chunk_size:
                chunks.append({
                    'type': 'section',
                    'header': section['header'],
                    'content': section_text,
                    'metadata': {
                        'section_number': section.get('section_number'),
                        'start_page': section['start_page'],
                        'extracted_data': self._serialize_extracted_data(section['extracted_data'])
                    }
                })
            else:
                # Split large sections into sub-chunks
                sub_chunks = self._split_large_section(section)
                chunks.extend(sub_chunks)
        
        return chunks
    
    def _combine_section_text(self, section: Dict[str, Any]) -> str:
        """Combine all text from a section"""
        combined_text = f"{section['header']}\n\n"
        
        for content in section['content']:
            combined_text += f"[Page {content['page']}]\n{content['text']}\n\n"
        
        return combined_text
    
    def _split_large_section(self, section: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split large sections into manageable chunks"""
        chunks = []
        current_chunk = ""
        chunk_num = 1
        
        for content in section['content']:
            page_text = f"[Page {content['page']}]\n{content['text']}\n\n"
            
            # If adding this page would exceed limit, save current chunk
            if len(current_chunk + page_text) > self.max_chunk_size and current_chunk:
                chunks.append({
                    'type': 'section_part',
                    'header': f"{section['header']} (Part {chunk_num})",
                    'content': current_chunk,
                    'metadata': {
                        'section_number': section.get('section_number'),
                        'part_number': chunk_num,
                        'parent_section': section['header']
                    }
                })
                current_chunk = ""
                chunk_num += 1
            
            current_chunk += page_text
        
        # Don't forget the last chunk
        if current_chunk:
            chunks.append({
                'type': 'section_part',
                'header': f"{section['header']} (Part {chunk_num})",
                'content': current_chunk,
                'metadata': {
                    'section_number': section.get('section_number'),
                    'part_number': chunk_num,
                    'parent_section': section['header']
                }
            })
        
        return chunks
    
    def _serialize_extracted_data(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert extracted data to JSON-serializable format"""
        return {
            'companies': list(extracted_data['companies']),
            'technical_specs': extracted_data['technical_specs'],
            'dates': extracted_data['dates'],
            'compliance_info': extracted_data['compliance_info']
        }
    
    def create_company_focused_index(self, chunks: List[Dict[str, Any]]) -> Dict[str, List[int]]:
        """Create index mapping companies to relevant chunks"""
        company_index = {}
        
        for i, chunk in enumerate(chunks):
            if 'extracted_data' in chunk.get('metadata', {}):
                companies = chunk['metadata']['extracted_data'].get('companies', [])
                for company in companies:
                    if company not in company_index:
                        company_index[company] = []
                    company_index[company].append(i)
        
        return company_index
    
    def process_large_document(self, pdf_path: str, output_dir: str = "processed_docs") -> Dict[str, Any]:
        """Main processing pipeline for large documents"""
        
        print(f"🔄 Processing large document: {Path(pdf_path).name}")
        
        # Create output directory
        Path(output_dir).mkdir(exist_ok=True)
        
        # Step 1: Extract sections
        print("📄 Extracting document sections...")
        sections = self.extract_document_sections(pdf_path)
        print(f"   Found {len(sections)} major sections")
        
        # Step 2: Create intelligent chunks
        print("🔪 Creating intelligent chunks...")
        chunks = self.create_intelligent_chunks(sections)
        print(f"   Created {len(chunks)} chunks")
        
        # Step 3: Create company index
        print("🏢 Building company index...")
        company_index = self.create_company_focused_index(chunks)
        print(f"   Indexed {len(company_index)} companies")
        
        # Step 4: Save results
        doc_name = Path(pdf_path).stem
        
        # Save chunks
        chunks_file = Path(output_dir) / f"{doc_name}_chunks.json"
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        
        # Save company index  
        index_file = Path(output_dir) / f"{doc_name}_company_index.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(company_index, f, indent=2, ensure_ascii=False)
        
        # Save processing summary
        summary = {
            'document': Path(pdf_path).name,
            'processed_at': datetime.now().isoformat(),
            'sections_found': len(sections),
            'chunks_created': len(chunks),
            'companies_indexed': len(company_index),
            'section_headers': [s['header'] for s in sections[:10]],  # First 10 headers
            'top_companies': sorted(company_index.keys())[:20],  # Top 20 companies
            'files_created': [str(chunks_file), str(index_file)]
        }
        
        summary_file = Path(output_dir) / f"{doc_name}_processing_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Processing complete! Files saved in {output_dir}/")
        
        return summary

def main():
    """Process documents from data_real directory"""
    
    processor = LargeDocumentProcessor(max_chunk_size=3000)  # 3KB chunks for Claude
    
    # Process real documents (if they exist and are manageable)
    data_real_path = Path("data_real")
    if data_real_path.exists():
        pdf_files = list(data_real_path.glob("*.pdf"))
        
        for pdf_file in pdf_files:
            file_size_mb = pdf_file.stat().st_size / 1024 / 1024
            
            if file_size_mb > 50:  # Skip very large files for now
                print(f"⚠️  Skipping {pdf_file.name} ({file_size_mb:.1f}MB) - too large for initial processing")
                continue
                
            try:
                summary = processor.process_large_document(str(pdf_file))
                print(f"✅ {pdf_file.name} processed successfully")
                
                # Print summary
                print(f"   📊 {summary['sections_found']} sections, {summary['chunks_created']} chunks")
                print(f"   🏢 {summary['companies_indexed']} companies indexed")
                
            except Exception as e:
                print(f"❌ Error processing {pdf_file.name}: {e}")
    else:
        print("❌ data_real directory not found. Testing with data_prueba...")
        
        # Test with smaller documents
        data_prueba_path = Path("data_prueba") 
        pdf_files = list(data_prueba_path.glob("*.pdf"))
        
        for pdf_file in pdf_files:
            try:
                summary = processor.process_large_document(str(pdf_file))
                print(f"✅ {pdf_file.name} processed successfully")
            except Exception as e:
                print(f"❌ Error processing {pdf_file.name}: {e}")

if __name__ == "__main__":
    main()