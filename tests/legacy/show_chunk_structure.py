#!/usr/bin/env python3
"""
Show the complete searchable structure of chunks
"""

import sqlite3
from pathlib import Path
import json

def show_chunk_structure():
    """Show how chunks are structured for AI search"""
    
    conn = sqlite3.connect(str(Path(__file__).parent.parent.parent / "platform_data" / "database" / "dark_data.db"))
    conn.row_factory = sqlite3.Row
    
    print("🔍 ESTRUCTURA DE BÚSQUEDA PARA IA")
    print("=" * 60)
    
    # Get a high-quality example chunk
    cursor = conn.execute("""
        SELECT id, chunk_type, page_range, content_length, content,
               extracted_companies, extracted_technical_specs, extracted_dates,
               extracted_equipment, extracted_compliance, chunk_quality_score,
               processing_strategy
        FROM document_chunks 
        WHERE chunk_quality_score >= 0.9 AND 
              (json_array_length(extracted_companies) > 3 OR 
               json_array_length(extracted_technical_specs) > 3)
        LIMIT 1
    """)
    
    chunk = cursor.fetchone()
    if not chunk:
        print("No hay chunks de ejemplo disponibles")
        return
    
    print(f"📋 EJEMPLO: CHUNK #{chunk['id']}")
    print("=" * 40)
    
    # 1. METADATA TAGS
    print(f"\n🏷️  METADATA TAGS (para filtrado):")
    print(f"   📊 chunk_type: '{chunk['chunk_type']}'")
    print(f"   📏 page_range: '{chunk['page_range']}'")
    print(f"   📐 content_length: {chunk['content_length']}")
    print(f"   ⭐ quality_score: {chunk['chunk_quality_score']}")
    print(f"   🔧 processing_strategy: '{chunk['processing_strategy']}'")
    
    # 2. ENTITY TAGS (structured data)
    print(f"\n🔖 ENTITY TAGS (datos estructurados):")
    
    companies = json.loads(chunk['extracted_companies'] or '[]')
    if companies:
        print(f"   🏢 extracted_companies ({len(companies)}):")
        for i, company in enumerate(companies[:3]):
            print(f"      • \"{company}\"")
        if len(companies) > 3:
            print(f"      • ... y {len(companies)-3} más")
    
    specs = json.loads(chunk['extracted_technical_specs'] or '[]')
    if specs:
        print(f"   ⚡ extracted_technical_specs ({len(specs)}):")
        for i, spec in enumerate(specs[:3]):
            if isinstance(spec, dict):
                print(f"      • {spec.get('value', '')}{spec.get('unit', '')}")
            else:
                print(f"      • {spec}")
        if len(specs) > 3:
            print(f"      • ... y {len(specs)-3} más")
    
    dates = json.loads(chunk['extracted_dates'] or '[]')
    if dates:
        print(f"   📅 extracted_dates ({len(dates)}):")
        for date in dates[:3]:
            print(f"      • \"{date}\"")
    
    equipment = json.loads(chunk['extracted_equipment'] or '[]')
    if equipment:
        print(f"   ⚙️ extracted_equipment ({len(equipment)}):")
        for eq in equipment[:3]:
            print(f"      • \"{eq}\"")
    
    compliance = json.loads(chunk['extracted_compliance'] or '[]')
    if compliance:
        print(f"   📋 extracted_compliance ({len(compliance)}):")
        for comp in compliance[:2]:
            print(f"      • \"{comp}\"")
    
    # 3. FULL-TEXT SEARCH
    print(f"\n🔍 FULL-TEXT SEARCH (contenido completo):")
    content_preview = chunk['content'][:200].replace('\n', ' ').strip()
    print(f"   📝 Contenido indexado: \"{content_preview}...\"")
    
    # 4. Show FTS entry
    cursor = conn.execute("""
        SELECT extracted_text FROM chunks_fts WHERE chunk_id = ?
    """, (chunk['id'],))
    
    fts_row = cursor.fetchone()
    if fts_row and fts_row['extracted_text']:
        print(f"   🔎 Texto de búsqueda: \"{fts_row['extracted_text'][:100]}...\"")
    
    conn.close()

