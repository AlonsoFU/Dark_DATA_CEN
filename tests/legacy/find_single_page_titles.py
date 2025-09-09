#!/usr/bin/env python3
"""
Find annex titles that appear as single page titles
"""

import sqlite3
import re

def find_single_page_titles():
    conn = sqlite3.connect("dark_data.db")
    conn.row_factory = sqlite3.Row
    
    print("🔍 BUSCANDO TÍTULOS EN PÁGINAS INDIVIDUALES")
    print("=" * 60)
    
    # Look for chunks with short content that might be title pages
    cursor = conn.execute("""
        SELECT id, page_range, content, content_length
        FROM document_chunks 
        WHERE content_length < 1000 
          AND (content LIKE '%ANEXO%' OR content LIKE '%INFORME%')
        ORDER BY id
    """)
    
    short_chunks = cursor.fetchall()
    
    print(f"📄 Chunks cortos con 'ANEXO' o 'INFORME': {len(short_chunks)}")
    
    annexes_found = []
    document_sections_found = []
    
    for chunk in short_chunks:
        content = chunk['content'] or ''
        lines = content.split('\n')
        
        print(f"\n📋 Chunk #{chunk['id']} (Página {chunk['page_range']}, {chunk['content_length']} chars)")
        
        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue
                
            # Look for ANEXO titles
            anexo_match = re.search(r'ANEXO\s+N?[ºo°]?\s*([1-8])', line_clean, re.IGNORECASE)
            if anexo_match:
                anexo_num = anexo_match.group(1)
                print(f"   🎯 ANEXO {anexo_num} ENCONTRADO: \"{line_clean}\"")
                
                # Get potential title from next lines
                title_lines = [line_clean]
                line_idx = lines.index(line)
                for i in range(line_idx + 1, min(line_idx + 4, len(lines))):
                    next_line = lines[i].strip()
                    if next_line and not next_line.startswith('[Page'):
                        title_lines.append(next_line)
                    else:
                        break
                
                full_title = ' '.join(title_lines)
                annexes_found.append({
                    'number': anexo_num,
                    'title': full_title,
                    'chunk_id': chunk['id'],
                    'page_range': chunk['page_range']
                })
            
            # Look for document sections like INFORME DIARIO
            elif any(section in line_clean.upper() for section in ['INFORME DIARIO', 'RESUMEN EJECUTIVO', 'CRONOLOGÍA']):
                print(f"   📄 SECCIÓN DOCUMENTO: \"{line_clean}\"")
                
                # Get full section title
                section_lines = [line_clean]
                line_idx = lines.index(line)
                for i in range(line_idx + 1, min(line_idx + 3, len(lines))):
                    next_line = lines[i].strip()
                    if next_line and not next_line.startswith('[Page'):
                        section_lines.append(next_line)
                    else:
                        break
                
                full_section = ' '.join(section_lines)
                document_sections_found.append({
                    'title': full_section,
                    'chunk_id': chunk['id'],
                    'page_range': chunk['page_range']
                })
    
    # Also search in longer chunks that might contain standalone titles
    print(f"\n🔍 BUSCANDO TAMBIÉN EN CHUNKS MÁS LARGOS:")
    cursor = conn.execute("""
        SELECT id, page_range, content
        FROM document_chunks 
        WHERE content_length BETWEEN 1000 AND 3000
          AND content LIKE '%ANEXO N%'
        ORDER BY id
        LIMIT 10
    """)
    
    medium_chunks = cursor.fetchall()
    
    for chunk in medium_chunks:
        content = chunk['content'] or ''
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line_clean = line.strip()
            
            # Look for lines that are just ANEXO titles
            if re.match(r'^\s*ANEXO\s+N?[ºo°]?\s*[1-8]\s*$', line_clean, re.IGNORECASE):
                print(f"\n📋 Chunk #{chunk['id']} (Página {chunk['page_range']})")
                print(f"   🎯 TÍTULO ANEXO: \"{line_clean}\"")
                
                # Get next few lines for complete title
                title_parts = [line_clean]
                for j in range(i + 1, min(i + 5, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and not next_line.startswith('[Page') and len(next_line) > 5:
                        title_parts.append(next_line)
                        print(f"   📝 Línea siguiente: \"{next_line}\"")
                    elif not next_line:
                        continue
                    else:
                        break
                
                # Extract anexo number
                anexo_match = re.search(r'ANEXO\s+N?[ºo°]?\s*([1-8])', line_clean, re.IGNORECASE)
                if anexo_match:
                    anexo_num = anexo_match.group(1)
                    full_title = ' '.join(title_parts)
                    annexes_found.append({
                        'number': anexo_num,
                        'title': full_title,
                        'chunk_id': chunk['id'],
                        'page_range': chunk['page_range']
                    })
    
    print(f"\n✅ RESUMEN DE BÚSQUEDA:")
    print(f"📋 Anexos encontrados en páginas individuales: {len(annexes_found)}")
    for annex in annexes_found:
        print(f"   ANEXO {annex['number']}: Chunk #{annex['chunk_id']} - \"{annex['title'][:60]}...\"")
    
    print(f"\n📄 Secciones del documento: {len(document_sections_found)}")
    for section in document_sections_found:
        print(f"   \"{section['title'][:60]}...\" - Chunk #{section['chunk_id']}")
    
    conn.close()
    return annexes_found, document_sections_found

if __name__ == "__main__":
    annexes, sections = find_single_page_titles()