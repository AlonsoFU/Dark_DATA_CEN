# Data Directory Structure

This folder contains all data for the Dark Data Platform **organized by data source**.

## 📁 Data Source Organization

### **documents/** - Organized by Document Type
- `anexos_EAF/` - **Chilean Power System Failure Reports** (main focus)
  - `source_documents/` - Original 399-page PDF documents
  - `samples_and_tests/` - Reduced test versions
  - `extractions/` - JSON extraction results (ANEXO 1-8 + daily reports)
  - `documentation/` - Processing guides and patterns
- `power_system_reports/` - General power system documents
- `financial/` - Financial audit reports, statements, tax filings
- `legal/` - Case studies, contracts, regulations  
- `power_systems/` - Compliance reports, failure reports, maintenance logs

### **System Data**
- `databases/` - SQLite database files
- `processed/` - Cleaned data ready for database ingestion
- `profiles/` - Document processing profiles and patterns
- `knowledge_graphs/` - Graph data structures and schemas
- `training_data/` - ML training datasets and models
- `raw/` - Raw JSON data from external sources
- `cache/` - Temporary processing cache
- `.claude/` - Claude Code session data

## 🔄 Data Flow (by Source)

```
documents/anexos_EAF/source_documents/*.pdf 
    ↓ (EAF extraction scripts)
documents/anexos_EAF/extractions/*.json 
    ↓ (processing scripts)  
processed/anexos_EAF/*.json
    ↓ (ingest scripts)
databases/dark_data.db
```

## 📊 Current Status

### **ANEXOS EAF** (Primary Data Source) 🚀 **MAJOR PROGRESS**
- **Source**: 2 complete PDF documents (399 pages + daily reports)
- **Extraction**: ANEXO 1 (59 files, 95% complete) + ANEXO 2 (185+ plants, 90%+ success) ✅
- **Framework**: 10 chapter processing scripts (2 production-ready)
- **Business Intelligence**: Premium renewable energy data (730+ MWh solar plants)
- **Priority**: ANEXO 5 (Company Reports) & 6 (Compliance) next

### **Other Data Sources**
- **Financial/Legal**: Framework prepared, awaiting documents
- **Power Systems**: Compliance and maintenance structures ready