#!/usr/bin/env python3
"""
Adaptive Document Processor - Handles varying document structure
Adapts extraction strategy based on content type per section
"""

import PyPDF2
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

class AdaptiveDocumentProcessor:
    def __init__(self):
        # Multiple extraction strategies for different content types
        self.strategies = {
            'structured_section': self._extract_structured_content,
            'narrative_text': self._extract_narrative_content,
            'technical_specifications': self._extract_technical_content,
            'company_listing': self._extract_company_content,
            'mixed_content': self._extract_mixed_content,
            'sparse_content': self._extract_sparse_content
        }
        
        # Adaptive patterns that change based on context
        self.base_patterns = {
            'section_headers': [
                r'^(\d+)\.\s+(.+)$',  # Numbered sections
                r'^([A-Z\s]{5,})$',   # All caps headers  
                r'^([A-Z][^\.]+):$',  # Colon headers
                r'^\*\*(.+)\*\*$',    # Bold headers
            ],
            'companies': [
                r'(ENEL\s+(?:GENERACIÓN|DISTRIBUCIÓN|GREEN\s+POWER)?(?:\s+CHILE)?(?:\s+S\.A\.)?)',
                r'(COLBÚN\s+S\.A\.?)',
                r'(AES\s+(?:ANDES|GENER)?(?:\s+S\.A\.)?)',
                r'(INTERCHILE\s+S\.A\.?)',
                r'([A-Z][A-Za-z\s]*(?:S\.A\.|LTDA\.|SPA))',
            ],
            'technical_specs': r'(\d+[,.]?\d*)\s*(MW|kV|Hz|A|V|Ω|km|MVA)',
            'dates_times': r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}(?:\s+\d{1,2}:\d{2}(?::\d{2})?)?)',
            'compliance_status': r'(informe\s+(?:en\s+plazo|no\s+recibido|fuera\s+de\s+plazo|presentado))',
            'equipment': r'((?:Siemens|ABB|GE|Schneider|Areva)\s+[A-Z0-9\-]+)',
        }
    
    def analyze_and_process(self, pdf_path: str) -> Dict[str, Any]:
        """Main processing with adaptive strategies"""
        
        print(f"🔄 Adaptive processing: {Path(pdf_path).name}")
        
        # Step 1: Quick structure scan
        structure_map = self._scan_document_structure(pdf_path)
        
        # Step 2: Adaptive chunk processing
        chunks = self._process_with_adaptive_strategies(pdf_path, structure_map)
        
        # Step 3: Cross-reference and validate
        validated_chunks = self._validate_and_enhance_chunks(chunks)
        
        return {
            'document': Path(pdf_path).name,
            'structure_map': structure_map,
            'chunks': validated_chunks,
            'processing_stats': {
                'total_chunks': len(validated_chunks),
                'strategies_used': self._get_strategies_used(validated_chunks),
                'content_types': self._get_content_type_distribution(validated_chunks)
            }
        }
    
    def _scan_document_structure(self, pdf_path: str) -> Dict[str, Any]:
        """Quick scan to map document structure variation"""
        
        structure_map = {
            'page_types': {},
            'section_breaks': [],
            'content_transitions': [],
            'dominant_patterns': {}
        }
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                # Sample every 10th page for structure mapping
                sample_interval = max(1, total_pages // 50)  # 50 samples max
                
                for page_num in range(0, total_pages, sample_interval):
                    try:
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        
                        page_type = self._classify_page_type(text)
                        structure_map['page_types'][page_num] = page_type
                        
                        # Detect section breaks
                        if self._is_section_break(text):
                            structure_map['section_breaks'].append(page_num)
                            
                    except Exception as e:
                        print(f"      ⚠️  Error scanning page {page_num + 1}: {e}")
                        
        except Exception as e:
            print(f"❌ Error scanning document: {e}")
        
        return structure_map
    
    def _classify_page_type(self, text: str) -> str:
        """Classify page content type for adaptive strategy"""
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if len(lines) < 3:
            return 'sparse_content'
        
        # Count pattern occurrences
        pattern_counts = {}
        for pattern_name, patterns in self.base_patterns.items():
            if isinstance(patterns, list):
                total_matches = 0
                for pattern in patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                    total_matches += len(matches)
                pattern_counts[pattern_name] = total_matches
            else:
                matches = re.findall(patterns, text, re.IGNORECASE | re.MULTILINE)
                pattern_counts[pattern_name] = len(matches)
        
        # Adaptive classification based on pattern density
        if pattern_counts.get('companies', 0) > 10:
            return 'company_listing'
        elif pattern_counts.get('technical_specs', 0) > 15:
            return 'technical_specifications'  
        elif pattern_counts.get('section_headers', 0) > 3:
            return 'structured_section'
        elif len(text) < 500:
            return 'sparse_content'
        elif any(pattern_counts.get(p, 0) > 3 for p in ['companies', 'technical_specs', 'equipment']):
            return 'mixed_content'
        else:
            return 'narrative_text'
    
    def _is_section_break(self, text: str) -> bool:
        """Detect if page represents a major section break"""
        
        # Look for strong section indicators
        section_indicators = [
            r'^\s*\d+\.\s+[A-Z][^\.]+$',  # Numbered main sections
            r'^\s*[A-Z\s]{10,}\s*$',      # Long all-caps headers
            r'^\s*ANEXO\s+[A-Z0-9]',      # Anexo sections
        ]
        
        for indicator in section_indicators:
            if re.search(indicator, text, re.MULTILINE):
                return True
        
        return False
    
    def _process_with_adaptive_strategies(self, pdf_path: str, structure_map: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process document using adaptive strategies per page type"""
        
        chunks = []
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                current_chunk = {
                    'pages': [],
                    'content': '',
                    'extracted_data': {},
                    'strategy_used': 'unknown'
                }
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        text = page.extract_text()
                        
                        # CLASSIFY EVERY SINGLE PAGE - no sampling!
                        content_type = self._classify_page_type(text)
                        
                        # Check if we need a new chunk
                        if self._should_start_new_chunk(current_chunk, content_type, page_num, structure_map):
                            if current_chunk['pages']:  # Save previous chunk if has content
                                chunks.append(self._finalize_chunk(current_chunk))
                            
                            current_chunk = {
                                'pages': [],
                                'content': '',
                                'extracted_data': {},
                                'strategy_used': content_type
                            }
                        
                        # Add page to current chunk
                        current_chunk['pages'].append(page_num + 1)
                        current_chunk['content'] += f"\n[Page {page_num + 1}]\n{text}\n"
                        
                        # Apply adaptive extraction strategy
                        if content_type in self.strategies:
                            page_data = self.strategies[content_type](text, page_num + 1)
                            self._merge_extracted_data(current_chunk['extracted_data'], page_data)
                        
                        # Size-based chunking as fallback
                        if len(current_chunk['content']) > 4000:  # 4KB max
                            chunks.append(self._finalize_chunk(current_chunk))
                            current_chunk = {
                                'pages': [],
                                'content': '',
                                'extracted_data': {},
                                'strategy_used': content_type
                            }
                            
                    except Exception as e:
                        print(f"      ⚠️  Error processing page {page_num + 1}: {e}")
                
                # Don't forget the last chunk
                if current_chunk['pages']:
                    chunks.append(self._finalize_chunk(current_chunk))
                    
        except Exception as e:
            print(f"❌ Error processing document: {e}")
        
        return chunks
    
    def _should_start_new_chunk(self, current_chunk: Dict, content_type: str, page_num: int, structure_map: Dict) -> bool:
        """Decide if we should start a new chunk"""
        
        # Always start new chunk on major section breaks
        if page_num in structure_map['section_breaks']:
            return True
        
        # Start new chunk on content type change (but not for similar types)
        similar_types = [
            ['narrative_text', 'mixed_content'],
            ['technical_specifications', 'mixed_content'],
            ['company_listing', 'mixed_content']
        ]
        
        current_strategy = current_chunk.get('strategy_used', 'unknown')
        if current_strategy != content_type:
            # Check if types are similar
            for similar_group in similar_types:
                if current_strategy in similar_group and content_type in similar_group:
                    return False  # Don't split similar types
            return True
        
        return False
    
    # Adaptive extraction strategies for different content types
    def _extract_structured_content(self, text: str, page_num: int) -> Dict[str, Any]:
        """Extract from structured sections (headers, numbered lists)"""
        data = {
            'section_headers': [],
            'structured_items': [],
            'key_information': []
        }
        
        # Extract headers with multiple patterns
        for pattern in self.base_patterns['section_headers']:
            matches = re.findall(pattern, text, re.MULTILINE)
            data['section_headers'].extend(matches)
        
        return data
    
    def _extract_narrative_content(self, text: str, page_num: int) -> Dict[str, Any]:
        """Extract from narrative text (descriptions, explanations)"""
        data = {
            'key_entities': [],
            'dates_mentioned': [],
            'technical_references': []
        }
        
        # Extract dates and times
        dates = re.findall(self.base_patterns['dates_times'], text, re.IGNORECASE)
        data['dates_mentioned'] = dates
        
        # Extract any company mentions
        for pattern in self.base_patterns['companies']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            data['key_entities'].extend(matches)
        
        return data
    
    def _extract_technical_content(self, text: str, page_num: int) -> Dict[str, Any]:
        """Extract from technical specifications"""
        data = {
            'specifications': [],
            'equipment_mentioned': [],
            'measurements': []
        }
        
        # Extract technical specifications
        specs = re.findall(self.base_patterns['technical_specs'], text, re.IGNORECASE)
        data['specifications'] = [{'value': s[0], 'unit': s[1]} for s in specs]
        
        # Extract equipment
        equipment = re.findall(self.base_patterns['equipment'], text, re.IGNORECASE)
        data['equipment_mentioned'] = equipment
        
        return data
    
    def _extract_company_content(self, text: str, page_num: int) -> Dict[str, Any]:
        """Extract from company listings and compliance info"""
        data = {
            'companies_listed': [],
            'compliance_status': [],
            'contact_info': []
        }
        
        # Extract companies with all patterns
        for pattern in self.base_patterns['companies']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            data['companies_listed'].extend(matches)
        
        # Extract compliance status
        compliance = re.findall(self.base_patterns['compliance_status'], text, re.IGNORECASE)
        data['compliance_status'] = compliance
        
        return data
    
    def _extract_mixed_content(self, text: str, page_num: int) -> Dict[str, Any]:
        """Extract from mixed content (combination of types)"""
        # Combine strategies
        data = {}
        data.update(self._extract_narrative_content(text, page_num))
        data.update(self._extract_technical_content(text, page_num))
        data.update(self._extract_company_content(text, page_num))
        
        return data
    
    def _extract_sparse_content(self, text: str, page_num: int) -> Dict[str, Any]:
        """Extract from sparse content (headers, page breaks)"""
        return {
            'content_type': 'sparse',
            'text_length': len(text),
            'likely_header': len(text.split('\n')) < 5
        }
    
    def _merge_extracted_data(self, target: Dict[str, Any], source: Dict[str, Any]):
        """Merge extracted data from multiple pages"""
        for key, value in source.items():
            if key not in target:
                target[key] = []
            
            if isinstance(value, list):
                target[key].extend(value)
            else:
                target[key].append(value)
    
    def _finalize_chunk(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize chunk with metadata and cleanup"""
        return {
            'type': 'adaptive_chunk',
            'strategy': chunk['strategy_used'],
            'pages': chunk['pages'],
            'page_count': len(chunk['pages']),
            'content': chunk['content'].strip(),
            'content_length': len(chunk['content']),
            'extracted_data': chunk['extracted_data'],
            'metadata': {
                'processing_strategy': chunk['strategy_used'],
                'page_range': f"{min(chunk['pages'])}-{max(chunk['pages'])}",
                'extraction_completeness': self._assess_extraction_quality(chunk)
            }
        }
    
    def _assess_extraction_quality(self, chunk: Dict[str, Any]) -> str:
        """Assess quality of extraction for this chunk"""
        extracted = chunk['extracted_data']
        
        if not extracted:
            return 'minimal'
        
        total_items = sum(len(v) if isinstance(v, list) else 1 for v in extracted.values())
        
        if total_items > 20:
            return 'comprehensive'
        elif total_items > 5:
            return 'adequate'  
        else:
            return 'basic'
    
    def _validate_and_enhance_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Cross-validate and enhance chunks"""
        # Add cross-references, fix boundaries, etc.
        enhanced_chunks = []
        
        for i, chunk in enumerate(chunks):
            enhanced_chunk = chunk.copy()
            
            # Add chunk index
            enhanced_chunk['chunk_id'] = i
            
            # Add neighboring context
            if i > 0:
                enhanced_chunk['metadata']['previous_chunk_strategy'] = chunks[i-1]['strategy']
            if i < len(chunks) - 1:
                enhanced_chunk['metadata']['next_chunk_strategy'] = chunks[i+1]['strategy']
            
            enhanced_chunks.append(enhanced_chunk)
        
        return enhanced_chunks
    
    def _get_strategies_used(self, chunks: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get count of strategies used"""
        strategy_counts = {}
        for chunk in chunks:
            strategy = chunk.get('strategy', 'unknown')
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
        return strategy_counts
    
    def _get_content_type_distribution(self, chunks: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of content types"""
        return self._get_strategies_used(chunks)  # Same thing for now

def main():
    """Test adaptive processor"""
    processor = AdaptiveDocumentProcessor()
    
    # Test with real document
    test_file = Path("data_real/EAF-089-2025.pdf")
    if test_file.exists():
        result = processor.analyze_and_process(str(test_file))
        
        # Save results
        output_file = f"adaptive_processing_{test_file.stem}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # Print summary
        print(f"\n📊 ADAPTIVE PROCESSING RESULTS")
        print(f"📄 Document: {result['document']}")
        print(f"📏 Total chunks: {result['processing_stats']['total_chunks']}")
        
        print(f"\n🔧 Strategies used:")
        for strategy, count in result['processing_stats']['strategies_used'].items():
            print(f"   {strategy}: {count} chunks")
        
        print(f"\n💾 Results saved: {output_file}")
    else:
        print("❌ Test file not found: data_real/EAF-089-2025.pdf")

if __name__ == "__main__":
    main()