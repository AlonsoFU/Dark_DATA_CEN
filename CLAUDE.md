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

### EAF Document Processing (Anexos)
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

### EAF Document Processing (Individual Reports)
```bash
# New EAF domain for individual failure analysis reports
cd domains/operaciones/eaf/

# Chapter 1: Descripción de la Perturbación
cd chapters/capitulo_01_descripcion_perturbacion/processors

# Main processor (recommended)
python final_smart_processor.py

# Experimental processors (for development/comparison):
# - coordinate_based_table_processor.py
# - complete_coordinate_processor.py
# - improved_paragraph_processor.py
# - hybrid_granularity_processor.py
# - smart_content_classifier.py
# - improved_table_formatter.py

# All EAF chapters follow same structure as anexos_eaf
# Shared resources at: domains/operaciones/eaf/shared/
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
  - `eaf/` - Individual EAF failure reports (capitulo_01 implemented)
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
- **knowledge_graph/**: Knowledge graph processing (14 files)
- **mcp_bridges/**: Claude integration bridges

#### 3. Platform Services (`shared_platform/`)
- **web/**: Flask web dashboard for visualization
- **cli/**: Command-line interfaces for data queries
- **database_tools/**: Database management and ingestion tools
- **scrapers/**: Web scraping utilities (coordinador_cl)

#### 4. Data Layer (`platform_data/`)
- **database/**: Unified SQLite database with all extracted data
- **schemas/**: Database schema definitions

### Data Flow
```
PDF Documents → AI Extractors → JSON → SQLite → MCP Servers → AI Queries
```

## Document Processing Methodology

For processing new documents, follow the comprehensive 6-phase methodology documented in `docs/metodologia/DATA_FLOW.md`:

### Quick Reference: Processing a New Document (2-6 hours)
```bash
# 1. Setup domain structure (15-30 min)
mkdir -p domains/{domain}/chapters/{doc_type}/{docs,processors,outputs}

# 2. Analyze document structure with Claude Code (30-60 min)
# Use prompts from docs/metodologia/DATA_FLOW.md Section 2

# 3. Generate and calibrate extractor (45-90 min)
# Claude Code can generate document-specific processors

# 4. Validate extractions interactively (30-60 min)
python shared_platform/cli/validation_interface.py --interactive

# 5. Transform to universal schema (15-30 min)
# Use domain-specific adapters in domains/{domain}/shared/universal_schema_adapters/

# 6. Ingest and activate MCP access (15-30 min)
make ingest-data && make run-mcp
```

### Document Processing Phases
1. **Obtención** (15-30 min): Download/organize documents
2. **Análisis Estructural** (30-60 min): Detect chapters and patterns
3. **Extracción Adaptativa** (45-90 min): Extract with domain-specific processor
4. **Validación Manual** (30-60 min): Interactive human validation
5. **Transformación Universal** (15-30 min): Convert to universal schema
6. **Ingesta y Acceso AI** (15-30 min): Load to DB and activate MCP

Full methodology: `docs/metodologia/DATA_FLOW.md`, FAQ: `docs/metodologia/DATA_FLOW_FAQ.md`, Example: `docs/metodologia/DATA_FLOW_EXAMPLE.md`

## CLI Entry Points

The platform provides command-line tools:
```bash
# Direct usage (pyproject.toml defines dark_data.* but actual modules are in ai_platform/shared_platform):
python -m shared_platform.cli.main
python -m shared_platform.web.dashboard
python -m ai_platform.mcp_servers.core_server

# Document-specific processors are run directly:
cd domains/{domain}/chapters/{chapter}/processors
python {chapter}_processor.py

# Note: Entry points in pyproject.toml reference dark_data.* which doesn't exist
# The actual module structure is ai_platform.* and shared_platform.*
```

## Development Patterns

### Path Resolution Pattern
```python
# All components use pathlib for cross-platform compatibility
from pathlib import Path

# From processor within domains/{domain}/chapters/{chapter}/processors/
project_root = Path(__file__).parent.parent.parent.parent.parent
chapter_root = Path(__file__).parent.parent
domain_root = Path(__file__).parent.parent.parent.parent

# Common paths from processor context
db_path = project_root / "platform_data" / "database" / "dark_data.db"
chapter_outputs = chapter_root / "outputs"
chapter_docs = chapter_root / "docs"
domain_shared = domain_root / "shared"

# From shared_platform or ai_platform modules
project_root = Path(__file__).parent.parent.parent
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

### Extraction Rules and Validators Pattern
```python
# Each document processor should have extraction_rules_and_validators.json
# Located at: domains/{domain}/chapters/{doc_type}/docs/extraction_rules_and_validators.json

import json
from pathlib import Path

def load_extraction_rules():
    """Load extraction rules and code validators"""
    rules_file = Path(__file__).parent.parent / "docs" / "extraction_rules_and_validators.json"
    with open(rules_file, 'r') as f:
        return json.load(f)

def validate_extraction(extracted_data, rules_config):
    """Validate extraction using defined validators"""
    validators = rules_config["code_validators"]["processor_validators"]
    # Apply validation rules and return results
    return validation_results
```

## Key Files and Locations

### Configuration Files
- `platform_data/schemas/database_schema.sql` - Database schema definition
- `pyproject.toml` - Python packaging and tool configuration (Python 3.11+)
- `Makefile` - Development automation commands
- `requirements/base.txt` - Core dependencies
- `requirements/dev.txt` - Development dependencies
- `requirements/prod.txt` - Production dependencies

