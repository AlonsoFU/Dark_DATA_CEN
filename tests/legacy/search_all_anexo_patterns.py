#!/usr/bin/env python3
"""
Search all chunks for ANEXO patterns including missing 1, 3, 5
"""

import sqlite3
import re

def search_all_anexo_patterns():
    conn = sqlite3.connect("dark_data.db")
    conn.row_factory = sqlite3.Row
    
    print("🔍 BÚSQUEDA COMPLETA DE PATRONES ANEXO 1, 3, 5")
    print("=" * 60)
    
    missing_annexes = ['1', '3', '5']
    
    for anexo_num in missing_annexes:
        print(f"\n🔍 BUSCANDO ANEXO {anexo_num}:")
        print("=" * 30)
        
        # Different search patterns
        patterns = [
            f'%ANEXO {anexo_num}%',
            f'%Anexo {anexo_num}%', 
            f'%ANEXO N°{anexo_num}%',
            f'%ANEXO Nº{anexo_num}%',
            f'%ANEXO N {anexo_num}%'
        ]
        
        all_results = set()
        
        for pattern in patterns:
            cursor = conn.execute("""
                SELECT id, page_range, content
                FROM document_chunks 
                WHERE content LIKE ?
                ORDER BY id
            """, (pattern,))
            
            results = cursor.fetchall()
            
            if results:
                print(f"   📋 Patrón '{pattern}': {len(results)} chunks")
                
                for chunk in results:
                    all_results.add(chunk['id'])
                    
                    # Look for the specific line with ANEXO
                    lines = chunk['content'].split('\n') if chunk['content'] else []
                    
                    for i, line in enumerate(lines):
                        line_clean = line.strip()
                        
                        # Check if this line contains the anexo pattern
                        if (f'anexo {anexo_num}' in line_clean.lower() or 
                            f'anexo n°{anexo_num}' in line_clean.lower() or
                            f'anexo nº{anexo_num}' in line_clean.lower()):
                            
                            print(f"      🎯 Chunk #{chunk['id']} (Página {chunk['page_range']})")
                            print(f"         Línea {i+1}: \"{line_clean}\"")
                            
                            # Show context (next few lines)
                            for j in range(i+1, min(i+4, len(lines))):
                                context_line = lines[j].strip()
                                if context_line and not context_line.startswith('[Page'):
                                    print(f"         Línea {j+1}: \"{context_line}\"")
                            break
        
        if not all_results:
            print(f"   ❌ ANEXO {anexo_num} no encontrado con ningún patrón")
        else:
            print(f"   ✅ ANEXO {anexo_num} encontrado en {len(all_results)} chunks únicos")
    
    # Let's also specifically search for exact page titles
    print(f"\n🔍 BUSCANDO PÁGINAS CON SOLO TÍTULOS (contenido corto):")
    print("=" * 50)
    
    cursor = conn.execute("""
        SELECT id, page_range, content, content_length
        FROM document_chunks 
        WHERE content_length < 500 
          AND content IS NOT NULL
        ORDER BY content_length
        LIMIT 20
    """)
    
    short_chunks = cursor.fetchall()
    
    for chunk in short_chunks:
        content = chunk['content'] or ''
        
        # Check if it contains ANEXO or looks like a title
        if ('anexo' in content.lower() or 
            'informe diario' in content.lower() or 
            len(content.strip().split('\n')) <= 5):  # Very few lines = might be title
            
            print(f"\n📄 Chunk #{chunk['id']} (Página {chunk['page_range']}, {chunk['content_length']} chars)")
            
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                line_clean = line.strip()
                if line_clean and not line_clean.startswith('[Page'):
                    marker = "🎯 " if 'anexo' in line_clean.lower() else "   "
                    print(f"   {marker}Línea {i}: \"{line_clean}\"")
    
    # Search for patterns that might indicate title pages
    print(f"\n🔍 BUSCANDO PATRONES DE PÁGINAS DE TÍTULO:")
    print("=" * 45)
    
    title_patterns = [
        'INFORME DIARIO',
        'Martes 25 de Febrero',
        'Miércoles 26 de Febrero', 
        'RESUMEN',
        'CRONOLOGÍA'
    ]
    
    for pattern in title_patterns:
        cursor = conn.execute("""
            SELECT id, page_range, content
            FROM document_chunks 
            WHERE content LIKE ?
            ORDER BY id
            LIMIT 5
        """, (f'%{pattern}%',))
        
        results = cursor.fetchall()
        
        if results:
            print(f"\n📋 Patrón '{pattern}': {len(results)} chunks")
            
            for chunk in results:
                lines = chunk['content'].split('\n') if chunk['content'] else []
                
                for line in lines:
                    line_clean = line.strip()
                    if pattern.lower() in line_clean.lower():
                        print(f"   Chunk #{chunk['id']} (Página {chunk['page_range']}): \"{line_clean}\"")
                        break
    
    conn.close()

if __name__ == "__main__":
    search_all_anexo_patterns()