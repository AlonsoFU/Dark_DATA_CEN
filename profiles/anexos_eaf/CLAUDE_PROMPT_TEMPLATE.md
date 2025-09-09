# Claude Prompt Template for Anexos EAF Processing

## How to Continue This Work in Future Sessions

### Prompt Template for Phase 1 (Title Detection) - NEW DOCUMENT

```
I want to start interactive processing of a NEW Anexos EAF document using the established workflow.

DOCUMENT TYPE: Anexos EAF - Power system failure analysis reports with structured sections.

TITLE DETECTION APPROACH (proven method):
1. Title pages contain ONLY the title (minimal content <50 words)
2. Titles start with "ANEXO Nº" or "INFORME DIARIO"
3. Interactive validation required - user approves each candidate
4. Save validated results to profiles/anexos_eaf/

PROCESS:
1. Use existing patterns from profiles/anexos_eaf/title_detection_patterns.json
2. Run: python profiles/anexos_eaf/tools/show_title_candidates.py
3. Show me all candidates for validation
4. I'll respond: "All look good" or "Only candidates X, Y, Z" or "Skip candidate N"
5. Save my approved titles to profiles/anexos_eaf/validated_titles.json

EXPECTED RESULTS: Variable number of titles (not always 10) following same patterns:
- ANEXO Nº1, ANEXO Nº2, etc. (technical annexes)
- INFORME DIARIO (daily operational reports, usually 1-3 days)

START WITH: Document path [DOCUMENT_PATH]

Please begin Phase 1 title detection with interactive validation.
```

### Prompt Template for Phase 2 (Pattern Development)

```
I want to continue interactive processing of an Anexos EAF document. 

I've already completed Phase 1 (title detection) and the results are saved in:
- profiles/anexos_eaf/validated_titles.json
- profiles/anexos_eaf/WORKFLOW.md

The document structure is:
- ANEXO Nº1 (Pages 1-62): Generation Programming
- ANEXO Nº2 (Pages 63-95): Real Generation Data  
- ANEXO Nº3 (Pages 96-100): CDC Reports
- INFORME DIARIO (Pages 101-134): Daily Report Day 1
- INFORME DIARIO (Pages 135-163): Daily Report Day 2
- ANEXO Nº4 (Pages 164-190): Maintenance Schedules
- ANEXO Nº5 (Pages 191-245): Company Failure Reports
- ANEXO Nº6 (Pages 246-256): Company Background
- ANEXO Nº7 (Page 257): Coordinator Background
- ANEXO Nº8 (Page 258): EDAC Analysis

I want to start Phase 2: Interactive pattern development for [SPECIFY CHAPTER].

Please:
1. Read the existing workflow documentation
2. Show me sample pages from the chosen chapter  
3. Start interactive pattern development with real-time validation
4. Save any new patterns to profiles/anexos_eaf/

Document path: data/documents/anexos_EAF/raw/Anexos-EAF-089-2025.pdf
```

### Prompt Template for New Anexos EAF Document

```
I have a new Anexos EAF document to process using the established interactive workflow.

Please use the existing profile at profiles/anexos_eaf/ which contains:
- Proven title detection patterns
- Interactive validation tools  
- Complete workflow documentation

Start with Phase 1: Title detection for this new document:
[DOCUMENT_PATH]

Follow the same interactive approach:
1. Use the existing patterns from profiles/anexos_eaf/title_detection_patterns.json
2. Show me title candidates for validation
3. I'll approve/reject each candidate  
4. Save validated results to profiles/anexos_eaf/

The patterns should work for any Anexos EAF document (title pages with "ANEXO Nº" or "INFORME DIARIO" + minimal content).
```

### Prompt Template with Full Context (Complete Process)

