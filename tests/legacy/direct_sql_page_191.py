#!/usr/bin/env python3
"""
Direct SQL access to page 191 content
"""

import sqlite3

def direct_sql_page_191():
    conn = sqlite3.connect("dark_data.db")
    
    print("🔍 ACCESO SQL DIRECTO A PÁGINA 191")
    print("=" * 50)
    
    cursor = conn.execute("""
        SELECT id, page_range, LENGTH(content) as content_length, content
        FROM document_chunks 
        WHERE page_range LIKE '%191%'
        ORDER BY id
        LIMIT 2
    """)
    
    results = cursor.fetchall()
    
    for chunk_id, page_range, length, content in results:
        print(f"\n📋 Chunk #{chunk_id} (Página {page_range})")
        print(f"📐 Longitud real: {length} caracteres")
        
        if content and length > 10:
            print(f"\n📝 CONTENIDO REAL (primeros 1500 caracteres):")
            print("─" * 60)
            print(content[:1500])
            print("─" * 60)
            
            # Look for ANEXO patterns
            lines = content.split('\n')
            anexo_lines = []
            
            for i, line in enumerate(lines):
                line_clean = line.strip()
                if 'anexo' in line_clean.lower() and ('5' in line_clean or 'v' in line_clean.lower()):
                    anexo_lines.append((i+1, line_clean))
            
            if anexo_lines:
                print(f"\n🎯 LÍNEAS CON 'ANEXO':")
                for line_num, line_content in anexo_lines:
                    print(f"   Línea {line_num}: \"{line_content}\"")
            else:
                print(f"\n❌ No se encontraron líneas con 'ANEXO 5'")
        else:
            print(f"❌ Contenido vacío o muy corto")
    
    conn.close()

def show_summary_of_found_titles():
    """Show summary of what we actually found"""
    
    print(f"\n📊 RESUMEN FINAL DE TÍTULOS ENCONTRADOS")
    print("=" * 60)
    
    print("✅ TÍTULOS DETECTADOS COMO PÁGINAS INDIVIDUALES:")
    detected_titles = [
        ("ANEXO 2", "Detalle de la generación real..."),
        ("ANEXO 4", "Detalle de los mantenimientos programados..."), 
        ("ANEXO 6", "Otros antecedentes aportados por las empresas..."),
        ("ANEXO 7", "Otros antecedentes aportados por el Coordinador..."),
        ("ANEXO 8", "Análisis operativo del esquema EDAC")
    ]
    
    for i, (anexo, title) in enumerate(detected_titles, 1):
        print(f"   {i}. {anexo}: \"{title[:50]}...\"")
    
    print(f"\n❌ TÍTULOS SOLO EN ÍNDICE (no encontrados como páginas individuales):")
    missing_titles = [
        ("ANEXO 1", "Detalle de la generación programada..."),
        ("ANEXO 3", "Detalle del Movimiento de Centrales..."), 
        ("ANEXO 5", "Informes de fallas de instalaciones...")
    ]
    
    for anexo, title in missing_titles:
        print(f"   • {anexo}: \"{title[:50]}...\"")
    
    print(f"\n💡 OBSERVACIÓN:")
    print(f"   - Tengo los títulos formales del índice para TODOS los anexos 1-8")
    print(f"   - Pero solo 5 anexos fueron encontrados como páginas individuales de título")
    print(f"   - ANEXOS 1, 3, 5 pueden estar en páginas que no se procesaron correctamente")
    print(f"   - O pueden tener un formato diferente en sus páginas de título")

if __name__ == "__main__":
    direct_sql_page_191()
    show_summary_of_found_titles()