# 🤖 Using Claude with MCP - Dark Data Integration

## Setup Claude Desktop with Your MCP Server

### Step 1: Install Claude Desktop
1. Download Claude Desktop from: https://claude.ai/download
2. Install and sign in with your Anthropic account

### Step 2: Configure MCP Server
1. **Find Claude's config directory:**
   - **macOS**: `~/Library/Application Support/Claude/`
   - **Windows**: `%APPDATA%\Claude\`
   - **Linux**: `~/.config/Claude/`

2. **Create/edit `claude_desktop_config.json`:**
```json
{
  "mcpServers": {
    "dark-data": {
      "command": "python",
      "args": [
        "/home/alonso/Documentos/Github/Proyecto Dark Data CEN/mcp_server.py"
      ],
      "cwd": "/home/alonso/Documentos/Github/Proyecto Dark Data CEN",
      "env": {
        "PATH": "/home/alonso/Documentos/Github/Proyecto Dark Data CEN/venv/bin:/usr/bin:/bin",
        "PYTHONPATH": "/home/alonso/Documentos/Github/Proyecto Dark Data CEN/venv/lib/python3.12/site-packages"
      }
    }
  }
}
```

3. **Restart Claude Desktop**

### Step 3: Verify Connection
When Claude Desktop starts, you should see:
- 🔌 **MCP icon** in the interface
- **"dark-data" server** listed as connected
- **4 tools available** indicator

---

## 📋 Available Tools & Resources

### Tools You Can Ask Claude to Use:

#### 1. `search_incidents`
**What it does:** Search power system failures by keywords
**Example questions:**
```
"Search for all incidents involving Siemens equipment"
"Find failures related to protection systems" 
"Show me incidents from February 2025"
```

#### 2. `get_compliance_report`  
**What it does:** Get company compliance analysis
**Example questions:**
```
"Which companies have compliance issues?"
"Show me ENEL's reporting status"
"What's the overall compliance situation?"
```

#### 3. `analyze_equipment_failures`
**What it does:** Equipment risk assessment and aging analysis  
**Example questions:**
```
"What equipment failed and how old was it?"
"Are there any high-risk equipment patterns?"
"Show me equipment that needs maintenance"
```

#### 4. `get_incident_timeline`
**What it does:** Detailed timeline with cascade effects
**Example questions:**
```
"Show me the complete timeline of the 2025 blackout"
"What was the sequence of events during the failure?"
"How did the system collapse cascade through the grid?"
```

### Resources Available:

#### 1. Database Schema
**What it contains:** Complete database structure
**Ask Claude:** "What data is available in the dark data database?"

#### 2. Database Statistics  
**What it contains:** Current data counts and metrics
**Ask Claude:** "What's the current status of the database?"

---

## 🎯 Example Conversation with Claude

### Question: "What caused the February 2025 blackout?"

**Claude's Response Process:**
1. 🔍 Calls `search_incidents("February 2025 blackout")`
2. 🕐 Calls `get_incident_timeline("EAF-089/2025")`
3. ⚙️ Calls `analyze_equipment_failures()`

**Claude's Answer:**
> The February 2025 blackout (EAF-089/2025) was caused by an unexpected activation of the Siemens 7SL87 differential line protection system. Here's what happened:
> 
> **Root Cause:** The protection system's communication module failed, and during the recovery attempt, the differential line protection (87L) function had an unexpected activation.
> 
> **Equipment Details:**
> - Manufacturer: Siemens
> - Model: 7SL87  
> - Age: 6.7 years (installed May 31, 2018)
> - Risk Level: Medium Risk (approaching 7+ year threshold)
> 
> **System Impact:**
> - Total blackout affecting 11,066 MW (100% of system demand)
> - Cascade timeline: 5-second southern island collapse
> - 8 power plants affected across multiple technologies
> - Recovery varied by technology: Hydro fastest, thermal slowest

### Question: "Which companies are non-compliant with reporting?"

**Claude's Response Process:**
1. 📊 Calls `get_compliance_report()`

**Claude's Answer:**
> Based on the compliance analysis, here are the companies with reporting issues:
> 
> **🔴 CRITICAL - ENEL GENERACIÓN CHILE S.A.:**
> - Compliance Rate: Only 7.9% (3 out of 38 reports on time)
> - Status: 92% of reports late - major regulatory risk
> - Issues: Chronic late reporting pattern
> 
> **🟡 MODERATE - COLBÚN S.A.:**
> - Compliance Rate: 77.8% (14 out of 18 reports on time)  
> - Issues: Some late reports + 1 missing report
> 
> **🟡 NEEDS IMPROVEMENT - INTERCHILE S.A.:**
> - Compliance Rate: 50.0% (1 out of 2 reports on time)
> - Status: Half of reports late
> 
> **Recommendation:** ENEL requires immediate attention for compliance automation.

---

## 🛠️ Troubleshooting MCP Connection

### Issue: "MCP server not connecting"
```bash
# 1. Test MCP server manually
cd "/home/alonso/Documentos/Github/Proyecto Dark Data CEN"
source venv/bin/activate
python test_mcp.py

