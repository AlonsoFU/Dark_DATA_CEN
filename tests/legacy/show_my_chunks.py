#!/usr/bin/env python3
"""
Show specific chunks with full content
"""

import sqlite3
from pathlib import Path
import json

def show_my_chunks():
    conn = sqlite3.connect(str(Path(__file__).parent.parent.parent / "platform_data" / "database" / "dark_data.db"))
    conn.row_factory = sqlite3.Row
    
    print("📄 TUS CHUNKS REALES - CONTENIDO COMPLETO")
    print("=" * 70)
    
    # HIGH QUALITY CHUNK
    print("\n🟢 CHUNK DE ALTA CALIDAD")
    print("=" * 50)
    
    cursor = conn.execute("""
        SELECT id, chunk_type, page_range, content_length, content,
               extracted_companies, extracted_technical_specs, extracted_dates,
               chunk_quality_score
        FROM document_chunks 
        WHERE chunk_quality_score >= 0.9 AND content_length > 2000
        ORDER BY chunk_quality_score DESC, content_length DESC
        LIMIT 1
    """)
    
    high_chunk = cursor.fetchone()
    if high_chunk:
        show_full_chunk(high_chunk, "ALTA CALIDAD")
    
    print("\n" + "="*70)
    
    # LOW QUALITY CHUNK  
    print("\n🔴 CHUNK DE BAJA CALIDAD")
    print("=" * 50)
    
    cursor = conn.execute("""
        SELECT id, chunk_type, page_range, content_length, content,
               extracted_companies, extracted_technical_specs, extracted_dates,
               chunk_quality_score
        FROM document_chunks 
        WHERE chunk_quality_score < 0.4
        ORDER BY chunk_quality_score ASC
        LIMIT 1
    """)
    
    low_chunk = cursor.fetchone()
    if low_chunk:
        show_full_chunk(low_chunk, "BAJA CALIDAD")
    
    conn.close()

def show_full_chunk(chunk, quality_label):
    """Show complete chunk details"""
    
    print(f"📋 CHUNK #{chunk['id']} - {quality_label}")
    print(f"📊 Tipo: {chunk['chunk_type']}")
    print(f"📏 Páginas: {chunk['page_range']}")
    print(f"📐 Tamaño: {chunk['content_length']} caracteres")
    print(f"⭐ Calidad: {chunk['chunk_quality_score']:.2f}/1.0")
    
    # Show extracted entities
    companies = json.loads(chunk['extracted_companies'] or '[]')
    specs = json.loads(chunk['extracted_technical_specs'] or '[]')
    dates = json.loads(chunk['extracted_dates'] or '[]')
    
    print(f"\n🔍 ENTIDADES EXTRAÍDAS:")
    print(f"   🏢 Empresas: {len(companies)}")
    if companies:
        for i, company in enumerate(companies[:5]):
            print(f"      {i+1}. {company}")
        if len(companies) > 5:
            print(f"      ... y {len(companies)-5} más")
    
    print(f"   ⚡ Specs Técnicas: {len(specs)}")
    if specs:
        for i, spec in enumerate(specs[:5]):
            if isinstance(spec, dict):
                print(f"      {i+1}. {spec.get('value', '')}{spec.get('unit', '')}")
            else:
                print(f"      {i+1}. {spec}")
        if len(specs) > 5:
            print(f"      ... y {len(specs)-5} más")
    
    print(f"   📅 Fechas: {len(dates)}")
    if dates:
        for i, date in enumerate(dates[:3]):
            print(f"      {i+1}. {date}")
        if len(dates) > 3:
            print(f"      ... y {len(dates)-3} más")
    
    # Show FULL content
    print(f"\n📝 CONTENIDO COMPLETO:")
    print("─" * 60)
    content = chunk['content'] or ''
    
    # Clean up the content for better display
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if line:
            print(f"   {line}")
    
    print("─" * 60)
    
    # Quality analysis
    print(f"\n🎯 ANÁLISIS DE CALIDAD:")
    total_entities = len(companies) + len(specs) + len(dates)
    
    print(f"   📏 Longitud: {chunk['content_length']} caracteres", end="")
    if 1000 <= chunk['content_length'] <= 5000:
        print(" ✅ (+0.3 puntos - tamaño perfecto)")
    elif chunk['content_length'] > 500:
        print(" 🟡 (+0.1 puntos - tamaño adecuado)")
    else:
        print(" ❌ (+0.0 puntos - muy corto)")
    
    print(f"   🔍 Entidades totales: {total_entities}", end="")
    if total_entities > 10:
        print(" ✅ (+0.4 puntos - muy rico en datos)")
    elif total_entities > 5:
        print(" 🟡 (+0.2 puntos - moderadamente rico)")
    elif total_entities > 0:
        print(" 🟠 (+0.1 puntos - algo de info)")
    else:
        print(" ❌ (+0.0 puntos - sin datos útiles)")
    
    print(f"   📋 Tipo de contenido: {chunk['chunk_type']}", end="")
    if chunk['chunk_type'] != 'unknown':
        print(" ✅ (+0.2 puntos - tipo claro)")
    else:
        print(" ❌ (+0.0 puntos - tipo confuso)")
    
    print(f"\n💡 UTILIDAD PARA CLAUDE:")
    if chunk['chunk_quality_score'] >= 0.7:
        print("   ✅ MUY ÚTIL - Claude puede extraer mucha información")
        print("   ✅ Perfecto para responder preguntas específicas")
    elif chunk['chunk_quality_score'] >= 0.4:
        print("   🟡 MODERADAMENTE ÚTIL - Algo de información")
        print("   🟡 Puede complementar otros chunks")
    else:
        print("   ❌ POCO ÚTIL - Información mínima o irrelevante")
        print("   ❌ Claude probablemente lo ignorará")

if __name__ == "__main__":
    show_my_chunks()