# 🌑 Dark Data Platform
## Enterprise Document Intelligence Extraction System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![SQLite](https://img.shields.io/badge/database-SQLite-green.svg)](https://www.sqlite.org/)
[![MCP Compatible](https://img.shields.io/badge/AI-MCP%20Compatible-purple.svg)](https://model-context-protocol.ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Transform buried enterprise PDF documents into AI-queryable structured intelligence with validated accuracy.

---

## 🎯 Project Overview

**The Challenge**: 80% of critical business intelligence is trapped in unstructured documents - PDFs, reports, compliance files, and technical documents that contain vital insights but remain invisible to decision-makers.

**Our Solution**: Enterprise-grade platform that systematically discovers, extracts, and transforms document intelligence into AI-queryable structured data with user-validated accuracy.

### 🔬 **Current Proof of Concept: Power System Intelligence**
- 📊 **Document**: 399-page power system failure analysis reports (Anexos EAF)
- 🎯 **Status**: Phase 1 Complete (10 chapters identified), Phase 2 In Progress (50% - ANEXO 1)
- 📈 **Results**: 100% accurate chapter detection, structured table extraction from generation programming data

---

## 🚀 Quick Start

```bash
# 1. Clone repository
git clone https://github.com/your-username/dark-data-platform.git
cd dark-data-platform

# 2. Install dependencies
make install-dev          # Development setup with pre-commit hooks

# 3. Setup database
make setup-db
make ingest-data

# 4. Launch applications
make run-web              # Web dashboard → http://localhost:5000
make run-cli              # Command-line interface
make run-mcp              # MCP server for AI integration
```

**Time to Intelligence**: < 5 minutes from zero to AI-queryable insights

---

## 📂 Architecture Overview

### **Enterprise Design**
```
📄 ANY DOCUMENT → Adaptive Processing → Unified Database → MCP API → 🤖 AI Access
    ↓                    ↓                  ↓           ↓
  PDFs, Legacy         Structure          SQLite+     Claude/
  Reports, Data        Learning           JSON+FTS    GPT-4
```

### **Processing Pipeline**
```
dark_data/                   # Main Python package
├── core/                    # AI interfaces & business logic
├── database/                # SQLite + JSON storage layer
├── processors/              # Adaptive document processing
├── analyzers/              # Pattern detection & learning
├── mcp/                    # Model Context Protocol integration
├── web/                    # Flask dashboard
└── cli/                    # Command-line tools

scripts/eaf_processing/      # Document-specific processing
├── 01_title_detection/      # Chapter/section identification
├── chapters/               # Chapter-specific extraction
│   └── anexo_01_generation_programming/  # Current focus (50%)
└── 03_validation_quality/   # Quality control & validation
```

---

## 📊 Current Development Status

### **🎯 Active Work: ANEXO 1 - Generation Programming (50% Complete)**

| Component | Status | Description |
|-----------|---------|-------------|
| **Title Detection** | ✅ **100% Complete** | 10 chapters identified with perfect accuracy |
| **Content Extraction** | 🔄 **50% In Progress** | ANEXO 1 table extraction (Pages 1-62) |
| **Validation System** | ✅ **Ready** | User-validated extraction pipeline |
| **Output Generation** | ✅ **Ready** | Structured JSON with metadata |

### **📈 Processing Results (ANEXO 1)**
- ✅ **Pages 1-30**: Basic table extraction operational
- 🔄 **Pages 31-62**: OCR refinement and validation in progress
- 📊 **Data Points**: 16+ extraction points per page (power plants, capacities, schedules)
- 🎯 **Next Priority**: ANEXO 5 (Company Reports) & ANEXO 6 (Compliance Data)

---

## 🛠️ Key Features

### **🧠 Interactive Intelligence**
- **User-Validated Extractions**: No AI hallucinations - all data approved by users
- **Adaptive Pattern Learning**: Self-improving extraction based on document structure
- **Phase-Based Processing**: Title Detection → Content Extraction → Validation → Output

### **🏗️ Enterprise Architecture**
- **Universal Document Processing**: Handle any document type or structure
- **Unified Database**: Single queryable repository for all extracted intelligence
- **AI-Native Integration**: Built-in MCP protocol for seamless AI access
- **Modular Design**: Each document type gets dedicated processing profiles

### **🔍 Quality Assurance**
- **Interactive Validation**: User approves all extractions before saving
- **Cross-Reference Validation**: Multiple extraction methods for accuracy
- **Pattern Consistency**: Reusable patterns across similar documents
- **Audit Trail**: Complete processing history and quality metrics

---

## 🚀 Development Workflow

### **Essential Commands**
```bash
# Testing
make test              # Full test suite with coverage
make test-quick        # Unit tests only

# Code Quality
make lint              # Check code quality (flake8, mypy, black, isort)
make format            # Auto-format code

# Document Processing (Current: ANEXO 1)
cd scripts/eaf_processing/chapters/anexo_01_generation_programming

# Extract generation programming tables
python content_extraction/extract_anexo1_with_ocr_per_row.py

# Validate extractions
python validation_quality/apply_corrections_with_review_summary.py

# Generate final output
python final_generation/generate_final_complete_json.py
```

### **Document Processing Pipeline**
1. **Title Detection**: Identify document structure and chapter boundaries
2. **Content Extraction**: Extract tables, data, and structured information
3. **Validation**: User-validated quality control and error correction
4. **Final Generation**: Produce structured JSON output with metadata

---

## 🤖 AI Integration

### **MCP (Model Context Protocol) Ready**
```bash
make run-mcp              # Start MCP server
```

**Available MCP Servers:**
- **Standard MCP**: Core database analysis tools
- **Enhanced MCP**: Extended system integration
- **Claude Bridge**: Direct Claude API integration

**MCP Resources:**
- `database://dark_data/schema` - Live database schema
- `database://dark_data/stats` - Real-time statistics

---

## 📈 Business Value Demonstration

### **Power System Analysis Results**
- **Incident Analysis**: Complete failure analysis from 399-page reports
- **Generation Intelligence**: Structured power plant capacity and scheduling data
- **Compliance Monitoring**: Automated regulatory compliance tracking
- **Pattern Detection**: Systematic identification of failure patterns and risk factors

### **Extraction Accuracy**
- **Title Detection**: 100% accuracy (10/10 chapters correctly identified)
- **Content Extraction**: High-confidence structured data extraction
- **Validation Rate**: User-approved accuracy ensuring zero hallucinations

---

## 🔧 Technology Stack

**Backend:**
- Python 3.11+ with modern typing
- SQLite with JSON fields + FTS5 search
- Flask web framework
- MCP SDK for AI integration

**Development:**
- pytest for testing with coverage
- black, isort for code formatting
- flake8, mypy for quality control
- pre-commit hooks for consistency

**Document Processing:**
- PyPDF2, PyMuPDF for PDF extraction
- pytesseract for OCR processing
- OpenCV for image processing
- Adaptive pattern recognition

---

## 🎯 Roadmap

### **Phase 2: Content Extraction (Current - 50%)**
- Complete ANEXO 1 generation programming extraction (Pages 31-62)
- Validate all power plant data and programming schedules
- Generate complete structured output for ANEXO 1

### **Phase 3: High-Value Sections (Next)**
- **ANEXO 5**: Company failure reports extraction
- **ANEXO 6**: Compliance data extraction and risk analysis
- Cross-reference validation between sections

### **Phase 4: Enterprise Scaling (Future)**
- Multi-document batch processing
- Automated pattern learning across document families
- Advanced AI integration with semantic search
- Real-time processing pipeline

---

## 📋 Requirements

- **Python 3.11+** (required for modern typing features)
- **SQLite 3.35+** (JSON support and FTS5)
- **4GB RAM** (recommended for large document processing)
- **Dependencies**: See `requirements/` for complete list

---

## 🤝 Contributing

### **Getting Started**
```bash
git clone https://github.com/your-username/dark-data-platform.git
cd dark-data-platform
make install-dev       # Installs pre-commit hooks and development dependencies
```

### **Development Standards**
- Type hints required for all functions
- 100% test coverage for new features
- Interactive validation for data extraction
- Black/isort formatting enforced

### **Current Contribution Opportunities**
- Complete ANEXO 1 extraction (Pages 31-62)
- Develop ANEXO 5 & 6 extraction patterns
- Enhance validation algorithms
- Improve OCR accuracy for power plant names

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🆘 Support & Documentation

- **Documentation**: Check `CLAUDE.md` for development guidance
- **Interactive CLI**: Use `dark-data` command for guided exploration  
- **Issues**: Report bugs or request features via GitHub Issues

---

**🌑 Dark Data Platform** - *Transforming buried intelligence into actionable insights*

> Made with ❤️ for enterprise document intelligence