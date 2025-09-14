# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Dark Data Platform** - an enterprise-grade system that transforms buried PDF reports (power system failure reports) into AI-queryable intelligence. The core architecture follows: `PDF → JSON → SQLite → MCP → AI Access`.

## Key Commands

### Quick Start
```bash
# Install dependencies
make install        # Production dependencies only
make install-dev    # Development dependencies + pre-commit hooks

# Setup database and ingest data
make setup-db
make ingest-data

# Run applications
make run-web        # Flask web dashboard at http://localhost:5000
make run-cli        # Command-line interface
make run-mcp        # MCP server for AI integration
```

### Development Workflow
```bash
# Testing
make test           # Full test suite with coverage
make test-quick     # Unit tests only

# Code quality
make lint           # Check code quality (flake8, mypy, black, isort)
make format         # Auto-format code

# Build and deployment
make build          # Build Python package
docker-compose up -d # Run with Docker
```

### Document Processing
```bash
# Database operations
make setup-db       # Create database from schema
make ingest-data    # Load JSON data into database

# Document structure learning
make learn-structure   # Learn document structure from data/raw/*.json
make analyze-patterns  # Analyze patterns without learning
make learn-discovery   # Discovery phase (3-5 documents)
make learn-validation  # Validation phase
make test-structure    # Test learned structure on new documents

# Direct Python execution
python scripts/database_tools/ingest_data.py
python scripts/database_tools/analysis_queries.py
python scripts/database_tools/learn_document_structure.py
```

### EAF Document Processing Workflows
```bash
# ANEXO 1 (Generation Programming) - 95% Complete
cd scripts/eaf_workflows/eaf_processing/chapters/anexo_01_generation_programming
python content_extraction/extract_anexo1_with_ocr_per_row.py
python validation_quality/apply_corrections_with_review_summary.py
python final_generation/generate_final_complete_json.py

# ANEXO 2 (Real Generation) - Production Ready
cd scripts/eaf_workflows/eaf_processing/chapters/anexo_02_real_generation
# 185+ solar plants extracted with 90%+ success rate

# Next priority: ANEXO 5-6 (High business value)
# Company reports and compliance data extraction
```

## Architecture Overview

### Package Structure
```
dark_data/                   # Main Python package
├── core/                    # Core business logic and AI interfaces
├── database/                # SQLite database layer and connections
├── processors/              # Document processing pipeline
├── analyzers/              # Pattern detection and structure learning
├── extractors/             # PDF extraction utilities
├── mcp/                    # Model Context Protocol integration
│   ├── servers/            # MCP servers (standard & enhanced)
│   ├── clients/            # MCP client implementations
│   └── bridges/            # Claude API bridges
├── web/                    # Flask web dashboard
└── cli/                    # Command-line interfaces

scripts/                    # Processing and analysis scripts
├── database_tools/         # Core data management and analysis
├── eaf_workflows/          # Complete EAF processing pipeline
├── document_processing/    # Generic document utilities
└── system_utils/          # Infrastructure and maintenance

data/                       # Data storage
├── databases/              # SQLite databases
├── documents/              # Organized document collections
│   ├── anexos_EAF/        # Power system failure reports
│   └── power_system_reports/ # Additional power system data
└── processed/              # Processed document chunks

profiles/                   # Document processing profiles
└── anexos_eaf/            # Anexos EAF processing profile (Phase 1 complete)

config/                     # Configuration and schemas
└── schemas/                # Database schema definitions

requirements/               # Dependency management
├── base.txt               # Core dependencies (pandas, flask, matplotlib, etc)
├── dev.txt                # Development tools (pytest, black, mypy, pre-commit)
└── prod.txt               # Production-specific dependencies
```

### Core Components
1. **Database Layer** (`dark_data/database/`): SQLite with JSON storage + FTS5 search
2. **Document Processing** (`dark_data/processors/`): Adaptive PDF processing pipeline
3. **Pattern Analysis** (`dark_data/analyzers/`): Structure learning and pattern detection
4. **PDF Extraction** (`dark_data/extractors/`): PDF parsing and OCR utilities
5. **Web Dashboard** (`dark_data/web/`): Flask application with visualizations
6. **MCP Integration** (`dark_data/mcp/`): AI model connectivity via MCP protocol
7. **CLI Tools** (`dark_data/cli/`): Command-line database viewers
8. **Core AI Logic** (`dark_data/core/`): Business logic and AI interfaces

