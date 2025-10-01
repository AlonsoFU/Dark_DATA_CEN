"""
Demonstration of Table Cell Merger
Shows how to fix multi-line cells (cDoubleLinea) in EAF table data
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from shared_platform.utils import TableCellMerger


def demo_with_json_file():
    """Demonstrate with actual EAF JSON file."""

    # Path to the JSON file
    json_path = project_root / "domains" / "operaciones" / "eaf" / "chapters" / \
                "capitulo_01_descripcion_perturbacion" / "outputs" / "universal_json" / \
                "capitulo_01_final_smart.json"

    if not json_path.exists():
        print(f"❌ JSON file not found: {json_path}")
        return

    print(f"📂 Loading: {json_path.name}")
    print("=" * 80)

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Find the first table entity
    table_entity = None
    for entity in data.get("entities", []):
        if entity.get("type") == "table":
            table_entity = entity
            break

    if not table_entity:
        print("❌ No table found in JSON")
        return

    print(f"\n📊 Table found: {table_entity['id']}")
    print(f"   Page: {table_entity['source_page']}")
    print(f"   Rows: {len(table_entity['properties']['table_structure']['rows'])}")

    # Get table rows
    table_rows = table_entity['properties']['table_structure']['rows']

    print(f"\n🔍 BEFORE MERGING (showing rows with issues):")
    print("-" * 80)
    for idx, row in enumerate(table_rows[:15], 1):
        campo = row.get('campo', '')
        valor = row.get('valor', '')

        # Highlight problematic rows
        if campo.startswith('/') or campo.startswith('y '):
            print(f"  ⚠️  Row {idx}: '{campo}' → '{valor}'  [CONTINUATION LINE]")
        else:
            print(f"      Row {idx}: '{campo}' → '{valor[:50]}...' " if len(valor) > 50 else f"      Row {idx}: '{campo}' → '{valor}'")

    # Apply merger
    merger = TableCellMerger()
    merged_rows = merger.merge_table_rows(table_rows)

    print(f"\n✅ AFTER MERGING:")
    print("-" * 80)
    for idx, row in enumerate(merged_rows[:12], 1):
        campo = row.get('campo', '')
        valor = row.get('valor', '')
        print(f"      Row {idx}: '{campo}' → '{valor[:70]}...' " if len(valor) > 70 else f"      Row {idx}: '{campo}' → '{valor}'")

    # Show statistics
    print(f"\n📈 STATISTICS:")
    print(f"   Before: {len(table_rows)} rows")
    print(f"   After:  {len(merged_rows)} rows")
    print(f"   Merged: {len(table_rows) - len(merged_rows)} continuation lines")

    # Save merged version
    output_path = json_path.parent / f"{json_path.stem}_merged.json"

    # Update the entity with merged rows
    table_entity['properties']['table_structure']['rows'] = merged_rows
    table_entity['properties']['table_metadata']['row_count'] = len(merged_rows)

    # Save
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Saved merged version to: {output_path.name}")


def demo_with_sample_data():
    """Demonstrate with sample problematic data."""

    print("\n" + "=" * 80)
    print("📝 SAMPLE DATA DEMONSTRATION")
    print("=" * 80)

    # Simulate problematic table from EAF
    sample_data = [
        {"row_id": 1, "campo": "1.", "valor": "Descripción pormenorizada de la perturbación"},
        {"row_id": 2, "campo": "a.", "valor": "Fecha y Hora de la falla"},
        {"row_id": 3, "campo": "Fecha", "valor": "25/02/2025"},
        {"row_id": 4, "campo": "Hora", "valor": "15:16"},
        {"row_id": 9, "campo": "b.", "valor": "Identificación instalación afectada"},
        {"row_id": 10, "campo": "Nombre de la instalación", "valor": "Ambos circuitos de la línea 2x500 kV Nueva Maitencillo - Nueva Pan de Azúcar"},
        {"row_id": 11, "campo": "/ LT002CI1TR01T0022ST01T0022", "valor": "y LT002CI2TR01T0022ST01T0022"},  # <- PROBLEMATIC LINE
        {"row_id": 12, "campo": "Tipo de instalación", "valor": "Línea"},
        {"row_id": 13, "campo": "Tensión nominal", "valor": "500 kV"},
        {"row_id": 14, "campo": "Propietario instalación afectada", "valor": "Interchile S.A."},
        {"row_id": 15, "campo": "RUT", "valor": "76.257.379-2"},
        {"row_id": 16, "campo": "Dirección", "valor": "Cerro El Plomo 5630, Oficina 1802, Las Condes"},
        {"row_id": 17, "campo": "Región Metropolitana de Santiago", "valor": ""},  # <- CONTINUATION
    ]

    print("\n🔍 BEFORE:")
    for row in sample_data:
        print(f"  {row['row_id']:2d}: {row['campo']:40s} → {row['valor']}")

    merger = TableCellMerger()
    merged = merger.merge_table_rows(sample_data)

    print("\n✅ AFTER:")
    for row in merged:
        print(f"  {row['row_id']:2d}: {row['campo']:40s} → {row['valor']}")

    print(f"\n📊 Reduced from {len(sample_data)} to {len(merged)} rows")


if __name__ == "__main__":
    print("🔧 TABLE CELL MERGER DEMONSTRATION")
    print("=" * 80)
    print("Fixes multi-line cells (cDoubleLinea, cTripleLinea) in EAF tables")
    print("=" * 80)

    # Run both demos
    demo_with_json_file()
    demo_with_sample_data()

    print("\n✨ Done!")
