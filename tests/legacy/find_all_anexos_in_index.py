#!/usr/bin/env python3
"""
Find all annexes from the index section
"""

import sqlite3
from pathlib import Path

def find_all_anexos():
    conn = sqlite3.connect(str(Path(__file__).parent.parent.parent / "platform_data" / "database" / "dark_data.db"))
    conn.row_factory = sqlite3.Row
    
    print("🔍 ENCONTRANDO TODOS LOS ANEXOS DEL ÍNDICE")
    print("=" * 60)
    
    # Get the chunk with the index
    cursor = conn.execute("""
        SELECT id, page_range, content
        FROM document_chunks 
        WHERE content LIKE '%Anexo N°1%' AND content LIKE '%Anexo N°2%'
        ORDER BY id
        LIMIT 1
    """)
    
    chunk = cursor.fetchone()
    if chunk:
        print(f"📄 Chunk #{chunk['id']} - Sección de Índice")
        
        lines = chunk['content'].split('\n')
        
        # Find all lines with Anexo patterns
        annexes_found = {}
        current_title = ""
        
        for i, line in enumerate(lines):
            line_clean = line.strip()
            
            # Check if line contains Anexo N°
            if 'anexo n°' in line_clean.lower():
                # Extract number
                import re
                match = re.search(r'anexo n°(\d+)', line_clean.lower())
                if match:
                    anexo_num = match.group(1)
                    
                    # Get title from previous line(s)
                    title_parts = []
                    
                    # Check current line for title before (Anexo N°...)
                    title_before = line_clean.split('(')[0].strip()
                    if title_before.startswith('•'):
                        title_before = title_before[1:].strip()
                    if title_before:
                        title_parts.append(title_before)
                    
                    # Check if title continues in previous line
                    if i > 0:
                        prev_line = lines[i-1].strip()
                        # If previous line doesn't contain anexo and looks like continuation
                        if 'anexo' not in prev_line.lower() and len(prev_line) > 10:
                            if prev_line.startswith('•'):
                                # This is the start of the title
                                title_parts = [prev_line[1:].strip()] + title_parts
                            elif not prev_line.endswith('.'):
                                # This might be a continuation
                                title_parts = [prev_line] + title_parts
                    
                    complete_title = ' '.join(title_parts).strip()
                    if complete_title:
                        annexes_found[anexo_num] = complete_title
                        
                        print(f"\n📋 ANEXO {anexo_num}:")
                        print(f"   📝 \"{complete_title}\"")
                        
                        # Show the raw lines for context
                        print(f"   📄 Líneas originales:")
                        if i > 0:
                            print(f"      {i}: {lines[i-1].strip()}")
                        print(f"   >>> {i+1}: {line_clean}")
        
        print(f"\n✅ ANEXOS ENCONTRADOS EN ÍNDICE: {len(annexes_found)}")
        return annexes_found
    
    conn.close()
    return {}

def update_detected_annexes(annexes_dict):
    """Update database with found annexes"""
    
    conn = sqlite3.connect(str(Path(__file__).parent.parent.parent / "platform_data" / "database" / "dark_data.db"))
    
    print(f"\n🔧 ACTUALIZANDO BASE DE DATOS CON ANEXOS ENCONTRADOS")
    print("=" * 60)
    
    for anexo_num, title in annexes_dict.items():
        # Clean up title
        clean_title = title.replace('•', '').strip()
        
        print(f"\n📋 Procesando ANEXO {anexo_num}:")
        print(f"   📝 \"{clean_title}\"")
        
        # First check if this anexo already exists
        cursor = conn.execute("""
            SELECT COUNT(*) as count FROM document_chunks 
            WHERE specific_annex_number = ?
        """, (anexo_num,))
        
        existing_count = cursor.fetchone()[0]
        
        if existing_count == 0:
            print(f"   🔍 Anexo {anexo_num} no detectado, buscando contenido...")
            
            # Try to find content that belongs to this anexo
            # Look for chunks that mention this anexo number
            cursor = conn.execute("""
                SELECT id, page_range, content
                FROM document_chunks 
                WHERE content LIKE ? OR content LIKE ?
                ORDER BY id
                LIMIT 5
            """, (f'%ANEXO {anexo_num}%', f'%Anexo {anexo_num}%'))
            
            potential_chunks = cursor.fetchall()
            
            if potential_chunks:
                print(f"   ✅ Encontrado {len(potential_chunks)} chunk(s) potenciales")
                
                # For now, just mark the first one as header
                first_chunk = potential_chunks[0]
                
                # Determine theme based on title
                theme = 'general_information'
                if 'generación' in clean_title.lower():
                    theme = 'generation_programming'
                elif 'movimiento' in clean_title.lower() or 'cdc' in clean_title.lower():
                    theme = 'operational_data'
                elif 'mantenimiento' in clean_title.lower():
                    theme = 'equipment_details'
                
                # Update this chunk
                conn.execute("""
                    UPDATE document_chunks 
                    SET specific_annex_number = ?,
                        specific_annex_title = ?,
                        annex_theme = ?,
                        is_annex_header = 1
                    WHERE id = ?
                """, (anexo_num, clean_title, theme, first_chunk[0]))
                
                print(f"   ✅ Actualizado chunk #{first_chunk[0]} como cabecera del ANEXO {anexo_num}")
            else:
                print(f"   ❌ No se encontró contenido para ANEXO {anexo_num}")
        else:
            # Update existing with correct title
            conn.execute("""
                UPDATE document_chunks 
                SET specific_annex_title = ?
                WHERE specific_annex_number = ?
            """, (clean_title, anexo_num))
            
            print(f"   ✅ Actualizado título del ANEXO {anexo_num} existente")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    found_annexes = find_all_anexos()
    if found_annexes:
        update_detected_annexes(found_annexes)