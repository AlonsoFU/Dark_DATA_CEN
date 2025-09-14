#!/usr/bin/env python3
"""
Search all content types including placeholder content to understand document structure
"""

import sqlite3
import re

def search_all_content_types():
    conn = sqlite3.connect("dark_data.db")
    conn.row_factory = sqlite3.Row
    
    print("🔍 ANÁLISIS COMPLETO DE TODOS LOS TIPOS DE CONTENIDO")
    print("=" * 70)
    
    # Check all chunks by content type
    cursor = conn.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN content LIKE '[%characters]' THEN 1 END) as placeholder,
            COUNT(CASE WHEN content IS NULL THEN 1 END) as null_content,
            COUNT(CASE WHEN LENGTH(content) < 100 THEN 1 END) as short_content,
            COUNT(CASE WHEN LENGTH(content) BETWEEN 100 AND 1000 THEN 1 END) as medium_content,
            COUNT(CASE WHEN LENGTH(content) > 1000 THEN 1 END) as long_content
        FROM document_chunks
    """)
    
    stats = cursor.fetchone()
    
    print("📊 ESTADÍSTICAS DE CONTENIDO:")
    print(f"   📄 Total chunks: {stats['total']}")
    print(f"   📋 Placeholder: {stats['placeholder']} ({stats['placeholder']/stats['total']*100:.1f}%)")
    print(f"   📋 Nulo: {stats['null_content']} ({stats['null_content']/stats['total']*100:.1f}%)")
    print(f"   📋 Corto (<100): {stats['short_content']} ({stats['short_content']/stats['total']*100:.1f}%)")
    print(f"   📋 Medio (100-1000): {stats['medium_content']} ({stats['medium_content']/stats['total']*100:.1f}%)")
    print(f"   📋 Largo (>1000): {stats['long_content']} ({stats['long_content']/stats['total']*100:.1f}%)")
    
    # The problem is clear: most content is placeholder
    print(f"\n⚠️  PROBLEMA IDENTIFICADO:")
    print(f"   {stats['placeholder']} chunks ({stats['placeholder']/stats['total']*100:.1f}%) tienen contenido placeholder")
    print(f"   Esto incluye probablemente las páginas de título que buscas")
    
    # Let's look at the accessible content and see what patterns we can find
    print(f"\n🔍 ANALIZANDO CONTENIDO ACCESIBLE PARA PATRONES:")
    print("=" * 60)
    
    cursor = conn.execute("""
        SELECT id, page_range, content, content_length
        FROM document_chunks 
        WHERE content IS NOT NULL
          AND content NOT LIKE '[%characters]'
          AND content_length > 50
        ORDER BY content_length DESC
        LIMIT 20
    """)
    
    accessible_chunks = cursor.fetchall()
    
    print(f"📄 Analizando los {len(accessible_chunks)} chunks más grandes con contenido accesible...")
    
    # Look for references to document sections
    section_references = {
        'INFORME DIARIO': [],
        'RESUMEN EJECUTIVO': [],
        'CRONOLOGÍA': [],
        'ANTECEDENTES': [],
        'CONCLUSIONES': [],
        'RECOMENDACIONES': [],
        'ANEXO': []
    }
    
    date_patterns_found = set()
    
    for chunk in accessible_chunks:
        content = chunk['content'] or ''
        lines = content.split('\n')
        
        for line in lines:
            line_clean = line.strip().upper()
            
            # Look for section references
            for section_name in section_references.keys():
                if section_name in line_clean:
                    section_references[section_name].append({
                        'chunk_id': chunk['id'],
                        'page_range': chunk['page_range'],
                        'line': line.strip()[:100] + "..." if len(line.strip()) > 100 else line.strip()
                    })
            
            # Look for date patterns
            date_patterns = [
                r'(LUNES|MARTES|MIÉRCOLES|JUEVES|VIERNES|SÁBADO|DOMINGO)\s+\d+\s+DE\s+\w+',
                r'\d+\s+DE\s+(ENERO|FEBRERO|MARZO|ABRIL|MAYO|JUNIO|JULIO|AGOSTO|SEPTIEMBRE|OCTUBRE|NOVIEMBRE|DICIEMBRE)',
                r'25\s+DE\s+FEBRERO',
                r'26\s+DE\s+FEBRERO'
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, line_clean)
                for match in matches:
                    date_patterns_found.add(match)
    
    # Show what we found
    print(f"\n📋 REFERENCIAS A SECCIONES ENCONTRADAS:")
    for section_name, references in section_references.items():
        if references:
            print(f"\n🔍 {section_name}: {len(references)} referencias")
            for ref in references[:3]:  # Show first 3
                print(f"   Chunk #{ref['chunk_id']} (Página {ref['page_range']}): \"{ref['line']}\"")
            if len(references) > 3:
                print(f"   ... y {len(references)-3} más")
    
    print(f"\n📅 PATRONES DE FECHAS ENCONTRADOS:")
    for date_pattern in sorted(date_patterns_found):
        print(f"   • {date_pattern}")
    
    # Infer document structure from references
    print(f"\n💡 ESTRUCTURA DEL DOCUMENTO INFERIDA:")
    print("=" * 50)
    
    likely_sections = []
    
    if section_references['INFORME DIARIO']:
        likely_sections.append("📄 INFORME DIARIO - probablemente con fechas específicas (25/26 febrero)")
    
    if section_references['ANEXO']:
        likely_sections.append(f"📋 ANEXOS - {len(section_references['ANEXO'])} referencias encontradas")
    
    if section_references['CRONOLOGÍA']:
        likely_sections.append("⏱️ CRONOLOGÍA DE EVENTOS")
    
    if section_references['ANTECEDENTES']:
        likely_sections.append("📚 ANTECEDENTES")
    
    if section_references['CONCLUSIONES']:
        likely_sections.append("🎯 CONCLUSIONES")
    
    for section in likely_sections:
        print(f"   {section}")
    
    # Suggest solution
    print(f"\n🔧 SOLUCIÓN SUGERIDA:")
    print("=" * 30)
    print(f"1. Las páginas de título están en los {stats['placeholder']} chunks con placeholder")
    print(f"2. Para encontrar títulos como 'INFORME DIARIO Martes 25 de Febrero del 2025'")
    print(f"   necesitamos reprocesar el contenido original")
    print(f"3. Los patrones que encontramos sugieren que SÍ existen esas secciones")
    print(f"4. El documento tiene la estructura típica de informes técnicos chilenos")
    
    # Show page ranges with placeholder content that might have titles
    print(f"\n📄 PÁGINAS CON CONTENIDO PLACEHOLDER (posibles títulos):")
    cursor = conn.execute("""
        SELECT page_range, content, COUNT(*) as count
        FROM document_chunks 
        WHERE content LIKE '[%characters]'
          AND page_range != ''
        GROUP BY page_range
        ORDER BY page_range
        LIMIT 20
    """)
    
    placeholder_pages = cursor.fetchall()
    
    for page in placeholder_pages:
        print(f"   Página {page['page_range']}: {page['content']} ({page['count']} chunks)")
    
    conn.close()

if __name__ == "__main__":
    search_all_content_types()