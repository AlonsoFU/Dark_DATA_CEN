#!/usr/bin/env python3
"""
Data ingestion script for Dark Data Database
Loads power system failure JSON data into SQLite database
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, Any, List
import os
from pathlib import Path

class DataIngester:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to platform_data/database/dark_data.db relative to project root
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / "platform_data" / "database" / "dark_data.db"
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Connect to SQLite database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        
    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            
    def insert_company(self, company_data: Dict[str, Any]) -> int:
        """Insert company data and return company ID"""
        cursor = self.conn.cursor()
        
        # Check if company already exists
        cursor.execute("SELECT id FROM companies WHERE name = ?", (company_data.get('name', ''),))
        existing = cursor.fetchone()
        if existing:
            return existing[0]
            
        # Insert new company
        cursor.execute("""
            INSERT INTO companies (name, rut, legal_representative, address)
            VALUES (?, ?, ?, ?)
        """, (
            company_data.get('name', ''),
            company_data.get('rut', ''),
            company_data.get('legal_representative', ''),
            company_data.get('address', '')
        ))
        return cursor.lastrowid
    
    def insert_incident(self, json_data: Dict[str, Any]) -> int:
        """Insert main incident data and return incident ID"""
        incident_info = json_data.get('incident_info', {})
        affected = json_data.get('affected_installation', {})
        failed_element = json_data.get('failed_element', {})
        tech_details = json_data.get('technical_details', {})
        metadata = json_data.get('metadata', {})
        
        # Parse dates
        failure_date = incident_info.get('failure_date', '').replace('/', '-')
        if len(failure_date.split('-')[2]) == 4:  # DD/MM/YYYY format
            day, month, year = failure_date.split('-')
            failure_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            
        extraction_date = metadata.get('extraction_date', '')
        
        # Prepare text for full-text search
        failure_cause_text = json_data.get('failure_origin_cause', '')
        technical_summary = f"""
        Equipment: {tech_details.get('protection_equipment', {}).get('manufacturer', '')} {tech_details.get('protection_equipment', {}).get('model', '')}
        Installation Date: {tech_details.get('protection_equipment', {}).get('installation_date', '')}
        Function Affected: {tech_details.get('protection_equipment', {}).get('function_affected', '')}
        Physical Phenomenon: {json_data.get('physical_phenomenon', '')}
        Electrical Phenomenon: {json_data.get('electrical_phenomenon', '')}
        System Impact: Power Transferred: {tech_details.get('system_impact', {}).get('power_transferred', '')}
        Location: {tech_details.get('geographical_location', {}).get('comuna', '')}, {tech_details.get('geographical_location', {}).get('region', '')}
        """.strip()
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO incidents (
                report_id, title, failure_date, failure_time, 
                disconnected_mw, classification,
                raw_json, incident_details, affected_installations, 
                generation_units, transmission_elements,
                failure_cause_text, technical_summary,
                document_pages, extraction_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            incident_info.get('report_id', ''),
            incident_info.get('title', ''),
            failure_date,
            incident_info.get('failure_time', ''),
            incident_info.get('disconnected_consumption_mw', 0),
            incident_info.get('classification', ''),
            json.dumps(json_data, ensure_ascii=False),  # Store full JSON
            json.dumps(incident_info, ensure_ascii=False),
            json.dumps(affected, ensure_ascii=False),
            json.dumps(json_data.get('generation_units', []), ensure_ascii=False),
            json.dumps(json_data.get('transmission_elements', []), ensure_ascii=False),
            failure_cause_text,
            technical_summary,
            metadata.get('document_pages', 0),
            extraction_date
        ))
        
        incident_id = cursor.lastrowid
        
        # Insert into full-text search table
        cursor.execute("""
            INSERT INTO incidents_fts (rowid, report_id, title, failure_cause_text, technical_summary)
            VALUES (?, ?, ?, ?, ?)
        """, (
            incident_id,
            incident_info.get('report_id', ''),
            incident_info.get('title', ''),
            failure_cause_text,
            technical_summary
        ))
        
        return incident_id
    
    def insert_compliance_reports(self, incident_id: int, json_data: Dict[str, Any]):
        """Insert compliance reports for companies"""
        company_reports = json_data.get('company_reports', [])
        
        for report in company_reports:
            # Insert or get company
            company_id = self.insert_company({
                'name': report.get('company_name', ''),
                'rut': '',  # Not provided in this data
                'legal_representative': '',
                'address': ''
            })
            
            # Insert compliance report
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO compliance_reports (
                    incident_id, company_id, reports_48h_status, 
                    reports_5d_status, compliance_issues
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                incident_id,
                company_id,
                report.get('reports_48h_status', ''),
                report.get('reports_5d_status', ''),
                json.dumps(report.get('compliance_issues', []), ensure_ascii=False)
            ))
    
    def insert_equipment(self, json_data: Dict[str, Any]):
        """Insert equipment data"""
        tech_details = json_data.get('technical_details', {})
        protection_equipment = tech_details.get('protection_equipment', {})
        
        if protection_equipment:
            # Parse installation date
            install_date = protection_equipment.get('installation_date', '')
            if install_date:
                # Convert "31 de mayo de 2018" to "2018-05-31"
                try:
                    # Simple date parsing for Spanish format
                    if 'de' in install_date:
                        parts = install_date.split()
                        if len(parts) >= 4:
                            day = parts[0]
                            month_map = {
                                'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
                                'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
                                'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
                            }
                            month = month_map.get(parts[2], '01')
                            year = parts[4]
                            install_date = f"{year}-{month}-{day.zfill(2)}"
                except:
                    install_date = ''
            
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO equipment (
                    manufacturer, model, installation_date, 
                    function_affected, system_number, raw_details
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                protection_equipment.get('manufacturer', ''),
                protection_equipment.get('model', ''),
                install_date,
                protection_equipment.get('function_affected', ''),
                protection_equipment.get('system_number', ''),
                json.dumps(protection_equipment, ensure_ascii=False)
            ))
    
    def ingest_json_file(self, json_file_path: str):
        """Main method to ingest JSON file into database"""
        print(f"Starting ingestion of: {json_file_path}")
        
        try:
            self.connect()
            
            # Load JSON data
            with open(json_file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            print("JSON loaded successfully")
            
            # Insert data in order (respecting foreign keys)
            print("Inserting incident data...")
            incident_id = self.insert_incident(json_data)
            print(f"Incident inserted with ID: {incident_id}")
            
            print("Inserting compliance reports...")
            self.insert_compliance_reports(incident_id, json_data)
            print("Compliance reports inserted")
            
            print("Inserting equipment data...")
            self.insert_equipment(json_data)
            print("Equipment data inserted")
            
            # Commit transaction
            self.conn.commit()
            print("✅ Data ingestion completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during ingestion: {e}")
            if self.conn:
                self.conn.rollback()
            raise
        finally:
            self.disconnect()
    
    def verify_data(self):
        """Verify that data was inserted correctly"""
        self.connect()
        try:
            cursor = self.conn.cursor()
            
            # Count records in each table
            tables = ['incidents', 'companies', 'compliance_reports', 'equipment']
            for table in tables:
                count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                print(f"{table}: {count} records")
            
            # Show sample incident
            incident = cursor.execute("""
                SELECT report_id, title, failure_date, disconnected_mw, classification
                FROM incidents LIMIT 1
            """).fetchone()
            
            if incident:
                print(f"\nSample incident:")
                print(f"Report ID: {incident[0]}")
                print(f"Title: {incident[1]}")
                print(f"Date: {incident[2]}")
                print(f"Impact: {incident[3]} MW")
                print(f"Classification: {incident[4]}")
                
        finally:
            self.disconnect()

def main():
    """Main execution function"""
    # File paths
    json_file = "power_system_failure_analysis.json"
    project_root = Path(__file__).parent.parent.parent
    db_file = project_root / "platform_data" / "database" / "dark_data.db"
    
    # Check if files exist
    if not os.path.exists(json_file):
        print(f"❌ JSON file not found: {json_file}")
        return
        
    if not os.path.exists(db_file):
        print(f"❌ Database file not found: {db_file}")
        return
    
    # Create ingester and run
    ingester = DataIngester(db_file)
    
    try:
        # Ingest data
        ingester.ingest_json_file(json_file)
        
        # Verify results
        print("\n=== VERIFICATION ===")
        ingester.verify_data()
        
        print(f"\n🎉 Dark data database ready!")
        print(f"📊 Database file: {db_file}")
        print(f"🔍 Ready for RAG queries and MCP integration!")
        
    except Exception as e:
        print(f"❌ Failed to complete ingestion: {e}")

if __name__ == "__main__":
    main()