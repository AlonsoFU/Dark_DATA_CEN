#!/usr/bin/env python3
"""
Enhanced processor that detects annex structure
"""

import sqlite3
import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

class EnhancedAnnexProcessor:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to platform_data/database/dark_data.db relative to project root
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / "platform_data" / "database" / "dark_data.db"
        self.db_path = db_path
        
        # Annex patterns for technical documents
        self.annex_patterns = {
            'ANEXO_A': [
                r'ANEXO\s+A[:\s]',
                r'Anexo\s+A[:\s]',
                r'ANEXO\s+A\s*[-–]\s*'
            ],
            'ANEXO_B': [
                r'ANEXO\s+B[:\s]',
                r'Anexo\s+B[:\s]',
            ],
            'ANEXO_I': [
                r'ANEXO\s+I[^IV\s]',
                r'Anexo\s+I[^IV\s]',
            ],
            'ANEXO_II': [
                r'ANEXO\s+II[:\s]',
                r'Anexo\s+II[:\s]',
            ],
            'ANEXO_III': [
                r'ANEXO\s+III[:\s]',
                r'Anexo\s+III[:\s]',
            ],
            'RESUMEN_DIARIO': [
                r'RESUMEN\s+DIARIO\s+DE\s+OPERACION',
                r'RESUMEN\s+DIARIO\s+OPERACIONAL',
                r'REPORTE\s+DIARIO\s+DE\s+OPERACION'
            ],
            'OPERACION_SEN': [
                r'OPERACION\s+DEL\s+SEN',
                r'SISTEMA\s+ELECTRICO\s+NACIONAL',
                r'COORDINACION\s+DE\s+OPERACION'
            ],
            'COMUNICACIONES': [
                r'COMUNICACIONES?\s+OFICIALES?',
                r'CORRESPONDENCIA\s+TECNICA',
                r'INFORMES?\s+TECNICOS?'
            ],
            'DOCUMENTOS_ADJUNTOS': [
                r'DOCUMENTOS?\s+ADJUNTOS?',
                r'ARCHIVOS?\s+ANEXOS?',
                r'MATERIAL\s+COMPLEMENTARIO'
            ],
            'CRONOGRAMA': [
                r'CRONOGRAMA\s+DE\s+',
                r'TIMELINE\s+',
                r'SECUENCIA\s+TEMPORAL'
            ]
        }
        
        # Topic patterns within annexes
        self.topic_patterns = {
            'technical_analysis': [
                r'ANALISIS\s+TECNICO',
                r'ESTUDIO\s+TECNICO',
                r'EVALUACION\s+TECNICA'
            ],
            'equipment_details': [
                r'EQUIPAMIENTO',
                r'EQUIPOS\s+AFECTADOS',
                r'SISTEMAS\s+DE\s+PROTECCION'
            ],
            'operational_data': [
                r'DATOS\s+OPERACIONALES',
                r'PARAMETROS\s+DE\s+OPERACION',
                r'MEDICIONES\s+ELECTRICAS'
            ],
            'compliance_reports': [
                r'INFORMES?\s+DE\s+CUMPLIMIENTO',
                r'REPORTES?\s+REGULATORIOS?',
                r'COMPLIANCE\s+REPORTS?'
            ]
        }
    
    def enhance_chunks_with_annex_info(self):
        """Add annex information to existing chunks"""
        
        print("🔧 MEJORANDO CHUNKS CON INFORMACIÓN DE ANEXOS")
        print("=" * 50)
        
        # First, add new columns
        self.add_annex_columns()
        
        # Then, analyze and update chunks
        self.analyze_and_update_chunks()
        
        # Finally, show results
        self.show_enhanced_results()
    
    def add_annex_columns(self):
        """Add new columns for annex information"""
        
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Add new columns
            new_columns = [
                'annex_section TEXT',           # ANEXO_A, ANEXO_B, etc.
                'annex_topic TEXT',             # RESUMEN_DIARIO, OPERACION_SEN, etc.
                'document_section TEXT',        # main_report, annexes, appendices
                'topic_category TEXT'           # technical_analysis, equipment_details, etc.
            ]
            
            for column in new_columns:
                try:
                    conn.execute(f"ALTER TABLE document_chunks ADD COLUMN {column}")
                    print(f"   ✅ Added column: {column}")
                except:
                    print(f"   ⚠️  Column already exists: {column}")
            
            conn.commit()
            
        except Exception as e:
            print(f"❌ Error adding columns: {e}")
        finally:
            conn.close()
    
    def analyze_and_update_chunks(self):
        """Analyze content and update chunks with annex info"""
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        try:
            # Get all chunks
            cursor = conn.execute("SELECT id, content, page_range FROM document_chunks")
            chunks = cursor.fetchall()
            
            updated_count = 0
            
            for chunk in chunks:
                chunk_id = chunk['id']
                content = chunk['content'] or ''
                page_range = chunk['page_range'] or ''
                
                # Analyze content
                analysis = self.analyze_chunk_content(content, page_range)
                
                if analysis['needs_update']:
                    # Update chunk with annex info
                    conn.execute("""
                        UPDATE document_chunks 
                        SET annex_section = ?,
                            annex_topic = ?,
                            document_section = ?,
                            topic_category = ?
                        WHERE id = ?
                    """, (
                        analysis['annex_section'],
                        analysis['annex_topic'],
                        analysis['document_section'],
                        analysis['topic_category'],
                        chunk_id
                    ))
                    
                    updated_count += 1
            
            conn.commit()
            print(f"✅ Updated {updated_count} chunks with annex information")
            
        except Exception as e:
            print(f"❌ Error updating chunks: {e}")
        finally:
            conn.close()
    
    def analyze_chunk_content(self, content: str, page_range: str) -> Dict[str, Any]:
        """Analyze chunk content to determine annex info"""
        
        analysis = {
            'annex_section': None,
            'annex_topic': None,
            'document_section': None,
            'topic_category': None,
            'needs_update': False
        }
        
        # Determine document section based on page number
        if page_range:
            try:
                # Extract first page number
                page_match = re.search(r'(\d+)', page_range)
                if page_match:
                    page_num = int(page_match.group(1))
                    
                    # Heuristic: main report usually < 100 pages, annexes after
                    if page_num <= 50:
                        analysis['document_section'] = 'main_report'
                    elif page_num <= 200:
                        analysis['document_section'] = 'detailed_analysis'
                    else:
                        analysis['document_section'] = 'annexes'
            except:
                pass
        
        # Check for annex section patterns
        for annex_name, patterns in self.annex_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    analysis['annex_section'] = annex_name
                    analysis['needs_update'] = True
                    break
            if analysis['annex_section']:
                break
        
        # Check for annex topics
        for topic_name, patterns in self.annex_patterns.items():
            if topic_name in ['RESUMEN_DIARIO', 'OPERACION_SEN', 'COMUNICACIONES', 'DOCUMENTOS_ADJUNTOS']:
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        analysis['annex_topic'] = topic_name
                        analysis['needs_update'] = True
                        break
        
        # Check for topic categories
        for category, patterns in self.topic_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    analysis['topic_category'] = category
                    analysis['needs_update'] = True
                    break
            if analysis['topic_category']:
                break
        
        # If we found any annex info, mark as needing update
        if any([analysis['annex_section'], analysis['annex_topic'], 
                analysis['document_section'], analysis['topic_category']]):
            analysis['needs_update'] = True
        
        return analysis
    
    def show_enhanced_results(self):
        """Show results of enhancement"""
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        print(f"\n📊 RESULTADOS DE MEJORA")
        print("=" * 40)
        
        # Show annex sections found
        cursor = conn.execute("""
            SELECT annex_section, COUNT(*) as count 
            FROM document_chunks 
            WHERE annex_section IS NOT NULL
            GROUP BY annex_section
            ORDER BY count DESC
        """)
        
        annex_sections = cursor.fetchall()
        if annex_sections:
            print(f"📋 Secciones de anexos detectadas:")
            for row in annex_sections:
                print(f"   {row['annex_section']}: {row['count']} chunks")
        
        # Show annex topics found
        cursor = conn.execute("""
            SELECT annex_topic, COUNT(*) as count 
            FROM document_chunks 
            WHERE annex_topic IS NOT NULL
            GROUP BY annex_topic
            ORDER BY count DESC
        """)
        
        annex_topics = cursor.fetchall()
        if annex_topics:
            print(f"\n🏷️  Tópicos de anexos detectados:")
            for row in annex_topics:
                print(f"   {row['annex_topic']}: {row['count']} chunks")
        
        # Show document sections
        cursor = conn.execute("""
            SELECT document_section, COUNT(*) as count 
            FROM document_chunks 
            WHERE document_section IS NOT NULL
            GROUP BY document_section
            ORDER BY count DESC
        """)
        
        doc_sections = cursor.fetchall()
        if doc_sections:
            print(f"\n📄 Secciones del documento:")
            for row in doc_sections:
                print(f"   {row['document_section']}: {row['count']} chunks")
        
        # Show sample enhanced chunks
        print(f"\n📋 MUESTRA DE CHUNKS MEJORADOS:")
        cursor = conn.execute("""
            SELECT id, chunk_type, page_range, annex_section, annex_topic, 
                   document_section, topic_category
            FROM document_chunks 
            WHERE annex_section IS NOT NULL OR annex_topic IS NOT NULL
            LIMIT 5
        """)
        
        samples = cursor.fetchall()
        for i, chunk in enumerate(samples, 1):
            print(f"\n{i}. Chunk #{chunk['id']} (Páginas: {chunk['page_range']})")
            if chunk['annex_section']:
                print(f"   📋 Anexo: {chunk['annex_section']}")
            if chunk['annex_topic']:
                print(f"   🏷️  Tópico: {chunk['annex_topic']}")
            if chunk['document_section']:
                print(f"   📄 Sección: {chunk['document_section']}")
            if chunk['topic_category']:
                print(f"   🔖 Categoría: {chunk['topic_category']}")
        
        conn.close()
    
    def show_new_search_capabilities(self):
        """Show what new searches are now possible"""
        
        print(f"\n🚀 NUEVAS CAPACIDADES DE BÚSQUEDA")
        print("=" * 45)
        
        new_searches = [
            {
                "query": "¿Qué dice el Anexo A?",
                "sql": "WHERE annex_section = 'ANEXO_A'"
            },
            {
                "query": "Mostrar solo el reporte principal",
                "sql": "WHERE document_section = 'main_report'"
            },
            {
                "query": "Resumen diario de operación",
                "sql": "WHERE annex_topic = 'RESUMEN_DIARIO'"
            },
            {
                "query": "Análisis técnico detallado",
                "sql": "WHERE topic_category = 'technical_analysis'"
            },
            {
                "query": "Información de equipos en anexos",
                "sql": "WHERE document_section = 'annexes' AND topic_category = 'equipment_details'"
            }
        ]
        
        for search in new_searches:
            print(f"🔍 \"{search['query']}\"")
            print(f"   SQL: {search['sql']}")

def main():
    processor = EnhancedAnnexProcessor()
    processor.enhance_chunks_with_annex_info()
    processor.show_new_search_capabilities()

if __name__ == "__main__":
    main()