# Step-by-Step Guide: Anexos EAF Interactive Processing

## For Anyone (Including Future Claude Sessions)

### Document Type: Anexos EAF
**What it is**: Power system failure analysis reports with structured annexes  
**Key characteristic**: Each section starts with a title-only page

---

## Step 1: Title Detection

### What You're Looking For
- **Title pages** that contain ONLY the title (minimal content)
- **Title format**: Starts with "ANEXO Nº" or "INFORME DIARIO"
- **Example**: "ANEXO Nº1" with subtitle on same page, total < 50 words

### How to Run
```bash
# Option A: Preview candidates first (recommended)
python profiles/anexos_eaf/tools/show_title_candidates.py

# Option B: Full interactive validation (if input available)
python profiles/anexos_eaf/tools/interactive_title_detector.py [document_path]
```

### What Each Tool Does

#### `show_title_candidates.py`
- **Purpose**: Shows all potential titles WITHOUT interaction
- **Output**: List of candidates with page numbers and content
- **Use when**: You want to see what would be found before validating
- **Example output**:
  ```
  📖 CANDIDATE 1:
     📄 Page: 1
     🏷️  Title: 'ANEXO Nº1'
     📊 Words: 17
     📝 Content: ANEXO Nº1 - Detalle de la generación...
  ```

#### `interactive_title_detector.py`
- **Purpose**: Full interactive validation with y/n prompts for each candidate
- **Use when**: You have interactive input capability
- **Process**: Shows each candidate → you approve/reject → saves validated titles
- **Note**: Requires terminal input (y/n responses)

### Expected Results
- **Variable number of titles** (this document had 10, others may have different counts)
- **Similar format pattern**: ANEXO Nº1, ANEXO Nº2, etc. + INFORME DIARIO entries
- **Title pages have < 50 words** (just title + brief description)

---

## Step 2: Validation Process

### Decision Making
For each candidate, ask:
1. **Is this just a title?** (not content pages)
2. **Does it start correctly?** ("ANEXO Nº" or "INFORME DIARIO")  
3. **Is content minimal?** (< 50 words total)

### Validation Responses
- **"All look good"** → Accept all candidates
- **"Only candidates 1, 3, 5"** → Accept specific ones
- **"Skip candidate 2"** → Accept all except specified

---

## Step 3: Results & Next Steps

### What Gets Saved
- `validated_titles.json` → Your approved titles + chapter structure
- `title_detection_patterns.json` → Reusable patterns for future docs
- Chapter page ranges calculated automatically

### Typical Chapter Structure Found
```
ANEXO Nº1: Generation data
ANEXO Nº2: Real generation data  
ANEXO Nº3: CDC reports
INFORME DIARIO: Daily operational reports (usually 2 days)
ANEXO Nº4+: Various technical annexes
```

### High-Value Chapters for Data Extraction
- **ANEXO Nº5**: Usually company failure reports
- **ANEXO Nº6**: Usually company background/compliance
- **INFORME DIARIO**: Operational timelines with timestamps

---

## Common Variations

### Different Document Sizes
- **Not always 10 titles** - could be 5, 8, 15, etc.
- **Pattern stays same**: ANEXO Nº + number sequence
- **INFORME DIARIO**: Usually 1-3 daily reports

### Title Variations Seen
- "ANEXO Nº1" vs "ANEXO N°1" vs "ANEXO No1" (all detected)
- "INFORME DIARIO" always consistent format
- Subtitles vary but pattern detection handles this

---

## Troubleshooting

### If No Titles Found
- Check document type (might not be Anexos EAF)
- Try manual page inspection: `python scripts/debug_document_content.py [doc] --pages 1-10`

### If Too Many False Positives
- Adjust word count threshold in patterns
- Review title detection rules

### If Interactive Tool Fails
- Use preview tool first: `show_title_candidates.py`
- Manually validate based on preview results

---

## Success Criteria

### Phase 1 Complete When
- ✅ All title pages identified
- ✅ User validated each title (or batch approved)
- ✅ Chapter structure saved to profile
- ✅ Ready for Phase 2 (pattern development)

### Quality Check
- **Accuracy**: All detected titles should be actual title pages
- **Completeness**: No title pages missed
- **Structure**: Clear chapter boundaries identified

---

*Guide Version: 1.0*  
*Last Updated: 2025-01-04*  
*Tested On: Anexos-EAF-089-2025.pdf (258 pages, 10 titles found)*