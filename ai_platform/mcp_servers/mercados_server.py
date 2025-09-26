#!/usr/bin/env python3
"""
Mercados MCP Server - Market Intelligence
Domain-specific MCP server for electricity market operations
"""

import asyncio
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

server = Server("mercados-server")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available mercados tools."""
    return [
        types.Tool(
            name="analyze_market_prices",
            description="Analyze electricity market prices and trends",
            inputSchema={
                "type": "object",
                "properties": {
                    "time_period": {"type": "string", "description": "Time period for analysis"},
                    "market_type": {"type": "string", "description": "Spot, futures, or ancillary services"}
                },
                "required": ["time_period"]
            }
        ),
        types.Tool(
            name="forecast_demand",
            description="Forecast electricity demand",
            inputSchema={
                "type": "object",
                "properties": {
                    "forecast_horizon": {"type": "string", "description": "Forecast period"},
                    "region": {"type": "string", "description": "Geographic region"}
                },
                "required": ["forecast_horizon"]
            }
        ),
        types.Tool(
            name="generation_dispatch_analysis",
            description="Analyze optimal generation dispatch",
            inputSchema={
                "type": "object",
                "properties": {
                    "demand_mw": {"type": "number", "description": "Demand in MW"},
                    "renewable_available": {"type": "number", "description": "Available renewable capacity"}
                },
                "required": ["demand_mw"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls for mercados domain."""

    if name == "analyze_market_prices":
        time_period = arguments.get("time_period", "today")
        market_type = arguments.get("market_type", "spot")

        result = f"Market Price Analysis ({market_type} - {time_period}):\n"
        result += "- Average price: $89.50/MWh\n"
        result += "- Peak price: $145.20/MWh (19:30)\n"
        result += "- Off-peak price: $65.80/MWh (03:00)\n"
        result += "- Price volatility: Medium (±18%)\n"
        result += "- Renewable contribution: 42%"

        return [types.TextContent(type="text", text=result)]

    elif name == "forecast_demand":
        forecast_horizon = arguments.get("forecast_horizon", "24h")
        region = arguments.get("region", "SIC")

        result = f"Demand Forecast - {region} ({forecast_horizon}):\n"
        result += "- Peak demand: 8,750 MW (20:00)\n"
        result += "- Minimum demand: 5,450 MW (04:30)\n"
        result += "- Average demand: 7,100 MW\n"
        result += "- Forecast accuracy: 97.2%\n"
        result += "- Weather factor: High temperature impact"

        return [types.TextContent(type="text", text=result)]

    elif name == "generation_dispatch_analysis":
        demand_mw = arguments.get("demand_mw", 7000)
        renewable_available = arguments.get("renewable_available", 2800)

        thermal_needed = max(0, demand_mw - renewable_available - 1200)  # Assuming 1200 MW hydro

        result = f"Optimal Dispatch for {demand_mw} MW:\n"
        result += f"- Renewable: {min(renewable_available, demand_mw)} MW ({min(renewable_available/demand_mw*100, 100):.1f}%)\n"
        result += f"- Hydro: {min(1200, demand_mw - renewable_available)} MW\n"
        result += f"- Thermal: {thermal_needed} MW\n"
        result += f"- Total cost: ${demand_mw * 75:.0f}/hour\n"
        result += f"- CO2 emissions: {thermal_needed * 0.8:.0f} tons/hour"

        return [types.TextContent(type="text", text=result)]

    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mercados-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())