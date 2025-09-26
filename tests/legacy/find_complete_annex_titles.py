#!/usr/bin/env python3
"""
Find complete annex titles in individual pages - ANEXO + descriptive text
"""

import sqlite3
from pathlib import Path
import re

def find_complete_annex_titles():
    conn = sqlite3.connect(str(Path(__file__).parent.parent.parent / "platform_data" / "database" / "dark_data.db"))
    conn.row_factory = sqlite3.Row
    
    print("🔍 BUSCANDO TÍTULOS COMPLETOS DE ANEXOS EN PÁGINAS INDIVIDUALES")
    print("=" * 70)
    print("Patrón esperado: 'ANEXO Nº[número]' seguido de texto descriptivo")
    
    # Strategy: Look for chunks that contain ANEXO followed by descriptive text
    # These would be title pages with both the number and description
    
    cursor = conn.execute("""
        SELECT id, page_range, content, content_length
        FROM document_chunks 
        WHERE content LIKE '%ANEXO%'
           OR content LIKE '%Anexo%'
        ORDER BY content_length  -- Start with shorter chunks (more likely to be title pages)
    """)
    
    chunks_with_anexos = cursor.fetchall()
    
    print(f"📄 Analizando {len(chunks_with_anexos)} chunks que contienen 'ANEXO'...")
    
    found_titles = []
    
    for chunk in chunks_with_anexos:
        content = chunk['content'] or ''
        
        if not content or len(content) > 5000:  # Skip very long chunks
            continue
        
        lines = content.split('\n')
        
        # Look for patterns like:
        # "ANEXO Nº5"
        # "Informe de trabajo y falla de instalaciones..."
        
        for i, line in enumerate(lines):
            line_clean = line.strip()
            
            # Skip page markers
            if line_clean.startswith('[Page') or line_clean.startswith('Página'):
                continue
            
            # Look for ANEXO line
            anexo_match = re.search(r'(ANEXO|Anexo)\s+N?[ºo°]?\s*([1-8])', line_clean, re.IGNORECASE)
            if anexo_match:
                anexo_num = anexo_match.group(2)
                anexo_line = line_clean
                
                # Look for descriptive text in following lines
                description_lines = []
                
                for j in range(i+1, min(i+10, len(lines))):  # Check next few lines
                    desc_line = lines[j].strip()
                    
                    # Skip empty lines and page markers
                    if not desc_line or desc_line.startswith('[') or desc_line.startswith('Página'):
                        continue
                    
                    # If the line looks like descriptive text (not a section number, not short)
                    if (len(desc_line) > 15 and 
                        not re.match(r'^\d+\.', desc_line) and  # Not like "1.2 Section"
                        not desc_line.upper() in ['RESUMEN', 'INTRODUCCIÓN', 'ANTECEDENTES']):
                        
                        description_lines.append(desc_line)
                        
                        # Stop if we hit what looks like another section
                        if any(stop_word in desc_line.upper() for stop_word in ['ANEXO', 'CAPÍTULO', 'SECCIÓN']):
                            if 'anexo' in desc_line.lower():
                                description_lines.pop()  # Remove this line
                            break
                
                if description_lines:
                    complete_title = anexo_line + ' ' + ' '.join(description_lines)
                    
                    found_titles.append({
                        'number': anexo_num,
                        'anexo_line': anexo_line,
                        'description': ' '.join(description_lines),
                        'complete_title': complete_title,
                        'chunk_id': chunk['id'],
                        'page_range': chunk['page_range'],
                        'content_length': chunk['content_length']
                    })
                    
                    print(f"\n🎯 ANEXO {anexo_num} ENCONTRADO")
                    print(f"   📋 Chunk #{chunk['id']} (Página {chunk['page_range']}, {chunk['content_length']} chars)")
                    print(f"   📝 Línea anexo: \"{anexo_line}\"")
                    print(f"   📝 Descripción: \"{' '.join(description_lines)[:100]}...\"")
                    
                    # Show context
                    print(f"   📄 Contexto:")
                    for k in range(max(0, i-1), min(len(lines), i+len(description_lines)+2)):
                        context_line = lines[k].strip()
                        if context_line and not context_line.startswith('['):
                            marker = "    >>> " if k == i else "        "
                            print(f"   {marker}{context_line[:80]}...")
                    
                    break  # Found anexo in this chunk, move to next chunk
    
    print(f"\n✅ RESUMEN DE TÍTULOS COMPLETOS ENCONTRADOS:")
    print(f"📋 Total: {len(found_titles)} anexos con títulos completos")
    
    # Sort by anexo number
    found_titles.sort(key=lambda x: int(x['number']))
    
    for i, title in enumerate(found_titles, 1):
        print(f"\n{i}. 📋 ANEXO {title['number']}")
        print(f"   📝 \"{title['complete_title'][:100]}...\"")
        print(f"   📋 Chunk #{title['chunk_id']} (Página {title['page_range']})")
    
    # Show which ones are still missing
    found_numbers = {title['number'] for title in found_titles}
    expected_numbers = {'1', '2', '3', '4', '5', '6', '7', '8'}
    missing_numbers = expected_numbers - found_numbers
    
    if missing_numbers:
        print(f"\n❌ ANEXOS AÚN NO ENCONTRADOS: {sorted(missing_numbers)}")
    else:
        print(f"\n✅ TODOS LOS ANEXOS 1-8 ENCONTRADOS COMO TÍTULOS COMPLETOS")
    
    conn.close()
    return found_titles

if __name__ == "__main__":
    titles = find_complete_annex_titles()