### Core Application Entry Points
- `shared_platform/web/dashboard.py` - Flask web dashboard
- `shared_platform/cli/main.py` - Command-line interface
- `ai_platform/mcp_servers/core_server.py` - Main MCP server
- `shared_platform/database_tools/ingest_data.py` - Data ingestion tool

### Domain Processing
- `domains/operaciones/anexos_eaf/` - EAF annexes processing (Chilean electrical system)
  - `chapters/{chapter}/` - Standardized chapter structure with docs/, processors/, outputs/
  - `shared/universal_schema_adapters/` - Universal JSON schema transformation utilities
  - 10 validated chapters with exact page ranges in `shared/chapter_definitions.json`
- `domains/operaciones/eaf/` - Individual EAF failure reports
  - Same structure as anexos_eaf but for single incident reports
  - `chapters/capitulo_01_descripcion_perturbacion/` - Failure description processing
    - `processors/` - 7 specialized processors for different extraction strategies:
      - `final_smart_processor.py` - **Recommended** production processor
      - `coordinate_based_table_processor.py` - Coordinate-based table extraction
      - `complete_coordinate_processor.py` - Complete coordinate extraction
      - `improved_paragraph_processor.py` - Paragraph-focused extraction
      - `hybrid_granularity_processor.py` - Hybrid approach combining strategies
      - `smart_content_classifier.py` - Content classification
      - `improved_table_formatter.py` - Table formatting utilities
    - `outputs/` - Processing outputs with structured README documentation
- `domains/operaciones/shared/` - Cross-domain shared utilities and scrapers
- `ai_platform/mcp_servers/` - MCP servers for AI integration (17 servers)
- `shared_platform/utils/` - Platform-wide utilities and helper functions

### Database and Data
- `platform_data/database/dark_data.db` - Main SQLite database
- Database tables: `incidents`, `companies`, `compliance_reports`, `equipment`, `incidents_fts`

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
- **Document Types**: EAF reports (ANEXO 1-8), EAF failure reports, daily operational reports, market data
- **Key Companies**: Enel Chile, Colbún S.A., AES Gener, ENGIE, Statkraft
- **Universal Schema**: JSON-LD structure for AI consumption with cross-references

## Important Notes for Development

### Domain Structure
- Each domain can contain multiple document types in `chapters/` subdirectories
- "chapters" is organizational - documents may or may not have actual chapters
- `shared/` directory within each domain contains reusable utilities for that domain
- Always use universal schema adapters for consistent data transformation

### Document Processing
- Follow the 6-phase methodology in `docs/metodologia/` for all new documents
- Use `extraction_rules_and_validators.json` for quality control
- Interactive validation is required for all extractions
- Claude Code can assist with all phases of document processing

### Processor Development Pattern
When developing new document processors, the typical evolution is:
1. **Initial processor** - Basic extraction with simple patterns
2. **Experimental processors** - Test different approaches (coordinate-based, region-based, hybrid)
3. **Final processor** - Best approach combining successful patterns from experiments
4. Keep experimental processors in codebase for reference and comparison
5. Document the recommended processor clearly in comments/docs

### File Exclusions
- PDFs, databases, and large JSON outputs are gitignored
- Keep only code, documentation, and small configuration files in version control
- Use `.gitkeep` files to preserve empty directory structure

### Known Issues and TODOs
- **Entry Points Mismatch**: `pyproject.toml` defines `dark_data.*` modules but actual structure uses `ai_platform.*` and `shared_platform.*`
  - **Workaround**: Always use `python -m shared_platform.cli.main` instead of entry point commands
  - Domain processors should be run directly: `cd domains/{domain}/chapters/{chapter}/processors && python {processor}.py`
- **Module Naming**: Consider aligning on a single naming convention across the codebase
- **Processor Consolidation**: Multiple experimental processors exist - document which are production-ready vs. experimental

## Important Instruction Reminders

- Do what has been asked; nothing more, nothing less
- NEVER create files unless absolutely necessary for achieving your goal
- ALWAYS prefer editing an existing file to creating a new one
- NEVER proactively create documentation files (*.md) or README files unless explicitly requested

### Working with EAF Documents

When processing EAF documents:
- **Always verify page ranges** using `domains/operaciones/anexos_eaf/shared/chapter_definitions.json`
- **Use recommended processor** (`final_smart_processor.py`) for production work in EAF individual reports
- **Test experimental processors** only when exploring new extraction strategies
- **Interactive validation is mandatory** - run validation before marking extractions complete
- **Check extraction rules** in each chapter's `docs/extraction_rules_and_validators.json`

### Document Processing Best Practices

1. **Before starting a new document type**:
   - Read `docs/metodologia/DATA_FLOW.md` for the 6-phase methodology
   - Check if a similar processor already exists in `domains/`
   - Verify the domain structure exists: `domains/{domain}/chapters/{doc_type}/`

2. **During extraction development**:
   - Start with coordinate-based or region-based approaches for tables
   - Use paragraph-based approaches for narrative text
   - Combine strategies in a hybrid/final processor
   - Keep all experimental processors for comparison and future reference

3. **Quality control**:
   - All extractions must pass interactive validation
   - Document success rates and accuracy metrics
   - Transform to universal schema before database ingestion
   - Test on multiple document samples before production use
