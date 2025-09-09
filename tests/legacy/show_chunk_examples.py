#!/usr/bin/env python3
"""
Show specific examples of processed chunks
"""

import sqlite3
import json

def show_chunk_examples():
    """Show real chunk examples from database"""
    
    conn = sqlite3.connect("dark_data.db")
    conn.row_factory = sqlite3.Row
    
    print("📄 EXAMPLES OF PROCESSED CHUNKS")
    print("=" * 60)
    
    # Example 1: High quality company chunk
    print("\n🟢 EXAMPLE 1: HIGH QUALITY COMPANY CHUNK")
    print("-" * 50)
    
    cursor = conn.execute("""
        SELECT id, chunk_type, page_range, content_length, content,
               extracted_companies, extracted_technical_specs, extracted_dates,
               chunk_quality_score
        FROM document_chunks 
        WHERE chunk_type = 'company_listing' OR 
              (json_array_length(extracted_companies) > 3 AND chunk_quality_score > 0.8)
        ORDER BY chunk_quality_score DESC, json_array_length(extracted_companies) DESC
        LIMIT 1
    """)
    
    chunk = cursor.fetchone()
    if chunk:
        show_chunk_details(chunk, "High quality - many companies")
    
    # Example 2: Technical specifications chunk
    print("\n🟡 EXAMPLE 2: TECHNICAL SPECIFICATIONS CHUNK")
    print("-" * 50)
    
    cursor = conn.execute("""
        SELECT id, chunk_type, page_range, content_length, content,
               extracted_companies, extracted_technical_specs, extracted_dates,
               chunk_quality_score
        FROM document_chunks 
        WHERE chunk_type = 'technical_specifications' OR
              json_array_length(extracted_technical_specs) > 5
        ORDER BY json_array_length(extracted_technical_specs) DESC
        LIMIT 1
    """)
    
    chunk = cursor.fetchone()
    if chunk:
        show_chunk_details(chunk, "Technical specifications rich")
    
    # Example 3: Structured section
    print("\n🔵 EXAMPLE 3: STRUCTURED SECTION CHUNK")
    print("-" * 50)
    
    cursor = conn.execute("""
        SELECT id, chunk_type, page_range, content_length, content,
               extracted_companies, extracted_technical_specs, extracted_dates,
               chunk_quality_score
        FROM document_chunks 
        WHERE chunk_type = 'structured_section'
        ORDER BY chunk_quality_score DESC
        LIMIT 1
    """)
    
    chunk = cursor.fetchone()
    if chunk:
        show_chunk_details(chunk, "Well-structured content")
    
    # Example 4: Low quality/sparse chunk
    print("\n🔴 EXAMPLE 4: LOW QUALITY CHUNK")
    print("-" * 50)
    
    cursor = conn.execute("""
        SELECT id, chunk_type, page_range, content_length, content,
               extracted_companies, extracted_technical_specs, extracted_dates,
               chunk_quality_score
        FROM document_chunks 
        WHERE chunk_quality_score < 0.3
        ORDER BY chunk_quality_score ASC
        LIMIT 1
    """)
    
    chunk = cursor.fetchone()
    if chunk:
        show_chunk_details(chunk, "Low quality - sparse content")
    
    # Example 5: Mixed content chunk
    print("\n🟠 EXAMPLE 5: MIXED CONTENT CHUNK")
    print("-" * 50)
    
    cursor = conn.execute("""
        SELECT id, chunk_type, page_range, content_length, content,
               extracted_companies, extracted_technical_specs, extracted_dates,
               chunk_quality_score
        FROM document_chunks 
        WHERE chunk_type = 'mixed_content'
        ORDER BY chunk_quality_score DESC
        LIMIT 1
    """)
    
    chunk = cursor.fetchone()
    if chunk:
        show_chunk_details(chunk, "Mixed content type")
    
    conn.close()

