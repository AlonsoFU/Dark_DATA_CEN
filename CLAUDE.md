# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Dark Data Platform** - an enterprise-grade system that transforms buried PDF reports (Chilean power system documents) into AI-queryable intelligence. The core architecture follows: `PDF → JSON → SQLite → MCP → AI Access`.

## Key Commands

### Quick Start
```bash
# Install dependencies
make install        # Production dependencies only
make install-dev    # Development dependencies + pre-commit hooks

# Setup database and ingest data
make setup-db       # Create database from platform_data/schemas/database_schema.sql
make ingest-data    # Load JSON data into database

# Run applications
make run-web        # Flask web dashboard at http://localhost:5000
make run-cli        # Command-line interface
make run-mcp        # Core MCP server for AI integration
```

### Development Workflow
```bash
# Testing
make test           # Full test suite with coverage
make test-quick     # Unit tests only
pytest tests/unit/  # Specific test category

# Code quality
make lint           # Check code quality (flake8, mypy, black, isort)
make format         # Auto-format code
make clean          # Clean build artifacts

# Build and deployment
make build          # Build Python package
make docs           # Generate documentation with Sphinx
```

### Document Processing
```bash
# Database operations
make setup-db       # Create SQLite database with schema
make ingest-data    # Load processed JSON into database

# Document structure learning
make learn-structure   # Learn document structure from data
make analyze-patterns  # Analyze patterns without learning
make learn-discovery   # Discovery phase (3-5 documents)
make learn-validation  # Validation phase
make test-structure    # Test learned structure on new documents

# Direct processing scripts
python shared_platform/database_tools/ingest_data.py
python shared_platform/database_tools/learn_document_structure.py
```

### EAF Document Processing
```bash
# ANEXO 1 (Generation Programming) - ✅ Complete
cd domains/operaciones/anexos_eaf/chapters/anexo_01/processors
python anexo_01_processor.py

# ANEXO 2 (Real Generation) - ✅ Complete
cd domains/operaciones/anexos_eaf/chapters/anexo_02/processors
python anexo_02_processor.py
# 185+ solar plants extracted with 90%+ success rate

# INFORME DIARIO (Daily Reports) - ✅ Ready
cd domains/operaciones/anexos_eaf/chapters/informe_diario/processors
python informe_diario_processor.py

# All chapters follow standardized structure:
# domains/operaciones/anexos_eaf/chapters/{chapter}/
# ├── docs/           # Documentation and patterns
# ├── processors/     # Chapter-specific processing code
# ├── outputs/        # Processing outputs
# │   ├── raw_extractions/
# │   ├── validated_extractions/
# │   └── universal_json/
# └── universal_schema_adapters/ # Schema transformation utilities
#
# Shared resources at: domains/operaciones/anexos_eaf/shared/
```

### MCP Servers
```bash
# Run AI Platform MCP servers
cd ai_platform/mcp_servers
python operaciones_server.py       # Grid operations intelligence
python mercados_server.py          # Energy market analysis
python legal_server.py             # Legal compliance analysis
python cross_domain_server.py      # Cross-domain intelligence
python core_server.py              # Core platform server
python enhanced_server.py          # Enhanced capabilities
python resource_discovery_server.py # Resource discovery
```

## Architecture Overview

The Dark Data Platform follows a domain-driven architecture for processing Chilean electrical system documents:

### Core Components

