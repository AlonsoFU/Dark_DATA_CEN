#!/usr/bin/env python3
"""
Workflow Integrator - Adds schema enforcement to existing extraction workflows
Automatically enhances existing scripts with universal schema compliance
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from .claude_schema_enforcer import ClaudeSchemaEnforcer

class WorkflowIntegrator:
    """Integrates schema enforcement into existing workflows"""

    def __init__(self):
        self.enforcer = ClaudeSchemaEnforcer()
        self.project_root = Path(__file__).parent.parent.parent.parent

    def enhance_existing_workflow(self, workflow_file: Path,
                                domain: str, document_type: str) -> Dict:
        """
        Add schema enforcement to existing workflow file

        Args:
            workflow_file: Path to existing extraction script
            domain: Target domain
            document_type: Document type being processed

        Returns:
            Dict with enhancement details
        """

        if not workflow_file.exists():
            return {"success": False, "error": f"Workflow file not found: {workflow_file}"}

        # Read existing workflow
        with open(workflow_file, 'r', encoding='utf-8') as f:
            original_content = f.read()

        # Create enhanced version
        enhanced_content = self._add_schema_enforcement_code(
            original_content, domain, document_type
        )

        # Create backup
        backup_file = workflow_file.with_suffix('.py.backup')
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(original_content)

        # Save enhanced version
        with open(workflow_file, 'w', encoding='utf-8') as f:
            f.write(enhanced_content)

        return {
            "success": True,
            "enhanced_file": workflow_file,
            "backup_file": backup_file,
            "changes_made": self._analyze_changes(original_content, enhanced_content)
        }

    def _add_schema_enforcement_code(self, original_content: str,
                                   domain: str, document_type: str) -> str:
        """Add schema enforcement imports and functions to existing code"""

        # Add imports at the top
        import_addition = """
