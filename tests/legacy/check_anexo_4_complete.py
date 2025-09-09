#!/usr/bin/env python3
"""
Check complete ANEXO 4 details and all detected annexes
"""

import sqlite3

def check_anexo_4_complete():
    conn = sqlite3.connect("dark_data.db")
    conn.row_factory = sqlite3.Row
    
    print("🔍 DETALLES COMPLETOS DEL ANEXO 4")
    print("=" * 60)
    
    # Get ANEXO 4 details
    cursor = conn.execute("""
        SELECT id, specific_annex_number, specific_annex_title, annex_theme, 
               is_annex_header, page_range, content
        FROM document_chunks 
        WHERE specific_annex_number = '4'
    """)
    
    anexo_4_chunks = cursor.fetchall()
    
    if anexo_4_chunks:
        for chunk in anexo_4_chunks:
            print(f"📋 Chunk #{chunk['id']}")
            print(f"   📝 Número: ANEXO {chunk['specific_annex_number']}")
            print(f"   📝 Título completo: \"{chunk['specific_annex_title']}\"")
            print(f"   🏷️  Tema: {chunk['annex_theme']}")
            print(f"   📄 Es cabecera: {'Sí' if chunk['is_annex_header'] else 'No'}")
            print(f"   📍 Página: {chunk['page_range']}")
            
            if chunk['content']:
                content_preview = chunk['content'][:400].replace('\n', ' | ')
                print(f"   📝 Contenido: \"{content_preview}...\"")
    else:
        print("❌ ANEXO 4 no encontrado")
    
    print(f"\n📊 TODOS LOS TÍTULOS DE ANEXOS DETECTADOS:")
    print("=" * 60)
    
    # Get all annexes with their complete titles
    cursor = conn.execute("""
        SELECT specific_annex_number, specific_annex_title, annex_theme, 
               COUNT(*) as chunk_count, is_annex_header
        FROM document_chunks 
        WHERE specific_annex_number IS NOT NULL
        GROUP BY specific_annex_number, specific_annex_title, annex_theme, is_annex_header
        ORDER BY 
            CASE 
                WHEN specific_annex_number GLOB '[0-9]*' THEN CAST(specific_annex_number AS INTEGER)
                ELSE 999 
            END,
            specific_annex_number
    """)
    
    all_annexes = cursor.fetchall()
    
    for annex in all_annexes:
        print(f"\n📋 ANEXO {annex['specific_annex_number']}")
        print(f"   📝 Título: \"{annex['specific_annex_title']}\"")
        print(f"   🏷️  Tema: {annex['annex_theme']}")
        print(f"   📊 Chunks: {annex['chunk_count']}")
        print(f"   📄 Cabecera: {'Sí' if annex['is_annex_header'] else 'No'}")
    
    # Check if chunks are properly separated by annexes
    print(f"\n🔍 ¿ESTÁN LOS CHUNKS SEPARADOS POR ANEXOS?")
    print("=" * 50)
    
    # Check chunks around detected annexes
    annexo_numbers = ['1', '2', '3', '4', '5', '6', '7', '8']
    
    for num in annexo_numbers:
        cursor = conn.execute("""
            SELECT COUNT(*) as count
            FROM document_chunks 
            WHERE specific_annex_number = ?
        """, (num,))
        
        count = cursor.fetchone()['count']
        status = "✅ Detectado" if count > 0 else "❌ No detectado"
        print(f"   ANEXO {num}: {status} ({count} chunks)")
    
    # Show chunks without annexo assignment near detected ones
    print(f"\n🔍 CHUNKS SIN ASIGNAR CERCA DE ANEXOS:")
    cursor = conn.execute("""
        SELECT id, page_range, content
        FROM document_chunks 
        WHERE specific_annex_number IS NULL 
          AND (content LIKE '%ANEXO%' OR content LIKE '%Anexo%')
        ORDER BY id
        LIMIT 5
    """)
    
    unassigned = cursor.fetchall()
    
    for chunk in unassigned:
        lines = chunk['content'].split('\n') if chunk['content'] else []
        for line in lines:
            if 'anexo' in line.lower():
                print(f"   Chunk #{chunk['id']} (Página {chunk['page_range']}): \"{line.strip()}\"")
                break
    
    conn.close()

if __name__ == "__main__":
    check_anexo_4_complete()