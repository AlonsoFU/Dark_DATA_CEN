#!/usr/bin/env python3
"""
Integrate intelligent chunks into existing database
Extends current SQLite schema to support chunk-based queries
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, List

class ChunkDatabaseIntegrator:
    def __init__(self, db_path: str = "dark_data.db"):
        self.db_path = db_path
    
    def create_chunk_tables(self):
        """Extend existing database with chunk tables"""
        
        conn = sqlite3.connect(self.db_path)
        try:
            # Create chunks table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    incident_id INTEGER REFERENCES incidents(id),
                    
                    -- Chunk information
                    chunk_type TEXT NOT NULL,
                    page_range TEXT,
                    content TEXT NOT NULL,
                    content_length INTEGER,
                    
                    -- Extracted entities (JSON)
                    extracted_companies JSON,
                    extracted_technical_specs JSON,
                    extracted_dates JSON,
                    extracted_equipment JSON,
                    extracted_compliance JSON,
                    
                    -- Processing metadata
                    processing_strategy TEXT,
                    chunk_quality_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_type ON document_chunks(chunk_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_incident ON document_chunks(incident_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_quality ON document_chunks(chunk_quality_score)")
            
            # Create FTS table for chunk content
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                    chunk_id UNINDEXED,
                    chunk_type,
                    content,
                    extracted_text,
                    content=''
                )
            """)
            
            # Create view for easy querying
            conn.execute("""
                CREATE VIEW IF NOT EXISTS chunk_summary AS
                SELECT 
                    dc.id as chunk_id,
                    i.report_id,
                    i.title,
                    dc.chunk_type,
                    dc.page_range,
                    dc.content_length,
                    json_array_length(dc.extracted_companies) as company_count,
                    json_array_length(dc.extracted_technical_specs) as spec_count,
                    json_array_length(dc.extracted_dates) as date_count,
                    dc.chunk_quality_score,
                    dc.created_at
                FROM document_chunks dc
                JOIN incidents i ON dc.incident_id = i.id
            """)
            
            conn.commit()
            print("✅ Chunk tables created successfully")
            
        except Exception as e:
            print(f"❌ Error creating chunk tables: {e}")
        finally:
            conn.close()
    
    def import_chunks_from_json(self, chunks_file: str, report_id: str):
        """Import chunks from processed JSON file"""
        
        print(f"📥 Importing chunks from {chunks_file} for report {report_id}")
        
        # Load chunks data
        with open(chunks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        chunks = data.get('chunks', [])
        if not chunks:
            print("❌ No chunks found in file")
            return
        
        conn = sqlite3.connect(self.db_path)
        try:
            # Get incident ID
            cursor = conn.execute("SELECT id FROM incidents WHERE report_id = ?", (report_id,))
            incident_row = cursor.fetchone()
            if not incident_row:
                print(f"❌ Incident {report_id} not found in database")
                return
            
            incident_id = incident_row[0]
            
            # Import each chunk
            imported_count = 0
            for chunk in chunks:
                try:
                    # Calculate quality score
                    quality_score = self._calculate_quality_score(chunk)
                    
                    # Prepare extracted entities
                    extracted_entities = chunk.get('extracted_entities', {})
                    
                    # Insert chunk
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO document_chunks (
                            incident_id, chunk_type, page_range, content, content_length,
                            extracted_companies, extracted_technical_specs, extracted_dates,
                            extracted_equipment, extracted_compliance,
                            processing_strategy, chunk_quality_score
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        incident_id,
                        chunk.get('primary_content_type', 'unknown'),
                        chunk.get('page_range', ''),
                        chunk.get('content', ''),
                        chunk.get('content_length', 0),
                        json.dumps(extracted_entities.get('companies', [])),
                        json.dumps(extracted_entities.get('technical_specs', [])),
                        json.dumps(extracted_entities.get('dates', [])),
                        json.dumps(extracted_entities.get('equipment', [])),
                        json.dumps(extracted_entities.get('compliance', [])),
                        chunk.get('metadata', {}).get('adaptation_strategy', 'unknown'),
                        quality_score
                    ))
                    
                    # Get chunk ID for FTS
                    chunk_id = cursor.lastrowid
                    
                    # Add to FTS index
                    extracted_text = self._create_searchable_text(extracted_entities)
                    conn.execute("""
                        INSERT INTO chunks_fts (chunk_id, chunk_type, content, extracted_text)
                        VALUES (?, ?, ?, ?)
                    """, (
                        chunk_id,
                        chunk.get('primary_content_type', 'unknown'),
                        chunk.get('content', ''),
                        extracted_text
                    ))
                    
                    imported_count += 1
                    
                except Exception as e:
                    print(f"⚠️  Error importing chunk: {e}")
            
            conn.commit()
            print(f"✅ Imported {imported_count} chunks for {report_id}")
            
        except Exception as e:
            print(f"❌ Error importing chunks: {e}")
        finally:
            conn.close()
    
    def _calculate_quality_score(self, chunk: Dict[str, Any]) -> float:
        """Calculate quality score for chunk (0.0 to 1.0)"""
        
        score = 0.0
        
        # Content length score (optimal around 2000-4000 chars)
        content_length = chunk.get('content_length', 0)
        if 1000 <= content_length <= 5000:
            score += 0.3
        elif content_length > 500:
            score += 0.1
        
        # Entity richness score
        entities = chunk.get('extracted_entities', {})
        entity_count = sum(len(v) for v in entities.values())
        if entity_count > 10:
            score += 0.4
        elif entity_count > 5:
            score += 0.2
        elif entity_count > 0:
            score += 0.1
        
        # Content type consistency score
        content_types = chunk.get('content_type_distribution', {})
        if len(content_types) == 1:  # Pure content type
            score += 0.2
        elif len(content_types) <= 2:  # Mixed but manageable
            score += 0.1
        
        # Processing strategy score
        strategy = chunk.get('metadata', {}).get('adaptation_strategy', '')
        if strategy == 'page_by_page_classification':
            score += 0.1
        
        return min(1.0, score)
    
    def _create_searchable_text(self, entities: Dict[str, List]) -> str:
        """Create searchable text from extracted entities"""
        
        searchable_parts = []
        
        # Add companies
        companies = entities.get('companies', [])
        if companies:
            searchable_parts.append(' '.join(companies))
        
        # Add technical specs as text
        specs = entities.get('technical_specs', [])
        for spec in specs:
            if isinstance(spec, dict):
                searchable_parts.append(f"{spec.get('value', '')} {spec.get('unit', '')}")
            else:
                searchable_parts.append(str(spec))
        
        # Add equipment
        equipment = entities.get('equipment', [])
        if equipment:
            searchable_parts.append(' '.join(equipment))
        
        # Add dates
        dates = entities.get('dates', [])
        if dates:
            searchable_parts.append(' '.join(dates))
        
        return ' '.join(searchable_parts)
    
    def create_enhanced_mcp_queries(self):
        """Create enhanced query functions for MCP server"""
        
        queries = {
            'search_chunks_by_type': """
                SELECT chunk_id, incident_id, chunk_type, page_range, content, chunk_quality_score
                FROM document_chunks 
                WHERE chunk_type = ? AND chunk_quality_score > 0.3
                ORDER BY chunk_quality_score DESC
                LIMIT ?
            """,
            
            'search_chunks_by_company': """
                SELECT dc.chunk_id, i.report_id, dc.chunk_type, dc.page_range, 
                       dc.content, dc.extracted_companies
                FROM document_chunks dc
                JOIN incidents i ON dc.incident_id = i.id
                WHERE JSON_EXTRACT(dc.extracted_companies, '$') LIKE ?
                ORDER BY dc.chunk_quality_score DESC
                LIMIT ?
            """,
            
            'search_chunks_fts': """
                SELECT cf.chunk_id, dc.chunk_type, dc.page_range, i.report_id,
                       dc.content, cf.rank
                FROM chunks_fts cf
                JOIN document_chunks dc ON cf.chunk_id = dc.id
                JOIN incidents i ON dc.incident_id = i.id
                WHERE chunks_fts MATCH ?
                ORDER BY cf.rank
                LIMIT ?
            """,
            
            'get_chunk_statistics': """
                SELECT 
                    chunk_type,
                    COUNT(*) as chunk_count,
                    AVG(content_length) as avg_length,
                    AVG(chunk_quality_score) as avg_quality,
                    SUM(json_array_length(extracted_companies)) as total_companies
                FROM document_chunks
                GROUP BY chunk_type
                ORDER BY chunk_count DESC
            """
        }
        
        return queries

