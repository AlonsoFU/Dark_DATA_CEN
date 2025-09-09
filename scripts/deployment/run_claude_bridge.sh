#!/bin/bash
"""
Quick start script for Claude MCP Bridge
"""

echo "🚀 CLAUDE + MCP BRIDGE"
echo "======================"
echo ""
echo "⚠️  IMPORTANT: You need a Claude API key first!"
echo "   1. Go to: https://console.anthropic.com/"
echo "   2. Create account / Sign in"
echo "   3. Get API key (starts with sk-ant-...)"
echo ""
echo "🔧 SET YOUR API KEY:"
echo "   Option A: export ANTHROPIC_API_KEY=sk-ant-your-key-here"
echo "   Option B: Edit claude_mcp_bridge.py line ~30"
echo ""

read -p "Do you have your API key ready? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -z "$ANTHROPIC_API_KEY" ]; then
        echo "⚠️  API key not set as environment variable"
        echo "   Run: export ANTHROPIC_API_KEY=sk-ant-your-key-here"
        echo "   Or edit the script to add your key directly"
        exit 1
    fi
    
    echo "✅ API key found, starting bridge..."
    
    cd "/home/alonso/Documentos/Github/Proyecto Dark Data CEN"
    source venv/bin/activate
    python3 claude_mcp_bridge.py
else
    echo ""
    echo "📝 NEXT STEPS:"
    echo "1. Get API key: https://console.anthropic.com/"
    echo "2. Set key: export ANTHROPIC_API_KEY=sk-ant-your-key"
    echo "3. Run: ./run_claude_bridge.sh"
fi