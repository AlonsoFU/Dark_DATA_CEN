#!/usr/bin/env python3
"""
Truly Adaptive Document Processor
Handles structure changes at ANY point in the document
"""

import PyPDF2
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple

class TrulyAdaptiveProcessor:
    def __init__(self):
        self.max_chunk_size = 3000
        self.patterns = {
            'section_headers': [
                r'^(\d+)\.\s+(.+)$',
                r'^([A-Z\s]{5,})$',
                r'^([A-Z][^\.]+):$'
            ],
            'companies': [
                r'(ENEL\s+(?:GENERACIÓN|DISTRIBUCIÓN|GREEN\s+POWER)?(?:\s+CHILE)?(?:\s+S\.A\.)?)',
                r'(COLBÚN\s+S\.A\.?)',
                r'(AES\s+(?:ANDES|GENER)?(?:\s+S\.A\.)?)',
                r'(INTERCHILE\s+S\.A\.?)',
                r'([A-Z][A-Za-z\s]*(?:S\.A\.|LTDA\.|SPA))',
            ],
            'technical_specs': r'(\d+[,.]?\d*)\s*(MW|kV|Hz|A|V|Ω|km|MVA)',
            'dates': r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}(?:\s+\d{1,2}:\d{2})?)',
            'compliance': r'(informe\s+(?:en\s+plazo|no\s+recibido|fuera\s+de\s+plazo))',
            'equipment': r'((?:Siemens|ABB|GE|Schneider|Areva)\s+[A-Z0-9\-]+)',
        }
    
    def process_with_continuous_adaptation(self, pdf_path: str) -> Dict[str, Any]:
        """Process document with continuous adaptation - no sampling"""
        
        print(f"🔄 Truly adaptive processing: {Path(pdf_path).name}")
        
        chunks = []
        page_classifications = []  # Track classification of every page
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                print(f"📄 Processing {total_pages} pages individually...")
                
                # Process every single page
                for page_num, page in enumerate(pdf_reader.pages):
                    if page_num % 50 == 0:
                        print(f"   📍 Page {page_num + 1}/{total_pages}")
                    
                    try:
                        text = page.extract_text()
                        
                        # Classify THIS specific page
                        page_type = self._classify_page_real_time(text, page_num + 1)
                        page_classifications.append({
                            'page': page_num + 1,
                            'type': page_type,
                            'text_length': len(text),
                            'pattern_density': self._calculate_pattern_density(text)
                        })
                        
                        # Add to growing chunk list
                        page_data = {
                            'page_number': page_num + 1,
                            'content': text,
                            'content_type': page_type,
                            'extracted_entities': self._extract_all_entities(text),
                            'metadata': {
                                'char_count': len(text),
                                'line_count': len(text.split('\n')),
                                'pattern_density': self._calculate_pattern_density(text)
                            }
                        }
                        
                    except Exception as e:
                        print(f"      ⚠️  Error processing page {page_num + 1}: {e}")
                        page_data = {
                            'page_number': page_num + 1,
                            'content': '',
                            'content_type': 'error',
                            'extracted_entities': {},
                            'error': str(e)
                        }
                        page_classifications.append({
                            'page': page_num + 1,
                            'type': 'error',
                            'text_length': 0,
                            'pattern_density': {}
                        })
                
                # Now intelligently group pages into chunks
                chunks = self._intelligent_chunking(page_classifications, pdf_reader)
                
        except Exception as e:
            print(f"❌ Error processing document: {e}")
            return {'error': str(e)}
        
        return {
            'document': Path(pdf_path).name,
            'total_pages': total_pages,
            'page_classifications': page_classifications,
            'chunks': chunks,
            'adaptation_stats': self._analyze_adaptation_performance(page_classifications, chunks)
        }
    
    def _classify_page_real_time(self, text: str, page_num: int) -> str:
        """Classify page in real-time with full pattern analysis"""
        
        if len(text.strip()) < 100:
            return 'sparse_content'
        
        # Calculate pattern densities
        densities = {}
        for pattern_name, patterns in self.patterns.items():
            total_matches = 0
            
            if isinstance(patterns, list):
                for pattern in patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                    total_matches += len(matches)
            else:
                matches = re.findall(patterns, text, re.IGNORECASE | re.MULTILINE)
                total_matches = len(matches)
            
            # Calculate density per 1000 chars
            density = (total_matches / len(text)) * 1000 if text else 0
            densities[pattern_name] = {
                'count': total_matches,
                'density': density
            }
        
        # Intelligent classification based on densities
        company_density = densities['companies']['density']
        tech_density = densities['technical_specs']['density']
        section_density = densities['section_headers']['density']
        
        # Decision tree based on actual content
        if section_density > 2:
            return 'structured_section'
        elif company_density > 15:
            return 'company_listing'
        elif tech_density > 20:
            return 'technical_specifications'
        elif company_density > 5 and tech_density > 5:
            return 'mixed_content'
        elif len(text) > 1500:
            return 'narrative_text'
        else:
            return 'sparse_content'
    
    def _calculate_pattern_density(self, text: str) -> Dict[str, float]:
        """Calculate pattern density for this text"""
        densities = {}
        text_len = len(text) if text else 1
        
        for pattern_name, patterns in self.patterns.items():
            count = 0
            if isinstance(patterns, list):
                for pattern in patterns:
                    count += len(re.findall(pattern, text, re.IGNORECASE))
            else:
                count = len(re.findall(patterns, text, re.IGNORECASE))
            
            densities[pattern_name] = (count / text_len) * 1000  # per 1000 chars
        
        return densities
    
    def _extract_all_entities(self, text: str) -> Dict[str, List]:
        """Extract all entities from text"""
        entities = {}
        
        for pattern_name, patterns in self.patterns.items():
            matches = []
            if isinstance(patterns, list):
                for pattern in patterns:
                    found = re.findall(pattern, text, re.IGNORECASE)
                    matches.extend(found)
            else:
                found = re.findall(patterns, text, re.IGNORECASE)
                matches.extend(found)
            
            entities[pattern_name] = matches
        
        return entities
    
    def _intelligent_chunking(self, page_classifications: List[Dict], pdf_reader) -> List[Dict[str, Any]]:
        """Group pages into intelligent chunks based on classifications"""
        
        chunks = []
        current_chunk = {
            'pages': [],
            'content': '',
            'primary_type': None,
            'type_distribution': {},
            'extracted_data': {}
        }
        
        for i, page_info in enumerate(page_classifications):
            page_num = page_info['page']
            page_type = page_info['type']
            
            # Get actual page content
            try:
                page_content = pdf_reader.pages[page_num - 1].extract_text()
            except:
                page_content = ""
            
            # Decision: Should we start a new chunk?
            should_split = False
            
            # Split on major content type changes
            if current_chunk['primary_type'] and page_type != current_chunk['primary_type']:
                # Don't split on minor variations
                compatible_types = {
                    'narrative_text': ['mixed_content'],
                    'mixed_content': ['narrative_text', 'technical_specifications', 'company_listing'],
                    'technical_specifications': ['mixed_content'],
                    'company_listing': ['mixed_content']
                }
                
                current_compatible = compatible_types.get(current_chunk['primary_type'], [])
                if page_type not in current_compatible:
                    should_split = True
            
            # Split on size limit
            if len(current_chunk['content']) + len(page_content) > self.max_chunk_size:
                should_split = True
            
            # Split on major section breaks (high section header density)
            if page_info.get('pattern_density', {}).get('section_headers', 0) > 3:
                should_split = True
            
            # Execute split if needed
            if should_split and current_chunk['pages']:
                chunks.append(self._finalize_intelligent_chunk(current_chunk))
                current_chunk = {
                    'pages': [],
                    'content': '',
                    'primary_type': None,
                    'type_distribution': {},
                    'extracted_data': {}
                }
            
            # Add page to current chunk
            current_chunk['pages'].append(page_num)
            current_chunk['content'] += f"\n[Page {page_num}]\n{page_content}\n"
            
            # Update type tracking
            if not current_chunk['primary_type']:
                current_chunk['primary_type'] = page_type
            
            current_chunk['type_distribution'][page_type] = current_chunk['type_distribution'].get(page_type, 0) + 1
            
            # Extract and merge entities
            page_entities = self._extract_all_entities(page_content)
            for entity_type, entities in page_entities.items():
                if entity_type not in current_chunk['extracted_data']:
                    current_chunk['extracted_data'][entity_type] = []
                current_chunk['extracted_data'][entity_type].extend(entities)
        
        # Don't forget the last chunk
        if current_chunk['pages']:
            chunks.append(self._finalize_intelligent_chunk(current_chunk))
        
        return chunks
    
    def _finalize_intelligent_chunk(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize chunk with comprehensive metadata"""
        return {
            'chunk_type': 'truly_adaptive',
            'pages': chunk['pages'],
            'page_count': len(chunk['pages']),
            'page_range': f"{min(chunk['pages'])}-{max(chunk['pages'])}",
            'content': chunk['content'].strip(),
            'content_length': len(chunk['content']),
            'primary_content_type': chunk['primary_type'],
            'content_type_distribution': chunk['type_distribution'],
            'extracted_entities': {
                k: list(set(v)) for k, v in chunk['extracted_data'].items()  # Remove duplicates
            },
            'entity_counts': {
                k: len(set(v)) for k, v in chunk['extracted_data'].items()
            },
            'metadata': {
                'adaptation_strategy': 'page_by_page_classification',
                'content_diversity': len(chunk['type_distribution']),
                'entity_richness': sum(len(set(v)) for v in chunk['extracted_data'].values())
            }
        }
    
    def _analyze_adaptation_performance(self, page_classifications: List[Dict], chunks: List[Dict]) -> Dict[str, Any]:
        """Analyze how well the adaptation worked"""
        
        # Page type distribution
        page_types = {}
        for page in page_classifications:
            page_type = page['type']
            page_types[page_type] = page_types.get(page_type, 0) + 1
        
        # Chunk effectiveness
        chunk_sizes = [chunk['page_count'] for chunk in chunks]
        
        return {
            'total_pages_processed': len(page_classifications),
            'page_type_distribution': page_types,
            'total_chunks_created': len(chunks),
            'average_chunk_size': sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0,
            'chunk_size_range': f"{min(chunk_sizes)}-{max(chunk_sizes)}" if chunk_sizes else "0-0",
            'adaptation_effectiveness': self._calculate_effectiveness_score(page_classifications, chunks)
        }
    
    def _calculate_effectiveness_score(self, page_classifications: List[Dict], chunks: List[Dict]) -> str:
        """Calculate overall effectiveness of adaptation"""
        
        # Good indicators:
        # - Reasonable number of chunks (not too many, not too few)
        # - Chunks group similar content types together
        # - Good entity extraction coverage
        
        total_pages = len(page_classifications)
        total_chunks = len(chunks)
        
        chunk_ratio = total_chunks / total_pages if total_pages > 0 else 0
        
        if 0.05 <= chunk_ratio <= 0.2:  # 5-20% of pages become chunks
            return "high_effectiveness"
        elif 0.02 <= chunk_ratio <= 0.3:
            return "moderate_effectiveness"
        else:
            return "needs_tuning"

def main():
    """Test truly adaptive processor"""
    
    processor = TrulyAdaptiveProcessor()
    
    # Test with real document
    test_file = Path("data_real/EAF-089-2025.pdf")
    if test_file.exists():
        result = processor.process_with_continuous_adaptation(str(test_file))
        
        if 'error' not in result:
            # Save results
            output_file = f"truly_adaptive_{test_file.stem}.json"
            
            # Save without page content to reduce file size
            save_result = result.copy()
            for chunk in save_result['chunks']:
                chunk['content'] = f"[{chunk['content_length']} characters]"  # Replace content with size
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(save_result, f, indent=2, ensure_ascii=False)
            
            # Print summary
            print(f"\n📊 TRULY ADAPTIVE PROCESSING RESULTS")
            print(f"📄 Document: {result['document']}")
            print(f"📏 Total pages: {result['total_pages']}")
            print(f"🔪 Total chunks: {len(result['chunks'])}")
            
            stats = result['adaptation_stats']
            print(f"\n📋 Page Type Distribution:")
            for page_type, count in stats['page_type_distribution'].items():
                print(f"   {page_type}: {count} pages")
            
            print(f"\n🎯 Adaptation Performance:")
            print(f"   Effectiveness: {stats['adaptation_effectiveness']}")
            print(f"   Avg chunk size: {stats['average_chunk_size']:.1f} pages")
            print(f"   Chunk size range: {stats['chunk_size_range']} pages")
            
            print(f"\n💾 Results saved: {output_file}")
    else:
        print("❌ Test file not found")

if __name__ == "__main__":
    main()