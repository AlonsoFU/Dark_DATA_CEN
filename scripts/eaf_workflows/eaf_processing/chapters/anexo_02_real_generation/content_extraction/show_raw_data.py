#!/usr/bin/env python3
"""
Show raw text data from ANEXO 2 pages to understand patterns
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.append(str(project_root))

from extract_anexo2_real_generation import extract_page_text, extract_ocr_text, find_pdf_file

def show_raw_data(page_num):
    """Show raw text data for a specific page"""
    pdf_path = find_pdf_file()
    if not pdf_path:
        print("❌ PDF file not found!")
        return
    
    print(f"🔍 RAW DATA ANALYSIS - ANEXO 2 Page {page_num}")
    print("=" * 60)
    
    # Get raw text
    raw_text = extract_page_text(pdf_path, page_num)
    ocr_text = extract_ocr_text(pdf_path, page_num)
    
    print(f"📄 RAW TEXT (PyPDF2) - Length: {len(raw_text)} chars")
    print("-" * 40)
    print(raw_text[:1500] + "\n[... truncated ...]" if len(raw_text) > 1500 else raw_text)
    
    print(f"\n🔍 OCR TEXT (Tesseract) - Length: {len(ocr_text)} chars")
    print("-" * 40)
    print(ocr_text[:1500] + "\n[... truncated ...]" if len(ocr_text) > 1500 else ocr_text)
    
    # Show combined text with line numbers
    print(f"\n📋 COMBINED TEXT (Line by Line Analysis)")
    print("-" * 40)
    combined_text = raw_text + "\n" + ocr_text
    lines = combined_text.split('\n')
    
    for i, line in enumerate(lines[:100]):  # Show first 100 lines
        if line.strip():
            print(f"[{i:3d}] {line}")
    
    if len(lines) > 100:
        print(f"\n[... {len(lines) - 100} more lines ...]")

if __name__ == "__main__":
    page_num = int(sys.argv[1]) if len(sys.argv) > 1 else 70
    show_raw_data(page_num)