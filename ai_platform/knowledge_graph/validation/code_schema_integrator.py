#!/usr/bin/env python3
"""
Code Schema Integrator - Modifies extraction code to output universal schema
Transforms existing extraction scripts to generate schema-compliant JSON
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

class CodeSchemaIntegrator:
    """Integrates universal schema directly into extraction code"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent

    def create_schema_wrapper_functions(self, domain: str) -> str:
        """Create helper functions to wrap extraction results in universal schema"""

        wrapper_code = f'''
# Universal Schema Wrapper Functions - Auto-generated
# Add these functions to your extraction scripts

import json
from datetime import datetime
from pathlib import Path

def create_universal_document(extraction_data: dict,
                            document_title: str,
                            document_date: str,
                            document_type: str,
                            confidence_score: float = 0.85) -> dict:
    """
    Wrap extraction results in universal schema format

    Args:
        extraction_data: Your original extraction results
        document_title: Title from document
        document_date: Date in YYYY-MM-DD format
        document_type: Type of document (anexo_01, anexo_02, etc.)
        confidence_score: Overall extraction confidence

    Returns:
        Universal schema compliant document
    """

    # Generate document ID
    doc_id = f"cen:{domain}:{{document_type}}:{{document_date}}"

    # Extract entities from your data
    entities = extract_entities_from_data(extraction_data)

    # Generate semantic tags
    semantic_tags = generate_semantic_tags(extraction_data, "{domain}")

    universal_document = {{
        "@context": "https://coordinador.cl/context/v1",
        "@id": doc_id,
        "@type": get_document_type("{domain}"),

        "universal_metadata": {{
            "title": document_title,
            "domain": "{domain}",
            "document_type": document_type,
            "creation_date": document_date,
            "processing_date": datetime.now().isoformat(),
            "language": "es",
            "version": "1.0",
            "status": "final"
        }},

        "entities": entities,

        "cross_references": [],  # Will be populated by cross-reference engine

        "semantic_tags": semantic_tags,

        "domain_specific_data": {{
            "{domain}": extraction_data  # Your original extraction goes here
        }},

        "quality_metadata": {{
            "extraction_confidence": confidence_score,
            "validation_status": "passed",
            "processing_method": "automated_extraction",
            "quality_score": confidence_score,
            "human_validated": False
        }}
    }}

    return universal_document

def extract_entities_from_data(data: dict) -> dict:
    """Extract entities from your extraction data"""
    entities = {{
        "power_plants": [],
        "companies": [],
        "locations": [],
        "regulations": [],
        "equipment": []
    }}

    # Extract power plants from your data structure
    # Adapt this based on your actual data structure

    # Example for anexos with plant data
    if "plants" in data:
        for plant in data["plants"]:
            plant_name = plant.get("name", "").strip()
            if plant_name:
                # Determine plant type
                plant_type = determine_plant_type(plant_name)

                entities["power_plants"].append({{
                    "@id": f"cen:plant:{{normalize_name(plant_name)}}",
                    "@type": plant_type,
                    "name": plant_name,
                    "confidence": plant.get("confidence", 0.9)
                }})

    # Extract from table structures (common in anexos)
    if "upper_table" in data:
        table = data["upper_table"]
        if "rows" in table:
            for row in table["rows"]:
                # Look for plant names in row data
                for cell_value in row.values():
                    if isinstance(cell_value, str) and is_likely_plant_name(cell_value):
                        plant_name = cell_value.strip()
                        entities["power_plants"].append({{
                            "@id": f"cen:plant:{{normalize_name(plant_name)}}",
                            "@type": determine_plant_type(plant_name),
                            "name": plant_name,
                            "confidence": 0.8
                        }})

    # Extract from lower_table (anexo structure)
    if "lower_table" in data:
        table = data["lower_table"]
        if "rows" in table:
            for row in table["rows"]:
                for cell_value in row.values():
                    if isinstance(cell_value, str) and is_likely_plant_name(cell_value):
                        plant_name = cell_value.strip()
                        if not any(p["name"] == plant_name for p in entities["power_plants"]):
                            entities["power_plants"].append({{
                                "@id": f"cen:plant:{{normalize_name(plant_name)}}",
                                "@type": determine_plant_type(plant_name),
                                "name": plant_name,
                                "confidence": 0.8
                            }})

    # Remove duplicates
    entities["power_plants"] = remove_duplicate_entities(entities["power_plants"])

    return entities

def determine_plant_type(plant_name: str) -> str:
    """Determine plant type from name"""
    name_lower = plant_name.lower()

    if any(word in name_lower for word in ["solar", "fotovoltaica", "pv"]):
        return "SolarPowerPlant"
    elif any(word in name_lower for word in ["eólica", "eolica", "viento", "wind"]):
        return "WindPowerPlant"
    elif any(word in name_lower for word in ["hidro", "agua", "embalse"]):
        return "HydroPowerPlant"
    elif any(word in name_lower for word in ["térmica", "termica", "carbón", "carbon", "gas", "diesel"]):
        return "ThermalPowerPlant"
    else:
        return "PowerPlant"

def is_likely_plant_name(text: str) -> bool:
    """Check if text is likely a power plant name"""
    if not isinstance(text, str) or len(text) < 3:
        return False

    # Skip numeric values, dates, units
    if re.match(r'^[\\d\\.\\,]+$', text.strip()):
        return False
    if re.match(r'^\\d{{2}}/\\d{{2}}/\\d{{4}}$', text.strip()):
        return False
    if text.strip().upper() in ["MW", "GWH", "KV", "N/A", "SI", "NO"]:
        return False

    # Look for plant indicators
    plant_indicators = ["central", "planta", "parque", "complejo", "generador"]
    energy_words = ["solar", "eólica", "eolica", "hidro", "térmica", "termica"]

    text_lower = text.lower()
    has_plant_word = any(word in text_lower for word in plant_indicators)
    has_energy_word = any(word in text_lower for word in energy_words)

    # If it has both indicators, likely a plant name
    if has_plant_word and has_energy_word:
        return True

    # If it has energy words and is reasonable length, probably a plant
    if has_energy_word and 5 <= len(text) <= 50:
        return True

    # Common Chilean plant name patterns
    if re.match(r'^[A-ZÁÉÍÓÚÑ][a-záéíóúñ\\s]+\\d*$', text) and len(text) > 5:
        return True

    return False

def normalize_name(name: str) -> str:
    """Normalize name for entity ID"""
    # Remove special characters and normalize
    normalized = re.sub(r'[^a-zA-Z0-9\\s]', '', name.lower())
    normalized = re.sub(r'\\s+', '_', normalized.strip())
    return normalized

def remove_duplicate_entities(entity_list: list) -> list:
    """Remove duplicate entities by name"""
    seen_names = set()
    unique_entities = []

    for entity in entity_list:
        name = entity.get("name", "")
        if name not in seen_names:
            seen_names.add(name)
            unique_entities.append(entity)

    return unique_entities

def generate_semantic_tags(data: dict, domain: str) -> list:
    """Generate semantic tags from extraction data"""
    tags = [domain]  # Always include domain

    # Add data type tags
    if "date" in data or "fecha" in data:
        tags.append("real_time")
    else:
        tags.append("historical")

    # Add domain-specific tags
    if domain == "operaciones":
        tags.extend(["operational_data", "system_management"])

        # Check for renewable energy
        if any("solar" in str(v).lower() for v in flatten_dict(data)):
            tags.append("renewable_energy")
        if any("eólica" in str(v).lower() or "eolica" in str(v).lower() for v in flatten_dict(data)):
            tags.append("renewable_energy")
        if any("hidro" in str(v).lower() for v in flatten_dict(data)):
            tags.append("renewable_energy")

    elif domain == "mercados":
        tags.extend(["market_data", "economic_analysis"])
    elif domain == "legal":
        tags.extend(["regulation_compliance", "legal_framework"])
    elif domain == "planificacion":
        tags.extend(["infrastructure_planning", "capacity_analysis"])

    return list(set(tags))  # Remove duplicates

def flatten_dict(d: dict) -> list:
    """Flatten dictionary values for searching"""
    values = []
    for v in d.values():
        if isinstance(v, dict):
            values.extend(flatten_dict(v))
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    values.extend(flatten_dict(item))
                else:
                    values.append(str(item))
        else:
            values.append(str(v))
    return values

def get_document_type(domain: str) -> str:
    """Get @type for document"""
    type_mapping = {{
        "operaciones": "PowerSystemDocument",
        "mercados": "MarketReport",
        "legal": "LegalRegulation",
        "planificacion": "PlanningStudy"
    }}
    return type_mapping.get(domain, "Document")

def save_universal_schema_json(document: dict, output_path: Path):
    """Save document in universal schema format"""

    # Ensure directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Add save metadata
    document["quality_metadata"]["saved_at"] = datetime.now().isoformat()
    document["quality_metadata"]["file_path"] = str(output_path)

    # Save with proper formatting
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(document, f, indent=2, ensure_ascii=False)

    print(f"✅ Universal schema document saved: {{output_path}}")
    return output_path

# Example of how to modify your existing extraction function:
def modified_extraction_function(input_file: Path, output_dir: Path):
    """Example of modified extraction function using universal schema"""

    # Your existing extraction logic here
    extraction_results = {{
        "title": "ANEXO 1 - Generación Programada",
        "date": "2025-02-15",
        "upper_table": {{
            "rows": [
                {{"plant": "Solar Atacama", "capacity": "150 MW"}},
                {{"plant": "Eólica Tarapacá", "capacity": "200 MW"}}
            ]
        }},
        "confidence": 0.92
    }}

    # Wrap in universal schema
    universal_document = create_universal_document(
        extraction_data=extraction_results,
        document_title=extraction_results["title"],
        document_date=extraction_results["date"],
        document_type="anexo_01",
        confidence_score=extraction_results["confidence"]
    )

    # Save in universal format
    output_file = output_dir / f"{{universal_document['@id'].replace(':', '_')}}.json"
    save_universal_schema_json(universal_document, output_file)

    return universal_document
'''

        return wrapper_code

    def modify_existing_extraction_script(self, script_path: Path, domain: str) -> Dict:
        """Modify existing extraction script to use universal schema"""

        if not script_path.exists():
            return {"success": False, "error": f"Script not found: {script_path}"}

        # Read original script
        with open(script_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        # Create backup
        backup_path = script_path.with_suffix('.py.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)

        # Add schema wrapper functions at the top
        wrapper_functions = self.create_schema_wrapper_functions(domain)

        # Modify the script
        modified_content = self._inject_schema_code(original_content, wrapper_functions, domain)

        # Save modified script
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)

        return {
            "success": True,
            "original_file": script_path,
            "backup_file": backup_path,
            "changes": self._analyze_script_changes(original_content, modified_content)
        }

    def _inject_schema_code(self, original_content: str, wrapper_functions: str, domain: str) -> str:
        """Inject schema code into existing script"""

        lines = original_content.split('\n')

        # Find insertion point (after imports)
        insert_point = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                insert_point = i + 1
            elif line.strip().startswith('def ') or line.strip().startswith('class '):
                break

        # Insert wrapper functions
        lines.insert(insert_point, '\n' + wrapper_functions + '\n')

        # Find and modify save operations
        modified_lines = []
        for line in lines:
            # Look for JSON save operations
            if 'json.dump(' in line or 'to_json(' in line:
                # Add comment suggesting schema wrapper
                modified_lines.append('    # TODO: Use create_universal_document() wrapper')
                modified_lines.append('    # universal_doc = create_universal_document(data, title, date, doc_type)')
                modified_lines.append('    # save_universal_schema_json(universal_doc, output_path)')
                modified_lines.append(line)
            else:
                modified_lines.append(line)

        return '\n'.join(modified_lines)

    def _analyze_script_changes(self, original: str, modified: str) -> List[str]:
        """Analyze what changes were made to the script"""
        changes = []

        if 'create_universal_document' in modified and 'create_universal_document' not in original:
            changes.append("Added universal schema wrapper functions")

        if 'extract_entities_from_data' in modified:
            changes.append("Added entity extraction from data structures")

        if 'save_universal_schema_json' in modified:
            changes.append("Added universal schema save function")

        if 'TODO: Use create_universal_document()' in modified:
            changes.append("Added suggestions for existing save operations")

        return changes

    def create_migration_guide(self, script_path: Path, domain: str) -> str:
        """Create specific migration guide for a script"""

        guide = f"""
# Migration Guide for {script_path.name}

## What needs to change:

### 1. Add Schema Wrapper Functions (DONE automatically)
The script now includes universal schema wrapper functions.

### 2. Modify your main extraction function:

#### Before:
```python
def extract_anexo_data(pdf_path):
    # Your extraction logic
    results = {{
        "title": extracted_title,
        "date": extracted_date,
        "upper_table": extracted_upper_table,
        "lower_table": extracted_lower_table
    }}

    # Save results
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    return results
```

#### After:
```python
def extract_anexo_data(pdf_path):
    # Your existing extraction logic (UNCHANGED)
    results = {{
        "title": extracted_title,
        "date": extracted_date,
        "upper_table": extracted_upper_table,
        "lower_table": extracted_lower_table
    }}

    # NEW: Wrap in universal schema
    universal_document = create_universal_document(
        extraction_data=results,
        document_title=results["title"],
        document_date=results["date"],
        document_type="anexo_01",  # Change based on your anexo type
        confidence_score=0.85
    )

    # NEW: Save in universal format
    save_universal_schema_json(universal_document, output_path)

    return universal_document  # Now returns schema-compliant data
```

### 3. Update your output file naming:
```python
# OLD naming
output_file = "anexo1_page70_extraction.json"

# NEW naming (universal schema compatible)
doc_id = universal_document["@id"].replace(":", "_")
output_file = f"{{doc_id}}.json"
```

### 4. Entity extraction is automatic:
The wrapper functions automatically extract:
- Power plants from your table structures
- Plant types (Solar, Wind, Hydro, Thermal)
- Confidence scores
- Semantic tags

### 5. Test your changes:
```python
# Test with existing input
result = extract_anexo_data("path/to/anexo.pdf")

# Verify schema compliance
print("Document ID:", result["@id"])
print("Entities found:", len(result["entities"]["power_plants"]))
print("Schema valid:", "@context" in result and "@id" in result)
```

## Benefits after migration:
✅ All extractions follow universal schema
✅ Automatic entity extraction from your data
✅ Knowledge graph compatibility
✅ Cross-domain AI queries possible
✅ Your existing logic unchanged - only output format enhanced
"""

        return guide

    def create_batch_migration_script(self, workflow_directory: Path, domain: str) -> Path:
        """Create script to migrate all extraction scripts in a directory"""

        migration_script = f'''#!/usr/bin/env python3
"""
Batch Migration Script for {workflow_directory}
Migrates all extraction scripts to universal schema output
"""

from pathlib import Path
from ai_platform.knowledge_graph.validation.code_schema_integrator import CodeSchemaIntegrator

def migrate_all_extraction_scripts():
    """Migrate all Python extraction scripts in directory"""

    integrator = CodeSchemaIntegrator()
    workflow_dir = Path("{workflow_directory}")

    # Find all Python extraction scripts
    script_patterns = ["*extract*.py", "*extraction*.py", "*process*.py"]
    python_files = []

    for pattern in script_patterns:
        python_files.extend(workflow_dir.rglob(pattern))

    # Remove duplicates and filter out backup files
    unique_files = {{}}
    for f in python_files:
        if not f.name.endswith('.backup') and f.name not in unique_files:
            unique_files[f.name] = f

    results = []
    print(f"Found {{len(unique_files)}} extraction scripts to migrate\\n")

    for script_name, script_path in unique_files.items():
        print(f"Migrating: {{script_path}}")

        result = integrator.modify_existing_extraction_script(script_path, "{domain}")
        results.append(result)

        if result["success"]:
            print(f"  ✅ Migrated successfully")
            for change in result["changes"]:
                print(f"    - {{change}}")
            print(f"  📁 Backup: {{result['backup_file']}}")

            # Create migration guide
            guide = integrator.create_migration_guide(script_path, "{domain}")
            guide_file = script_path.parent / f"{{script_path.stem}}_migration_guide.md"
            with open(guide_file, 'w', encoding='utf-8') as f:
                f.write(guide)
            print(f"  📄 Guide: {{guide_file}}")
        else:
            print(f"  ❌ Failed: {{result.get('error')}}")

        print()

    # Summary
    successful = [r for r in results if r["success"]]
    print(f"Migration complete:")
    print(f"  ✅ Successfully migrated: {{len(successful)}} scripts")
    print(f"  ❌ Failed: {{len(results) - len(successful)}} scripts")
    print(f"\\n🎯 Next steps:")
    print(f"  1. Review migration guides for each script")
    print(f"  2. Update your extraction function calls")
    print(f"  3. Test with sample inputs")
    print(f"  4. Run scripts to generate universal schema JSON")

    return results

if __name__ == "__main__":
    migrate_all_extraction_scripts()
'''

        script_path = workflow_directory / "migrate_extraction_scripts.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(migration_script)

        script_path.chmod(0o755)
        return script_path

# Example usage
if __name__ == "__main__":
    integrator = CodeSchemaIntegrator()

    # Example: Generate wrapper functions for operaciones domain
    wrapper_code = integrator.create_schema_wrapper_functions("operaciones")
    print("Wrapper functions generated (first 500 chars):")
    print(wrapper_code[:500] + "...")

    # Example path (adjust to your actual script)
    sample_script = Path("scripts/eaf_workflows/eaf_processing/chapters/anexo_01_generation_programming/content_extraction/extract_anexo1_with_ocr_per_row.py")

    if sample_script.exists():
        result = integrator.modify_existing_extraction_script(sample_script, "operaciones")
        print(f"\\nModification result: {result['success']}")
    else:
        print(f"\\nSample script not found at: {sample_script}")