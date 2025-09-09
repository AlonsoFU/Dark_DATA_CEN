# Interactive Process Documentation

## What "Interactive" Means in This Context

### The Interactive Validation Approach (Proven Method)

**NOT automated detection** - The patterns find candidates, but **YOU decide** what's valid.

### Real Interactive Process Flow

#### Phase 1: Title Detection (COMPLETED)
```
1. Claude runs: show_title_candidates.py
   → Shows all candidates with content preview

2. Claude presents to user:
   "Found 10 potential titles:
   📖 CANDIDATE 1: Page 1: 'ANEXO Nº1' (17 words)
   📖 CANDIDATE 2: Page 63: 'ANEXO Nº 2' (19 words)
   [... shows all candidates with content]"

3. User validates in real-time:
   → "All look good!" 
   → "Only candidates 1, 3, 5"
   → "Skip candidate 2"

4. Claude saves ONLY user-approved titles
   → Updates profiles/anexos_eaf/validated_titles.json
   → Only contains what YOU approved

5. Result: 100% user-validated chapter structure
```

#### Phase 2: Pattern Development (NEXT)
```
1. User chooses chapter: "Let's work on ANEXO Nº5"

2. Claude extracts sample pages:
   → "Page 192: Found 'EMPRESA: ENEL CHILE S.A.' - Is this a company name? (y/n)"
   → "Page 193: Found 'RUT: 76.536.353-9' - Is this correct format? (y/n)"

3. User validates each extraction:
   → "Yes, that's a company name"
   → "No, that RUT format is wrong - should be XX.XXX.XXX-X"

4. Claude builds patterns based on your feedback:
   → Saves working patterns to profiles/
   → Tests patterns on more pages
   → Shows results for your approval

5. Iterative refinement:
   → Pattern fails → Claude shows you → You guide correction → Pattern improves
```

#### Phase 3: Data Extraction (FUTURE)
```
1. Claude processes pages in batches:
   → "Processing pages 191-195... found 3 companies, 2 RUTs"

2. Shows extractions for validation:
   → "EXTRACTED: Company: 'COLBÚN S.A.', RUT: '76.536.353-9' - Correct? (y/n)"

3. User validates in real-time:
   → "Yes, continue"
   → "No, that company name is incomplete"

4. Claude adjusts and continues:
   → Only saves user-approved data
   → Refines patterns based on your corrections
```

## Key Interactive Principles

### 1. User Control at Every Step
- **Claude finds candidates** → **User decides what's valid**
- **Claude extracts data** → **User validates each extraction**  
- **Claude suggests patterns** → **User approves/corrects**

### 2. Real-Time Feedback Loop
- Show results immediately after each step
- Get user validation before proceeding
- Adjust approach based on user feedback
- Never assume automated results are correct

### 3. Iterative Improvement
- Patterns start basic → improve with user feedback
- Each validation improves accuracy
- User corrections become pattern refinements
- Progressive learning throughout session

## Interactive vs Non-Interactive

### ❌ Non-Interactive (BAD)
```
Claude: "I processed the document and found 147 companies and 89 RUTs"
User: "How do I know if they're correct?"
Result: No validation, potentially wrong data
```

### ✅ Interactive (GOOD - Our Approach)
```
Claude: "Page 192: Found 'EMPRESA ELÉCTRICA DEL SUR S.A.' - Is this a complete company name? (y/n)"
User: "No, it should be 'EMPRESA ELÉCTRICA DEL SUR S.A. - SUBSIDIARY CHILE'"  
Claude: "Updated pattern to capture full company names including subsidiaries"
Result: Accurate, user-validated data with improved patterns
```

## Why This Interactive Approach Works

### 1. Accuracy Through Validation
- **Human expertise** validates automated findings
- **Domain knowledge** guides pattern development
- **Real-time corrections** prevent error propagation

### 2. Pattern Learning
- **User feedback** improves extraction patterns
- **Iterative refinement** increases accuracy over time
- **Reusable patterns** work better on future documents

### 3. User Confidence
- **You approve everything** before it's saved
- **Transparent process** - see exactly what's being extracted
- **Control over quality** - reject anything that doesn't look right

## Commands for Interactive Sessions

### Starting Interactive Session
```bash
# Phase 1: Title detection
python profiles/anexos_eaf/tools/show_title_candidates.py
# → Claude shows candidates → You validate → Claude saves approved

# Phase 2: Pattern development  
# → Choose chapter → Claude extracts samples → You validate → Patterns improve

# Phase 3: Data extraction
# → Process in batches → Claude shows extractions → You validate → Save approved data
```

### Validation Language
- **"All look good"** → Accept all candidates
- **"Only 1, 3, 5"** → Accept specific ones
- **"Skip 2"** → Accept all except specified
- **"Show me page X"** → Need more context
- **"That's wrong because..."** → Correction with explanation

## Success Metrics

### Interactive Session Success
- ✅ **User validates every finding** before saving
- ✅ **Patterns improve** based on user feedback
- ✅ **High accuracy** through human oversight  
- ✅ **Reusable assets** created for future documents

### What Makes It "Interactive"
1. **Real-time validation** - immediate user feedback
2. **Iterative refinement** - patterns improve during session
3. **User control** - nothing saved without approval
4. **Learning system** - each correction improves future results

---

*Interactive Process Documentation v1.0*  
*Created: 2025-01-04*  
*Purpose: Ensure future sessions maintain interactive validation approach*