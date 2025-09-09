#!/usr/bin/env python3
"""
Search for ANEXO 3 and 4 specifically
"""

import sqlite3

def search_anexos_3_4():
    conn = sqlite3.connect("dark_data.db")
    conn.row_factory = sqlite3.Row
    
    print("🔍 BUSCANDO ANEXOS 3 Y 4")
    print("=" * 50)
    
    # Check if they were detected
    for anexo_num in ['3', '4']:
        print(f"\n📋 ANEXO {anexo_num}:")
        
        cursor = conn.execute("""
            SELECT id, specific_annex_number, specific_annex_title, annex_theme, page_range
            FROM document_chunks 
            WHERE specific_annex_number = ?
        """, (anexo_num,))
        
        results = cursor.fetchall()
        
        if results:
            print(f"   ✅ Detectado - {len(results)} chunk(s)")
            for chunk in results:
                print(f"      Chunk #{chunk['id']} - \"{chunk['specific_annex_title']}\"")
                print(f"      Tema: {chunk['annex_theme']} | Página: {chunk['page_range']}")
        else:
            print(f"   ❌ No detectado")
            
            # Search for potential content
            cursor = conn.execute("""
                SELECT id, page_range, content
                FROM document_chunks 
                WHERE content LIKE ? OR content LIKE ? OR content LIKE ?
                ORDER BY id
                LIMIT 3
            """, (f'%ANEXO {anexo_num}%', f'%Anexo {anexo_num}%', f'%ANEXO N°{anexo_num}%'))
            
            potential = cursor.fetchall()
            if potential:
                print(f"   🔍 Posibles menciones:")
                for chunk in potential:
                    # Look for the specific line
                    lines = chunk['content'].split('\n')
                    for line in lines:
                        if f'anexo {anexo_num}' in line.lower() or f'anexo n°{anexo_num}' in line.lower():
                            line_clean = line.strip()
                            print(f"      Chunk #{chunk['id']} (Página {chunk['page_range']}): \"{line_clean}\"")
                            break
    
    # Search for formal titles in index
    print(f"\n🔍 BUSCANDO TÍTULOS FORMALES EN ÍNDICE:")
    cursor = conn.execute("""
        SELECT id, page_range, content
        FROM document_chunks 
        WHERE content LIKE '%Anexo N°3%' OR content LIKE '%Anexo N°4%'
           OR content LIKE '%ANEXO N°3%' OR content LIKE '%ANEXO N°4%'
        ORDER BY id
    """)
    
    index_chunks = cursor.fetchall()
    
    for chunk in index_chunks:
        lines = chunk['content'].split('\n')
        print(f"\n📄 Chunk #{chunk['id']} (Página {chunk['page_range']}):")
        
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if ('anexo n°3' in line_clean.lower() or 'anexo n°4' in line_clean.lower() or
                'anexo 3' in line_clean.lower() or 'anexo 4' in line_clean.lower()):
                print(f"   📝 Línea {i+1}: \"{line_clean}\"")
    
    conn.close()

if __name__ == "__main__":
    search_anexos_3_4()