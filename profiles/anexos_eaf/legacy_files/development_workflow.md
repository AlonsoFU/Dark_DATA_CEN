# Anexos EAF Development Workflow

## Quick Start Commands

```bash
# 1. Load this profile for development
make load-profile --name anexos_EAF

# 2. Start with a single document
make learn-structure --document "data/raw/anexo_sample.json" --profile anexos_EAF --interactive

# 3. Review results in dashboard
make run-web
# Navigate to: http://localhost:5000/processing-status/anexos_EAF
```

## Development Phases

### Phase 1: Single Document Mastery
**Goal:** Perfect extraction on one representative document

```bash
# Place your sample document
cp anexo_sample.pdf data/raw/anexos_EAF/

# Start interactive learning
make learn-discovery --profile anexos_EAF --document "anexo_sample.pdf" --interactive-mode

# Check results
python -c "
import json
with open('data/profiles/anexos_EAF/development_log.json') as f:
    log = json.load(f)
    print(f'Chapters detected: {len(log[\"chapters\"])}')
    for ch in log['chapters']:
        print(f'  {ch[\"name\"]}: {ch[\"confidence\"]:.2f} confidence')
"
```

**Live Review Process:**
1. **You run:** `make learn-discovery`
2. **You report:** "8 chapters detected. Technical specs 94% confidence, but company chapter only 67%"
3. **I adjust:** Patterns for company detection
4. **You test:** `make test-chapter --chapter company_reports`
5. **Repeat** until all chapters >90% confidence

### Phase 2: Chapter-by-Chapter Refinement
**Goal:** Achieve >90% quality on each chapter type

```bash
# Test individual chapters
for chapter in title_page executive_summary chronology technical_specifications company_reports equipment_analysis compliance_status conclusions; do
  echo "Testing $chapter..."
  make test-chapter --chapter $chapter --profile anexos_EAF --document "anexo_sample.pdf"
done
```

**Quality Checkpoints:**
- **Title Page:** Document ID extracted? Date correct? 
- **Executive Summary:** Company names found? Power values extracted?
- **Chronology:** Timeline events in order? Timestamps correct?
- **Technical Specs:** All MW/kV values? Equipment models identified?
- **Company Reports:** All company names? RUT numbers valid?
- **Equipment Analysis:** Failure causes identified? Equipment ages extracted?
- **Compliance:** Percentages correct? Status classifications accurate?
- **Conclusions:** Recommendations extracted? Action items identified?

### Phase 3: Multi-Document Validation
**Goal:** Validate patterns work across different Anexos EAF documents

```bash
# Test on multiple documents
make validate-patterns --documents "data/raw/anexos_EAF/*.pdf" --profile anexos_EAF --batch-size 3

# Generate comparison report
make generate-validation-report --profile anexos_EAF
```

**What to Look For:**
- **Consistent Quality:** All documents >85% overall quality
- **Pattern Robustness:** Same chapter types detected across documents
- **Entity Consistency:** Company names standardized across documents
- **Format Adaptability:** Handles format variations gracefully

### Phase 4: Production Readiness
**Goal:** Automated processing with quality monitoring

```bash
# Final validation suite
make production-validation --profile anexos_EAF --documents "data/test/anexos_EAF/*.pdf"

# Deploy to production profile
make deploy-profile --name anexos_EAF --version 1.0 --to production/
```

## Live Collaboration Workflow

### Development Commands for You:
```bash
# Quick quality check
make quality-check --profile anexos_EAF --document "current_test.pdf"

# Chapter-specific testing
make test-chapter --chapter technical_specifications --profile anexos_EAF

# Pattern effectiveness analysis
make pattern-analysis --profile anexos_EAF --show-failures

# Processing time benchmark
make benchmark-processing --profile anexos_EAF --documents "data/raw/anexos_EAF/*.pdf"
```

### What to Report to Me:

#### ✅ Good Progress Reports:
```
"Chapter detection working well:
- Title page: 98% confidence ✅
- Executive summary: 94% confidence ✅  
- Technical specs: 91% confidence ✅
- Company reports: 89% confidence ⚠️ (close)
- Chronology: 87% confidence ⚠️ (needs work)
Ready for next batch testing."
```

