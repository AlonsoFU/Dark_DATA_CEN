#!/usr/bin/env python3
"""
Usage Examples - How to apply schema enforcement to existing workflows
Practical examples for immediate implementation
"""

import json
from pathlib import Path
from claude_schema_enforcer import ClaudeSchemaEnforcer
from workflow_integrator import WorkflowIntegrator

def example_1_simple_enforcement():
    """Example 1: Add schema enforcement to a simple extraction"""

    # Your existing extraction result
    legacy_extraction = {
        "title": "ANEXO 1 - Generación Programada",
        "date": "2025-02-15",
        "plants": [
            {"name": "Solar Atacama", "capacity": "150 MW"},
            {"name": "Eólica Tarapacá", "capacity": "200 MW"}
        ],
        "confidence": 0.92
    }

    # Apply schema enforcement
    enforcer = ClaudeSchemaEnforcer()

    # Method 1: Manual wrapping
    universal_document = {
        "@context": "https://coordinador.cl/context/v1",
        "@id": "cen:operaciones:anexo_01:2025-02-15",
        "@type": "PowerSystemDocument",

        "universal_metadata": {
            "title": legacy_extraction["title"],
            "domain": "operaciones",
            "document_type": "anexo_01",
            "creation_date": legacy_extraction["date"],
            "processing_date": "2025-02-15T00:00:00Z",
            "language": "es",
            "version": "1.0",
            "status": "final"
        },

        "entities": {
            "power_plants": [
                {
                    "@id": "cen:plant:solar_atacama",
                    "@type": "SolarPowerPlant",
                    "name": "Solar Atacama",
                    "confidence": 0.95
                },
                {
                    "@id": "cen:plant:eolica_tarapaca",
                    "@type": "WindPowerPlant",
                    "name": "Eólica Tarapacá",
                    "confidence": 0.95
                }
            ]
        },

        "cross_references": [],
        "semantic_tags": ["operaciones", "renewable_energy", "real_time"],

        "domain_specific_data": {
            "operaciones": legacy_extraction  # Your original data here
        },

        "quality_metadata": {
            "extraction_confidence": legacy_extraction["confidence"],
            "validation_status": "pending",
            "processing_method": "manual_enhancement",
            "quality_score": 0.92,
            "human_validated": False
        }
    }

    # Validate the result
    validation = enforcer.validate_claude_response(
        response=json.dumps(universal_document),
        domain="operaciones"
    )

    print("Example 1 - Simple Enforcement:")
    print(f"Valid: {validation['valid']}")
    if validation['errors']:
        print("Errors:", validation['errors'])

    return validation['corrected_document']

def example_2_claude_prompt_enforcement():
    """Example 2: Use schema-enforced prompts with Claude"""

    enforcer = ClaudeSchemaEnforcer()

    # Your document text
    document_text = """
    ANEXO 1 - GENERACIÓN PROGRAMADA
    Fecha: 15 de febrero de 2025

    Central Solar Atacama: 150 MW
    Parque Eólico Tarapacá: 200 MW
    Central Hidroeléctrica Los Andes: 300 MW
    """

    # Create schema-enforced prompt
    extraction_prompt = enforcer.create_extraction_prompt(
        domain="operaciones",
        document_type="anexo_01",
        document_text=document_text,
        additional_context="Extract generation programming data from anexo"
    )

    print("Example 2 - Claude Prompt (first 500 chars):")
    print(extraction_prompt[:500] + "...")

    # Simulate Claude response (in real use, send prompt to Claude)
    simulated_claude_response = {
        "@context": "https://coordinador.cl/context/v1",
        "@id": "cen:operaciones:anexo_01:2025-02-15",
        "@type": "PowerSystemDocument",
        "universal_metadata": {
            "title": "ANEXO 1 - GENERACIÓN PROGRAMADA",
            "domain": "operaciones",
            "document_type": "anexo_01",
            "creation_date": "2025-02-15"
        },
        "entities": {
            "power_plants": [
                {
                    "@id": "cen:plant:solar_atacama",
                    "@type": "SolarPowerPlant",
                    "name": "Solar Atacama",
                    "confidence": 0.95
                }
            ]
        }
    }

    # Validate Claude's response
    validation = enforcer.validate_claude_response(
        response=json.dumps(simulated_claude_response),
        domain="operaciones"
    )

    print(f"Claude response valid: {validation['valid']}")
    return validation['corrected_document']