def show_search_capabilities():
    """Show different search methods Claude can use"""
    
    print(f"\n🎯 CAPACIDADES DE BÚSQUEDA PARA CLAUDE")
    print("=" * 50)
    
    searches = [
        {
            "type": "Por Tipo de Contenido",
            "example": "chunk_type = 'company_listing'",
            "use_case": "Claude busca: 'información de empresas'"
        },
        {
            "type": "Por Empresa Específica", 
            "example": "JSON_EXTRACT(extracted_companies, '$') LIKE '%ENEL%'",
            "use_case": "Claude busca: '¿qué dice sobre ENEL?'"
        },
        {
            "type": "Por Especificación Técnica",
            "example": "JSON_EXTRACT(extracted_technical_specs, '$') LIKE '%500 kV%'",
            "use_case": "Claude busca: 'líneas de 500 kV'"
        },
        {
            "type": "Por Calidad",
            "example": "chunk_quality_score >= 0.8",
            "use_case": "Claude necesita: solo información de alta calidad"
        },
        {
            "type": "Full-Text Search",
            "example": "chunks_fts MATCH 'protection system'",
            "use_case": "Claude busca: 'sistema de protección'"
        },
        {
            "type": "Por Rango de Páginas",
            "example": "page_range LIKE '%15-%' OR page_range LIKE '%16%'",
            "use_case": "Claude busca: 'información de las páginas 15-20'"
        }
    ]
    
    for i, search in enumerate(searches, 1):
        print(f"\n{i}. 🔍 {search['type']}")
        print(f"   SQL: {search['example']}")
        print(f"   💡 Caso de uso: {search['use_case']}")

def show_indexing_strategy():
    """Show how data is indexed for fast retrieval"""
    
    conn = sqlite3.connect(str(Path(__file__).parent.parent.parent / "platform_data" / "database" / "dark_data.db"))
    
    print(f"\n📊 ESTRATEGIA DE INDEXACIÓN")
    print("=" * 40)
    
    # Check indexes
    cursor = conn.execute("""
        SELECT name, sql FROM sqlite_master 
        WHERE type = 'index' AND name LIKE '%chunk%'
    """)
    
    indexes = cursor.fetchall()
    print(f"🗂️  Índices creados para búsqueda rápida:")
    for index in indexes:
        print(f"   • {index['name']}")
    
    # Show FTS table structure
    cursor = conn.execute("PRAGMA table_info(chunks_fts)")
    fts_columns = cursor.fetchall()
    
    print(f"\n🔎 Tabla Full-Text Search (FTS5):")
    for col in fts_columns:
        print(f"   • {col['name']}: {col['type']}")
    
    # Show statistics
    cursor = conn.execute("SELECT COUNT(*) as total FROM chunks_fts")
    fts_count = cursor.fetchone()['total']
    print(f"   📈 {fts_count} entradas indexadas para búsqueda instantánea")
    
    conn.close()

def show_claude_query_examples():
    """Show actual query examples Claude would use"""
    
    print(f"\n🤖 EJEMPLOS DE CONSULTAS QUE CLAUDE HARÍA")
    print("=" * 50)
    
    examples = [
        {
            "question": "¿Qué problemas de compliance tiene ENEL?",
            "query": """
                SELECT content FROM document_chunks 
                WHERE JSON_EXTRACT(extracted_companies, '$') LIKE '%ENEL%'
                  AND chunk_quality_score >= 0.5
                ORDER BY chunk_quality_score DESC
            """
        },
        {
            "question": "Buscar especificaciones de 500 kV",
            "query": """
                SELECT content FROM document_chunks
                WHERE JSON_EXTRACT(extracted_technical_specs, '$') LIKE '%500%kV%'
                ORDER BY chunk_quality_score DESC
            """
        },
        {
            "question": "¿Qué equipos Siemens fallaron?",
            "query": """
                SELECT content FROM chunks_fts cf
                JOIN document_chunks dc ON cf.chunk_id = dc.id
                WHERE chunks_fts MATCH 'Siemens'
                  AND dc.chunk_quality_score >= 0.6
            """
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. ❓ Pregunta: \"{example['question']}\"")
        print(f"   🔍 Query SQL que Claude ejecutaría:")
        query_lines = example['query'].strip().split('\n')
        for line in query_lines:
            print(f"      {line.strip()}")

if __name__ == "__main__":
    show_chunk_structure()
    show_search_capabilities()
    show_indexing_strategy()
    show_claude_query_examples()