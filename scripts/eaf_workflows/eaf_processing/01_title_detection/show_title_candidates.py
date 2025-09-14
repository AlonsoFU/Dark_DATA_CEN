#!/usr/bin/env python3
"""
Show Title Candidates - Preview what the interactive detector found
"""
import os
import sys
import re
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from PyPDF2 import PdfReader
except ImportError:
    print("Installing PyPDF2...")
    os.system("pip install PyPDF2")
    from PyPDF2 import PdfReader

def extract_page_text(reader, page_num):
    try:
        if 1 <= page_num <= len(reader.pages):
            return reader.pages[page_num - 1].extract_text().strip()
        return ""
    except:
        return ""

def is_title_page(text):
    clean_text = text.strip()
    words = clean_text.split()
    
    # Rule 1: Must start with "Anexo" or "INFORME DIARIO"
    title_patterns = [
        r'^ANEXO\s+N[º°ªo]?\s*\d+',
        r'^INFORME\s+DIARIO'
    ]
    
    matched_title = ""
    for pattern in title_patterns:
        match = re.search(pattern, clean_text, re.IGNORECASE)
        if match:
            matched_title = match.group(0)
            break
    
    if not matched_title:
        return False, ""
    
    # Rule 2: Minimal content (< 50 words)
    word_count = len(words)
    is_minimal = word_count < 50
    
    return is_minimal, matched_title

def main():
    doc_path = "data/documents/anexos_EAF/raw/Anexos-EAF-089-2025.pdf"
    
    print("📋 TITLE CANDIDATES PREVIEW")
    print("=" * 50)
    
    try:
        reader = PdfReader(doc_path)
        total_pages = len(reader.pages)
        print(f"📄 Document: {total_pages} pages")
        print()
        
        candidates = []
        
        # Scan all pages
        for page_num in range(1, total_pages + 1):
            text = extract_page_text(reader, page_num)
            is_title, title_text = is_title_page(text)
            
            if is_title:
                candidates.append({
                    'page': page_num,
                    'title': title_text,
                    'text': text,
                    'word_count': len(text.split())
                })
        
        print(f"🎯 Found {len(candidates)} potential title pages:")
        print()
        
        for i, candidate in enumerate(candidates, 1):
            print(f"📖 CANDIDATE {i}:")
            print(f"   📄 Page: {candidate['page']}")
            print(f"   🏷️  Title: '{candidate['title']}'")
            print(f"   📊 Words: {candidate['word_count']}")
            print(f"   📝 Content:")
            print("   " + "-" * 30)
            # Indent each line
            content_lines = candidate['text'].split('\n')
            for line in content_lines:
                if line.strip():
                    print(f"   {line}")
            print("   " + "-" * 30)
            print()
        
        print("=" * 50)
        print("💡 Next: Tell me which candidates you want to validate as titles")
        print("Example: 'Validate candidates 1, 3, and 5' or 'All look good' or 'Only candidate 2'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())