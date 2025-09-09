#!/usr/bin/env python3
"""
Manually add ANEXO 5 with the correct title provided by user
"""

import sqlite3

def manually_add_anexo_5():
    conn = sqlite3.connect("dark_data.db")
    
    print("🔧 AGREGANDO MANUALMENTE ANEXO 5")
    print("=" * 50)
    
    # The correct title as provided by user
    correct_title = "Informe de trabajo y falla de instalaciones ingresados en el sistema del Coordinador Eléctrico Nacional por las empresas coordinadas"
    
    print(f"📝 Título correcto: \"{correct_title}\"")
    
    # Find the index chunk that mentions ANEXO 5
    cursor = conn.execute("""
        SELECT id, page_range, content
        FROM document_chunks 
        WHERE content LIKE '%Anexo N°5%'
        ORDER BY id
        LIMIT 1
    """)
    
    index_chunk = cursor.fetchone()
    
    if index_chunk:
        chunk_id, page_range, content = index_chunk
        
        print(f"📋 Usando chunk del índice #{chunk_id} como base")
        
        # Update this chunk to be ANEXO 5
        cursor = conn.execute("""
            UPDATE document_chunks 
            SET specific_annex_number = '5',
                specific_annex_title = ?,
                annex_theme = 'technical_analysis',
                is_annex_header = 1
            WHERE id = ?
        """, (correct_title, chunk_id))
        
        rows_affected = cursor.rowcount
        conn.commit()
        
        if rows_affected > 0:
            print(f"✅ ANEXO 5 agregado exitosamente")
            print(f"   📋 Chunk #{chunk_id}")
            print(f"   📝 Título: \"{correct_title}\"")
            print(f"   🏷️  Tema: technical_analysis")
        else:
            print(f"❌ No se pudo agregar ANEXO 5")
    else:
        print(f"❌ No se encontró chunk con referencia a ANEXO 5")
    
    # Verify the addition
    cursor = conn.execute("""
        SELECT specific_annex_number, specific_annex_title, annex_theme
        FROM document_chunks 
        WHERE specific_annex_number = '5'
    """)
    
    verification = cursor.fetchone()
    if verification:
        print(f"\n✅ VERIFICACIÓN:")
        print(f"   ANEXO {verification[0]}: \"{verification[1]}\"")
        print(f"   Tema: {verification[2]}")
    
    conn.close()

def show_all_annexes_now():
    """Show all annexes after adding ANEXO 5"""
    
    conn = sqlite3.connect("dark_data.db")
    conn.row_factory = sqlite3.Row
    
    print(f"\n📊 TODOS LOS ANEXOS DESPUÉS DE AGREGAR EL 5")
    print("=" * 60)
    
    cursor = conn.execute("""
        SELECT specific_annex_number, specific_annex_title, annex_theme, COUNT(*) as chunk_count
        FROM document_chunks 
        WHERE specific_annex_number IS NOT NULL
        GROUP BY specific_annex_number, specific_annex_title, annex_theme
        ORDER BY CAST(specific_annex_number AS INTEGER)
    """)
    
    all_annexes = cursor.fetchall()
    
    print(f"🔢 TOTAL ANEXOS DETECTADOS: {len(all_annexes)}")
    
    for i, annex in enumerate(all_annexes, 1):
        print(f"\n{i}. 📋 ANEXO {annex['specific_annex_number']}")
        print(f"   📝 \"{annex['specific_annex_title']}\"")
        print(f"   🏷️  {annex['annex_theme']}")
        print(f"   📊 {annex['chunk_count']} chunk(s)")
    
    # Show which ones are still missing from 1-8
    detected_numbers = {annex['specific_annex_number'] for annex in all_annexes}
    expected_numbers = {'1', '2', '3', '4', '5', '6', '7', '8'}
    missing_numbers = expected_numbers - detected_numbers
    
    if missing_numbers:
        print(f"\n❌ ANEXOS FALTANTES: {sorted(missing_numbers)}")
    else:
        print(f"\n✅ TODOS LOS ANEXOS 1-8 DETECTADOS")
    
    conn.close()

if __name__ == "__main__":
    manually_add_anexo_5()
    show_all_annexes_now()