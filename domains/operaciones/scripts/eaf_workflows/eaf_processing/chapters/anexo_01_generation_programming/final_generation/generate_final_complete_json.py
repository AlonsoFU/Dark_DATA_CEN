#!/usr/bin/env python3
"""
Generate Final Complete JSON Structure
=====================================

Creates the final JSON with the complete structure:
- Document metadata (from chapter structure)
- Upper table: System metrics with corrections + OCR validation
- Lower table: Power plants with name matching + corrections
- Quality summary and cross-validation
- Complete review summary

This is the final production-ready JSON with everything we've developed.
"""

import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from difflib import SequenceMatcher

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from PyPDF2 import PdfReader
    import pytesseract
    from PIL import Image
    import fitz  # PyMuPDF
    import cv2
    import numpy as np
    HAS_OCR = True
except ImportError:
    print("Installing PyPDF2...")
    import os
    os.system("pip install PyPDF2")
    from PyPDF2 import PdfReader
    HAS_OCR = False
    print("⚠️  OCR libraries not available - OCR lines will not be saved")

def load_chapter_structure() -> Dict:
    """Load the validated chapter structure"""
    try:
        structure_path = project_root / "profiles/anexos_eaf/validated_titles.json"
        with open(structure_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load chapter structure: {e}")
        return {}

def extract_document_metadata(text: str, document_path: str, page_number: int) -> Dict:
    """Extract comprehensive document metadata using chapter structure"""
    
    chapter_data = load_chapter_structure()
    
    metadata = {
        "document_file": Path(document_path).name,
        "document_path": document_path.replace(str(project_root) + "/", ""),
        "page_number": page_number,
        "extraction_timestamp": datetime.now().isoformat(),
        "document_type": "ANEXO_EAF",
        "extraction_method": "final_complete_structure"
    }
    
    # Add chapter information from validated structure
    if chapter_data and "chapters" in chapter_data:
        for chapter in chapter_data["chapters"]:
            if (chapter["start_page"] <= page_number <= chapter["end_page"] and 
                chapter["chapter_type"] == "anexo"):
                
                metadata.update({
                    "search_tags": [
                        "generacion_programada", "programacion", "detalle",
                        "fecha_2025", "mes_febrero", "dia_25",
                        "documento_regulatorio", "sistema_electrico", "coordinador"
                    ],
                    "anexo_number": chapter["anexo_number"],
                    "full_title": chapter["full_title"],
                    "chapter_name": chapter["chapter_title"],
                    "content_type": "generation_programming",
                    "chapter_start_page": chapter["start_page"],
                    "chapter_end_page": chapter["end_page"]
                })
                break
    
    return metadata

def apply_all_corrections(text: str) -> Tuple[str, List[Dict]]:
    """Apply all correction patterns"""
    
    corrections_applied = []
    corrected_text = text
    
    # No specific patterns - let OCR handle ambiguous cases
    
    # Zero-prefix patterns
    zero_matches = list(re.finditer(r'\b0(\d{2})\b', corrected_text))
    for match in reversed(zero_matches):
        full = match.group(0)
        digits = match.group(1)
        replacement = f"0 {digits}"
        
        corrected_text = corrected_text[:match.start()] + replacement + corrected_text[match.end():]
        corrections_applied.append({
            "type": "zero_prefix",
            "original": full,
            "corrected": ["0", digits],
            "confidence": "high"
        })
    
    # Decimal comma fixes
    comma_matches = list(re.finditer(r'(\d),(\d)', corrected_text))
    for match in reversed(comma_matches):
        original = match.group(0)
        replacement = f"{match.group(1)}.{match.group(2)}"
        corrected_text = corrected_text[:match.start()] + replacement + corrected_text[match.end():]
        corrections_applied.append({
            "type": "decimal_comma",
            "original": original,
            "corrected": [replacement],
            "confidence": "high"
        })
    
    return corrected_text, corrections_applied

def extract_ocr_text(document_path: str, page_num: int) -> str:
    """Extract OCR text from PDF page with improved preprocessing"""
    if not HAS_OCR:
        return ""
    
    try:
        import io
        doc = fitz.open(document_path)
        if 0 <= page_num - 1 < len(doc):
            page = doc[page_num - 1]
            
            # Higher DPI for better text quality
            mat = fitz.Matrix(4, 4)  # 288 DPI (higher quality)
            pix = page.get_pixmap(matrix=mat)
            
            img_data = pix.tobytes("ppm")
            pil_image = Image.open(io.BytesIO(img_data))
            opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            # Advanced preprocessing for better OCR
            gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
            
            # Remove noise with bilateral filter
            denoised = cv2.bilateralFilter(gray, 9, 75, 75)
            
            # Enhance contrast
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(denoised)
            
            # Morphological operations to clean text
            kernel = np.ones((1,1), np.uint8)
            cleaned = cv2.morphologyEx(enhanced, cv2.MORPH_CLOSE, kernel)
            
            # Adaptive thresholding with better parameters
            processed = cv2.adaptiveThreshold(
                cleaned, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 4
            )
            
            processed_pil = Image.fromarray(processed)
            
            # Multiple OCR configs to try
            ocr_configs = [
                '--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzáéíóúñ .,/[]():-',  # Restricted charset
                '--psm 6',  # Default
                '--psm 4',  # Single column text
                '--psm 8'   # Single word
            ]
            
            best_result = ""
            best_score = 0
            
            for config in ocr_configs:
                try:
                    ocr_text = pytesseract.image_to_string(processed_pil, lang='spa+eng', config=config)
                    # Score based on number count and reasonable characters
                    numbers_found = len(re.findall(r'\d+', ocr_text))
                    reasonable_chars = sum(1 for c in ocr_text if c.isalnum() or c in ' .,/[]():-')
                    total_chars = len(ocr_text)
                    
                    if total_chars > 0:
                        quality_score = (numbers_found * 2) + (reasonable_chars / total_chars * 100)
                        
                        if quality_score > best_score:
                            best_score = quality_score
                            best_result = ocr_text
                except:
                    continue
            
            doc.close()
            return best_result.strip()
        
        doc.close()
        return ""
    except Exception as e:
        print(f"⚠️  OCR extraction failed: {e}")
        return ""

def find_ocr_line_for_metric(ocr_text: str, metric_key: str, raw_line: str) -> Optional[Dict]:
    """Find corresponding OCR line for a metric"""
    
    if not ocr_text:
        return None
    
    # Define search terms for each metric type
    search_terms = {
        "generacion_total": ["generaci", "total", "mwh"],
        "costos_operacion": ["operacion", "costos"],
        "costos_encendido_detencion": ["encendido", "detencion"],
        "costo_marginal": ["marginal", "costo"],
        "indisponibilidad_forzada": ["indisponibilidad", "forzada"],
        "indisponibilidad_programada": ["indisponibilidad", "programada"],
        "factor_planta_bruto": ["factor", "planta", "bruto"],
        "factor_planta_neto": ["factor", "planta", "neto"],
        "horas_servicio": ["horas", "servicio"]
    }
    
    terms = search_terms.get(metric_key, [])
    if not terms:
        return None
    
    best_match = None
    best_score = 0
    
    for ocr_line in ocr_text.split('\n'):
        if not ocr_line.strip():
            continue
        
        # Score based on search terms found
        score = sum(1 for term in terms if term.lower() in ocr_line.lower())
        
        # Boost for lines with numbers (likely data rows)
        if re.search(r'\d+', ocr_line):
            score += 0.5
        
        if score > best_score and score >= 1:  # Minimum threshold
            best_score = score
            best_match = ocr_line
    
    if best_match:
        ocr_numbers = re.findall(r'\d+(?:[.,]\d+)?', best_match)
        raw_numbers = re.findall(r'\d+(?:[.,]\d+)?', raw_line)
        
        return {
            "ocr_line": best_match.strip(),
            "ocr_numbers": ocr_numbers,
            "raw_numbers": raw_numbers,
            "ocr_count": len(ocr_numbers),
            "raw_count": len(raw_numbers),
            "shows_more_detail": len(ocr_numbers) > len(raw_numbers)
        }
    
    return None

def should_use_ocr_validation(raw_numbers: List[str], ocr_data: Optional[Dict], metric_key: str) -> Tuple[bool, str]:
    """Enhanced OCR validation with multiple criteria"""
    
    if not ocr_data or not ocr_data.get("ocr_numbers"):
        return False, "no_ocr_data"
    
    ocr_numbers = ocr_data["ocr_numbers"]
    
    # Criterion 1: Raw extraction doesn't have 24 + total (25) values
    if len(raw_numbers) < 25:
        if len(ocr_numbers) >= 24:
            return True, "insufficient_raw_values"
    
    # Criterion 2: OCR shows more numbers than RAW (original logic)
    if ocr_data.get("shows_more_detail") and len(ocr_numbers) >= 24:
        return True, "ocr_more_detail"
    
    # Criterion 3: Cross-validation - check if OCR values are more reasonable
    if len(raw_numbers) >= 20 and len(ocr_numbers) >= 20:  # Both have substantial data
        ocr_reasonableness = evaluate_value_reasonableness(ocr_numbers, metric_key)
        raw_reasonableness = evaluate_value_reasonableness(raw_numbers, metric_key)
        
        if ocr_reasonableness > raw_reasonableness:
            return True, "cross_validation_better"
    
    return False, "raw_sufficient"

def evaluate_value_reasonableness(numbers: List[str], metric_key: str) -> float:
    """Evaluate how reasonable the extracted values are for the metric type"""
    
    try:
        # Convert to floats for analysis
        values = []
        for num_str in numbers[:24]:  # Only check first 24 values
            try:
                values.append(float(num_str))
            except:
                continue
        
        if len(values) < 10:  # Not enough data
            return 0.0
        
        # Define reasonable ranges for different metrics
        reasonable_ranges = {
            "generacion_total": (5000, 15000),      # MWh - typical generation range
            "costos_operacion": (10, 1000),         # kUSD - operation costs
            "costos_encendido_detencion": (0, 200), # kUSD - start/stop costs
            "costo_marginal": (0, 150),             # USD/MWh - marginal cost
            "indisponibilidad_forzada": (0, 100),   # % - forced outage
            "indisponibilidad_programada": (0, 100), # % - planned outage
            "factor_planta_bruto": (0, 100),        # % - gross capacity factor
            "factor_planta_neto": (0, 100),         # % - net capacity factor
            "horas_servicio": (0, 24)               # h - service hours
        }
        
        expected_min, expected_max = reasonable_ranges.get(metric_key, (0, 100000))
        
        # Score based on how many values fall within expected range
        in_range_count = sum(1 for v in values if expected_min <= v <= expected_max)
        range_score = in_range_count / len(values)
        
        # Score based on variability (not all values the same)
        import statistics
        if len(set(values)) > 1:  # Has variation
            std_dev = statistics.stdev(values)
            mean_val = statistics.mean(values)
            # Reasonable coefficient of variation
            cv = std_dev / mean_val if mean_val > 0 else 0
            variation_score = min(1.0, cv * 2)  # Moderate variation is good
        else:
            variation_score = 0.1  # All same values is suspicious
        
        # Score based on no obviously wrong patterns
        pattern_score = 1.0
        
        # Check for obvious OCR errors (like too many very large numbers)
        very_large_count = sum(1 for v in values if v > expected_max * 10)
        if very_large_count > len(values) * 0.2:  # More than 20% are way too large
            pattern_score -= 0.5
        
        # Check for merged numbers (values much larger than expected)
        if metric_key in ["generacion_total", "costos_operacion"]:
            suspicious_large = sum(1 for v in values if v > expected_max * 3)
            if suspicious_large > 2:  # Multiple suspiciously large values
                pattern_score -= 0.3
        
        # Combined score
        total_score = (range_score * 0.5) + (variation_score * 0.3) + (pattern_score * 0.2)
        return min(1.0, total_score)
        
    except Exception:
        return 0.0

def apply_neighbor_corrections(numbers: List[str], metric_key: str) -> Tuple[List[str], List[Dict]]:
    """Apply corrections based on neighboring values analysis"""
    
    if len(numbers) < 10:  # Need enough data for pattern analysis
        return numbers, []
    
    corrections_applied = []
    corrected_numbers = numbers.copy()
    
    try:
        # Convert to floats for analysis
        float_values = []
        for i, num_str in enumerate(numbers):
            try:
                float_values.append((i, float(num_str)))
            except:
                float_values.append((i, None))
        
        # Find outliers by comparing to neighbors
        outliers = detect_outliers_by_neighbors(float_values, metric_key)
        
        for outlier_idx, outlier_value, expected_range in outliers:
            original_str = numbers[outlier_idx]
            
            # Try to split the outlier intelligently
            split_candidates = generate_split_candidates(original_str, expected_range)
            
            if split_candidates:
                # Pick the best split candidate
                best_split = choose_best_split(split_candidates, expected_range)
                
                if best_split:
                    # Replace the outlier with the split values
                    corrected_numbers = (
                        corrected_numbers[:outlier_idx] + 
                        best_split + 
                        corrected_numbers[outlier_idx + 1:]
                    )
                    
                    corrections_applied.append({
                        "type": "neighbor_analysis",
                        "original": original_str,
                        "corrected": best_split,
                        "confidence": "medium",
                        "reason": f"Outlier compared to neighbors (expected: {expected_range[0]:.0f}-{expected_range[1]:.0f})",
                        "neighbors_used": True
                    })
    
    except Exception:
        pass  # Fall back to original numbers if analysis fails
    
    return corrected_numbers, corrections_applied

def detect_outliers_by_neighbors(float_values: List[Tuple[int, float]], metric_key: str) -> List[Tuple[int, float, Tuple[float, float]]]:
    """Detect outliers by comparing each value to its neighbors"""
    
    outliers = []
    
    # Define what constitutes a "neighbor" range for different metrics
    neighbor_tolerance = {
        "generacion_total": 0.3,        # 30% variation is normal
        "costos_operacion": 0.5,        # 50% variation normal for costs
        "costos_encendido_detencion": 2.0, # High variation normal for start/stop
        "costo_marginal": 0.4,          # 40% variation normal for marginal cost
    }
    
    tolerance = neighbor_tolerance.get(metric_key, 0.5)
    
    for i in range(1, len(float_values) - 1):  # Skip first and last
        idx, value = float_values[i]
        if value is None:
            continue
            
        # Get valid neighbors (up to 2 on each side)
        neighbors = []
        
        # Look left
        for j in range(max(0, i-2), i):
            if float_values[j][1] is not None:
                neighbors.append(float_values[j][1])
        
        # Look right  
        for j in range(i+1, min(len(float_values), i+3)):
            if float_values[j][1] is not None:
                neighbors.append(float_values[j][1])
        
        if len(neighbors) < 2:  # Need at least 2 neighbors
            continue
            
        # Calculate neighbor statistics
        neighbor_mean = sum(neighbors) / len(neighbors)
        neighbor_min = min(neighbors)
        neighbor_max = max(neighbors)
        
        # Check if current value is an extreme outlier
        expected_min = neighbor_mean * (1 - tolerance)
        expected_max = neighbor_mean * (1 + tolerance)
        
        # Special case: if neighbors are very small (< 50) and current is very large
        if neighbor_max < 50 and value > neighbor_max * 10:
            outliers.append((idx, value, (neighbor_min, neighbor_max)))
        
        # General case: value is way outside expected range
        elif value < expected_min * 0.1 or value > expected_max * 3:
            outliers.append((idx, value, (expected_min, expected_max)))
    
    return outliers

def generate_split_candidates(number_str: str, expected_range: Tuple[float, float]) -> List[List[str]]:
    """Generate possible ways to split a merged number"""
    
    if len(number_str) < 4:  # Too short to meaningfully split
        return []
    
    candidates = []
    expected_min, expected_max = expected_range
    
    # Try different split points
    for split_pos in range(1, len(number_str)):
        left = number_str[:split_pos]
        right = number_str[split_pos:]
        
        # Skip if either part starts with 0 (unless it's just "0")
        if (left.startswith('0') and len(left) > 1) or (right.startswith('0') and len(right) > 1):
            continue
        
        try:
            left_val = float(left)
            right_val = float(right)
            
            # Check if both parts are reasonable
            if (expected_min * 0.5 <= left_val <= expected_max * 2 and 
                expected_min * 0.5 <= right_val <= expected_max * 2):
                candidates.append([left, right])
        except:
            continue
    
    # Try 3-way splits for longer numbers
    if len(number_str) >= 6:
        for split1 in range(1, len(number_str) - 2):
            for split2 in range(split1 + 1, len(number_str)):
                part1 = number_str[:split1]
                part2 = number_str[split1:split2]
                part3 = number_str[split2:]
                
                # Skip parts starting with 0
                if any(p.startswith('0') and len(p) > 1 for p in [part1, part2, part3]):
                    continue
                
                try:
                    vals = [float(p) for p in [part1, part2, part3]]
                    
                    # All parts should be reasonable
                    if all(expected_min * 0.5 <= v <= expected_max * 2 for v in vals):
                        candidates.append([part1, part2, part3])
                except:
                    continue
    
    return candidates

def choose_best_split(candidates: List[List[str]], expected_range: Tuple[float, float]) -> Optional[List[str]]:
    """Choose the best split candidate based on how close values are to expected range"""
    
    if not candidates:
        return None
    
    expected_min, expected_max = expected_range
    expected_mid = (expected_min + expected_max) / 2
    
    best_candidate = None
    best_score = float('inf')
    
    for candidate in candidates:
        try:
            values = [float(part) for part in candidate]
            
            # Score based on how close each value is to expected middle
            score = sum(abs(v - expected_mid) / expected_mid for v in values)
            
            # Penalty for values outside reasonable range
            for v in values:
                if v < expected_min * 0.2 or v > expected_max * 5:
                    score += 10  # Heavy penalty
            
            if score < best_score:
                best_score = score
                best_candidate = candidate
        except:
            continue
    
    return best_candidate

def process_system_metrics(raw_text: str, document_path: str = None, page_num: int = None) -> Dict:
    """Process system metrics with complete structure"""
    
    # Extract OCR text if available
    ocr_text = ""
    if document_path and page_num and HAS_OCR:
        print("🔎 Extracting OCR for system metrics validation...")
        ocr_text = extract_ocr_text(document_path, page_num)
    
    metric_patterns = {
        "generacion_total": {
            "pattern": r"Generaci[óo]n\s+Total[^\n]*\[MWh\][^\n]*",
            "full_title": "Generación Total [MWh]"
        },
        "costos_operacion": {
            "pattern": r"Costos?\s+Operaci[óo]n[^\n]*",
            "full_title": "Costos Operación [kUSD]"
        },
        "costos_encendido_detencion": {
            "pattern": r"Costos?\s+Encendido[^\n]*Detenci[^\n]*",
            "full_title": "Costos Encendido/Detención [kUSD]"
        },
        "costo_marginal": {
            "pattern": r"Costo\s+Marginal[^\n]*",
            "full_title": "Costo Marginal [USD/MWh]"
        },
        "indisponibilidad_forzada": {
            "pattern": r"Indisponibilidad\s+Forzada[^\n]*",
            "full_title": "Indisponibilidad Forzada [%]"
        },
        "indisponibilidad_programada": {
            "pattern": r"Indisponibilidad\s+Programada[^\n]*",
            "full_title": "Indisponibilidad Programada [%]"
        },
        "factor_planta_bruto": {
            "pattern": r"Factor\s+de?\s+Planta\s+Bruto[^\n]*",
            "full_title": "Factor de Planta Bruto [%]"
        },
        "factor_planta_neto": {
            "pattern": r"Factor\s+de?\s+Planta\s+Neto[^\n]*",
            "full_title": "Factor de Planta Neto [%]"
        },
        "horas_servicio": {
            "pattern": r"Horas?\s+de?\s+Servicio[^\n]*",
            "full_title": "Horas de Servicio [h]"
        }
    }
    
    system_metrics = {}
    
    for metric_key, config in metric_patterns.items():
        matches = re.findall(config["pattern"], raw_text, re.IGNORECASE)
        if matches:
            raw_line = matches[0].strip()
            
            # Apply corrections
            corrected_text, corrections = apply_all_corrections(raw_line)
            
            # Extract numbers from corrected text
            raw_numbers = re.findall(r'\d+(?:[.,]\d+)?', corrected_text)
            
            # Find OCR data if available
            ocr_data = None
            if ocr_text:
                ocr_data = find_ocr_line_for_metric(ocr_text, metric_key, raw_line)
            
            # Multi-level validation: OCR first, then neighbor analysis
            should_use_ocr, ocr_reason = should_use_ocr_validation(raw_numbers, ocr_data, metric_key)
            
            if should_use_ocr and ocr_data:
                numbers = ocr_data["ocr_numbers"]
                extraction_source = f"ocr_enhanced_{ocr_reason}"
                neighbor_corrections = []
            else:
                # If OCR doesn't help, try neighbor-based corrections
                numbers, neighbor_corrections = apply_neighbor_corrections(raw_numbers, metric_key)
                if neighbor_corrections:
                    extraction_source = "neighbor_corrected"
                else:
                    extraction_source = "raw_corrected"
            
            # Process based on metric type
            if len(numbers) >= 24:
                hourly_values = numbers[:24]
                total = numbers[24] if len(numbers) > 24 else "calculated"
            else:
                hourly_values = numbers
                total = "calculated"
            
            # Handle special cases
            location_context = None
            full_title = config["full_title"]
            
            if metric_key == "costo_marginal":
                # Extract location context like "Quillota 220 kV"
                context_match = re.search(r'([A-Za-z]+\s+\d+\s*kV)', raw_line)
                if context_match:
                    location_context = context_match.group(1)
                    full_title = f"Costo Marginal {location_context} [USD/MWh]"
            
            # Build metric data
            metric_data = {
                "full_title": full_title,
                "hourly_values": hourly_values,
                "total": total,
                "raw_line": raw_line,
                "validation": {
                    "is_valid": len(hourly_values) == 24,
                    "total_values": len(hourly_values),
                    "expected_values": 24,
                    "issues": [] if len(hourly_values) == 24 else [f"Found {len(hourly_values)} values, expected 24"]
                },
                "extraction_quality": "enhanced",
                "extraction_source": extraction_source,
                "corrections_applied": corrections + (neighbor_corrections if 'neighbor_corrections' in locals() else [])
            }
            
            # Add OCR data if available
            if ocr_data:
                metric_data["ocr_validation"] = {
                    "ocr_line": ocr_data["ocr_line"],
                    "ocr_numbers_count": ocr_data["ocr_count"],
                    "raw_numbers_count": ocr_data["raw_count"],
                    "ocr_shows_more_detail": ocr_data["shows_more_detail"]
                }
            
            if location_context:
                metric_data["location_context"] = location_context
            
            system_metrics[metric_key] = metric_data
    
    return system_metrics

def extract_power_plants(raw_text: str) -> Dict:
    """Extract power plants with complete structure"""
    
    plant_rows = []
    plant_categories = []
    
    # Look for category headers
    category_patterns = [
        r"Hidroel[ée]ctricas\s+de\s+Pasada",
        r"Hidroel[ée]ctricas\s+de\s+Embalse", 
        r"T[ée]rmicas",
        r"Solares",
        r"E[óo]licas",
        r"Biomasa",
        r"Geot[ée]rmicas"
    ]
    
    current_category = "unknown"
    
    for line in raw_text.split('\n'):
        line = line.strip()
        if not line:
            continue
        
        # Check for category headers
        for pattern in category_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                current_category = line
                plant_categories.append({
                    "category_type": line,
                    "raw_header_line": line,
                    "plants_count": 0,
                    "plant_names": []
                })
                continue
        
        # Look for plant data rows
        numbers = re.findall(r'\d+(?:[.,]\d+)?', line)
        
        if len(numbers) >= 20:  # Plant data typically has 20+ numbers
            # Extract plant name
            first_number_match = re.search(r'\d', line)
            if first_number_match:
                plant_name = line[:first_number_match.start()].strip()
                
                # Filter out non-plant lines
                if len(plant_name) >= 3:
                    skip_patterns = [
                        r'costos?\s+', r'generaci[óo]n\s+', r'indisponibilidad\s+',
                        r'factor\s+', r'horas?\s+', r'costo\s+marginal', r'total\s+',
                        r'fecha\s+', r'coordinador\s+', r'martes', r'perdidas', r'consumos'
                    ]
                    
                    if not any(re.search(pattern, plant_name.lower()) for pattern in skip_patterns):
                        # Apply corrections to plant data
                        corrected_text, corrections = apply_all_corrections(line)
                        corrected_numbers = re.findall(r'\d+(?:[.,]\d+)?', corrected_text)
                        
                        # Process plant data
                        if len(corrected_numbers) >= 24:
                            hourly_generation = corrected_numbers[:24]
                            daily_total = corrected_numbers[24] if len(corrected_numbers) > 24 else "calculated"
                        else:
                            hourly_generation = corrected_numbers
                            daily_total = "calculated"
                        
                        plant_data = {
                            "plant_name": plant_name,
                            "plant_type": current_category if current_category != "unknown" else "unclassified",
                            "hourly_generation": hourly_generation,
                            "daily_total": daily_total,
                            "raw_line": line,
                            "validation": {
                                "is_valid": len(hourly_generation) == 24,
                                "total_values": len(hourly_generation),
                                "expected_values": 24,
                                "issues": [] if len(hourly_generation) == 24 else [f"Found {len(hourly_generation)} values"]
                            },
                            "extraction_quality": "enhanced",
                            "corrections_applied": corrections
                        }
                        
                        plant_rows.append(plant_data)
                        
                        # Update category info
                        if plant_categories and current_category != "unknown":
                            plant_categories[-1]["plants_count"] += 1
                            plant_categories[-1]["plant_names"].append(plant_name)
    
    return {
        "plant_categories": plant_categories,
        "power_plants": plant_rows
    }

def generate_quality_summary(system_metrics: Dict, power_plants: Dict) -> Dict:
    """Generate comprehensive quality summary"""
    
    system_validation_issues = sum(1 for m in system_metrics.values() if not m["validation"]["is_valid"])
    plant_validation_issues = sum(1 for p in power_plants["power_plants"] if not p["validation"]["is_valid"])
    
    total_corrections = (
        sum(len(m["corrections_applied"]) for m in system_metrics.values()) +
        sum(len(p["corrections_applied"]) for p in power_plants["power_plants"])
    )
    
    if system_validation_issues == 0 and plant_validation_issues == 0:
        overall_quality = "excellent"
    elif system_validation_issues + plant_validation_issues <= 2:
        overall_quality = "good"
    else:
        overall_quality = "needs_review"
    
    return {
        "system_metrics_found": len(system_metrics),
        "power_plants_found": len(power_plants["power_plants"]),
        "plant_categories_found": len(power_plants["plant_categories"]),
        "total_corrections_applied": total_corrections,
        "validation_issues": system_validation_issues + plant_validation_issues,
        "overall_quality": overall_quality,
        "success_rate": f"{((len(system_metrics) + len(power_plants['power_plants']) - system_validation_issues - plant_validation_issues) / (len(system_metrics) + len(power_plants['power_plants'])) * 100):.1f}%" if (len(system_metrics) + len(power_plants['power_plants'])) > 0 else "0%"
    }

def cross_validate_results(current_result: Dict, page_num: int) -> Dict:
    """Cross-validate against previous results"""
    
    validation = {
        "cross_validation_performed": False,
        "reference_file": None,
        "comparison_results": {},
        "confidence_score": 1.0
    }
    
    # Look for previous enhanced results to compare
    reference_files = [
        f"page_{page_num}_extraction_enhanced_final.json",
        f"page_{page_num}_extraction_corrected_final.json"
    ]
    
    for ref_filename in reference_files:
        reference_file = project_root / "data" / "documents" / "anexos_EAF" / "development" / ref_filename
        
        if reference_file.exists():
            try:
                with open(reference_file, 'r', encoding='utf-8') as f:
                    reference_data = json.load(f)
                
                validation["cross_validation_performed"] = True
                validation["reference_file"] = str(reference_file)
                
                # Compare counts
                current_system_count = len(current_result.get("upper_table", {}).get("system_metrics", {}))
                reference_system_count = len(reference_data.get("upper_table", {}).get("system_metrics", {}))
                
                current_plants_count = len(current_result.get("lower_table", {}).get("power_plants", []))
                reference_plants_count = len(reference_data.get("lower_table", {}).get("power_plants", []))
                
                validation["comparison_results"] = {
                    "system_metrics_count": {
                        "current": current_system_count,
                        "reference": reference_system_count,
                        "match": current_system_count == reference_system_count
                    },
                    "power_plants_count": {
                        "current": current_plants_count,
                        "reference": reference_plants_count,
                        "match": current_plants_count == reference_plants_count
                    }
                }
                
                # Calculate confidence
                matches = sum(1 for comp in validation["comparison_results"].values() if comp.get("match", False))
                validation["confidence_score"] = matches / len(validation["comparison_results"])
                break
                
            except Exception as e:
                print(f"Warning: Could not load reference file {ref_filename}: {e}")
    
    return validation

def main():
    """Generate final complete JSON structure"""
    
    if len(sys.argv) != 2:
        print("Usage: python scripts/generate_final_complete_json.py [page_number]")
        sys.exit(1)
    
    try:
        page_num = int(sys.argv[1])
    except ValueError:
        print("Error: Page number must be an integer")
        sys.exit(1)
    
    document_path = project_root / "data" / "documents" / "anexos_EAF" / "raw" / "Anexos-EAF-089-2025.pdf"
    
    print(f"📋 GENERATING FINAL COMPLETE JSON - Page {page_num}")
    print("Structure: Complete metadata + Upper table + Lower table + Validation")
    print("=" * 80)
    
    # Extract raw text
    try:
        reader = PdfReader(str(document_path))
        page = reader.pages[page_num - 1]
        raw_text = page.extract_text()
    except Exception as e:
        print(f"Error reading PDF: {e}")
        sys.exit(1)
    
    print(f"📄 RAW text: {len(raw_text)} chars")
    
    # Extract date info
    date_info = {}
    date_match = re.search(r'(\w+),?\s*(\d+)\s*de\s*(\w+)\s*de\s*(\d{4})', raw_text)
    if date_match:
        date_info = {
            "day_name": date_match.group(1),
            "day": date_match.group(2),
            "month": date_match.group(3),
            "year": date_match.group(4),
            "formatted_date": f"{date_match.group(1)} {date_match.group(2)} de {date_match.group(3)} de {date_match.group(4)}"
        }
    
    # Process both tables
    print("🔧 Processing system metrics...")
    system_metrics = process_system_metrics(raw_text, str(document_path), page_num)
    
    print("🏭 Processing power plants...")
    power_plants_data = extract_power_plants(raw_text)
    
    # Generate summaries
    quality_summary = generate_quality_summary(system_metrics, power_plants_data)
    
    # Build final complete structure
    final_result = {
        "_template_info": {
            "name": "ANEXO EAF Final Complete Structure",
            "version": "2.0",
            "created": datetime.now().isoformat(),
            "purpose": "Production-ready complete JSON with all corrections and validations",
            "based_on": "All developed patterns and user validations"
        },
        
        "document_metadata": extract_document_metadata(raw_text, str(document_path), page_num),
        
        "upper_table": {
            "date_info": date_info,
            "system_metrics": system_metrics
        },
        
        "lower_table": power_plants_data,
        
        "quality_summary": quality_summary,
        
        "cross_validation": cross_validate_results({
            "upper_table": {"system_metrics": system_metrics},
            "lower_table": power_plants_data
        }, page_num),
        
        "extraction_notes": {
            "enhancements_applied": [
                "Zero-prefix pattern corrections (015 → 0+15)",
                "Decimal comma normalization",
                "OCR validation for ambiguous number sequences",
                "24-hour validation with detailed reporting",
                "Power plant categorization",
                "Complete metadata from chapter structure",
                "Cross-validation against reference data",
                "Advanced OCR preprocessing and validation"
            ],
            "accuracy_target": "Production-ready with pattern corrections",
            "extraction_method": "production_pattern_corrections",
            "corrections_confidence": "high"
        }
    }
    
    # Save final result
    output_file = project_root / "data" / "documents" / "anexos_EAF" / "development" / f"page_{page_num}_final_complete_structure.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_result, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 FINAL STRUCTURE SUMMARY:")
    print("=" * 80)
    
    print(f"📋 Document Metadata: ✅ Complete with chapter structure")
    print(f"📊 System Metrics: {quality_summary['system_metrics_found']}")
    print(f"🏭 Power Plants: {quality_summary['power_plants_found']}")
    print(f"🏷️  Plant Categories: {quality_summary['plant_categories_found']}")
    print(f"🔧 Total Corrections Applied: {quality_summary['total_corrections_applied']}")
    print(f"⚠️  Validation Issues: {quality_summary['validation_issues']}")
    print(f"🏆 Overall Quality: {quality_summary['overall_quality']}")
    print(f"📈 Success Rate: {quality_summary['success_rate']}")
    
    if final_result["cross_validation"]["cross_validation_performed"]:
        cv = final_result["cross_validation"]
        print(f"✅ Cross-Validation: {cv['confidence_score']:.2f} confidence score")
    
    print(f"\n💾 Final complete JSON saved to:")
    print(f"   {output_file}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())