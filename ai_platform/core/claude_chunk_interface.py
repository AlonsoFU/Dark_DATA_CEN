#!/usr/bin/env python3
"""
Claude-Friendly Interface for Large Document Chunks
Allows intelligent querying of processed document chunks
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

class ClaudeChunkInterface:
    def __init__(self, processed_docs_dir: str = "processed_docs"):
        self.processed_docs_dir = Path(processed_docs_dir)
        self.loaded_documents = {}
        self.company_indexes = {}
        self._load_all_documents()
    
    def _load_all_documents(self):
        """Load all processed documents into memory for fast querying"""
        
        if not self.processed_docs_dir.exists():
            print(f"❌ Processed docs directory {self.processed_docs_dir} not found")
            return
        
        # Find all chunk files
        chunk_files = list(self.processed_docs_dir.glob("*_chunks.json"))
        
        for chunk_file in chunk_files:
            doc_name = chunk_file.stem.replace("_chunks", "")
            
            # Load chunks
            with open(chunk_file, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
            
            # Load company index
            company_index_file = self.processed_docs_dir / f"{doc_name}_company_index.json"
            if company_index_file.exists():
                with open(company_index_file, 'r', encoding='utf-8') as f:
                    company_index = json.load(f)
            else:
                company_index = {}
            
            self.loaded_documents[doc_name] = chunks
            self.company_indexes[doc_name] = company_index
            
            print(f"📄 Loaded {doc_name}: {len(chunks)} chunks")
    
    def search_by_keyword(self, keyword: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for chunks containing specific keywords"""
        
        results = []
        keyword_lower = keyword.lower()
        
        for doc_name, chunks in self.loaded_documents.items():
            for i, chunk in enumerate(chunks):
                content = chunk.get('content', '').lower()
                header = chunk.get('header', '').lower()
                
                if keyword_lower in content or keyword_lower in header:
                    results.append({
                        'document': doc_name,
                        'chunk_index': i,
                        'relevance_score': self._calculate_relevance(chunk, keyword_lower),
                        'header': chunk.get('header', ''),
                        'preview': self._get_content_preview(chunk, keyword, 200),
                        'metadata': chunk.get('metadata', {})
                    })
        
        # Sort by relevance and limit results
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:limit]
    
    def search_by_company(self, company: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find chunks related to specific company"""
        
        results = []
        
        for doc_name, company_index in self.company_indexes.items():
            # Direct company match
            if company in company_index:
                chunk_indices = company_index[company][:limit]
                chunks = self.loaded_documents[doc_name]
                
                for chunk_idx in chunk_indices:
                    if chunk_idx < len(chunks):
                        chunk = chunks[chunk_idx]
                        results.append({
                            'document': doc_name,
                            'chunk_index': chunk_idx,
                            'header': chunk.get('header', ''),
                            'preview': self._get_content_preview(chunk, company, 200),
                            'metadata': chunk.get('metadata', {}),
                            'match_type': 'direct_index'
                        })
            
            # Fuzzy company matching in chunk content
            else:
                chunks = self.loaded_documents[doc_name]
                for i, chunk in enumerate(chunks):
                    content = chunk.get('content', '').lower()
                    if company.lower() in content:
                        results.append({
                            'document': doc_name,
                            'chunk_index': i,
                            'header': chunk.get('header', ''),
                            'preview': self._get_content_preview(chunk, company, 200),
                            'metadata': chunk.get('metadata', {}),
                            'match_type': 'content_search'
                        })
        
        return results[:limit]
    
    def get_section_by_number(self, section_number: str, doc_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all chunks from a specific numbered section (e.g., "1.", "2.")"""
        
        results = []
        target_docs = [doc_name] if doc_name else self.loaded_documents.keys()
        
        for doc in target_docs:
            if doc not in self.loaded_documents:
                continue
                
            chunks = self.loaded_documents[doc]
            for i, chunk in enumerate(chunks):
                metadata = chunk.get('metadata', {})
                chunk_section = metadata.get('section_number')
                
                if chunk_section == section_number:
                    results.append({
                        'document': doc,
                        'chunk_index': i,
                        'header': chunk.get('header', ''),
                        'content': chunk.get('content', ''),
                        'metadata': metadata
                    })
        
        return results
    
    def get_document_overview(self, doc_name: Optional[str] = None) -> Dict[str, Any]:
        """Get overview of document structure and content"""
        
        if doc_name and doc_name in self.loaded_documents:
            docs_to_analyze = {doc_name: self.loaded_documents[doc_name]}
        else:
            docs_to_analyze = self.loaded_documents
        
        overview = {}
        
        for doc, chunks in docs_to_analyze.items():
            # Get section headers
            section_headers = []
            companies = set()
            
            for chunk in chunks[:20]:  # First 20 chunks for overview
                header = chunk.get('header', '')
                if header and len(header) < 100:  # Reasonable header length
                    section_headers.append(header)
                
                # Extract companies from metadata
                metadata = chunk.get('metadata', {})
                extracted_data = metadata.get('extracted_data', {})
                chunk_companies = extracted_data.get('companies', [])
                companies.update(chunk_companies)
            
            overview[doc] = {
                'total_chunks': len(chunks),
                'main_sections': section_headers[:10],  # Top 10 sections
                'companies_found': list(companies)[:10],  # Top 10 companies
                'indexed_companies': list(self.company_indexes.get(doc, {}).keys())
            }
        
        return overview
    
    def get_chunk_content(self, doc_name: str, chunk_index: int) -> Optional[Dict[str, Any]]:
        """Get full content of specific chunk"""
        
        if doc_name not in self.loaded_documents:
            return None
        
        chunks = self.loaded_documents[doc_name]
        if chunk_index >= len(chunks):
            return None
        
        return chunks[chunk_index]
    
    def _calculate_relevance(self, chunk: Dict[str, Any], keyword: str) -> float:
        """Calculate relevance score for keyword match"""
        
        content = chunk.get('content', '').lower()
        header = chunk.get('header', '').lower()
        
        # Count keyword occurrences
        content_matches = content.count(keyword)
        header_matches = header.count(keyword) * 2  # Header matches worth more
        
        # Bonus for being in section header
        header_bonus = 10 if keyword in header else 0
        
        # Penalty for very long chunks (less focused)
        length_penalty = len(content) / 1000
        
        score = content_matches + header_matches + header_bonus - length_penalty
        return max(0, score)
    
    def _get_content_preview(self, chunk: Dict[str, Any], highlight_term: str, max_chars: int) -> str:
        """Get preview of chunk content with highlighted term"""
        
        content = chunk.get('content', '')
        if not content:
            return ""
        
        # Find first occurrence of highlight term
        content_lower = content.lower()
        highlight_lower = highlight_term.lower()
        
        start_pos = content_lower.find(highlight_lower)
        if start_pos == -1:
            # Term not found, return beginning
            start_pos = 0
        else:
            # Center around the term
            start_pos = max(0, start_pos - max_chars // 2)
        
        end_pos = min(len(content), start_pos + max_chars)
        preview = content[start_pos:end_pos]
        
        # Add ellipsis if truncated
        if start_pos > 0:
            preview = "..." + preview
        if end_pos < len(content):
            preview = preview + "..."
        
        return preview
    
    def claude_friendly_search(self, query: str, max_results: int = 3) -> str:
        """
        Main interface for Claude - returns formatted search results
        This is the function Claude should call most often
        """
        
        # Detect query type
        if any(company in query.upper() for company in ['ENEL', 'COLBUN', 'AES', 'INTERCHILE']):
            # Company-focused query
            company_terms = [term for term in ['ENEL', 'COLBUN', 'AES', 'INTERCHILE'] if term in query.upper()]
            results = []
            for company in company_terms:
                results.extend(self.search_by_company(company, max_results))
        
        elif re.search(r'\b\d+\.', query):
            # Section number query (e.g., "section 1." or "1.")
            section_match = re.search(r'\b(\d+)\.', query)
            if section_match:
                section_num = section_match.group(1)
                results = self.get_section_by_number(section_num)
            else:
                results = []
        
        else:
            # General keyword search
            results = self.search_by_keyword(query, max_results)
        
        # Format results for Claude
        if not results:
            return f"No results found for query: '{query}'"
        
        formatted_results = []
        formatted_results.append(f"🔍 Search results for: '{query}'")
        formatted_results.append("=" * 50)
        
        for i, result in enumerate(results[:max_results], 1):
            doc_name = result['document']
            header = result['header'][:80] + "..." if len(result['header']) > 80 else result['header']
            preview = result.get('preview', result.get('content', ''))[:200] + "..."
            
            formatted_results.append(f"\n{i}. 📄 {doc_name}")
            formatted_results.append(f"   📋 {header}")
            formatted_results.append(f"   💬 {preview}")
            
            if 'metadata' in result and result['metadata']:
                metadata = result['metadata']
                if 'section_number' in metadata:
                    formatted_results.append(f"   🔢 Section: {metadata['section_number']}")
        
        return "\n".join(formatted_results)

def main():
    """Interactive testing interface"""
    
    interface = ClaudeChunkInterface()
    
    if not interface.loaded_documents:
        print("❌ No processed documents found. Run large_document_processor.py first.")
        return
    
    print("\n🤖 CLAUDE CHUNK INTERFACE")
    print("=" * 40)
    
    # Show available documents
    overview = interface.get_document_overview()
    print(f"\n📚 Available Documents:")
    for doc_name, info in overview.items():
        print(f"   📄 {doc_name}: {info['total_chunks']} chunks")
        print(f"      Companies: {', '.join(info['companies_found'][:3])}")
        print(f"      Sections: {', '.join(info['main_sections'][:3])}")
    
    # Interactive search
    print(f"\n🔍 Try some searches:")
    test_queries = [
        "ENEL compliance",
        "Siemens protection system", 
        "section 1.",
        "equipment failure"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")
        result = interface.claude_friendly_search(query)
        print(result)
        print()

if __name__ == "__main__":
    main()