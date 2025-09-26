#!/usr/bin/env python3
"""
Schema Validator - Ensures all extractions conform to universal schema
Forces Claude and all AI systems to respect JSON schema structure
"""

import json
import jsonschema
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

class SchemaValidator:
    """Validates all document extractions against universal schema"""

    def __init__(self):
        self.schemas_dir = Path(__file__).parent.parent / "schemas"
        self.universal_schema = self._load_universal_schema()
        self.domain_vocabularies = self._load_domain_vocabularies()
        self.context_schema = self._load_context_schema()

    def _load_universal_schema(self) -> Dict:
        """Load universal document schema for validation"""
        schema_file = self.schemas_dir / "universal_document_schema.json"
        if schema_file.exists():
            with open(schema_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _load_domain_vocabularies(self) -> Dict:
        """Load domain vocabularies for entity validation"""
        vocab_file = self.schemas_dir / "domain_vocabularies.json"
        if vocab_file.exists():
            with open(vocab_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _load_context_schema(self) -> Dict:
        """Load JSON-LD context for validation"""
        context_file = self.schemas_dir / "coordinador_context.jsonld"
        if context_file.exists():
            with open(context_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def validate_document(self, document: Dict, strict_mode: bool = True) -> Dict:
        """
        Validate document against universal schema

        Args:
            document: Document to validate
            strict_mode: If True, fails on any violation. If False, tries to fix

        Returns:
            Dict with validation results and corrected document
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "corrected_document": document.copy(),
            "auto_corrections": []
        }

        # 1. Validate JSON Schema structure
        schema_validation = self._validate_json_schema(document)
        validation_result["errors"].extend(schema_validation["errors"])
        validation_result["warnings"].extend(schema_validation["warnings"])

        # 2. Validate required universal fields
        universal_validation = self._validate_universal_fields(document)
        validation_result["errors"].extend(universal_validation["errors"])

        # 3. Validate entity types against vocabularies
        entity_validation = self._validate_entities(document)
        validation_result["errors"].extend(entity_validation["errors"])
        validation_result["warnings"].extend(entity_validation["warnings"])

        # 4. Validate cross-references
        cross_ref_validation = self._validate_cross_references(document)
        validation_result["errors"].extend(cross_ref_validation["errors"])

        # 5. Validate semantic tags
        tags_validation = self._validate_semantic_tags(document)
        validation_result["warnings"].extend(tags_validation["warnings"])

        # Apply auto-corrections if not in strict mode
        if not strict_mode and validation_result["errors"]:
            corrected = self._apply_auto_corrections(document, validation_result["errors"])
            validation_result["corrected_document"] = corrected["document"]
            validation_result["auto_corrections"] = corrected["corrections"]
            validation_result["errors"] = corrected["remaining_errors"]

        validation_result["valid"] = len(validation_result["errors"]) == 0

        return validation_result

    def _validate_json_schema(self, document: Dict) -> Dict:
        """Validate against JSON Schema"""
        errors = []
        warnings = []

        try:
            # Create a basic schema validator for universal structure
            schema = {
                "type": "object",
                "required": ["@context", "@id", "@type", "universal_metadata"],
                "properties": {
                    "@context": {"type": "string"},
                    "@id": {"type": "string"},
                    "@type": {"type": "string"},
                    "universal_metadata": {
                        "type": "object",
                        "required": ["title", "domain", "document_type", "creation_date"],
                        "properties": {
                            "title": {"type": "string"},
                            "domain": {"type": "string", "enum": ["operaciones", "mercados", "legal", "planificacion"]},
                            "document_type": {"type": "string"},
                            "creation_date": {"type": "string"}
                        }
                    },
                    "entities": {"type": "object"},
                    "cross_references": {"type": "array"},
                    "semantic_tags": {"type": "array"},
                    "domain_specific_data": {"type": "object"},
                    "quality_metadata": {"type": "object"}
                }
            }

            jsonschema.validate(document, schema)

        except jsonschema.ValidationError as e:
            errors.append(f"JSON Schema validation failed: {e.message}")
        except Exception as e:
            errors.append(f"Schema validation error: {str(e)}")

        return {"errors": errors, "warnings": warnings}

    def _validate_universal_fields(self, document: Dict) -> Dict:
        """Validate universal metadata fields"""
        errors = []

        # Check @id format
        doc_id = document.get("@id", "")
        if not doc_id.startswith("cen:"):
            errors.append(f"Document @id must start with 'cen:'. Found: {doc_id}")

        id_parts = doc_id.split(":")
        if len(id_parts) != 4:
            errors.append(f"Document @id must follow format 'cen:domain:type:date'. Found: {doc_id}")

        # Check domain consistency
        metadata = document.get("universal_metadata", {})
        domain = metadata.get("domain")
        if domain and len(id_parts) >= 2 and id_parts[1] != domain:
            errors.append(f"Domain mismatch: @id has '{id_parts[1]}' but metadata has '{domain}'")

        # Check date format
        creation_date = metadata.get("creation_date")
        if creation_date:
            try:
                datetime.fromisoformat(creation_date)
            except ValueError:
                errors.append(f"Invalid date format: {creation_date}. Use YYYY-MM-DD")

        return {"errors": errors}

    def _validate_entities(self, document: Dict) -> Dict:
        """Validate entities against domain vocabularies"""
        errors = []
        warnings = []

        entities = document.get("entities", {})
        vocab = self.domain_vocabularies.get("entity_types", {})

        for entity_type, entity_list in entities.items():
            # Check if entity type is in vocabulary
            if entity_type not in vocab:
                warnings.append(f"Entity type '{entity_type}' not in domain vocabulary")

            # Validate each entity
            if isinstance(entity_list, list):
                for entity in entity_list:
                    if not isinstance(entity, dict):
                        errors.append(f"Entity in '{entity_type}' must be object, found: {type(entity)}")
                        continue

                    # Check required fields
                    if "@id" not in entity:
                        errors.append(f"Entity in '{entity_type}' missing @id field")
                    if "@type" not in entity:
                        errors.append(f"Entity in '{entity_type}' missing @type field")
                    if "name" not in entity:
                        errors.append(f"Entity in '{entity_type}' missing name field")

                    # Check @id format
                    entity_id = entity.get("@id", "")
                    if not entity_id.startswith("cen:"):
                        errors.append(f"Entity @id must start with 'cen:'. Found: {entity_id}")

                    # Check @type against vocabulary
                    entity_type_val = entity.get("@type")
                    valid_types = vocab.get(entity_type, {}).get("subtypes", [])
                    if entity_type_val and valid_types and entity_type_val not in valid_types:
                        warnings.append(f"Entity @type '{entity_type_val}' not in vocabulary for '{entity_type}'")

        return {"errors": errors, "warnings": warnings}

    def _validate_cross_references(self, document: Dict) -> Dict:
        """Validate cross-references structure"""
        errors = []

        cross_refs = document.get("cross_references", [])
        if not isinstance(cross_refs, list):
            errors.append("cross_references must be an array")
            return {"errors": errors}

        for i, ref in enumerate(cross_refs):
            if not isinstance(ref, dict):
                errors.append(f"Cross-reference {i} must be object")
                continue

            # Check required fields
            required_fields = ["target_document_id", "target_domain", "relationship_type", "confidence"]
            for field in required_fields:
                if field not in ref:
                    errors.append(f"Cross-reference {i} missing required field: {field}")

            # Validate confidence score
            confidence = ref.get("confidence")
            if confidence is not None:
                if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
                    errors.append(f"Cross-reference {i} confidence must be float between 0.0 and 1.0")

            # Validate target_domain
            target_domain = ref.get("target_domain")
            valid_domains = ["operaciones", "mercados", "legal", "planificacion"]
            if target_domain and target_domain not in valid_domains:
                errors.append(f"Cross-reference {i} invalid target_domain: {target_domain}")

        return {"errors": errors}

    def _validate_semantic_tags(self, document: Dict) -> Dict:
        """Validate semantic tags against vocabulary"""
        warnings = []

        tags = document.get("semantic_tags", [])
        if not isinstance(tags, list):
            warnings.append("semantic_tags should be an array")
            return {"warnings": warnings}

        # Load approved tags from vocabulary
        approved_tags = set()
        vocab = self.domain_vocabularies.get("semantic_tags", {})
        for tag_category in vocab.values():
            if isinstance(tag_category, list):
                approved_tags.update(tag_category)

        # Check each tag
        for tag in tags:
            if not isinstance(tag, str):
                warnings.append(f"Semantic tag must be string, found: {type(tag)}")
            elif approved_tags and tag not in approved_tags:
                warnings.append(f"Semantic tag '{tag}' not in approved vocabulary")

        return {"warnings": warnings}

    def _apply_auto_corrections(self, document: Dict, errors: List[str]) -> Dict:
        """Apply automatic corrections to common errors"""
        corrected_doc = document.copy()
        corrections = []
        remaining_errors = []

        for error in errors:
            if "Document @id must start with 'cen:'" in error:
                # Try to fix @id format
                old_id = corrected_doc.get("@id", "")
                if old_id and not old_id.startswith("cen:"):
                    # Generate proper ID from metadata
                    metadata = corrected_doc.get("universal_metadata", {})
                    domain = metadata.get("domain", "unknown")
                    doc_type = metadata.get("document_type", "document")
                    date = metadata.get("creation_date", "unknown")

                    new_id = f"cen:{domain}:{doc_type}:{date}"
                    corrected_doc["@id"] = new_id
                    corrections.append(f"Fixed @id from '{old_id}' to '{new_id}'")
                else:
                    remaining_errors.append(error)

            elif "missing @id field" in error:
                # Generate missing entity IDs
                entities = corrected_doc.get("entities", {})
                for entity_type, entity_list in entities.items():
                    if isinstance(entity_list, list):
                        for entity in entity_list:
                            if "@id" not in entity and "name" in entity:
                                name_normalized = entity["name"].lower().replace(" ", "_")
                                entity["@id"] = f"cen:{entity_type}:{name_normalized}"
                                corrections.append(f"Generated @id for entity: {entity['name']}")

            elif "missing @type field" in error:
                # Generate missing entity types
                entities = corrected_doc.get("entities", {})
                for entity_type, entity_list in entities.items():
                    if isinstance(entity_list, list):
                        for entity in entity_list:
                            if "@type" not in entity:
                                # Use default type based on category
                                type_mapping = {
                                    "power_plants": "PowerPlant",
                                    "companies": "PowerCompany",
                                    "locations": "Location",
                                    "regulations": "LegalRegulation",
                                    "equipment": "Equipment"
                                }
                                entity["@type"] = type_mapping.get(entity_type, "Entity")
                                corrections.append(f"Generated @type for entity: {entity.get('name', 'unknown')}")

            else:
                remaining_errors.append(error)

        return {
            "document": corrected_doc,
            "corrections": corrections,
            "remaining_errors": remaining_errors
        }

    def create_schema_enforcer_prompt(self, domain: str, document_type: str) -> str:
        """
        Create a prompt that enforces schema compliance for Claude

        Args:
            domain: Target domain (operaciones, mercados, legal, planificacion)
            document_type: Specific document type

        Returns:
            Detailed prompt with schema requirements
        """

        prompt = f"""
CRITICAL: You MUST extract data following the EXACT universal schema structure below.
Any deviation will cause system failures. Follow this structure PRECISELY:

## REQUIRED JSON STRUCTURE:

```json
{{
  "@context": "https://coordinador.cl/context/v1",
  "@id": "cen:{domain}:{document_type}:YYYY-MM-DD",
  "@type": "{self._get_document_type(domain)}",

  "universal_metadata": {{
    "title": "EXACT title from document",
    "domain": "{domain}",
    "document_type": "{document_type}",
    "creation_date": "YYYY-MM-DD",
    "processing_date": "Current timestamp",
    "language": "es",
    "version": "1.0",
    "status": "final"
  }},

  "entities": {{
    "power_plants": [
      {{
        "@id": "cen:plant:normalized_name",
        "@type": "SolarPowerPlant|WindPowerPlant|HydroPowerPlant|ThermalPowerPlant",
        "name": "Exact plant name from document",
        "confidence": 0.0-1.0
      }}
    ],
    "companies": [
      {{
        "@id": "cen:company:normalized_name",
        "@type": "PowerCompany",
        "name": "Exact company name",
        "confidence": 0.0-1.0
      }}
    ],
    "locations": [
      {{
        "@id": "cen:location:normalized_name",
        "@type": "Region|Province|Commune",
        "name": "Exact location name",
        "confidence": 0.0-1.0
      }}
    ]
  }},

  "cross_references": [
    {{
      "target_document_id": "cen:domain:type:date",
      "target_domain": "operaciones|mercados|legal|planificacion",
      "relationship_type": "IMPACTS|REFERENCES|COMPLIES_WITH|TRIGGERS",
      "confidence": 0.0-1.0,
      "context": "Brief explanation"
    }}
  ],

  "semantic_tags": ["approved_tags_only"],

  "domain_specific_data": {{
    "{domain}": {{
      // Your existing extraction structure goes here
    }}
  }},

  "quality_metadata": {{
    "extraction_confidence": 0.0-1.0,
    "validation_status": "passed|failed",
    "processing_method": "method_name",
    "quality_score": 0.0-1.0,
    "human_validated": false
  }}
}}
```

## VALIDATION RULES:

1. **@id Format**: MUST be "cen:domain:type:date" - NO exceptions
2. **Entity @id**: MUST be "cen:entity_type:normalized_name"
3. **Domain**: MUST be exactly "{domain}"
4. **All entities**: MUST have @id, @type, name, confidence fields
5. **Confidence scores**: MUST be between 0.0 and 1.0
6. **Dates**: MUST be YYYY-MM-DD format
7. **Cross-references**: Target domains MUST be valid CEN domains

## APPROVED SEMANTIC TAGS:
{self._get_approved_tags_for_domain(domain)}

## ENTITY TYPES:
- Power Plants: SolarPowerPlant, WindPowerPlant, HydroPowerPlant, ThermalPowerPlant
- Companies: PowerCompany
- Locations: Region, Province, Commune
- Regulations: LegalRegulation
- Equipment: Equipment

## FAILURE CONDITIONS:
- Missing required fields → SYSTEM FAILURE
- Wrong @id format → SYSTEM FAILURE
- Invalid domain values → SYSTEM FAILURE
- Missing confidence scores → SYSTEM FAILURE

EXTRACT DATA NOW following this EXACT structure. Your existing domain-specific data should go inside "domain_specific_data".{domain}.
"""
        return prompt

    def _get_document_type(self, domain: str) -> str:
        """Get @type for document based on domain"""
        type_mapping = {
            "operaciones": "PowerSystemDocument",
            "mercados": "MarketReport",
            "legal": "LegalRegulation",
            "planificacion": "PlanningStudy"
        }
        return type_mapping.get(domain, "Document")

    def _get_approved_tags_for_domain(self, domain: str) -> str:
        """Get approved semantic tags for domain"""
        domain_tags = {
            "operaciones": ["operational_data", "real_time", "renewable_energy", "thermal_generation", "incidents"],
            "mercados": ["market_data", "price_analysis", "demand_forecast", "trading"],
            "legal": ["regulation_compliance", "legal_framework", "penalties"],
            "planificacion": ["infrastructure_planning", "capacity_analysis", "forecasting"]
        }

        tags = domain_tags.get(domain, [])
        return ", ".join([f'"{tag}"' for tag in tags])

# Example usage
if __name__ == "__main__":
    validator = SchemaValidator()

    # Test document
    test_doc = {
        "@context": "https://coordinador.cl/context/v1",
        "@id": "cen:operaciones:anexo_01:2025-02-15",
        "@type": "PowerSystemDocument",
        "universal_metadata": {
            "title": "ANEXO 1 - Test",
            "domain": "operaciones",
            "document_type": "anexo_01",
            "creation_date": "2025-02-15"
        },
        "entities": {
            "power_plants": [
                {
                    "@id": "cen:plant:solar_test",
                    "@type": "SolarPowerPlant",
                    "name": "Solar Test",
                    "confidence": 0.95
                }
            ]
        },
        "cross_references": [],
        "semantic_tags": ["operational_data", "real_time"]
    }

    # Validate
    result = validator.validate_document(test_doc, strict_mode=False)
    print(f"Valid: {result['valid']}")
    if result['errors']:
        print("Errors:", result['errors'])
    if result['auto_corrections']:
        print("Auto-corrections:", result['auto_corrections'])

    # Generate enforcer prompt
    prompt = validator.create_schema_enforcer_prompt("operaciones", "anexo_01")
    print("\nSchema Enforcer Prompt Preview:")
    print(prompt[:500] + "...")