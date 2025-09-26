#!/usr/bin/env python3
"""
New algorithm to find title pages by analyzing page structure and content patterns
"""

import sqlite3
from pathlib import Path
import re

def find_title_pages():
    conn = sqlite3.connect(str(Path(__file__).parent.parent.parent / "platform_data" / "database" / "dark_data.db"))
    conn.row_factory = sqlite3.Row
    
    print("🔍 NUEVO ALGORITMO: ENCONTRAR PÁGINAS DE TÍTULO")
    print("=" * 60)
    
    print("Estrategia:")
    print("1. Buscar chunks con contenido corto/medio (páginas de título)")
    print("2. Buscar patrones específicos de ANEXO")
    print("3. Buscar secciones como INFORME DIARIO")
    print("4. Analizar todas las páginas una por una")
    
    # Strategy 1: Look through ALL chunks systematically
    cursor = conn.execute("""
        SELECT id, page_range, content, content_length, chunk_type
        FROM document_chunks 
        WHERE content IS NOT NULL
        ORDER BY id
    """)
    
    all_chunks = cursor.fetchall()
    
    print(f"\n📊 Analizando {len(all_chunks)} chunks sistemáticamente...")
    
    found_titles = []
    
    for chunk in all_chunks:
        if not chunk['content']:
            continue
            
        content = chunk['content']
        
        # Skip if content is just the placeholder
        if content.strip() in ['[4550 characters]', '[3663 characters]', '[277 characters]']:
            continue
        
        # Look for title patterns
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line_clean = line.strip()
            
            # Skip empty lines and page markers
            if not line_clean or line_clean.startswith('[Page') or line_clean.startswith('Página'):
                continue
            
            # Pattern 1: Look for standalone ANEXO titles
            anexo_patterns = [
                r'^ANEXO\s+N?[ºo°]?\s*([1-8])\s*$',  # Just "ANEXO N°1"
                r'^ANEXO\s+N?[ºo°]?\s*([1-8])\s*[-:]?\s*(.{5,100})\s*$'  # "ANEXO N°1 - Title"
            ]
            
            for pattern in anexo_patterns:
                match = re.match(pattern, line_clean, re.IGNORECASE)
                if match:
                    anexo_num = match.group(1)
                    
                    # Get the complete title from following lines
                    title_parts = [line_clean]
                    
                    for j in range(i+1, min(i+5, len(lines))):
                        next_line = lines[j].strip()
                        if next_line and not next_line.startswith('[') and not next_line.startswith('Página'):
                            if len(next_line) > 10 and not re.match(r'^\d+\.\d+', next_line):  # Not a section number
                                title_parts.append(next_line)
                        elif not next_line:  # Empty line
                            continue
                        else:
                            break
                    
                    complete_title = ' '.join(title_parts)
                    
                    found_titles.append({
                        'type': 'ANEXO',
                        'number': anexo_num,
                        'title': complete_title,
                        'chunk_id': chunk['id'],
                        'page_range': chunk['page_range'],
                        'line_num': i+1
                    })
                    
                    print(f"🎯 ANEXO {anexo_num} encontrado!")
                    print(f"   Chunk #{chunk['id']} (Página {chunk['page_range']})")
                    print(f"   Título: \"{complete_title}\"")
                    break
            
            # Pattern 2: Look for document sections
            section_patterns = [
                r'INFORME\s+DIARIO',
                r'(Lunes|Martes|Miércoles|Jueves|Viernes|Sábado|Domingo)\s+\d+\s+de\s+\w+',
                r'RESUMEN\s+EJECUTIVO',
                r'CRONOLOGÍA',
                r'ANÁLISIS\s+DE\s+LA\s+FALLA'
            ]
            
            for pattern in section_patterns:
                if re.search(pattern, line_clean, re.IGNORECASE):
                    # This looks like a section title
                    section_title = line_clean
                    
                    # Get additional context lines
                    for j in range(i+1, min(i+3, len(lines))):
                        next_line = lines[j].strip()
                        if next_line and not next_line.startswith('[') and len(next_line) > 5:
                            section_title += ' ' + next_line
                        else:
                            break
                    
                    found_titles.append({
                        'type': 'SECTION',
                        'number': None,
                        'title': section_title,
                        'chunk_id': chunk['id'], 
                        'page_range': chunk['page_range'],
                        'line_num': i+1
                    })
                    
                    print(f"📄 SECCIÓN encontrada!")
                    print(f"   Chunk #{chunk['id']} (Página {chunk['page_range']})")
                    print(f"   Título: \"{section_title[:80]}...\"")
                    break
    
    print(f"\n✅ RESULTADOS DEL ANÁLISIS SISTEMÁTICO:")
    print(f"📋 Total de títulos encontrados: {len(found_titles)}")
    
    # Group by type
    anexos = [t for t in found_titles if t['type'] == 'ANEXO']
    sections = [t for t in found_titles if t['type'] == 'SECTION']
    
    print(f"\n📋 ANEXOS ENCONTRADOS: {len(anexos)}")
    for anexo in anexos:
        print(f"   ANEXO {anexo['number']}: Chunk #{anexo['chunk_id']} (Página {anexo['page_range']})")
        print(f"      \"{anexo['title'][:80]}...\"")
    
    print(f"\n📄 SECCIONES ENCONTRADAS: {len(sections)}")
    for section in sections:
        print(f"   Chunk #{section['chunk_id']} (Página {section['page_range']})")
        print(f"   \"{section['title'][:80]}...\"")
    
    conn.close()
    return found_titles

def check_specific_pages():
    """Check specific pages that should contain titles"""
    
    conn = sqlite3.connect(str(Path(__file__).parent.parent.parent / "platform_data" / "database" / "dark_data.db"))
    
    print(f"\n🔍 VERIFICANDO PÁGINAS ESPECÍFICAS:")
    print("=" * 50)
    
    # Check pages around where annexes should be
    target_pages = ['191', '164', '180', '200', '250']  # You mentioned 191 for ANEXO 5
    
    for page in target_pages:
        cursor = conn.execute("""
            SELECT id, page_range, content
            FROM document_chunks 
            WHERE page_range LIKE ?
            ORDER BY id
            LIMIT 1
        """, (f'%{page}%',))
        
        result = cursor.fetchone()
        if result:
            chunk_id, page_range, content = result
            print(f"\n📄 Página {page} - Chunk #{chunk_id}")
            
            if content and len(content) > 50:
                # Try to extract meaningful lines
                lines = content.split('\n')[:10]  # First 10 lines
                meaningful_lines = []
                
                for line in lines:
                    line_clean = line.strip()
                    if (line_clean and 
                        not line_clean.startswith('[') and 
                        not line_clean.startswith('Página') and
                        len(line_clean) > 3):
                        meaningful_lines.append(line_clean)
                
                if meaningful_lines:
                    print(f"   Contenido:")
                    for i, line in enumerate(meaningful_lines[:5], 1):
                        marker = "🎯 " if any(word in line.upper() for word in ['ANEXO', 'INFORME']) else "   "
                        print(f"   {marker}{i}: {line[:80]}...")
                else:
                    print(f"   ❌ No se pudo extraer contenido significativo")
            else:
                print(f"   ❌ Sin contenido o muy corto")
    
    conn.close()

if __name__ == "__main__":
    titles = find_title_pages()
    check_specific_pages()