#!/usr/bin/env python3
"""
Claude Schema Enforcer - Ensures Claude always respects JSON schema
Automatically injects schema validation into all AI interactions
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from .schema_validator import SchemaValidator

class ClaudeSchemaEnforcer:
    """Enforces universal schema compliance in all Claude interactions"""

    def __init__(self):
        self.validator = SchemaValidator()
        self.templates_dir = Path(__file__).parent / "templates"
        self.templates_dir.mkdir(exist_ok=True)

    def create_extraction_prompt(self, domain: str, document_type: str,
                               document_text: str, additional_context: str = "") -> str:
        """
        Create schema-enforced extraction prompt for Claude

        Args:
            domain: Target domain (operaciones, mercados, legal, planificacion)
            document_type: Specific document type
            document_text: Text to extract from
            additional_context: Any additional extraction context

        Returns:
            Complete prompt with schema enforcement
        """

        schema_prompt = self.validator.create_schema_enforcer_prompt(domain, document_type)

        full_prompt = f"""
{schema_prompt}

## DOCUMENT TO EXTRACT FROM:

{document_text}

## ADDITIONAL CONTEXT:
{additional_context}

## EXTRACTION INSTRUCTIONS:

1. Read the document carefully
2. Extract ALL entities (power plants, companies, locations, regulations, equipment)
3. Follow the EXACT JSON structure provided above
4. Put your domain-specific extraction data inside "domain_specific_data".{domain}
5. Generate appropriate semantic tags from the approved list
6. Set realistic confidence scores based on extraction certainty
7. Do NOT add any fields not shown in the schema
8. Do NOT deviate from the required structure

## RESPONSE FORMAT:

Return ONLY valid JSON following the exact structure above. No additional text, explanations, or formatting.

