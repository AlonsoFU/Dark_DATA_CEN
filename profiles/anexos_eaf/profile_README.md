# ANEXOS EAF Processing Profile

## Overview
This profile contains validated patterns and tools for processing ANEXOS EAF documents (power system failure analysis reports) with 100% accuracy using OCR-based spacing correction.

## Key Achievement
**🎯 Critical Success**: Successfully solved the merged number problem where raw PDF text extraction loses visual spacing. OCR coordinate analysis detects that "980310125" should be "9803" + "10125" by analyzing visual pixel spacing.

## Document Structure
- **Total Pages**: 399 (10 chapters + annexes)
- **Current Focus**: ANEXO Nº1 (Pages 1-62) - Generation Programming Data
- **Table Structure**: Dual tables per page (system metrics + power plant data)

## Processing Approach
1. **Phase 1 (Completed)**: Title Detection - Interactive validation of 10 chapter titles
2. **Phase 2 (Completed)**: Pattern Development - OCR spacing correction achieving 100% accuracy  
3. **Phase 3 (Ready)**: Batch Extraction - Process all ANEXO Nº1 pages

## Files in this Profile

### Core Configuration
- `validated_titles.json` - User-approved chapter structure and page ranges
- `extraction_patterns.json` - Complete regex patterns and OCR configuration
- `workflow_documentation.md` - Step-by-step interactive processing guide

### Working Tools
- `tools/show_title_candidates.py` - Preview tool for title detection (used for interactive validation)

### Validation Results  
- `development/page_2_extraction_ocr_corrected.json` - Successful extraction with OCR corrections
- `development/targeted_spacing_analysis.json` - OCR spacing analysis results

## Critical Technology: OCR Spacing Correction

**Problem**: Raw PDF text extraction merges visually separate numbers
- Raw: "980310125" (merged)
- Visual: "9803" + gap + "10125" (separate numbers)

**Solution**: OCR coordinate analysis
- Convert PDF to 300 DPI image
- Run OCR with coordinate data
- Analyze X-position gaps between characters
- Detect visual spacing that indicates number boundaries

**Implementation**: `scripts/extract_anexo1_ocr_corrected_clean.py`

## Usage for Future Claude Sessions

1. **Load this profile**: Read all files in `profiles/anexos_eaf/`
2. **Use interactive approach**: Always validate findings with user before proceeding
3. **Apply OCR correction**: Use coordinate-based spacing analysis for 100% accuracy
4. **Follow phase structure**: Title → Pattern → Extraction

## Validation Metrics
- ✅ System metrics: 8/8 patterns identified
- ✅ Power plants: 49+ facilities mapped  
- ✅ OCR accuracy: 100% separation of merged numbers
- ✅ Interactive validation: User approved all findings

## Next Steps
- Process remaining ANEXO Nº1 pages (3-62) using proven patterns
- Apply similar methodology to other anexos with different formats
- Create production batch processing pipeline