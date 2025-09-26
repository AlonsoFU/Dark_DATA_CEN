#!/usr/bin/env python3
"""
PDF Extractor V2 - Specialized for structured technical documents
Eliminates placeholder content by using multiple extraction methods
"""

import logging
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import yaml

# PDF processing libraries
try:
    import pdfplumber
except ImportError:
    pdfplumber = None
    
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None
    
try:
    from pdfminer.high_level import extract_text_to_fp
    from pdfminer.layout import LAParams
    import io
except ImportError:
    extract_text_to_fp = None

@dataclass
class ExtractionResult:
    """Result of text extraction for a single page"""
    page_num: int
    text: str
    method_used: str
    confidence_score: float
    processing_time: float
    has_placeholder: bool = False
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []

class PDFExtractorV2:
    """
    Advanced PDF extractor designed for structured technical documents
    """
    
    def __init__(self, config_path: str = None):
        # Load configuration
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "processing_config.yaml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # Setup logging
        logging.basicConfig(
            level=getattr(logging, self.config['logging']['level']),
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Extraction methods configuration
        self.extraction_methods = self.config['pdf_extraction']['methods']
        self.batch_size = self.config['pdf_extraction']['batch_size']
        self.max_retries = self.config['pdf_extraction']['max_retries']
        self.min_chars = self.config['pdf_extraction']['min_chars_per_page']
        
        self.logger.info(f"Initialized PDFExtractorV2 with methods: {self.extraction_methods}")
    
    def extract_document(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract text from entire PDF using multiple methods as needed
        """
        self.logger.info(f"Starting extraction of: {pdf_path}")
        start_time = time.time()
        
        results = {
            'pages': {},
            'total_pages': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'placeholder_count': 0,
            'extraction_summary': {},
            'processing_time': 0
        }
        
        # Get total pages first
        try:
            if pdfplumber:
                with pdfplumber.open(pdf_path) as pdf:
                    results['total_pages'] = len(pdf.pages)
            elif fitz:
                doc = fitz.open(pdf_path)
                results['total_pages'] = len(doc)
                doc.close()
            else:
                raise Exception("No PDF library available")
                
        except Exception as e:
            self.logger.error(f"Could not determine page count: {e}")
            return results
        
        self.logger.info(f"Document has {results['total_pages']} pages")
        
        # Process pages in batches
        for batch_start in range(0, results['total_pages'], self.batch_size):
            batch_end = min(batch_start + self.batch_size, results['total_pages'])
            self.logger.info(f"Processing pages {batch_start + 1} to {batch_end}")
            
            batch_results = self._extract_batch(pdf_path, batch_start, batch_end)
            
            for page_num, result in batch_results.items():
                results['pages'][page_num] = result
                
                if result.text and not result.has_placeholder:
                    results['successful_extractions'] += 1
                else:
                    results['failed_extractions'] += 1
                    
                if result.has_placeholder:
                    results['placeholder_count'] += 1
        
        # Calculate summary statistics
        total_processing_time = time.time() - start_time
        results['processing_time'] = total_processing_time
        
        # Method usage summary
        method_counts = {}
        for result in results['pages'].values():
            method = result.method_used
            method_counts[method] = method_counts.get(method, 0) + 1
        
        results['extraction_summary'] = {
            'success_rate': results['successful_extractions'] / results['total_pages'] * 100,
            'placeholder_rate': results['placeholder_count'] / results['total_pages'] * 100,
            'avg_processing_time': total_processing_time / results['total_pages'],
            'method_usage': method_counts
        }
        
        self.logger.info(f"Extraction completed: {results['extraction_summary']}")
        return results
    
    def _extract_batch(self, pdf_path: str, start_page: int, end_page: int) -> Dict[int, ExtractionResult]:
        """Extract text from a batch of pages"""
        batch_results = {}
        
        for page_num in range(start_page, end_page):
            self.logger.debug(f"Processing page {page_num + 1}")
            
            result = self._extract_single_page(pdf_path, page_num)
            batch_results[page_num] = result
            
        return batch_results
    
    def _extract_single_page(self, pdf_path: str, page_num: int) -> ExtractionResult:
        """
        Extract text from a single page using multiple methods if needed
        """
        start_time = time.time()
        
        for attempt in range(self.max_retries):
            for method_name in self.extraction_methods:
                try:
                    text = self._extract_with_method(pdf_path, page_num, method_name)
                    
                    # Validate extraction
                    validation = self._validate_extraction(text, page_num)
                    
                    if validation['is_valid']:
                        processing_time = time.time() - start_time
                        
                        return ExtractionResult(
                            page_num=page_num,
                            text=text,
                            method_used=method_name,
                            confidence_score=validation['confidence'],
                            processing_time=processing_time,
                            has_placeholder=validation['has_placeholder'],
                            warnings=validation['warnings']
                        )
                    else:
                        self.logger.debug(f"Page {page_num + 1} failed validation with {method_name}: {validation['reason']}")
                        
                except Exception as e:
                    self.logger.debug(f"Method {method_name} failed for page {page_num + 1}: {e}")
                    continue
        
        # All methods failed
        processing_time = time.time() - start_time
        self.logger.warning(f"All extraction methods failed for page {page_num + 1}")
        
        return ExtractionResult(
            page_num=page_num,
            text="",
            method_used="none",
            confidence_score=0.0,
            processing_time=processing_time,
            has_placeholder=True,
            warnings=["All extraction methods failed"]
        )
    
    def _extract_with_method(self, pdf_path: str, page_num: int, method: str) -> str:
        """Extract text using a specific method"""
        
        if method == "pdfplumber" and pdfplumber:
            return self._extract_with_pdfplumber(pdf_path, page_num)
            
        elif method == "pymupdf" and fitz:
            return self._extract_with_pymupdf(pdf_path, page_num)
            
        elif method == "pdfminer" and extract_text_to_fp:
            return self._extract_with_pdfminer(pdf_path, page_num)
            
        elif method == "tesseract_ocr":
            return self._extract_with_ocr(pdf_path, page_num)
            
        else:
            raise Exception(f"Method {method} not available or not implemented")
    
    def _extract_with_pdfplumber(self, pdf_path: str, page_num: int) -> str:
        """Extract using pdfplumber - best for structured text"""
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[page_num]
            text = page.extract_text()
            
            # Also try to extract tables if regular text extraction fails
            if not text or len(text.strip()) < self.min_chars:
                tables = page.extract_tables()
                if tables:
                    table_text = []
                    for table in tables:
                        for row in table:
                            if row:
                                table_text.append(" | ".join([cell or "" for cell in row]))
                    text = "\\n".join(table_text)
                    
            return text or ""
    
    def _extract_with_pymupdf(self, pdf_path: str, page_num: int) -> str:
        """Extract using PyMuPDF - good for complex layouts"""
        doc = fitz.open(pdf_path)
        try:
            page = doc[page_num]
            text = page.get_text()
            
            # Try different extraction methods if needed
            if not text or len(text.strip()) < self.min_chars:
                # Try extracting with layout preservation
                text = page.get_text("dict")
                # Process text blocks from dict format
                blocks_text = []
                for block in text.get("blocks", []):
                    if "lines" in block:
                        for line in block["lines"]:
                            line_text = ""
                            for span in line.get("spans", []):
                                line_text += span.get("text", "")
                            if line_text.strip():
                                blocks_text.append(line_text.strip())
                text = "\\n".join(blocks_text)
                    
            return text or ""
        finally:
            doc.close()
    
    def _extract_with_pdfminer(self, pdf_path: str, page_num: int) -> str:
        """Extract using pdfminer - fallback method"""
        # This is more complex as pdfminer doesn't easily extract single pages
        # For now, implement basic extraction
        with open(pdf_path, 'rb') as file:
            output_string = io.StringIO()
            laparams = LAParams(
                boxes_flow=0.5,
                word_margin=0.1,
                char_margin=2.0,
                line_margin=0.5
            )
            extract_text_to_fp(file, output_string, laparams=laparams)
            full_text = output_string.getvalue()
            
            # This extracts all text - need to split by pages somehow
            # For now, return the full text (not ideal but functional)
            return full_text or ""
    
    def _extract_with_ocr(self, pdf_path: str, page_num: int) -> str:
        """Extract using OCR - last resort method"""
        # This would require converting PDF page to image and running OCR
        # Not implemented in this version
        raise Exception("OCR extraction not implemented yet")
    
    def _validate_extraction(self, text: str, page_num: int) -> Dict[str, Any]:
        """
        Validate extracted text quality and detect common issues
        """
        validation = {
            'is_valid': False,
            'confidence': 0.0,
            'has_placeholder': False,
            'warnings': [],
            'reason': ''
        }
        
        if not text:
            validation['reason'] = "No text extracted"
            return validation
        
        text_clean = text.strip()
        
        # Check for placeholder patterns
        placeholder_patterns = [
            r'\\[\\d+\\s+characters?\\]',
            r'\\[Page\\s+\\d+\\]',
            r'^\\[.*\\]$'
        ]
        
        import re
        for pattern in placeholder_patterns:
            if re.search(pattern, text_clean):
                validation['has_placeholder'] = True
                validation['reason'] = f"Contains placeholder pattern: {pattern}"
                return validation
        
        # Check minimum length
        if len(text_clean) < self.min_chars:
            validation['reason'] = f"Text too short: {len(text_clean)} < {self.min_chars}"
            return validation
        
        # Calculate confidence based on text characteristics
        confidence = 0.0
        
        # Length score (optimal range 100-5000 characters)
        length = len(text_clean)
        if 100 <= length <= 5000:
            confidence += 0.4
        elif 50 <= length < 100 or 5000 < length <= 10000:
            confidence += 0.2
        
        # Character variety (letters, numbers, punctuation)
        has_letters = any(c.isalpha() for c in text_clean)
        has_numbers = any(c.isdigit() for c in text_clean)
        has_punctuation = any(c in '.,;:!?()[]{}' for c in text_clean)
        
        if has_letters:
            confidence += 0.3
        if has_numbers:
            confidence += 0.2
        if has_punctuation:
            confidence += 0.1
        
        validation['confidence'] = min(confidence, 1.0)
        
        # Consider valid if confidence is above threshold
        if validation['confidence'] >= 0.6:
            validation['is_valid'] = True
        else:
            validation['reason'] = f"Low confidence score: {validation['confidence']:.2f}"
        
        return validation

def main():
    """Test the extractor with sample document"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python pdf_extractor_v2.py <pdf_file>")
        return
    
    pdf_path = sys.argv[1]
    extractor = PDFExtractorV2()
    
    print(f"Extracting text from: {pdf_path}")
    results = extractor.extract_document(pdf_path)
    
    print("\\n=== EXTRACTION SUMMARY ===")
    print(f"Total pages: {results['total_pages']}")
    print(f"Successful: {results['successful_extractions']}")
    print(f"Failed: {results['failed_extractions']}")
    print(f"Success rate: {results['extraction_summary']['success_rate']:.1f}%")
    print(f"Placeholder rate: {results['extraction_summary']['placeholder_rate']:.1f}%")
    print(f"Processing time: {results['processing_time']:.2f}s")
    
    print("\\n=== METHOD USAGE ===")
    for method, count in results['extraction_summary']['method_usage'].items():
        print(f"{method}: {count} pages")
    
    # Show sample results
    print("\\n=== SAMPLE EXTRACTIONS ===")
    for page_num in sorted(results['pages'].keys())[:3]:
        result = results['pages'][page_num]
        print(f"\\nPage {page_num + 1} ({result.method_used}, confidence: {result.confidence_score:.2f}):")
        sample_text = result.text[:200] + "..." if len(result.text) > 200 else result.text
        print(f"'{sample_text}'")
        if result.warnings:
            print(f"Warnings: {result.warnings}")

if __name__ == "__main__":
    main()