#!/usr/bin/env python3
"""
Interactive test of Claude + MCP with new tools
"""

import asyncio
from pathlib import Path
from claude_mcp_bridge import ClaudeMCPBridge

async def interactive_test():
    """Test Claude with your API key interactively"""
    print("🤖 CLAUDE + MCP INTERACTIVE TEST")
    print("=" * 50)
    
    # Use environment variable for API key
    bridge = ClaudeMCPBridge()
    
    print("✅ Claude API connected!")
    print("🔧 8 MCP tools available")
    print()
    print("💡 TRY THESE COMMANDS:")
    print("1. 'Open the dashboard'")
    print("2. 'Generate an executive report'") 
    print("3. 'Export all data to a file'")
    print("4. 'Check system status'")
    print("5. 'What companies have compliance issues?'")
    print("6. Type 'exit' to quit")
    print("=" * 50)
    
    while True:
        try:
            question = input("\n🤖 Ask Claude: ").strip()
            
            if question.lower() in ['exit', 'quit', 'salir']:
                print("👋 Goodbye!")
                break
                
            if not question:
                continue
                
            print("\n" + "="*60)
            print(f"🔍 Processing: '{question}'")
            print("⏳ Claude is thinking...")
            
            # Ask Claude
            response = await bridge.ask_claude(question)
            
            print("\n📝 CLAUDE'S RESPONSE:")
            print("-" * 40)
            print(response)
            print("="*60)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(interactive_test())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")