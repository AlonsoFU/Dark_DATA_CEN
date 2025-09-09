#!/usr/bin/env python3
"""
Check how Anexo 2 was detected and tagged
"""

import sqlite3
import json

def check_anexo_2():
    conn = sqlite3.connect("dark_data.db")
    conn.row_factory = sqlite3.Row
    
    print("🔍 VERIFICANDO DETECCIÓN DEL ANEXO 2")
    print("=" * 50)
    
    # Check if Anexo 2 was detected
    cursor = conn.execute("""
        SELECT id, specific_annex_number, specific_annex_title, annex_theme, 
               is_annex_header, page_range, content
        FROM document_chunks 
        WHERE specific_annex_number = '2'
        ORDER BY id
    """)
    
    anexo_2_chunks = cursor.fetchall()
    
    if not anexo_2_chunks:
        print("❌ No se detectó el Anexo 2")
        
        # Let's search for potential Anexo 2 content
        print("\n🔍 Buscando contenido que podría ser Anexo 2...")
        cursor = conn.execute("""
            SELECT id, page_range, content
            FROM document_chunks 
            WHERE content LIKE '%ANEXO 2%' OR content LIKE '%Anexo 2%'
            ORDER BY id
            LIMIT 5
        """)
        
        potential_chunks = cursor.fetchall()
        for chunk in potential_chunks:
            content_preview = chunk['content'][:200].replace('\n', ' ').strip()
            print(f"   Chunk #{chunk['id']} (Página {chunk['page_range']}): \"{content_preview}...\"")
    else:
        print(f"✅ ANEXO 2 DETECTADO - {len(anexo_2_chunks)} chunks")
        
        for chunk in anexo_2_chunks:
            print(f"\n📋 Chunk #{chunk['id']}")
            print(f"   📝 Título: \"{chunk['specific_annex_title']}\"")
            print(f"   🏷️  Tema: {chunk['annex_theme']}")
            print(f"   📄 Es cabecera: {'Sí' if chunk['is_annex_header'] else 'No'}")
            print(f"   📍 Página: {chunk['page_range']}")
            
            if chunk['is_annex_header']:
                content_preview = chunk['content'][:300].replace('\n', ' ').strip()
                print(f"   📝 Contenido cabecera: \"{content_preview}...\"")
    
    # Also check what other numbered annexes were detected
    print(f"\n📊 OTROS ANEXOS NUMERADOS DETECTADOS:")
    cursor = conn.execute("""
        SELECT specific_annex_number, specific_annex_title, annex_theme, COUNT(*) as chunk_count
        FROM document_chunks 
        WHERE specific_annex_number REGEXP '^[0-9]+$'
        GROUP BY specific_annex_number, specific_annex_title, annex_theme
        ORDER BY CAST(specific_annex_number AS INTEGER)
    """)
    
    numbered_annexes = cursor.fetchall()
    for annex in numbered_annexes:
        print(f"   ANEXO {annex['specific_annex_number']}: \"{annex['specific_annex_title'][:60]}...\" ({annex['annex_theme']})")
    
    conn.close()

if __name__ == "__main__":
    check_anexo_2()