def main():
    """Integrate chunks into existing database"""
    
    integrator = ChunkDatabaseIntegrator()
    
    # Step 1: Create chunk tables
    integrator.create_chunk_tables()
    
    # Step 2: Import chunks if files exist
    processed_files = [
        ('truly_adaptive_EAF-089-2025.json', 'EAF-089/2025'),
        ('adaptive_processing_EAF-089-2025.json', 'EAF-089/2025'),
    ]
    
    for filename, report_id in processed_files:
        if Path(filename).exists():
            integrator.import_chunks_from_json(filename, report_id)
        else:
            print(f"⚠️  File not found: {filename}")
    
    # Step 3: Show integration results
    conn = sqlite3.connect(integrator.db_path)
    cursor = conn.execute("SELECT COUNT(*) FROM document_chunks")
    chunk_count = cursor.fetchone()[0]
    conn.close()
    
    print(f"\n📊 INTEGRATION COMPLETE")
    print(f"📄 Total chunks in database: {chunk_count}")
    
    if chunk_count > 0:
        print(f"\n✅ Your MCP server can now use:")
        print(f"   • Chunk-based search by type")
        print(f"   • Company-specific chunk queries")
        print(f"   • Full-text search across chunks")
        print(f"   • Quality-scored results")
    
    print(f"\n🔧 Next steps:")
    print(f"   1. Update mcp_server.py with chunk queries")
    print(f"   2. Test new chunk-based searches")
    print(f"   3. Compare performance with original approach")

if __name__ == "__main__":
    main()