#!/usr/bin/env python3
"""
Direct SQL query to see page 164 content
"""

import sqlite3

def sql_direct_164():
    conn = sqlite3.connect("dark_data.db")
    
    print("🔍 CONSULTA SQL DIRECTA PÁGINA 164")
    print("=" * 50)
    
    # Get the actual content
    cursor = conn.execute("""
        SELECT id, page_range, LENGTH(content) as content_length,
               content
        FROM document_chunks 
        WHERE page_range LIKE '%164%'
        ORDER BY id
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    
    if result:
        chunk_id, page_range, length, content = result
        print(f"📋 Chunk #{chunk_id}")
        print(f"📏 Páginas: {page_range}")
        print(f"📐 Longitud real: {length} caracteres")
        
        if content:
            print(f"\n📝 PRIMERAS 1000 CARACTERES:")
            print("─" * 50)
            print(content[:1000])
            print("─" * 50)
            
            # Look for ANEXO in the content
            if 'ANEXO' in content.upper():
                print("✅ Contiene 'ANEXO'")
                # Find all ANEXO occurrences
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'anexo' in line.lower():
                        print(f"🎯 Línea {i+1}: {line.strip()}")
            else:
                print("❌ No contiene 'ANEXO'")
                
                # Check what type of content this is
                if 'mantenim' in content.lower():
                    print("💡 Contiene 'mantenimiento' - podría ser contenido del ANEXO 4")
                elif 'programado' in content.lower():
                    print("💡 Contiene 'programado' - podría ser contenido de mantenimientos")
        else:
            print("❌ Contenido vacío")
    else:
        print("❌ No se encontró chunk para página 164")
    
    # Let's also search the complete index chunk to see if ANEXO 4 was missed
    print(f"\n🔍 REVISANDO ÍNDICE COMPLETO PARA ANEXO 4:")
    cursor = conn.execute("""
        SELECT content
        FROM document_chunks 
        WHERE content LIKE '%Anexo N°1%' AND content LIKE '%Anexo N°2%'
        LIMIT 1
    """)
    
    index_result = cursor.fetchone()
    if index_result:
        index_content = index_result[0]
        lines = index_content.split('\n')
        
        print("📋 Líneas del índice:")
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if line_clean and ('anexo' in line_clean.lower() or 'mantenimiento' in line_clean.lower()):
                print(f"   {i+1:2d}: {line_clean}")
    
    conn.close()

if __name__ == "__main__":
    sql_direct_164()