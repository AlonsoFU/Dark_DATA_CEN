#!/usr/bin/env python3
"""
Find formal annex titles in the document
"""

import sqlite3
import re

def find_formal_titles():
    conn = sqlite3.connect("dark_data.db")
    conn.row_factory = sqlite3.Row
    
    print("🔍 BUSCANDO TÍTULOS FORMALES DE ANEXOS")
    print("=" * 50)
    
    # Search for formal titles like "ANEXO Nº2"
    cursor = conn.execute("""
        SELECT id, page_range, content
        FROM document_chunks 
        WHERE content LIKE '%ANEXO N%2%' 
           OR content LIKE '%Detalle de la generación real%'
           OR content LIKE '%generación real para los días%'
        ORDER BY id
    """)
    
    results = cursor.fetchall()
    
    print(f"📋 Chunks con posibles títulos formales: {len(results)}")
    
    for chunk in results:
        print(f"\n📄 Chunk #{chunk['id']} (Página {chunk['page_range']})")
        content = chunk['content']
        
        # Look for the exact pattern
        lines = content.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if 'ANEXO' in line and ('2' in line or 'generación real' in line):
                print(f"   📝 Línea {i+1}: \"{line}\"")
                # Show next few lines for context
                for j in range(i+1, min(i+4, len(lines))):
                    next_line = lines[j].strip()
                    if next_line:
                        print(f"   📝 Línea {j+1}: \"{next_line}\"")
                break
    
    # Also search for patterns like "Detalle de la generación real"
    print(f"\n🔍 BUSCANDO PATRÓN 'Detalle de la generación real':")
    cursor = conn.execute("""
        SELECT id, page_range, content
        FROM document_chunks 
        WHERE content LIKE '%Detalle de la generación real%'
        ORDER BY id
    """)
    
    title_chunks = cursor.fetchall()
    for chunk in title_chunks:
        content_preview = chunk['content'][:300].replace('\n', ' | ')
        print(f"   Chunk #{chunk['id']} (Página {chunk['page_range']}): \"{content_preview}...\"")
    
    conn.close()

if __name__ == "__main__":
    find_formal_titles()