Begin extraction now:
"""
        return full_prompt

    def validate_claude_response(self, response: str, domain: str,
                                strict_mode: bool = False) -> Dict:
        """
        Validate Claude's response against schema

        Args:
            response: Claude's JSON response
            domain: Expected domain
            strict_mode: Whether to apply strict validation

        Returns:
            Validation result with corrected document if needed
        """

        try:
            # Parse JSON response
            if isinstance(response, str):
                document = json.loads(response)
            else:
                document = response

            # Validate against schema
            validation_result = self.validator.validate_document(document, strict_mode)

            # Additional Claude-specific checks
            claude_checks = self._perform_claude_specific_checks(document, domain)
            validation_result["warnings"].extend(claude_checks["warnings"])
            validation_result["errors"].extend(claude_checks["errors"])

            return validation_result

        except json.JSONDecodeError as e:
            return {
                "valid": False,
                "errors": [f"Invalid JSON response: {str(e)}"],
                "warnings": [],
                "corrected_document": None,
                "auto_corrections": []
            }

    def _perform_claude_specific_checks(self, document: Dict, expected_domain: str) -> Dict:
        """Perform Claude-specific validation checks"""
        errors = []
        warnings = []

        # Check if Claude followed domain instruction
        actual_domain = document.get("universal_metadata", {}).get("domain")
        if actual_domain != expected_domain:
            errors.append(f"Claude used wrong domain: expected '{expected_domain}', got '{actual_domain}'")

        # Check if Claude added unauthorized fields
        required_top_level = {"@context", "@id", "@type", "universal_metadata", "entities",
                             "cross_references", "semantic_tags", "domain_specific_data", "quality_metadata"}
        actual_fields = set(document.keys())
        extra_fields = actual_fields - required_top_level

        if extra_fields:
            warnings.append(f"Claude added extra fields: {list(extra_fields)}")

        # Check if Claude provided confidence scores
        entities = document.get("entities", {})
        for entity_type, entity_list in entities.items():
            if isinstance(entity_list, list):
                for entity in entity_list:
                    if "confidence" not in entity:
                        warnings.append(f"Missing confidence score for {entity_type} entity")

        return {"errors": errors, "warnings": warnings}

    def create_workflow_integration(self, workflow_file: Path) -> str:
        """
        Create code snippet to integrate schema enforcement into existing workflows

        Args:
            workflow_file: Path to existing extraction workflow

        Returns:
            Python code to add to workflow
        """

        integration_code = f'''
# Schema Enforcement Integration - Add to {workflow_file.name}

from ai_platform.knowledge_graph.validation.claude_schema_enforcer import ClaudeSchemaEnforcer

def extract_with_schema_enforcement(document_text: str, domain: str, document_type: str):
    """Extract data with automatic schema validation"""

    # Initialize enforcer
    enforcer = ClaudeSchemaEnforcer()

    # Create schema-enforced prompt
    extraction_prompt = enforcer.create_extraction_prompt(
        domain=domain,
        document_type=document_type,
        document_text=document_text,
        additional_context="Your existing extraction context here"
    )

    # Send to Claude (replace with your Claude API call)
    claude_response = send_to_claude(extraction_prompt)

    # Validate response
    validation_result = enforcer.validate_claude_response(
        response=claude_response,
        domain=domain,
        strict_mode=False  # Allow auto-corrections
    )

    if validation_result["valid"]:
        print("✅ Schema validation passed")
        return validation_result["corrected_document"]
    else:
        print("❌ Schema validation failed:")
        for error in validation_result["errors"]:
            print(f"  - {{error}}")

        # Use corrected document if available
        if validation_result["corrected_document"]:
            print("🔧 Using auto-corrected document")
            return validation_result["corrected_document"]
        else:
            raise ValueError("Schema validation failed and no corrections possible")

# Example usage in your extraction workflow:
# extracted_data = extract_with_schema_enforcement(
#     document_text=pdf_text,
#     domain="operaciones",
#     document_type="anexo_01"
# )
'''
        return integration_code

    def save_prompt_template(self, domain: str, document_type: str) -> Path:
        """Save reusable prompt template for domain/document type"""

        template_content = {
            "domain": domain,
            "document_type": document_type,
            "schema_prompt": self.validator.create_schema_enforcer_prompt(domain, document_type),
            "created": "2025-02-15",
            "description": f"Schema-enforced extraction template for {domain} {document_type}"
        }

        template_file = self.templates_dir / f"{domain}_{document_type}_template.json"
        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(template_content, f, indent=2, ensure_ascii=False)

        return template_file

    def create_system_prompt_enhancement(self) -> str:
        """Create system prompt enhancement for Claude configurations"""

        system_enhancement = """
## UNIVERSAL SCHEMA COMPLIANCE REQUIREMENT

You are working with a Chilean electrical system data processing project that requires STRICT adherence to a universal JSON schema.

### CRITICAL RULES:
1. **ALL document extractions MUST follow the universal schema structure**
2. **NEVER deviate from the required @context, @id, @type format**
3. **ALWAYS include universal_metadata with exact required fields**
4. **ALL entities MUST have @id, @type, name, confidence fields**
5. **Document @id MUST follow format: cen:domain:type:date**
6. **Entity @id MUST follow format: cen:entity_type:normalized_name**

### VALIDATION REQUIREMENTS:
- Domain MUST be one of: operaciones, mercados, legal, planificacion
- All confidence scores MUST be between 0.0 and 1.0
- Dates MUST be in YYYY-MM-DD format
- Entity types MUST be from approved vocabulary
- Cross-references MUST target valid CEN domains

### FAILURE CONDITIONS:
Any deviation from the schema structure will cause system failures and data corruption.

### RESPONSE FORMAT:
When extracting data, return ONLY valid JSON following the universal schema. No additional text or explanations outside the JSON structure.
"""
        return system_enhancement

    def generate_documentation(self) -> str:
        """Generate comprehensive documentation for schema enforcement"""

        doc = """
# Claude Schema Enforcement System

