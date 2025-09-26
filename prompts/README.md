# Prompts Directory

This directory contains AI instruction templates for the Chilean electrical system project.

## Available Prompts

### `PROMPT_ESQUEMA_UNIVERSAL_CHILE_IA.md`
**Primary AI instruction template** for generating schema-compliant extraction code.

**Usage:**
1. Copy the entire prompt content
2. Paste at the beginning of your AI conversation
3. Request: "Generate extraction code for [document type]"
4. AI automatically produces universal JSON structure

**Purpose:**
- Ensures all AI-generated extraction scripts follow universal schema
- Provides general document structure for any domain
- Preserves original extraction data
- Creates standardized JSON-LD output

### `PROMPT_REFERENCIAS_CRUZADAS.md`
**Secondary template** for generating cross-references between documents.

**Usage:**
1. Copy the prompt content
2. Paste your universal JSON document
3. AI analyzes and returns cross-references array
4. Integrate references into your document

**Purpose:**
- Generates automatic cross-references between related documents
- Applies temporal, entity, and domain-specific rules
- Creates linkages for knowledge graph integration
- Returns clean JSON array ready for integration

## How to Use

1. **For any new document extraction:**
   - Open `PROMPT_ESQUEMA_UNIVERSAL_CHILE_IA.md`
   - Copy the entire content
   - Paste at the start of your AI conversation
   - Ask AI to generate extraction code

2. **Expected output:**
   - Code that produces universal JSON-LD structure
   - Automatic entity extraction (plants, companies)
   - Chilean electrical system context
   - Cross-domain compatibility

## Workflow

### Step 1: Extract with Universal Schema
```bash
# Use PROMPT_ESQUEMA_UNIVERSAL_CHILE_IA.md
# Result: Document with universal JSON structure
```

### Step 2: Generate Cross-References
```bash
# Use PROMPT_REFERENCIAS_CRUZADAS.md
# Result: Array of cross-references to integrate
```

### Step 3: Final Integration
```python
# Add references array to your universal document
document["referencias_cruzadas"] = referencias_array
```

## File Structure

```
prompts/
├── README.md                            # This documentation
├── PROMPT_ESQUEMA_UNIVERSAL_CHILE_IA.md # Main universal schema template
└── PROMPT_REFERENCIAS_CRUZADAS.md       # Cross-references generation template
```