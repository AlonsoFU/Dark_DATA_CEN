#!/bin/bash
"""
Setup script for Claude Desktop MCP integration
This configures Claude to use your dark data MCP server
"""

echo "🤖 Setting up Claude Desktop MCP Integration"
echo "============================================="

# Get current directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📁 Project directory: $PROJECT_DIR"

# Detect OS and find Claude config directory
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
    OS_NAME="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    CLAUDE_CONFIG_DIR="$HOME/.config/Claude"
    OS_NAME="Linux"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows
    CLAUDE_CONFIG_DIR="$APPDATA/Claude"
    OS_NAME="Windows"
else
    echo "❌ Unsupported OS: $OSTYPE"
    exit 1
fi

echo "🖥️  Operating System: $OS_NAME"
echo "📂 Claude config directory: $CLAUDE_CONFIG_DIR"

# Create Claude config directory if it doesn't exist
mkdir -p "$CLAUDE_CONFIG_DIR"
echo "✅ Created Claude config directory"

# Create the MCP configuration
CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"

echo "📝 Creating MCP configuration..."

# Get Python path from virtual environment
PYTHON_PATH="$PROJECT_DIR/venv/bin/python"
if [[ ! -f "$PYTHON_PATH" ]]; then
    # Fallback to system python
    PYTHON_PATH="python3"
    echo "⚠️  Virtual environment not found, using system python"
else
    echo "🐍 Using virtual environment python: $PYTHON_PATH"
fi

# Create the configuration
cat > "$CONFIG_FILE" << EOF
{
  "mcpServers": {
    "dark-data": {
      "command": "$PYTHON_PATH",
      "args": [
        "$PROJECT_DIR/mcp_server.py"
      ],
      "cwd": "$PROJECT_DIR",
      "env": {
        "PATH": "$PROJECT_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin",
        "PYTHONPATH": "$PROJECT_DIR/venv/lib/python3.12/site-packages:$PROJECT_DIR"
      }
    }
  }
}
EOF

echo "✅ Created Claude Desktop configuration"

# Verify the configuration file
echo "📋 Configuration file contents:"
echo "================================"
cat "$CONFIG_FILE"
echo "================================"

# Test MCP server
echo ""
echo "🧪 Testing MCP server..."
cd "$PROJECT_DIR"
if [[ -f "venv/bin/activate" ]]; then
    source venv/bin/activate
fi

python3 test_mcp.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ MCP server test passed"
else
    echo "❌ MCP server test failed"
    echo "   Run 'python3 test_mcp.py' to see details"
fi

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "📝 Next Steps:"
echo "1. Install Claude Desktop: https://claude.ai/download"
echo "2. Sign in to Claude Desktop"
echo "3. Restart Claude Desktop (to load new config)"
echo "4. Look for the MCP connection indicator (🔌 icon)"
echo ""
echo "✅ When connected, you'll see:"
echo "   • MCP server: 'dark-data' connected"  
echo "   • 4 tools available"
echo "   • 2 resources available"
echo ""
echo "🤖 Try asking Claude:"
echo "   • 'What caused the February 2025 blackout?'"
echo "   • 'Which companies have compliance issues?'"
echo "   • 'Show me equipment failure patterns'"
echo "   • 'What was the timeline of the system collapse?'"
echo ""
echo "🔧 If issues occur:"
echo "   • Check Claude Desktop logs (Help → Show Logs)"
echo "   • Verify paths in: $CONFIG_FILE"
echo "   • Test server: python3 test_mcp.py"