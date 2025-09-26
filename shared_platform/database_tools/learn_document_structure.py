#!/usr/bin/env python3
"""
Document Structure Learning Script
Easy-to-use script for learning document structures progressively
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ai_platform.core.iterative_learner import IterativeLearner
from ai_platform.analyzers.pattern_analyzer import PatternAnalyzer


def main():
    parser = argparse.ArgumentParser(
        description="Learn document structure patterns progressively",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start with 3-5 documents for discovery
  python scripts/learn_document_structure.py --documents data/raw/*.json --phase discovery
  
  # Validate with more documents  
  python scripts/learn_document_structure.py --documents data/raw/*.json --phase validation
  
  # Test learned structure
  python scripts/learn_document_structure.py --test data/test/*.json
  
  # Analyze patterns only
  python scripts/learn_document_structure.py --analyze data/raw/*.json
        """
    )
    
    parser.add_argument(
        '--documents', '-d',
        nargs='+',
        help='Document paths to learn from'
    )
    
    parser.add_argument(
        '--phase', '-p', 
        choices=['discovery', 'validation', 'refinement', 'auto'],
        default='auto',
        help='Learning phase (auto-detects by default)'
    )
    
    parser.add_argument(
        '--test', '-t',
        nargs='+',
        help='Test documents to validate learned structure'
    )
    
    parser.add_argument(
        '--analyze', '-a',
        nargs='+', 
        help='Only analyze patterns without learning'
    )
    
    parser.add_argument(
        '--confidence-target', '-c',
        type=float,
        default=0.85,
        help='Target confidence score (default: 0.85)'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        default=None,
        help='Output directory for results'
    )
    
    parser.add_argument(
        '--batch-size', '-b',
        type=int,
        default=None,
        help='Documents per learning batch (auto-determined if not set)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.documents, args.test, args.analyze]):
        parser.error("Must provide --documents, --test, or --analyze")
    
    # Initialize learner
    learner = IterativeLearner(workspace_dir=args.output_dir)
    
    print("📖 Document Structure Learning Tool")
    print("=" * 50)
    
    # Analyze mode
    if args.analyze:
        print(f"🔍 Analyzing {len(args.analyze)} documents...")
        analyzer = PatternAnalyzer(args.output_dir)
        results = analyzer.analyze_document_collection(args.analyze)
        
        print("\\n📊 Analysis Results:")
        print(f"   Documents: {results['collection_stats']['total_documents']}")
        print(f"   Patterns Found: {len(results['pattern_analysis']['section_patterns'])}")
        print(f"   Consistency: {results['pattern_analysis']['consistency_score']:.3f}")
        print(f"   Unique Terms: {results['vocabulary_analysis']['total_unique_terms']}")
        
        print("\\n💡 Recommendations:")
        for rec in results['recommendations']:
            print(f"   • {rec}")
        
        return
    
    # Test mode
    if args.test:
        print(f"🧪 Testing learned structure on {len(args.test)} documents...")
        results = learner.validate_learned_structure(args.test)
        
        print("\\n📊 Validation Results:")
        print(f"   Mean Accuracy: {results['overall_metrics'].get('mean_accuracy', 0):.3f}")
        print(f"   Mean Coverage: {results['overall_metrics'].get('mean_coverage', 0):.3f}")
        print(f"   Pass Rate: {results['overall_metrics'].get('pass_rate', 0):.3f}")
        
        if results['failed_documents']:
            print(f"\\n⚠️  Failed Documents ({len(results['failed_documents'])}):")
            for failed in results['failed_documents'][:5]:  # Show first 5
                print(f"   • {failed['document']}: {failed.get('issue', 'unknown')}")
        
        print("\\n💡 Recommendations:")
        for rec in results['recommendations']:
            print(f"   • {rec}")
        
        return
    
    # Learning mode
    if args.documents:
        documents = []
        for pattern in args.documents:
            documents.extend(Path().glob(pattern))
        
        documents = [str(d) for d in documents if d.is_file()]
        
        if not documents:
            print("❌ No documents found matching the patterns")
            return
        
        print(f"📚 Learning from {len(documents)} documents...")
        
        # Determine learning strategy
        if args.phase == 'auto':
            print("🎯 Planning adaptive learning strategy...")
            strategy = learner.adaptive_learning_strategy(
                documents, 
                target_confidence=args.confidence_target
            )
            
            print(f"\\n📋 Learning Plan:")
            print(f"   Estimated Sessions: {strategy['estimated_sessions']}")
            print(f"   Estimated Duration: {strategy['estimated_duration_hours']:.1f} hours")
            print(f"   Target Confidence: {args.confidence_target}")
            
            # Execute learning plan
            for i, batch_info in enumerate(strategy['batches'], 1):
                print(f"\\n🚀 Batch {i}/{len(strategy['batches'])} ({batch_info['learning_phase']} phase)")
                
                session = learner.start_learning_cycle(
                    batch_info['documents'],
                    learning_goals={'min_confidence': args.confidence_target}
                )
                
                print(f"   ✅ Session {session.session_id} completed")
                print(f"   📈 Confidence: {session.confidence_improvement:.3f}")
                
                # Check if target reached
                if session.confidence_improvement >= args.confidence_target:
                    print(f"\\n🎉 Target confidence reached! Stopping early.")
                    break
        
        else:
            # Single batch learning
            if args.batch_size:
                # Process in specified batch sizes
                for i in range(0, len(documents), args.batch_size):
                    batch = documents[i:i+args.batch_size]
                    print(f"\\n🚀 Processing batch {i//args.batch_size + 1}")
                    
                    session = learner.start_learning_cycle(
                        batch,
                        learning_goals={'min_confidence': args.confidence_target}
                    )
            else:
                # Single session with all documents
                session = learner.start_learning_cycle(
                    documents,
                    learning_goals={'min_confidence': args.confidence_target}
                )
        
        print("\\n✅ Learning completed! Check output directory for detailed results.")
        
        # Show final recommendations
        if 'session' in locals():
            print("\\n🔮 Final Recommendations:")
            for rec in session.recommendations[-3:]:
                print(f"   • {rec}")


if __name__ == "__main__":
    main()