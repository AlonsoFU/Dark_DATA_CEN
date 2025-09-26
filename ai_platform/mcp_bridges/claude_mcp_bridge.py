#!/usr/bin/env python3
"""
Claude API + MCP Bridge for Linux
Direct integration between your dark data and Claude API
"""

import asyncio
import os
from typing import Optional
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# You'll need to install anthropic: pip install anthropic
try:
    import anthropic
except ImportError:
    print("❌ Please install: pip install anthropic")
    exit(1)

class ClaudeMCPBridge:
    def __init__(self, api_key: Optional[str] = None):
        # API Key from environment or parameter
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            print("❌ No API key found. Set ANTHROPIC_API_KEY environment variable or pass api_key parameter")
            print("💡 Get your API key from: https://console.anthropic.com/")
            exit(1)
        
        self.claude = anthropic.Anthropic(api_key=self.api_key)
        self.server_params = StdioServerParameters(
            command="python3",
            args=["mcp_server_enhanced.py"],
            cwd="/home/alonso/Documentos/Github/Proyecto Dark Data CEN"
        )
        print("✅ Claude MCP Bridge initialized")

    async def get_mcp_data(self, question: str) -> str:
        """Get relevant data from MCP server based on question"""
        print(f"🔍 Analyzing question: '{question}'")
        
        # Determine which MCP tools to call based on question keywords
        question_lower = question.lower()
        
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                context = "POWER SYSTEM DATA CONTEXT:\n\n"
                
                # Always get basic overview
                try:
                    if any(word in question_lower for word in ["compliance", "cumplimiento", "reportes", "enel", "colbún", "empresas"]):
                        print("📊 Getting compliance data...")
                        compliance = await session.call_tool("get_compliance_report", {})
                        if compliance.content:
                            context += "COMPLIANCE ANALYSIS:\n" + compliance.content[0].text + "\n\n"
                    
                    if any(word in question_lower for word in ["equipo", "equipment", "siemens", "edad", "riesgo", "falla"]):
                        print("⚙️ Getting equipment data...")
                        equipment = await session.call_tool("analyze_equipment_failures", {})
                        if equipment.content:
                            context += "EQUIPMENT ANALYSIS:\n" + equipment.content[0].text + "\n\n"
                    
                    if any(word in question_lower for word in ["timeline", "cronologia", "tiempo", "cascada", "apagón", "blackout"]):
                        print("🕐 Getting incident timeline...")
                        timeline = await session.call_tool("get_incident_timeline", {})
                        if timeline.content:
                            context += "INCIDENT TIMELINE:\n" + timeline.content[0].text + "\n\n"
                    
                    # Search for specific terms
                    search_terms = []
                    if "siemens" in question_lower:
                        search_terms.append("siemens")
                    if "protection" in question_lower or "protección" in question_lower:
                        search_terms.append("protection")
                    if "enel" in question_lower:
                        search_terms.append("enel")
                    
                    for term in search_terms:
                        print(f"🔍 Searching for: {term}")
                        search = await session.call_tool("search_incidents", {"query": term, "limit": 3})
                        if search.content:
                            context += f"SEARCH RESULTS FOR '{term}':\n" + search.content[0].text + "\n\n"
                    
                    # Check for dashboard opening request
                    if any(word in question_lower for word in ["dashboard", "abrir", "open", "abre", "muestra", "show", "launch"]):
                        print("🌐 Opening dashboard...")
                        dashboard = await session.call_tool("open_dashboard", {})
                        if dashboard.content:
                            context += "DASHBOARD STATUS:\n" + dashboard.content[0].text + "\n\n"
                    
                    # If no specific match, get general overview
                    if len(context.split("\n")) < 5:
                        print("📋 Getting general overview...")
                        compliance = await session.call_tool("get_compliance_report", {})
                        equipment = await session.call_tool("analyze_equipment_failures", {})
                        if compliance.content:
                            context += "COMPLIANCE OVERVIEW:\n" + compliance.content[0].text + "\n\n"
                        if equipment.content:
                            context += "EQUIPMENT OVERVIEW:\n" + equipment.content[0].text + "\n\n"
                
                except Exception as e:
                    print(f"⚠️ MCP Error: {e}")
                    context += f"Error getting some data: {e}\n"
                
                return context

    async def ask_claude(self, question: str) -> str:
        """Ask Claude a question using MCP data as context"""
        print(f"🤖 Asking Claude: '{question}'")
        
        # Get relevant data from MCP
        mcp_context = await self.get_mcp_data(question)
        
        # Create the prompt for Claude
        full_prompt = f"""You are analyzing power system failure data from a 399-page regulatory report (EAF-089/2025) that caused a total blackout in Chile.

CONTEXT FROM DATABASE:
{mcp_context}

KEY FACTS TO REMEMBER:
- This was a total blackout affecting 11,066 MW (100% of system demand)
- Caused by Siemens 7SL87 protection system failure (6.7 years old)
- ENEL has 7.9% compliance rate (major regulatory risk)
- COLBÚN has 77.8% compliance rate (moderate)
- Cascade failure: 5-second southern grid collapse
- 8 power plants affected across multiple technologies

USER QUESTION: {question}

Please analyze the data and provide actionable insights. Focus on:
- Business impact and regulatory risks
- Equipment failure patterns and maintenance recommendations  
- Compliance issues and corrective actions needed
- System vulnerabilities and prevention measures

Answer in Spanish if the question was in Spanish, English if in English."""

        try:
            # Call Claude API
            print("🔄 Calling Claude API...")
            response = self.claude.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": full_prompt
                }]
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"❌ Error calling Claude API: {e}\nCheck your API key and internet connection."

    async def interactive_mode(self):
        """Interactive chat with Claude using your MCP data"""
        print("🚀 CLAUDE + MCP BRIDGE - Interactive Mode")
        print("=" * 60)
        print("💡 Ask questions about your power system data:")
        print("   • '¿Qué empresas tienen problemas de cumplimiento?'")
        print("   • 'What equipment should I monitor for failures?'")
        print("   • '¿Cuál fue el costo del apagón de febrero 2025?'")
        print("   • 'How can I prevent cascade failures?'")
        print("   • Type 'exit' to quit")
        print("=" * 60)
        
        while True:
            try:
                question = input("\n🤖 Your question: ").strip()
                
                if question.lower() in ['exit', 'quit', 'salir']:
                    print("\n👋 Goodbye!")
                    break
                
                if not question:
                    continue
                
                print("\n" + "="*60)
                answer = await self.ask_claude(question)
                print("\n📝 CLAUDE'S RESPONSE:")
                print("-" * 40)
                print(answer)
                print("="*60)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

async def main():
    """Main function - you can modify this for your needs"""
    
    # Use environment variable (recommended for security)
    # Set your API key: export ANTHROPIC_API_KEY=your_key_here
    bridge = ClaudeMCPBridge()
    
    # Alternative: Pass API key as parameter (not recommended for production)
    # bridge = ClaudeMCPBridge(api_key="your_key_here")
    # export ANTHROPIC_API_KEY=sk-ant-your-key-here
    #bridge = ClaudeMCPBridge()
    
    print("🎯 Choose mode:")
    print("1. Interactive chat")
    print("2. Single question")
    
    mode = input("Enter choice (1 or 2, default=1): ").strip()
    
    if mode == "2":
        question = input("Enter your question: ").strip()
        if question:
            answer = await bridge.ask_claude(question)
            print("\n📝 ANSWER:")
            print("=" * 40)
            print(answer)
    else:
        await bridge.interactive_mode()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")