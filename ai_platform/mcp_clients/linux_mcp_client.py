#!/usr/bin/env python3
"""
Linux MCP Client - Use your dark data with any LLM
Since Claude Desktop doesn't exist for Linux, this creates a simple interface
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class LinuxMCPClient:
    def __init__(self):
        self.server_params = StdioServerParameters(
            command="python3",
            args=["mcp_server.py"],
            cwd="/home/alonso/Documentos/Github/Proyecto Dark Data CEN"
        )

    async def ask_question(self, question: str):
        """Ask a question and get structured data to feed to any LLM"""
        print(f"🤖 Processing question: '{question}'")
        print("=" * 60)
        
        # Determine which tool to use based on question
        tool_mapping = {
            ("compliance", "cumplimiento", "reportes", "enel", "colbun"): "get_compliance_report",
            ("equipment", "equipo", "siemens", "edad", "riesgo"): "analyze_equipment_failures", 
            ("timeline", "cronologia", "cascada", "tiempo", "secuencia"): "get_incident_timeline",
            ("search", "buscar", "encontrar", "incident"): "search_incidents"
        }
        
        selected_tool = "search_incidents"  # default
        selected_args = {"query": question, "limit": 3}
        
        # Simple keyword matching
        question_lower = question.lower()
        for keywords, tool in tool_mapping.items():
            if any(keyword in question_lower for keyword in keywords):
                selected_tool = tool
                if tool == "search_incidents":
                    selected_args = {"query": question, "limit": 3}
                else:
                    selected_args = {}
                break
        
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                print(f"🔧 Using tool: {selected_tool}")
                print(f"📝 With arguments: {selected_args}")
                print("\n📊 RESULT:")
                print("-" * 40)
                
                try:
                    result = await session.call_tool(selected_tool, selected_args)
                    
                    response_text = ""
                    for content in result.content:
                        if hasattr(content, 'text'):
                            response_text += content.text
                    
                    print(response_text)
                    
                    # Return structured data for LLM integration
                    return {
                        "question": question,
                        "tool_used": selected_tool,
                        "arguments": selected_args,
                        "response": response_text,
                        "raw_result": result
                    }
                    
                except Exception as e:
                    error_msg = f"❌ Error: {e}"
                    print(error_msg)
                    return {
                        "question": question,
                        "error": str(e),
                        "tool_used": selected_tool,
                        "arguments": selected_args
                    }

    async def interactive_mode(self):
        """Interactive mode for asking questions"""
        print("🚀 LINUX MCP CLIENT - Dark Data Query Interface")
        print("=" * 60)
        print("💡 Ask questions about your power system data:")
        print("   • 'What companies have compliance issues?'")
        print("   • 'Show me equipment failures'")
        print("   • 'What caused the blackout?'")
        print("   • 'Show me the timeline'")
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
                
                await self.ask_question(question)
                print("\n" + "=" * 60)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

    async def generate_llm_context(self, question: str):
        """Generate context data to feed to external LLM (ChatGPT, etc.)"""
        result = await self.ask_question(question)
        
        context = f"""
DARK DATA CONTEXT FOR LLM:

User Question: {result['question']}
Tool Used: {result['tool_used']}
Arguments: {json.dumps(result['arguments'], indent=2)}

Data Retrieved:
{result.get('response', 'No data available')}

Instructions for LLM:
- Use this data to answer the user's question about power system failures
- Focus on compliance issues, equipment risks, and system impacts
- Provide actionable insights based on the data
- If asked about specific companies: ENEL has 7.9% compliance (critical), COLBÚN has 77.8%
- If asked about equipment: Siemens 7SL87 failed at 6.7 years old
- If asked about the blackout: 11,066 MW total impact, cascade failure in 5 seconds
"""
        
        print("\n📋 CONTEXT FOR EXTERNAL LLM:")
        print("=" * 50)
        print(context)
        print("=" * 50)
        print("💡 Copy this context and paste it to ChatGPT/Claude web with your question!")
        
        return context

async def main():
    client = LinuxMCPClient()
    
    print("🐧 LINUX MCP CLIENT")
    print("Since Claude Desktop isn't available for Linux, use this interface:")
    print("1. Interactive mode - Ask questions directly")
    print("2. Generate context - Get data to use with web LLMs")
    
    mode = input("\nChoose mode (1=interactive, 2=context, Enter=interactive): ").strip()
    
    if mode == "2":
        question = input("Enter your question: ").strip()
        if question:
            await client.generate_llm_context(question)
    else:
        await client.interactive_mode()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")