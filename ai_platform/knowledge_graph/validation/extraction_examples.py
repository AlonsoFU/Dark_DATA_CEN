#!/usr/bin/env python3
"""
Extraction Examples - Before and After Universal Schema Integration
Shows exactly how to modify existing extraction code
"""

import json
from pathlib import Path
from datetime import datetime

# ============================================================================
# BEFORE: Your existing extraction code (example)
# ============================================================================

def old_anexo_extraction(pdf_path: Path) -> dict:
    """Example of your existing extraction function - BEFORE schema integration"""

    # Your existing logic
    extracted_data = {
        "title": "ANEXO 1 - Generación Programada",
        "date": "2025-02-15",
        "upper_table": {
            "headers": ["Central", "Potencia MW", "Energía GWh"],
            "rows": [
                {"central": "Solar Atacama", "potencia": "150", "energia": "360"},
                {"central": "Eólica Tarapacá", "potencia": "200", "energia": "480"}
            ]
        },
        "lower_table": {
            "headers": ["Empresa", "Total MW"],
            "rows": [
                {"empresa": "Energías Renovables S.A.", "total": "350"}
            ]
        },
        "confidence": 0.92
    }

    # Your existing save logic
    output_path = Path("output/anexo1_extraction.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, indent=2, ensure_ascii=False)

    return extracted_data

# ============================================================================
# AFTER: Modified extraction code with universal schema
# ============================================================================

def create_universal_document(extraction_data: dict,
                            document_title: str,
                            document_date: str,
                            document_type: str,
                            domain: str = "operaciones",
                            confidence_score: float = 0.85) -> dict:
    """Convert extraction results to universal schema format"""

    # Generate document ID
    doc_id = f"cen:{domain}:{document_type}:{document_date}"

    # Extract entities from your existing data structure
    entities = extract_entities_from_extraction_data(extraction_data)

    # Generate semantic tags
    semantic_tags = generate_semantic_tags_from_data(extraction_data, domain)

    universal_document = {
        "@context": "https://coordinador.cl/context/v1",
        "@id": doc_id,
        "@type": get_document_type(domain),

        "universal_metadata": {
            "title": document_title,
            "domain": domain,
            "document_type": document_type,
            "creation_date": document_date,
            "processing_date": datetime.now().isoformat(),
            "language": "es",
            "version": "1.0",
            "status": "final"
        },

        "entities": entities,
        "cross_references": [],
        "semantic_tags": semantic_tags,

        "domain_specific_data": {
            domain: extraction_data  # Your original extraction preserved here
        },

        "quality_metadata": {
            "extraction_confidence": confidence_score,
            "validation_status": "passed",
            "processing_method": "automated_extraction",
            "quality_score": confidence_score,
            "human_validated": False
        }
    }

    return universal_document

def extract_entities_from_extraction_data(data: dict) -> dict:
    """Extract entities from your existing extraction data structure"""

    entities = {
        "power_plants": [],
        "companies": [],
        "locations": [],
        "regulations": [],
        "equipment": []
    }

    # Extract from upper_table (anexo structure)
    if "upper_table" in data and "rows" in data["upper_table"]:
        for row in data["upper_table"]["rows"]:
            # Look for plant names in different possible field names
            plant_name = None
            for field in ["central", "planta", "plant", "nombre"]:
                if field in row and row[field]:
                    plant_name = row[field].strip()
                    break

            if plant_name:
                entities["power_plants"].append({
                    "@id": f"cen:plant:{normalize_name(plant_name)}",
                    "@type": determine_plant_type(plant_name),
                    "name": plant_name,
                    "confidence": 0.9
                })

    # Extract from lower_table
    if "lower_table" in data and "rows" in data["lower_table"]:
        for row in data["lower_table"]["rows"]:
            # Look for company names
            company_name = None
            for field in ["empresa", "company", "compañia"]:
                if field in row and row[field]:
                    company_name = row[field].strip()
                    break

            if company_name:
                entities["companies"].append({
                    "@id": f"cen:company:{normalize_name(company_name)}",
                    "@type": "PowerCompany",
                    "name": company_name,
                    "confidence": 0.85
                })

    # Remove duplicates
    for entity_type in entities:
        entities[entity_type] = remove_duplicate_entities(entities[entity_type])

    return entities

def new_anexo_extraction(pdf_path: Path) -> dict:
    """Modified extraction function - AFTER schema integration"""

    # Your existing extraction logic (UNCHANGED!)
    extracted_data = {
        "title": "ANEXO 1 - Generación Programada",
        "date": "2025-02-15",
        "upper_table": {
            "headers": ["Central", "Potencia MW", "Energía GWh"],
            "rows": [
                {"central": "Solar Atacama", "potencia": "150", "energia": "360"},
                {"central": "Eólica Tarapacá", "potencia": "200", "energia": "480"}
            ]
        },
        "lower_table": {
            "headers": ["Empresa", "Total MW"],
            "rows": [
                {"empresa": "Energías Renovables S.A.", "total": "350"}
            ]
        },
        "confidence": 0.92
    }

    # NEW: Wrap in universal schema
    universal_document = create_universal_document(
        extraction_data=extracted_data,
        document_title=extracted_data["title"],
        document_date=extracted_data["date"],
        document_type="anexo_01",
        domain="operaciones",
        confidence_score=extracted_data["confidence"]
    )

    # NEW: Save in universal schema format
    doc_id = universal_document["@id"].replace(":", "_")
    output_path = Path(f"output/{doc_id}.json")
    save_universal_schema_json(universal_document, output_path)

    return universal_document  # Now returns schema-compliant data!

# ============================================================================
# Helper functions (add these to your scripts)
# ============================================================================

def determine_plant_type(plant_name: str) -> str:
    """Determine plant type from name"""
    name_lower = plant_name.lower()

    if "solar" in name_lower:
        return "SolarPowerPlant"
    elif "eólica" in name_lower or "eolica" in name_lower:
        return "WindPowerPlant"
    elif "hidro" in name_lower:
        return "HydroPowerPlant"
    elif "térmica" in name_lower or "termica" in name_lower:
        return "ThermalPowerPlant"
    else:
        return "PowerPlant"

def normalize_name(name: str) -> str:
    """Normalize name for entity ID"""
    import re
    normalized = re.sub(r'[^a-zA-Z0-9\s]', '', name.lower())
    normalized = re.sub(r'\s+', '_', normalized.strip())
    return normalized

def remove_duplicate_entities(entity_list: list) -> list:
    """Remove duplicate entities by name"""
    seen = set()
    unique = []
    for entity in entity_list:
        name = entity.get("name", "")
        if name not in seen:
            seen.add(name)
            unique.append(entity)
    return unique

def generate_semantic_tags_from_data(data: dict, domain: str) -> list:
    """Generate semantic tags from extraction data"""
    tags = [domain, "extraction_data"]

    # Look for renewable energy indicators
    data_str = json.dumps(data).lower()
    if "solar" in data_str:
        tags.append("renewable_energy")
    if "eólica" in data_str or "eolica" in data_str:
        tags.append("renewable_energy")
    if "hidro" in data_str:
        tags.append("renewable_energy")

    return list(set(tags))

def get_document_type(domain: str) -> str:
    """Get @type for document"""
    return {
        "operaciones": "PowerSystemDocument",
        "mercados": "MarketReport",
        "legal": "LegalRegulation",
        "planificacion": "PlanningStudy"
    }.get(domain, "Document")

def save_universal_schema_json(document: dict, output_path: Path):
    """Save document in universal schema format"""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(document, f, indent=2, ensure_ascii=False)

    print(f"✅ Universal schema document saved: {output_path}")
    return output_path

# ============================================================================
# Comparison demonstration
# ============================================================================

def demonstrate_before_after():
    """Show the difference between old and new extraction output"""

    print("=== BEFORE vs AFTER Comparison ===\n")

    # Old extraction
    print("🔴 OLD extraction output:")
    old_result = old_anexo_extraction(Path("sample.pdf"))
    print(f"Keys: {list(old_result.keys())}")
    print(f"Structure: Traditional flat extraction")
    print(f"AI-queryable: ❌ No")
    print(f"Cross-domain linkable: ❌ No")
    print(f"Knowledge graph ready: ❌ No\n")

    # New extraction
    print("🟢 NEW extraction output:")
    new_result = new_anexo_extraction(Path("sample.pdf"))
    print(f"Keys: {list(new_result.keys())}")
    print(f"Document ID: {new_result['@id']}")
    print(f"Entities found: {len(new_result['entities']['power_plants'])} plants, {len(new_result['entities']['companies'])} companies")
    print(f"AI-queryable: ✅ Yes")
    print(f"Cross-domain linkable: ✅ Yes")
    print(f"Knowledge graph ready: ✅ Yes")
    print(f"Original data preserved: ✅ In domain_specific_data.operaciones")

    # Show entity extraction
    print(f"\n📊 Automatically extracted entities:")
    for plant in new_result['entities']['power_plants']:
        print(f"  🏭 {plant['name']} ({plant['@type']})")
    for company in new_result['entities']['companies']:
        print(f"  🏢 {company['name']}")

# ============================================================================
# Step-by-step migration instructions
# ============================================================================

def migration_instructions():
    """Print step-by-step migration instructions"""

    instructions = """
📋 STEP-BY-STEP MIGRATION INSTRUCTIONS

Your existing extraction code needs only MINIMAL changes:

1️⃣ ADD helper functions to your script:
   - create_universal_document()
   - extract_entities_from_extraction_data()
   - Helper functions (normalize_name, determine_plant_type, etc.)

2️⃣ MODIFY your main extraction function:

   BEFORE:
   ```python
   def extract_anexo(pdf_path):
       results = your_extraction_logic()
       with open(output_path, 'w') as f:
           json.dump(results, f)
       return results
   ```

   AFTER:
   ```python
   def extract_anexo(pdf_path):
       results = your_extraction_logic()  # UNCHANGED!

       # NEW: Wrap in universal schema
       universal_doc = create_universal_document(
           extraction_data=results,
           document_title=results["title"],
           document_date=results["date"],
           document_type="anexo_01"  # Change per anexo
       )

       # NEW: Save in schema format
       save_universal_schema_json(universal_doc, output_path)
       return universal_doc
   ```

3️⃣ UPDATE output file naming:
   OLD: "anexo1_page70.json"
   NEW: "cen_operaciones_anexo_01_2025-02-15.json"

4️⃣ TEST your changes:
   - Run existing script
   - Verify output has @context, @id, entities
   - Check that domain_specific_data contains your original extraction

✅ BENEFITS:
- Your extraction logic stays the same
- Output becomes AI-queryable
- Automatic entity extraction from your tables
- Knowledge graph compatibility
- Cross-domain linking possible

⚡ AUTOMATION LEVEL:
- Entity extraction: AUTOMATIC (from your table structures)
- Plant type detection: AUTOMATIC (Solar/Wind/Hydro/Thermal)
- Schema compliance: AUTOMATIC (wrapper handles it)
- Cross-references: SEMI-AUTOMATIC (will be added by cross-reference engine)
"""

    print(instructions)

if __name__ == "__main__":
    demonstrate_before_after()
    print("\n" + "="*60 + "\n")
    migration_instructions()