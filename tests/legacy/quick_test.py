#!/usr/bin/env python3
"""
Quick one-shot tests for specific tools
"""

import asyncio
from claude_mcp_bridge import ClaudeMCPBridge

async def quick_tests():
    """Run quick tests of specific functionality"""
    # Use environment variable for API key  
    bridge = ClaudeMCPBridge()
    
    tests = [
        "Check system status",
        "Open dashboard", 
        "Generate executive report",
        "What companies have compliance problems?"
    ]
    
    print("🚀 QUICK CLAUDE+MCP TESTS")
    print("=" * 40)
    
    for i, test in enumerate(tests, 1):
        print(f"\n{i}. TESTING: '{test}'")
        print("-" * 30)
        
        try:
            response = await bridge.ask_claude(test)
            # Show first 200 characters
            preview = response[:200] + "..." if len(response) > 200 else response
            print(f"✅ SUCCESS: {preview}")
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    asyncio.run(quick_tests())