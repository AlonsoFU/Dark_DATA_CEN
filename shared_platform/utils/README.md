# Shared Platform Utilities

General-purpose utilities that can be used across all domains and components.

## ContentClassifier

Universal PDF content classifier for identifying and extracting different content types.

### Features

- **Multi-type detection**: Text, Tables, Formulas, Images, Headings, Lists
- **OCR support**: Optional Tesseract integration for scanned documents
- **Layout analysis**: PyMuPDF-based coordinate extraction
- **Table detection**: Multiple strategies (PyMuPDF built-in + alignment analysis)
- **Confidence scoring**: Each block includes confidence metric
- **General-purpose**: Works with any PDF document

### Quick Start

```python
from shared_platform.utils import ContentClassifier

# Classify single page
classifier = ContentClassifier(pdf_path="document.pdf")
blocks = classifier.classify_page(page_num=1)

for block in blocks:
    print(f"Type: {block.type}, Confidence: {block.confidence}")
    print(f"Content: {block.content}")

# Classify entire document
results = classifier.classify_document(start_page=1, end_page=10)
print(f"Found {results['statistics']['table']} tables")
print(f"Found {results['statistics']['text']} text blocks")
```

### With OCR (for scanned documents)

```python
# Enable OCR with Spanish + English
classifier = ContentClassifier(
    pdf_path="scanned_document.pdf",
    use_ocr=True,
    ocr_language="spa+eng"
)

blocks = classifier.classify_page(1)
```

### Usage from Domain Processors

```python
from shared_platform.utils import ContentClassifier, ContentType

class MyDocumentProcessor:
    def __init__(self, pdf_path: str):
        self.classifier = ContentClassifier(pdf_path)

    def extract_tables_only(self, page_num: int):
        """Extract only tables from page."""
        blocks = self.classifier.classify_page(page_num)

        tables = [
            block for block in blocks
            if block.type == ContentType.TABLE.value
        ]

        return tables
```

### Content Types

- **TEXT**: Paragraphs and narrative text
- **TABLE**: Structured tabular data
- **FORMULA**: Mathematical equations and formulas
- **IMAGE**: Graphics and images
- **HEADING**: Titles and section headings
- **LIST**: Bulleted or numbered lists

### Test Script

Test the classifier on your documents:

```bash
cd shared_platform/utils

# Test single page
python test_classifier.py /path/to/document.pdf 1

# Test page range (1-3)
python test_classifier.py /path/to/document.pdf

# Test on EAF document
python test_classifier.py ../../domains/operaciones/eaf/shared/source/EAF-089-2025.pdf 1
```

### Tested Results

**EAF-089-2025 Page 1:**
- ✅ 5 Tables detected (0.70-0.90 confidence)
- ✅ 9 Text blocks (0.95 confidence)
- ✅ 6 Headings (0.90 confidence)

### Implementation Details

**Detection Strategies:**

1. **Tables**:
   - PyMuPDF built-in `find_tables()` (0.9 confidence)
   - Column alignment analysis (0.7-0.95 confidence)

2. **Formulas**:
   - Mathematical notation patterns (∫∑∏√∂∇)
   - Greek letters (α-ωΑ-Ω)
   - LaTeX-like syntax

3. **Headings**:
   - Font size analysis (>14pt)
   - Bold formatting detection
   - Pattern matching (Capítulo, Sección, numbered)

4. **Lists**:
   - Bullet markers (•-*)
   - Numbered lists (1. 2. 3.)
   - Lettered lists (a) b) c))

5. **Images**:
   - PyMuPDF `get_images()` with bbox extraction

**Configuration:**

- `table_detection_threshold`: Minimum confidence for tables (default: 0.7)
- `use_ocr`: Enable Tesseract OCR (default: False)
- `ocr_language`: Tesseract language codes (default: "spa+eng")

### Dependencies

- `PyMuPDF` (fitz): Core PDF processing
- `tesseract-ocr` (optional): For scanned documents

```bash
pip install pymupdf
# For OCR support:
sudo apt-get install tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng
```

### Performance

- **Fast**: ~0.5-2 seconds per page (without OCR)
- **Memory efficient**: Processes page-by-page
- **Scalable**: Works with large documents (399+ pages tested)

### Future Enhancements

- [ ] Enhanced formula extraction with LaTeX conversion
- [ ] Deep learning table detection (DeepDeSRT integration)
- [ ] Multi-column layout detection
- [ ] Header/footer automatic exclusion
- [ ] Cross-page table detection