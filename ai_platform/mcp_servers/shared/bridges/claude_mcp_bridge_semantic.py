#!/usr/bin/env python3
"""
Advanced Claude API + MCP Bridge with Semantic Tool Selection
Uses embeddings and semantic similarity for intelligent tool selection
"""

import asyncio
import os
import numpy as np
from typing import Optional, List, Dict, Tuple
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Required packages
try:
    import anthropic
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError as e:
    missing_packages = []
    if 'anthropic' in str(e):
        missing_packages.append('anthropic')
    if 'sentence_transformers' in str(e):
        missing_packages.append('sentence-transformers')
    if 'sklearn' in str(e):
        missing_packages.append('scikit-learn')
    
    print(f"❌ Missing packages: {', '.join(missing_packages)}")
    print("💡 Install with: pip install anthropic sentence-transformers scikit-learn")
    exit(1)

class SemanticToolSelector:
    """Semantic tool selection using sentence embeddings"""
    
    def __init__(self):
        print("🧠 Loading semantic model...")
        # Use a lightweight multilingual model for Spanish/English
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        # Tool descriptions with semantic context
        self.tool_descriptions = {
            "get_compliance_report": [
                "compliance analysis regulatory requirements violations companies ENEL COLBÚN",
                "cumplimiento normativo empresas regulación reportes incumplimiento",
                "show company compliance status regulatory violations penalties"
            ],
            "analyze_equipment_failures": [
                "equipment failures analysis maintenance age Siemens protection systems",
                "análisis equipos fallas mantenimiento edad protección sistemas",
                "analyze equipment condition maintenance needs failure patterns"
            ],
            "get_incident_timeline": [
                "incident timeline chronology blackout cascade failure sequence events",
                "cronología incidente apagón cascada secuencia eventos tiempo",
                "show timeline of events incident chronology sequence"
            ],
            "search_incidents": [
                "search find incidents specific terms companies equipment types",
                "buscar incidentes términos específicos empresas equipos",
                "find search locate specific incident data information"
            ],
            "open_dashboard": [
                "open dashboard web visualize show display interface browser",
                "abrir dashboard mostrar visualizar interfaz navegador web",
                "launch open show web interface visualization dashboard"
            ],
            "get_system_status": [
                "system health status check database files integrity",
                "estado sistema salud verificar base datos archivos",
                "check system health status database integrity"
            ],
            "generate_executive_report": [
                "executive report summary business insights recommendations management",
                "reporte ejecutivo resumen negocio recomendaciones gerencia",
                "create generate executive summary business report insights"
            ],
            "export_data": [
                "export data file format JSON CSV Excel download save",
                "exportar datos archivo formato JSON CSV Excel descargar",
                "export save data to file format JSON CSV Excel"
            ]
        }
        
        # Pre-compute embeddings for all tool descriptions
        print("🔄 Computing tool embeddings...")
        self.tool_embeddings = {}
        for tool_name, descriptions in self.tool_descriptions.items():
            # Combine all descriptions for each tool
            combined_desc = " ".join(descriptions)
            embedding = self.model.encode([combined_desc])
            self.tool_embeddings[tool_name] = embedding[0]
        
        print("✅ Semantic tool selector ready")
    
    def select_tools(self, user_query: str, threshold: float = 0.3) -> List[Tuple[str, float]]:
        """
        Select most relevant tools based on semantic similarity
        Returns list of (tool_name, similarity_score) tuples
        """
        # Encode user query
        query_embedding = self.model.encode([user_query])[0]
        
        # Calculate similarities
        similarities = []
        for tool_name, tool_embedding in self.tool_embeddings.items():
            similarity = cosine_similarity(
                query_embedding.reshape(1, -1),
                tool_embedding.reshape(1, -1)
            )[0][0]
            
            if similarity >= threshold:
                similarities.append((tool_name, similarity))
        
        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities
    
    def explain_selection(self, user_query: str, selected_tools: List[Tuple[str, float]]) -> str:
        """Explain why tools were selected"""
        if not selected_tools:
            return "No tools matched with sufficient confidence"
        
        explanation = f"🧠 Semantic Analysis for: '{user_query}'\n"
        explanation += "Selected tools based on semantic similarity:\n"
        
        for tool_name, score in selected_tools:
            confidence = "HIGH" if score > 0.7 else "MEDIUM" if score > 0.5 else "LOW"
            explanation += f"  • {tool_name}: {score:.3f} ({confidence})\n"
        
        return explanation

