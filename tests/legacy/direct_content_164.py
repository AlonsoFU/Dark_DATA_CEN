#!/usr/bin/env python3
"""
Direct access to page 164 content
"""

import sqlite3

def direct_content_164():
    conn = sqlite3.connect("dark_data.db")
    
    print("📄 ACCESO DIRECTO A CONTENIDO PÁGINA 164")
    print("=" * 60)
    
    cursor = conn.execute("""
        SELECT id, page_range, SUBSTR(content, 1, 2000) as content_preview
        FROM document_chunks 
        WHERE page_range LIKE '%164%'
        ORDER BY id
    """)
    
    chunks = cursor.fetchall()
    
    for chunk_id, page_range, content_preview in chunks:
        print(f"\n📋 Chunk #{chunk_id} (Páginas: {page_range})")
        print("─" * 50)
        
        if content_preview:
            lines = content_preview.split('\n')
            for i, line in enumerate(lines[:20], 1):  # First 20 lines
                line_clean = line.strip()
                if line_clean:
                    # Look for ANEXO patterns
                    if 'anexo' in line_clean.lower():
                        print(f"🎯 {i:2d}: {line_clean}")
                    else:
                        print(f"   {i:2d}: {line_clean}")
        else:
            print("   ❌ Sin contenido")
    
    # Also search for any chunk that might contain "mantenimiento" since that was missing from index
    print(f"\n🔍 BUSCANDO POSIBLE ANEXO 4 POR CONTENIDO:")
    cursor = conn.execute("""
        SELECT id, page_range, SUBSTR(content, 1, 500) as preview
        FROM document_chunks 
        WHERE content LIKE '%mantenimiento%' 
           OR content LIKE '%programado%'
           OR content LIKE '%forzado%'
        ORDER BY id
        LIMIT 5
    """)
    
    maintenance_chunks = cursor.fetchall()
    
    if maintenance_chunks:
        print(f"📋 Chunks con 'mantenimiento': {len(maintenance_chunks)}")
        for chunk_id, page_range, preview in maintenance_chunks:
            # Look for the line with mantenimiento
            lines = preview.split('\n')
            for line in lines:
                if 'mantenimiento' in line.lower():
                    print(f"   Chunk #{chunk_id} (Página {page_range}): \"{line.strip()}\"")
                    break
    
    conn.close()

if __name__ == "__main__":
    direct_content_164()