#### 1. Domain Processing (`domains/`)
- **operaciones/**: Grid operations and EAF document processing ✅ Active
  - `anexos_eaf/` - 3 chapters complete (anexo_01, anexo_02, informe_diario)
  - `shared/` - Domain utilities and universal schema adapters
- **mercados/**: Energy market data (empty - planned)
- **legal/**: Legal compliance documents (empty - planned)
- **planificacion/**: Planning and development (empty - planned)

#### 2. AI Intelligence Platform (`ai_platform/`)
- **mcp_servers/**: MCP servers for AI integration (17 servers)
- **processors/**: Cross-domain data processing pipelines
- **analyzers/**: Pattern detection and structure learning
- **extractors/**: PDF parsing and data extraction utilities
- **core/**: Core AI business logic and interfaces

#### 3. Platform Services (`shared_platform/`)
- **web/**: Flask web dashboard for visualization
- **cli/**: Command-line interfaces for data queries
- **database_tools/**: Database management and ingestion tools

#### 4. Data Layer (`platform_data/`)
- **database/**: Unified SQLite database with all extracted data
- **schemas/**: Database schema definitions

### Data Flow
```
PDF Documents → AI Extractors → JSON → SQLite → MCP Servers → AI Queries
```

## CLI Entry Points

The platform provides command-line tools (note: pyproject.toml needs to be updated to match actual structure):
```bash
# Current entry points defined in pyproject.toml (need correction):
dark-data            # Should point to shared_platform.cli.main:main
dark-data-web        # Should point to shared_platform.web.dashboard:main
dark-data-mcp        # Should point to ai_platform.mcp_servers.core_server:main

# Direct usage until entry points are fixed:
python -m shared_platform.cli.main
python -m shared_platform.web.dashboard
python -m ai_platform.mcp_servers.core_server
```

## Development Patterns

### Path Resolution Pattern
```python
# All components use pathlib for cross-platform compatibility
from pathlib import Path
project_root = Path(__file__).parent.parent
db_path = project_root / "platform_data" / "database" / "dark_data.db"
```

### Database Connection Pattern
```python
def get_connection(self):
    conn = sqlite3.connect(self.db_path)
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    return conn
```

### MCP Tool Pattern
```python
# Standard MCP server tool pattern
@server.call_tool()
async def tool_name(arguments: dict) -> list[types.TextContent]:
    # Process arguments, query database, format response
    return [types.TextContent(type="text", text=result)]
```

### Universal Schema Transformation Pattern
```python
# All chapter processors should transform to universal schema
from domains.operaciones.anexos_eaf.shared.universal_schema_adapters import (
    extractor_universal_integrado
)

# Transform chapter-specific extraction to universal format
universal_data = extractor_universal_integrado.transform(
    chapter_data,
    chapter_type="anexo_01",
    source_document="EAF-089-2025"
)
```

## Key Files and Locations

### Configuration Files
- `platform_data/schemas/database_schema.sql` - Database schema definition
- `pyproject.toml` - Python packaging and tool configuration
- `Makefile` - Development automation commands
- `requirements/base.txt` - Core dependencies
- `requirements/dev.txt` - Development dependencies

### Core Application Entry Points
- `shared_platform/web/dashboard.py` - Flask web dashboard
- `shared_platform/cli/main.py` - Command-line interface
- `ai_platform/mcp_servers/core_server.py` - Main MCP server
- `shared_platform/database_tools/ingest_data.py` - Data ingestion tool

### Domain Processing
- `domains/operaciones/anexos_eaf/` - EAF document processing (Chilean electrical system)
  - `chapters/{chapter}/` - Standardized chapter structure with docs/, config/, processors/, outputs/
  - `shared/universal_schema_adapters/` - Universal JSON schema transformation utilities
- `domains/operaciones/shared/` - Shared utilities and scrapers
- `ai_platform/mcp_servers/` - MCP servers for AI integration (17 servers)

### Database and Data
- `platform_data/database/dark_data.db` - Main SQLite database
- Database tables: `incidents`, `companies`, `compliance_reports`, `equipment`, `incidents_fts`

## Development Patterns

### Path Resolution Pattern
```python
# All components use pathlib for cross-platform compatibility
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
db_path = project_root / "platform_data" / "database" / "dark_data.db"

# Domain processing pattern
domain_root = Path(__file__).parent.parent  # Within domain
extractions_path = domain_root / "extractions"
patterns_path = domain_root / "patterns"
```

### Database Connection Pattern
```python
def get_connection(self):
    conn = sqlite3.connect(self.db_path)
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    return conn
```

### MCP Tool Pattern
```python
# Standard MCP server tool pattern
@server.call_tool()
async def tool_name(arguments: dict) -> list[types.TextContent]:
    # Process arguments, query database, format response
    return [types.TextContent(type="text", text=result)]
```

## Testing and Code Quality

```bash
# Testing
make test           # Full test suite with coverage
make test-quick     # Unit tests only
pytest tests/unit/  # Specific test category

# Code quality
make lint           # Check code quality (black, isort, flake8, mypy)
make format         # Auto-format code
pre-commit install  # Install pre-commit hooks
```

### Tool Configuration
- **Black**: Line length 88, Python 3.11+ target
- **isort**: Black-compatible profile
- **mypy**: Strict typing with Python 3.11+
- **pytest**: Coverage reporting with minimum requirements
- **pre-commit**: Automated hooks for code quality

## Chilean Electrical System Context

The platform specializes in Chilean electrical system (SEN - Sistema Eléctrico Nacional) documents:
- **Regulator**: Coordinador Eléctrico Nacional
- **Document Types**: EAF reports (ANEXO 1-8), daily operational reports, market data
- **Key Companies**: Enel Chile, Colbún S.A., AES Gener, ENGIE, Statkraft
- **Universal Schema**: JSON-LD structure for AI consumption with cross-references
