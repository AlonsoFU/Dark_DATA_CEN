#!/usr/bin/env python3
"""
Find ANEXO 5 with the specific pattern you provided
"""

import sqlite3
from pathlib import Path
import re

def find_anexo_5_specific():
    conn = sqlite3.connect(str(Path(__file__).parent.parent.parent / "platform_data" / "database" / "dark_data.db"))
    conn.row_factory = sqlite3.Row
    
    print("🔍 BUSCANDO ANEXO 5 CON PATRÓN ESPECÍFICO")
    print("=" * 60)
    print("Patrón buscado:")
    print("VVANEXO Nº5")
    print("Informe de trabajo y falla de instalaciones ingresados en el sistema del")
    print("Coordinador Eléctrico Nacional por las empresas coordinadas")
    
    # Search for variations of the pattern
    search_patterns = [
        '%VVANEXO%',
        '%ANEXO%5%',
        '%Informe de trabajo y falla%',
        '%instalaciones ingresados%',
        '%empresas coordinadas%',
        '%Coordinador Eléctrico Nacional%'
    ]
    
    all_matches = set()
    
    for pattern in search_patterns:
        cursor = conn.execute("""
            SELECT id, page_range, content
            FROM document_chunks 
            WHERE content LIKE ?
            ORDER BY id
        """, (pattern,))
        
        results = cursor.fetchall()
        
        if results:
            print(f"\n📋 Patrón '{pattern}': {len(results)} chunks")
            
            for chunk in results:
                all_matches.add(chunk['id'])
                
                if pattern == '%VVANEXO%' or pattern == '%Informe de trabajo y falla%':
                    # Show the content for these key patterns
                    content = chunk['content'] or ''
                    lines = content.split('\n')
                    
                    for i, line in enumerate(lines, 1):
                        line_clean = line.strip()
                        if ('vvanexo' in line_clean.lower() or 
                            'anexo' in line_clean.lower() and '5' in line_clean or
                            'informe de trabajo' in line_clean.lower()):
                            
                            print(f"   🎯 Chunk #{chunk['id']} (Página {chunk['page_range']})")
                            print(f"      Línea {i}: \"{line_clean}\"")
                            
                            # Show context lines
                            for j in range(max(1, i-1), min(len(lines)+1, i+4)):
                                if j != i and j <= len(lines):
                                    context_line = lines[j-1].strip()
                                    if context_line and not context_line.startswith('['):
                                        print(f"      Línea {j}: \"{context_line}\"")
                            break
    
    print(f"\n✅ CHUNKS ÚNICOS CON COINCIDENCIAS: {len(all_matches)}")
    
    # Now search with more flexible patterns
    print(f"\n🔍 BÚSQUEDA FLEXIBLE PARA ANEXO 5:")
    
    flexible_patterns = [
        r'.*ANEXO.*N?[ºo°]?\s*5',
        r'.*VVANEXO.*N?[ºo°]?\s*5',  # OCR error pattern
        r'Informe.*trabajo.*falla',
        r'instalaciones.*ingresados.*sistema'
    ]
    
    for pattern in flexible_patterns:
        print(f"\n📋 Patrón regex: {pattern}")
        
        cursor = conn.execute("""
            SELECT id, page_range, content
            FROM document_chunks 
            WHERE content IS NOT NULL
            ORDER BY id
        """)
        
        all_chunks = cursor.fetchall()
        matches = 0
        
        for chunk in all_chunks:
            content = chunk['content'] or ''
            
            if re.search(pattern, content, re.IGNORECASE):
                matches += 1
                
                # Find the matching line
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        print(f"   🎯 Chunk #{chunk['id']} (Página {chunk['page_range']})")
                        print(f"      Línea {i}: \"{line.strip()}\"")
                        break
                
                if matches >= 3:  # Limit output
                    break
        
        print(f"   Total coincidencias: {matches}")
    
    conn.close()

def create_corrected_anexo_5():
    """Create the corrected ANEXO 5 entry"""
    
    conn = sqlite3.connect(str(Path(__file__).parent.parent.parent / "platform_data" / "database" / "dark_data.db"))
    
    print(f"\n🔧 CREANDO ANEXO 5 CON TÍTULO CORRECTO")
    print("=" * 50)
    
    # First find a suitable chunk to assign as ANEXO 5
    cursor = conn.execute("""
        SELECT id, page_range, content
        FROM document_chunks 
        WHERE page_range LIKE '%191%'
           OR content LIKE '%Coordinador Eléctrico Nacional%empresas%'
           OR content LIKE '%instalaciones ingresados%'
        ORDER BY 
            CASE WHEN page_range LIKE '%191%' THEN 1 ELSE 2 END,
            id
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    
    if result:
        chunk_id, page_range, content = result
        
        # Correct title based on what you provided
        correct_title = "Informe de trabajo y falla de instalaciones ingresados en el sistema del Coordinador Eléctrico Nacional por las empresas coordinadas"
        
        # Update or insert ANEXO 5
        conn.execute("""
            UPDATE document_chunks 
            SET specific_annex_number = '5',
                specific_annex_title = ?,
                annex_theme = 'technical_analysis',
                is_annex_header = 1
            WHERE id = ?
        """, (correct_title, chunk_id))
        
        if cursor.rowcount > 0:
            print(f"✅ ANEXO 5 creado/actualizado:")
            print(f"   📋 Chunk #{chunk_id}")
            print(f"   📍 Página: {page_range}")
            print(f"   📝 Título: \"{correct_title}\"")
            
            conn.commit()
        else:
            print(f"❌ No se pudo actualizar el chunk")
    else:
        print(f"❌ No se encontró chunk adecuado para ANEXO 5")
    
    conn.close()

if __name__ == "__main__":
    find_anexo_5_specific()
    create_corrected_anexo_5()