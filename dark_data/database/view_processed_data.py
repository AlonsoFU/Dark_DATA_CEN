#!/usr/bin/env python3
"""
View processed chunk data from database
"""

import sqlite3
import json
from pathlib import Path

def view_chunk_statistics():
    """Show statistics about processed chunks"""
    
    if not Path("dark_data.db").exists():
        print("❌ Database not found. Run integrate_chunks_to_db.py first")
        return
    
    conn = sqlite3.connect("dark_data.db")
    conn.row_factory = sqlite3.Row
    
    print("📊 PROCESSED CHUNK STATISTICS")
    print("=" * 50)
    
    # Total chunks
    cursor = conn.execute("SELECT COUNT(*) as total FROM document_chunks")
    total = cursor.fetchone()['total']
    print(f"📄 Total chunks: {total}")
    
    # By content type
    print(f"\n📋 Chunks by Content Type:")
    cursor = conn.execute("""
        SELECT chunk_type, COUNT(*) as count, 
               AVG(content_length) as avg_length,
               AVG(chunk_quality_score) as avg_quality
        FROM document_chunks 
        GROUP BY chunk_type 
        ORDER BY count DESC
    """)
    
    for row in cursor:
        print(f"   {row['chunk_type']}: {row['count']} chunks")
        print(f"      Avg length: {row['avg_length']:.0f} chars")
        print(f"      Avg quality: {row['avg_quality']:.2f}")
    
    # Quality distribution
    print(f"\n⭐ Quality Score Distribution:")
    cursor = conn.execute("""
        SELECT 
            CASE 
                WHEN chunk_quality_score >= 0.7 THEN 'High (0.7+)'
                WHEN chunk_quality_score >= 0.4 THEN 'Medium (0.4-0.7)'
                ELSE 'Low (<0.4)'
            END as quality_range,
            COUNT(*) as count
        FROM document_chunks 
        GROUP BY quality_range
        ORDER BY chunk_quality_score DESC
    """)
    
    for row in cursor:
        print(f"   {row['quality_range']}: {row['count']} chunks")
    
    conn.close()

def show_sample_chunks(chunk_type=None, limit=3):
    """Show sample chunks"""
    
    conn = sqlite3.connect("dark_data.db")
    conn.row_factory = sqlite3.Row
    
    print(f"\n📋 SAMPLE CHUNKS" + (f" - {chunk_type}" if chunk_type else ""))
    print("=" * 60)
    
    where_clause = f"WHERE chunk_type = '{chunk_type}'" if chunk_type else ""
    
    cursor = conn.execute(f"""
        SELECT id, chunk_type, page_range, content_length, 
               extracted_companies, extracted_technical_specs, chunk_quality_score
        FROM document_chunks 
        {where_clause}
        ORDER BY chunk_quality_score DESC
        LIMIT {limit}
    """)
    
    for i, row in enumerate(cursor, 1):
        print(f"\n{i}. Chunk #{row['id']} - {row['chunk_type']}")
        print(f"   📏 Pages: {row['page_range']}")
        print(f"   📊 Length: {row['content_length']} chars")
        print(f"   ⭐ Quality: {row['chunk_quality_score']:.2f}")
        
        # Show extracted entities
        companies = json.loads(row['extracted_companies'] or '[]')
        if companies:
            print(f"   🏢 Companies: {', '.join(companies[:3])}{'...' if len(companies) > 3 else ''}")
        
        specs = json.loads(row['extracted_technical_specs'] or '[]')
        if specs:
            spec_text = []
            for spec in specs[:3]:
                if isinstance(spec, dict):
                    spec_text.append(f"{spec.get('value', '')}{spec.get('unit', '')}")
                else:
                    spec_text.append(str(spec))
            print(f"   ⚡ Tech specs: {', '.join(spec_text)}{'...' if len(specs) > 3 else ''}")
    
    conn.close()

