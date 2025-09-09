#!/usr/bin/env python3
"""
Get the complete title of ANEXO 3 from the index
"""

import sqlite3

def get_anexo_3_title():
    conn = sqlite3.connect("dark_data.db")
    conn.row_factory = sqlite3.Row
    
    print("🔍 OBTENIENDO TÍTULO COMPLETO DEL ANEXO 3")
    print("=" * 60)
    
    # Get the chunk with ANEXO 3 reference
    cursor = conn.execute("""
        SELECT id, page_range, content
        FROM document_chunks 
        WHERE content LIKE '%Anexo N°3%'
        ORDER BY id
        LIMIT 1
    """)
    
    chunk = cursor.fetchone()
    if chunk:
        print(f"📄 Chunk #{chunk['id']} (Página {chunk['page_range']})")
        
        lines = chunk['content'].split('\n')
        
        # Find the line with ANEXO 3 and show context
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if 'anexo n°3' in line_clean.lower():
                print(f"\n🎯 ANEXO 3 encontrado en línea {i+1}:")
                
                # Show previous lines for complete title
                start = max(0, i-3)
                end = min(len(lines), i+2)
                
                complete_title = ""
                for j in range(start, end):
                    context_line = lines[j].strip()
                    marker = " >>> " if j == i else "     "
                    print(f"   {marker}{j+1}: {context_line}")
                    
                    # Build complete title from previous line
                    if j == i-1 and context_line:
                        complete_title = context_line
                
                if complete_title:
                    print(f"\n📝 TÍTULO COMPLETO DEL ANEXO 3:")
                    print(f"   \"{complete_title}\"")
                    
                    # Check if this looks like a title
                    if any(word in complete_title.lower() for word in ['detalle', 'movimiento', 'centrales', 'cdc']):
                        print(f"   ✅ Parece ser el título formal")
                        return complete_title
                    else:
                        print(f"   ❓ No parece un título formal")
                
                break
        
        # Also search for ANEXO 4 patterns
        print(f"\n🔍 BUSCANDO TAMBIÉN ANEXO 4 EN EL MISMO CHUNK:")
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if 'anexo' in line_clean.lower() and '4' in line_clean:
                print(f"   📝 Línea {i+1}: \"{line_clean}\"")
    
    conn.close()
    return None

if __name__ == "__main__":
    title = get_anexo_3_title()