#!/usr/bin/env python3
"""
Count and show all detected annexe titles
"""

import sqlite3

def count_all_titles():
    conn = sqlite3.connect("dark_data.db")
    conn.row_factory = sqlite3.Row
    
    print("📊 CONTEO COMPLETO DE TÍTULOS DETECTADOS")
    print("=" * 60)
    
    # Get all unique annex titles
    cursor = conn.execute("""
        SELECT specific_annex_number, specific_annex_title, annex_theme, 
               is_annex_header, COUNT(*) as chunk_count
        FROM document_chunks 
        WHERE specific_annex_number IS NOT NULL
        GROUP BY specific_annex_number, specific_annex_title
        ORDER BY 
            CASE 
                WHEN specific_annex_number GLOB '[0-9]*' THEN CAST(specific_annex_number AS INTEGER)
                ELSE 999 
            END,
            specific_annex_number
    """)
    
    all_titles = cursor.fetchall()
    
    print(f"🔢 TOTAL DE TÍTULOS DETECTADOS: {len(all_titles)}")
    print("=" * 60)
    
    for i, title in enumerate(all_titles, 1):
        print(f"\n{i:2d}. 📋 ANEXO {title['specific_annex_number']}")
        print(f"     📝 \"{title['specific_annex_title']}\"")
        print(f"     🏷️  Tema: {title['annex_theme']}")
        print(f"     📊 Chunks: {title['chunk_count']}")
        
        # Explain what "cabecera" means
        if i == 1:
            print(f"\n💡 ¿QUÉ SIGNIFICA 'CABECERA'?")
            print(f"     📄 Cabecera = El chunk que contiene el TÍTULO del anexo")
            print(f"     📄 Contenido = Los chunks con el contenido real del anexo")
            print(f"     📄 Ejemplo: 'ANEXO 1: Título...' es cabecera")
            print(f"     📄          Las páginas con datos/tablas son contenido")
    
    # Show breakdown by type
    print(f"\n📊 DESGLOSE POR TIPO DE ANEXO:")
    print("=" * 40)
    
    # Count by number vs letter
    numbered_annexes = [t for t in all_titles if t['specific_annex_number'].isdigit()]
    letter_annexes = [t for t in all_titles if not t['specific_annex_number'].isdigit()]
    
    print(f"🔢 Anexos numerados (1, 2, 3...): {len(numbered_annexes)}")
    for annex in numbered_annexes:
        print(f"   ANEXO {annex['specific_annex_number']}: \"{annex['specific_annex_title'][:50]}...\"")
    
    print(f"\n🔤 Anexos con letras (A, B, S...): {len(letter_annexes)}")
    for annex in letter_annexes:
        print(f"   ANEXO {annex['specific_annex_number']}: \"{annex['specific_annex_title'][:50]}...\"")
    
    # Show theme distribution
    print(f"\n🏷️  DISTRIBUCIÓN POR TEMA:")
    cursor = conn.execute("""
        SELECT annex_theme, COUNT(DISTINCT specific_annex_number) as annex_count
        FROM document_chunks 
        WHERE specific_annex_number IS NOT NULL
        GROUP BY annex_theme
        ORDER BY annex_count DESC
    """)
    
    themes = cursor.fetchall()
    for theme in themes:
        print(f"   {theme['annex_theme']}: {theme['annex_count']} anexos")
    
    conn.close()
    
    return len(all_titles)

if __name__ == "__main__":
    total = count_all_titles()
    print(f"\n✅ RESUMEN: {total} títulos de anexos detectados en total")