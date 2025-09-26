#!/usr/bin/env python3
"""
Detect specific annex titles and themes from document
"""

import sqlite3
import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

class SpecificAnnexDetector:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to platform_data/database/dark_data.db relative to project root
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / "platform_data" / "database" / "dark_data.db"
        self.db_path = db_path
        
        # Specific patterns for numbered annexes with titles
        self.specific_annex_patterns = {
            'header_patterns': [
                # Index/table of contents style
                r'•\s*(.{10,150})\s*\(Anexo\s+N[ºo°]?\s*(\d+)\)',
                r'•\s*(.{10,150})\s*\(ANEXO\s+N[ºo°]?\s*(\d+)\)',
                # Formal titles in separate lines/pages
                r'ANEXO\s+N[ºo°]?\s*(\d+)\s*\n\s*(.{10,150})',
                r'ANEXO\s+N[ºo°]?\s*(\d+)\s*[:\n]\s*(.{10,150})',
                # Traditional patterns
                r'ANEXO\s+N[ºo°]?\s*(\d+)\s*[:-]?\s*(.{10,100})',
                r'ANEXO\s+(\d+)\s*[:-]\s*(.{10,100})',
                r'Anexo\s+N[ºo°]?\s*(\d+)\s*[:-]?\s*(.{10,100})',
                r'Anexo\s+(\d+)\s*[:-]\s*(.{10,100})',
            ],
            'section_patterns': [
                r'(\d+)\.\s*(.{10,80})\s*$',  # "1. Título de sección"
                r'([A-Z]\d*)\.\s*(.{10,80})\s*$',  # "A1. Título de sección"
            ]
        }
        
        # Theme categorization based on keywords
        self.theme_keywords = {
            'generation_programming': [
                'generación programada', 'programación de generación', 'despacho programado',
                'plan de generación', 'cronograma de generación'
            ],
            'operational_data': [
                'datos operacionales', 'información operativa', 'parámetros de operación',
                'mediciones', 'registros operacionales'
            ],
            'incident_timeline': [
                'cronología', 'secuencia temporal', 'timeline', 'cronograma del incidente',
                'desarrollo temporal', 'línea de tiempo'
            ],
            'technical_analysis': [
                'análisis técnico', 'estudio técnico', 'evaluación técnica',
                'diagnóstico técnico', 'informe técnico'
            ],
            'equipment_details': [
                'equipamiento', 'equipos', 'dispositivos', 'sistemas',
                'protecciones', 'interruptores', 'transformadores'
            ],
            'communication_logs': [
                'comunicaciones', 'correspondencia', 'mensajes', 'avisos',
                'notificaciones', 'informes de comunicación'
            ],
            'regulatory_compliance': [
                'cumplimiento', 'normativa', 'regulación', 'compliance',
                'requerimientos regulatorios', 'disposiciones'
            ],
            'recovery_procedures': [
                'recuperación', 'restablecimiento', 'normalización',
                'procedimientos de recuperación', 'plan de recuperación'
            ]
        }
    
    def detect_specific_annexes(self):
        """Detect and catalog specific annex titles"""
        
        print("🔍 DETECTANDO TÍTULOS ESPECÍFICOS DE ANEXOS")
        print("=" * 50)
        
        # Add new column for specific annex info
        self.add_specific_annex_columns()
        
        # Find annex headers in content
        annex_catalog = self.scan_for_annex_headers()
        
        # Update chunks with specific annex information
        self.update_chunks_with_specific_annexes(annex_catalog)
        
        # Show results
        self.show_specific_results()
        
        return annex_catalog
    
    def add_specific_annex_columns(self):
        """Add columns for specific annex information"""
        
        conn = sqlite3.connect(self.db_path)
        
        try:
            new_columns = [
                'specific_annex_number TEXT',    # "1", "2", "3", etc.
                'specific_annex_title TEXT',     # "Detalle de la generación programada..."
                'annex_theme TEXT',              # generation_programming, operational_data, etc.
                'is_annex_header BOOLEAN'       # TRUE if this chunk contains the annex title
            ]
            
            for column in new_columns:
                try:
                    conn.execute(f"ALTER TABLE document_chunks ADD COLUMN {column}")
                    print(f"   ✅ Added column: {column}")
                except:
                    print(f"   ⚠️  Column exists: {column.split()[0]}")
            
            conn.commit()
            
        except Exception as e:
            print(f"❌ Error adding columns: {e}")
        finally:
            conn.close()
    
    def scan_for_annex_headers(self) -> Dict[str, Any]:
        """Scan all chunks for annex headers and titles"""
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        annex_catalog = {}
        
        try:
            # Get all chunks, prioritize those likely to contain headers
            cursor = conn.execute("""
                SELECT id, content, page_range, chunk_type, content_length
                FROM document_chunks 
                WHERE content IS NOT NULL
                ORDER BY CAST(SUBSTR(page_range, 1, INSTR(page_range||'-', '-')-1) AS INTEGER)
            """)
            
            chunks = cursor.fetchall()
            print(f"🔍 Scanning {len(chunks)} chunks for annex headers...")
            
            for chunk in chunks:
                content = chunk['content'] or ''
                
                # Look for annex headers
                annex_info = self.extract_annex_header(content)
                
                if annex_info:
                    annex_number = annex_info['number']
                    
                    if annex_number not in annex_catalog:
                        annex_catalog[annex_number] = {
                            'title': annex_info['title'],
                            'theme': self.categorize_theme(annex_info['title']),
                            'header_chunk_id': chunk['id'],
                            'page_range': chunk['page_range'],
                            'content_chunks': []
                        }
                        
                        print(f"   📋 Found ANEXO {annex_number}: \"{annex_info['title'][:60]}...\"")
                    
                    annex_catalog[annex_number]['content_chunks'].append(chunk['id'])
        
        except Exception as e:
            print(f"❌ Error scanning for annexes: {e}")
        finally:
            conn.close()
        
        return annex_catalog
    
    def extract_annex_header(self, content: str) -> Optional[Dict[str, str]]:
        """Extract annex number and title from content"""
        
        # Look for specific annex patterns
        for pattern in self.specific_annex_patterns['header_patterns']:
            match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            if match:
                # Handle different pattern groups (index style vs traditional)
                if pattern.startswith(r'•'):
                    # Index style: title comes first, then number
                    title = match.group(1).strip()
                    number = match.group(2)
                else:
                    # Traditional style: number first, then title  
                    number = match.group(1)
                    title = match.group(2).strip()
                
                # Clean up the title
                title = re.sub(r'\s+', ' ', title)  # Multiple spaces to single
                title = title.strip('.,:-')         # Remove trailing punctuation
                title = title.replace('\n', ' ')     # Remove line breaks
                
                # Check if this looks like a real title (not random content)
                if len(title) > 10 and ('detalle' in title.lower() or 'generación' in title.lower() or 
                                       'cronograma' in title.lower() or 'análisis' in title.lower() or
                                       'comunicaciones' in title.lower() or 'operación' in title.lower() or
                                       'movimiento' in title.lower() or 'mantenimiento' in title.lower()):
                    return {
                        'number': number,
                        'title': title
                    }
        
        # Also look for section patterns within content
        for pattern in self.specific_annex_patterns['section_patterns']:
            matches = re.findall(pattern, content, re.MULTILINE)
            for match in matches:
                if len(match) == 2:
                    section_num = match[0]
                    section_title = match[1].strip()
                    
                    # Check if this looks like a main annex title
                    if any(keyword in section_title.lower() for keyword in 
                           ['anexo', 'generación', 'operación', 'cronograma', 'detalle']):
                        return {
                            'number': section_num,
                            'title': section_title
                        }
        
        return None
    
    def categorize_theme(self, title: str) -> str:
        """Categorize annex theme based on title"""
        
        title_lower = title.lower()
        
        for theme, keywords in self.theme_keywords.items():
            for keyword in keywords:
                if keyword in title_lower:
                    return theme
        
        # Default categorization based on common words
        if any(word in title_lower for word in ['generación', 'despacho', 'programada']):
            return 'generation_programming'
        elif any(word in title_lower for word in ['cronología', 'tiempo', 'secuencia']):
            return 'incident_timeline'
        elif any(word in title_lower for word in ['técnico', 'análisis', 'estudio']):
            return 'technical_analysis'
        elif any(word in title_lower for word in ['equipo', 'sistema', 'protección']):
            return 'equipment_details'
        else:
            return 'general_information'
    
    def update_chunks_with_specific_annexes(self, annex_catalog: Dict[str, Any]):
        """Update chunks with specific annex information"""
        
        conn = sqlite3.connect(self.db_path)
        
        try:
            updated_count = 0
            
            for annex_num, annex_info in annex_catalog.items():
                header_chunk_id = annex_info['header_chunk_id']
                title = annex_info['title']
                theme = annex_info['theme']
                
                # Update header chunk
                conn.execute("""
                    UPDATE document_chunks 
                    SET specific_annex_number = ?,
                        specific_annex_title = ?,
                        annex_theme = ?,
                        is_annex_header = 1
                    WHERE id = ?
                """, (annex_num, title, theme, header_chunk_id))
                
                updated_count += 1
                
                # Now find and update related content chunks
                # Strategy: chunks in similar page range likely belong to same annex
                header_page = self.extract_page_number(annex_info['page_range'])
                
                if header_page:
                    # Update chunks in the following pages (heuristic: next 20 pages)
                    cursor = conn.execute("""
                        SELECT id, page_range FROM document_chunks 
                        WHERE specific_annex_number IS NULL
                    """)
                    
                    potential_chunks = cursor.fetchall()
                    
                    for chunk_id, page_range in potential_chunks:
                        chunk_page = self.extract_page_number(page_range)
                        
                        if chunk_page and header_page < chunk_page <= header_page + 20:
                            # Check if this chunk should belong to this annex
                            cursor_content = conn.execute("""
                                SELECT content FROM document_chunks WHERE id = ?
                            """, (chunk_id,))
                            
                            content_row = cursor_content.fetchone()
                            if content_row and self.chunk_belongs_to_annex(content_row[0], theme):
                                conn.execute("""
                                    UPDATE document_chunks 
                                    SET specific_annex_number = ?,
                                        specific_annex_title = ?,
                                        annex_theme = ?,
                                        is_annex_header = 0
                                    WHERE id = ?
                                """, (annex_num, title, theme, chunk_id))
                                
                                updated_count += 1
            
            conn.commit()
            print(f"✅ Updated {updated_count} chunks with specific annex information")
            
        except Exception as e:
            print(f"❌ Error updating chunks: {e}")
        finally:
            conn.close()
    
    def extract_page_number(self, page_range: str) -> Optional[int]:
        """Extract first page number from page range"""
        if not page_range:
            return None
        
        match = re.search(r'(\d+)', page_range)
        if match:
            return int(match.group(1))
        return None
    
    def chunk_belongs_to_annex(self, content: str, theme: str) -> bool:
        """Determine if chunk content belongs to specific annex theme"""
        
        if not content:
            return False
        
        content_lower = content.lower()
        
        # Check for theme-related keywords
        theme_keywords = self.theme_keywords.get(theme, [])
        keyword_matches = sum(1 for keyword in theme_keywords if keyword in content_lower)
        
        # If it has relevant keywords, it likely belongs
        return keyword_matches >= 1
    
    def show_specific_results(self):
        """Show results of specific annex detection"""
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        print(f"\n📊 ANEXOS ESPECÍFICOS DETECTADOS")
        print("=" * 40)
        
        # Show detected specific annexes
        cursor = conn.execute("""
            SELECT specific_annex_number, specific_annex_title, annex_theme,
                   COUNT(*) as chunk_count
            FROM document_chunks 
            WHERE specific_annex_number IS NOT NULL
            GROUP BY specific_annex_number, specific_annex_title, annex_theme
            ORDER BY CAST(specific_annex_number AS INTEGER)
        """)
        
        annexes = cursor.fetchall()
        
        if annexes:
            for annex in annexes:
                print(f"\n📋 ANEXO {annex['specific_annex_number']}")
                print(f"   📝 Título: \"{annex['specific_annex_title']}\"")
                print(f"   🏷️  Tema: {annex['annex_theme']}")
                print(f"   📊 Chunks: {annex['chunk_count']}")
        else:
            print("❌ No se detectaron anexos específicos")
        
        # Show header chunks
        cursor = conn.execute("""
            SELECT specific_annex_number, page_range, content
            FROM document_chunks 
            WHERE is_annex_header = 1
            ORDER BY CAST(specific_annex_number AS INTEGER)
        """)
        
        headers = cursor.fetchall()
        
        if headers:
            print(f"\n📄 CHUNKS DE CABECERAS DE ANEXOS:")
            for header in headers:
                content_preview = header['content'][:100].replace('\n', ' ').strip()
                print(f"   Anexo {header['specific_annex_number']} (Página {header['page_range']}): \"{content_preview}...\"")
        
        conn.close()
    
    def show_new_search_examples(self):
        """Show new search capabilities"""
        
        print(f"\n🔍 NUEVAS BÚSQUEDAS ESPECÍFICAS DISPONIBLES")
        print("=" * 50)
        
        searches = [
            {
                "query": "¿Qué dice el Anexo 1?",
                "sql": "WHERE specific_annex_number = '1'"
            },
            {
                "query": "Información sobre generación programada",
                "sql": "WHERE annex_theme = 'generation_programming'"
            },
            {
                "query": "Cronología del incidente",
                "sql": "WHERE annex_theme = 'incident_timeline'"
            },
            {
                "query": "Solo las cabeceras de anexos",
                "sql": "WHERE is_annex_header = 1"
            },
            {
                "query": "Contenido completo del anexo sobre equipos",
                "sql": "WHERE annex_theme = 'equipment_details' AND specific_annex_number IS NOT NULL"
            }
        ]
        
        for search in searches:
            print(f"🔍 \"{search['query']}\"")
            print(f"   SQL: {search['sql']}")

def main():
    detector = SpecificAnnexDetector()
    annex_catalog = detector.detect_specific_annexes()
    detector.show_new_search_examples()
    
    return annex_catalog

if __name__ == "__main__":
    catalog = main()