```
I want to do complete interactive document processing for Anexos EAF documents, following the established workflow.

CONTEXT: Anexos EAF documents are power system failure analysis reports with structured sections. Each section starts with a title-only page containing minimal content (<50 words) and specific patterns.

ESTABLISHED WORKFLOW (from profiles/anexos_eaf/):
- Phase 1: Interactive title detection (COMPLETED method proven)
- Phase 2: Pattern development for data extraction  
- Phase 3: Real-time data extraction with validation

TITLE DETECTION RULES (validated approach):
1. Title pages have ONLY the title (minimal content <50 words)
2. Titles start with "ANEXO Nº" or "INFORME DIARIO" 
3. Interactive validation required - user approves each candidate
4. Save validated results to profiles/anexos_eaf/

TOOLS TO USE:
- Use show_title_candidates.py first (gets results quickly for you to analyze)
- I'll validate based on your preview results
- Don't use interactive_title_detector.py (requires terminal input)

EXPECTED DOCUMENT STRUCTURE (typical):
- ANEXO Nº1: Generation programming data
- ANEXO Nº2: Real generation data
- ANEXO Nº3: CDC reports  
- INFORME DIARIO: Daily operational reports (1-3 days)
- ANEXO Nº4+: Various technical annexes
- HIGH VALUE: Company reports, compliance data, failure analysis

START WITH: Document path [DOCUMENT_PATH]

Please:
1. Use existing patterns from profiles/anexos_eaf/title_detection_patterns.json
2. Run show_title_candidates.py to get all candidates quickly
3. Show me the candidates for validation ("all look good" or specific choices)
4. Save validated titles to profiles and suggest next phase focus

Follow the proven interactive approach with real-time user validation.
```

### Prompt Template for Different Document Type

```
I want to create a new document processing profile similar to the successful anexos_eaf profile.

New document type: [DOCUMENT_TYPE]
Document characteristics: [DESCRIBE STRUCTURE]

Please follow the same interactive approach used for anexos_eaf:
1. Create profiles/[new_document_type]/ directory
2. Develop title/chapter detection patterns interactively
3. I'll validate each pattern with real-time feedback
4. Save all patterns and tools to the new profile
5. Create complete workflow documentation

Reference the anexos_eaf profile structure as a template:
- Interactive validation approach
- Pattern persistence  
- Tool organization
- Documentation completeness
```

---

## Key Phrases for Claude to Recognize

### When You Want Interactive Processing
- **"interactive processing"**
- **"real-time validation"**  
- **"I'll validate each [finding/pattern/extraction]"**
- **"show me candidates for approval"**

### When You Want to Use Existing Profile
- **"use the anexos_eaf profile"**
- **"follow the existing workflow"**
- **"load patterns from profiles/anexos_eaf/"**

### When You Want to Continue Previous Work
- **"continue Phase 2"** or **"start Phase 2"**
- **"read the validated titles from profiles/"**
- **"pick up where we left off"**

---

## What Claude Should Always Do

### For Anexos EAF Documents
1. **Check profiles/anexos_eaf/ first** - Don't recreate existing work
2. **Use interactive validation** - Get user approval for everything  
3. **Save to profiles/** - Persist all patterns and results
4. **Follow phase structure** - Title detection → Pattern development → Data extraction

### For Any Document Processing
1. **Ask for user criteria first** - Don't assume patterns
2. **Show examples before validation** - Let user see what you found
3. **Get explicit approval** - "All look good" or specific selections
4. **Save everything** - Tools, patterns, results, documentation

---

## Example Claude Response Pattern

```
I see you want to continue with Anexos EAF processing. Let me:

1. ✅ Read existing profile: profiles/anexos_eaf/validated_titles.json
2. ✅ Load proven patterns and workflow
3. 🎯 [NEXT ACTION BASED ON PHASE]

From the validated titles, I can see we have 10 chapters identified.
Which chapter would you like to start pattern development on?

High-value options:
- ANEXO Nº5 (Pages 191-245): Company failure reports
- ANEXO Nº6 (Pages 246-256): Company background  

Or specify a different chapter for interactive pattern development.
```

---

*Template Version: 1.0*  
*Created: 2025-01-04*  
*Purpose: Ensure consistent continuation of interactive document processing*