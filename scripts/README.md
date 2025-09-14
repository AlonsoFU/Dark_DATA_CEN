# Scripts Directory Structure

All automation scripts for the Dark Data Platform organized by function and workflow.

## 📁 Folder Organization

### **Database & Analysis Tools**
- `database_tools/` - Core data management scripts
  - `ingest_data.py` - Load JSON data into SQLite database
  - `analysis_queries.py` - Business intelligence queries
  - `learn_document_structure.py` - AI-powered document structure learning
  - `search_all_content_types.py` - Content search and discovery

### **Document Processing**
- `document_processing/` - Generic document processing utilities
  - Text extraction, OCR, parsing tools
  - Format conversion utilities

### **EAF Workflows** 
- `eaf_workflows/` - Complete EAF document processing pipeline
  - `eaf_processing/` - Chapter-by-chapter extraction framework
    - `chapters/anexo_01_generation_programming/` - Programming data (50% complete)
    - `chapters/anexo_02_real_generation/` - Real generation data (framework ready)
    - `chapters/anexo_03_cdc_reports/` - CDC reports (planned)
    - `chapters/anexo_04_maintenance/` - Maintenance logs (planned)
    - `chapters/anexo_05_company_reports/` - Company reports (high priority)
    - `chapters/anexo_06_compliance_data/` - Compliance data (high priority)
    - `chapters/anexo_07_coordinator/` - Coordinator reports (planned)
    - `chapters/anexo_08_edac/` - EDAC data (planned)
    - `chapters/informe_diario_day1/` - Daily report day 1 (planned)
    - `chapters/informe_diario_day2/` - Daily report day 2 (planned)
  - `01_title_detection/` - Chapter boundary detection
  - `interactive_commands.sh` - Interactive processing commands

### **System Utilities**
- `system_utils/` - Infrastructure and maintenance
  - `deployment/` - Deployment automation
  - `maintenance/` - System maintenance scripts
  - `session_management/` - Session handling
  - `viewers/` - Data viewing utilities
  - `mcp/` - Model Context Protocol integration

## 🚀 Quick Commands

```bash
# Database operations
python scripts/database_tools/ingest_data.py
python scripts/database_tools/analysis_queries.py

# EAF document processing  
cd scripts/eaf_workflows/eaf_processing/chapters/anexo_01_generation_programming/content_extraction
python extract_anexo1_with_ocr_per_row.py

# Structure learning
python scripts/database_tools/learn_document_structure.py
```

## 🎯 Workflow Status 🚀 **MAJOR PROGRESS**

- **ANEXO 1**: ✅ 95% complete (59/62 pages extracted) - **NEARLY COMPLETE**
- **ANEXO 2**: ✅ **PRODUCTION READY** (185+ solar plants, 90%+ success rate) - **COMPLETED**
- **ANEXO 5-6**: 🎯 **NEXT PRIORITY** - High business value targets
- **Database**: ✅ Ready for renewable energy intelligence ingestion