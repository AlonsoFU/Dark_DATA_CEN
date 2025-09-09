# Anexos EAF Document Processing Profile

## Overview
This profile handles the extraction and processing of **Anexos EAF** (Anexos de Eventos de Alteración del Funcionamiento) - supplementary documents that accompany Chilean power system failure reports.

**Document Characteristics:**
- **Size:** 50-400 pages per document
- **Language:** Spanish (Chilean electrical sector terminology)
- **Content:** Mixed format with multiple chapter types
- **Critical Data:** Company compliance, technical specifications, chronological events

---

## Document Structure Pattern

### Typical Chapter Sequence:
1. **Title Page & Index** (Pages 1-5)
2. **Executive Summary** (Pages 6-15) - Narrative format
3. **Chronology of Events** (Pages 16-50) - Timeline format  
4. **Technical Specifications** (Pages 51-120) - Tables and technical data
5. **Company Reports** (Pages 121-180) - Structured company information
6. **Equipment Analysis** (Pages 181-250) - Technical equipment details
7. **Compliance Status** (Pages 251-300) - Regulatory compliance data
8. **Conclusions & Recommendations** (Pages 301-350) - Narrative format
9. **Appendices** (Pages 351+) - Mixed supporting documents

### Format Change Detection Points:
- **Page ~16:** Narrative → Timeline format
- **Page ~51:** Timeline → Technical tables
- **Page ~121:** Technical → Company listings
- **Page ~181:** Company data → Equipment specifications
- **Page ~251:** Equipment → Compliance tables
- **Page ~301:** Tables → Narrative conclusions

---

## Extraction Logic Philosophy

### 1. **Adaptive Chapter Recognition**
- **Don't assume page numbers** - chapters vary by document length
- **Use content patterns** to detect chapter boundaries
- **Multiple validation signals** - headers + content + formatting

### 2. **Progressive Quality Validation**
- **Chapter-by-chapter processing** - fail fast, adjust patterns
- **Quality thresholds per chapter** - different expectations for different content types
- **Human-in-the-loop validation** - flag uncertain extractions

### 3. **Robust Error Handling**
- **Format variations** - same content type, different formatting
- **OCR failures** - fallback extraction methods
- **Missing sections** - detect gaps, mark as incomplete

---

## Critical Extraction Targets

### High Priority (Must Extract):
1. **Company Information:**
   - Company names (ENEL, COLBÚN, AES, etc.)
   - Legal representatives
   - RUT numbers
   - Compliance status

2. **Technical Specifications:**
   - Power ratings (MW, MVA)
   - Voltage levels (kV)
   - Equipment models (Siemens 7SL87, etc.)
   - Failure causes and times

3. **Regulatory Compliance:**
   - Report submission dates
   - Compliance percentages
   - Non-compliance reasons

### Medium Priority (Good to Have):
1. **Timeline Data:**
   - Event sequences
   - Response times
   - Recovery procedures

2. **Equipment Details:**
   - Manufacturer information
   - Age at failure
   - Maintenance history

### Low Priority (Nice to Have):
1. **Appendix Content:**
   - Supporting calculations
   - Additional documentation
   - Reference materials

---

## Quality Validation Strategy

### Chapter-Level Quality Metrics:
- **Executive Summary:** 90%+ text extraction, key entities identified
- **Technical Specs:** 95%+ numerical values, 90%+ equipment names
- **Company Reports:** 100% company names, 95%+ RUT numbers
- **Compliance Data:** 100% status indicators, 95%+ dates

### Validation Checkpoints:
1. **Per Chapter:** Immediate feedback on extraction quality
2. **Cross-Chapter:** Consistency checks (same company info across chapters)
3. **Document-Level:** Completeness assessment (all expected chapters present)

---

## Processing Workflow

### Development Phase:
1. **Single Document Analysis:**
   ```bash
   make learn-structure --documents "anexos_EAF_sample.json" --profile anexos_EAF
   ```

2. **Chapter-by-Chapter Refinement:**
   ```bash
   make test-chapter --chapter "technical_specs" --profile anexos_EAF
   ```

3. **Pattern Validation:**
   ```bash
   make validate-patterns --documents "anexos_EAF_batch/*.json" --profile anexos_EAF
   ```

### Production Phase:
```bash
make process-production --documents "incoming/*.pdf" --profile anexos_EAF --quality-threshold 90
```

---

## Known Challenges & Solutions

### Challenge 1: Format Variations
**Problem:** Same chapter type with different table layouts
**Solution:** Multiple pattern templates per chapter type, confidence scoring

### Challenge 2: OCR Quality Issues  
**Problem:** Scanned pages with poor text extraction
**Solution:** Multi-stage extraction (pdfplumber → pymupdf → OCR fallback)

### Challenge 3: Chapter Boundary Detection
**Problem:** No clear page breaks between chapters
**Solution:** Content-based transition detection, pattern analysis

### Challenge 4: Company Name Variations
**Problem:** "ENEL GENERACIÓN CHILE S.A." vs "Enel Generación" vs "ENEL CHILE"
**Solution:** Fuzzy matching with canonical company registry

---

## Success Metrics

### Target Quality Thresholds:
- **Overall Extraction:** 92%+ accuracy
- **Critical Data:** 98%+ accuracy (company names, technical specs)
- **Processing Speed:** <5 minutes per 300-page document
- **Format Change Detection:** 95%+ accuracy

### Monitoring Indicators:
- **False Positives:** <3% incorrect extractions
- **False Negatives:** <5% missed critical information
- **Processing Failures:** <1% complete extraction failures

---

## Future Enhancements

1. **Machine Learning Integration:**
   - Pattern learning from successful extractions
   - Automatic format adaptation
   - Predictive quality scoring

2. **Multi-Language Support:**
   - English technical documentation
   - Portuguese regulatory reports

3. **Real-Time Processing:**
   - Stream processing for live document feeds
   - Immediate quality alerts
   - Auto-correction suggestions

---

## Development History

- **v1.0** - Initial profile creation for EAF-089/2025 documents
- **v1.1** - Enhanced technical specification extraction
- **v1.2** - Improved chapter boundary detection
- **v2.0** - Production-ready with quality monitoring

---

*Last Updated: September 2025*  
*Profile Owner: Dark Data Platform Team*