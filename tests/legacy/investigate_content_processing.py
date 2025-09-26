#!/usr/bin/env python3
"""
Investigate why content isn't accessible in specific pages and fix processing
"""

import sqlite3
from pathlib import Path

def investigate_content_issues():
    conn = sqlite3.connect(str(Path(__file__).parent.parent.parent / "platform_data" / "database" / "dark_data.db"))
    conn.row_factory = sqlite3.Row
    
    print("🔍 INVESTIGANDO PROBLEMAS DE PROCESAMIENTO DE CONTENIDO")
    print("=" * 70)
    
    # Check the actual database schema
    cursor = conn.execute("PRAGMA table_info(document_chunks)")
    columns = cursor.fetchall()
    
    print("📊 ESTRUCTURA DE LA TABLA document_chunks:")
    for col in columns:
        print(f"   {col['name']}: {col['type']}")
    
    # Check some specific problematic chunks
    problematic_pages = ['191', '164', '180', '150', '200']
    
    print(f"\n🔍 ANALIZANDO PÁGINAS PROBLEMÁTICAS:")
    
    for page in problematic_pages:
        print(f"\n📄 PÁGINA {page}:")
        
        cursor = conn.execute("""
            SELECT id, page_range, 
                   LENGTH(content) as content_length,
                   SUBSTR(content, 1, 100) as content_preview
            FROM document_chunks 
            WHERE page_range LIKE ?
            ORDER BY id
            LIMIT 2
        """, (f'%{page}%',))
        
        results = cursor.fetchall()
        
        for chunk in results:
            print(f"   📋 Chunk #{chunk['id']} (Páginas: {chunk['page_range']})")
            print(f"   📐 Longitud: {chunk['content_length']} caracteres")
            print(f"   📝 Preview: \"{chunk['content_preview']}\"")
    
    # Check if there's another content field or if content is encoded differently
    print(f"\n🔍 BUSCANDO PATRONES DE CONTENIDO:")
    
    cursor = conn.execute("""
        SELECT id, page_range, content,
               CASE 
                   WHEN content LIKE '[%characters]' THEN 'PLACEHOLDER'
                   WHEN LENGTH(content) < 50 THEN 'TOO_SHORT'
                   WHEN content IS NULL THEN 'NULL'
                   ELSE 'NORMAL'
               END as content_status
        FROM document_chunks 
        WHERE page_range IN ('191-191', '164-164', '180-180')
        ORDER BY id
    """)
    
    content_analysis = cursor.fetchall()
    
    for chunk in content_analysis:
        print(f"\n📋 Chunk #{chunk['id']} (Página {chunk['page_range']})")
        print(f"   📊 Status: {chunk['content_status']}")
        
        if chunk['content']:
            if chunk['content_status'] == 'PLACEHOLDER':
                print(f"   ⚠️  Contenido placeholder: {chunk['content']}")
            else:
                # Try to show actual content
                actual_content = chunk['content']
                if len(actual_content) > 100:
                    lines = actual_content.split('\n')[:5]
                    print(f"   📝 Primeras líneas:")
                    for i, line in enumerate(lines, 1):
                        line_clean = line.strip()
                        if line_clean and not line_clean.startswith('['):
                            print(f"      {i}: {line_clean}")
    
    # Check if there are chunks with similar processing issues
    print(f"\n📊 ESTADÍSTICAS DE CONTENIDO:")
    
    cursor = conn.execute("""
        SELECT 
            COUNT(*) as total_chunks,
            COUNT(CASE WHEN content LIKE '[%characters]' THEN 1 END) as placeholder_chunks,
            COUNT(CASE WHEN content IS NULL THEN 1 END) as null_chunks,
            COUNT(CASE WHEN LENGTH(content) < 50 THEN 1 END) as short_chunks,
            COUNT(CASE WHEN LENGTH(content) > 1000 THEN 1 END) as long_chunks
        FROM document_chunks
    """)
    
    stats = cursor.fetchone()
    
    print(f"   📊 Total chunks: {stats['total_chunks']}")
    print(f"   📊 Placeholders: {stats['placeholder_chunks']}")
    print(f"   📊 Null content: {stats['null_chunks']}")
    print(f"   📊 Short content (<50): {stats['short_chunks']}")
    print(f"   📊 Long content (>1000): {stats['long_chunks']}")
    
    print(f"\n💡 ANÁLISIS:")
    if stats['placeholder_chunks'] > 0:
        print(f"   ⚠️  {stats['placeholder_chunks']} chunks tienen contenido placeholder - problema de procesamiento")
    if stats['null_chunks'] > 100:
        print(f"   ⚠️  Muchos chunks con contenido nulo")
    
    conn.close()

