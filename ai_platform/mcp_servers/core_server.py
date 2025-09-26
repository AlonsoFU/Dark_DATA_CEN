#!/usr/bin/env python3
"""
MCP Server for Dark Data Database
Exposes power system failure data to AI models via Model Context Protocol
"""

import asyncio
import sqlite3
import json
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
server = Server("dark-data-server")

class DarkDataMCP:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to platform_data/database/dark_data.db relative to project root
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / "platform_data" / "database" / "dark_data.db"
        self.db_path = str(db_path)
        
    def get_connection(self):
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
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
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get overall database statistics"""
        conn = self.get_connection()
        try:
            stats = {}
            
            # Count records in each table
            tables = ['incidents', 'companies', 'compliance_reports', 'equipment']
            for table in tables:
                count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                stats[f"total_{table}"] = count
            
            # Get date range
            date_range = conn.execute("""
                SELECT MIN(failure_date) as earliest, MAX(failure_date) as latest
                FROM incidents
            """).fetchone()
            
            stats['date_range'] = {
                'earliest_incident': date_range['earliest'],
                'latest_incident': date_range['latest']
            }
            
            # Total MW affected
            total_mw = conn.execute("SELECT SUM(disconnected_mw) FROM incidents").fetchone()[0]
            stats['total_mw_affected'] = total_mw
            
            return stats
        finally:
            conn.close()

# Initialize the dark data handler
dark_data = DarkDataMCP()

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
        stats = dark_data.get_database_stats()
        return json.dumps(stats, indent=2)
    
    else:
        raise ValueError(f"Unknown resource: {uri}")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools"""
    return [
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
    """Run the MCP server"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="dark-data-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())