def show_chunk_content(chunk_id):
    """Show full content of specific chunk"""
    
    conn = sqlite3.connect("dark_data.db")
    conn.row_factory = sqlite3.Row
    
    cursor = conn.execute("""
        SELECT * FROM document_chunks WHERE id = ?
    """, (chunk_id,))
    
    chunk = cursor.fetchone()
    if not chunk:
        print(f"❌ Chunk {chunk_id} not found")
        return
    
    print(f"\n📄 CHUNK #{chunk_id} DETAILS")
    print("=" * 60)
    print(f"Type: {chunk['chunk_type']}")
    print(f"Pages: {chunk['page_range']}")
    print(f"Length: {chunk['content_length']} characters")
    print(f"Quality: {chunk['chunk_quality_score']:.2f}")
    print(f"Strategy: {chunk['processing_strategy']}")
    
    print(f"\n📝 CONTENT PREVIEW (first 500 chars):")
    print("-" * 40)
    content = chunk['content'] or ''
    print(content[:500] + "..." if len(content) > 500 else content)
    
    print(f"\n🔍 EXTRACTED ENTITIES:")
    print("-" * 30)
    
    entities = {
        'Companies': json.loads(chunk['extracted_companies'] or '[]'),
        'Technical Specs': json.loads(chunk['extracted_technical_specs'] or '[]'),
        'Dates': json.loads(chunk['extracted_dates'] or '[]'),
        'Equipment': json.loads(chunk['extracted_equipment'] or '[]')
    }
    
    for entity_type, entity_list in entities.items():
        if entity_list:
            print(f"{entity_type}: {entity_list[:5]}{'...' if len(entity_list) > 5 else ''}")
    
    conn.close()

def search_chunks(query, limit=5):
    """Search chunks using FTS"""
    
    conn = sqlite3.connect("dark_data.db")
    conn.row_factory = sqlite3.Row
    
    print(f"\n🔍 SEARCH RESULTS for '{query}'")
    print("=" * 60)
    
    try:
        cursor = conn.execute("""
            SELECT cf.chunk_id, dc.chunk_type, dc.page_range, 
                   dc.content_length, dc.chunk_quality_score
            FROM chunks_fts cf
            JOIN document_chunks dc ON cf.chunk_id = dc.id
            WHERE chunks_fts MATCH ?
            ORDER BY cf.rank
            LIMIT ?
        """, (query, limit))
        
        results = cursor.fetchall()
        if not results:
            print("No results found.")
            return
        
        for i, row in enumerate(results, 1):
            print(f"{i}. Chunk #{row['chunk_id']} - {row['chunk_type']}")
            print(f"   📏 Pages: {row['page_range']}")
            print(f"   📊 Length: {row['content_length']} chars")
            print(f"   ⭐ Quality: {row['chunk_quality_score']:.2f}")
        
    except Exception as e:
        print(f"❌ Search error: {e}")
    
    conn.close()

def main():
    """Main viewer interface"""
    
    print("🔍 PROCESSED DATA VIEWER")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. 📊 View statistics")
        print("2. 📋 Show sample chunks")
        print("3. 📄 View specific chunk")
        print("4. 🔍 Search chunks")
        print("5. 📋 Show chunks by type")
        print("0. ❌ Exit")
        
        choice = input("\nChoice (0-5): ").strip()
        
        if choice == "0":
            print("👋 Goodbye!")
            break
        elif choice == "1":
            view_chunk_statistics()
        elif choice == "2":
            show_sample_chunks()
        elif choice == "3":
            chunk_id = input("Enter chunk ID: ").strip()
            if chunk_id.isdigit():
                show_chunk_content(int(chunk_id))
        elif choice == "4":
            query = input("Enter search query: ").strip()
            if query:
                search_chunks(query)
        elif choice == "5":
            print("Available types: company_listing, technical_specifications, narrative_text, structured_section, mixed_content")
            chunk_type = input("Enter chunk type: ").strip()
            if chunk_type:
                show_sample_chunks(chunk_type)
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    # Quick overview first
    view_chunk_statistics()
    show_sample_chunks(limit=2)
    
    # Then interactive mode
    main()