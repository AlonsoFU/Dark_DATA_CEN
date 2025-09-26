#!/usr/bin/env python3
"""
Migrate ANEXO Scripts - Practical migration for your existing extraction scripts
Adds universal schema output to your current ANEXO extraction code
"""

import json
from pathlib import Path
from code_schema_integrator import CodeSchemaIntegrator

class AnexoScriptMigrator:
    """Specifically for migrating your ANEXO extraction scripts"""

    def __init__(self):
        self.integrator = CodeSchemaIntegrator()
        self.project_root = Path(__file__).parent.parent.parent.parent

    def find_anexo_scripts(self) -> dict:
        """Find all your existing ANEXO extraction scripts"""

        anexo_scripts = {
            "anexo_01": [],
            "anexo_02": [],
            "informe_diario": []
        }

        # Look in EAF workflows directory
        eaf_dir = self.project_root / "scripts" / "eaf_workflows" / "eaf_processing" / "chapters"

        if eaf_dir.exists():
            # ANEXO 1 scripts
            anexo1_dir = eaf_dir / "anexo_01_generation_programming"
            if anexo1_dir.exists():
                anexo_scripts["anexo_01"] = list(anexo1_dir.rglob("*extract*.py"))

            # ANEXO 2 scripts
            anexo2_dir = eaf_dir / "anexo_02_real_generation"
            if anexo2_dir.exists():
                anexo_scripts["anexo_02"] = list(anexo2_dir.rglob("*extract*.py"))

            # Daily reports
            daily_dir = eaf_dir / "informe_diario_day1"
            if daily_dir.exists():
                anexo_scripts["informe_diario"] = list(daily_dir.rglob("*extract*.py"))

        return anexo_scripts

    def migrate_specific_anexo_script(self, script_path: Path, anexo_type: str) -> dict:
        """Migrate a specific ANEXO script with anexo-specific logic"""

        # Read the original script
        with open(script_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        # Create anexo-specific wrapper
        anexo_wrapper = self.create_anexo_specific_wrapper(anexo_type)

        # Create backup
        backup_path = script_path.with_suffix('.py.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)

        # Add wrapper functions to the script
        enhanced_content = self._inject_anexo_wrapper(original_content, anexo_wrapper, anexo_type)

        # Save enhanced script
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(enhanced_content)

        # Create specific migration instructions
        instructions = self.create_anexo_migration_instructions(script_path, anexo_type)
        instructions_file = script_path.parent / f"{script_path.stem}_MIGRATION_INSTRUCTIONS.md"
        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write(instructions)

        return {
            "success": True,
            "script": script_path,
            "backup": backup_path,
            "instructions": instructions_file,
            "anexo_type": anexo_type
        }

    def create_anexo_specific_wrapper(self, anexo_type: str) -> str:
        """Create anexo-specific wrapper functions"""

        if anexo_type == "anexo_01":
            wrapper = '''
# ANEXO 1 Universal Schema Wrapper
def wrap_anexo1_extraction(extraction_results: dict) -> dict:
    """Convert ANEXO 1 extraction to universal schema"""

    # Extract metadata from your existing structure
    title = extraction_results.get("title", "ANEXO 1 - Generación Programada")
    date = extraction_results.get("date", extraction_results.get("fecha", "2025-02-15"))

    # Create universal document
    universal_doc = create_universal_document(
        extraction_data=extraction_results,
        document_title=title,
        document_date=date,
        document_type="anexo_01_generation_programming",
        domain="operaciones",
        confidence_score=extraction_results.get("confidence", 0.85)
    )

    return universal_doc

def extract_anexo1_entities(data: dict) -> dict:
    """Extract entities specific to ANEXO 1 structure"""
    entities = {"power_plants": [], "companies": [], "locations": [], "regulations": [], "equipment": []}

    # Extract from upper table (generation programming)
    if "upper_table" in data and "rows" in data["upper_table"]:
        for row in data["upper_table"]["rows"]:
            # Look for plant names in common ANEXO 1 fields
            plant_name = None
            for field in ["central", "planta", "generador", "unidad"]:
                if field in row and row[field] and isinstance(row[field], str):
                    potential_name = row[field].strip()
                    if len(potential_name) > 3 and not potential_name.replace(".", "").isdigit():
                        plant_name = potential_name
                        break

            if plant_name:
                entities["power_plants"].append({
                    "@id": f"cen:plant:{normalize_name(plant_name)}",
                    "@type": determine_plant_type(plant_name),
                    "name": plant_name,
                    "confidence": 0.9,
                    "metadata": {
                        "anexo_source": "upper_table",
                        "generation_programming": True
                    }
                })

    # Extract from lower table if exists
    if "lower_table" in data and "rows" in data["lower_table"]:
        for row in data["lower_table"]["rows"]:
            for field in ["central", "planta", "generador"]:
                if field in row and row[field] and isinstance(row[field], str):
                    potential_name = row[field].strip()
                    if len(potential_name) > 3 and not potential_name.replace(".", "").isdigit():
                        # Check if not already added
                        if not any(p["name"] == potential_name for p in entities["power_plants"]):
                            entities["power_plants"].append({
                                "@id": f"cen:plant:{normalize_name(potential_name)}",
                                "@type": determine_plant_type(potential_name),
                                "name": potential_name,
                                "confidence": 0.85,
                                "metadata": {
                                    "anexo_source": "lower_table",
                                    "generation_programming": True
                                }
                            })

    return entities
'''

        elif anexo_type == "anexo_02":
            wrapper = '''
# ANEXO 2 Universal Schema Wrapper
def wrap_anexo2_extraction(extraction_results: dict) -> dict:
    """Convert ANEXO 2 extraction to universal schema"""

    title = extraction_results.get("title", "ANEXO 2 - Generación Real")
    date = extraction_results.get("date", extraction_results.get("fecha", "2025-02-15"))

    universal_doc = create_universal_document(
        extraction_data=extraction_results,
        document_title=title,
        document_date=date,
        document_type="anexo_02_real_generation",
        domain="operaciones",
        confidence_score=extraction_results.get("confidence", 0.85)
    )

    return universal_doc

def extract_anexo2_entities(data: dict) -> dict:
    """Extract entities specific to ANEXO 2 real generation structure"""
    entities = {"power_plants": [], "companies": [], "locations": [], "regulations": [], "equipment": []}

    # ANEXO 2 has real generation data
    for table_key in ["upper_table", "lower_table", "plant_data", "generation_data"]:
        if table_key in data and "rows" in data[table_key]:
            for row in data[table_key]["rows"]:
                # Look for plant names
                plant_name = None
                for field in ["central", "planta", "plant_name", "nombre", "generador"]:
                    if field in row and row[field] and isinstance(row[field], str):
                        potential_name = row[field].strip()
                        if len(potential_name) > 3 and not potential_name.replace(".", "").isdigit():
                            plant_name = potential_name
                            break

                if plant_name and not any(p["name"] == plant_name for p in entities["power_plants"]):
                    entities["power_plants"].append({
                        "@id": f"cen:plant:{normalize_name(plant_name)}",
                        "@type": determine_plant_type(plant_name),
                        "name": plant_name,
                        "confidence": 0.9,
                        "metadata": {
                            "anexo_source": table_key,
                            "real_generation": True
                        }
                    })

    return entities
'''

        elif anexo_type == "informe_diario":
            wrapper = '''
# Informe Diario Universal Schema Wrapper
def wrap_informe_diario_extraction(extraction_results: dict) -> dict:
    """Convert daily report extraction to universal schema"""

    title = extraction_results.get("title", "Informe Diario Operacional")
    date = extraction_results.get("date", extraction_results.get("fecha", "2025-02-15"))

    universal_doc = create_universal_document(
        extraction_data=extraction_results,
        document_title=title,
        document_date=date,
        document_type="informe_diario_operacional",
        domain="operaciones",
        confidence_score=extraction_results.get("confidence", 0.80)
    )

    # Add daily report specific semantic tags
    universal_doc["semantic_tags"].extend(["daily_report", "operational_status", "real_time"])

    return universal_doc

def extract_informe_diario_entities(data: dict) -> dict:
    """Extract entities from daily operational report"""
    entities = {"power_plants": [], "companies": [], "locations": [], "regulations": [], "equipment": []}

    # Daily reports can have multiple data sections
    for section_key in data:
        if isinstance(data[section_key], dict) and "rows" in data[section_key]:
            for row in data[section_key]["rows"]:
                # Look for equipment and plant names
                for field_name, field_value in row.items():
                    if isinstance(field_value, str) and len(field_value) > 3:
                        # Check if it looks like equipment
                        if any(keyword in field_value.lower() for keyword in ["transformador", "interruptor", "línea", "subestación"]):
                            entities["equipment"].append({
                                "@id": f"cen:equipment:{normalize_name(field_value)}",
                                "@type": "Equipment",
                                "name": field_value.strip(),
                                "confidence": 0.75
                            })
                        # Check if it looks like a plant
                        elif any(keyword in field_value.lower() for keyword in ["central", "planta", "generador"]):
                            entities["power_plants"].append({
                                "@id": f"cen:plant:{normalize_name(field_value)}",
                                "@type": determine_plant_type(field_value),
                                "name": field_value.strip(),
                                "confidence": 0.80
                            })

    return entities
'''

        else:
            # Generic wrapper
            wrapper = '''
# Generic ANEXO Universal Schema Wrapper
def wrap_anexo_extraction(extraction_results: dict, anexo_type: str) -> dict:
    """Convert any ANEXO extraction to universal schema"""

    title = extraction_results.get("title", f"ANEXO {anexo_type.upper()}")
    date = extraction_results.get("date", extraction_results.get("fecha", "2025-02-15"))

    universal_doc = create_universal_document(
        extraction_data=extraction_results,
        document_title=title,
        document_date=date,
        document_type=f"anexo_{anexo_type}",
        domain="operaciones",
        confidence_score=extraction_results.get("confidence", 0.80)
    )

    return universal_doc
'''

        return wrapper

    def _inject_anexo_wrapper(self, original_content: str, wrapper_functions: str, anexo_type: str) -> str:
        """Inject anexo-specific wrapper into script"""

        lines = original_content.split('\n')

        # Find insertion point after imports
        insert_point = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                insert_point = i + 1
            elif line.strip().startswith('def ') or line.strip().startswith('class '):
                break

        # Insert the universal schema helper functions first
        universal_helpers = self.integrator.create_schema_wrapper_functions("operaciones")
        lines.insert(insert_point, '\n' + universal_helpers)

        # Then insert anexo-specific wrapper
        lines.insert(insert_point + 1, '\n' + wrapper_functions + '\n')

        # Add usage example at the end
        usage_example = f'''

# USAGE EXAMPLE - Add this to your main extraction function:
#
# def your_extraction_function(input_file):
#     # Your existing extraction logic
#     results = your_existing_extraction_logic()
#
#     # NEW: Wrap in universal schema
#     universal_doc = wrap_{anexo_type}_extraction(results)
#
#     # NEW: Save universal format
#     output_path = Path(f"output/{{universal_doc['@id'].replace(':', '_')}}.json")
#     save_universal_schema_json(universal_doc, output_path)
#
#     return universal_doc
'''

        lines.append(usage_example)

        return '\n'.join(lines)

    def create_anexo_migration_instructions(self, script_path: Path, anexo_type: str) -> str:
        """Create specific migration instructions for an anexo script"""

        instructions = f"""
# Migration Instructions for {script_path.name}

## ✅ COMPLETED AUTOMATICALLY:
- Added universal schema helper functions
- Added {anexo_type.upper()}-specific wrapper functions
- Created backup at {script_path.stem}.py.backup

## 🔧 MANUAL CHANGES NEEDED:

### 1. Find your main extraction function
Look for a function like:
```python
def extract_{anexo_type}_data(pdf_path: Path):
    # Your extraction logic here
    results = {{
        "title": "...",
        "date": "...",
        "upper_table": {{...}},
        "lower_table": {{...}}
    }}

    # Old save
    with open(output_path, 'w') as f:
        json.dump(results, f)

    return results
```

### 2. Replace the save logic with:
```python
def extract_{anexo_type}_data(pdf_path: Path):
    # Your extraction logic (UNCHANGED!)
    results = {{
        "title": "...",
        "date": "...",
        "upper_table": {{...}},
        "lower_table": {{...}}
    }}

    # NEW: Universal schema wrapper
    universal_doc = wrap_{anexo_type}_extraction(results)

    # NEW: Save in universal format
    output_path = Path(f"output/{{universal_doc['@id'].replace(':', '_')}}.json")
    save_universal_schema_json(universal_doc, output_path)

    return universal_doc  # Now returns schema-compliant data!
```

### 3. Update any scripts that call this function:
```python
# Before
result = extract_{anexo_type}_data(pdf_path)
plant_count = len(result["upper_table"]["rows"])

# After
result = extract_{anexo_type}_data(pdf_path)
plant_count = len(result["entities"]["power_plants"])  # Entities now extracted automatically!
original_data = result["domain_specific_data"]["operaciones"]  # Your original data is here
```

## 🎯 BENEFITS AFTER MIGRATION:

### ✅ Automatic Entity Extraction:
Your {anexo_type.upper()} extraction will now automatically extract:
- Power plant names from table structures
- Plant types (Solar/Wind/Hydro/Thermal)
- Company names
- Equipment mentions

### ✅ Universal Schema Compliance:
- Document ID: `cen:operaciones:{anexo_type}_...:2025-02-15`
- JSON-LD format for knowledge graph
- Cross-reference compatibility
- AI-queryable structure

### ✅ Preserved Original Data:
Your original extraction is preserved in:
`result["domain_specific_data"]["operaciones"]`

## 🧪 TESTING:

1. Run your script with a sample input
2. Check the output JSON has these fields:
   - `@context`, `@id`, `@type`
   - `universal_metadata`
   - `entities` (with automatically extracted plants/companies)
   - `domain_specific_data.operaciones` (your original data)

3. Verify entity extraction worked:
```python
result = extract_{anexo_type}_data("sample.pdf")
print(f"Plants found: {{len(result['entities']['power_plants'])}}")
for plant in result['entities']['power_plants']:
    print(f"- {{plant['name']}} ({{plant['@type']}})")
```

## 📞 Need Help?
Check the usage examples at the end of your script file.
"""

        return instructions

    def migrate_all_anexo_scripts(self) -> dict:
        """Migrate all found ANEXO scripts"""

        scripts = self.find_anexo_scripts()
        results = {
            "total_found": 0,
            "total_migrated": 0,
            "migrations": []
        }

        for anexo_type, script_list in scripts.items():
            for script_path in script_list:
                results["total_found"] += 1

                try:
                    migration_result = self.migrate_specific_anexo_script(script_path, anexo_type)
                    results["migrations"].append(migration_result)
                    results["total_migrated"] += 1

                    print(f"✅ Migrated: {script_path}")
                    print(f"   Backup: {migration_result['backup']}")
                    print(f"   Instructions: {migration_result['instructions']}")

                except Exception as e:
                    print(f"❌ Failed to migrate {script_path}: {e}")
                    results["migrations"].append({
                        "success": False,
                        "script": script_path,
                        "error": str(e),
                        "anexo_type": anexo_type
                    })

        return results

def main():
    """Run the ANEXO script migration"""

    print("🚀 ANEXO Scripts Universal Schema Migration")
    print("="*50)

    migrator = AnexoScriptMigrator()

    # Find scripts
    scripts = migrator.find_anexo_scripts()
    total_scripts = sum(len(script_list) for script_list in scripts.values())

    print(f"📁 Found {total_scripts} ANEXO extraction scripts:")
    for anexo_type, script_list in scripts.items():
        print(f"  {anexo_type}: {len(script_list)} scripts")
        for script in script_list:
            print(f"    - {script.name}")

    if total_scripts == 0:
        print("❌ No ANEXO extraction scripts found.")
        print("   Check the paths in find_anexo_scripts()")
        return

    # Migrate all
    input("Press Enter to proceed with migration...")

    results = migrator.migrate_all_anexo_scripts()

    print(f"\n🎉 Migration Summary:")
    print(f"   📊 Found: {results['total_found']} scripts")
    print(f"   ✅ Migrated: {results['total_migrated']} scripts")
    print(f"   ❌ Failed: {results['total_found'] - results['total_migrated']} scripts")

    print(f"\n📋 Next Steps:")
    print(f"   1. Review the *_MIGRATION_INSTRUCTIONS.md files")
    print(f"   2. Update your main extraction functions as shown")
    print(f"   3. Test with sample inputs")
    print(f"   4. All output will now be universal schema compliant!")

if __name__ == "__main__":
    main()