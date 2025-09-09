#!/usr/bin/env python3
"""
Simple Web Dashboard for Dark Data Database
Visualizes power system failure patterns and insights
"""

import sqlite3
import json
from flask import Flask, render_template, request, jsonify
from datetime import datetime
import os
from pathlib import Path

app = Flask(__name__)

class DashboardData:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to data/databases/dark_data.db relative to project root
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / "data" / "databases" / "dark_data.db"
        self.db_path = str(db_path)
        
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_overview_stats(self):
        """Get basic overview statistics"""
        conn = self.get_connection()
        try:
            stats = conn.execute("""
                SELECT 
                    COUNT(*) as total_incidents,
                    SUM(disconnected_mw) as total_mw_affected,
                    AVG(disconnected_mw) as avg_mw_per_incident,
                    MAX(disconnected_mw) as max_mw_incident
                FROM incidents
            """).fetchone()
            return dict(stats)
        finally:
            conn.close()
    
    def get_compliance_data(self):
        """Get compliance data for visualization"""
        conn = self.get_connection()
        try:
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
            
            compliance_scores = []
            for comp in compliance:
                name = comp['name']
                reports_48h = comp['reports_48h_status']
                
                # Parse compliance rate
                if 'en plazo' in reports_48h and 'fuera de plazo' in reports_48h:
                    parts = reports_48h.split(' y ')
                    on_time = int(parts[0].split()[0]) if parts[0].split()[0].isdigit() else 0
                    late = int(parts[1].split()[0]) if parts[1].split()[0].isdigit() else 0
                    total = on_time + late
                    compliance_rate = (on_time / total) * 100 if total > 0 else 0
                    
                    compliance_scores.append({
                        'name': name,
                        'compliance_rate': compliance_rate,
                        'on_time': on_time,
                        'late': late,
                        'total': total,
                        'issues': json.loads(comp['compliance_issues']) if comp['compliance_issues'] else []
                    })
            
            return compliance_scores
        finally:
            conn.close()
    
    def get_generation_data(self):
        """Get generation impact data"""
        conn = self.get_connection()
        try:
            incidents = conn.execute("""
                SELECT generation_units FROM incidents
            """).fetchall()
            
            tech_breakdown = {}
            total_capacity = 0
            
            for incident in incidents:
                gen_units = json.loads(incident['generation_units']) if incident['generation_units'] else []
                
                for unit in gen_units:
                    tech = unit.get('technology_type', 'Unknown')
                    capacity = unit.get('capacity_mw', 0)
                    
                    if tech not in tech_breakdown:
                        tech_breakdown[tech] = {'capacity': 0, 'units': 0, 'plants': set()}
                    
                    tech_breakdown[tech]['capacity'] += capacity
                    tech_breakdown[tech]['units'] += 1
                    tech_breakdown[tech]['plants'].add(unit.get('plant_name', ''))
                    total_capacity += capacity
            
            # Convert to list for JSON serialization
            tech_data = []
            for tech, data in tech_breakdown.items():
                tech_data.append({
                    'technology': tech,
                    'capacity': data['capacity'],
                    'units': data['units'],
                    'plants': len(data['plants']),
                    'percentage': (data['capacity'] / total_capacity) * 100 if total_capacity > 0 else 0
                })
            
            return sorted(tech_data, key=lambda x: x['capacity'], reverse=True)
        finally:
            conn.close()
    
    def get_equipment_data(self):
        """Get equipment failure data"""
        conn = self.get_connection()
        try:
            equipment = conn.execute("""
                SELECT manufacturer, model, installation_date, 
                       function_affected, system_number
                FROM equipment
            """).fetchall()
            
            equipment_list = []
            for eq in equipment:
                age_years = None
                if eq['installation_date']:
                    try:
                        install_date = datetime.strptime(eq['installation_date'], '%Y-%m-%d')
                        failure_date = datetime.strptime('2025-02-25', '%Y-%m-%d')
                        age_years = round((failure_date - install_date).days / 365.25, 1)
                    except:
                        pass
                
                equipment_list.append({
                    'manufacturer': eq['manufacturer'],
                    'model': eq['model'],
                    'installation_date': eq['installation_date'],
                    'function_affected': eq['function_affected'],
                    'system_number': eq['system_number'],
                    'age_years': age_years
                })
            
            return equipment_list
        finally:
            conn.close()
    
    def search_incidents(self, query: str):
        """Search incidents using full-text search"""
        conn = self.get_connection()
        try:
            # Simple LIKE search since FTS5 had issues
            results = conn.execute("""
                SELECT report_id, title, failure_cause_text, 
                       disconnected_mw, classification, failure_date
                FROM incidents
                WHERE title LIKE ? OR failure_cause_text LIKE ?
                ORDER BY failure_date DESC
            """, [f"%{query}%", f"%{query}%"]).fetchall()
            
            return [dict(row) for row in results]
        finally:
            conn.close()

# Initialize data provider
dashboard_data = DashboardData()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/overview')
def api_overview():
    """API endpoint for overview statistics"""
    return jsonify(dashboard_data.get_overview_stats())

@app.route('/api/compliance')
def api_compliance():
    """API endpoint for compliance data"""
    return jsonify(dashboard_data.get_compliance_data())

@app.route('/api/generation')
def api_generation():
    """API endpoint for generation impact data"""
    return jsonify(dashboard_data.get_generation_data())

@app.route('/api/equipment')
def api_equipment():
    """API endpoint for equipment data"""
    return jsonify(dashboard_data.get_equipment_data())

@app.route('/api/search')
def api_search():
    """API endpoint for searching incidents"""
    query = request.args.get('q', '')
    if query:
        results = dashboard_data.search_incidents(query)
        return jsonify(results)
    return jsonify([])

def main():
    """Main entry point for the dashboard."""
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("🌐 Starting Dark Data Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("🔍 Features: Overview, Compliance Tracking, Generation Impact, Equipment Analysis")
    
    app.run(debug=True, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()