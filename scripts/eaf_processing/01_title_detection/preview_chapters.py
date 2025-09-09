#!/usr/bin/env python3
"""
Chapter Preview - Show potential chapters without interaction
First scan to show you what we find, then you decide how to proceed
"""
import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from PyPDF2 import PdfReader
except ImportError:
    print("Installing PyPDF2...")
    os.system("pip install PyPDF2")
    from PyPDF2 import PdfReader

@dataclass
class ChapterFind:
    page: int
    title: str
    type: str
    preview: str
    confidence: str

def main():
    doc_path = "data/documents/anexos_EAF/raw/Anexos-EAF-089-2025.pdf"
    
    print("🔍 CHAPTER PREVIEW SCAN")
    print("=" * 50)
    
    try:
        reader = PdfReader(doc_path)
        total_pages = len(reader.pages)
        print(f"📄 Document: {total_pages} pages")
        print(f"🔍 Scanning for chapter patterns...")
        print()
        
        # Chapter patterns
        patterns = {
            r"ANEXO\s*N[º°ªo]?\s*\d+": "anexo_section",
            r"(?:RESUMEN\s*EJECUTIVO|SÍNTESIS\s*EJECUTIVA)": "executive_summary", 
            r"(?:CRONOLOGÍA|SECUENCIA|TIMELINE)": "chronology",
            r"(?:EMPRESA|INFORME\s*DE\s*LA\s*EMPRESA)": "company_reports",
            r"(?:ANÁLISIS\s*TÉCNICO|EVALUACIÓN\s*TÉCNICA)": "technical_analysis",
            r"(?:RECOMENDACIONES|MEDIDAS\s*CORRECTIVAS)": "recommendations",
            r"(?:CONCLUSIONES|SÍNTESIS\s*FINAL)": "conclusions"
        }
        
        found_chapters = []
        
        # Scan key pages (every 10th page for speed)
        scan_pages = list(range(1, min(100, total_pages), 5)) + list(range(100, total_pages, 10))
        
        for page_num in scan_pages:
            try:
                text = reader.pages[page_num - 1].extract_text()
                
                for pattern, chapter_type in patterns.items():
                    matches = list(re.finditer(pattern, text, re.IGNORECASE))
                    
                    for match in matches:
                        preview = text[:300].replace('\n', ' ').strip()
                        confidence = "HIGH" if match.start() < 100 else "MEDIUM"
                        
                        chapter = ChapterFind(
                            page=page_num,
                            title=match.group(0),
                            type=chapter_type,
                            preview=preview,
                            confidence=confidence
                        )
                        found_chapters.append(chapter)
                        
            except:
                continue
        
        # Show results
        if found_chapters:
            print(f"🎯 Found {len(found_chapters)} potential chapters:")
            print()
            
            for i, ch in enumerate(found_chapters, 1):
                print(f"📖 {i}. Page {ch.page}: '{ch.title}'")
                print(f"    Type: {ch.type}")
                print(f"    Confidence: {ch.confidence}")
                print(f"    Preview: {ch.preview[:100]}...")
                print()
        else:
            print("❌ No clear chapter patterns found in sampled pages")
            print("💡 Try scanning more pages or different patterns")
            
        print("=" * 50)
        print("💡 Next step: Run interactive chapter mapper to validate these findings")
        print("Command: python scripts/phase1_chapter_mapper.py [document] --batch-size 10")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())