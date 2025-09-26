# Universal Schema Implementation Guide

## Overview
This guide explains how to implement the universal document schema across all domains in the Coordinador Eléctrico Nacional project.

## Schema Structure

### 1. Universal Document Schema
**File**: `platform_data/schemas/universal_document_schema.json`

**Purpose**: Standardizes ALL documents across ALL domains while allowing domain-specific flexibility.

### 2. Domain Vocabularies
**File**: `platform_data/schemas/domain_vocabularies.json`

**Purpose**: Defines standardized entity types, relationships, and terminology for knowledge graph integration.

### 3. JSON-LD Context
**File**: `platform_data/schemas/coordinador_context.jsonld`

**Purpose**: Enables knowledge graph capabilities and linked data integration.

## Document ID Convention

### Format
```
cen:{domain}:{document_type}:{date}
```

### Examples
- `cen:operaciones:anexo_01:2025-02-15`
- `cen:mercados:price_report:2025-02-15`
- `cen:legal:regulation_123:2025-02-15`
- `cen:planificacion:capacity_study:2025-02-15`

## Implementation Steps

### 1. Update Existing Templates
Modify existing JSON extraction templates to include:

```json
{
  "@context": "https://coordinador.cl/context/v1",
  "@id": "cen:operaciones:anexo_01:2025-02-15",
  "@type": "PowerSystemDocument",

  "universal_metadata": {
    "title": "ANEXO 1 - Generación Programada",
    "domain": "operaciones",
    "document_type": "anexo_generation_programming",
    "creation_date": "2025-02-15",
    "processing_date": "2025-02-15T10:30:00Z"
  },

  "entities": {
    "power_plants": [
      {
        "@id": "cen:plant:solar_atacama_123",
        "@type": "SolarPowerPlant",
        "name": "Solar Atacama 123",
        "confidence": 0.95
      }
    ]
  },

  "cross_references": [
    {
      "target_document_id": "cen:mercados:price_forecast:2025-02-15",
      "target_domain": "mercados",
      "relationship_type": "IMPACTS",
      "confidence": 0.85,
      "context": "Generation affects market prices"
    }
  ],

  "semantic_tags": ["renewable_energy", "operational_data", "real_time"],

  "domain_specific_data": {
    "operaciones": {
      // Existing anexo structure goes here
      "upper_table": { ... },
      "lower_table": { ... }
    }
  },

  "quality_metadata": {
    "extraction_confidence": 0.92,
    "validation_status": "passed",
    "human_validated": true
  }
}
```

### 2. Entity Recognition Rules

#### Power Plants
- **ID Format**: `cen:plant:{name_normalized}`
- **Types**: SolarPowerPlant, WindPowerPlant, HydroPowerPlant, ThermalPowerPlant
- **Extract from**: Plant names in generation tables

#### Companies
- **ID Format**: `cen:company:{company_name_normalized}`
- **Type**: PowerCompany
- **Extract from**: Company ownership information

#### Locations
- **ID Format**: `cen:location:{region_normalized}`
- **Type**: Region, Province, Commune
- **Extract from**: Address or location context

### 3. Cross-Reference Detection

#### Automatic Linking
- **Same Date Documents**: Link anexos with daily reports from same date
- **Plant References**: Link operational data with market data for same plants
- **Regulatory Links**: Link operational procedures with legal regulations

#### Example Cross-References
```json
"cross_references": [
  {
    "target_document_id": "cen:mercados:daily_prices:2025-02-15",
    "target_domain": "mercados",
    "relationship_type": "IMPACTS",
    "confidence": 0.80,
    "context": "Solar generation affects midday prices"
  },
  {
    "target_document_id": "cen:legal:solar_regulation_456",
    "target_domain": "legal",
    "relationship_type": "COMPLIES_WITH",
    "confidence": 0.95,
    "context": "Solar plant follows renewable energy regulations"
  }
]
```

### 4. Semantic Tags Guidelines

#### Mandatory Tags (All Documents)
- **Domain**: operaciones/mercados/legal/planificacion
- **Data Type**: real_time/historical/forecast/statistical
- **Priority**: critical/high/medium/low

#### Domain-Specific Tags
- **Operaciones**: renewable_energy, thermal_generation, transmission, incidents
- **Mercados**: market_price, demand_forecast, auctions, trading
- **Legal**: regulation_compliance, penalties, environmental_law
- **Planificacion**: capacity_expansion, infrastructure, forecasting

### 5. Migration Strategy

#### Phase 1: Core Implementation
1. Update operaciones anexo templates with universal schema
2. Implement entity recognition for power plants and companies
3. Add basic cross-references to same-date documents

#### Phase 2: Knowledge Graph
1. Implement full entity linking across domains
2. Add relationship detection algorithms
3. Create knowledge graph visualization

#### Phase 3: AI Integration
1. Use standardized schema for AI training
2. Implement semantic search across domains
3. Enable AI to answer cross-domain questions

## Benefits

### For AI Understanding
- **Consistent Structure**: AI knows what to expect in ANY document
- **Entity Linking**: AI can connect power plants across different documents
- **Cross-Domain Insights**: AI can answer "How did this incident affect prices?"

### For Data Integration
- **Universal Search**: Find any entity across all domains
- **Relationship Mapping**: Understand how operations affects markets
- **Standardized APIs**: Same query structure for all domains

### For Knowledge Management
- **Institutional Memory**: Track how entities evolve over time
- **Impact Analysis**: Trace effects across different business areas
- **Regulatory Compliance**: Link operations to legal requirements

## Validation

### Schema Validation
All documents must validate against:
1. JSON Schema: `universal_document_schema.json`
2. Required fields: @context, @id, @type, universal_metadata
3. Domain vocabulary: Entity types from `domain_vocabularies.json`

### Quality Checks
- Entity confidence scores > 0.7
- Cross-references have valid target documents
- Semantic tags from approved vocabulary
- Document IDs follow convention

## Next Steps

1. **Update Existing Templates**: Modify current anexo templates
2. **Implement Entity Recognition**: Add AI-powered entity extraction
3. **Create Cross-Reference Engine**: Detect relationships between documents
4. **Build Knowledge Graph**: Visualize connections between entities
5. **Enable Semantic Search**: Query across all domains using natural language

This universal schema enables AI to understand relationships between operational data, market impacts, legal compliance, and planning requirements - creating true institutional intelligence.