#!/usr/bin/env python3
"""
Show processed results summary
"""

import sqlite3
import json
from pathlib import Path

def show_summary():
    """Show complete processing summary"""
    
    conn = sqlite3.connect("dark_data.db")
    conn.row_factory = sqlite3.Row
    
    print("🎉 DOCUMENT PROCESSING COMPLETE!")
    print("=" * 50)
    
    # Basic stats
    cursor = conn.execute("SELECT COUNT(*) as total FROM document_chunks")
    total = cursor.fetchone()['total']
    print(f"✅ Total chunks processed: {total}")
    
    # By type
    print(f"\n📊 Chunks by Type:")
    cursor = conn.execute("""
        SELECT chunk_type, COUNT(*) as count 
        FROM document_chunks 
        GROUP BY chunk_type 
        ORDER BY count DESC
    """)
    
    for row in cursor:
        print(f"   📋 {row['chunk_type']}: {row['count']} chunks")
    
    # Quality distribution
    cursor = conn.execute("""
        SELECT 
            COUNT(CASE WHEN chunk_quality_score >= 0.7 THEN 1 END) as high,
            COUNT(CASE WHEN chunk_quality_score >= 0.4 AND chunk_quality_score < 0.7 THEN 1 END) as medium,
            COUNT(CASE WHEN chunk_quality_score < 0.4 THEN 1 END) as low
        FROM document_chunks
    """)
    
    quality = cursor.fetchone()
    print(f"\n⭐ Quality Distribution:")
    print(f"   🟢 High quality (0.7+): {quality['high']} chunks")
    print(f"   🟡 Medium quality (0.4-0.7): {quality['medium']} chunks")  
    print(f"   🔴 Low quality (<0.4): {quality['low']} chunks")
    
    # Sample high-quality chunks
    print(f"\n🏆 TOP 5 HIGH-QUALITY CHUNKS:")
    cursor = conn.execute("""
        SELECT id, chunk_type, page_range, content_length, 
               extracted_companies, chunk_quality_score
        FROM document_chunks 
        WHERE chunk_quality_score >= 0.7
        ORDER BY chunk_quality_score DESC, content_length DESC
        LIMIT 5
    """)
    
    for i, row in enumerate(cursor, 1):
        companies = json.loads(row['extracted_companies'] or '[]')
        company_text = f" - Companies: {', '.join(companies[:2])}" if companies else ""
        
        print(f"   {i}. Chunk #{row['id']} ({row['chunk_type']})")
        print(f"      📏 Pages {row['page_range']} - {row['content_length']} chars - Quality {row['chunk_quality_score']:.2f}{company_text}")
    
    # Files created
    print(f"\n📁 Files Available:")
    files_to_check = [
        "dark_data.db",
        "truly_adaptive_EAF-089-2025.json",
        "processed_docs/",
        "analysis_output/"
    ]
    
    for file_path in files_to_check:
        path = Path(file_path)
        if path.exists():
            if path.is_file():
                size_mb = path.stat().st_size / 1024 / 1024
                print(f"   ✅ {file_path} ({size_mb:.1f} MB)")
            else:
                file_count = len(list(path.glob("*")))
                print(f"   ✅ {file_path} ({file_count} files)")
        else:
            print(f"   ❌ {file_path} (missing)")
    
    conn.close()

def show_claude_capabilities():
    """Show what Claude can now do"""
    
    print(f"\n🤖 WHAT CLAUDE CAN NOW DO:")
    print("=" * 40)
    
    capabilities = [
        ("Search by company", "Find all chunks mentioning ENEL, Colbún, etc."),
        ("Search by content type", "Get only technical specs or company listings"),
        ("Full-text search", "Search across all chunk content"),
        ("Quality-filtered results", "Get only high-quality, relevant chunks"),
        ("Page-specific queries", "Find information from specific page ranges"),
        ("Entity extraction", "Access pre-extracted companies, dates, specs")
    ]
    
    for capability, description in capabilities:
        print(f"   ✅ {capability}: {description}")
    
    print(f"\n💡 Example Claude Queries:")
    examples = [
        "¿Qué problemas de compliance tiene ENEL?",
        "Buscar especificaciones técnicas de 500 kV", 
        "¿Cuáles empresas reportaron tarde?",
        "Cronología del incidente del 25/02/2025",
        "¿Qué equipos Siemens fallaron?",
    ]
    
    for example in examples:
        print(f"   🔹 \"{example}\"")

def main():
    show_summary()
    show_claude_capabilities()
    
    print(f"\n🚀 NEXT STEPS:")
    print("1. Your MCP server can now use chunk-based queries")
    print("2. Claude can search your 399-page document intelligently")  
    print("3. All chunks are stored in dark_data.db with full-text search")
    print("4. Original incident/company data is still available")
    
    print(f"\n💾 Your document is now AI-ready!")

if __name__ == "__main__":
    main()