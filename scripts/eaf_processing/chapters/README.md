# EAF Document Chapters - Processing Scripts

**Structure**: Each chapter has its own processing pipeline (content_extraction → validation_quality → final_generation)

## All 10 Chapters from EAF Document

| Chapter | Pages | Content | Status | Scripts |
|---------|-------|---------|---------|---------|
| **anexo_01_generation_programming** | 1-62 | Generation Programming | 🔄 **50% Complete** | ✅ **Has Scripts** |
| **anexo_02_real_generation** | 63-95 | Real Generation Data | ⏳ Pending | 📁 Ready |
| **anexo_03_cdc_reports** | 96-100 | CDC Reports | ⏳ Pending | 📁 Ready |
| **informe_diario_day1** | 101-134 | Daily Report Day 1 | ⏳ Pending | 📁 Ready |
| **informe_diario_day2** | 135-163 | Daily Report Day 2 | ⏳ Pending | 📁 Ready |
| **anexo_04_maintenance** | 164-190 | Maintenance Schedules | ⏳ Pending | 📁 Ready |
| **anexo_05_company_reports** | 191-245 | Company Failure Reports | 🎯 **High Priority** | 📁 Ready |
| **anexo_06_compliance_data** | 246-256 | Company Compliance Data | 🎯 **High Priority** | 📁 Ready |
| **anexo_07_coordinator** | 257 | Coordinator Background | ⏳ Pending | 📁 Ready |
| **anexo_08_edac** | 258 | EDAC Analysis | ⏳ Pending | 📁 Ready |

## Chapter Structure (Each chapter follows same pattern)

```
anexo_XX_name/
├── content_extraction/    # Extract tables/data from this chapter's pages
├── validation_quality/    # Validate extractions for this chapter  
└── final_generation/      # Generate final output for this chapter
```

## Current Focus: ANEXO 01 Only

**ANEXO 01** is the ONLY chapter with actual scripts currently:
- ✅ `content_extraction/extract_anexo1_with_ocr_per_row.py` (Latest - Sep 8)
- ✅ `validation_quality/apply_corrections_with_review_summary.py` (Latest - Sep 8) 
- ✅ `validation_quality/corrected_validation_strategy.py` (Sep 6)
- ✅ `final_generation/generate_final_complete_json.py` (Sep 6)

## Next Development Priority

1. **Complete ANEXO 01** (50% → 100%)
2. **ANEXO 05**: Company Reports (High business value)
3. **ANEXO 06**: Compliance Data (High business value)
4. **Other chapters** as needed

## Quick Access - ANEXO 01 (Current Work)
```bash
cd scripts/eaf_processing/chapters/anexo_01_generation_programming

# Extract content
python content_extraction/extract_anexo1_with_ocr_per_row.py

# Validate results  
python validation_quality/apply_corrections_with_review_summary.py

# Generate final output
python final_generation/generate_final_complete_json.py
```

## Development Pattern for New Chapters

When starting a new chapter (e.g., ANEXO 05):
1. Create scripts in `anexo_05_company_reports/content_extraction/`
2. Develop validation in `anexo_05_company_reports/validation_quality/` 
3. Build final generation in `anexo_05_company_reports/final_generation/`