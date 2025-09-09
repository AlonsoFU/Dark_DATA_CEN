#!/usr/bin/env python3
"""
Add ANEXO 4 with correct title to database
"""

import sqlite3

def add_anexo_4():
    conn = sqlite3.connect("dark_data.db")
    
    print("🔧 AGREGANDO ANEXO 4 A LA BASE DE DATOS")
    print("=" * 50)
    
    # Complete title for ANEXO 4
    anexo_4_title = "Detalle de los mantenimientos programados y forzados para los días 25 y 26 de febrero de 2025"
    
    print(f"📝 Título ANEXO 4: \"{anexo_4_title}\"")
    
    # Search for content that might belong to ANEXO 4
    cursor = conn.execute("""
        SELECT id, page_range, content
        FROM document_chunks 
        WHERE (page_range LIKE '%164%' AND LENGTH(content) > 100)
           OR content LIKE '%mantenimiento%programado%'
           OR content LIKE '%mantenimiento%forzado%'
        ORDER BY 
            CASE WHEN page_range LIKE '%164%' THEN 1 ELSE 2 END,
            id
        LIMIT 3
    """)
    
    potential_chunks = cursor.fetchall()
    
    print(f"\n🔍 Chunks potenciales para ANEXO 4: {len(potential_chunks)}")
    
    if potential_chunks:
        # Use the first chunk (page 164) as the header
        header_chunk = potential_chunks[0]
        chunk_id, page_range, content = header_chunk
        
        print(f"📋 Seleccionando Chunk #{chunk_id} (Página {page_range}) como cabecera")
        
        # Update this chunk as ANEXO 4 header
        conn.execute("""
            UPDATE document_chunks 
            SET specific_annex_number = '4',
                specific_annex_title = ?,
                annex_theme = 'equipment_details',
                is_annex_header = 1
            WHERE id = ?
        """, (anexo_4_title, chunk_id))
        
        print(f"✅ ANEXO 4 agregado:")
        print(f"   📋 Chunk #{chunk_id}")
        print(f"   📝 Título: \"{anexo_4_title}\"")
        print(f"   🏷️  Tema: equipment_details")
        print(f"   📄 Página: {page_range}")
        
        conn.commit()
        
        # Verify the addition
        cursor = conn.execute("""
            SELECT specific_annex_number, specific_annex_title, annex_theme, page_range
            FROM document_chunks 
            WHERE specific_annex_number = '4'
        """)
        
        verification = cursor.fetchone()
        if verification:
            print(f"\n✅ VERIFICACIÓN EXITOSA:")
            print(f"   ANEXO {verification[0]}: \"{verification[1]}\"")
            print(f"   Tema: {verification[2]} | Página: {verification[3]}")
        else:
            print(f"\n❌ Error en verificación")
    else:
        print(f"❌ No se encontraron chunks potenciales para ANEXO 4")
    
    conn.close()

def show_updated_annexes():
    """Show all detected annexes after update"""
    
    conn = sqlite3.connect("dark_data.db")
    
    print(f"\n📊 TODOS LOS ANEXOS DETECTADOS ACTUALIZADOS:")
    print("=" * 60)
    
    cursor = conn.execute("""
        SELECT specific_annex_number, specific_annex_title, annex_theme, COUNT(*) as chunk_count
        FROM document_chunks 
        WHERE specific_annex_number IS NOT NULL
        GROUP BY specific_annex_number, specific_annex_title, annex_theme
        ORDER BY CAST(specific_annex_number AS INTEGER)
    """)
    
    annexes = cursor.fetchall()
    
    for annex in annexes:
        print(f"\n📋 ANEXO {annex[0]}")
        print(f"   📝 \"{annex[1]}\"")
        print(f"   🏷️  {annex[2]}")
        print(f"   📊 {annex[3]} chunk(s)")
    
    conn.close()

if __name__ == "__main__":
    add_anexo_4()
    show_updated_annexes()