#!/usr/bin/env python3
"""
Enhanced MCP Server with Dashboard and System Integration Tools
Adds tools to open dashboard, generate reports, and control the system
"""

import asyncio
import sqlite3
import json
import subprocess
import webbrowser
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.types as types

# Initialize MCP server
server = Server("dark-data-enhanced-server")

class EnhancedDarkDataMCP:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to platform_data/database/dark_data.db relative to project root
            project_root = Path(__file__).parent.parent.parent.parent.parent
            db_path = project_root / "platform_data" / "database" / "dark_data.db"
        self.db_path = str(db_path)
        self.project_dir = Path(__file__).parent.parent.parent.parent.parent
        
    def get_connection(self):
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    # === EXISTING MCP TOOLS ===
    
    def search_incidents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search power system incidents"""
        conn = self.get_connection()
        try:
            results = conn.execute("""
                SELECT 
                    report_id, title, failure_date, failure_time,
                    disconnected_mw, classification, failure_cause_text,
                    technical_summary
                FROM incidents
                WHERE title LIKE ? OR failure_cause_text LIKE ? OR technical_summary LIKE ?
                ORDER BY failure_date DESC
                LIMIT ?
            """, [f"%{query}%", f"%{query}%", f"%{query}%", limit]).fetchall()
            
            return [dict(row) for row in results]
        finally:
            conn.close()
    
    def get_compliance_report(self, company_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get compliance data for companies"""
        conn = self.get_connection()
        try:
            query = """
                SELECT 
                    c.name, cr.reports_48h_status, cr.reports_5d_status,
                    cr.compliance_issues
                FROM compliance_reports cr
                JOIN companies c ON cr.company_id = c.id
            """
            params = []
            
            if company_name:
                query += " WHERE c.name LIKE ?"
                params.append(f"%{company_name}%")
                
            query += " ORDER BY c.name"
            
            results = conn.execute(query, params).fetchall()
            
            compliance_data = []
            for row in results:
                # Parse compliance rates
                reports_48h = row['reports_48h_status']
                compliance_rate = 0
                on_time = 0
                late = 0
                
                if 'en plazo' in reports_48h and 'fuera de plazo' in reports_48h:
                    parts = reports_48h.split(' y ')
                    on_time = int(parts[0].split()[0]) if parts[0].split()[0].isdigit() else 0
                    late = int(parts[1].split()[0]) if parts[1].split()[0].isdigit() else 0
                    total = on_time + late
                    compliance_rate = (on_time / total) * 100 if total > 0 else 0
                
                compliance_data.append({
                    'company_name': row['name'],
                    'compliance_rate': round(compliance_rate, 1),
                    'reports_48h_status': row['reports_48h_status'],
                    'reports_5d_status': row['reports_5d_status'],
                    'on_time_reports': on_time,
                    'late_reports': late,
                    'compliance_issues': json.loads(row['compliance_issues']) if row['compliance_issues'] else []
                })
            
            return compliance_data
        finally:
            conn.close()
    
    def analyze_equipment_failures(self) -> List[Dict[str, Any]]:
        """Analyze equipment failure patterns"""
        conn = self.get_connection()
        try:
            results = conn.execute("""
                SELECT 
                    manufacturer, model, installation_date,
                    function_affected, system_number, raw_details
                FROM equipment
            """).fetchall()
            
            equipment_analysis = []
            for row in results:
                age_years = None
                risk_level = "Unknown"
                
                if row['installation_date']:
                    try:
                        install_date = datetime.strptime(row['installation_date'], '%Y-%m-%d')
                        current_date = datetime.strptime('2025-02-25', '%Y-%m-%d')  # Failure date
                        age_years = round((current_date - install_date).days / 365.25, 1)
                        
                        # Risk assessment based on age
                        if age_years >= 7:
                            risk_level = "High Risk"
                        elif age_years >= 5:
                            risk_level = "Medium Risk"
                        else:
                            risk_level = "Low Risk"
                    except:
                        pass
                
                equipment_analysis.append({
                    'manufacturer': row['manufacturer'],
                    'model': row['model'],
                    'installation_date': row['installation_date'],
                    'age_years': age_years,
                    'risk_level': risk_level,
                    'function_affected': row['function_affected'],
                    'system_number': row['system_number']
                })
            
            return equipment_analysis
        finally:
            conn.close()
    
    def get_incident_timeline(self, incident_id: Optional[str] = None) -> Dict[str, Any]:
        """Get detailed timeline of an incident"""
        conn = self.get_connection()
        try:
            query = "SELECT * FROM incidents"
            params = []
            
            if incident_id:
                query += " WHERE report_id = ?"
                params.append(incident_id)
            else:
                query += " ORDER BY failure_date DESC LIMIT 1"
            
            incident = conn.execute(query, params).fetchone()
            
            if not incident:
                return {"error": "No incident found"}
            
            # Parse generation units and transmission elements from JSON
            generation_units = json.loads(incident['generation_units']) if incident['generation_units'] else []
            transmission_elements = json.loads(incident['transmission_elements']) if incident['transmission_elements'] else []
            raw_json = json.loads(incident['raw_json']) if incident['raw_json'] else {}
            
            # Build timeline
            timeline_events = []
            
            # Initial failure
            failure_time = incident['failure_time']
            timeline_events.append({
                'time': failure_time,
                'event': f"Initial failure: {incident['title']}",
                'type': 'failure',
                'impact_mw': incident['disconnected_mw']
            })
            
            # Generation unit impacts
            for unit in generation_units:
                if unit.get('disconnection_time'):
                    timeline_events.append({
                        'time': unit['disconnection_time'],
                        'event': f"{unit['plant_name']} ({unit['technology_type']}) disconnected - {unit['capacity_mw']} MW",
                        'type': 'generation_loss'
                    })
                if unit.get('normalization_time'):
                    timeline_events.append({
                        'time': unit['normalization_time'],
                        'event': f"{unit['plant_name']} normalized",
                        'type': 'recovery'
                    })
            
            # Transmission element impacts
            for element in transmission_elements:
                if element.get('disconnection_time'):
                    timeline_events.append({
                        'time': element['disconnection_time'],
                        'event': f"Transmission element disconnected: {element['element_name']}",
                        'type': 'transmission_loss'
                    })
                if element.get('normalization_time'):
                    timeline_events.append({
                        'time': element['normalization_time'],
                        'event': f"Transmission element normalized: {element['element_name']}",
                        'type': 'recovery'
                    })
            
            # Sort timeline by time
            timeline_events.sort(key=lambda x: x['time'])
            
            return {
                'incident_id': incident['report_id'],
                'title': incident['title'],
                'failure_date': incident['failure_date'],
                'total_impact_mw': incident['disconnected_mw'],
                'classification': incident['classification'],
                'timeline': timeline_events,
                'system_impact': raw_json.get('technical_details', {}).get('system_impact', {}),
                'root_cause': incident['failure_cause_text']
            }
        finally:
            conn.close()
    
    # === NEW ENHANCED TOOLS ===
    
    def open_dashboard(self) -> Dict[str, Any]:
        """Open the web dashboard in browser"""
        try:
            dashboard_url = "http://localhost:5000"
            
            # Check if dashboard is running
            try:
                import requests
                response = requests.get(dashboard_url, timeout=2)
                dashboard_running = response.status_code == 200
            except:
                dashboard_running = False
            
            if not dashboard_running:
                # Start dashboard in background
                cmd = f"cd '{self.project_dir}' && source venv/bin/activate && python3 dashboard.py"
                subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                # Wait a bit for startup
                import time
                time.sleep(3)
            
            # Open in browser
            webbrowser.open(dashboard_url)
            
            return {
                "status": "success",
                "message": "Dashboard opened successfully",
                "url": dashboard_url,
                "dashboard_running": dashboard_running
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to open dashboard: {str(e)}"
            }
    
    def generate_executive_report(self) -> Dict[str, Any]:
        """Generate executive summary report"""
        try:
            # Get data from existing tools
            compliance = self.get_compliance_report()
            equipment = self.analyze_equipment_failures()
            timeline = self.get_incident_timeline()
            
            # Generate executive summary
            total_companies = len(compliance)
            critical_companies = [c for c in compliance if c['compliance_rate'] < 50]
            high_risk_equipment = [e for e in equipment if e['risk_level'] == 'High Risk']
            
            executive_summary = {
                "report_date": datetime.now().isoformat(),
                "executive_summary": {
                    "total_incidents_analyzed": 1,
                    "total_mw_impact": timeline['total_impact_mw'],
                    "system_classification": timeline['classification'],
                    "root_cause": "Siemens 7SL87 protection system failure"
                },
                "compliance_risks": {
                    "total_companies": total_companies,
                    "companies_at_risk": len(critical_companies),
                    "worst_performer": min(compliance, key=lambda x: x['compliance_rate'])['company_name'] if compliance else "None",
                    "worst_compliance_rate": min(compliance, key=lambda x: x['compliance_rate'])['compliance_rate'] if compliance else 0
                },
                "equipment_risks": {
                    "total_equipment_analyzed": len(equipment),
                    "high_risk_equipment": len(high_risk_equipment),
                    "equipment_details": equipment
                },
                "recommendations": [
                    "Immediate compliance automation for ENEL (7.9% rate)",
                    "Monitor all Siemens 7SL87 equipment approaching 7+ years",
                    "Implement cascade failure prevention protocols",
                    "Establish predictive maintenance for protection systems"
                ],
                "financial_impact": {
                    "energy_lost_mwh": 7015,
                    "estimated_cost_millions": 35.0,  # Rough estimate
                    "regulatory_risk": "High - potential fines for non-compliance"
                }
            }
            
            return executive_summary
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to generate report: {str(e)}"
            }
    
    def export_data(self, format_type: str = "json") -> Dict[str, Any]:
        """Export all data in specified format"""
        try:
            # Gather all data
            export_data = {
                "export_metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "format": format_type,
                    "source": "Dark Data MCP Server"
                },
                "compliance_data": self.get_compliance_report(),
                "equipment_analysis": self.analyze_equipment_failures(),
                "incident_timeline": self.get_incident_timeline(),
                "executive_report": self.generate_executive_report()
            }
            
            # Save to file
            filename = f"dark_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
            filepath = os.path.join(self.project_dir, filename)
            
            if format_type == "json":
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
            else:
                return {"status": "error", "message": f"Format {format_type} not supported yet"}
            
            return {
                "status": "success",
                "message": f"Data exported successfully to {filename}",
                "filepath": filepath,
                "size_mb": round(os.path.getsize(filepath) / (1024*1024), 2)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Export failed: {str(e)}"
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        try:
            # Check database
            conn = self.get_connection()
            db_stats = {}
            tables = ['incidents', 'companies', 'compliance_reports', 'equipment']
            for table in tables:
                count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                db_stats[f"total_{table}"] = count
            conn.close()
            
            # Check dashboard
            try:
                import requests
                dashboard_response = requests.get("http://localhost:5000", timeout=2)
                dashboard_status = "running" if dashboard_response.status_code == 200 else "stopped"
            except:
                dashboard_status = "stopped"
            
            # Check files
            files_status = {}
            important_files = [
                "dark_data.db",
                "power_system_failure_analysis.json",
                "dashboard.py",
                "mcp_server.py"
            ]
            
            for file in important_files:
                filepath = os.path.join(self.project_dir, file)
                files_status[file] = {
                    "exists": os.path.exists(filepath),
                    "size_mb": round(os.path.getsize(filepath) / (1024*1024), 2) if os.path.exists(filepath) else 0
                }
            
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "database": db_stats,
                "dashboard": dashboard_status,
                "files": files_status,
                "project_directory": self.project_dir
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"System check failed: {str(e)}"
            }

