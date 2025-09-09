# Analysis Tools Inventory

## Document Understanding Code Location

### 🎯 **CORE WORKING TOOLS** (In Profile)
**Location**: `profiles/anexos_eaf/tools/`
- **`show_title_candidates.py`** ⭐ MAIN TOOL
  - **Purpose**: Fast preview of title candidates for Claude to show user
  - **How it works**: Applies title detection patterns, shows all candidates
  - **Used for**: Phase 1 title detection (proven method)

- **`interactive_title_detector.py`** 
  - **Purpose**: Full interactive validation with y/n prompts
  - **How it works**: Same detection + interactive user validation loop
  - **Used for**: Terminal environments with interactive input

### 🔍 **ANALYSIS & DEBUG TOOLS** (In Scripts)
**Location**: `scripts/`

#### Document Content Analysis
- **`debug_document_content.py`** ⭐ KEY ANALYSIS TOOL
  - **Purpose**: Show raw text from specific pages
  - **How it works**: Extracts text, shows with character/word counts
  - **Used for**: Understanding what's actually in document pages
  - **Example**: `python scripts/debug_document_content.py [doc.pdf] --pages 1-3`

- **`preview_chapters.py`**
  - **Purpose**: Quick chapter scan without interaction
  - **How it works**: Pattern matching across sample pages
  - **Used for**: Initial document structure discovery

#### Pattern Development Tools
- **`interactive_anexos_processor.py`**
  - **Purpose**: Multi-phase interactive processor (early version)
  - **How it works**: Chapter detection + pattern development framework
  - **Status**: Evolved into current profile approach

- **`smart_interactive_processor.py`**
  - **Purpose**: Smart chunked processing for large documents
  - **How it works**: Processes in batches with user validation
  - **Status**: Foundation for interactive approach

- **`phase1_chapter_mapper.py`**
  - **Purpose**: Interactive chapter boundary detection
  - **How it works**: Scans for chapter indicators + user validation
  - **Status**: Specialized for chapter mapping

#### Pattern Analysis Tools
- **`analyze_title_patterns.py`**
  - **Purpose**: Analyze title patterns across documents
  - **How it works**: Extract and compare title formats
  - **Used for**: Understanding title consistency

- **`find_all_document_titles.py`**
  - **Purpose**: Comprehensive title search
  - **How it works**: Multiple pattern matching approaches
  - **Used for**: Validation of title detection accuracy

## 🧠 **How Document Understanding Worked**

### Step 1: Initial Discovery
```python
# Used debug_document_content.py to see actual content
python scripts/debug_document_content.py [doc] --pages 1-5
# → Showed us page structure, word counts, actual text
```

### Step 2: Pattern Recognition  
```python
# Used preview_chapters.py to find potential patterns
python scripts/preview_chapters.py
# → Found "ANEXO Nº" and "INFORME DIARIO" patterns
```

### Step 3: Validation Development
```python
# Developed show_title_candidates.py for fast validation
python scripts/show_title_candidates.py  
# → Shows all candidates for user approval
```

### Step 4: Interactive Refinement
- **User feedback**: "Titles have minimal content + specific starters"
- **Pattern refinement**: <50 words + regex patterns
- **Validation approach**: User approves each candidate
- **Result**: 100% accuracy on title detection

## 🔧 **Key Code Patterns Used**

### Title Detection Logic
```python
def is_title_page(text):
    # Rule 1: Must start with specific patterns
    title_patterns = [
        r'^ANEXO\s+N[º°ªo]?\s*\d+',
        r'^INFORME\s+DIARIO'
    ]
    
    # Rule 2: Minimal content (title-only pages)
    word_count = len(text.split())
    is_minimal = word_count < 50
    
    return is_minimal and pattern_matches
```

### PDF Text Extraction
```python
from PyPDF2 import PdfReader

def extract_page_text(page_num):
    reader = PdfReader(document_path)
    page = reader.pages[page_num - 1]
    return page.extract_text().strip()
```

### Pattern Confidence Calculation
```python
def calculate_confidence(text, match, chapter_type):
    factors = []
    if match.start() < 200:  # Near page start
        factors.append("start_of_page")
    if len(text.split()) < 50:  # Minimal content
        factors.append("minimal_content")
    
    # High/Medium/Low based on factor count
    return confidence_level
```

## 📊 **Tools Usage Summary**

### For Initial Analysis
1. **`debug_document_content.py`** → See raw content
2. **`preview_chapters.py`** → Find patterns
3. **User validation** → Define rules

### For Working Process
1. **`show_title_candidates.py`** → Fast candidate preview
2. **User approval** → "All look good" or specific choices
3. **Save to profile** → `validated_titles.json`

### For Future Development
- **Phase 2**: Same pattern (extract samples → user validates → refine patterns)
- **Phase 3**: Batch processing with validation checkpoints

## 🎯 **Current Active Tools**

**Primary**: `profiles/anexos_eaf/tools/show_title_candidates.py`
- Used for all new Anexos EAF documents
- Fast terminal results for Claude to show user
- Proven 100% accuracy with user validation

**Debug**: `scripts/debug_document_content.py`  
- Used when need to see raw page content
- Essential for understanding document structure

**All other tools**: Development history, available for reference

---

*Analysis Tools Inventory v1.0*  
*Created: 2025-01-04*  
*Purpose: Document all code used to understand and process Anexos EAF documents*