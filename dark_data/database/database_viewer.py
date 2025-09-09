#!/usr/bin/env python3
"""
Database Viewer for Power System Failure Analysis
Provides multiple ways to view and query the database
"""

import sqlite3
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional

class DatabaseViewer:
    """Database viewer and query interface"""
    
    def __init__(self, db_path: str = "power_system_analysis.db"):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Connect to the database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        return self.conn
        
    def disconnect(self):
        """Disconnect from database"""
        if self.conn:
            self.conn.close()
            
    def create_database(self, schema_file: str = "database_schema.sql"):
        """Create database from schema file"""
        if not Path(schema_file).exists():
            print(f"Schema file {schema_file} not found!")
            return False
            
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema = f.read()
            
        self.connect()
        try:
            self.conn.executescript(schema)
            self.conn.commit()
            print(f"Database created successfully: {self.db_path}")
            return True
        except Exception as e:
            print(f"Error creating database: {e}")
            return False
        finally:
            self.disconnect()
            
    def load_json_data(self, json_file: str = "power_system_failure_analysis.json"):
        """Load data from JSON file into database"""
        if not Path(json_file).exists():
            print(f"JSON file {json_file} not found!")
            return False
            
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        self.connect()
        try:
            # Insert incident data
            incident_data = {
                'report_id': data['incident_info']['report_id'],
                'title': data['incident_info']['title'],
                'failure_date': data['incident_info']['failure_date'],
                'failure_time': data['incident_info']['failure_time'],
                'disconnected_mw': data['incident_info']['disconnected_consumption_mw'],
                'classification': data['incident_info']['classification'],
                'raw_json': json.dumps(data),
                'incident_details': json.dumps(data['incident_info']),
                'affected_installations': json.dumps(data['affected_installation']),
                'generation_units': json.dumps(data['generation_units']),
                'transmission_elements': json.dumps(data['transmission_elements']),
                'failure_cause_text': data['failure_origin_cause'],
                'technical_summary': json.dumps(data['technical_details']),
                'document_pages': data['metadata']['document_pages'],
                'extraction_date': data['metadata']['extraction_date']
            }
            
            self.conn.execute("""
                INSERT OR REPLACE INTO incidents (
                    report_id, title, failure_date, failure_time, disconnected_mw,
                    classification, raw_json, incident_details, affected_installations,
                    generation_units, transmission_elements, failure_cause_text,
                    technical_summary, document_pages, extraction_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple(incident_data.values()))
            
            # Insert company data
            companies = {
                data['affected_installation']['owner']: {
                    'rut': data['affected_installation']['rut'],
                    'legal_representative': data['affected_installation']['legal_representative'],
                    'address': data['affected_installation']['address']
                }
            }
            
            # Add companies from compliance reports
            for report in data['company_reports']:
                companies[report['company_name']] = {
                    'rut': 'N/A',
                    'legal_representative': 'N/A', 
                    'address': 'N/A'
                }
            
            for company_name, info in companies.items():
                self.conn.execute("""
                    INSERT OR REPLACE INTO companies (name, rut, legal_representative, address)
                    VALUES (?, ?, ?, ?)
                """, (company_name, info['rut'], info['legal_representative'], info['address']))
                
            # Insert compliance reports
            incident_id = self.conn.execute("SELECT id FROM incidents WHERE report_id = ?", 
                                          (data['incident_info']['report_id'],)).fetchone()[0]
            
            for report in data['company_reports']:
                company_id = self.conn.execute("SELECT id FROM companies WHERE name = ?", 
                                             (report['company_name'],)).fetchone()[0]
                
                self.conn.execute("""
                    INSERT OR REPLACE INTO compliance_reports 
                    (incident_id, company_id, reports_48h_status, reports_5d_status, compliance_issues)
                    VALUES (?, ?, ?, ?, ?)
                """, (incident_id, company_id, report['reports_48h_status'], 
                     report['reports_5d_status'], json.dumps(report['compliance_issues'])))
            
            # Insert equipment data
            equipment_data = data['technical_details']['protection_equipment']
            self.conn.execute("""
                INSERT OR REPLACE INTO equipment 
                (manufacturer, model, installation_date, function_affected, system_number, raw_details)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (equipment_data['manufacturer'], equipment_data['model'],
                 equipment_data['installation_date'], equipment_data['function_affected'],
                 equipment_data['system_number'], json.dumps(equipment_data)))
            
            self.conn.commit()
            print("Data loaded successfully!")
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
        finally:
            self.disconnect()
            
    def view_incidents(self) -> pd.DataFrame:
        """View all incidents"""
        self.connect()
        try:
            df = pd.read_sql_query("""
                SELECT report_id, title, failure_date, failure_time, 
                       disconnected_mw, classification, document_pages
                FROM incidents
            """, self.conn)
            return df
        finally:
            self.disconnect()
            
    def view_failure_summary(self) -> pd.DataFrame:
        """View failure summary using the database view"""
        self.connect()
        try:
            df = pd.read_sql_query("SELECT * FROM failure_summary", self.conn)
            return df
        finally:
            self.disconnect()
            
    def view_generation_units(self, report_id: str = None) -> pd.DataFrame:
        """View generation units affected"""
        self.connect()
        try:
            query = """
                SELECT report_id, title, generation_units 
                FROM incidents
            """
            if report_id:
                query += " WHERE report_id = ?"
                df = pd.read_sql_query(query, self.conn, params=(report_id,))
            else:
                df = pd.read_sql_query(query, self.conn)
            
            # Parse JSON generation units
            units_list = []
            for _, row in df.iterrows():
                units = json.loads(row['generation_units'])
                for unit in units:
                    unit['report_id'] = row['report_id']
                    units_list.append(unit)
                    
            return pd.DataFrame(units_list)
        finally:
            self.disconnect()
            
    def view_transmission_elements(self, report_id: str = None) -> pd.DataFrame:
        """View transmission elements affected"""
        self.connect()
        try:
            query = """
                SELECT report_id, title, transmission_elements 
                FROM incidents
            """
            if report_id:
                query += " WHERE report_id = ?"
                df = pd.read_sql_query(query, self.conn, params=(report_id,))
            else:
                df = pd.read_sql_query(query, self.conn)
            
            # Parse JSON transmission elements
            elements_list = []
            for _, row in df.iterrows():
                elements = json.loads(row['transmission_elements'])
                for element in elements:
                    element['report_id'] = row['report_id']
                    elements_list.append(element)
                    
            return pd.DataFrame(elements_list)
        finally:
            self.disconnect()
            
    def view_compliance_reports(self) -> pd.DataFrame:
        """View compliance reports with company info"""
        self.connect()
        try:
            df = pd.read_sql_query("""
                SELECT 
                    i.report_id,
                    c.name as company_name,
                    cr.reports_48h_status,
                    cr.reports_5d_status,
                    cr.compliance_issues
                FROM compliance_reports cr
                JOIN companies c ON cr.company_id = c.id
                JOIN incidents i ON cr.incident_id = i.id
            """, self.conn)
            return df
        finally:
            self.disconnect()
            
    def search_full_text(self, search_term: str) -> pd.DataFrame:
        """Full-text search across incidents"""
        self.connect()
        try:
            df = pd.read_sql_query("""
                SELECT 
                    incidents.report_id,
                    incidents.title,
                    incidents.failure_date,
                    incidents.classification,
                    snippet(incidents_fts, 2, '<b>', '</b>', '...', 32) as snippet
                FROM incidents_fts
                JOIN incidents ON incidents.rowid = incidents_fts.rowid
                WHERE incidents_fts MATCH ?
            """, self.conn, params=(search_term,))
            return df
        finally:
            self.disconnect()
            
    def custom_query(self, query: str) -> pd.DataFrame:
        """Execute custom SQL query"""
        self.connect()
        try:
            df = pd.read_sql_query(query, self.conn)
            return df
        finally:
            self.disconnect()
            
    def export_to_excel(self, filename: str = "power_system_analysis.xlsx"):
        """Export all data to Excel file with multiple sheets"""
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Export incidents
            incidents_df = self.view_incidents()
            incidents_df.to_excel(writer, sheet_name='Incidents', index=False)
            
            # Export generation units
            gen_df = self.view_generation_units()
            gen_df.to_excel(writer, sheet_name='Generation_Units', index=False)
            
            # Export transmission elements
            trans_df = self.view_transmission_elements()
            trans_df.to_excel(writer, sheet_name='Transmission_Elements', index=False)
            
            # Export compliance reports
            comp_df = self.view_compliance_reports()
            comp_df.to_excel(writer, sheet_name='Compliance_Reports', index=False)
            
        print(f"Data exported to {filename}")

def main():
    """Demonstrate database viewer functionality"""
    viewer = DatabaseViewer()
    
    print("🔧 Creating database...")
    if viewer.create_database():
        print("✅ Database created successfully")
    
    print("\n📊 Loading JSON data...")
    if viewer.load_json_data():
        print("✅ Data loaded successfully")
    
    print("\n📋 Viewing incidents:")
    incidents = viewer.view_incidents()
    print(incidents)
    
    print("\n📈 Viewing failure summary:")
    summary = viewer.view_failure_summary()
    print(summary)
    
    print("\n⚡ Viewing generation units:")
    gen_units = viewer.view_generation_units()
    print(gen_units.head())
    
    print("\n🔌 Viewing transmission elements:")
    trans_elements = viewer.view_transmission_elements()
    print(trans_elements.head())
    
    print("\n📊 Exporting to Excel...")
    viewer.export_to_excel()
    
    print("\n🔍 Full-text search example (searching for 'protección'):")
    search_results = viewer.search_full_text("protección")
    print(search_results)

if __name__ == "__main__":
    main()
