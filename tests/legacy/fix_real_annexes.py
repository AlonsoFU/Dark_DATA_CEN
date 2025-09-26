#!/usr/bin/env python3
"""
Fix annexes to detect only ANEXOS 1-8 and document sections
"""

import sqlite3
from pathlib import Path

def fix_real_annexes():
    conn = sqlite3.connect(str(Path(__file__).parent.parent.parent / "platform_data" / "database" / "dark_data.db"))
    
    print("🔧 CORRIGIENDO DETECCIÓN DE ANEXOS REALES")
    print("=" * 60)
    
    # First, clear wrong annexes
    print("🗑️  LIMPIANDO ANEXOS INCORRECTOS:")
    
    wrong_annexes = ['A', 'N', 'S', 'V', 'W', '9', '13', '47']
    
    for wrong_num in wrong_annexes:
        cursor = conn.execute("""
            UPDATE document_chunks 
            SET specific_annex_number = NULL,
                specific_annex_title = NULL,
                annex_theme = NULL,
                is_annex_header = NULL
            WHERE specific_annex_number = ?
        """, (wrong_num,))
        
        if cursor.rowcount > 0:
            print(f"   ❌ Limpiado ANEXO {wrong_num} ({cursor.rowcount} chunks)")
    
    conn.commit()
    
    # Now set the correct ANEXOS 1-8 from the index
    print(f"\n✅ ESTABLECIENDO ANEXOS REALES 1-8:")
    
    real_annexes = {
        '1': "Detalle de la generación programada para los días 25 y 26 de febrero de 2025",
        '2': "Detalle de la generación real de los días 25 y 26 de febrero de 2025",
        '3': "Detalle del Movimiento de Centrales e Informe Diario del CDC correspondientes a los días 25 y 26 de febrero de 2025",
        '4': "Detalle de los mantenimientos programados y forzados para los días 25 y 26 de febrero de 2025",
        '5': "Informes de fallas de instalaciones ingresados en el sistema del Coordinador Eléctrico Nacional por las empresas involucradas en la falla",
        '6': "Otros antecedentes aportados por las empresas involucradas en la falla",
        '7': "Otros antecedentes aportados por el Coordinador Eléctrico Nacional",
        '8': "Análisis operativo del esquema EDAC"
    }
    
    for anexo_num, title in real_annexes.items():
        # Check if already exists
        cursor = conn.execute("""
            SELECT COUNT(*) as count FROM document_chunks 
            WHERE specific_annex_number = ?
        """, (anexo_num,))
        
        existing_count = cursor.fetchone()[0]
        
        if existing_count == 0:
            # Try to find content that belongs to this anexo
            search_patterns = [
                f'%ANEXO {anexo_num}%',
                f'%Anexo {anexo_num}%',
                f'%ANEXO N°{anexo_num}%'
            ]
            
            found_chunk = None
            for pattern in search_patterns:
                cursor = conn.execute("""
                    SELECT id, page_range, content
                    FROM document_chunks 
                    WHERE content LIKE ?
                    ORDER BY id
                    LIMIT 1
                """, (pattern,))
                
                result = cursor.fetchone()
                if result:
                    found_chunk = result
                    break
            
            if found_chunk:
                # Determine theme
                theme = 'general_information'
                if 'generación' in title.lower():
                    theme = 'generation_programming'
                elif 'movimiento' in title.lower() or 'cdc' in title.lower():
                    theme = 'operational_data'
                elif 'mantenimiento' in title.lower():
                    theme = 'equipment_details'
                elif 'fallas' in title.lower():
                    theme = 'technical_analysis'
                elif 'antecedentes' in title.lower():
                    theme = 'communication_logs'
                elif 'edac' in title.lower():
                    theme = 'technical_analysis'
                
                # Update this chunk
                conn.execute("""
                    UPDATE document_chunks 
                    SET specific_annex_number = ?,
                        specific_annex_title = ?,
                        annex_theme = ?,
                        is_annex_header = 1
                    WHERE id = ?
                """, (anexo_num, title, theme, found_chunk[0]))
                
                print(f"   ✅ ANEXO {anexo_num}: Asignado a chunk #{found_chunk[0]}")
            else:
                print(f"   ❓ ANEXO {anexo_num}: No se encontró contenido")
        else:
            print(f"   ✅ ANEXO {anexo_num}: Ya existe")
    
    conn.commit()
    
    # Now look for document sections like "INFORME DIARIO"
    print(f"\n🔍 BUSCANDO SECCIONES DEL DOCUMENTO:")
    
    section_patterns = [
        'INFORME DIARIO',
        'Martes 25 de Febrero',
        'Miércoles 26 de Febrero',
        'RESUMEN EJECUTIVO',
        'CRONOLOGÍA',
        'ANÁLISIS DE LA FALLA'
    ]
    
    for pattern in section_patterns:
        cursor = conn.execute("""
            SELECT id, page_range, content
            FROM document_chunks 
            WHERE content LIKE ?
            ORDER BY id
            LIMIT 3
        """, (f'%{pattern}%',))
        
        results = cursor.fetchall()
        if results:
            print(f"   📄 '{pattern}': {len(results)} chunks encontrados")
            for result in results:
                lines = result[2].split('\n') if result[2] else []
                for line in lines:
                    if pattern.lower() in line.lower():
                        print(f"      Chunk #{result[0]} (Página {result[1]}): \"{line.strip()}\"")
                        break
    
    conn.close()

def show_corrected_annexes():
    """Show the corrected annexes"""
    
    conn = sqlite3.connect(str(Path(__file__).parent.parent.parent / "platform_data" / "database" / "dark_data.db"))
    conn.row_factory = sqlite3.Row
    
    print(f"\n📊 ANEXOS CORREGIDOS (SOLO 1-8):")
    print("=" * 50)
    
    cursor = conn.execute("""
        SELECT specific_annex_number, specific_annex_title, annex_theme, COUNT(*) as chunk_count
        FROM document_chunks 
        WHERE specific_annex_number IS NOT NULL
        GROUP BY specific_annex_number, specific_annex_title, annex_theme
        ORDER BY CAST(specific_annex_number AS INTEGER)
    """)
    
    corrected_annexes = cursor.fetchall()
    
    if corrected_annexes:
        for annex in corrected_annexes:
            print(f"\n📋 ANEXO {annex['specific_annex_number']}")
            print(f"   📝 \"{annex['specific_annex_title']}\"")
            print(f"   🏷️  {annex['annex_theme']}")
            print(f"   📊 {annex['chunk_count']} chunk(s)")
    else:
        print("❌ No hay anexos detectados")
    
    conn.close()

if __name__ == "__main__":
    fix_real_annexes()
    show_corrected_annexes()