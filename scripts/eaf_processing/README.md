# EAF Processing Scripts

This directory contains all scripts related to processing Anexos EAF (Power System Failure Reports).

## Processing Pipeline Overview

```
📄 PDF Input → 01_title_detection → 02_content_extraction → 03_validation_quality → 04_final_generation → ✅ Structured Output
                     ↓                        ↓                      ↓                       ↓
                Title Detection         Content Extraction      Quality Control        Final JSON/Data
                Chapter Mapping         OCR Processing          Validation             Complete Results
                Structure Learning      Table Extraction        Error Correction       Batch Processing
```

## Folder Structure

### **01_title_detection/** - Phase 1: Document Structure
Scripts for identifying chapter titles and document boundaries (✅ **COMPLETED** - 10 titles identified with 100% accuracy).

### **02_content_extraction/** - Phase 2: Content Processing  
Scripts for extracting actual content from identified chapters (🔄 **IN PROGRESS**).

### **03_validation_quality/** - Quality Control
Scripts for validating extractions, correcting errors, and ensuring data quality.

### **04_final_generation/** - Output Generation
Scripts for generating final structured outputs and complete JSON files.

### **05_analysis_tools/** - Analysis & Batch Processing
Scripts for analyzing patterns and batch processing multiple documents.

### **06_development_debug/** - Development Tools
Debugging tools and development utilities.

## Current Status

- **Phase 1** ✅ Complete: Document structure mapping (10 chapters identified)
- **Phase 2** 🔄 In Progress: Content extraction from high-value sections
- **Phase 3** 📋 Planned: Automated batch processing with validation

## Quick Start

```bash
# Phase 1: Title detection (if needed for new documents)
python 01_title_detection/interactive_title_detector.py [document.pdf]

# Phase 2: Content extraction (current focus)
python 02_content_extraction/extract_anexo1_with_ocr_per_row.py

# Quality validation
python 03_validation_quality/apply_corrections_with_review_summary.py

# Generate final output
python 04_final_generation/generate_final_complete_json.py
```

## Latest/Recommended Scripts

1. **extract_anexo1_with_ocr_per_row.py** - Latest extraction method
2. **apply_corrections_with_review_summary.py** - Current validation approach
3. **generate_final_complete_json.py** - Final output generation
4. **interactive_title_detector.py** - Title detection (for new documents)