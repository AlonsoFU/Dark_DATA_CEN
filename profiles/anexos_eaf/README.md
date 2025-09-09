# Anexos EAF Profile

## Profile Summary
**Document Type**: Anexos EAF - Power System Failure Analysis Reports  
**Status**: Phase 1 Complete ✅  
**Validated**: 10 title pages with 100% user approval  

## Profile Contents

### Core Configuration
- `validated_titles.json` - User-approved title structure (10 titles)
- `title_detection_patterns.json` - Reusable title detection patterns
- `WORKFLOW.md` - Complete interactive processing workflow

### Analysis Tools
- `tools/interactive_title_detector.py` - Full interactive validation system
- `tools/show_title_candidates.py` - Preview title candidates

### Document Structure (Validated)
```
📄 ANEXO Nº1 (Pages 1-62): Generation Programming
📄 ANEXO Nº2 (Pages 63-95): Real Generation Data  
📄 ANEXO Nº3 (Pages 96-100): CDC Reports
📄 INFORME DIARIO (Pages 101-134): Daily Report Day 1
📄 INFORME DIARIO (Pages 135-163): Daily Report Day 2
📄 ANEXO Nº4 (Pages 164-190): Maintenance Schedules
📄 ANEXO Nº5 (Pages 191-245): Company Failure Reports 🎯
📄 ANEXO Nº6 (Pages 246-256): Company Background 🎯
📄 ANEXO Nº7 (Page 257): Coordinator Background
📄 ANEXO Nº8 (Page 258): EDAC Analysis
```

## Usage for New Anexos EAF Documents

### Quick Start
```bash
# Use this profile for new Anexos EAF documents
python profiles/anexos_eaf/tools/show_title_candidates.py [new_document.pdf]

# Interactive validation 
python profiles/anexos_eaf/tools/interactive_title_detector.py [new_document.pdf]
```

### Reusable Patterns
The patterns in `title_detection_patterns.json` should work for any Anexos EAF document:
- Title detection rules (minimal content + specific starters)
- Content type mapping
- Interactive validation workflow

## Next Steps (Phase 2)

### Recommended Starting Points
1. **ANEXO Nº5** - Company failure reports (high-value structured data)
2. **ANEXO Nº6** - Company background/compliance (regulatory data)

### Phase 2 Development
Create pattern extraction for specific anexos with same interactive approach:
- User validates each extraction pattern
- Save working patterns to profile
- Build reusable data extraction tools

---
*Profile created: 2025-01-04*  
*Last tested: Anexos-EAF-089-2025.pdf*  
*Success rate: 100% title detection accuracy*