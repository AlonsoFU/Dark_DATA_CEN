#!/usr/bin/env python3
"""
Debug script to find why TER plant extraction is incomplete
"""

import sys
import re
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent.parent.parent
sys.path.append(str(project_root))

import fitz

def debug_detect_table_structure(raw_text: str):
    """Debug version of detect_table_structure"""
    tables = {
        "power_plants": [],
        "left_table": [],
        "right_table": [],
        "debug_info": []
    }

    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]

    i = 0
    current_table_side = "left"
    plant_count = 0

    while i < len(lines):
        line = lines[i]

        # Look for plant name pattern
        plant_match = re.match(r'^(PE|PFV|PEO|CTM|CTH|CTA|TER|U)\s+(.+)$', line)
        if plant_match:
            plant_type = plant_match.group(1)
            plant_name = plant_match.group(2).strip()
            plant_count += 1

            # Detect table side
            if plant_type == "TER" or plant_count > 25:
                current_table_side = "right"

            print(f"Processing plant {plant_count}: {plant_type} {plant_name} ({current_table_side})")

            # Initialize plant data
            plant_data = {
                "plant_type": plant_type,
                "plant_name": plant_name,
                "programmed_mwh": None,
                "real_mwh": None,
                "percentage_diff": None,
                "estado": None,
                "table_side": current_table_side,
                "special_markers": [],
                "comments": [],
                "raw_lines": [line],
                "debug_line_start": i
            }

            # Look ahead for data values
            j = i + 1
            values_found = []

            while j < len(lines) and j < i + 6:
                next_line = lines[j]

                # Check if this is another plant (stop processing current plant)
                if re.match(r'^(PE|PFV|PEO|CTM|CTH|CTA|TER|U)\s+(.+)$', next_line):
                    break

                # Check for programmed value (number with possible markers)
                number_with_marker = re.match(r'^(\d+\.?\d*)([*†‡§¶#@]+)?$', next_line)
                if number_with_marker:
                    value = float(number_with_marker.group(1))
                    values_found.append(('number', value, next_line))
                    plant_data["raw_lines"].append(next_line)

                # Check for percentage with markers
                elif re.match(r'^(\(\*\))?\s*([\+\-]?\d+\.?\d*)\s*%?([*†‡§¶#@]+)?$', next_line):
                    percentage_match = re.match(r'^(\(\*\))?\s*([\+\-]?\d+\.?\d*)\s*%?([*†‡§¶#@]+)?$', next_line)
                    percentage = float(re.sub(r'[%\s*†‡§¶#@()]', '', percentage_match.group(2)))
                    values_found.append(('percentage', percentage, next_line))
                    plant_data["raw_lines"].append(next_line)

                # Check for standard percentage
                elif re.match(r'^([\+\-]?\d+\.?\d*)\s*%?$', next_line):
                    percentage = float(re.sub(r'[%\s]', '', next_line))
                    values_found.append(('percentage', percentage, next_line))
                    plant_data["raw_lines"].append(next_line)

                # Check for Estado
                elif re.match(r'^[A-Z]{2,3}$', next_line) and len(next_line) <= 3:
                    plant_data["estado"] = next_line
                    plant_data["raw_lines"].append(next_line)

                # Check for blank/missing data
                elif next_line in ['-', '--', '', 'N/A', 'n/a', '*']:
                    values_found.append(('blank', None, next_line))
                    plant_data["raw_lines"].append(next_line)

                j += 1

            # Process the found values
            numbers = [v for v in values_found if v[0] == 'number']
            percentages = [v for v in values_found if v[0] == 'percentage']

            if len(numbers) >= 2:
                plant_data["programmed_mwh"] = numbers[0][1]
                plant_data["real_mwh"] = numbers[1][1]
            elif len(numbers) == 1:
                plant_data["programmed_mwh"] = numbers[0][1]

            if percentages:
                plant_data["percentage_diff"] = percentages[0][1]

            plant_data["debug_line_end"] = j
            plant_data["debug_values_found"] = values_found

            print(f"  Found values: {len(numbers)} numbers, {len(percentages)} percentages")
            print(f"  Raw lines: {plant_data['raw_lines']}")

            # Add to tables
            tables["power_plants"].append(plant_data)
            if current_table_side == "left":
                tables["left_table"].append(plant_data)
            else:
                tables["right_table"].append(plant_data)

            # Skip the processed lines
            i = j
            continue

        i += 1

    return tables

def main():
    # Open PDF and extract page 105
    pdf_path = "/home/alonso/Documentos/Github/Proyecto Dark Data CEN/data/documents/power_system_reports/anexos_EAF/Anexos-EAF-089-2025.pdf"
    doc = fitz.open(pdf_path)
    page = doc.load_page(104)  # 0-indexed
    raw_text = page.get_text()
    doc.close()

    print("Starting debug extraction...")
    result = debug_detect_table_structure(raw_text)

    print(f"\n=== SUMMARY ===")
    print(f"Total plants: {len(result['power_plants'])}")
    print(f"Left table: {len(result['left_table'])}")
    print(f"Right table: {len(result['right_table'])}")

    # Count by type
    by_type = {}
    for plant in result['power_plants']:
        plant_type = plant['plant_type']
        by_type[plant_type] = by_type.get(plant_type, 0) + 1

    print(f"By type: {by_type}")

    # Check for San Isidro
    san_isidro = [p for p in result['power_plants'] if 'San Isidro' in p['plant_name']]
    print(f"\nSan Isidro plants found: {len(san_isidro)}")
    for plant in san_isidro:
        print(f"  {plant['plant_type']} {plant['plant_name']}")

    # Show last 5 plants
    print(f"\nLast 5 plants:")
    for plant in result['power_plants'][-5:]:
        print(f"  {plant['plant_type']} {plant['plant_name']} ({plant['table_side']})")

if __name__ == "__main__":
    main()