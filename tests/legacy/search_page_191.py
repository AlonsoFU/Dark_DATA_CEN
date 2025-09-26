#!/usr/bin/env python3
"""
Search specifically for page 191 and show all individual page titles found
"""

import sqlite3
from pathlib import Path

def search_page_191():
    conn = sqlite3.connect(str(Path(__file__).parent.parent.parent / "platform_data" / "database" / "dark_data.db"))
    conn.row_factory = sqlite3.Row
    
    print("🔍 BUSCANDO ESPECÍFICAMENTE PÁGINA 191 - ANEXO 5")
    print("=" * 60)
    
    # Search for chunks containing page 191
    cursor = conn.execute("""
        SELECT id, page_range, content, content_length
        FROM document_chunks 
        WHERE page_range LIKE '%191%' 
           OR content LIKE '%Page 191%'
        ORDER BY id
    """)
    
    page_191_chunks = cursor.fetchall()
    
    print(f"📄 Chunks que contienen página 191: {len(page_191_chunks)}")
    
    for chunk in page_191_chunks:
        print(f"\n📋 Chunk #{chunk['id']}")
        print(f"   📏 Páginas: {chunk['page_range']}")
        print(f"   📐 Tamaño: {chunk['content_length']} caracteres")
        
        if chunk['content'] and chunk['content_length'] < 5000:  # Show content if not too long
            content = chunk['content']
            lines = content.split('\n')
            
            print(f"   📝 CONTENIDO:")
            for i, line in enumerate(lines[:15], 1):  # First 15 lines
                line_clean = line.strip()
                if line_clean and not line_clean.startswith('[') and 'characters' not in line_clean:
                    # Highlight ANEXO lines
                    marker = "🎯 " if 'anexo' in line_clean.lower() else "   "
                    print(f"   {marker}{i:2d}: {line_clean}")
        else:
            print(f"   📝 Contenido muy largo o vacío")
    
    conn.close()

def show_all_detected_titles():
    """Show all titles we've actually found with their sources"""
    
    conn = sqlite3.connect(str(Path(__file__).parent.parent.parent / "platform_data" / "database" / "dark_data.db"))
    conn.row_factory = sqlite3.Row
    
    print(f"\n📊 RESUMEN: TODOS LOS TÍTULOS DETECTADOS")
    print("=" * 60)
    
    # Get current detected annexes
    cursor = conn.execute("""
        SELECT specific_annex_number, specific_annex_title, annex_theme, 
               COUNT(*) as chunk_count
        FROM document_chunks 
        WHERE specific_annex_number IS NOT NULL
        GROUP BY specific_annex_number, specific_annex_title, annex_theme
        ORDER BY CAST(specific_annex_number AS INTEGER)
    """)
    
    detected_annexes = cursor.fetchall()
    
    print(f"🔢 ANEXOS ACTUALMENTE DETECTADOS: {len(detected_annexes)}")
    
    for i, annex in enumerate(detected_annexes, 1):
        print(f"\n{i}. 📋 ANEXO {annex['specific_annex_number']}")
        print(f"   📝 \"{annex['specific_annex_title']}\"")
        print(f"   🏷️  {annex['annex_theme']}")
        print(f"   📊 {annex['chunk_count']} chunk(s)")
    
    # Show what we know from the index
    print(f"\n📋 TÍTULOS CONOCIDOS DEL ÍNDICE (pero no detectados como páginas individuales):")
    
    index_titles = {
        '1': "Detalle de la generación programada para los días 25 y 26 de febrero de 2025",
        '2': "Detalle de la generación real de los días 25 y 26 de febrero de 2025", 
        '3': "Detalle del Movimiento de Centrales e Informe Diario del CDC correspondientes a los días 25 y 26 de febrero de 2025",
        '4': "Detalle de los mantenimientos programados y forzados para los días 25 y 26 de febrero de 2025",
        '5': "Informes de fallas de instalaciones ingresados en el sistema del Coordinador Eléctrico Nacional por las empresas involucradas en la falla",
        '6': "Otros antecedentes aportados por las empresas involucradas en la falla",
        '7': "Otros antecedentes aportados por el Coordinador Eléctrico Nacional", 
        '8': "Análisis operativo del esquema EDAC"
    }
    
    detected_numbers = {annex['specific_annex_number'] for annex in detected_annexes}
    
    for num, title in index_titles.items():
        status = "✅ Detectado" if num in detected_numbers else "❌ Solo en índice"
        print(f"   ANEXO {num}: {status}")
        print(f"      \"{title}\"")
    
    conn.close()

if __name__ == "__main__":
    search_page_191()
    show_all_detected_titles()