# 2. Check Claude config path
# Ensure claude_desktop_config.json is in correct location

# 3. Verify paths in config
# Make sure all paths are absolute, not relative
```

### Issue: "Tools not appearing in Claude"
1. **Restart Claude Desktop** after config changes
2. **Check logs** in Claude Desktop (Help → Show Logs)
3. **Verify Python environment** is activated in config

### Issue: "Database not found"
```bash
# Ensure database exists and is populated
cd "/home/alonso/Documentos/Github/Proyecto Dark Data CEN"
ls -la dark_data.db  # Should exist and be ~10KB+
python ingest_data.py  # Re-run if needed
```

---

## 🎯 Advanced Usage Tips

### 1. **Multi-step Analysis**
```
"Analyze the complete impact of the 2025 blackout: what caused it, 
which companies were affected, what equipment failed, and what 
was the timeline of recovery?"
```

### 2. **Compliance Monitoring**
```
"Create a compliance risk report showing which companies need 
immediate attention and what the regulatory implications are."
```

### 3. **Predictive Insights**
```
"Based on the equipment failure patterns, what other equipment 
should we monitor for potential failures?"
```

### 4. **Cross-Reference Analysis**  
```
"Compare the compliance rates with the companies that had the 
most generation units affected in the blackout."
```

---

## 🚀 Alternative MCP Clients

If you don't use Claude Desktop, you can use:

### 1. **VS Code with MCP Extension**
```json
// .vscode/settings.json
{
  "mcp.servers": {
    "dark-data": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/project"
    }
  }
}
```

### 2. **Custom Python Client**
```python
# custom_mcp_client.py
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def ask_question(question: str):
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
        cwd="/home/alonso/Documentos/Github/Proyecto Dark Data CEN"
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools.tools]}")
            
            # Example: Search for incidents
            if "search" in question.lower():
                result = await session.call_tool("search_incidents", {"query": question})
                for content in result.content:
                    print(content.text)

# Usage
asyncio.run(ask_question("What caused the blackout?"))
```

### 3. **Web Interface MCP Client**
```bash
# Start web-based MCP client
python mcp_web_client.py
# Access at http://localhost:8000
```

---

## 📊 Monitoring MCP Usage

### Check Tool Usage Stats
```python
# Add to mcp_server.py for monitoring
tool_usage_stats = {
    "search_incidents": 0,
    "get_compliance_report": 0, 
    "analyze_equipment_failures": 0,
    "get_incident_timeline": 0
}

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    tool_usage_stats[name] += 1
    print(f"Tool usage: {tool_usage_stats}")
    # ... rest of function
```

Your MCP server is now ready for AI integration! Claude (or any MCP-compatible LLM) can directly query your dark data and provide intelligent analysis.