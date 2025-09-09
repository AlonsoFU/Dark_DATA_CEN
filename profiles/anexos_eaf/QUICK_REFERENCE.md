# Quick Reference Card

## Tool Purpose (Clear Answer)

### `show_title_candidates.py`
**Why it exists**: Claude Code can't handle interactive y/n prompts  
**What it does**: Gets all results fast in terminal so Claude can show you  
**When to use**: Always use this first in Claude Code sessions  
**Result**: Claude shows you candidates → you validate → Claude saves approved ones

### `interactive_title_detector.py`  
**Why it exists**: Full validation with step-by-step y/n prompts  
**What it does**: Asks you about each candidate individually  
**When to use**: Terminal environments with interactive input  
**Result**: Automatically saves only the titles you approve

## Essential Prompt for Continuing Work

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

START WITH: Document path [DOCUMENT_PATH]

Please:
1. Use existing patterns from profiles/anexos_eaf/title_detection_patterns.json
2. Run show_title_candidates.py to get all candidates quickly
3. Show me the candidates for validation ("all look good" or specific choices)
4. Save validated titles to profiles and suggest next phase focus

Follow the proven interactive approach with real-time user validation.
```

## Key Points

✅ **Preview tool = Speed for Claude** (no waiting for y/n prompts)  
✅ **Interactive tool = Full validation** (for terminal users)  
✅ **Always start with preview** in Claude Code  
✅ **Include full context** in prompts for best results  
✅ **Patterns work for any number of titles** (not just 10)  

---
*Quick Reference v1.0 - 2025-01-04*