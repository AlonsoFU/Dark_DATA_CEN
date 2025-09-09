#!/usr/bin/env python3
"""
Find INFORME DIARIO titles in individual pages
"""

import sqlite3
import re

def find_informe_diario_titles():
    conn = sqlite3.connect("dark_data.db")
    conn.row_factory = sqlite3.Row
    
    print("🔍 BUSCANDO TÍTULOS DE 'INFORME DIARIO' EN PÁGINAS INDIVIDUALES")
    print("=" * 70)
    print("Patrón esperado: 'INFORME DIARIO' + fecha como 'Martes 25 de Febrero del 2025'")
    
    # Search for chunks that contain INFORME DIARIO patterns
    cursor = conn.execute("""
        SELECT id, page_range, content, content_length
        FROM document_chunks 
        WHERE (content LIKE '%INFORME DIARIO%' OR content LIKE '%Informe Diario%')
          AND content_length > 50
        ORDER BY content_length
    """)
    
    chunks_with_informe = cursor.fetchall()
    
    print(f"📄 Analizando {len(chunks_with_informe)} chunks que contienen 'INFORME DIARIO'...")
    
    found_titles = []
    
    for chunk in chunks_with_informe:
        content = chunk['content'] or ''
        
        if not content or content.startswith('[') and 'characters]' in content:
            continue
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line_clean = line.strip()
            
            # Skip page markers
            if line_clean.startswith('[Page') or line_clean.startswith('Página'):
                continue
            
            # Look for INFORME DIARIO patterns
            if re.search(r'INFORME\s+DIARIO', line_clean, re.IGNORECASE):
                print(f"\n🎯 INFORME DIARIO encontrado")
                print(f"   📋 Chunk #{chunk['id']} (Página {chunk['page_range']}, {chunk['content_length']} chars)")
                print(f"   📝 Línea: \"{line_clean}\"")
                
                # Look for date information in surrounding lines
                date_lines = []
                
                # Check current line and next few lines for dates
                lines_to_check = lines[i:i+5]  # Current + next 4 lines
                
                for j, check_line in enumerate(lines_to_check):
                    check_clean = check_line.strip()
                    
                    # Look for date patterns
                    date_patterns = [
                        r'(Lunes|Martes|Miércoles|Jueves|Viernes|Sábado|Domingo)\s+\d+\s+de\s+\w+\s+del?\s+\d{4}',
                        r'\d+\s+de\s+(Enero|Febrero|Marzo|Abril|Mayo|Junio|Julio|Agosto|Septiembre|Octubre|Noviembre|Diciembre)\s+del?\s+\d{4}',
                        r'(25|26)\s+de\s+febrero\s+de\s+2025',
                        r'febrero.*2025'
                    ]
                    
                    for pattern in date_patterns:
                        if re.search(pattern, check_clean, re.IGNORECASE):
                            date_lines.append(check_clean)
                            print(f"   📅 Fecha encontrada: \"{check_clean}\"")
                            break
                    
                    # Also show any significant lines that might be part of the title
                    if (check_clean and len(check_clean) > 5 and 
                        not check_clean.startswith('[') and 
                        j <= 3):  # Only first few lines
                        if j == 0:  # The INFORME DIARIO line itself
                            continue
                        print(f"   📝 Línea {j+1}: \"{check_clean}\"")
                
                # Build complete title
                complete_title = line_clean
                if date_lines:
                    complete_title += " " + " ".join(date_lines[:2])  # Max 2 date lines
                
                found_titles.append({
                    'title': complete_title,
                    'chunk_id': chunk['id'],
                    'page_range': chunk['page_range'],
                    'content_length': chunk['content_length'],
                    'informe_line': line_clean,
                    'date_info': date_lines
                })
                
                # Show more context
                print(f"   📄 Contexto completo:")
                start_line = max(0, i-1)
                end_line = min(len(lines), i+4)
                for k in range(start_line, end_line):
                    context_line = lines[k].strip()
                    if context_line and not context_line.startswith('['):
                        marker = "    >>> " if k == i else "        "
                        print(f"   {marker}{context_line[:80]}...")
                
                break  # Found informe in this chunk, move to next
    
    print(f"\n✅ RESUMEN DE TÍTULOS DE INFORME DIARIO:")
    print(f"📋 Total encontrados: {len(found_titles)}")
    
    if found_titles:
        for i, title_info in enumerate(found_titles, 1):
            print(f"\n{i}. 📄 INFORME DIARIO")
            print(f"   📝 \"{title_info['title'][:100]}...\"")
            print(f"   📋 Chunk #{title_info['chunk_id']} (Página {title_info['page_range']})")
            if title_info['date_info']:
                print(f"   📅 Fechas: {', '.join(title_info['date_info'][:2])}")
    else:
        print("❌ No se encontraron títulos completos de INFORME DIARIO en páginas individuales")
    
    # Also look for other document section patterns
    print(f"\n🔍 BUSCANDO OTROS TÍTULOS DE SECCIONES DEL DOCUMENTO:")
    
    other_patterns = [
        'RESUMEN EJECUTIVO',
        'CRONOLOGÍA',
        'ANTECEDENTES',
        'ANÁLISIS DE LA FALLA',
        'CONCLUSIONES'
    ]
    
    for pattern in other_patterns:
        cursor = conn.execute("""
            SELECT id, page_range, content
            FROM document_chunks 
            WHERE content LIKE ?
              AND content NOT LIKE '[%characters]'
            ORDER BY id
            LIMIT 3
        """, (f'%{pattern}%',))
        
        results = cursor.fetchall()
        
        if results:
            print(f"\n📋 Patrón '{pattern}': {len(results)} chunks")
            
            for chunk_id, page_range, content in results:
                lines = content.split('\n') if content else []
                
                for line in lines:
                    line_clean = line.strip()
                    if pattern.lower() in line_clean.lower() and len(line_clean) < 100:
                        print(f"   Chunk #{chunk_id} (Página {page_range}): \"{line_clean}\"")
                        break
    
    conn.close()
    return found_titles

if __name__ == "__main__":
    titles = find_informe_diario_titles()