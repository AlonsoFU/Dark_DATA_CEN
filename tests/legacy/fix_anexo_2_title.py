#!/usr/bin/env python3
"""
Fix ANEXO 2 title specifically based on found formal title
"""

import sqlite3
from pathlib import Path

def fix_anexo_2_title():
    conn = sqlite3.connect(str(Path(__file__).parent.parent.parent / "platform_data" / "database" / "dark_data.db"))
    
    print("🔧 CORRIGIENDO TÍTULO DEL ANEXO 2")
    print("=" * 50)
    
    # The correct title found in chunk #592
    correct_title = "Detalle de la generación real de los días 25 y 26 de febrero de 2025"
    
    # Update ANEXO 2 with correct title
    cursor = conn.execute("""
        UPDATE document_chunks 
        SET specific_annex_title = ?
        WHERE specific_annex_number = '2'
    """, (correct_title,))
    
    rows_updated = cursor.rowcount
    
    print(f"✅ Actualizado {rows_updated} chunk(s) del ANEXO 2")
    print(f"📝 Nuevo título: \"{correct_title}\"")
    
    conn.commit()
    
    # Verify the update
    cursor = conn.execute("""
        SELECT id, specific_annex_number, specific_annex_title, annex_theme, page_range
        FROM document_chunks 
        WHERE specific_annex_number = '2'
    """)
    
    anexo_2_chunks = cursor.fetchall()
    
    print(f"\n✅ VERIFICACIÓN:")
    for chunk in anexo_2_chunks:
        print(f"   Chunk #{chunk[0]} - ANEXO {chunk[1]}")
        print(f"   📝 Título: \"{chunk[2]}\"")
        print(f"   🏷️  Tema: {chunk[3]}")
        print(f"   📄 Página: {chunk[4]}")
    
    conn.close()

def also_fix_other_annexes():
    """Fix other annexes with their formal titles"""
    
    conn = sqlite3.connect(str(Path(__file__).parent.parent.parent / "platform_data" / "database" / "dark_data.db"))
    
    print(f"\n🔧 CORRIGIENDO OTROS ANEXOS CON TÍTULOS FORMALES")
    print("=" * 60)
    
    # Based on the search results, these are the formal titles:
    formal_titles = {
        '1': "Detalle de la generación programada para los días 25 y 26 de febrero de 2025",
        '3': "Detalle del Movimiento de Centrales e Informe Diario del CDC correspondientes a los días 25 y 26 de febrero de 2025"
    }
    
    for annexo_num, title in formal_titles.items():
        cursor = conn.execute("""
            UPDATE document_chunks 
            SET specific_annex_title = ?
            WHERE specific_annex_number = ?
        """, (title, annexo_num))
        
        rows_updated = cursor.rowcount
        if rows_updated > 0:
            print(f"✅ ANEXO {annexo_num}: Actualizado {rows_updated} chunk(s)")
            print(f"   📝 \"{title}\"")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    fix_anexo_2_title()
    also_fix_other_annexes()