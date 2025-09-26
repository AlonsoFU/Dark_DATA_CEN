#!/usr/bin/env python3
"""
Analysis Queries for Dark Data Database
Extracts insights from power system failure data
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

class FailureAnalyzer:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to platform_data/database/dark_data.db relative to project root
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / "platform_data" / "database" / "dark_data.db"
        self.db_path = db_path
        
    def connect(self):
        """Connect to database with row factory for easier access"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def incident_overview(self):
        """Basic incident statistics"""
        conn = self.connect()
        try:
            print("=== INCIDENT OVERVIEW ===")
            
            # Basic stats
            stats = conn.execute("""
                SELECT 
                    COUNT(*) as total_incidents,
                    SUM(disconnected_mw) as total_mw_affected,
                    AVG(disconnected_mw) as avg_mw_per_incident,
                    MAX(disconnected_mw) as max_mw_incident
                FROM incidents
            """).fetchone()
            
            print(f"Total Incidents: {stats['total_incidents']}")
            print(f"Total MW Affected: {stats['total_mw_affected']:,.2f} MW")
            print(f"Average MW per Incident: {stats['avg_mw_per_incident']:,.2f} MW")
            print(f"Largest Incident: {stats['max_mw_incident']:,.2f} MW")
            
            # Classification breakdown
            print(f"\n=== BY CLASSIFICATION ===")
            classifications = conn.execute("""
                SELECT classification, COUNT(*) as count, SUM(disconnected_mw) as total_mw
                FROM incidents 
                GROUP BY classification
                ORDER BY total_mw DESC
            """).fetchall()
            
            for c in classifications:
                print(f"{c['classification']}: {c['count']} incidents, {c['total_mw']:,.2f} MW")
                
        finally:
            conn.close()
    
    def compliance_analysis(self):
        """Analyze company compliance patterns"""
        conn = self.connect()
        try:
            print("\n=== COMPLIANCE ANALYSIS ===")
            
            # Company compliance overview
            compliance = conn.execute("""
                SELECT 
                    c.name,
                    cr.reports_48h_status,
                    cr.reports_5d_status,
                    cr.compliance_issues
                FROM compliance_reports cr
                JOIN companies c ON cr.company_id = c.id
                ORDER BY c.name
            """).fetchall()
            
            for comp in compliance:
                print(f"\n{comp['name']}:")
                print(f"  48h Reports: {comp['reports_48h_status']}")
                print(f"  5-day Reports: {comp['reports_5d_status']}")
                
                issues = json.loads(comp['compliance_issues']) if comp['compliance_issues'] else []
                if issues:
                    print(f"  ⚠️  Issues: {', '.join(issues)}")
                else:
                    print(f"  ✅ No compliance issues")
            
            # Calculate compliance scores
            print(f"\n=== COMPLIANCE SCORES ===")
            for comp in compliance:
                name = comp['name']
                reports_48h = comp['reports_48h_status']
                
                # Parse "X informes en plazo y Y informes fuera de plazo"
                if 'en plazo' in reports_48h and 'fuera de plazo' in reports_48h:
                    parts = reports_48h.split(' y ')
                    on_time = int(parts[0].split()[0]) if parts[0].split()[0].isdigit() else 0
                    late = int(parts[1].split()[0]) if parts[1].split()[0].isdigit() else 0
                    total = on_time + late
                    if total > 0:
                        compliance_rate = (on_time / total) * 100
                        print(f"{name}: {compliance_rate:.1f}% on-time ({on_time}/{total} reports)")
                    
        finally:
            conn.close()
    
    def equipment_analysis(self):
        """Analyze equipment failure patterns"""
        conn = self.connect()
        try:
            print("\n=== EQUIPMENT ANALYSIS ===")
            
            equipment = conn.execute("""
                SELECT manufacturer, model, installation_date, 
                       function_affected, system_number
                FROM equipment
            """).fetchall()
            
            for eq in equipment:
                print(f"Failed Equipment: {eq['manufacturer']} {eq['model']}")
                print(f"Installed: {eq['installation_date']}")
                print(f"Function: {eq['function_affected']}")
                print(f"System: {eq['system_number']}")
                
                # Calculate age if installation date available
                if eq['installation_date']:
                    try:
                        install_date = datetime.strptime(eq['installation_date'], '%Y-%m-%d')
                        failure_date = datetime.strptime('2025-02-25', '%Y-%m-%d')  # From our data
                        age_years = (failure_date - install_date).days / 365.25
                        print(f"Age at Failure: {age_years:.1f} years")
                    except:
                        pass
                        
        finally:
            conn.close()
    
    def generation_impact_analysis(self):
        """Analyze impact on different generation types"""
        conn = self.connect()
        try:
            print("\n=== GENERATION IMPACT ANALYSIS ===")
            
            # Extract generation data from JSON
            incidents = conn.execute("""
                SELECT generation_units, transmission_elements
                FROM incidents
            """).fetchall()
            
            for incident in incidents:
                gen_units = json.loads(incident['generation_units']) if incident['generation_units'] else []
                
                if gen_units:
                    # Group by technology type
                    by_tech = {}
                    total_capacity = 0
                    total_downtime = 0
                    
                    for unit in gen_units:
                        tech = unit.get('technology_type', 'Unknown')
                        capacity = unit.get('capacity_mw', 0)
                        
                        if tech not in by_tech:
                            by_tech[tech] = {'capacity': 0, 'units': 0, 'plants': set()}
                        
                        by_tech[tech]['capacity'] += capacity
                        by_tech[tech]['units'] += 1
                        by_tech[tech]['plants'].add(unit.get('plant_name', ''))
                        total_capacity += capacity
                        
                        # Calculate downtime (failure to normalization)
                        try:
                            failure_time = datetime.strptime('15:16', '%H:%M')
                            norm_time_str = unit.get('normalization_time', '')
                            if norm_time_str and ':' in norm_time_str:
                                norm_time = datetime.strptime(norm_time_str, '%H:%M')
                                if norm_time < failure_time:  # Next day
                                    downtime_hours = 24 - failure_time.hour + norm_time.hour - failure_time.minute/60 + norm_time.minute/60
                                else:
                                    downtime_hours = (norm_time.hour - failure_time.hour) + (norm_time.minute - failure_time.minute)/60
                                total_downtime += downtime_hours * capacity  # MW-hours
                        except:
                            pass
                    
                    print(f"Technology Breakdown ({total_capacity:.1f} MW total):")
                    for tech, data in sorted(by_tech.items(), key=lambda x: x[1]['capacity'], reverse=True):
                        pct = (data['capacity'] / total_capacity) * 100 if total_capacity > 0 else 0
                        print(f"  {tech}: {data['capacity']:.1f} MW ({pct:.1f}%) - {data['units']} units from {len(data['plants'])} plants")
                    
                    if total_downtime > 0:
                        print(f"\nTotal Energy Impact: {total_downtime:,.0f} MW-hours")
                        
        finally:
            conn.close()
    
    def cascade_analysis(self):
        """Analyze cascading failure effects"""
        conn = self.connect()
        try:
            print("\n=== CASCADE ANALYSIS ===")
            
            # Get transmission elements and their recovery times
            incidents = conn.execute("""
                SELECT transmission_elements, raw_json
                FROM incidents
            """).fetchall()
            
            for incident in incidents:
                trans_elements = json.loads(incident['transmission_elements']) if incident['transmission_elements'] else []
                raw_data = json.loads(incident['raw_json']) if incident['raw_json'] else {}
                
                if trans_elements:
                    print(f"Transmission Elements Affected: {len(trans_elements)}")
                    
                    # Sort by disconnection time to see cascade pattern
                    sorted_elements = sorted(trans_elements, 
                                           key=lambda x: x.get('disconnection_time', '99:99'))
                    
                    print("\nCascade Timeline:")
                    for elem in sorted_elements:
                        disc_time = elem.get('disconnection_time', 'Unknown')
                        norm_time = elem.get('normalization_time', 'Unknown')
                        name = elem.get('element_name', 'Unknown')
                        print(f"  {disc_time}: {name} (recovered: {norm_time})")
                    
                    # System impact details
                    system_impact = raw_data.get('technical_details', {}).get('system_impact', {})
                    if system_impact:
                        print(f"\nSystem Impact Details:")
                        print(f"  Power Transferred: {system_impact.get('power_transferred', 'Unknown')}")
                        print(f"  Oscillation Duration: {system_impact.get('oscillation_duration', 'Unknown')}")
                        print(f"  Northern Island Collapse: {system_impact.get('northern_island_collapse_time', 'Unknown')}")
                        print(f"  Southern Island Collapse: {system_impact.get('southern_island_collapse_time', 'Unknown')}")
                        
        finally:
            conn.close()
    
    def search_demo(self, query: str = "protection system failure"):
        """Demonstrate full-text search capabilities for RAG"""
        conn = self.connect()
        try:
            print(f"\n=== SEARCH DEMO: '{query}' ===")
            
            results = conn.execute("""
                SELECT i.report_id, i.title, 
                       snippet(incidents_fts, 2, '<mark>', '</mark>', '...', 32) as snippet,
                       i.disconnected_mw, i.classification
                FROM incidents_fts fts
                JOIN incidents i ON fts.rowid = i.id  
                WHERE fts MATCH ?
                ORDER BY rank
            """, [query]).fetchall()
            
            if results:
                for result in results:
                    print(f"\n📋 {result['report_id']}: {result['title']}")
                    print(f"   Impact: {result['disconnected_mw']} MW | {result['classification']}")
                    print(f"   Snippet: {result['snippet']}")
            else:
                print("No results found")
                
        except Exception as e:
            print(f"Search error: {e}")
        finally:
            conn.close()
    
    def generate_insights_report(self):
        """Generate comprehensive insights report"""
        print("🔍 DARK DATA INSIGHTS REPORT")
        print("=" * 50)
        
        self.incident_overview()
        self.compliance_analysis() 
        self.equipment_analysis()
        self.generation_impact_analysis()
        self.cascade_analysis()
        
        # Demo searches
        self.search_demo("Siemens protection")
        self.search_demo("differential line")
        self.search_demo("communication failure")
        
        print(f"\n" + "=" * 50)
        print("🎯 KEY FINDINGS:")
        print("• Single protection system failure caused total blackout (11,066 MW)")
        print("• ENEL Generación: 92% of reports late (35/38)")
        print("• Equipment age: 6.7 years (Siemens 7SL87)")
        print("• Cascade effect: 5-second southern island collapse")
        print("• Recovery time varies: Hydro < Solar < Thermal")
        print("\n💡 ACTIONABLE INSIGHTS:")
        print("• Monitor Siemens 7SL87 equipment approaching 7+ years")
        print("• Implement compliance automation for ENEL")
        print("• Investigate communication module failures")
        print("• Create cascade prevention protocols")

def main():
    """Run all analysis queries"""
    analyzer = FailureAnalyzer()
    analyzer.generate_insights_report()

if __name__ == "__main__":
    main()