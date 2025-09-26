#!/usr/bin/env python3
"""
Real content analysis - access actual content in chunks
"""

import sqlite3
from pathlib import Path

def analyze_real_content():
    conn = sqlite3.connect(str(Path(__file__).parent.parent.parent / "platform_data" / "database" / "dark_data.db"))
    
    print("🔍 ANÁLISIS REAL DEL CONTENIDO - PÁGINA 191")
    print("=" * 60)
    
    # Get the actual content, not the display version
    cursor = conn.execute("""
        SELECT id, page_range, content
        FROM document_chunks 
        WHERE page_range = '191-191'
        ORDER BY id
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    
    if result:
        chunk_id, page_range, content = result
        print(f"📋 Chunk #{chunk_id} (Página {page_range})")
        
        if content and len(content) > 20:
            # The content might be stored correctly, let's check raw
            print(f"📐 Contenido real encontrado: {len(content)} caracteres")
            
            # Split into lines and look for patterns
            lines = content.split('\n')
            print(f"📝 Total de líneas: {len(lines)}")
            
            # Show all lines to see what's actually there
            for i, line in enumerate(lines, 1):
                line_clean = line.strip()
                if line_clean and not line_clean.startswith('[Page'):
                    # Look for any annexo patterns
                    if any(word in line_clean.upper() for word in ['ANEXO', 'INFORME', 'RESUMEN']):
                        print(f"🎯 Línea {i:3d}: {line_clean}")
                    elif len(line_clean) < 100:  # Short lines might be titles
                        print(f"   Línea {i:3d}: {line_clean}")
                    elif i <= 10:  # Show first 10 lines anyway
                        print(f"   Línea {i:3d}: {line_clean[:80]}...")
        else:
            print("❌ No hay contenido real")
    
    print(f"\n🔍 NUEVO ALGORITMO: BUSCAR PÁGINAS INDIVIDUALES CON TÍTULOS")
    print("=" * 60)
    
    # New algorithm: look for pages that might be title pages
    # Strategy: find chunks with specific characteristics of title pages
    
    cursor = conn.execute("""
        SELECT id, page_range, content, content_length,
               CASE 
                   WHEN content LIKE '%ANEXO%' THEN 1
                   WHEN content LIKE '%INFORME DIARIO%' THEN 1  
                   ELSE 0
               END as has_title_keywords
        FROM document_chunks 
        WHERE content IS NOT NULL
          AND content_length BETWEEN 100 AND 2000  -- Title pages are usually not too long
          AND has_title_keywords = 1
        ORDER BY page_range, id
        LIMIT 20
    """)
    
    potential_titles = cursor.fetchall()
    
    print(f"📄 Chunks potenciales con títulos: {len(potential_titles)}")
    
    annexes_found = []
    sections_found = []
    
    for chunk_id, page_range, content, content_length, has_keywords in potential_titles:
        print(f"\n📋 Chunk #{chunk_id} (Página {page_range}, {content_length} chars)")
        
        if content:
            lines = content.split('\n')
            
            # Look for title patterns
            for i, line in enumerate(lines):
                line_clean = line.strip()
                
                # Skip page markers
                if line_clean.startswith('[Page') or line_clean.startswith('Página'):
                    continue
                
                # Look for ANEXO patterns
                if 'ANEXO' in line_clean.upper():
                    # Check if this looks like a title line
                    if len(line_clean) < 150 and any(char.isdigit() for char in line_clean):
                        print(f"   🎯 POSIBLE ANEXO: \"{line_clean}\"")
                        
                        # Get following lines for complete title
                        title_lines = [line_clean]
                        for j in range(i+1, min(i+3, len(lines))):
                            next_line = lines[j].strip()
                            if next_line and not next_line.startswith('[') and len(next_line) > 5:
                                title_lines.append(next_line)
                                print(f"   📝 Continuación: \"{next_line}\"")
                        
                        annexes_found.append({
                            'chunk_id': chunk_id,
                            'page_range': page_range,
                            'title_lines': title_lines
                        })
                        break
                
                # Look for other document sections
                elif any(section in line_clean.upper() for section in ['INFORME DIARIO', 'RESUMEN EJECUTIVO', 'CRONOLOGÍA']):
                    if len(line_clean) < 200:
                        print(f"   📄 SECCIÓN: \"{line_clean}\"")
                        
                        sections_found.append({
                            'chunk_id': chunk_id,
                            'page_range': page_range, 
                            'title': line_clean
                        })
    
    print(f"\n✅ RESUMEN DEL NUEVO ANÁLISIS:")
    print(f"📋 Anexos potenciales encontrados: {len(annexes_found)}")
    print(f"📄 Secciones del documento: {len(sections_found)}")
    
    conn.close()
    
    return annexes_found, sections_found

if __name__ == "__main__":
    annexes, sections = analyze_real_content()