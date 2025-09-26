#!/usr/bin/env python3
"""
Search for the exact ANEXO 2 title
"""

import sqlite3
from pathlib import Path
import re

def search_anexo_2():
    conn = sqlite3.connect(str(Path(__file__).parent.parent.parent / "platform_data" / "database" / "dark_data.db"))
    conn.row_factory = sqlite3.Row
    
    print("🔍 BÚSQUEDA ESPECÍFICA DEL TÍTULO DEL ANEXO 2")
    print("=" * 60)
    
    # Search broadly for chunks that might contain the title
    patterns_to_search = [
        '%ANEXO%2%',
        '%Anexo%2%', 
        '%febrero de 2025%',
        '%generación real%',
        '%días 25 y 26%'
    ]
    
    all_results = set()
    
    for pattern in patterns_to_search:
        cursor = conn.execute("""
            SELECT id, page_range, content
            FROM document_chunks 
            WHERE content LIKE ?
            ORDER BY id
        """, (pattern,))
        
        results = cursor.fetchall()
        print(f"📋 Patrón '{pattern}': {len(results)} chunks")
        
        for chunk in results:
            all_results.add(chunk['id'])
    
    print(f"\n🎯 Total de chunks únicos a revisar: {len(all_results)}")
    
    # Now examine each unique chunk
    for chunk_id in sorted(all_results):
        cursor = conn.execute("""
            SELECT id, page_range, content
            FROM document_chunks 
            WHERE id = ?
        """, (chunk_id,))
        
        chunk = cursor.fetchone()
        content = chunk['content']
        
        # Look for ANEXO patterns in the content
        if 'ANEXO' in content.upper() and '2' in content:
            print(f"\n📄 Chunk #{chunk['id']} (Página {chunk['page_range']})")
            
            # Split content into lines and look for the title
            lines = content.split('\n')
            found_title = False
            
            for i, line in enumerate(lines):
                line_clean = line.strip()
                
                # Check if this line contains ANEXO and 2
                if ('ANEXO' in line_clean.upper() and '2' in line_clean) or \
                   ('generación real' in line_clean.lower() and 'febrero' in line_clean.lower()):
                    
                    print(f"   🎯 POSIBLE TÍTULO en línea {i+1}:")
                    print(f"      \"{line_clean}\"")
                    
                    # Show surrounding lines for context
                    start = max(0, i-2)
                    end = min(len(lines), i+5)
                    
                    print(f"   📝 Contexto (líneas {start+1}-{end}):")
                    for j in range(start, end):
                        marker = " >>> " if j == i else "     "
                        context_line = lines[j].strip()
                        if context_line:
                            print(f"   {marker}{j+1}: {context_line}")
                    
                    found_title = True
                    break
            
            if not found_title:
                # Show first 200 chars as fallback
                content_preview = content.replace('\n', ' | ')[:200]
                print(f"   📝 Contenido: \"{content_preview}...\"")
    
    conn.close()

if __name__ == "__main__":
    search_anexo_2()