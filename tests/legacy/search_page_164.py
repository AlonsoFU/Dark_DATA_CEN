#!/usr/bin/env python3
"""
Search for content in page 164 where ANEXO 4 should be
"""

import sqlite3
from pathlib import Path

def search_page_164():
    conn = sqlite3.connect(str(Path(__file__).parent.parent.parent / "platform_data" / "database" / "dark_data.db"))
    conn.row_factory = sqlite3.Row
    
    print("🔍 BUSCANDO EN PÁGINA 164 - ANEXO 4")
    print("=" * 50)
    
    # Search for chunks that contain page 164
    cursor = conn.execute("""
        SELECT id, page_range, content, chunk_type, content_length
        FROM document_chunks 
        WHERE page_range LIKE '%164%' 
           OR content LIKE '%Page 164%'
        ORDER BY id
    """)
    
    page_164_chunks = cursor.fetchall()
    
    print(f"📄 Chunks que contienen página 164: {len(page_164_chunks)}")
    
    for chunk in page_164_chunks:
        print(f"\n📋 Chunk #{chunk['id']}")
        print(f"   📏 Páginas: {chunk['page_range']}")
        print(f"   📊 Tipo: {chunk['chunk_type']}")
        print(f"   📐 Tamaño: {chunk['content_length']} caracteres")
        
        content = chunk['content']
        lines = content.split('\n')
        
        # Look for ANEXO patterns
        anexo_found = False
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if 'anexo' in line_clean.lower() and ('4' in line_clean or 'iv' in line_clean.lower()):
                print(f"   🎯 ANEXO encontrado en línea {i+1}: \"{line_clean}\"")
                
                # Show context
                start = max(0, i-2)
                end = min(len(lines), i+5)
                print(f"   📝 Contexto:")
                for j in range(start, end):
                    marker = " >>> " if j == i else "     "
                    context_line = lines[j].strip()
                    if context_line:
                        print(f"   {marker}{j+1}: {context_line}")
                
                anexo_found = True
                break
        
        if not anexo_found:
            # Show first 300 characters to see what's there
            content_preview = content.replace('\n', ' | ')[:300]
            print(f"   📝 Contenido: \"{content_preview}...\"")
    
    # Also search broadly for ANEXO 4 patterns
    print(f"\n🔍 BÚSQUEDA AMPLIA DE ANEXO 4:")
    patterns = ['%ANEXO 4%', '%Anexo 4%', '%ANEXO IV%', '%Anexo IV%', '%ANEXO N°4%']
    
    for pattern in patterns:
        cursor = conn.execute("""
            SELECT id, page_range, content
            FROM document_chunks 
            WHERE content LIKE ?
            ORDER BY id
        """, (pattern,))
        
        results = cursor.fetchall()
        if results:
            print(f"\n📋 Patrón '{pattern}': {len(results)} chunks")
            for chunk in results:
                lines = chunk['content'].split('\n')
                for line in lines:
                    if '4' in line and 'anexo' in line.lower():
                        print(f"   Chunk #{chunk['id']} (Página {chunk['page_range']}): \"{line.strip()}\"")
                        break
    
    conn.close()

if __name__ == "__main__":
    search_page_164()