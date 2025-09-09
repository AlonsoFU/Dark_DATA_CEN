#!/usr/bin/env python3
"""
MCP Demo Script - Shows how to interact with your dark data
Run this to see exactly what tools and data are available to AI
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPDemo:
    def __init__(self):
        self.server_params = StdioServerParameters(
            command="python3",
            args=["mcp_server.py"],
            cwd="/home/alonso/Documentos/Github/Proyecto Dark Data CEN"
        )

    async def discover_capabilities(self):
        """Show what tools and resources are available to AI"""
        print("🔍 DISCOVERING MCP CAPABILITIES...")
        print("=" * 60)
        
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # List tools
                print("\n🔧 AVAILABLE TOOLS (What AI can do):")
                print("-" * 40)
                tools = await session.list_tools()
                for i, tool in enumerate(tools.tools, 1):
                    print(f"{i}. {tool.name}")
                    print(f"   📄 {tool.description}")
                    print(f"   📝 Input: {list(tool.inputSchema.get('properties', {}).keys())}")
                    print()
                
                # List resources  
                print("\n📚 AVAILABLE RESOURCES (What AI can read):")
                print("-" * 40)
                resources = await session.list_resources()
                for i, resource in enumerate(resources.resources, 1):
                    print(f"{i}. {resource.name}")
                    print(f"   📄 {resource.description}")
                    print(f"   🔗 URI: {resource.uri}")
                    print()

    async def demo_questions(self):
        """Demonstrate typical AI questions and responses"""
        print("\n🤖 DEMO: AI QUESTIONS & RESPONSES")
        print("=" * 60)
        
        questions = [
            {
                "question": "What equipment failed?",
                "tool": "analyze_equipment_failures",
                "args": {}
            },
            {
                "question": "Which companies have compliance issues?", 
                "tool": "get_compliance_report",
                "args": {}
            },
            {
                "question": "Find incidents with protection systems",
                "tool": "search_incidents", 
                "args": {"query": "protection system", "limit": 2}
            },
            {
                "question": "Show me the blackout timeline",
                "tool": "get_incident_timeline",
                "args": {}
            }
        ]
        
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                for demo in questions:
                    print(f"\n❓ USER QUESTION: '{demo['question']}'")
                    print(f"🔧 AI CALLS TOOL: {demo['tool']}")
                    print(f"📝 WITH ARGS: {demo['args']}")
                    print("\n🤖 AI RESPONSE:")
                    print("-" * 30)
                    
                    try:
                        result = await session.call_tool(demo['tool'], demo['args'])
                        for content in result.content:
                            if hasattr(content, 'text'):
                                # Truncate long responses for demo
                                text = content.text
                                if len(text) > 300:
                                    text = text[:300] + "...\n[Response truncated for demo]"
                                print(text)
                    except Exception as e:
                        print(f"❌ Error: {e}")
                    
                    print("\n" + "="*60)

    async def show_database_info(self):
        """Show what data is actually in the database"""
        print("\n📊 DATABASE CONTENTS (What AI can access):")
        print("=" * 60)
        
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Read database schema
                print("\n📋 DATABASE SCHEMA:")
                print("-" * 30)
                try:
                    schema = await session.read_resource("database://dark_data/schema")
                    schema_data = json.loads(schema)
                    
                    print(f"📝 Description: {schema_data['description']}")
                    print("\n📊 Tables:")
                    for table_name, table_info in schema_data['tables'].items():
                        print(f"   • {table_name}: {table_info['description']}")
                        print(f"     Fields: {', '.join(table_info['fields'])}")
                        
                except Exception as e:
                    print(f"❌ Could not read schema: {e}")
                
                # Read database stats
                print("\n📈 DATABASE STATISTICS:")
                print("-" * 30)
                try:
                    stats = await session.read_resource("database://dark_data/stats")
                    stats_data = json.loads(stats)
                    
                    for key, value in stats_data.items():
                        if isinstance(value, dict):
                            print(f"📅 {key.replace('_', ' ').title()}:")
                            for k, v in value.items():
                                print(f"   • {k.replace('_', ' ').title()}: {v}")
                        else:
                            print(f"📊 {key.replace('_', ' ').title()}: {value}")
                            
                except Exception as e:
                    print(f"❌ Could not read stats: {e}")

    async def run_full_demo(self):
        """Run complete demo showing MCP capabilities"""
        print("🚀 MCP DARK DATA DEMO")
        print("🔗 Showing what AI can access in your database")
        print("="*80)
        
        try:
            await self.discover_capabilities()
            await self.show_database_info()
            await self.demo_questions()
            
            print("\n🎉 DEMO COMPLETE!")
            print("=" * 80)
            print("💡 WHAT THIS MEANS:")
            print("• Any AI tool (Claude, GPT, etc.) can use these 4 tools")
            print("• AI can search your power system failures")  
            print("• AI can analyze compliance issues")
            print("• AI can assess equipment risks")
            print("• AI can reconstruct incident timelines")
            print("• AI gets real-time data, not static responses")
            print("\n🔗 NEXT STEPS:")
            print("1. Configure Claude Desktop with your MCP server")
            print("2. Ask Claude: 'What caused the February 2025 blackout?'")
            print("3. Ask Claude: 'Which companies have compliance problems?'")
            print("4. Watch Claude use your tools to answer from live data!")
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            print("\n🛠️ TROUBLESHOOTING:")
            print("1. Make sure your MCP server is working: python test_mcp.py")
            print("2. Check database exists: ls -la dark_data.db") 
            print("3. Verify data loaded: python analysis_queries.py")

async def main():
    """Run the MCP demo"""
    demo = MCPDemo()
    await demo.run_full_demo()

if __name__ == "__main__":
    print("🎯 This script shows exactly what AI can access in your dark data database")
    print("⏱️  Takes ~30 seconds to run complete demo\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("\nℹ️  Make sure you're in the project directory and database is created")