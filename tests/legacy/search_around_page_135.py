#!/usr/bin/env python3
"""
Search around page 135 for INFORME DIARIO title
"""

import sqlite3

def search_around_page_135():
    conn = sqlite3.connect("dark_data.db")
    conn.row_factory = sqlite3.Row
    
    print("🔍 BUSCANDO ALREDEDOR DE PÁGINA 135")
    print("=" * 50)
    print("Buscando páginas 133, 134, 135, 136, 137 para encontrar:")
    print("INFORME DIARIO")
    print("Miércoles 26 de Febrero del 2025")
    
    # Search pages around 135
    target_pages = ['133', '134', '135', '136', '137']
    
    for page in target_pages:
        print(f"\n📄 PÁGINA {page}:")
        print("─" * 30)
        
        cursor = conn.execute("""
            SELECT id, page_range, content, content_length
            FROM document_chunks 
            WHERE page_range LIKE ?
            ORDER BY id
        """, (f'%{page}%',))
        
        chunks = cursor.fetchall()
        
        for chunk in chunks:
            # Check if this chunk has accessible content
            content = chunk['content']
            
            if content and not content.startswith('[') and 'characters]' not in content:
                print(f"   📋 Chunk #{chunk['id']} - CONTENIDO ACCESIBLE")
                
                lines = content.split('\n')
                
                # Look specifically for title patterns
                found_title = False
                for i, line in enumerate(lines):
                    line_clean = line.strip()
                    
                    # Look for INFORME DIARIO pattern
                    if 'informe diario' in line_clean.lower():
                        print(f"   🎯 INFORME DIARIO encontrado en línea {i+1}:")
                        print(f"      \"{line_clean}\"")
                        found_title = True
                        
                        # Show next few lines for date
                        for j in range(i+1, min(i+4, len(lines))):
                            next_line = lines[j].strip()
                            if next_line and not next_line.startswith('['):
                                print(f"      Línea {j+1}: \"{next_line}\"")
                                
                                # Check if this is the date line
                                if any(word in next_line.lower() for word in ['miércoles', '26', 'febrero']):
                                    print(f"      🎯 ¡FECHA ENCONTRADA!")
                        break
                
                # If no title found, show first few lines anyway
                if not found_title:
                    print(f"   📝 Primeras líneas:")
                    for i, line in enumerate(lines[:5], 1):
                        line_clean = line.strip()
                        if line_clean and not line_clean.startswith('['):
                            # Highlight if contains key words
                            marker = "🎯 " if any(word in line_clean.lower() for word in ['informe', 'diario', 'miércoles', '26', 'febrero']) else "   "
                            print(f"   {marker}{i}: {line_clean}")
            else:
                # Placeholder content
                print(f"   📋 Chunk #{chunk['id']} - Contenido placeholder: {content}")
    
    # Also search for the specific date pattern more broadly
    print(f"\n🔍 BÚSQUEDA AMPLIA DE 'Miércoles 26':")
    print("=" * 40)
    
    cursor = conn.execute("""
        SELECT id, page_range, content
        FROM document_chunks 
        WHERE content LIKE '%Miércoles 26%'
           OR content LIKE '%miércoles 26%'
           OR content LIKE '%MIÉRCOLES 26%'
        ORDER BY id
    """)
    
    results = cursor.fetchall()
    
    if results:
        print(f"📋 {len(results)} chunks encontrados con 'Miércoles 26'")
        
        for chunk in results:
            print(f"\n📋 Chunk #{chunk['id']} (Página {chunk['page_range']})")
            
            if chunk['content'] and not chunk['content'].startswith('['):
                lines = chunk['content'].split('\n')
                
                for i, line in enumerate(lines, 1):
                    line_clean = line.strip()
                    if 'miércoles 26' in line_clean.lower():
                        print(f"   🎯 Línea {i}: \"{line_clean}\"")
                        
                        # Show surrounding lines
                        start = max(0, i-2)
                        end = min(len(lines), i+2)
                        print(f"   📝 Contexto:")
                        for j in range(start, end):
                            ctx_line = lines[j].strip()
                            if ctx_line:
                                marker = "    >>> " if j == i-1 else "        "
                                print(f"   {marker}{ctx_line}")
                        break
            else:
                print(f"   ⚠️  Contenido placeholder: {chunk['content']}")
    else:
        print("❌ No se encontró 'Miércoles 26' en contenido accesible")
    
    conn.close()

if __name__ == "__main__":
    search_around_page_135()