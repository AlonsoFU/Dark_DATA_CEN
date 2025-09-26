#!/usr/bin/env python3
"""
Intelligent Document Classifier for AI Learning
Automatically identifies document types and applies appropriate processing strategies
"""

import os
import re
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class DocumentType:
    """Document type definition with processing strategy"""
    name: str
    file_patterns: List[str]
    processing_strategy: str
    structure: Dict
    ai_features: Dict


class DocumentClassifier:
    """Classifies documents and determines optimal processing strategy"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "document_types.yaml"
        
        self.config_path = config_path
        self.document_types = self._load_document_types()
        self.processing_strategies = self._load_processing_strategies()
    
    def _load_document_types(self) -> Dict[str, DocumentType]:
        """Load document type configurations"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        document_types = {}
        for name, config_data in config['document_types'].items():
            document_types[name] = DocumentType(
                name=name,
                file_patterns=config_data['file_patterns'],
                processing_strategy=config_data['processing_strategy'],
                structure=config_data['structure'],
                ai_features=config_data['ai_features']
            )
        
        return document_types
    
    def _load_processing_strategies(self) -> Dict:
        """Load processing strategy configurations"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config.get('processing_strategies', {})
    
    def classify_document(self, file_path: str) -> Tuple[str, DocumentType, float]:
        """
        Classify a document and return type with confidence score
        
        Returns:
            Tuple of (document_type_name, DocumentType_object, confidence_score)
        """
        file_name = os.path.basename(file_path)
        
        # Pattern matching scoring
        best_match = None
        best_score = 0.0
        
        for type_name, doc_type in self.document_types.items():
            score = self._calculate_pattern_score(file_name, doc_type.file_patterns)
            
            if score > best_score:
                best_score = score
                best_match = (type_name, doc_type)
        
        if best_match and best_score > 0.5:
            return best_match[0], best_match[1], best_score
        
        # Fallback to content analysis if pattern matching fails
        return self._classify_by_content(file_path)
    
    def _calculate_pattern_score(self, filename: str, patterns: List[str]) -> float:
        """Calculate how well filename matches patterns"""
        scores = []
        
        for pattern in patterns:
            # Convert glob pattern to regex
            regex_pattern = pattern.replace('*', '.*').replace('?', '.')
            
            if re.match(regex_pattern, filename, re.IGNORECASE):
                scores.append(1.0)
            elif any(keyword in filename.lower() for keyword in 
                    self._extract_keywords_from_pattern(pattern)):
                scores.append(0.7)
            else:
                scores.append(0.0)
        
        return max(scores) if scores else 0.0
    
    def _extract_keywords_from_pattern(self, pattern: str) -> List[str]:
        """Extract meaningful keywords from file patterns"""
        # Remove wildcards and extensions
        clean_pattern = pattern.replace('*', '').replace('.pdf', '')
        # Split by common separators
        keywords = re.split(r'[-_\s]+', clean_pattern.lower())
        return [k for k in keywords if len(k) > 2]
    
    def _classify_by_content(self, file_path: str) -> Tuple[str, DocumentType, float]:
        """Classify based on document content analysis"""
        # This would implement content-based classification
        # For now, return unknown type
        return "unknown", None, 0.0
    
    def get_processing_strategy(self, document_type: DocumentType) -> Dict:
        """Get processing strategy for a document type"""
        strategy_name = document_type.processing_strategy
        return self.processing_strategies.get(strategy_name, {})
    
    def organize_document(self, file_path: str, base_data_dir: str = None) -> str:
        """
        Organize document into appropriate directory structure
        
        Returns:
            New file path where document was moved
        """
        if base_data_dir is None:
            project_root = Path(__file__).parent.parent.parent
            base_data_dir = project_root / "data" / "documents"
        
        doc_type_name, doc_type, confidence = self.classify_document(file_path)
        
        if doc_type is None:
            # Put unknown documents in a general folder
            target_dir = Path(base_data_dir) / "unknown" / "raw"
        else:
            # Determine target directory based on document type
            target_dir = self._get_target_directory(doc_type_name, base_data_dir)
        
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Move file to organized location
        source_file = Path(file_path)
        target_file = target_dir / source_file.name
        
        # Add classification metadata
        metadata = {
            "original_path": str(source_file),
            "document_type": doc_type_name,
            "confidence": confidence,
            "classified_at": "2025-01-01",  # Replace with actual timestamp
            "processing_strategy": doc_type.processing_strategy if doc_type else "unknown"
        }
        
        metadata_file = target_dir / f"{source_file.stem}_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return str(target_file)
    
    def _get_target_directory(self, doc_type_name: str, base_dir: str) -> Path:
        """Determine target directory for a document type"""
        # Map document types to directory structure
        type_mapping = {
            "power_system_failures": "power_systems/failure_reports",
            "maintenance_reports": "power_systems/maintenance_logs", 
            "compliance_documents": "power_systems/compliance_reports"
        }
        
        subdir = type_mapping.get(doc_type_name, f"unknown/{doc_type_name}")
        return Path(base_dir) / subdir / "raw"


def main():
    """Demo usage of document classifier"""
    classifier = DocumentClassifier()
    
    # Example classification
    test_files = [
        "EAF-089-2025.pdf",
        "mantenimiento-enero-2025.pdf", 
        "compliance-report-Q4.pdf",
        "unknown-document.pdf"
    ]
    
    for file_name in test_files:
        doc_type, doc_obj, confidence = classifier.classify_document(file_name)
        print(f"📄 {file_name}")
        print(f"   Type: {doc_type}")
        print(f"   Confidence: {confidence:.2f}")
        
        if doc_obj:
            strategy = classifier.get_processing_strategy(doc_obj)
            print(f"   Strategy: {doc_obj.processing_strategy}")
            print(f"   Chunk Size: {strategy.get('chunk_size', 'unknown')}")
        print()


if __name__ == "__main__":
    main()