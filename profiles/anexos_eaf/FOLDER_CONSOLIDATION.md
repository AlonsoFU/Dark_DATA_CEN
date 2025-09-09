# Profile Folder Consolidation

## Issue Found
There were TWO anexos profile folders:
- `/profiles/anexos_eaf/` (current - interactive approach)  
- `/data/profiles/anexos_EAF/` (old - different approach)

## Resolution
- **ACTIVE PROFILE**: `/profiles/anexos_eaf/` 
- **LEGACY FILES**: Moved old files to `/profiles/anexos_eaf/legacy_files/`

## Current Active Profile Structure
```
profiles/anexos_eaf/
├── INTERACTIVE_PROCESS.md       # ⭐ NEW: Clear interactive approach
├── QUICK_REFERENCE.md           # Essential prompts & tool clarity
├── CLAUDE_PROMPT_TEMPLATE.md    # Full context prompts
├── TOOL_REFERENCE.md            # Tool purposes & usage
├── STEP_BY_STEP_GUIDE.md        # Anyone can follow
├── WORKFLOW.md                  # Complete workflow
├── README.md                    # Profile overview
├── validated_titles.json       # YOUR approved 10 titles
├── title_detection_patterns.json # Reusable patterns
├── tools/                       # Analysis tools
│   ├── show_title_candidates.py
│   └── interactive_title_detector.py
└── legacy_files/               # OLD files from data/profiles/
    ├── chapter_definitions.json
    ├── development_workflow.md
    ├── extraction_patterns.json
    ├── processing_config.yaml
    ├── README.md
    └── validation_rules.json
```

## Key Differences

### Current Profile (Interactive Approach)
- ✅ **Real-time user validation** at every step
- ✅ **Phase-based workflow** (Title → Patterns → Extraction)  
- ✅ **Proven results** (100% title detection accuracy)
- ✅ **Complete documentation** for future sessions

### Legacy Files (Old Approach)
- ❓ **Different methodology** (stored in legacy_files/)
- ❓ **May have useful patterns** for reference
- ❓ **Not validated** with interactive approach

## Recommendation
**Use current profile** (`/profiles/anexos_eaf/`) which has:
- Proven interactive methodology  
- Complete workflow documentation
- User-validated results
- Tools that work in Claude Code environment

Legacy files available for reference if needed.

---
*Consolidation completed: 2025-01-04*