# 🚀 Dark Data Database - Quick Start Guide

## What This Project Does

Transform buried **399-page PDF reports** into **queryable intelligence** using a Dark Data Database approach.

### Key Value Delivered:
- ⚡ **11,066 MW blackout** → Actionable insights in seconds
- 📊 **ENEL 92% late reports** → Compliance risk alerts  
- ⚙️ **Siemens 6.7 years old** → Predictive maintenance warnings
- 🔍 **AI-queryable data** → Direct database access via MCP

---

## 🏃‍♂️ Quick Start (5 minutes)

### Prerequisites
- Python 3.12+
- Linux/macOS terminal

### Step 1: Setup Environment
```bash
# Navigate to project
cd "/path/to/Proyecto Dark Data CEN"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install flask mcp
```

### Step 2: Create Database & Load Data
```bash
# Create SQLite database from schema
python3 -c "import sqlite3; conn = sqlite3.connect('dark_data.db'); conn.executescript(open('database_schema.sql').read()); conn.close(); print('Database created!')"

# Load JSON data into database
python3 ingest_data.py
```
**Expected Output:**
```
✅ Data ingestion completed successfully!
incidents: 1 records
companies: 3 records  
compliance_reports: 3 records
equipment: 1 records
```

### Step 3: Generate Insights
```bash
# Run analysis queries
python3 analysis_queries.py
```
**Key Insights Generated:**
- Total MW Affected: 11,066.23 MW
- ENEL Compliance: 7.9% (CRITICAL)
- Equipment Age: 6.7 years (Medium Risk)
- Cascade Timeline: 5-second system collapse

### Step 4: Launch Web Dashboard
```bash
# Start dashboard (runs in background)
python3 dashboard.py
```
**Access at:** http://localhost:5000
- 📊 Real-time overview stats
- 📋 Compliance tracking with visual alerts  
- 🔌 Generation impact by technology
- ⚙️ Equipment aging analysis

### Step 5: Test MCP AI Integration
```bash
# Test basic MCP server
python3 test_mcp.py

# Test enhanced MCP server with system tools
python3 test_new_tools_direct.py

# Test interactive Claude integration
python3 test_claude_interactive.py
```
**Expected Output:**
```
✅ MCP Server connected successfully!
🔧 4 tools available for AI access
📄 2 resources exposed
🎉 Your Dark Data is now MCP-ready!
✨ Enhanced tools: dashboard, reports, system control
```

### Step 6: Setup Claude Desktop (Optional)
```bash
# Automated Claude Desktop configuration
./setup_claude_mcp.sh

# Start semantic Claude bridge  
./run_claude_bridge.sh
```
**New Features:**
- 🧠 Semantic tool selection with embeddings
- 🎯 Direct Claude Desktop integration
- 🔧 Enhanced MCP server with system controls
- 📊 Dashboard auto-launch capabilities

---

## 🎯 What You Just Built

### Architecture Overview
```
PDF Reports → JSON → SQLite → Analysis + Dashboard + MCP
    ↓           ↓        ↓         ↓           ↓        ↓
399 pages → Structured → Database → Insights → WebUI → AI Access
```

### Core Components Created:
1. **Database** (`dark_data.db`) - SQLite with JSON fields
2. **Ingestion** (`ingest_data.py`) - PDF → Database pipeline  
3. **Analysis** (`analysis_queries.py`) - Insight extraction
4. **Dashboard** (`dashboard.py`) - Web visualization
5. **MCP Server** (`mcp_server.py`) - AI integration

### Key Files:
- `database_schema.sql` - Database structure
- `power_system_failure_analysis.json` - Source data
- `templates/dashboard.html` - Web interface
- `mcp_config.json` - MCP configuration
- `claude_mcp_setup.md` - Claude Desktop setup guide
- `mcp_server_enhanced.py` - Enhanced MCP with system tools
- `claude_mcp_bridge_semantic.py` - Semantic AI integration

---

## 🔥 Demo Script (for Stakeholders)

### Problem Statement:
*"We have 399-page PDF reports sitting unused. Critical compliance issues and equipment failures are buried in text."*

### Solution Demonstration:

1. **Show Raw Data Challenge:**
   - Open `data/EAF-089-2025_reduc.pdf` (399 pages)
   - *"Find ENEL's compliance rate manually"* → Takes hours

2. **Show Database Solution:**
   ```bash
   python3 analysis_queries.py
   ```
   - **Result:** ENEL 7.9% compliance in 2 seconds

3. **Show Dashboard Value:**
   - Open http://localhost:5000
   - Visual compliance alerts, equipment aging warnings
   - **ROI:** Prevent regulatory fines, predictive maintenance

4. **Show AI Integration:**
   ```bash
   python3 test_mcp.py
   ```
   - AI can now query: *"What caused the blackout?"*
   - **Result:** Direct access to failure analysis

### Business Impact:
- ⚡ **Speed:** Hours → Seconds for insight generation
- 💰 **Cost Savings:** Prevent compliance fines, equipment failures
- 🤖 **AI Ready:** Future-proof with direct AI integration
- 📈 **Scalable:** Add more reports, data sources easily

---

## ✅ Success Criteria

Your Dark Data Database is working when:
- [ ] Database loads 1 incident + 3 companies
- [ ] Analysis shows ENEL 7.9% compliance  
- [ ] Dashboard displays at http://localhost:5000
- [ ] MCP test shows 4 tools + 2 resources
- [ ] Search finds equipment by manufacturer

**Time to Value:** 5 minutes from zero to AI-queryable insights!

---

## 🚀 Next Steps

Ready to scale? See `TECHNICAL_DOCUMENTATION.md` for:
- Vector embeddings (semantic search)
- Cloud data lake migration  
- Real-time streaming ingestion
- Machine learning predictions
- Enterprise security features

**Your dark data is now intelligent data!** 🎉