def example_3_workflow_integration():
    """Example 3: Integrate with existing workflow files"""

    integrator = WorkflowIntegrator()

    # Path to your existing extraction script
    workflow_file = Path("scripts/eaf_workflows/eaf_processing/chapters/anexo_01_generation_programming/content_extraction/extract_anexo1_with_ocr_per_row.py")

    if workflow_file.exists():
        # Enhance the workflow
        result = integrator.enhance_existing_workflow(
            workflow_file=workflow_file,
            domain="operaciones",
            document_type="anexo_01"
        )

        print("Example 3 - Workflow Integration:")
        print(f"Success: {result['success']}")
        if result['success']:
            print("Changes made:")
            for change in result['changes_made']:
                print(f"  - {change}")
            print(f"Backup created: {result['backup_file']}")
    else:
        print("Example 3: Workflow file not found for demonstration")

    return result if workflow_file.exists() else None

def example_4_batch_validation():
    """Example 4: Validate existing JSON files"""

    integrator = WorkflowIntegrator()

    # Check existing extractions
    data_dir = Path("data/documents/anexos_EAF/extractions")

    if data_dir.exists():
        checker_script = integrator.create_validation_checker(data_dir)
        print(f"Example 4 - Batch Validation:")
        print(f"Validation script created: {checker_script}")
        print("Run with: python check_schema_compliance.py")
    else:
        print("Example 4: Data directory not found for demonstration")

    return checker_script if data_dir.exists() else None

def example_5_complete_integration():
    """Example 5: Complete integration in a new extraction function"""

    def extract_with_universal_schema(pdf_path: Path, domain: str, doc_type: str):
        """Complete extraction function with schema enforcement"""

        # 1. Extract text (your existing logic)
        # document_text = extract_text_from_pdf(pdf_path)

        # 2. Create schema-enforced prompt
        enforcer = ClaudeSchemaEnforcer()
        extraction_prompt = enforcer.create_extraction_prompt(
            domain=domain,
            document_type=doc_type,
            document_text="Your extracted text here",
            additional_context="Extract data maintaining universal schema compliance"
        )

        # 3. Send to Claude (replace with your Claude API call)
        # claude_response = your_claude_api_call(extraction_prompt)

        # 4. Validate response
        claude_response = '{"@context": "https://coordinador.cl/context/v1", "@id": "cen:operaciones:anexo_01:2025-02-15"}'  # Simulated

        validation = enforcer.validate_claude_response(
            response=claude_response,
            domain=domain,
            strict_mode=False
        )

        # 5. Return validated result
        if validation['valid']:
            return validation['corrected_document']
        else:
            print("Validation errors:", validation['errors'])
            return validation['corrected_document']  # Use corrected version

    print("Example 5 - Complete Integration Function Created")
    return extract_with_universal_schema

def main():
    """Run all examples"""

    print("=== Schema Enforcement Usage Examples ===\n")

    # Example 1: Simple enforcement
    result1 = example_1_simple_enforcement()
    print(f"✅ Example 1 completed\n")

    # Example 2: Claude prompt enforcement
    result2 = example_2_claude_prompt_enforcement()
    print(f"✅ Example 2 completed\n")

    # Example 3: Workflow integration
    result3 = example_3_workflow_integration()
    print(f"✅ Example 3 completed\n")

    # Example 4: Batch validation
    result4 = example_4_batch_validation()
    print(f"✅ Example 4 completed\n")

    # Example 5: Complete integration
    result5 = example_5_complete_integration()
    print(f"✅ Example 5 completed\n")

    print("=== Summary ===")
    print("All examples demonstrate different levels of schema enforcement:")
    print("1. Manual wrapping of existing extractions")
    print("2. Schema-enforced prompts for Claude")
    print("3. Automatic workflow enhancement")
    print("4. Batch validation of existing files")
    print("5. Complete integration for new workflows")

if __name__ == "__main__":
    main()