class ClaudeMCPBridgeSemantic:
    def __init__(self, api_key: Optional[str] = None):
        # API Key setup
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
        
        # Initialize semantic tool selector
        self.tool_selector = SemanticToolSelector()
        print("✅ Claude MCP Bridge with Semantic Selection initialized")

    async def get_mcp_data_semantic(self, question: str) -> str:
        """Get relevant data from MCP server using semantic tool selection"""
        print(f"🔍 Analyzing question: '{question}'")
        
        # Use semantic selection to choose tools
        selected_tools = self.tool_selector.select_tools(question, threshold=0.3)
        
        # Show selection reasoning
        selection_info = self.tool_selector.explain_selection(question, selected_tools)
        print(selection_info)
        
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                context = "POWER SYSTEM DATA CONTEXT:\n\n"
                
                try:
                    # Call tools based on semantic similarity
                    for tool_name, similarity_score in selected_tools[:3]:  # Top 3 tools max
                        print(f"🔧 Calling {tool_name} (similarity: {similarity_score:.3f})")
                        
                        if tool_name == "search_incidents":
                            # For search, extract key terms from question
                            search_terms = self._extract_search_terms(question)
                            for term in search_terms[:2]:  # Max 2 searches
                                print(f"  🔍 Searching for: {term}")
                                result = await session.call_tool("search_incidents", {"query": term, "limit": 3})
                                if result.content:
                                    context += f"SEARCH RESULTS FOR '{term}':\n" + result.content[0].text + "\n\n"
                        else:
                            # Call tool with empty parameters for most tools
                            tool_params = {}
                            if tool_name == "export_data":
                                tool_params = {"format_type": "json"}
                            
                            result = await session.call_tool(tool_name, tool_params)
                            if result.content:
                                tool_title = tool_name.replace("_", " ").title()
                                context += f"{tool_title.upper()}:\n" + result.content[0].text + "\n\n"
                    
                    # If no tools selected or low confidence, get general overview
                    if not selected_tools or selected_tools[0][1] < 0.4:
                        print("📋 Low confidence - getting general overview...")
                        compliance = await session.call_tool("get_compliance_report", {})
                        equipment = await session.call_tool("analyze_equipment_failures", {})
                        if compliance.content:
                            context += "GENERAL COMPLIANCE OVERVIEW:\n" + compliance.content[0].text + "\n\n"
                        if equipment.content:
                            context += "GENERAL EQUIPMENT OVERVIEW:\n" + equipment.content[0].text + "\n\n"
                
                except Exception as e:
                    print(f"⚠️ MCP Error: {e}")
                    context += f"Error getting some data: {e}\n"
                
                return context
    
    def _extract_search_terms(self, question: str) -> List[str]:
        """Extract key search terms from question"""
        # Simple keyword extraction - could be enhanced with NLP
        important_terms = []
        question_lower = question.lower()
        
        # Look for company names
        if "enel" in question_lower:
            important_terms.append("enel")
        if "colbún" in question_lower or "colbun" in question_lower:
            important_terms.append("colbún")
        
        # Look for equipment terms
        if "siemens" in question_lower:
            important_terms.append("siemens")
        if "protection" in question_lower or "protección" in question_lower:
            important_terms.append("protection")
        
        # Default search terms if none found
        if not important_terms:
            important_terms = ["siemens", "protection"]
        
        return important_terms

    async def ask_claude(self, question: str) -> str:
        """Ask Claude a question using semantic MCP data selection"""
        print(f"🤖 Asking Claude: '{question}'")
        
        # Get relevant data using semantic selection
        mcp_context = await self.get_mcp_data_semantic(question)
        
        # Enhanced prompt with semantic context
        full_prompt = f"""You are analyzing power system failure data from a 399-page regulatory report (EAF-089/2025) that caused a total blackout in Chile.

CONTEXT FROM SEMANTIC DATABASE SELECTION:
{mcp_context}

KEY FACTS TO REMEMBER:
- Total blackout: 11,066 MW (100% of system demand)
- Root cause: Siemens 7SL87 protection system failure (6.7 years old)
- ENEL compliance: 7.9% (critical regulatory risk)
- COLBÚN compliance: 77.8% (moderate risk)
- Cascade failure: 5-second southern grid collapse
- 8 power plants affected across multiple technologies

USER QUESTION: {question}

Please analyze the semantically selected data and provide actionable insights. Focus on:
- Business impact and regulatory compliance risks
- Equipment failure patterns and maintenance recommendations  
- System vulnerabilities and prevention measures
- Specific actions needed based on the data retrieved

Answer in Spanish if the question was in Spanish, English if in English."""

        try:
            print("🔄 Calling Claude API with semantic context...")
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
        """Interactive chat with semantic tool selection"""
        print("🚀 CLAUDE + MCP BRIDGE - Semantic Mode")
        print("=" * 60)
        print("🧠 Advanced AI that understands your intent:")
        print("   • Uses embeddings for intelligent tool selection")
        print("   • Explains why tools are chosen")
        print("   • Works in Spanish and English")
        print("   • Type 'explain' to see tool selection reasoning")
        print("   • Type 'exit' to quit")
        print("=" * 60)
        
        while True:
            try:
                question = input("\n🤖 Your question: ").strip()
                
                if question.lower() in ['exit', 'quit', 'salir']:
                    print("\n👋 Goodbye!")
                    break
                
                if question.lower() == 'explain':
                    print("\n🧠 SEMANTIC TOOL SELECTION:")
                    print("Uses sentence-transformers to understand meaning")
                    print("Compares your question to tool descriptions")
                    print("Selects most relevant tools automatically")
                    continue
                
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
    """Main function with semantic tool selection"""
    # Use environment variable for API key
    bridge = ClaudeMCPBridgeSemantic()
    
    print("🎯 Choose mode:")
    print("1. Interactive chat (semantic)")
    print("2. Single question (semantic)")
    print("3. Test semantic selection")
    
    mode = input("Enter choice (1, 2, or 3, default=1): ").strip()
    
    if mode == "2":
        question = input("Enter your question: ").strip()
        if question:
            answer = await bridge.ask_claude(question)
            print("\n📝 ANSWER:")
            print("=" * 40)
            print(answer)
    elif mode == "3":
        # Test semantic selection
        test_queries = [
            "puedes abrir el dashboard web del reporte de fallas?",
            "What companies have compliance problems?",
            "¿Qué equipos de Siemens están fallando?",
            "Generate a report for executives",
            "Export all data to Excel",
            "Check if the system is working"
        ]
        
        print("\n🧪 TESTING SEMANTIC SELECTION:")
        print("=" * 50)
        
        for query in test_queries:
            print(f"\n❓ Query: '{query}'")
            selected_tools = bridge.tool_selector.select_tools(query)
            explanation = bridge.tool_selector.explain_selection(query, selected_tools)
            print(explanation)
    else:
        await bridge.interactive_mode()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")