#### ⚠️ Issues to Flag:
```
"Problems found in technical_specifications chapter:
- MW values: found 12/18 expected (67% success)
- Equipment models: Siemens detected but ABB missed
- Voltage levels: 220kV and 500kV found, but 66kV missing
- Page 45-67 seem to have different table format

Need pattern adjustment for ABB equipment and 66kV detection."
```

#### ❌ Major Issues:
```
"Chapter 4 (company_reports) extraction completely failed:
- Text extraction: 23% (very poor)
- Company names: 0/8 found
- Appears to be scanned images instead of text
- Pages 89-134 need OCR processing

Recommend switching to OCR method for this section."
```

## Quality Monitoring Dashboard

### Real-Time Processing View:
```bash
# Start monitoring dashboard
make run-monitoring --profile anexos_EAF

# View at: http://localhost:5000/monitor/anexos_EAF
# Shows:
# 📄 Current Document: Processing anexo_034.pdf
# 📊 Progress: Chapter 5/8 (Equipment Analysis)
# ⏱️ Time: 3m 45s elapsed, ~2m remaining  
# 📈 Quality: 92% average (above threshold)
# ⚠️ Issues: 2 warnings (minor table format variations)
```

### Quality Report Analysis:
```bash
# Generate detailed report
make quality-report --profile anexos_EAF --timeframe "last_24h"

# Output example:
# 📊 Anexos EAF Quality Report (Last 24 Hours)
# 
# Documents Processed: 12
# Average Quality: 91.3%
# Success Rate: 94.7% (11/12 successful)
# 
# Chapter Performance:
#   Title Page: 98.2% avg quality ✅
#   Executive Summary: 93.1% avg quality ✅  
#   Technical Specs: 89.7% avg quality ⚠️
#   Company Reports: 95.4% avg quality ✅
#   Chronology: 85.3% avg quality ⚠️ (below 90% target)
#
# Top Issues:
#   1. Chronology timestamp extraction: 3 documents affected
#   2. Technical specs table format variation: 2 documents  
#   3. OCR quality on pages 200+: 1 document
```

## Troubleshooting Guide

### Common Issues & Solutions:

#### Issue: "Chapter detection confidence <80%"
```bash
# Debug chapter detection
make debug-chapters --document "problem_doc.pdf" --profile anexos_EAF --verbose

# Check what patterns are failing
make pattern-debug --chapter "failing_chapter" --profile anexos_EAF
```

#### Issue: "Entity extraction missing key data" 
```bash
# Test entity patterns individually  
make test-entities --entity-type "company_names" --profile anexos_EAF --document "test.pdf"

# View extraction details
make extraction-debug --chapter "company_reports" --show-patterns
```

#### Issue: "Processing too slow"
```bash
# Profile performance
make performance-profile --document "large_doc.pdf" --profile anexos_EAF

# Optimize settings
make optimize-config --profile anexos_EAF --target-time "5min"
```

## Success Metrics & Targets

### Development Targets:
- **Chapter Detection:** >90% confidence for critical chapters
- **Entity Extraction:** >95% for companies, >90% for technical specs  
- **Processing Speed:** <5 minutes per 300-page document
- **Quality Consistency:** <10% variance between similar documents

### Production Targets:
- **Overall Success Rate:** >95% of documents processed successfully
- **Critical Data Accuracy:** >98% for regulatory compliance data
- **Processing Throughput:** 10+ documents per hour
- **Manual Review Rate:** <5% of documents require manual review

## Deployment Checklist

Before moving to production:

- [ ] Single document processing: >95% quality
- [ ] Multi-document consistency: <5% quality variance  
- [ ] All critical chapters: >90% confidence
- [ ] Entity extraction: Company names 100%, technical specs >95%
- [ ] Performance: <5 min per 300-page document
- [ ] Error handling: Graceful failure recovery tested
- [ ] Validation rules: All thresholds properly calibrated
- [ ] Monitoring: Quality dashboard operational
- [ ] Documentation: Processing patterns documented
- [ ] Rollback plan: Previous version available if needed

## Next Steps After Production

1. **Monitor production quality** for first week
2. **Collect feedback** on extraction accuracy
3. **Fine-tune patterns** based on production data
4. **Expand to new document types** using learned patterns
5. **Implement machine learning** for automatic pattern improvement

---

*This workflow ensures systematic development, thorough testing, and reliable production deployment of the Anexos EAF processing profile.*