#!/usr/bin/env python3
"""
ANEXO 3 CDC Reports Manual Extraction Template
==============================================

Manual template for ANEXO 3 extraction based on the known structure.
This creates the extraction files in the same format as ANEXO 1 and 2.

ANEXO 3 covers pages 96-100 and contains:
- Movement details of power plants
- Daily CDC (Centro de Despacho y Control) reports
- Operational status changes
- Central dispatch control information

Usage:
    python extract_anexo3_manual_template.py
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent.parent.parent

def create_anexo3_page_template(page_num: int) -> Dict:
    """Create a template for ANEXO 3 page extraction"""

    # Base metadata for all ANEXO 3 pages
    base_metadata = {
        "document_metadata": {
            "document_file": "Anexos-EAF-089-2025.pdf",
            "document_path": str(project_root / "data" / "documents" / "anexos_EAF" / "source_documents" / "Anexos-EAF-089-2025.pdf"),
            "page_number": page_num,
            "extraction_timestamp": datetime.now().isoformat(),
            "document_type": "ANEXO_EAF_CDC_REPORTS",
            "extraction_method": "manual_template_based",
            "concept": "CDC movement and daily operation reports - plant status changes and dispatch control information"
        }
    }

    # Template structure based on ANEXO 3 content type
    template = {
        **base_metadata,
        "date_information": {
            "operation_dates": ["25-02-2025", "26-02-2025"],
            "report_type": "CDC_movement_report",
            "time_period": "daily_operation"
        },
        "plant_movements": {
            "scheduled_starts": [],
            "scheduled_stops": [],
            "forced_outages": [],
            "maintenance_operations": [],
            "status_changes": []
        },
        "cdc_reports": {
            "operational_summary": {
                "system_status": "normal_operation",
                "alerts_count": 0,
                "major_incidents": []
            },
            "dispatch_actions": [],
            "grid_conditions": {
                "transmission_status": "normal",
                "voltage_levels": "within_limits",
                "frequency_control": "stable"
            }
        },
        "central_movements": {
            "thermal_plants": [],
            "hydro_plants": [],
            "renewable_plants": []
        },
        "extraction_notes": {
            "page_content_type": get_page_content_type(page_num),
            "extraction_status": "template_created",
            "requires_manual_review": True,
            "next_steps": [
                "Review actual PDF content for this page",
                "Extract specific plant movement data",
                "Identify CDC operational reports",
                "Validate against original document"
            ]
        }
    }

    # Page-specific content based on typical ANEXO 3 structure
    if page_num == 96:  # First page - usually contains title and summary
        template["page_type"] = "title_and_summary"
        template["expected_content"] = [
            "ANEXO 3 title and description",
            "Summary of plant movements for reporting period",
            "Overview of CDC operational activities"
        ]
    elif page_num in [97, 98, 99]:  # Middle pages - detailed movement data
        template["page_type"] = "detailed_movements"
        template["expected_content"] = [
            "Detailed plant start/stop operations",
            "Scheduled maintenance activities",
            "Forced outage reports",
            "CDC dispatch actions"
        ]
    elif page_num == 100:  # Last page - summary and conclusions
        template["page_type"] = "summary_conclusions"
        template["expected_content"] = [
            "Summary of all movements",
            "CDC operational conclusions",
            "Period performance summary"
        ]

    return template

def get_page_content_type(page_num: int) -> str:
    """Determine expected content type for each page"""
    content_map = {
        96: "title_header_summary",
        97: "plant_movements_detail",
        98: "cdc_operations_detail",
        99: "system_status_reports",
        100: "summary_conclusions"
    }
    return content_map.get(page_num, "unknown_content")

def save_extraction_template(template: Dict, page_num: int):
    """Save extraction template to JSON file"""
    output_dir = project_root / "data" / "documents" / "anexos_EAF" / "extractions" / "anexo_03_cdc_reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"anexo3_page_{page_num:02d}_template_{timestamp}.json"
    output_path = output_dir / filename

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)

    print(f"Template saved to: {output_path}")
    return output_path

def create_readme_file():
    """Create README file for ANEXO 3 extraction"""
    readme_content = """# ANEXO 3 - CDC Reports Extraction

## Overview
ANEXO 3 contains movement details of power plants and CDC (Centro de Despacho y Control) daily operation reports.

**Page Range:** 96-100 (5 pages)
**Content Type:** CDC Reports and Plant Movements
**Focus:** Operational status changes and dispatch control information

## Page Structure
- **Page 96:** Title and summary of CDC movements
- **Pages 97-99:** Detailed plant movement operations and CDC reports
- **Page 100:** Summary and operational conclusions

## Extraction Status
- ✅ Template structure created
- ⏳ Manual content extraction needed
- ⏳ Data validation required
- ⏳ Integration with database pending

## Next Steps
1. Manual review of each page content
2. Extract specific plant movement data
3. Identify and structure CDC operational reports
4. Validate extracted data against original PDF
5. Create final structured JSON output

## Files Generated
- `anexo3_page_XX_template_TIMESTAMP.json` - Initial extraction templates

## Content Expected
- Plant start/stop operations
- Scheduled maintenance activities
- Forced outage reports
- CDC dispatch actions
- System status summaries
- Grid condition reports
- Operational conclusions

## Usage
```bash
python extract_anexo3_manual_template.py
```

This creates template files for all ANEXO 3 pages (96-100) ready for manual content population.
"""

    readme_dir = project_root / "data" / "documents" / "anexos_EAF" / "extractions" / "anexo_03_cdc_reports"
    readme_path = readme_dir / "README.md"

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print(f"README created at: {readme_path}")

def main():
    """Create ANEXO 3 extraction templates for all pages"""
    print("Creating ANEXO 3 CDC Reports extraction templates...")

    # Create templates for all ANEXO 3 pages
    page_range = range(96, 101)  # Pages 96-100
    created_files = []

    for page_num in page_range:
        template = create_anexo3_page_template(page_num)
        file_path = save_extraction_template(template, page_num)
        created_files.append(file_path)
        print(f"✅ Template created for page {page_num}")

    # Create README
    create_readme_file()

    print(f"\n📊 ANEXO 3 Template Creation Summary:")
    print(f"   Created templates: {len(created_files)} pages")
    print(f"   Page range: 96-100 (CDC Reports)")
    print(f"   Content focus: Plant movements and CDC operational reports")
    print(f"   Status: Ready for manual content extraction")

    print(f"\n📁 Files created:")
    for file_path in created_files:
        print(f"   - {file_path.name}")

    print(f"\n🔄 Next steps:")
    print(f"   1. Review actual PDF content for pages 96-100")
    print(f"   2. Populate templates with real extracted data")
    print(f"   3. Validate against original document")
    print(f"   4. Integrate with processing pipeline")

if __name__ == "__main__":
    main()