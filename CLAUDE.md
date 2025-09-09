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
python scripts/ingest_data.py
python scripts/analysis_queries.py
```

### Interactive Anexos EAF Processing
```bash
# Continue with established profile (Phase 1 completed: 10 titles identified)
python profiles/anexos_eaf/tools/show_title_candidates.py [document.pdf]
# Interactive title validation and pattern development
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
├── analysis/               # Data exploration and pattern analysis
└── session_management/     # Processing session tracking

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
├── base.txt               # Core production dependencies
├── dev.txt                # Development tools
└── prod.txt               # Production-specific dependencies
```

### Core Components
1. **Database Layer** (`dark_data/database/`): SQLite with JSON storage + FTS5 search
2. **Document Processing** (`dark_data/processors/`): Adaptive PDF processing pipeline
3. **Pattern Analysis** (`dark_data/analyzers/`): Structure learning and pattern detection
4. **Web Dashboard** (`dark_data/web/`): Flask application with visualizations
5. **MCP Integration** (`dark_data/mcp/`): AI model connectivity via MCP protocol
6. **CLI Tools** (`dark_data/cli/`): Command-line database viewers

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
- `scripts/ingest_data.py` - Data ingestion pipeline
- `scripts/analysis_queries.py` - Database analysis queries
- `scripts/interactive_title_detector.py` - Interactive document processing
- `scripts/extract_anexo1_with_ocr_per_row.py` - OCR-based extraction

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

## Anexos EAF Processing Profile

### Current Status
- **Phase 1 COMPLETE**: Title detection (10 chapters identified with 100% accuracy)
- **Phase 2 IN PROGRESS**: Content pattern development for high-value sections
- **Tool**: `python profiles/anexos_eaf/tools/show_title_candidates.py [document.pdf]`

### Interactive Processing Approach
1. Load existing patterns from `profiles/anexos_eaf/`
2. Show candidates to user for validation
3. Save only user-approved results
4. Follow phase-based approach: Title Detection → Pattern Development → Data Extraction

## Important Notes

- **Python 3.11+** required for modern typing features
- **Cross-platform paths** - All components use pathlib for file path resolution
- **Interactive validation** - User approves all extractions to prevent hallucinations
- **Modular design** - Each component in `dark_data/` is independently testable
- **SQLite database** - Zero-config file-based database with JSON support