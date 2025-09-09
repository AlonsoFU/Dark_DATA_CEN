#!/usr/bin/env python3
"""
Check if annexes structure was detected in chunks
"""

import sqlite3
import json
import re

def check_annexes():
    conn = sqlite3.connect("dark_data.db")
    conn.row_factory = sqlite3.Row
    
    print("📋 ANÁLISIS DE ESTRUCTURA DE ANEXOS")
    print("=" * 50)
    
    # Look for chunks with annex references
    cursor = conn.execute("""
        SELECT id, chunk_type, page_range, content, 
               chunk_quality_score
        FROM document_chunks 
        WHERE content LIKE '%ANEXO%' OR content LIKE '%Anexo%'
        ORDER BY id
        LIMIT 10
    """)
    
    annexes_chunks = cursor.fetchall()
    
    print(f"🔍 Chunks que mencionan 'ANEXO': {len(annexes_chunks)}")
    
    # Analyze annex patterns
    annex_patterns = {}
    
    for chunk in annexes_chunks:
        content = chunk['content'] or ''
        
        # Look for annex patterns
        patterns = [
            r'ANEXO\s+([A-Z0-9]+)',
            r'Anexo\s+([A-Z0-9]+)',
            r'ANEXO\s+([IVX]+)',
            r'RESUMEN\s+DIARIO',
            r'OPERACION\s+DEL\s+SEN'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                pattern_key = pattern.replace(r'\s+', ' ').replace('([A-Z0-9]+)', 'X').replace('([IVX]+)', 'X')
                if pattern_key not in annex_patterns:
                    annex_patterns[pattern_key] = []
                annex_patterns[pattern_key].extend(matches)
    
    print(f"\n📊 PATRONES DE ANEXOS DETECTADOS:")
    for pattern, matches in annex_patterns.items():
        unique_matches = list(set(matches))
        print(f"   {pattern}: {unique_matches[:5]}...")
    
    # Show sample content from annexes
    print(f"\n📄 MUESTRA DE CONTENIDO DE ANEXOS:")
    for i, chunk in enumerate(annexes_chunks[:3], 1):
        content = chunk['content'][:300].replace('\n', ' ').strip()
        print(f"\n{i}. Chunk #{chunk['id']} (Páginas: {chunk['page_range']})")
        print(f"   Contenido: \"{content}...\"")
        
        # Try to identify the annex
        annex_id = identify_annex_section(chunk['content'])
        if annex_id:
            print(f"   🏷️  Anexo identificado: {annex_id}")
    
    conn.close()

def identify_annex_section(content):
    """Try to identify which annex section this belongs to"""
    
    # Common annex patterns in technical documents
    patterns = {
        'ANEXO A': r'ANEXO\s+A|Anexo\s+A',
        'ANEXO B': r'ANEXO\s+B|Anexo\s+B', 
        'ANEXO I': r'ANEXO\s+I[^IV]|Anexo\s+I[^IV]',
        'ANEXO II': r'ANEXO\s+II|Anexo\s+II',
        'ANEXO III': r'ANEXO\s+III|Anexo\s+III',
        'RESUMEN DIARIO': r'RESUMEN\s+DIARIO',
        'OPERACION SEN': r'OPERACION\s+DEL\s+SEN',
        'DOCUMENTOS': r'DOCUMENTOS?\s+ADJUNTOS?',
        'CRONOGRAMA': r'CRONOGRAMA|TIMELINE',
        'COMUNICACIONES': r'COMUNICACIONES?|CORRESPONDENCE'
    }
    
    for annex_name, pattern in patterns.items():
        if re.search(pattern, content, re.IGNORECASE):
            return annex_name
    
    return None

def suggest_annex_tagging():
    """Suggest how to add annex tagging to chunks"""
    
    print(f"\n💡 SUGERENCIA: MEJORAR TAGGING DE ANEXOS")
    print("=" * 45)
    
    print("🔧 Para mejorar la estructura, podríamos agregar:")
    print("   • annex_section: 'ANEXO_A', 'ANEXO_B', etc.")
    print("   • annex_topic: 'RESUMEN_DIARIO', 'OPERACION_SEN', etc.")
    print("   • document_section: 'main_report', 'annexes'")
    
    print(f"\n📊 Esto permitiría búsquedas como:")
    searches = [
        "Claude: '¿Qué dice el Anexo A?' → WHERE annex_section = 'ANEXO_A'",
        "Claude: 'Resumen diario de operación' → WHERE annex_topic = 'RESUMEN_DIARIO'",
        "Claude: 'Solo el reporte principal' → WHERE document_section = 'main_report'"
    ]
    
    for search in searches:
        print(f"   🔍 {search}")

def check_current_structure():
    """Check what structure we currently have"""
    
    conn = sqlite3.connect("dark_data.db")
    conn.row_factory = sqlite3.Row
    
    print(f"\n📊 ESTRUCTURA ACTUAL VS ANEXOS")
    print("=" * 40)
    
    # Check page distribution
    cursor = conn.execute("""
        SELECT page_range, COUNT(*) as chunk_count,
               chunk_type, AVG(chunk_quality_score) as avg_quality
        FROM document_chunks 
        WHERE page_range != ''
        GROUP BY chunk_type
        ORDER BY chunk_count DESC
    """)
    
    results = cursor.fetchall()
    
    print("📋 Distribución por tipo de contenido:")
    for row in results:
        print(f"   {row['chunk_type']}: {row['chunk_count']} chunks (calidad avg: {row['avg_quality']:.2f})")
    
    # Check if we can infer annex structure from page numbers
    cursor = conn.execute("""
        SELECT page_range, content
        FROM document_chunks 
        WHERE content LIKE '%ANEXO%' OR content LIKE '%Anexo%'
        ORDER BY CAST(SUBSTR(page_range, 1, INSTR(page_range, '-')-1) AS INTEGER)
        LIMIT 5
    """)
    
    print(f"\n📄 Chunks con referencias a anexos (por orden de página):")
    annexes_content = cursor.fetchall()
    
    for i, chunk in enumerate(annexes_content, 1):
        content_preview = chunk['content'][:150].replace('\n', ' ').strip()
        print(f"   {i}. Página {chunk['page_range']}: \"{content_preview}...\"")
    
    conn.close()

if __name__ == "__main__":
    check_annexes()
    suggest_annex_tagging()
    check_current_structure()