#!/usr/bin/env python3
"""
Pattern Analysis Tools for Document Structure Learning
Visual and statistical analysis of document patterns
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Any, Tuple
import re
from wordcloud import WordCloud
import numpy as np


class PatternAnalyzer:
    """Advanced pattern analysis and visualization"""
    
    def __init__(self, output_dir: str = None):
        if output_dir is None:
            project_root = Path(__file__).parent.parent.parent
            self.output_dir = project_root / "data" / "analysis_output"
        else:
            self.output_dir = Path(output_dir)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style for visualizations
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
    
    def analyze_document_collection(self, document_paths: List[str]) -> Dict[str, Any]:
        """
        Comprehensive analysis of a document collection
        Returns insights and generates visualizations
        """
        print("🔍 Analyzing document collection...")
        
        analysis_results = {
            'collection_stats': {},
            'pattern_analysis': {},
            'vocabulary_analysis': {},
            'structure_analysis': {},
            'recommendations': []
        }
        
        # Load all documents
        documents = []
        for doc_path in document_paths:
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    if doc_path.endswith('.json'):
                        doc_data = json.load(f)
                        doc_data['_source'] = doc_path
                        documents.append(doc_data)
            except Exception as e:
                print(f"⚠️ Couldn't load {doc_path}: {e}")
        
        if not documents:
            return analysis_results
        
        # 1. Collection Statistics
        analysis_results['collection_stats'] = self._analyze_collection_stats(documents)
        
        # 2. Pattern Analysis
        analysis_results['pattern_analysis'] = self._analyze_patterns(documents)
        
        # 3. Vocabulary Analysis
        analysis_results['vocabulary_analysis'] = self._analyze_vocabulary(documents)
        
        # 4. Structure Analysis
        analysis_results['structure_analysis'] = self._analyze_structure_consistency(documents)
        
        # 5. Generate Visualizations
        self._generate_visualizations(analysis_results)
        
        # 6. Generate Recommendations
        analysis_results['recommendations'] = self._generate_learning_recommendations(analysis_results)
        
        # Save analysis report
        self._save_analysis_report(analysis_results)
        
        return analysis_results
    
    def _analyze_collection_stats(self, documents: List[Dict]) -> Dict[str, Any]:
        """Basic statistics about document collection"""
        stats = {
            'total_documents': len(documents),
            'avg_size': 0,
            'size_distribution': [],
            'file_types': Counter(),
            'languages_detected': Counter()
        }
        
        sizes = []
        for doc in documents:
            doc_size = len(str(doc))
            sizes.append(doc_size)
            
            # Detect file type patterns
            source = doc.get('_source', '')
            if 'EAF' in source:
                stats['file_types']['failure_report'] += 1
            elif 'maintenance' in source.lower():
                stats['file_types']['maintenance'] += 1
            else:
                stats['file_types']['other'] += 1
            
            # Simple language detection
            text_content = str(doc)
            spanish_indicators = ['información', 'elemento', 'empresa', 'fecha']
            english_indicators = ['information', 'element', 'company', 'date']
            
            if any(indicator in text_content.lower() for indicator in spanish_indicators):
                stats['languages_detected']['spanish'] += 1
            elif any(indicator in text_content.lower() for indicator in english_indicators):
                stats['languages_detected']['english'] += 1
        
        stats['avg_size'] = sum(sizes) / len(sizes) if sizes else 0
        stats['size_distribution'] = {
            'min': min(sizes) if sizes else 0,
            'max': max(sizes) if sizes else 0,
            'median': np.median(sizes) if sizes else 0
        }
        
        return stats
    
    def _analyze_patterns(self, documents: List[Dict]) -> Dict[str, Any]:
        """Analyze structural patterns across documents"""
        patterns = {
            'section_patterns': Counter(),
            'header_patterns': Counter(),
            'common_sequences': [],
            'consistency_score': 0.0
        }
        
        all_sections = []
        all_headers = []
        
        for doc in documents:
            # Extract sections
            if 'sections' in doc:
                doc_sections = [s.get('title', '') for s in doc['sections']]
                all_sections.extend(doc_sections)
                
                # Track section sequences
                if len(doc_sections) > 1:
                    patterns['common_sequences'].append(doc_sections)
            
            # Extract headers (look for common header patterns)
            text_content = str(doc)
            header_matches = re.findall(r'^([A-ZÁÉÍÓÚ][A-ZÁÉÍÓÚ\s]{5,})$', text_content, re.MULTILINE)
            all_headers.extend(header_matches)
        
        # Count pattern frequencies
        patterns['section_patterns'] = Counter(all_sections)
        patterns['header_patterns'] = Counter(all_headers)
        
        # Calculate consistency score
        if all_sections:
            unique_sections = len(set(all_sections))
            total_sections = len(all_sections)
            patterns['consistency_score'] = 1 - (unique_sections / total_sections)
        
        return patterns
    
    def _analyze_vocabulary(self, documents: List[Dict]) -> Dict[str, Any]:
        """Analyze vocabulary and terminology patterns"""
        vocabulary = {
            'total_unique_terms': 0,
            'most_common_terms': [],
            'domain_terms': Counter(),
            'technical_terms': Counter(),
            'term_frequency_distribution': {}
        }
        
        all_text = []
        for doc in documents:
            all_text.append(str(doc).lower())
        
        combined_text = ' '.join(all_text)
        
        # Extract words
        words = re.findall(r'\\b[a-záéíóúñ]{3,}\\b', combined_text)
        word_counts = Counter(words)
        
        vocabulary['total_unique_terms'] = len(word_counts)
        vocabulary['most_common_terms'] = word_counts.most_common(20)
        
        # Identify domain-specific terms
        power_system_terms = ['potencia', 'mw', 'generación', 'transmisión', 'falla', 'equipo']
        technical_terms = ['protección', 'sistema', 'operación', 'mantenimiento', 'instalación']
        
        for word, count in word_counts.items():
            if any(term in word for term in power_system_terms):
                vocabulary['domain_terms'][word] = count
            if any(term in word for term in technical_terms):
                vocabulary['technical_terms'][word] = count
        
        return vocabulary
    
    def _analyze_structure_consistency(self, documents: List[Dict]) -> Dict[str, Any]:
        """Analyze how consistent document structures are"""
        structure = {
            'structure_types': Counter(),
            'section_count_distribution': Counter(),
            'common_section_names': Counter(),
            'structural_similarity': 0.0
        }
        
        section_counts = []
        all_section_names = []
        
        for doc in documents:
            if 'sections' in doc:
                section_count = len(doc['sections'])
                section_counts.append(section_count)
                structure['section_count_distribution'][section_count] += 1
                
                # Collect section names
                section_names = [s.get('title', '').lower().strip() for s in doc['sections']]
                all_section_names.extend(section_names)
        
        structure['common_section_names'] = Counter(all_section_names)
        
        # Calculate structural similarity
        if section_counts:
            avg_sections = np.mean(section_counts)
            std_sections = np.std(section_counts)
            structure['structural_similarity'] = 1 - (std_sections / avg_sections) if avg_sections > 0 else 0
        
        return structure
    
    def _generate_visualizations(self, analysis_results: Dict[str, Any]):
        """Generate visualization charts"""
        print("📊 Generating visualizations...")
        
        # 1. Collection Overview
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # File type distribution
        file_types = analysis_results['collection_stats']['file_types']
        ax1.pie(file_types.values(), labels=file_types.keys(), autopct='%1.1f%%')
        ax1.set_title('Document Type Distribution')
        
        # Size distribution
        size_dist = analysis_results['collection_stats']['size_distribution']
        sizes = ['Min', 'Median', 'Max']
        values = [size_dist['min'], size_dist['median'], size_dist['max']]
        ax2.bar(sizes, values)
        ax2.set_title('Document Size Distribution')
        ax2.set_ylabel('Size (characters)')
        
        # Most common sections
        common_sections = analysis_results['pattern_analysis']['section_patterns'].most_common(10)
        if common_sections:
            sections, counts = zip(*common_sections)
            ax3.barh(range(len(sections)), counts)
            ax3.set_yticks(range(len(sections)))
            ax3.set_yticklabels(sections)
            ax3.set_title('Most Common Sections')
            ax3.set_xlabel('Frequency')
        
        # Vocabulary frequency
        vocab_terms = analysis_results['vocabulary_analysis']['most_common_terms'][:10]
        if vocab_terms:
            terms, freqs = zip(*vocab_terms)
            ax4.bar(range(len(terms)), freqs)
            ax4.set_xticks(range(len(terms)))
            ax4.set_xticklabels(terms, rotation=45)
            ax4.set_title('Most Common Terms')
            ax4.set_ylabel('Frequency')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'document_analysis_overview.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Word Cloud
        try:
            all_terms = dict(analysis_results['vocabulary_analysis']['most_common_terms'])
            if all_terms:
                wordcloud = WordCloud(
                    width=800, height=400,
                    background_color='white',
                    max_words=100
                ).generate_from_frequencies(all_terms)
                
                plt.figure(figsize=(10, 5))
                plt.imshow(wordcloud, interpolation='bilinear')
                plt.axis('off')
                plt.title('Document Vocabulary Word Cloud')
                plt.savefig(self.output_dir / 'vocabulary_wordcloud.png', dpi=300, bbox_inches='tight')
                plt.close()
        except ImportError:
            print("⚠️ WordCloud not available, skipping word cloud generation")
    
    def _generate_learning_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """Generate specific recommendations for learning"""
        recommendations = []
        
        stats = analysis_results['collection_stats']
        patterns = analysis_results['pattern_analysis']
        vocab = analysis_results['vocabulary_analysis']
        structure = analysis_results['structure_analysis']
        
        # Collection size recommendations
        if stats['total_documents'] < 5:
            recommendations.append("📈 Add 3-5 more documents for better pattern discovery")
        elif stats['total_documents'] < 10:
            recommendations.append("🔍 Current size good for validation phase - consider adding 5+ more")
        else:
            recommendations.append("✅ Good collection size for pattern refinement")
        
        # Pattern consistency
        if patterns['consistency_score'] > 0.7:
            recommendations.append("✅ High pattern consistency - structure is learnable")
        elif patterns['consistency_score'] > 0.4:
            recommendations.append("⚠️ Moderate consistency - focus on common patterns")
        else:
            recommendations.append("❌ Low consistency - may need manual structure definition")
        
        # Vocabulary richness
        if vocab['total_unique_terms'] > 100:
            recommendations.append("📚 Rich vocabulary - good for NLP model training")
        else:
            recommendations.append("📖 Limited vocabulary - consider adding more diverse documents")
        
        # Structure recommendations
        if structure['structural_similarity'] > 0.6:
            recommendations.append("🏗️ Consistent structure - can create reliable templates")
        else:
            recommendations.append("🔧 Variable structure - focus on flexible parsing strategies")
        
        return recommendations
    
    def _save_analysis_report(self, analysis_results: Dict[str, Any]):
        """Save detailed analysis report"""
        report_path = self.output_dir / 'pattern_analysis_report.json'
        
        # Make results JSON serializable
        json_safe_results = {}
        for key, value in analysis_results.items():
            if isinstance(value, dict):
                json_safe_results[key] = {
                    k: dict(v) if hasattr(v, 'items') else v
                    for k, v in value.items()
                }
            else:
                json_safe_results[key] = value
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(json_safe_results, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Analysis report saved: {report_path}")
    
    def compare_documents(self, doc1_path: str, doc2_path: str) -> Dict[str, Any]:
        """Compare structure between two documents"""
        with open(doc1_path, 'r', encoding='utf-8') as f:
            doc1 = json.load(f)
        with open(doc2_path, 'r', encoding='utf-8') as f:
            doc2 = json.load(f)
        
        comparison = {
            'similarity_score': 0.0,
            'common_sections': [],
            'unique_to_doc1': [],
            'unique_to_doc2': [],
            'size_comparison': {},
            'recommendations': []
        }
        
        # Extract sections
        sections1 = set(s.get('title', '').lower() for s in doc1.get('sections', []))
        sections2 = set(s.get('title', '').lower() for s in doc2.get('sections', []))
        
        # Calculate similarity
        common = sections1.intersection(sections2)
        total_unique = sections1.union(sections2)
        
        if total_unique:
            comparison['similarity_score'] = len(common) / len(total_unique)
        
        comparison['common_sections'] = list(common)
        comparison['unique_to_doc1'] = list(sections1 - sections2)
        comparison['unique_to_doc2'] = list(sections2 - sections1)
        
        # Size comparison
        comparison['size_comparison'] = {
            'doc1_size': len(str(doc1)),
            'doc2_size': len(str(doc2)),
            'size_ratio': len(str(doc1)) / len(str(doc2)) if len(str(doc2)) > 0 else 0
        }
        
        # Generate recommendations
        if comparison['similarity_score'] > 0.7:
            comparison['recommendations'].append("✅ High similarity - same document type")
        elif comparison['similarity_score'] > 0.4:
            comparison['recommendations'].append("⚠️ Moderate similarity - related document types")
        else:
            comparison['recommendations'].append("❌ Low similarity - different document types")
        
        return comparison


def main():
    """Demo pattern analysis"""
    analyzer = PatternAnalyzer()
    
    print("🔍 Pattern Analysis Demo")
    print("=" * 40)
    
    # Simulate analysis of document collection
    sample_docs = [
        "data/raw/power_system_failure_1.json",
        "data/raw/power_system_failure_2.json",
        "data/raw/power_system_failure_3.json",
    ]
    
    # Note: These are example paths - in reality you'd use actual document paths
    print("📊 Analyzing document collection...")
    # results = analyzer.analyze_document_collection(sample_docs)
    
    print("✅ Analysis complete! Check output directory for visualizations.")


if __name__ == "__main__":
    main()