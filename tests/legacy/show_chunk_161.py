#!/usr/bin/env python3
"""
Show complete content of chunk #161 from page 164
"""

import sqlite3
from pathlib import Path

def show_chunk_161():
    conn = sqlite3.connect(str(Path(__file__).parent.parent.parent / "platform_data" / "database" / "dark_data.db"))
    conn.row_factory = sqlite3.Row
    
    print("📄 CONTENIDO COMPLETO DEL CHUNK #161 (PÁGINA 164)")
    print("=" * 70)
    
    cursor = conn.execute("""
        SELECT id, page_range, content, chunk_type, content_length
        FROM document_chunks 
        WHERE id = 161
    """)
    
    chunk = cursor.fetchone()
    if chunk:
        print(f"📋 Chunk #{chunk['id']}")
        print(f"   📏 Páginas: {chunk['page_range']}")
        print(f"   📊 Tipo: {chunk['chunk_type']}")
        print(f"   📐 Tamaño: {chunk['content_length']} caracteres")
        
        content = chunk['content']
        lines = content.split('\n')
        
        print(f"\n📝 CONTENIDO LÍNEA POR LÍNEA:")
        print("─" * 70)
        
        anexo_found = False
        for i, line in enumerate(lines, 1):
            line_clean = line.strip()
            if line_clean:  # Only show non-empty lines
                # Highlight lines that might contain ANEXO
                marker = "🎯 " if 'anexo' in line_clean.lower() else "   "
                print(f"{marker}{i:3d}: {line_clean}")
                
                if 'anexo' in line_clean.lower():
                    anexo_found = True
        
        print("─" * 70)
        
        if anexo_found:
            print("✅ Contenido con 'ANEXO' encontrado")
        else:
            print("❌ No se encontró 'ANEXO' en este chunk")
            print("💡 Esto podría ser contenido del anexo, no el título")
    
    # Also check nearby chunks
    print(f"\n🔍 REVISANDO CHUNKS CERCANOS:")
    cursor = conn.execute("""
        SELECT id, page_range, content
        FROM document_chunks 
        WHERE id BETWEEN 158 AND 165
        ORDER BY id
    """)
    
    nearby_chunks = cursor.fetchall()
    for chunk in nearby_chunks:
        has_anexo = 'anexo' in (chunk['content'] or '').lower()
        marker = "🎯" if has_anexo else "  "
        content_preview = (chunk['content'] or '')[:100].replace('\n', ' ')
        print(f"{marker} Chunk #{chunk['id']} (Página {chunk['page_range']}): \"{content_preview}...\"")
    
    conn.close()

if __name__ == "__main__":
    show_chunk_161()