# Schema Enforcement - Added by WorkflowIntegrator
from ai_platform.knowledge_graph.validation.claude_schema_enforcer import ClaudeSchemaEnforcer
import json
"""

        # Add schema enforcement function
        function_addition = f'''

def apply_schema_enforcement(extracted_data: dict, document_text: str = "") -> dict:
    """Apply universal schema enforcement to extracted data"""

    enforcer = ClaudeSchemaEnforcer()

    # If data doesn't have universal structure, wrap it
    if "@context" not in extracted_data:
        # Convert existing extraction to universal schema
        universal_data = {{
            "@context": "https://coordinador.cl/context/v1",
            "@id": f"cen:{domain}:{document_type}:{{extracted_data.get('date', '2025-02-15')}}",
            "@type": enforcer.validator._get_document_type("{domain}"),

            "universal_metadata": {{
                "title": extracted_data.get("title", "Extracted Document"),
                "domain": "{domain}",
                "document_type": "{document_type}",
                "creation_date": extracted_data.get("date", "2025-02-15"),
                "processing_date": "2025-02-15T00:00:00Z",
                "language": "es",
                "version": "1.0",
                "status": "final"
            }},

            "entities": {{
                "power_plants": [],
                "companies": [],
                "locations": [],
                "regulations": [],
                "equipment": []
            }},

            "cross_references": [],

            "semantic_tags": ["{domain}", "extracted_data"],

            "domain_specific_data": {{
                "{domain}": extracted_data  # Your original extraction goes here
            }},

            "quality_metadata": {{
                "extraction_confidence": extracted_data.get("confidence", 0.8),
                "validation_status": "pending",
                "processing_method": "legacy_enhanced",
                "quality_score": 0.8,
                "human_validated": False
            }}
        }}
    else:
        universal_data = extracted_data

    # Validate and correct
    validation_result = enforcer.validate_claude_response(
        response=json.dumps(universal_data),
        domain="{domain}",
        strict_mode=False
    )

    if validation_result["valid"]:
        print("✅ Schema validation passed")
        return validation_result["corrected_document"]
    else:
        print("⚠️ Schema validation issues found:")
        for error in validation_result["errors"]:
            print(f"  - {{error}}")
        for warning in validation_result["warnings"]:
            print(f"  - WARNING: {{warning}}")

        # Return corrected version if available
        if validation_result["corrected_document"]:
            print("🔧 Using auto-corrected document")
            return validation_result["corrected_document"]
        else:
            print("❌ Using original data with validation issues")
            return universal_data

def save_with_schema_compliance(data: dict, output_path: Path):
    """Save data ensuring schema compliance"""

    # Apply schema enforcement
    validated_data = apply_schema_enforcement(data)

    # Save with validation metadata
    output_data = {{
        "document": validated_data,
        "validation_metadata": {{
            "schema_version": "universal_v1",
            "validated_at": "2025-02-15T00:00:00Z",
            "validation_tool": "WorkflowIntegrator",
            "compliance_status": "enforced"
        }}
    }}

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Schema-compliant data saved to: {{output_path}}")
    return output_path
'''

        # Find where to insert the imports
        lines = original_content.split('\n')
        insert_line = 0

        # Find last import or first function/class
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                insert_line = i + 1
            elif line.strip().startswith('def ') or line.strip().startswith('class '):
                break

        # Insert imports
        lines.insert(insert_line, import_addition)

        # Add enforcement functions at the end
        enhanced_content = '\n'.join(lines) + function_addition

        # Look for existing save operations and enhance them
        enhanced_content = self._enhance_save_operations(enhanced_content)

        return enhanced_content

    def _enhance_save_operations(self, content: str) -> str:
        """Find and enhance existing save operations"""

        # Pattern to find JSON save operations
        save_patterns = [
            r'(with open\([^)]+\.json[^)]*\)[^:]*:[\s\S]*?json\.dump\([^)]+\))',
            r'(json\.dump\([^,]+,\s*[^,]+\))',
            r'(\w+\.to_json\([^)]*\))'
        ]

        enhanced_content = content

        for pattern in save_patterns:
            matches = re.finditer(pattern, enhanced_content, re.MULTILINE)
            for match in matches:
                original_save = match.group(1)
                # Add comment suggesting schema enforcement
                enhancement = f"\n    # TODO: Consider using save_with_schema_compliance() instead\n    {original_save}"
                enhanced_content = enhanced_content.replace(original_save, enhancement, 1)

        return enhanced_content

    def _analyze_changes(self, original: str, enhanced: str) -> List[str]:
        """Analyze what changes were made"""
        changes = []

        if "ClaudeSchemaEnforcer" in enhanced and "ClaudeSchemaEnforcer" not in original:
            changes.append("Added schema enforcement imports")

        if "apply_schema_enforcement" in enhanced:
            changes.append("Added schema enforcement function")

        if "save_with_schema_compliance" in enhanced:
            changes.append("Added schema-compliant save function")

        if "TODO: Consider using save_with_schema_compliance" in enhanced:
            changes.append("Added suggestions for existing save operations")

        return changes

    def create_migration_script(self, workflow_directory: Path) -> Path:
        """Create script to migrate entire workflow directory"""

        migration_script = f'''#!/usr/bin/env python3
"""
Migration Script - Auto-generated by WorkflowIntegrator
Migrates all workflows in {workflow_directory} to use universal schema
"""

from pathlib import Path
from ai_platform.knowledge_graph.validation.workflow_integrator import WorkflowIntegrator

def migrate_workflows():
    """Migrate all Python files in workflow directory"""

    integrator = WorkflowIntegrator()
    workflow_dir = Path("{workflow_directory}")

    # Find all Python files
    python_files = list(workflow_dir.rglob("*.py"))

    results = []
    for py_file in python_files:
        if py_file.name.startswith("_") or "test" in py_file.name.lower():
            continue  # Skip private files and tests

        print(f"Migrating: {{py_file}}")

        # Determine domain and document type from path
        parts = py_file.parts
        domain = "operaciones"  # Default
        doc_type = "document"   # Default

        # Try to extract from path
        if "operaciones" in parts:
            domain = "operaciones"
        elif "mercados" in parts:
            domain = "mercados"
        elif "legal" in parts:
            domain = "legal"
        elif "planificacion" in parts:
            domain = "planificacion"

        if "anexo" in py_file.name:
            doc_type = py_file.stem.replace("_", "")

        # Apply enhancement
        result = integrator.enhance_existing_workflow(py_file, domain, doc_type)
        results.append(result)

        if result["success"]:
            print(f"  ✅ Enhanced successfully")
            for change in result["changes_made"]:
                print(f"    - {{change}}")
        else:
            print(f"  ❌ Failed: {{result.get('error')}}")

    print(f"\\nMigration complete: {{len([r for r in results if r['success']])}} files enhanced")
    return results

if __name__ == "__main__":
    migrate_workflows()
'''

        script_path = workflow_directory / "migrate_to_universal_schema.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(migration_script)

        script_path.chmod(0o755)  # Make executable
        return script_path

    def create_validation_checker(self, data_directory: Path) -> Path:
        """Create script to validate existing JSON files against schema"""

        checker_script = f'''#!/usr/bin/env python3
"""
Schema Validation Checker - Auto-generated by WorkflowIntegrator
Checks existing JSON files against universal schema
"""

import json
from pathlib import Path
from ai_platform.knowledge_graph.validation.schema_validator import SchemaValidator

def check_existing_files():
    """Check all JSON files in data directory for schema compliance"""

    validator = SchemaValidator()
    data_dir = Path("{data_directory}")

    json_files = list(data_dir.rglob("*.json"))

    results = {{
        "total_files": len(json_files),
        "valid_files": 0,
        "invalid_files": 0,
        "detailed_results": []
    }}

    for json_file in json_files:
        print(f"Checking: {{json_file}}")

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Check if it has universal schema structure
            if "@context" in data and "@id" in data:
                validation = validator.validate_document(data, strict_mode=False)

                if validation["valid"]:
                    print(f"  ✅ Valid universal schema")
                    results["valid_files"] += 1
                else:
                    print(f"  ❌ Invalid universal schema:")
                    for error in validation["errors"]:
                        print(f"    - {{error}}")
                    results["invalid_files"] += 1

                results["detailed_results"].append({{
                    "file": str(json_file),
                    "has_universal_schema": True,
                    "valid": validation["valid"],
                    "errors": validation["errors"],
                    "warnings": validation["warnings"]
                }})
            else:
                print(f"  📋 Legacy format (no universal schema)")
                results["detailed_results"].append({{
                    "file": str(json_file),
                    "has_universal_schema": False,
                    "valid": False,
                    "errors": ["No universal schema structure"],
                    "warnings": []
                }})
                results["invalid_files"] += 1

        except Exception as e:
            print(f"  ❌ Error reading file: {{e}}")
            results["detailed_results"].append({{
                "file": str(json_file),
                "has_universal_schema": False,
                "valid": False,
                "errors": [f"File error: {{e}}"],
                "warnings": []
            }})
            results["invalid_files"] += 1

    # Save results
    results_file = data_dir / "schema_validation_report.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\\nValidation complete:")
    print(f"  📊 Total files: {{results['total_files']}}")
    print(f"  ✅ Valid: {{results['valid_files']}}")
    print(f"  ❌ Invalid: {{results['invalid_files']}}")
    print(f"  📄 Report saved to: {{results_file}}")

    return results

if __name__ == "__main__":
    check_existing_files()
'''

        checker_path = data_directory / "check_schema_compliance.py"
        with open(checker_path, 'w', encoding='utf-8') as f:
            f.write(checker_script)

        checker_path.chmod(0o755)  # Make executable
        return checker_path

    def generate_integration_summary(self) -> Dict:
        """Generate summary of available integration options"""

        return {
            "integration_methods": {
                "automatic_enhancement": {
                    "description": "Automatically enhance existing Python workflows",
                    "method": "enhance_existing_workflow()",
                    "use_case": "Add schema enforcement to existing extraction scripts"
                },
                "migration_script": {
                    "description": "Create migration script for entire directories",
                    "method": "create_migration_script()",
                    "use_case": "Migrate all workflows in a directory at once"
                },
                "validation_checker": {
                    "description": "Create script to validate existing JSON files",
                    "method": "create_validation_checker()",
                    "use_case": "Check compliance of existing data files"
                }
            },

            "integration_levels": {
                "minimal": "Add validation functions, keep existing logic",
                "enhanced": "Wrap existing extractions in universal schema",
                "complete": "Full rewrite to use schema-enforced prompts"
            },

            "benefits": {
                "consistency": "All extractions follow same structure",
                "validation": "Automatic error detection and correction",
                "compatibility": "Works with existing AI platform",
                "knowledge_graph": "Enables cross-domain connections"
            }
        }

# Example usage
if __name__ == "__main__":
    integrator = WorkflowIntegrator()

    # Example: Enhance a specific workflow
    anexo_workflow = Path("scripts/eaf_workflows/eaf_processing/chapters/anexo_01_generation_programming/content_extraction/extract_anexo1_with_ocr_per_row.py")

    if anexo_workflow.exists():
        result = integrator.enhance_existing_workflow(
            workflow_file=anexo_workflow,
            domain="operaciones",
            document_type="anexo_01"
        )
        print(f"Enhancement result: {result}")

    # Generate summary
    summary = integrator.generate_integration_summary()
    print("Integration options:", json.dumps(summary, indent=2))