# Data Documents Structure

## New Hierarchical Organization

This directory has been reorganized to align with the new hierarchical processing structure:

### ANEXOS EAF Data
```
anexos_eaf/data/
├── source_documents/           # Original EAF PDF files
├── samples_and_tests/         # Test documents for development
└── consolidated_extractions/  # Cross-chapter analysis results
```

### Chapter-Specific Data
```
anexos_eaf/chapters/anexo_XX/data/
├── extractions/              # Processed extraction results
└── documentation/            # Chapter-specific documentation
```

### Shared Data (Future Document Types)
```
shared/data/
├── compliance_reports/       # Compliance document storage
├── failure_reports/          # Failure report storage
├── maintenance_logs/         # Maintenance log storage
└── scrapers/scraped_data/    # Web-scraped data storage
```

## Data Flow

1. **Source documents** → stored in appropriate document type folder
2. **Processing** → chapter-specific processors extract data
3. **Results** → stored in chapter-specific data/extractions
4. **Consolidation** → cross-chapter analysis in consolidated_extractions

## Migration Notes

- Chapter documentation moved from `data/documents/anexos_EAF/documentation/` to `anexos_eaf/chapters/*/data/documentation/`
- Future document types moved to `shared/data/` for cross-domain access
- Scraped data centralized in `shared/scrapers/scraped_data/`
