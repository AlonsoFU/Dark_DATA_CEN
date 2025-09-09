#!/usr/bin/env python3
"""
Simple Web Interface for Power System Failure Analysis
Flask-based web viewer for the database
"""

import sqlite3
import json
from flask import Flask, render_template, request, jsonify
from pathlib import Path

app = Flask(__name__)

class WebViewer:
    def __init__(self, db_path: str = "power_system_analysis.db"):
        self.db_path = db_path
        
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
        
    def get_incidents(self):
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT report_id, title, failure_date, failure_time, 
                       disconnected_mw, classification, document_pages
                FROM incidents
            """)
            return [dict(row) for row in cursor.fetchall()]
            
    def get_incident_details(self, report_id):
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM incidents WHERE report_id = ?
            """, (report_id,))
            row = cursor.fetchone()
            if row:
                incident = dict(row)
                # Parse JSON fields
                for field in ['incident_details', 'affected_installations', 
                             'generation_units', 'transmission_elements', 'technical_summary']:
                    if incident[field]:
                        incident[field] = json.loads(incident[field])
                return incident
            return None
            
    def get_generation_units(self, report_id=None):
        with self.get_connection() as conn:
            if report_id:
                cursor = conn.execute("""
                    SELECT generation_units FROM incidents WHERE report_id = ?
                """, (report_id,))
            else:
                cursor = conn.execute("SELECT generation_units FROM incidents")
                
            units = []
            for row in cursor.fetchall():
                if row['generation_units']:
                    units.extend(json.loads(row['generation_units']))
            return units
            
    def search_incidents(self, search_term):
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT 
                    incidents.report_id,
                    incidents.title,
                    incidents.failure_date,
                    incidents.classification
                FROM incidents
                WHERE incidents.title LIKE ? 
                   OR incidents.failure_cause_text LIKE ?
                   OR incidents.classification LIKE ?
            """, (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
            return [dict(row) for row in cursor.fetchall()]

viewer = WebViewer()

@app.route('/')
def index():
    """Main dashboard"""
    incidents = viewer.get_incidents()
    return render_template('index.html', incidents=incidents)

@app.route('/incident/<report_id>')
def incident_detail(report_id):
    """Detailed view of an incident"""
    incident = viewer.get_incident_details(report_id)
    if not incident:
        return "Incident not found", 404
    return render_template('incident_detail.html', incident=incident)

@app.route('/generation')
def generation():
    """Generation units view"""
    units = viewer.get_generation_units()
    return render_template('generation.html', units=units)

@app.route('/api/search')
def search_api():
    """Search API endpoint"""
    term = request.args.get('q', '')
    if term:
        results = viewer.search_incidents(term)
        return jsonify(results)
    return jsonify([])

# Create templates directory and files
def create_templates():
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Base template
    base_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Power System Analysis{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/"><i class="fas fa-bolt"></i> Power System Analysis</a>
            <div class="navbar-nav">
                <a class="nav-link" href="/">Dashboard</a>
                <a class="nav-link" href="/generation">Generation</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>"""
    
    # Index template
    index_template = """{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-12">
        <h1><i class="fas fa-exclamation-triangle text-warning"></i> Power System Incidents</h1>
        
        <div class="mb-3">
            <input type="text" class="form-control" id="searchInput" placeholder="Search incidents...">
        </div>
        
        <div class="card">
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Report ID</th>
                                <th>Title</th>
                                <th>Date</th>
                                <th>Time</th>
                                <th>MW Lost</th>
                                <th>Classification</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for incident in incidents %}
                            <tr>
                                <td><span class="badge bg-primary">{{ incident.report_id }}</span></td>
                                <td>{{ incident.title[:60] }}{% if incident.title|length > 60 %}...{% endif %}</td>
                                <td>{{ incident.failure_date }}</td>
                                <td>{{ incident.failure_time }}</td>
                                <td><span class="badge bg-danger">{{ incident.disconnected_mw }} MW</span></td>
                                <td><span class="badge bg-warning text-dark">{{ incident.classification }}</span></td>
                                <td>
                                    <a href="/incident/{{ incident.report_id }}" class="btn btn-sm btn-outline-primary">
                                        <i class="fas fa-eye"></i> View Details
                                    </a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
document.getElementById('searchInput').addEventListener('input', function(e) {
    const searchTerm = e.target.value;
    if (searchTerm.length > 2) {
        fetch(`/api/search?q=${encodeURIComponent(searchTerm)}`)
            .then(response => response.json())
            .then(data => {
                console.log('Search results:', data);
                // Update table with search results
            });
    }
});
</script>
{% endblock %}"""
    
    # Incident detail template
    incident_detail_template = """{% extends "base.html" %}

{% block content %}
<div class="row">
    <div class="col-12">
        <a href="/" class="btn btn-outline-secondary mb-3">
            <i class="fas fa-arrow-left"></i> Back to Dashboard
        </a>
        
        <h1>{{ incident.title }}</h1>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card mb-4">
                    <div class="card-header">
                        <h5><i class="fas fa-info-circle"></i> Incident Information</h5>
                    </div>
                    <div class="card-body">
                        <table class="table table-sm">
                            <tr><td><strong>Report ID:</strong></td><td>{{ incident.report_id }}</td></tr>
                            <tr><td><strong>Date:</strong></td><td>{{ incident.failure_date }}</td></tr>
                            <tr><td><strong>Time:</strong></td><td>{{ incident.failure_time }}</td></tr>
                            <tr><td><strong>MW Disconnected:</strong></td><td>{{ incident.disconnected_mw }}</td></tr>
                            <tr><td><strong>Classification:</strong></td><td>{{ incident.classification }}</td></tr>
                        </table>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card mb-4">
                    <div class="card-header">
                        <h5><i class="fas fa-building"></i> Affected Installation</h5>
                    </div>
                    <div class="card-body">
                        {% if incident.affected_installations %}
                        <table class="table table-sm">
                            <tr><td><strong>Name:</strong></td><td>{{ incident.affected_installations.name }}</td></tr>
                            <tr><td><strong>Type:</strong></td><td>{{ incident.affected_installations.type }}</td></tr>
                            <tr><td><strong>Voltage:</strong></td><td>{{ incident.affected_installations.nominal_voltage }}</td></tr>
                            <tr><td><strong>Owner:</strong></td><td>{{ incident.affected_installations.owner }}</td></tr>
                        </table>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card mb-4">
            <div class="card-header">
                <h5><i class="fas fa-exclamation-triangle"></i> Failure Cause</h5>
            </div>
            <div class="card-body">
                <p>{{ incident.failure_cause_text }}</p>
            </div>
        </div>
        
        {% if incident.generation_units %}
        <div class="card mb-4">
            <div class="card-header">
                <h5><i class="fas fa-industry"></i> Affected Generation Units</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Plant</th>
                                <th>Unit</th>
                                <th>Capacity (MW)</th>
                                <th>Technology</th>
                                <th>Disconnection Time</th>
                                <th>Restoration Time</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for unit in incident.generation_units %}
                            <tr>
                                <td>{{ unit.plant_name }}</td>
                                <td>{{ unit.unit_name }}</td>
                                <td>{{ unit.capacity_mw }}</td>
                                <td><span class="badge bg-info">{{ unit.technology_type }}</span></td>
                                <td>{{ unit.disconnection_time }}</td>
                                <td>{{ unit.normalization_time }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}"""
    
    # Write templates
    with open(templates_dir / "base.html", "w", encoding="utf-8") as f:
        f.write(base_template)
    
    with open(templates_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(index_template)
        
    with open(templates_dir / "incident_detail.html", "w", encoding="utf-8") as f:
        f.write(incident_detail_template)

if __name__ == "__main__":
    create_templates()
    print("🌐 Starting web interface...")
    print("📊 Access your data at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