## Overview
This system ensures that every interaction with Claude respects the universal JSON schema for the Chilean electrical system data processing project.

## How It Works

### 1. Automatic Prompt Enhancement
Every extraction request is automatically enhanced with:
- Complete schema structure requirements
- Validation rules and constraints
- Approved vocabularies and entity types
- Failure conditions and consequences

### 2. Response Validation
Every Claude response is automatically validated against:
- JSON Schema structure
- Universal metadata requirements
- Entity format compliance
- Cross-reference validity

### 3. Auto-Correction System
When validation fails in non-strict mode:
- Missing @id fields are generated automatically
- Wrong @id formats are corrected
- Missing entity types are inferred
- Basic structural issues are fixed

## Integration Examples

### Basic Extraction
```python
from ai_platform.knowledge_graph.validation.claude_schema_enforcer import ClaudeSchemaEnforcer

enforcer = ClaudeSchemaEnforcer()

# Create schema-enforced prompt
prompt = enforcer.create_extraction_prompt(
    domain="operaciones",
    document_type="anexo_01",
    document_text=pdf_content
)

# Send to Claude and validate response
response = send_to_claude(prompt)
validation = enforcer.validate_claude_response(response, "operaciones")

if validation["valid"]:
    final_data = validation["corrected_document"]
else:
    print("Validation errors:", validation["errors"])
```

### Workflow Integration
```python
# Add to existing extraction scripts
def enhanced_extraction(pdf_path: Path, domain: str, doc_type: str):
    text = extract_text_from_pdf(pdf_path)

    # Schema enforcement
    enforcer = ClaudeSchemaEnforcer()
    prompt = enforcer.create_extraction_prompt(domain, doc_type, text)

    response = claude_api_call(prompt)
    validation = enforcer.validate_claude_response(response, domain)

    return validation["corrected_document"]
```

## Benefits

### For Developers
- **Guaranteed Consistency**: All extractions follow same structure
- **Automatic Validation**: Catch errors before they enter the system
- **Auto-Correction**: Fix common issues automatically
- **Clear Error Messages**: Know exactly what went wrong

### For AI Integration
- **Predictable Structure**: AI knows exactly what to expect
- **Entity Linking**: Standardized IDs enable cross-document connections
- **Knowledge Graph Ready**: JSON-LD format for semantic web integration
- **Cross-Domain Queries**: Universal schema enables complex queries

### For Data Quality
- **Schema Compliance**: 100% adherence to universal structure
- **Validation Scores**: Confidence metrics for every extraction
- **Error Prevention**: Stop bad data before it enters the system
- **Audit Trail**: Track validation results and corrections

## Files Created

1. `schema_validator.py` - Core validation engine
2. `claude_schema_enforcer.py` - Claude integration layer
3. Template files for each domain/document type
4. Integration code snippets for existing workflows

## Next Steps

1. **Integrate with existing workflows** - Add enforcer to current extraction scripts
2. **Update MCP servers** - Include schema validation in MCP tool responses
3. **Train AI models** - Use validated data for training and fine-tuning
4. **Build knowledge graph** - Connect validated documents across domains
"""
        return doc

# Example usage
if __name__ == "__main__":
    enforcer = ClaudeSchemaEnforcer()

    # Create example prompt
    sample_text = "Central Solar Atacama generó 150 MW el 15 de febrero de 2025"
    prompt = enforcer.create_extraction_prompt("operaciones", "anexo_01", sample_text)

    print("Schema-Enforced Prompt Preview:")
    print(prompt[:800] + "...")

    # Save template
    template_file = enforcer.save_prompt_template("operaciones", "anexo_01")
    print(f"\nTemplate saved to: {template_file}")

    # Generate integration code
    workflow_path = Path("scripts/eaf_workflows/eaf_processing/chapters/anexo_01_generation_programming")
    integration = enforcer.create_workflow_integration(workflow_path)
    print(f"\nIntegration code length: {len(integration)} characters")