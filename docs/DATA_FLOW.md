# 📊 Data Flow - Complete Pipeline

## Overview

This document describes the complete data flow from PDF download to AI-powered queries in the Dark Data Platform.

## 🔄 Visual Flow

```
📄 PDF → 🔍 Extraction → 📦 Universal Schema → 🔗 Cross-References → 💾 Storage → 🤖 AI Access
```

---

## Step 1: 📥 Document Download & Storage

Documents are organized by business domain:

```
domains/
├── operaciones/
│   └── data/
│       └── documents/
│           └── anexos_EAF/
│               ├── anexo_01.pdf
│               ├── anexo_02.pdf
│               └── informe_diario.pdf
├── mercados/data/documents/
├── legal/data/documents/
└── planificacion/data/documents/
```

**Purpose**: Raw document storage with domain separation for better organization and processing.

---

## Step 2: 🔍 Document-Specific Extraction

Each document type requires specialized processing with its own extraction logic, field names, and cross-reference rules. The system routes documents to type-specific processors that output universal JSON format.

### **🔑 Key Point: Each Document Type is Completely Different**

**What's INDIVIDUAL per document type:**
- ❌ **PDF extraction logic** - Each document has different table structures
- ❌ **Data field names** - "upper_table" vs "incidentes_reportados" vs "eventos_operacionales"
- ❌ **Entity extraction logic** - Looking for different column names and data types
- ❌ **Cross-reference rules** - Each type relates differently to other domains
- ❌ **Processing functions** - Each needs specialized parsing functions

**What's UNIVERSAL across all types:**
- ✅ **JSON structure** - All follow same "@context", "@id", "@type" pattern
- ✅ **Metadata fields** - All have "metadatos_universales" with same structure
- ✅ **Entity categories** - All use "entidades", "referencias_cruzadas" sections
- ✅ **Storage format** - All preserve original data in "datos_especificos_dominio"

**New Document Type**: AI-assisted processor creation (15-20 min) → Reuse for all future documents (30 sec)

---

## Step 3: 💾 Structured Storage

All documents saved as universal JSON-LD with semantic web compliance, consistent metadata, extracted entities, cross-references, and preserved original data.

---

## Step 4: 🗄️ Database Consolidation

Unified SQLite database with documents, entities, cross-references, and full-text searchable content.

---

## Step 5: 🤖 AI Access

Multiple access channels: MCP servers for direct AI tool access, web dashboard for human users, and CLI tools.

---

## Step 6: 🧠 Intelligent AI Queries

AI can process cross-domain queries by following references between documents, enabling operational, temporal, and compliance analysis across all domains.

---

## 🎯 Architecture Summary

**Flow**: PDF → Document-Specific Processing → Universal JSON → Database → AI Access

**Key Patterns**:
- Each document type needs specialized processor
- First time: AI-assisted creation (15-20 min)
- Subsequent times: Reuse existing processor (30 seconds)
- All outputs follow universal JSON-LD schema

---

## 🔗 Cross-References and Tags Management

**Rule Generation**: New document types → AI suggests rules → Human validates → Rules applied to all future documents
**Management**: YAML configuration files, web interface, CLI tools, automatic code generation

## Quick Start

1. Process document with type-specific processor
2. Ingest to unified database
3. Start AI access via MCP servers

## Related Documentation

- [`DATA_FLOW_EXAMPLE.md`](DATA_FLOW_EXAMPLE.md) - Complete walkthrough example
- [`prompts/README.md`](../prompts/README.md) - AI prompt templates
- [`CLAUDE.md`](../CLAUDE.md) - Project documentation