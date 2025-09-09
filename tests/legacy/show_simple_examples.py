#!/usr/bin/env python3
"""
Simple chunk examples viewer
"""

import sqlite3
import json

def show_examples():
    conn = sqlite3.connect("dark_data.db")
    conn.row_factory = sqlite3.Row
    
    print("📄 EJEMPLOS REALES DE CHUNKS PROCESADOS")
    print("=" * 60)
    
    # Get a variety of examples
    examples = [
        ("Alta Calidad - Rica en Empresas", "chunk_quality_score >= 0.9 AND json_array_length(extracted_companies) > 10"),
        ("Alta Calidad - Rica en Specs Técnicas", "chunk_quality_score >= 0.9 AND json_array_length(extracted_technical_specs) > 5"),
        ("Calidad Media", "chunk_quality_score BETWEEN 0.4 AND 0.7"),
        ("Baja Calidad", "chunk_quality_score < 0.4")
    ]
    
    for title, condition in examples:
        print(f"\n🔍 {title.upper()}")
        print("-" * 50)
        
        cursor = conn.execute(f"""
            SELECT id, chunk_type, page_range, content_length, content,
                   extracted_companies, extracted_technical_specs, 
                   chunk_quality_score
            FROM document_chunks 
            WHERE {condition}
            LIMIT 1
        """)
        
        chunk = cursor.fetchone()
        if chunk:
            show_chunk(chunk)
        else:
            print("   (No hay ejemplos de este tipo)")
    
    conn.close()

def show_chunk(chunk):
    """Show chunk details clearly"""
    
    # Basic info
    print(f"📋 Chunk #{chunk['id']} ({chunk['chunk_type']})")
    print(f"   📏 Páginas: {chunk['page_range']}")
    print(f"   📊 Tamaño: {chunk['content_length']} caracteres")
    print(f"   ⭐ Calidad: {chunk['chunk_quality_score']:.2f}/1.0")
    
    # Extracted entities
    companies = json.loads(chunk['extracted_companies'] or '[]')
    specs = json.loads(chunk['extracted_technical_specs'] or '[]')
    
    if companies:
        print(f"   🏢 Empresas encontradas ({len(companies)}): {', '.join(companies[:3])}...")
    
    if specs:
        spec_strs = []
        for spec in specs[:3]:
            if isinstance(spec, dict):
                spec_strs.append(f"{spec.get('value', '')}{spec.get('unit', '')}")
            else:
                spec_strs.append(str(spec))
        print(f"   ⚡ Especificaciones técnicas ({len(specs)}): {', '.join(spec_strs)}...")
    
    # Content sample
    content = chunk['content'] or ''
    lines = content.split('\n')
    meaningful_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('[Page')]
    
    print(f"   📝 Muestra del contenido:")
    for line in meaningful_lines[:3]:
        if len(line) > 60:
            print(f"      '{line[:60]}...'")
        else:
            print(f"      '{line}'")
    
    # Quality explanation
    print(f"   🎯 ¿Por qué esta calidad?")
    explain_quality(chunk['content_length'], len(companies) + len(specs), chunk['chunk_type'])

def explain_quality(length, entities, chunk_type):
    """Explain quality score"""
    
    points = []
    
    if 1000 <= length <= 5000:
        points.append("Tamaño óptimo (+0.3)")
    elif length > 500:
        points.append("Tamaño adecuado (+0.1)")
    else:
        points.append("Muy corto (+0.0)")
    
    if entities > 10:
        points.append("Muchas entidades (+0.4)")
    elif entities > 5:
        points.append("Algunas entidades (+0.2)")
    elif entities > 0:
        points.append("Pocas entidades (+0.1)")
    else:
        points.append("Sin entidades (+0.0)")
    
    if chunk_type != 'unknown':
        points.append("Tipo claro (+0.2)")
    else:
        points.append("Tipo unclear (+0.0)")
    
    print(f"      {' | '.join(points)}")

if __name__ == "__main__":
    show_examples()