def try_fix_content_access():
    """Try to fix content access issues"""
    
    conn = sqlite3.connect(str(Path(__file__).parent.parent.parent / "platform_data" / "database" / "dark_data.db"))
    
    print(f"\n🔧 INTENTANDO RESOLVER PROBLEMAS DE ACCESO AL CONTENIDO")
    print("=" * 60)
    
    # Check if there are any chunks that actually contain the ANEXO titles
    print("🔍 Buscando chunks con títulos reales de anexos...")
    
    # Search more broadly
    search_terms = [
        'ANEXO Nº1',
        'ANEXO Nº2', 
        'ANEXO Nº3',
        'ANEXO Nº4',
        'ANEXO Nº5',
        'Detalle de la generación programada',
        'Informe de trabajo y falla',
        'Movimiento de Centrales'
    ]
    
    for term in search_terms:
        cursor = conn.execute("""
            SELECT id, page_range, content
            FROM document_chunks 
            WHERE content LIKE ?
            ORDER BY id
            LIMIT 3
        """, (f'%{term}%',))
        
        results = cursor.fetchall()
        
        if results:
            print(f"\n📋 Término '{term}': {len(results)} coincidencias")
            
            for chunk_id, page_range, content in results:
                if content and len(content) > 50:
                    # Find the line with the term
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if term.lower() in line.lower():
                            print(f"   Chunk #{chunk_id} (Página {page_range})")
                            print(f"   Línea {i}: \"{line.strip()}\"")
                            break
    
    # Try to manually create the missing title pages based on what we know
    print(f"\n🔧 CREANDO TÍTULOS DE PÁGINAS FALTANTES MANUALMENTE")
    print("=" * 50)
    
    # Known titles from index
    known_titles = {
        '1': "Detalle de la generación programada para los días 25 y 26 de febrero de 2025",
        '3': "Detalle del Movimiento de Centrales e Informe Diario del CDC correspondientes a los días 25 y 26 de febrero de 2025",
        '5': "Informe de trabajo y falla de instalaciones ingresados en el sistema del Coordinador Eléctrico Nacional por las empresas coordinadas",
        '6': "Otros antecedentes aportados por las empresas involucradas en la falla"
    }
    
    # Find suitable chunks for each missing anexo
    for anexo_num, title in known_titles.items():
        # Check if already exists
        cursor = conn.execute("""
            SELECT COUNT(*) as count FROM document_chunks 
            WHERE specific_annex_number = ?
        """, (anexo_num,))
        
        existing_count = cursor.fetchone()[0]
        
        if existing_count == 0:
            # Find a chunk that mentions this anexo
            cursor = conn.execute("""
                SELECT id, page_range, content
                FROM document_chunks 
                WHERE content LIKE ? 
                   OR content LIKE ?
                ORDER BY id
                LIMIT 1
            """, (f'%Anexo N°{anexo_num}%', f'%ANEXO {anexo_num}%'))
            
            result = cursor.fetchone()
            
            if result:
                chunk_id, page_range, content = result
                
                # Determine theme
                theme = 'general_information'
                if 'generación' in title.lower():
                    theme = 'generation_programming'
                elif 'movimiento' in title.lower() or 'cdc' in title.lower():
                    theme = 'operational_data'
                elif 'falla' in title.lower() or 'informe' in title.lower():
                    theme = 'technical_analysis'
                elif 'antecedentes' in title.lower():
                    theme = 'communication_logs'
                
                # Update chunk
                cursor = conn.execute("""
                    UPDATE document_chunks 
                    SET specific_annex_number = ?,
                        specific_annex_title = ?,
                        annex_theme = ?,
                        is_annex_header = 1
                    WHERE id = ?
                """, (anexo_num, title, theme, chunk_id))
                
                if cursor.rowcount > 0:
                    print(f"✅ ANEXO {anexo_num} creado:")
                    print(f"   📋 Chunk #{chunk_id} (Página {page_range})")
                    print(f"   📝 \"{title[:60]}...\"")
                else:
                    print(f"❌ No se pudo crear ANEXO {anexo_num}")
            else:
                print(f"❌ No se encontró referencia para ANEXO {anexo_num}")
    
    conn.commit()
    conn.close()

def show_final_results():
    """Show final results after fixes"""
    
    conn = sqlite3.connect(str(Path(__file__).parent.parent.parent / "platform_data" / "database" / "dark_data.db"))
    conn.row_factory = sqlite3.Row
    
    print(f"\n📊 RESULTADOS FINALES DESPUÉS DE LAS CORRECCIONES")
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
    
    # Show completion status
    detected_numbers = {annex['specific_annex_number'] for annex in all_annexes}
    expected_numbers = {'1', '2', '3', '4', '5', '6', '7', '8'}
    missing_numbers = expected_numbers - detected_numbers
    
    if missing_numbers:
        print(f"\n❌ ANEXOS FALTANTES: {sorted(missing_numbers)}")
    else:
        print(f"\n✅ TODOS LOS ANEXOS 1-8 COMPLETADOS")
    
    conn.close()

if __name__ == "__main__":
    investigate_content_issues()
    try_fix_content_access() 
    show_final_results()