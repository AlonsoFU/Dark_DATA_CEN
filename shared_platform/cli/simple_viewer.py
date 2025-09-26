#!/usr/bin/env python3
"""
Simple Command-Line Interface for Power System Failure Analysis
No external dependencies required - uses only Python standard library
"""

import sqlite3
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

class SimpleDatabaseViewer:
    """Simple database viewer using only standard library"""
    
    def __init__(self, db_path: str = "power_system_analysis.db"):
        self.db_path = db_path
        
    def create_database_and_load_data(self):
        """Create database from schema and load JSON data"""
        # Create database from schema
        schema_file = "database_schema.sql"
        if not Path(schema_file).exists():
            print(f"❌ Schema file {schema_file} not found!")
            return False
            
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema = f.read()
            
        conn = sqlite3.connect(self.db_path)
        try:
            conn.executescript(schema)
            conn.commit()
            print(f"✅ Database created: {self.db_path}")
        except Exception as e:
            print(f"❌ Error creating database: {e}")
            return False
        
        # Load JSON data
        json_file = "power_system_failure_analysis.json"
        if not Path(json_file).exists():
            print(f"❌ JSON file {json_file} not found!")
            return False
            
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        try:
            # Insert incident data
            incident_data = (
                data['incident_info']['report_id'],
                data['incident_info']['title'],
                data['incident_info']['failure_date'],
                data['incident_info']['failure_time'],
                data['incident_info']['disconnected_consumption_mw'],
                data['incident_info']['classification'],
                json.dumps(data),
                json.dumps(data['incident_info']),
                json.dumps(data['affected_installation']),
                json.dumps(data['generation_units']),
                json.dumps(data['transmission_elements']),
                data['failure_origin_cause'],
                json.dumps(data['technical_details']),
                data['metadata']['document_pages'],
                data['metadata']['extraction_date']
            )
            
            conn.execute("""
                INSERT OR REPLACE INTO incidents (
                    report_id, title, failure_date, failure_time, disconnected_mw,
                    classification, raw_json, incident_details, affected_installations,
                    generation_units, transmission_elements, failure_cause_text,
                    technical_summary, document_pages, extraction_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, incident_data)
            
            # Insert companies
            companies = {
                data['affected_installation']['owner']: (
                    data['affected_installation']['rut'],
                    data['affected_installation']['legal_representative'],
                    data['affected_installation']['address']
                )
            }
            
            for report in data['company_reports']:
                companies[report['company_name']] = ('N/A', 'N/A', 'N/A')
            
            for company_name, (rut, legal_rep, address) in companies.items():
                conn.execute("""
                    INSERT OR REPLACE INTO companies (name, rut, legal_representative, address)
                    VALUES (?, ?, ?, ?)
                """, (company_name, rut, legal_rep, address))
                
            # Get incident and company IDs
            incident_id = conn.execute("SELECT id FROM incidents WHERE report_id = ?", 
                                     (data['incident_info']['report_id'],)).fetchone()[0]
            
            # Insert compliance reports
            for report in data['company_reports']:
                company_id = conn.execute("SELECT id FROM companies WHERE name = ?", 
                                        (report['company_name'],)).fetchone()[0]
                
                conn.execute("""
                    INSERT OR REPLACE INTO compliance_reports 
                    (incident_id, company_id, reports_48h_status, reports_5d_status, compliance_issues)
                    VALUES (?, ?, ?, ?, ?)
                """, (incident_id, company_id, report['reports_48h_status'], 
                     report['reports_5d_status'], json.dumps(report['compliance_issues'])))
            
            # Insert equipment
            eq_data = data['technical_details']['protection_equipment']
            conn.execute("""
                INSERT OR REPLACE INTO equipment 
                (manufacturer, model, installation_date, function_affected, system_number, raw_details)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (eq_data['manufacturer'], eq_data['model'], eq_data['installation_date'],
                 eq_data['function_affected'], eq_data['system_number'], json.dumps(eq_data)))
            
            conn.commit()
            print("✅ Data loaded successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
        finally:
            conn.close()
            
    def view_incidents(self):
        """View all incidents in a formatted table"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("""
            SELECT report_id, title, failure_date, failure_time, 
                   disconnected_mw, classification, document_pages
            FROM incidents
        """)
        
        incidents = cursor.fetchall()
        conn.close()
        
        print("\n" + "="*100)
        print("📊 POWER SYSTEM INCIDENTS")
        print("="*100)
        
        if not incidents:
            print("No incidents found.")
            return
            
        # Print header
        print(f"{'Report ID':<15} {'Date':<12} {'Time':<8} {'MW Lost':<10} {'Classification':<15} {'Title':<50}")
        print("-" * 100)
        
        # Print incidents
        for incident in incidents:
            title = incident['title'][:47] + "..." if len(incident['title']) > 50 else incident['title']
            print(f"{incident['report_id']:<15} {incident['failure_date']:<12} {incident['failure_time']:<8} "
                  f"{incident['disconnected_mw']:<10.1f} {incident['classification']:<15} {title:<50}")
                  
    def view_incident_details(self, report_id: str):
        """View detailed information for a specific incident"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("SELECT * FROM incidents WHERE report_id = ?", (report_id,))
        incident = cursor.fetchone()
        conn.close()
        
        if not incident:
            print(f"❌ Incident {report_id} not found!")
            return
            
        print(f"\n" + "="*80)
        print(f"📋 INCIDENT DETAILS: {report_id}")
        print("="*80)
        
        print(f"Title: {incident['title']}")
        print(f"Date: {incident['failure_date']} at {incident['failure_time']}")
        print(f"MW Disconnected: {incident['disconnected_mw']}")
        print(f"Classification: {incident['classification']}")
        print(f"Document Pages: {incident['document_pages']}")
        
        print(f"\n🔥 FAILURE CAUSE:")
        print("-" * 40)
        print(incident['failure_cause_text'])
        
        # Parse and display generation units
        if incident['generation_units']:
            units = json.loads(incident['generation_units'])
            print(f"\n⚡ AFFECTED GENERATION UNITS ({len(units)} units):")
            print("-" * 80)
            print(f"{'Plant':<25} {'Unit':<8} {'MW':<8} {'Tech':<15} {'Disc.':<8} {'Rest.':<8}")
            print("-" * 80)
            
            for unit in units:
                plant = unit['plant_name'][:22] + "..." if len(unit['plant_name']) > 25 else unit['plant_name']
                print(f"{plant:<25} {unit['unit_name']:<8} {unit['capacity_mw']:<8} "
                      f"{unit['technology_type']:<15} {unit['disconnection_time']:<8} {unit['normalization_time']:<8}")
                      
        # Parse and display transmission elements
        if incident['transmission_elements']:
            elements = json.loads(incident['transmission_elements'])
            print(f"\n🔌 AFFECTED TRANSMISSION ELEMENTS ({len(elements)} elements):")
            print("-" * 80)
            print(f"{'Element':<50} {'Segment':<15} {'Disc.':<8} {'Rest.':<8}")
            print("-" * 80)
            
            for element in elements:
                elem_name = element['element_name'][:47] + "..." if len(element['element_name']) > 50 else element['element_name']
                print(f"{elem_name:<50} {element['segment']:<15} {element['disconnection_time']:<8} {element['normalization_time']:<8}")
                
    def view_generation_summary(self):
        """View summary of affected generation"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("SELECT generation_units FROM incidents")
        incidents = cursor.fetchall()
        conn.close()
        
        all_units = []
        for incident in incidents:
            if incident['generation_units']:
                units = json.loads(incident['generation_units'])
                all_units.extend(units)
                
        if not all_units:
            print("No generation units found.")
            return
            
        print("\n" + "="*100)
        print("⚡ GENERATION UNITS SUMMARY")
        print("="*100)
        
        # Group by technology
        tech_summary = {}
        total_capacity = 0
        
        for unit in all_units:
            tech = unit['technology_type']
            if tech not in tech_summary:
                tech_summary[tech] = {'count': 0, 'capacity': 0}
            tech_summary[tech]['count'] += 1
            tech_summary[tech]['capacity'] += unit['capacity_mw']
            total_capacity += unit['capacity_mw']
            
        print(f"{'Technology':<20} {'Units':<8} {'Total MW':<12} {'Percentage':<12}")
        print("-" * 60)
        
        for tech, data in tech_summary.items():
            percentage = (data['capacity'] / total_capacity) * 100
            print(f"{tech:<20} {data['count']:<8} {data['capacity']:<12.1f} {percentage:<12.1f}%")
            
        print("-" * 60)
        print(f"{'TOTAL':<20} {len(all_units):<8} {total_capacity:<12.1f} {'100.0%':<12}")
        
    def view_compliance_summary(self):
        """View compliance reports summary"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("""
            SELECT 
                c.name as company_name,
                cr.reports_48h_status,
                cr.reports_5d_status,
                cr.compliance_issues
            FROM compliance_reports cr
            JOIN companies c ON cr.company_id = c.id
        """)
        
        reports = cursor.fetchall()
        conn.close()
        
        if not reports:
            print("No compliance reports found.")
            return
            
        print("\n" + "="*100)
        print("📊 COMPLIANCE REPORTS SUMMARY")
        print("="*100)
        
        print(f"{'Company':<30} {'48h Status':<40} {'5d Status':<40}")
        print("-" * 100)
        
        for report in reports:
            company = report['company_name'][:27] + "..." if len(report['company_name']) > 30 else report['company_name']
            status_48h = report['reports_48h_status'][:37] + "..." if len(report['reports_48h_status']) > 40 else report['reports_48h_status']
            status_5d = report['reports_5d_status'][:37] + "..." if len(report['reports_5d_status']) > 40 else report['reports_5d_status']
            
            print(f"{company:<30} {status_48h:<40} {status_5d:<40}")
            
            # Show compliance issues if any
            if report['compliance_issues']:
                issues = json.loads(report['compliance_issues'])
                if issues:
                    print(f"{'':>30} Issues: {', '.join(issues)}")
                    
    def search_text(self, search_term: str):
        """Search in incident text"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("""
            SELECT report_id, title, failure_date, classification, failure_cause_text
            FROM incidents
            WHERE title LIKE ? OR failure_cause_text LIKE ? OR classification LIKE ?
        """, (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        
        results = cursor.fetchall()
        conn.close()
        
        print(f"\n🔍 SEARCH RESULTS for '{search_term}':")
        print("="*80)
        
        if not results:
            print("No results found.")
            return
            
        for result in results:
            print(f"\n📋 {result['report_id']} - {result['failure_date']}")
            print(f"Title: {result['title']}")
            print(f"Classification: {result['classification']}")
            
            # Show context where search term appears
            cause_text = result['failure_cause_text']
            if search_term.lower() in cause_text.lower():
                # Find and show context around the search term
                start = max(0, cause_text.lower().find(search_term.lower()) - 50)
                end = min(len(cause_text), start + 150)
                context = "..." + cause_text[start:end] + "..."
                print(f"Context: {context}")
                
    def interactive_menu(self):
        """Interactive command-line menu"""
        while True:
            print("\n" + "="*60)
            print("🔧 POWER SYSTEM FAILURE ANALYSIS - DATABASE VIEWER")
            print("="*60)
            print("1. 📊 View all incidents")
            print("2. 📋 View incident details")
            print("3. ⚡ View generation summary")
            print("4. 📊 View compliance summary")
            print("5. 🔍 Search incidents")
            print("6. 🗄️  Create/reload database")
            print("0. ❌ Exit")
            print("-" * 60)
            
            choice = input("Enter your choice (0-6): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                self.view_incidents()
            elif choice == "2":
                report_id = input("Enter report ID (e.g., EAF-089/2025): ").strip()
                if report_id:
                    self.view_incident_details(report_id)
            elif choice == "3":
                self.view_generation_summary()
            elif choice == "4":
                self.view_compliance_summary()
            elif choice == "5":
                search_term = input("Enter search term: ").strip()
                if search_term:
                    self.search_text(search_term)
            elif choice == "6":
                self.create_database_and_load_data()
            else:
                print("❌ Invalid choice. Please try again.")
                
            input("\nPress Enter to continue...")

def main():
    """Main function"""
    viewer = SimpleDatabaseViewer()
    
    # Check if database exists
    if not Path(viewer.db_path).exists():
        print("🔧 Database not found. Creating database and loading data...")
        viewer.create_database_and_load_data()
    
    # Start interactive menu
    viewer.interactive_menu()

if __name__ == "__main__":
    main()