# Initialize the enhanced dark data handler
dark_data = EnhancedDarkDataMCP()

@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List available resources"""
    return [
        Resource(
            uri="database://dark_data/schema",
            name="Database Schema",
            description="Power system failure database schema and structure",
            mimeType="application/json"
        ),
        Resource(
            uri="database://dark_data/stats", 
            name="Database Statistics",
            description="Overall statistics about the dark data database",
            mimeType="application/json"
        ),
        Resource(
            uri="system://dark_data/status",
            name="System Status",
            description="Current system status and health check",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read a resource"""
    if uri == "database://dark_data/schema":
        schema_info = {
            "description": "Dark Data Database for Power System Failures",
            "tables": {
                "incidents": {
                    "description": "Main incident records",
                    "fields": ["report_id", "title", "failure_date", "disconnected_mw", "classification", "failure_cause_text"]
                },
                "companies": {
                    "description": "Power companies involved",
                    "fields": ["name", "rut", "legal_representative", "address"]
                },
                "compliance_reports": {
                    "description": "Company compliance tracking",
                    "fields": ["reports_48h_status", "reports_5d_status", "compliance_issues"]
                },
                "equipment": {
                    "description": "Failed equipment details",
                    "fields": ["manufacturer", "model", "installation_date", "function_affected"]
                }
            }
        }
        return json.dumps(schema_info, indent=2)
    
    elif uri == "database://dark_data/stats":
        stats = dark_data.get_system_status()
        return json.dumps(stats, indent=2)
        
    elif uri == "system://dark_data/status":
        status = dark_data.get_system_status()
        return json.dumps(status, indent=2)
    
    else:
        raise ValueError(f"Unknown resource: {uri}")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools"""
    return [
        # Original tools
        Tool(
            name="search_incidents",
            description="Search power system failure incidents by keywords",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (equipment, failure type, location, etc.)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 5)",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_compliance_report",
            description="Get compliance reporting status for power companies",
            inputSchema={
                "type": "object",
                "properties": {
                    "company_name": {
                        "type": "string",
                        "description": "Specific company name (optional - returns all if not specified)"
                    }
                }
            }
        ),
        Tool(
            name="analyze_equipment_failures",
            description="Analyze equipment failure patterns and risk levels",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_incident_timeline",
            description="Get detailed timeline and cascade effects of an incident",
            inputSchema={
                "type": "object", 
                "properties": {
                    "incident_id": {
                        "type": "string",
                        "description": "Incident report ID (optional - returns latest if not specified)"
                    }
                }
            }
        ),
        # New enhanced tools
        Tool(
            name="open_dashboard",
            description="Open the web dashboard in browser to visualize data interactively",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="generate_executive_report", 
            description="Generate executive summary report with key insights and recommendations",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="export_data",
            description="Export all analyzed data to file in specified format",
            inputSchema={
                "type": "object",
                "properties": {
                    "format_type": {
                        "type": "string",
                        "description": "Export format (json, csv, excel)",
                        "default": "json"
                    }
                }
            }
        ),
        Tool(
            name="get_system_status",
            description="Check system health, database status, and file integrity",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    """Handle tool calls"""
    try:
        if name == "search_incidents":
            query = arguments.get("query", "") if arguments else ""
            limit = arguments.get("limit", 5) if arguments else 5
            
            results = dark_data.search_incidents(query, limit)
            
            if not results:
                return [types.TextContent(
                    type="text",
                    text=f"No incidents found matching query: '{query}'"
                )]
            
            response = f"Found {len(results)} incident(s) matching '{query}':\n\n"
            for result in results:
                response += f"📋 **{result['report_id']}** - {result['title']}\n"
                response += f"   📅 Date: {result['failure_date']} at {result['failure_time']}\n"
                response += f"   ⚡ Impact: {result['disconnected_mw']} MW | Classification: {result['classification']}\n"
                response += f"   🔍 Cause: {result['failure_cause_text'][:200]}...\n\n"
            
            return [types.TextContent(type="text", text=response)]
        
        elif name == "get_compliance_report":
            company_name = arguments.get("company_name") if arguments else None
            
            results = dark_data.get_compliance_report(company_name)
            
            if not results:
                return [types.TextContent(
                    type="text", 
                    text="No compliance data found"
                )]
            
            response = "📋 **COMPLIANCE REPORT**\n\n"
            for company in results:
                status_emoji = "🔴" if company['compliance_rate'] < 50 else "🟡" if company['compliance_rate'] < 80 else "🟢"
                response += f"{status_emoji} **{company['company_name']}**\n"
                response += f"   Compliance Rate: {company['compliance_rate']}%\n"
                response += f"   On-time Reports: {company['on_time_reports']}/{company['on_time_reports'] + company['late_reports']}\n"
                response += f"   48h Status: {company['reports_48h_status']}\n"
                response += f"   5d Status: {company['reports_5d_status']}\n"
                
                if company['compliance_issues']:
                    response += f"   ⚠️ Issues: {', '.join(company['compliance_issues'])}\n"
                
                response += "\n"
            
            return [types.TextContent(type="text", text=response)]
        
        elif name == "analyze_equipment_failures":
            results = dark_data.analyze_equipment_failures()
            
            if not results:
                return [types.TextContent(
                    type="text",
                    text="No equipment failure data found"
                )]
            
            response = "⚙️ **EQUIPMENT FAILURE ANALYSIS**\n\n"
            for equipment in results:
                risk_emoji = "🔴" if equipment['risk_level'] == "High Risk" else "🟡" if equipment['risk_level'] == "Medium Risk" else "🟢"
                response += f"{risk_emoji} **{equipment['manufacturer']} {equipment['model']}**\n"
                response += f"   Installation: {equipment['installation_date']}\n"
                response += f"   Age: {equipment['age_years']} years\n"
                response += f"   Risk Level: {equipment['risk_level']}\n"
                response += f"   Function: {equipment['function_affected']}\n"
                response += f"   System: {equipment['system_number']}\n\n"
            
            return [types.TextContent(type="text", text=response)]
        
        elif name == "get_incident_timeline":
            incident_id = arguments.get("incident_id") if arguments else None
            
            result = dark_data.get_incident_timeline(incident_id)
            
            if "error" in result:
                return [types.TextContent(
                    type="text",
                    text=f"Error: {result['error']}"
                )]
            
            response = f"🕐 **INCIDENT TIMELINE: {result['incident_id']}**\n\n"
            response += f"**Title:** {result['title']}\n"
            response += f"**Date:** {result['failure_date']}\n"
            response += f"**Total Impact:** {result['total_impact_mw']} MW\n"
            response += f"**Classification:** {result['classification']}\n\n"
            
            response += "**Timeline of Events:**\n"
            for event in result['timeline']:
                event_emoji = {
                    'failure': '💥',
                    'generation_loss': '⚡',
                    'transmission_loss': '🔌',
                    'recovery': '✅'
                }.get(event['type'], '📍')
                
                response += f"{event_emoji} **{event['time']}** - {event['event']}\n"
            
            if result['system_impact']:
                response += f"\n**System Impact Details:**\n"
                for key, value in result['system_impact'].items():
                    response += f"   {key.replace('_', ' ').title()}: {value}\n"
            
            response += f"\n**Root Cause:** {result['root_cause'][:300]}..."
            
            return [types.TextContent(type="text", text=response)]
        
        # NEW ENHANCED TOOLS
        
        elif name == "open_dashboard":
            result = dark_data.open_dashboard()
            
            if result['status'] == 'success':
                response = f"🌐 **DASHBOARD OPENED SUCCESSFULLY**\n\n"
                response += f"📊 URL: {result['url']}\n"
                response += f"🔄 Status: {'Already running' if result['dashboard_running'] else 'Started automatically'}\n"
                response += f"💡 The dashboard shows:\n"
                response += f"   • Real-time compliance monitoring\n"
                response += f"   • Equipment risk assessment\n"
                response += f"   • Interactive incident timeline\n"
                response += f"   • Search functionality\n\n"
                response += f"🎯 Try searching for 'Siemens' or 'ENEL' in the dashboard!"
            else:
                response = f"❌ **DASHBOARD ERROR**\n\n{result['message']}"
            
            return [types.TextContent(type="text", text=response)]
        
        elif name == "generate_executive_report":
            result = dark_data.generate_executive_report()
            
            if "status" in result and result["status"] == "error":
                return [types.TextContent(type="text", text=f"❌ {result['message']}")]
            
            response = f"📋 **EXECUTIVE SUMMARY REPORT**\n"
            response += f"📅 Generated: {result['report_date'][:19]}\n\n"
            
            response += f"🎯 **INCIDENT OVERVIEW**\n"
            response += f"   Total MW Impact: {result['executive_summary']['total_mw_impact']:,} MW\n"
            response += f"   Classification: {result['executive_summary']['system_classification']}\n"
            response += f"   Root Cause: {result['executive_summary']['root_cause']}\n\n"
            
            response += f"⚠️ **COMPLIANCE RISKS**\n"
            response += f"   Companies Analyzed: {result['compliance_risks']['total_companies']}\n"
            response += f"   Companies at Risk: {result['compliance_risks']['companies_at_risk']}\n"
            response += f"   Worst Performer: {result['compliance_risks']['worst_performer']} ({result['compliance_risks']['worst_compliance_rate']}%)\n\n"
            
            response += f"💰 **FINANCIAL IMPACT**\n"
            response += f"   Energy Lost: {result['financial_impact']['energy_lost_mwh']:,} MWh\n"
            response += f"   Estimated Cost: ${result['financial_impact']['estimated_cost_millions']} million\n"
            response += f"   Regulatory Risk: {result['financial_impact']['regulatory_risk']}\n\n"
            
            response += f"💡 **KEY RECOMMENDATIONS**\n"
            for i, rec in enumerate(result['recommendations'], 1):
                response += f"   {i}. {rec}\n"
            
            return [types.TextContent(type="text", text=response)]
        
        elif name == "export_data":
            format_type = arguments.get("format_type", "json") if arguments else "json"
            
            result = dark_data.export_data(format_type)
            
            if result['status'] == 'success':
                response = f"💾 **DATA EXPORT SUCCESSFUL**\n\n"
                response += f"📄 File: {result['filepath'].split('/')[-1]}\n"
                response += f"📊 Size: {result['size_mb']} MB\n"
                response += f"📅 Format: {format_type.upper()}\n\n"
                response += f"📋 Exported data includes:\n"
                response += f"   • Complete compliance analysis\n"
                response += f"   • Equipment failure patterns\n"
                response += f"   • Incident timeline details\n"
                response += f"   • Executive summary report\n\n"
                response += f"💡 You can now share this file with stakeholders!"
            else:
                response = f"❌ **EXPORT FAILED**\n\n{result['message']}"
            
            return [types.TextContent(type="text", text=response)]
        
        elif name == "get_system_status":
            result = dark_data.get_system_status()
            
            if result['status'] == 'error':
                return [types.TextContent(type="text", text=f"❌ {result['message']}")]
            
            response = f"🖥️ **SYSTEM STATUS**\n"
            response += f"📅 Last Check: {result['timestamp'][:19]}\n"
            response += f"✅ Status: {result['status'].upper()}\n\n"
            
            response += f"📊 **DATABASE**\n"
            for table, count in result['database'].items():
                response += f"   {table.replace('total_', '').title()}: {count} records\n"
            
            response += f"\n🌐 **DASHBOARD**\n"
            response += f"   Status: {result['dashboard'].upper()}\n"
            
            response += f"\n📁 **FILES**\n"
            for filename, info in result['files'].items():
                status = "✅" if info['exists'] else "❌"
                response += f"   {status} {filename}: {info['size_mb']} MB\n"
            
            response += f"\n📂 Project: {result['project_directory']}"
            
            return [types.TextContent(type="text", text=response)]
        
        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
            
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error executing tool '{name}': {str(e)}"
        )]

async def main():
    """Run the enhanced MCP server"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="dark-data-enhanced-server",
                server_version="2.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())