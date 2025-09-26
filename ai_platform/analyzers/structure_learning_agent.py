#!/usr/bin/env python3
"""
Document Structure Learning Agent
Progressive learning system to understand document type patterns
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass
from difflib import SequenceMatcher


@dataclass
class StructurePattern:
    """Represents a learned structural pattern"""
    pattern_id: str
    pattern_type: str  # 'header', 'section', 'table', 'list'
    regex_pattern: str
    confidence: float
    examples: List[str]
    position_hints: List[int]  # Page numbers where found
    frequency: int


@dataclass
class DocumentStructure:
    """Complete document structure representation"""
    document_id: str
    sections: List[Dict[str, Any]]
    headers: List[Dict[str, Any]]
    tables: List[Dict[str, Any]]
    lists: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class StructureLearningAgent:
    """Progressive learning agent for document structures"""
    
    def __init__(self, learning_dir: str = None):
        if learning_dir is None:
            project_root = Path(__file__).parent.parent.parent
            self.learning_dir = project_root / "data" / "structure_learning"
        else:
            self.learning_dir = Path(learning_dir)
        
        self.learning_dir.mkdir(parents=True, exist_ok=True)
        
        # Learning storage
        self.patterns = {}  # pattern_type -> [StructurePattern]
        self.vocabulary = Counter()  # Common terms
        self.section_sequences = []  # Common section orders
        self.confidence_threshold = 0.7
        
        # Load existing learning if available
        self._load_existing_patterns()
    
    def learn_from_documents(self, document_paths: List[str]) -> Dict[str, Any]:
        """
        Progressive learning from multiple documents
        
        Phase 1: Pattern Discovery (3-5 docs)
        Phase 2: Pattern Validation (5-10 docs)  
        Phase 3: Pattern Refinement (10+ docs)
        """
        results = {
            'phase': self._determine_learning_phase(len(document_paths)),
            'patterns_discovered': 0,
            'confidence_scores': {},
            'recommendations': []
        }
        
        print(f"🧠 Learning Phase: {results['phase']}")
        
        for i, doc_path in enumerate(document_paths):
            print(f"📖 Learning from document {i+1}/{len(document_paths)}: {Path(doc_path).name}")
            
            # Extract structure from document
            structure = self._extract_document_structure(doc_path)
            
            # Learn patterns based on current phase
            if results['phase'] == 'discovery':
                self._discover_patterns(structure)
            elif results['phase'] == 'validation':
                self._validate_patterns(structure)
            else:  # refinement
                self._refine_patterns(structure)
        
        # Analyze learning results
        results['patterns_discovered'] = len(self.patterns)
        results['confidence_scores'] = self._calculate_confidence_scores()
        results['recommendations'] = self._generate_recommendations()
        
        # Save learned patterns
        self._save_patterns()
        
        return results
    
    def _determine_learning_phase(self, doc_count: int) -> str:
        """Determine learning phase based on document count"""
        if doc_count <= 5:
            return 'discovery'
        elif doc_count <= 10:
            return 'validation'
        else:
            return 'refinement'
    
    def _extract_document_structure(self, doc_path: str) -> DocumentStructure:
        """Extract structure from a single document"""
        with open(doc_path, 'r', encoding='utf-8') as f:
            if doc_path.endswith('.json'):
                doc_data = json.load(f)
            else:
                # Handle text files
                content = f.read()
                doc_data = {'content': content}
        
        # Extract different structural elements
        structure = DocumentStructure(
            document_id=Path(doc_path).stem,
            sections=self._find_sections(doc_data),
            headers=self._find_headers(doc_data),
            tables=self._find_tables(doc_data),
            lists=self._find_lists(doc_data),
            metadata={'source': doc_path, 'size': len(str(doc_data))}
        )
        
        return structure
    
    def _find_sections(self, doc_data: Dict) -> List[Dict]:
        """Find section patterns in document"""
        sections = []
        
        if 'sections' in doc_data:
            # Already structured
            sections = doc_data['sections']
        elif 'content' in doc_data:
            # Extract from raw content
            content = doc_data['content']
            
            # Common section patterns for power system documents
            section_patterns = [
                r'(?i)^(\d+\.?\s*[A-ZÁÉÍÓÚ][^\\n]+)$',  # Numbered sections
                r'(?i)^([A-ZÁÉÍÓÚ][A-Z\s]{10,})$',       # ALL CAPS headers
                r'(?i)^(ANEXO\s+\d+[^\\n]+)$',            # Anexo sections
                r'(?i)^(INFORMACIÓN\s+[^\\n]+)$',         # Information sections
                r'(?i)^(ELEMENTO\s+[^\\n]+)$',            # Element sections
            ]
            
            for i, pattern in enumerate(section_patterns):
                matches = re.findall(pattern, content, re.MULTILINE)
                for match in matches:
                    sections.append({
                        'id': f'section_{len(sections)}',
                        'title': match.strip(),
                        'pattern_id': i,
                        'type': 'section_header'
                    })
        
        return sections
    
    def _find_headers(self, doc_data: Dict) -> List[Dict]:
        """Find header patterns"""
        headers = []
        
        # Look for various header patterns
        header_patterns = [
            r'(?i)^[A-ZÁÉÍÓÚ\s]{5,}$',  # All caps
            r'^\d+\.\s+[A-Za-z]',       # Numbered
            r'^[A-Z][a-z]+:',           # Title case with colon
        ]
        
        content = str(doc_data)
        for pattern in header_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            headers.extend([{'text': m, 'pattern': pattern} for m in matches])
        
        return headers
    
    def _find_tables(self, doc_data: Dict) -> List[Dict]:
        """Find table patterns"""
        tables = []
        
        # Table indicators
        if 'tables' in doc_data:
            tables = doc_data['tables']
        else:
            content = str(doc_data)
            # Look for table-like structures
            table_patterns = [
                r'\\|.*\\|.*\\|',  # Pipe-separated
                r'\\t.*\\t.*\\t',  # Tab-separated
            ]
            
            for pattern in table_patterns:
                matches = re.findall(pattern, content)
                tables.extend([{'content': m, 'pattern': pattern} for m in matches])
        
        return tables
    
    def _find_lists(self, doc_data: Dict) -> List[Dict]:
        """Find list patterns"""
        lists = []
        
        content = str(doc_data)
        list_patterns = [
            r'^[-•*]\\s+(.+)$',       # Bullet points
            r'^\\d+\\.\\s+(.+)$',     # Numbered lists
            r'^[a-z]\\)\\s+(.+)$',    # Letter lists
        ]
        
        for pattern in list_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            lists.extend([{'text': m, 'pattern': pattern} for m in matches])
        
        return lists
    
    def _discover_patterns(self, structure: DocumentStructure):
        """Phase 1: Discover new patterns"""
        # Learn section patterns
        for section in structure.sections:
            pattern_id = f"section_{section.get('pattern_id', 0)}"
            
            if pattern_id not in self.patterns:
                self.patterns[pattern_id] = StructurePattern(
                    pattern_id=pattern_id,
                    pattern_type='section',
                    regex_pattern='',
                    confidence=0.1,
                    examples=[],
                    position_hints=[],
                    frequency=0
                )
            
            self.patterns[pattern_id].examples.append(section['title'])
            self.patterns[pattern_id].frequency += 1
        
        # Learn vocabulary
        all_text = ' '.join([s.get('title', '') for s in structure.sections])
        words = re.findall(r'\\w+', all_text.lower())
        self.vocabulary.update(words)
    
    def _validate_patterns(self, structure: DocumentStructure):
        """Phase 2: Validate discovered patterns"""
        for pattern_id, pattern in self.patterns.items():
            # Check if pattern appears in new document
            found_examples = 0
            for section in structure.sections:
                if any(example.lower() in section.get('title', '').lower() 
                       for example in pattern.examples):
                    found_examples += 1
            
            # Update confidence based on consistency
            pattern.confidence = min(1.0, pattern.confidence + (found_examples * 0.2))
    
    def _refine_patterns(self, structure: DocumentStructure):
        """Phase 3: Refine and optimize patterns"""
        # Generate regex patterns from examples
        for pattern_id, pattern in self.patterns.items():
            if pattern.confidence > self.confidence_threshold:
                # Create regex from common elements in examples
                pattern.regex_pattern = self._generate_regex_from_examples(pattern.examples)
    
    def _generate_regex_from_examples(self, examples: List[str]) -> str:
        """Generate regex pattern from example strings"""
        if not examples:
            return ''
        
        # Find common structure
        common_parts = []
        for i in range(len(examples[0])):
            chars_at_position = [ex[i] if i < len(ex) else '' for ex in examples]
            if len(set(chars_at_position)) == 1 and chars_at_position[0]:
                common_parts.append(chars_at_position[0])
            else:
                common_parts.append('.')  # Wildcard for differences
        
        return ''.join(common_parts)
    
    def _calculate_confidence_scores(self) -> Dict[str, float]:
        """Calculate confidence scores for all patterns"""
        return {pid: pattern.confidence for pid, pattern in self.patterns.items()}
    
    def _generate_recommendations(self) -> List[str]:
        """Generate learning recommendations"""
        recommendations = []
        
        high_confidence = [p for p in self.patterns.values() if p.confidence > 0.8]
        medium_confidence = [p for p in self.patterns.values() if 0.5 <= p.confidence <= 0.8]
        low_confidence = [p for p in self.patterns.values() if p.confidence < 0.5]
        
        recommendations.append(f"✅ {len(high_confidence)} patterns learned with high confidence")
        recommendations.append(f"⚠️  {len(medium_confidence)} patterns need more examples")
        recommendations.append(f"❌ {len(low_confidence)} patterns are unreliable")
        
        if len(medium_confidence) > 0:
            recommendations.append("🔍 Add 3-5 more documents to improve medium confidence patterns")
        
        if len(self.vocabulary) > 100:
            recommendations.append(f"📚 Rich vocabulary learned: {len(self.vocabulary)} terms")
        
        return recommendations
    
    def _save_patterns(self):
        """Save learned patterns to disk"""
        patterns_file = self.learning_dir / "learned_patterns.json"
        
        patterns_data = {
            'patterns': {
                pid: {
                    'pattern_id': p.pattern_id,
                    'pattern_type': p.pattern_type,
                    'regex_pattern': p.regex_pattern,
                    'confidence': p.confidence,
                    'examples': p.examples,
                    'frequency': p.frequency
                }
                for pid, p in self.patterns.items()
            },
            'vocabulary': dict(self.vocabulary.most_common(100)),
            'last_updated': '2025-01-01'
        }
        
        with open(patterns_file, 'w', encoding='utf-8') as f:
            json.dump(patterns_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Patterns saved to: {patterns_file}")
    
    def _load_existing_patterns(self):
        """Load previously learned patterns"""
        patterns_file = self.learning_dir / "learned_patterns.json"
        
        if patterns_file.exists():
            with open(patterns_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for pid, pdata in data.get('patterns', {}).items():
                self.patterns[pid] = StructurePattern(
                    pattern_id=pdata['pattern_id'],
                    pattern_type=pdata['pattern_type'],
                    regex_pattern=pdata['regex_pattern'],
                    confidence=pdata['confidence'],
                    examples=pdata['examples'],
                    position_hints=[],
                    frequency=pdata['frequency']
                )
            
            self.vocabulary.update(data.get('vocabulary', {}))
            print(f"📖 Loaded {len(self.patterns)} existing patterns")
    
    def analyze_new_document(self, doc_path: str) -> Dict[str, Any]:
        """Analyze a new document using learned patterns"""
        structure = self._extract_document_structure(doc_path)
        
        analysis = {
            'document_id': structure.document_id,
            'matched_patterns': [],
            'confidence_score': 0.0,
            'structure_summary': {},
            'recommendations': []
        }
        
        # Match against learned patterns
        total_confidence = 0
        matched_count = 0
        
        for section in structure.sections:
            for pattern_id, pattern in self.patterns.items():
                if pattern.confidence > self.confidence_threshold:
                    # Check if section matches this pattern
                    similarity = max(
                        SequenceMatcher(None, section.get('title', ''), ex).ratio()
                        for ex in pattern.examples
                    )
                    
                    if similarity > 0.7:
                        analysis['matched_patterns'].append({
                            'pattern_id': pattern_id,
                            'pattern_type': pattern.pattern_type,
                            'similarity': similarity,
                            'matched_text': section.get('title', '')
                        })
                        total_confidence += pattern.confidence
                        matched_count += 1
        
        analysis['confidence_score'] = total_confidence / max(1, matched_count)
        analysis['structure_summary'] = {
            'sections_found': len(structure.sections),
            'headers_found': len(structure.headers),
            'tables_found': len(structure.tables),
            'lists_found': len(structure.lists)
        }
        
        # Generate recommendations
        if analysis['confidence_score'] > 0.8:
            analysis['recommendations'].append("✅ Document structure well understood")
        elif analysis['confidence_score'] > 0.5:
            analysis['recommendations'].append("⚠️ Partial understanding - consider adding to training set")
        else:
            analysis['recommendations'].append("❌ Unknown structure - needs manual review")
        
        return analysis


def main():
    """Demo structure learning process"""
    agent = StructureLearningAgent()
    
    print("🧠 Document Structure Learning Agent")
    print("=" * 50)
    
    # Simulate learning from documents
    sample_docs = [
        "data/raw/power_system_failure_1.json",
        "data/raw/power_system_failure_2.json", 
        "data/raw/power_system_failure_3.json",
    ]
    
    print("📚 Starting progressive learning...")
    results = agent.learn_from_documents(sample_docs)
    
    print(f"\\n🎯 Learning Results:")
    print(f"   Phase: {results['phase']}")
    print(f"   Patterns: {results['patterns_discovered']}")
    print(f"   Recommendations:")
    for rec in results['recommendations']:
        print(f"     • {rec}")


if __name__ == "__main__":
    main()