def show_chunk_details(chunk, description):
    """Show detailed information about a specific chunk"""
    
    print(f"📋 Chunk #{chunk['id']} - {description}")
    print(f"   📊 Type: {chunk['chunk_type']}")
    print(f"   📏 Pages: {chunk['page_range']}")
    print(f"   📐 Length: {chunk['content_length']} characters")
    print(f"   ⭐ Quality Score: {chunk['chunk_quality_score']:.2f}")
    
    # Show extracted entities
    companies = json.loads(chunk['extracted_companies'] or '[]')
    specs = json.loads(chunk['extracted_technical_specs'] or '[]')
    dates = json.loads(chunk['extracted_dates'] or '[]')
    
    print(f"\n🔍 EXTRACTED ENTITIES:")
    if companies:
        print(f"   🏢 Companies ({len(companies)}): {', '.join(companies[:3])}{'...' if len(companies) > 3 else ''}")
    
    if specs:
        spec_text = []
        for spec in specs[:3]:
            if isinstance(spec, dict):
                spec_text.append(f"{spec.get('value', '')}{spec.get('unit', '')}")
            else:
                spec_text.append(str(spec))
        print(f"   ⚡ Tech Specs ({len(specs)}): {', '.join(spec_text)}{'...' if len(specs) > 3 else ''}")
    
    if dates:
        print(f"   📅 Dates ({len(dates)}): {', '.join(dates[:3])}{'...' if len(dates) > 3 else ''}")
    
    # Show content preview
    content = chunk['content'] or ''
    print(f"\n📝 CONTENT PREVIEW:")
    print("   " + "-" * 40)
    
    # Show first 300 characters
    preview = content.replace('\n', ' ').strip()
    if len(preview) > 300:
        print(f"   {preview[:300]}...")
    else:
        print(f"   {preview}")
    
    print("   " + "-" * 40)
    
    # Analysis of why this quality score
    print(f"\n🎯 QUALITY ANALYSIS:")
    analyze_quality_score(chunk)

def analyze_quality_score(chunk):
    """Analyze why a chunk got its quality score"""
    
    content_length = chunk['content_length']
    companies = json.loads(chunk['extracted_companies'] or '[]')
    specs = json.loads(chunk['extracted_technical_specs'] or '[]')
    dates = json.loads(chunk['extracted_dates'] or '[]')
    
    total_entities = len(companies) + len(specs) + len(dates)
    
    print(f"   📏 Content length: {content_length} chars", end="")
    if 1000 <= content_length <= 5000:
        print(" → +0.3 points (optimal size)")
    elif content_length > 500:
        print(" → +0.1 points (adequate size)")
    else:
        print(" → +0.0 points (too short)")
    
    print(f"   🔍 Total entities: {total_entities}", end="")
    if total_entities > 10:
        print(" → +0.4 points (very rich)")
    elif total_entities > 5:
        print(" → +0.2 points (moderately rich)")
    elif total_entities > 0:
        print(" → +0.1 points (some info)")
    else:
        print(" → +0.0 points (no extractable info)")
    
    print(f"   📋 Content type: {chunk['chunk_type']}", end="")
    if chunk['chunk_type'] != 'unknown':
        print(" → +0.2 points (consistent type)")
    else:
        print(" → +0.0 points (unclear type)")

def show_comparison():
    """Show side-by-side comparison"""
    
    conn = sqlite3.connect("dark_data.db")
    conn.row_factory = sqlite3.Row
    
    print(f"\n📊 QUALITY COMPARISON")
    print("=" * 80)
    
    cursor = conn.execute("""
        SELECT 'HIGH' as category, id, chunk_type, content_length, 
               json_array_length(extracted_companies) as companies_count,
               json_array_length(extracted_technical_specs) as specs_count,
               chunk_quality_score
        FROM document_chunks 
        WHERE chunk_quality_score >= 0.8
        ORDER BY chunk_quality_score DESC
        LIMIT 3
        
        UNION ALL
        
        SELECT 'LOW' as category, id, chunk_type, content_length,
               json_array_length(extracted_companies) as companies_count,
               json_array_length(extracted_technical_specs) as specs_count,
               chunk_quality_score
        FROM document_chunks 
        WHERE chunk_quality_score <= 0.3
        ORDER BY chunk_quality_score ASC
        LIMIT 3
    """)
    
    results = cursor.fetchall()
    
    print(f"{'Category':<8} {'Chunk#':<8} {'Type':<20} {'Length':<8} {'Companies':<10} {'Specs':<8} {'Quality':<8}")
    print("-" * 80)
    
    for row in results:
        print(f"{row['category']:<8} #{row['id']:<7} {row['chunk_type']:<20} {row['content_length']:<8} "
              f"{row['companies_count'] or 0:<10} {row['specs_count'] or 0:<8} {row['chunk_quality_score']:<8.2f}")
    
    conn.close()

if __name__ == "__main__":
    show_chunk_examples()
    show_comparison()