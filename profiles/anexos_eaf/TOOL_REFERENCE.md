# Tool Reference Guide

## What Each Tool Does Exactly

### `show_title_candidates.py`
**Purpose**: Get results quickly in terminal for Claude to see and process  
**When to use**: Claude Code environments where interactive input doesn't work  
**Output**: List of all candidates with full content preview  
**Interaction**: None - just shows results for Claude to analyze  
**Key benefit**: Faster than interactive tool - Claude gets all candidates immediately  

**Example Usage**:
```bash
python profiles/anexos_eaf/tools/show_title_candidates.py
```

**Example Output**:
```
📖 CANDIDATE 1:
   📄 Page: 1
   🏷️  Title: 'ANEXO Nº1'
   📊 Words: 17
   📝 Content:
   ------------------------------
   ANEXO Nº1
   Detalle de la generación programada para los días 25 y 26 de febrero de 2025
   ------------------------------
```

**Use this when**:
- ✅ You want to see what would be detected before validating
- ✅ Quick preview of document structure  
- ✅ Working in environments without interactive input
- ✅ Showing results to others for review

---

### `interactive_title_detector.py`
**Purpose**: Full interactive validation with y/n prompts  
**When to use**: When you have terminal input capability  
**Output**: Only saves user-approved titles  
**Interaction**: Asks y/n for each candidate  

**Example Usage**:
```bash
python profiles/anexos_eaf/tools/interactive_title_detector.py [document_path]
```

**Interactive Process**:
```
📖 TITLE CANDIDATE 1/10
📄 Page: 1
🏷️  Detected Title: 'ANEXO Nº1'
📝 Full Page Content: [shows content]
❓ Is this a valid title page?
   y = Yes, this is a title page
   n = No, skip this page  
   m = Show more context
   q = Quit and save progress
👉 Your choice (y/n/m/q): █
```

**Use this when**:
- ✅ You can provide interactive y/n responses
- ✅ You want to validate each title individually  
- ✅ You want to see context around each candidate
- ✅ You want automatic saving of validated results

---

## Recommended Workflow

### Step 1: Preview First
```bash
# Always start with preview to see what was found
python profiles/anexos_eaf/tools/show_title_candidates.py
```

### Step 2: Decide Validation Method
**Option A: Batch Validation** (Recommended for Claude Code)
- Review preview results
- Tell Claude: "All look good" or "Validate candidates 1, 3, 5"
- Claude manually saves approved titles

**Option B: Interactive Validation** (For terminal environments)
```bash
python profiles/anexos_eaf/tools/interactive_title_detector.py [document]
```

## Key Differences

| Feature | show_title_candidates.py | interactive_title_detector.py |
|---------|-------------------------|--------------------------------|
| **Interaction** | None - just shows | y/n prompts for each |
| **Input Required** | No | Yes - terminal input |
| **Output** | Preview only | Saves validated results |
| **Use Case** | Quick overview | Detailed validation |
| **Environment** | Any | Terminal with input |

## For Different Users

### For Claude Code Sessions
- ✅ Use `show_title_candidates.py` first (faster results in terminal)
- ✅ Claude gets all candidates immediately to show user
- ✅ User validates based on preview ("all look good" or specific choices)
- ✅ Claude manually saves approved titles to profiles
- ❌ Don't use interactive tool (no terminal input available)

### For Terminal Users  
- ✅ Can use either tool
- ✅ Interactive tool provides step-by-step validation
- ✅ Preview tool for quick checks

### For Other Developers
- ✅ Both tools available as reference implementations
- ✅ Patterns can be extracted and reused
- ✅ Interactive approach can be adapted to other UIs

---

*Reference Version: 1.0*  
*Updated: 2025-01-04*  
*Purpose: Clear explanation of tool purposes and usage*