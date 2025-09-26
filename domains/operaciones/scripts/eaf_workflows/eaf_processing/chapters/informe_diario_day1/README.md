# INFORME DIARIO Day 1 Processing Workflow

Extracts and processes daily operational report data from **INFORME DIARIO - Tuesday, February 25, 2025** (Pages 101-134).

## Overview

This workflow processes the first daily report containing:
- System operational summary
- Peak demand and load profiles
- Generation sources and capacity
- Incidents and operational events
- System performance metrics (frequency, voltage)
- Weather impact assessments
- Transmission system status

## Directory Structure

```
informe_diario_day1/
├── content_extraction/
│   └── extract_informe_diario_day1.py      # Main extraction script
├── validation_quality/
│   └── validate_daily_report_data.py       # Data validation and QA
├── final_generation/
│   └── generate_final_daily_report.py      # Final report consolidation
└── README.md                               # This file
```

## Data Output Location

```
extractions/informe_diario_day1/
├── informe_diario_day1_page_101_YYYYMMDD_HHMMSS.json
├── informe_diario_day1_page_102_YYYYMMDD_HHMMSS.json
├── ...
├── validation_report_YYYYMMDD_HHMMSS.json
└── final_informe_diario_day1_report_YYYYMMDD_HHMMSS.json
```

## Usage

### 1. Content Extraction

Extract data from specific pages or all pages:

```bash
# Extract from a single page
python content_extraction/extract_informe_diario_day1.py 101

# Extract from all pages (101-134)
python content_extraction/extract_informe_diario_day1.py --all

# Extract from page range
for page in {101..134}; do
    python content_extraction/extract_informe_diario_day1.py $page
done
```

### 2. Data Validation

Validate extracted data quality:

```bash
# Standard validation
python validation_quality/validate_daily_report_data.py

# Strict validation with additional checks
python validation_quality/validate_daily_report_data.py --strict
```

### 3. Final Report Generation

Consolidate all extractions into final report:

```bash
# Generate final comprehensive report
python final_generation/generate_final_daily_report.py

# Include failed extractions in analysis
python final_generation/generate_final_daily_report.py --include-failed
```

## Extracted Data Structure

### Individual Page Extraction
```json
{
  "page": 101,
  "chapter": "INFORME_DIARIO_DAY1",
  "extraction_timestamp": "2025-09-15T...",
  "date_info": {
    "report_date": "2025-02-25",
    "day_name": "Tuesday"
  },
  "operational_summary": {
    "system_status": "operational",
    "peak_demand_mw": 8500.0,
    "peak_demand_time": "20:30",
    "transmission_status": "normal"
  },
  "generation_data": [
    {
      "source_type": "hidro",
      "capacity_mw": 450.0,
      "text_context": "central hidroeléctrica 450 mw"
    }
  ],
  "incidents_and_events": [
    {
      "type": "mantenimiento",
      "description": "Mantenimiento programado línea 220kV",
      "time": "14:30",
      "line_number": 25
    }
  ],
  "system_metrics": {
    "frequency_hz": 50.0,
    "voltage_levels": [220, 500],
    "reserve_margin_mw": 1200
  },
  "status": "extracted"
}
```

### Final Report Structure
```json
{
  "report_info": {
    "title": "INFORME DIARIO - Tuesday, February 25, 2025",
    "chapter": "INFORME_DIARIO_DAY1",
    "pages_analyzed": [101, 102, ..., 134],
    "successful_extractions": 30,
    "data_quality": "high"
  },
  "executive_summary": {
    "date": "Tuesday, February 25, 2025",
    "system_status": "OPERATIONAL",
    "key_metrics": {
      "peak_demand_mw": 8500,
      "total_incidents": 15,
      "generation_sources": 8
    },
    "highlights": [...],
    "concerns": [...],
    "recommendations": [...]
  },
  "operational_overview": {...},
  "generation_analysis": [...],
  "incidents_analysis": {...},
  "system_performance": {...},
  "business_intelligence": {...}
}
```

## Data Quality Validation

The validation script checks:

### Operational Metrics
- Peak demand within reasonable range (5,000-15,000 MW)
- Valid time formats (HH:MM)
- System status consistency

### Generation Data
- Valid source types (hidro, térmica, solar, etc.)
- Realistic capacity ranges (0-2,000 MW)
- Data completeness

### System Metrics
- Frequency within normal range (49.5-50.5 Hz)
- Standard Chilean voltage levels
- Metric consistency

### Incidents
- Valid incident types
- Adequate description length
- Proper time formatting

## Quality Scoring

Each extraction receives a quality score (0-100):
- **90-100 (A)**: Excellent extraction
- **80-89 (B)**: Good extraction
- **70-79 (C)**: Acceptable extraction
- **60-69 (D)**: Poor extraction
- **0-59 (F)**: Failed extraction

Score components:
- Data completeness (40%)
- Content richness (30%)
- Validation passed (20%)
- Extraction success (10%)

## Business Intelligence

The final report includes BI metrics:

### Operational Efficiency
- System reliability assessment
- Generation diversity index
- Performance indicators

### Risk Assessment
- Operational risk level
- Incident frequency analysis
- System stress indicators

### Performance Indicators
- Peak demand ratios
- Generation utilization
- Frequency stability scores

## Troubleshooting

### Common Issues

1. **Low text extraction**: Pages may be image-heavy
   - Solution: OCR processing is automatically applied

2. **Missing generation data**: Text parsing issues
   - Solution: Review extraction patterns in code

3. **Invalid time formats**: Inconsistent time representation
   - Solution: Validation will flag these for manual review

### Error Handling

The scripts include comprehensive error handling:
- Failed extractions are logged but don't stop processing
- Validation issues are reported with specific guidance
- Final report includes success/failure statistics

## Integration with Database

After successful extraction and validation, data can be ingested into the main database:

```bash
# Ingest final reports into main database
python scripts/database_tools/ingest_data.py --source informe_diario_day1
```

## Performance Notes

- Processing all 34 pages typically takes 3-5 minutes
- OCR processing adds ~10 seconds per image-heavy page
- Validation runs in under 30 seconds for all extractions
- Final report generation takes ~1 minute for full dataset