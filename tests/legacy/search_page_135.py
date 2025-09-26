#!/usr/bin/env python3
"""
Search specifically for page 135 with INFORME DIARIO title
"""

import sqlite3
from pathlib import Path

def search_page_135():
    conn = sqlite3.connect(str(Path(__file__).parent.parent.parent / "platform_data" / "database" / "dark_data.db"))
    conn.row_factory = sqlite3.Row
    
    print("🔍 BUSCANDO ESPECÍFICAMENTE PÁGINA 135")
    print("=" * 50)
    print("Título esperado:")
    print("INFORME DIARIO")
    print("Miércoles 26 de Febrero del 2025")
    
    # Search for chunks containing page 135
    cursor = conn.execute("""
        SELECT id, page_range, content, content_length
        FROM document_chunks 
        WHERE page_range LIKE '%135%' 
           OR content LIKE '%Page 135%'
        ORDER BY id
    """)
    
    page_135_chunks = cursor.fetchall()
    
    print(f"\n📄 Chunks que contienen página 135: {len(page_135_chunks)}")
    
    for chunk in page_135_chunks:
        print(f"\n📋 Chunk #{chunk['id']}")
        print(f"   📏 Páginas: {chunk['page_range']}")
        print(f"   📐 Tamaño: {chunk['content_length']} caracteres")
        
        content = chunk['content']
        if content:
            if content.strip().startswith('[') and 'characters]' in content:
                print(f"   ⚠️  Contenido placeholder: {content}")
                print(f"   💡 Este chunk tiene el problema de contenido no accesible")
            else:
                print(f"   📝 CONTENIDO REAL:")
                lines = content.split('\n')
                
                for i, line in enumerate(lines[:20], 1):  # First 20 lines
                    line_clean = line.strip()
                    if line_clean:
                        # Highlight lines with INFORME DIARIO or dates
                        if ('informe diario' in line_clean.lower() or 
                            'miércoles' in line_clean.lower() or
                            '26 de febrero' in line_clean.lower()):
                            print(f"   🎯 {i:2d}: {line_clean}")
                        elif not line_clean.startswith('['):
                            print(f"      {i:2d}: {line_clean}")
        else:
            print(f"   ❌ Sin contenido")
    
    # Also search more broadly for the exact patterns
    print(f"\n🔍 BÚSQUEDA AMPLIA DE PATRONES ESPECÍFICOS:")
    
    patterns = [
        'INFORME DIARIO',
        'Miércoles 26 de Febrero',
        'Miércoles 26',
        '26 de Febrero del 2025'
    ]
    
    for pattern in patterns:
        cursor = conn.execute("""
            SELECT id, page_range, content
            FROM document_chunks 
            WHERE content LIKE ?
            ORDER BY id
            LIMIT 5
        """, (f'%{pattern}%',))
        
        results = cursor.fetchall()
        
        if results:
            print(f"\n📋 Patrón '{pattern}': {len(results)} coincidencias")
            
            for chunk in results:
                if chunk['content'] and not chunk['content'].startswith('['):
                    lines = chunk['content'].split('\n')
                    for line in lines:
                        if pattern.lower() in line.lower():
                            print(f"   Chunk #{chunk['id']} (Página {chunk['page_range']}): \"{line.strip()}\"")
                            break
        else:
            print(f"\n❌ Patrón '{pattern}': No encontrado")
    
    conn.close()

def try_direct_sql_access():
    """Try direct SQL access to get raw content"""
    
    conn = sqlite3.connect(str(Path(__file__).parent.parent.parent / "platform_data" / "database" / "dark_data.db"))
    
    print(f"\n🔧 ACCESO SQL DIRECTO A PÁGINA 135:")
    print("=" * 40)
    
    cursor = conn.execute("""
        SELECT id, page_range, LENGTH(content) as content_length, 
               SUBSTR(content, 1, 500) as content_start
        FROM document_chunks 
        WHERE page_range = '135-135'
        ORDER BY id
        LIMIT 2
    """)
    
    results = cursor.fetchall()
    
    for chunk_id, page_range, length, content_start in results:
        print(f"\n📋 Chunk #{chunk_id} (Página {page_range})")
        print(f"📐 Longitud real: {length} caracteres")
        print(f"📝 Inicio del contenido:")
        print(f"─" * 50)
        if content_start:
            print(content_start)
        else:
            print("❌ Sin contenido")
        print(f"─" * 50)
    
    conn.close()

if __name__ == "__main__":
    search_page_135()
    try_direct_sql_access()