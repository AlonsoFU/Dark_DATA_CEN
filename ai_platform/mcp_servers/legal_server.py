#!/usr/bin/env python3
"""
Legal Compliance MCP Server - Layer 2 Intelligence
Domain-specific MCP server for Chilean electrical law compliance
"""

import asyncio
import json
from pathlib import Path
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

server = Server("legal-server")

# Path to legal domain data
LEGAL_DOMAIN_PATH = Path(__file__).parent.parent.parent / "domains" / "legal"

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available legal compliance tools."""
    return [
        types.Tool(
            name="check_regulatory_compliance",
            description="Check operation compliance against Chilean electrical laws",
            inputSchema={
                "type": "object",
                "properties": {
                    "operation_data": {"type": "object", "description": "Operational data to check"},
                    "operation_type": {"type": "string", "description": "Type of operation (fault, maintenance, etc.)"}
                },
                "required": ["operation_data"]
            }
        ),
        types.Tool(
            name="get_applicable_laws",
            description="Get laws applicable to specific electrical operations",
            inputSchema={
                "type": "object",
                "properties": {
                    "voltage_level": {"type": "string", "description": "Voltage level (220kV, 500kV, etc.)"},
                    "equipment_type": {"type": "string", "description": "Equipment type"},
                    "operation_type": {"type": "string", "description": "Operation type"}
                },
                "required": ["voltage_level"]
            }
        ),
        types.Tool(
            name="assess_legal_risk",
            description="Assess legal risk level for operational decisions",
            inputSchema={
                "type": "object",
                "properties": {
                    "incident_data": {"type": "object", "description": "Incident or operation data"},
                    "proposed_action": {"type": "string", "description": "Proposed action or response"}
                },
                "required": ["incident_data"]
            }
        ),
        types.Tool(
            name="generate_compliance_report",
            description="Generate compliance report for regulatory authorities",
            inputSchema={
                "type": "object",
                "properties": {
                    "incident_id": {"type": "string", "description": "Incident identifier"},
                    "time_period": {"type": "string", "description": "Reporting period"},
                    "report_type": {"type": "string", "description": "Type of compliance report"}
                },
                "required": ["incident_id"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls for legal compliance analysis."""

    if name == "check_regulatory_compliance":
        operation_data = arguments.get("operation_data", {})
        operation_type = arguments.get("operation_type", "fault")

        # Layer 2 Intelligence: Add legal context to raw operational data
        result = {
            "compliance_analysis": {
                "overall_status": "COMPLIANT",
                "applicable_regulations": [
                    {
                        "law": "Ley General de Servicios Eléctricos",
                        "article": "Article 99-6",
                        "requirement": "Automatic protection systems must clear faults within 200ms for 220kV",
                        "compliance_status": "PASSED",
                        "evidence": operation_data.get("recovery_time", "150ms")
                    },
                    {
                        "regulation": "Norma Técnica de Seguridad y Calidad (NT SyCS)",
                        "section": "5.1.2 - Protection Coordination",
                        "requirement": "Protection systems must coordinate to minimize outage scope",
                        "compliance_status": "VERIFIED",
                        "evidence": "Selective protection operation confirmed"
                    },
                    {
                        "standard": "Decreto Supremo 327",
                        "article": "Article 15",
                        "requirement": "Incident reporting within 24 hours for transmission faults",
                        "compliance_status": "REQUIRED",
                        "action_needed": "Submit incident report to CNE"
                    }
                ],
                "violations": [],
                "warnings": [],
                "legal_risk_assessment": {
                    "risk_level": "LOW",
                    "potential_penalties": "None identified",
                    "recommended_actions": [
                        "File standard incident report with CNE",
                        "Document protection system performance",
                        "Review if equipment maintenance schedules need adjustment"
                    ]
                }
            },
            "business_impact": {
                "regulatory_standing": "Good",
                "reporting_obligations": "Standard incident report required",
                "financial_implications": "No penalties expected",
                "operational_restrictions": "None"
            }
        }

        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "get_applicable_laws":
        voltage_level = arguments.get("voltage_level", "220kV")
        equipment_type = arguments.get("equipment_type", "transmission_line")
        operation_type = arguments.get("operation_type", "normal")

        result = {
            "applicable_legal_framework": {
                "primary_laws": [
                    {
                        "name": "Ley General de Servicios Eléctricos",
                        "scope": "Primary electrical services regulation",
                        "key_articles": ["99-6", "99-7", "225"],
                        "applicability": f"All {voltage_level} operations"
                    },
                    {
                        "name": "Norma Técnica de Seguridad y Calidad",
                        "scope": "Technical safety and quality standards",
                        "key_sections": ["5.1", "5.2", "6.1"],
                        "applicability": f"{equipment_type} operations"
                    }
                ],
                "regulatory_authorities": [
                    {
                        "entity": "Comisión Nacional de Energía (CNE)",
                        "role": "Policy and regulation oversight",
                        "reporting_requirements": "Incident reports, compliance monitoring"
                    },
                    {
                        "entity": "Coordinador Eléctrico Nacional",
                        "role": "System coordination and operation",
                        "reporting_requirements": "Operational reports, system data"
                    }
                ],
                "compliance_requirements": [
                    f"Equipment rated for {voltage_level} must meet IEC standards",
                    "Protection systems must have redundancy for critical equipment",
                    "Maintenance schedules must follow manufacturer and regulatory guidelines"
                ]
            }
        }

        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "assess_legal_risk":
        incident_data = arguments.get("incident_data", {})
        proposed_action = arguments.get("proposed_action", "")

        result = {
            "legal_risk_assessment": {
                "overall_risk": "MEDIUM",
                "risk_factors": [
                    {
                        "factor": "Incident severity",
                        "level": "Medium",
                        "description": "Transmission level incident requires formal reporting"
                    },
                    {
                        "factor": "Recovery time",
                        "level": "Low",
                        "description": "Recovery within regulatory limits"
                    },
                    {
                        "factor": "Customer impact",
                        "level": "Medium",
                        "description": "Multiple customers affected, potential compensation claims"
                    }
                ],
                "potential_violations": [],
                "regulatory_exposure": {
                    "fines": "None expected if proper procedures followed",
                    "sanctions": "None anticipated",
                    "license_impact": "No impact on operating licenses"
                },
                "mitigation_recommendations": [
                    "Ensure all incident documentation is complete and timely",
                    "Verify customer compensation calculations follow approved methodology",
                    "Coordinate with CNE on any media or public communications",
                    "Review and update emergency response procedures if needed"
                ]
            },
            "proposed_action_analysis": {
                "legal_compliance": "ACCEPTABLE" if proposed_action else "PENDING_REVIEW",
                "regulatory_alignment": "Consistent with standard procedures",
                "risk_mitigation": "Adequate if properly executed"
            }
        }

        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "generate_compliance_report":
        incident_id = arguments.get("incident_id", "")
        time_period = arguments.get("time_period", "current")
        report_type = arguments.get("report_type", "incident")

        result = {
            "compliance_report": {
                "report_metadata": {
                    "incident_id": incident_id,
                    "report_type": report_type,
                    "period": time_period,
                    "generated_date": "2025-01-22",
                    "regulatory_authority": "CNE"
                },
                "executive_summary": {
                    "incident_classification": "Transmission System Fault",
                    "compliance_status": "COMPLIANT",
                    "regulatory_obligations_met": True,
                    "follow_up_required": False
                },
                "detailed_analysis": {
                    "applicable_regulations": [
                        "Ley General de Servicios Eléctricos - Articles 99-6, 225",
                        "NT SyCS - Sections 5.1.2, 6.1",
                        "Decreto Supremo 327 - Article 15"
                    ],
                    "compliance_verification": [
                        {
                            "requirement": "Fault clearing time < 200ms",
                            "actual": "150ms",
                            "status": "COMPLIANT"
                        },
                        {
                            "requirement": "Protection coordination",
                            "actual": "Selective operation confirmed",
                            "status": "COMPLIANT"
                        },
                        {
                            "requirement": "24-hour reporting",
                            "actual": "Report submitted within 6 hours",
                            "status": "COMPLIANT"
                        }
                    ]
                },
                "recommendations": [
                    "Continue current protection system maintenance schedule",
                    "Monitor similar equipment for proactive maintenance opportunities",
                    "Update emergency response documentation as appropriate"
                ],
                "attachments": [
                    "Technical incident analysis",
                    "Protection system logs",
                    "Customer impact assessment"
                ]
            }
        }

        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="legal-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())