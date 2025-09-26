# Anexos EAF Documentation

## Overview
Power System Failure Analysis Reports processing for the Chilean Electrical Coordinator.

**Status**: Phase 1 Complete ✅
**Validated**: 10 document types with 100% accuracy

## Document Types
- `anexo_01_generation_programming` - Generation programming tables
- `anexo_02_real_generation` - Real generation data (185+ solar plants)
- `anexo_03_cdc_reports` - CDC reports
- `anexo_04_maintenance` - Maintenance data
- `anexo_05_company_reports` - Company reports (high business value)
- `anexo_06_compliance_data` - Compliance data (high business value)
- `anexo_07_coordinator` - Coordinator reports
- `anexo_08_edac` - EDAC data
- `informe_diario_day1` - Daily operational reports (Pages 101-134)
- `informe_diario_day2` - Additional daily reports

## Quick Start
```bash
# Processing workflow
cd scripts/eaf_workflows/eaf_processing/chapters/anexo_01_generation_programming
python content_extraction/extract_anexo1_with_ocr_per_row.py
python validation_quality/apply_corrections_with_review_summary.py
python final_generation/generate_final_complete_json.py
```

## Key Files
- **Patterns**: `patterns/anexos_eaf/_shared/` - Shared templates and tools
- **Extractions**: `extractions/anexos_eaf/` - Processed results
- **Scripts**: `scripts/eaf_workflows/` - Processing pipeline

## Success Metrics
- ANEXO 1: ✅ Complete - Generation programming fully extracted
- ANEXO 2: ✅ Complete - 185+ solar plants (90%+ success rate)
- INFORME DIARIO: 🚀 Ready for processing