### Database Schema
- `incidents` - Power system failure incidents with JSON metadata
- `companies` - Company information and compliance data
- `compliance_reports` - Regulatory compliance tracking
- `equipment` - Protection equipment specifications
- `incidents_fts` - Full-text search virtual table

## Development Patterns

### Path Resolution Pattern
```python
# All components use pathlib for cross-platform compatibility
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
db_path = project_root / "data" / "databases" / "dark_data.db"
```

### Database Connection Pattern
```python
def get_connection(self):
    conn = sqlite3.connect(self.db_path)
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    return conn
```

### Interactive Processing Pattern (Anexos EAF Profile)
```python
# Phase-based approach with user validation:
# 1. Load existing patterns from profiles/anexos_eaf/
# 2. Show candidates to user for validation
# 3. Save only user-approved results
# 4. Follow: Title Detection → Pattern Development → Data Extraction
```

### MCP Tool Pattern
```python
@server.call_tool()
async def tool_name(arguments: dict) -> list[types.TextContent]:
    # Process arguments, query database, format response
    return [types.TextContent(type="text", text=result)]
```

## Key File Locations

### Core Application Files
- `dark_data/web/dashboard.py` - Flask web dashboard
- `dark_data/cli/simple_viewer.py` - Command-line database viewer
- `dark_data/database/database_viewer.py` - Advanced database interface
- `dark_data/mcp/servers/mcp_server.py` - Standard MCP server
- `dark_data/mcp/servers/mcp_server_enhanced.py` - Enhanced MCP server

### Configuration & Data
- `config/schemas/database_schema.sql` - Database schema definition
- `data/databases/dark_data.db` - Main SQLite database
- `data/documents/anexos_EAF/` - Power system failure reports
- `data/processed/` - Processed document chunks

### Processing Scripts
- `scripts/database_tools/ingest_data.py` - Data ingestion pipeline
- `scripts/database_tools/analysis_queries.py` - Database analysis queries
- `scripts/database_tools/learn_document_structure.py` - Document structure learning
- `scripts/eaf_workflows/eaf_processing/chapters/anexo_01_generation_programming/content_extraction/extract_anexo1_with_ocr_per_row.py` - OCR-based extraction

### Anexos EAF Profile (Phase 1 Complete)
- `profiles/anexos_eaf/validated_titles.json` - 10 validated chapter titles
- `profiles/anexos_eaf/tools/show_title_candidates.py` - Title validation tool

### Development Configuration
- `pyproject.toml` - Python packaging with CLI entry points
- `Makefile` - Development automation commands
- `requirements/` - Dependency management (base.txt, dev.txt, prod.txt)

## Testing

```bash
make test           # Full test suite with coverage
make test-quick     # Unit tests only
pytest tests/unit/  # Specific test category
```

## Deployment

### Local Development
```bash
make install-dev    # Install with development dependencies
make run-web        # Run Flask app with auto-reload
```

### Docker
```bash
docker-compose up -d  # Full stack deployment
```

## MCP Integration

### Available Servers
- `dark_data/mcp/servers/mcp_server.py` - Standard MCP server (4 core tools)
- `dark_data/mcp/servers/mcp_server_enhanced.py` - Enhanced MCP server with system tools
- `dark_data/mcp/bridges/` - Claude API bridges with semantic tool selection

### Setup
```bash
make run-mcp  # Start MCP server
```

## Code Quality

```bash
make lint     # Check code quality (black, isort, flake8, mypy)
make format   # Auto-format code
pre-commit install  # Install pre-commit hooks
```

## EAF Processing Status (Major Progress)

### Current Status
- **ANEXO 1**: 🚀 **95% Complete** (59/62 pages) - Generation programming tables
- **ANEXO 2**: ✅ **Production Ready** - 185+ solar plants extracted (90%+ success rate)
- **Next Priority**: ANEXO 5-6 (Company reports & compliance data - high business value)
- **Database**: Ready for renewable energy intelligence ingestion

### EAF Processing Workflow
1. **Title Detection**: ✅ Complete (10 chapters identified with 100% accuracy)
2. **Content Extraction**: 🔄 In progress (ANEXO 1: 95%, ANEXO 2: Complete)
3. **Validation Pipeline**: ✅ User-approved extractions prevent hallucinations
4. **Structured Output**: JSON with metadata and business intelligence

## Important Notes

- **Python 3.11+** required for modern typing features
- **Cross-platform paths** - All components use pathlib for file path resolution
- **Interactive validation** - User approves all extractions to prevent hallucinations
- **Modular design** - Each component in `dark_data/` is independently testable
- **SQLite database** - Zero-config file-based database with JSON support