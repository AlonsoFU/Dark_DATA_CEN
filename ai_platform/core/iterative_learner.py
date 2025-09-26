#!/usr/bin/env python3
"""
Iterative Document Structure Learning Pipeline
Progressive learning system that improves with each document batch
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from ai_platform.analyzers.structure_learning_agent import StructureLearningAgent
from ai_platform.analyzers.pattern_analyzer import PatternAnalyzer


@dataclass
class LearningSession:
    """Represents a learning session with metadata"""
    session_id: str
    timestamp: str
    documents_processed: int
    patterns_learned: int
    confidence_improvement: float
    session_type: str  # 'discovery', 'validation', 'refinement'
    duration_seconds: float
    recommendations: List[str]


class IterativeLearner:
    """Manages iterative document structure learning"""
    
    def __init__(self, workspace_dir: str = None):
        if workspace_dir is None:
            project_root = Path(__file__).parent.parent.parent
            self.workspace_dir = project_root / "data" / "learning_workspace"
        else:
            self.workspace_dir = Path(workspace_dir)
        
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.structure_agent = StructureLearningAgent(
            str(self.workspace_dir / "structure_learning")
        )
        self.pattern_analyzer = PatternAnalyzer(
            str(self.workspace_dir / "analysis_output")
        )
        
        # Learning history
        self.sessions_history = self._load_learning_history()
        self.current_confidence = 0.0
        
    def start_learning_cycle(
        self,
        document_batch: List[str],
        learning_goals: Optional[Dict[str, Any]] = None
    ) -> LearningSession:
        """
        Start a new learning cycle with a batch of documents
        
        Args:
            document_batch: List of document paths to learn from
            learning_goals: Optional learning objectives and thresholds
            
        Returns:
            LearningSession with results and recommendations
        """
        start_time = time.time()
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"🚀 Starting learning cycle: {session_id}")
        print(f"📚 Processing {len(document_batch)} documents")
        
        # Set default learning goals if not provided
        if learning_goals is None:
            learning_goals = {
                'min_confidence': 0.8,
                'min_patterns': 5,
                'consistency_threshold': 0.7
            }
        
        # Phase 1: Pattern Analysis
        print("🔍 Phase 1: Analyzing patterns...")
        analysis_results = self.pattern_analyzer.analyze_document_collection(document_batch)
        
        # Phase 2: Structure Learning
        print("🧠 Phase 2: Learning structures...")
        learning_results = self.structure_agent.learn_from_documents(document_batch)
        
        # Phase 3: Progress Assessment
        print("📊 Phase 3: Assessing progress...")
        progress_assessment = self._assess_learning_progress(
            analysis_results, learning_results, learning_goals
        )
        
        # Phase 4: Generate Recommendations
        print("💡 Phase 4: Generating recommendations...")
        recommendations = self._generate_cycle_recommendations(
            analysis_results, learning_results, progress_assessment
        )
        
        # Create session record
        end_time = time.time()
        session = LearningSession(
            session_id=session_id,
            timestamp=datetime.now().isoformat(),
            documents_processed=len(document_batch),
            patterns_learned=learning_results.get('patterns_discovered', 0),
            confidence_improvement=self._calculate_confidence_improvement(learning_results),
            session_type=learning_results.get('phase', 'unknown'),
            duration_seconds=end_time - start_time,
            recommendations=recommendations
        )
        
        # Save session and update history
        self._save_learning_session(session, analysis_results, learning_results)
        self.sessions_history.append(session)
        
        print(f"✅ Learning cycle completed in {session.duration_seconds:.2f}s")
        self._print_session_summary(session)
        
        return session
    
    def adaptive_learning_strategy(
        self,
        available_documents: List[str],
        target_confidence: float = 0.85
    ) -> Dict[str, Any]:
        """
        Adaptive learning strategy that selects optimal document batches
        
        Args:
            available_documents: All available documents for learning
            target_confidence: Target confidence score to achieve
            
        Returns:
            Learning strategy with recommended batches and timeline
        """
        print(f"🎯 Planning adaptive learning strategy (target: {target_confidence:.2f})")
        
        strategy = {
            'batches': [],
            'estimated_sessions': 0,
            'estimated_duration_hours': 0,
            'confidence_trajectory': [],
            'learning_plan': []
        }
        
        current_confidence = self._get_current_confidence()
        remaining_docs = available_documents.copy()
        batch_number = 1
        
        while current_confidence < target_confidence and remaining_docs:
            # Determine optimal batch size based on current phase
            batch_size = self._determine_optimal_batch_size(
                current_confidence, len(remaining_docs)
            )
            
            # Select most valuable documents for this batch
            batch_docs = self._select_optimal_documents(
                remaining_docs, batch_size, current_confidence
            )
            
            # Estimate confidence improvement from this batch
            estimated_improvement = self._estimate_confidence_improvement(
                batch_docs, current_confidence
            )
            
            strategy['batches'].append({
                'batch_number': batch_number,
                'documents': batch_docs,
                'batch_size': len(batch_docs),
                'expected_confidence_gain': estimated_improvement,
                'learning_phase': self._predict_learning_phase(current_confidence)
            })
            
            # Update for next iteration
            current_confidence += estimated_improvement
            strategy['confidence_trajectory'].append(current_confidence)
            remaining_docs = [d for d in remaining_docs if d not in batch_docs]
            batch_number += 1
            
            # Safety limit
            if batch_number > 10:
                break
        
        strategy['estimated_sessions'] = len(strategy['batches'])
        strategy['estimated_duration_hours'] = self._estimate_total_duration(strategy['batches'])
        strategy['learning_plan'] = self._create_learning_plan(strategy)
        
        return strategy
    
    def validate_learned_structure(
        self,
        test_documents: List[str],
        validation_criteria: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Validate learned structure against new documents
        
        Args:
            test_documents: Documents to test against
            validation_criteria: Validation thresholds
            
        Returns:
            Validation results with metrics and recommendations
        """
        if validation_criteria is None:
            validation_criteria = {
                'min_accuracy': 0.8,
                'min_coverage': 0.7,
                'max_false_positive_rate': 0.2
            }
        
        validation_results = {
            'test_documents': len(test_documents),
            'accuracy_scores': [],
            'coverage_scores': [],
            'false_positive_rates': [],
            'overall_metrics': {},
            'failed_documents': [],
            'recommendations': []
        }
        
        print(f"🧪 Validating structure on {len(test_documents)} test documents...")
        
        for doc_path in test_documents:
            try:
                # Analyze document with learned patterns
                analysis = self.structure_agent.analyze_new_document(doc_path)
                
                # Calculate metrics
                accuracy = analysis.get('confidence_score', 0.0)
                coverage = len(analysis.get('matched_patterns', [])) / max(1, 
                    analysis.get('structure_summary', {}).get('sections_found', 1))
                
                validation_results['accuracy_scores'].append(accuracy)
                validation_results['coverage_scores'].append(coverage)
                
                # Check against criteria
                if accuracy < validation_criteria['min_accuracy']:
                    validation_results['failed_documents'].append({
                        'document': Path(doc_path).name,
                        'accuracy': accuracy,
                        'issue': 'low_accuracy'
                    })
                
            except Exception as e:
                validation_results['failed_documents'].append({
                    'document': Path(doc_path).name,
                    'error': str(e),
                    'issue': 'processing_error'
                })
        
        # Calculate overall metrics
        if validation_results['accuracy_scores']:
            validation_results['overall_metrics'] = {
                'mean_accuracy': sum(validation_results['accuracy_scores']) / len(validation_results['accuracy_scores']),
                'mean_coverage': sum(validation_results['coverage_scores']) / len(validation_results['coverage_scores']),
                'pass_rate': sum(1 for score in validation_results['accuracy_scores'] 
                                if score >= validation_criteria['min_accuracy']) / len(validation_results['accuracy_scores'])
            }
        
        # Generate recommendations
        validation_results['recommendations'] = self._generate_validation_recommendations(
            validation_results, validation_criteria
        )
        
        return validation_results
    
    def _assess_learning_progress(
        self,
        analysis_results: Dict[str, Any],
        learning_results: Dict[str, Any],
        learning_goals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess progress towards learning goals"""
        progress = {
            'confidence_met': False,
            'patterns_met': False,
            'consistency_met': False,
            'overall_progress': 0.0,
            'next_steps': []
        }
        
        # Check confidence goal
        current_confidence = max(learning_results.get('confidence_scores', {}).values()) if learning_results.get('confidence_scores') else 0
        progress['confidence_met'] = current_confidence >= learning_goals['min_confidence']
        
        # Check patterns goal
        patterns_count = learning_results.get('patterns_discovered', 0)
        progress['patterns_met'] = patterns_count >= learning_goals['min_patterns']
        
        # Check consistency goal
        consistency = analysis_results.get('pattern_analysis', {}).get('consistency_score', 0)
        progress['consistency_met'] = consistency >= learning_goals['consistency_threshold']
        
        # Calculate overall progress
        goals_met = sum([progress['confidence_met'], progress['patterns_met'], progress['consistency_met']])
        progress['overall_progress'] = goals_met / 3.0
        
        # Determine next steps
        if not progress['confidence_met']:
            progress['next_steps'].append("Increase pattern confidence through validation")
        if not progress['patterns_met']:
            progress['next_steps'].append("Discover more structural patterns")
        if not progress['consistency_met']:
            progress['next_steps'].append("Add more similar documents to improve consistency")
        
        return progress
    
    def _generate_cycle_recommendations(
        self,
        analysis_results: Dict[str, Any],
        learning_results: Dict[str, Any],
        progress_assessment: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations for next learning cycle"""
        recommendations = []
        
        # Based on overall progress
        if progress_assessment['overall_progress'] >= 0.8:
            recommendations.append("✅ Excellent progress - ready for production testing")
        elif progress_assessment['overall_progress'] >= 0.6:
            recommendations.append("🔄 Good progress - continue with validation phase")
        else:
            recommendations.append("📈 Early stage - focus on pattern discovery")
        
        # Specific recommendations from components
        recommendations.extend(analysis_results.get('recommendations', []))
        recommendations.extend(learning_results.get('recommendations', []))
        
        # Next steps
        for step in progress_assessment['next_steps']:
            recommendations.append(f"🎯 Next: {step}")
        
        return recommendations
    
    def _determine_optimal_batch_size(
        self,
        current_confidence: float,
        remaining_docs: int
    ) -> int:
        """Determine optimal batch size based on learning phase"""
        if current_confidence < 0.3:
            # Discovery phase - small batches for pattern discovery
            return min(3, remaining_docs)
        elif current_confidence < 0.7:
            # Validation phase - medium batches
            return min(5, remaining_docs)
        else:
            # Refinement phase - larger batches
            return min(8, remaining_docs)
    
    def _select_optimal_documents(
        self,
        available_docs: List[str],
        batch_size: int,
        current_confidence: float
    ) -> List[str]:
        """Select most valuable documents for next learning batch"""
        # For now, simple selection - in practice, this could be more sophisticated
        # Could consider: document diversity, size, complexity, etc.
        return available_docs[:batch_size]
    
    def _get_current_confidence(self) -> float:
        """Get current overall confidence score"""
        if self.sessions_history:
            return max(session.confidence_improvement for session in self.sessions_history[-3:])
        return 0.0
    
    def _load_learning_history(self) -> List[LearningSession]:
        """Load previous learning sessions"""
        history_file = self.workspace_dir / "learning_history.json"
        
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
            
            return [
                LearningSession(**session_data) 
                for session_data in history_data.get('sessions', [])
            ]
        
        return []
    
    def _save_learning_session(
        self,
        session: LearningSession,
        analysis_results: Dict[str, Any],
        learning_results: Dict[str, Any]
    ):
        """Save learning session with detailed results"""
        session_dir = self.workspace_dir / "sessions" / session.session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Save session metadata
        with open(session_dir / "session.json", 'w', encoding='utf-8') as f:
            json.dump(asdict(session), f, indent=2, ensure_ascii=False)
        
        # Save detailed results
        with open(session_dir / "analysis_results.json", 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)
        
        with open(session_dir / "learning_results.json", 'w', encoding='utf-8') as f:
            json.dump(learning_results, f, indent=2, ensure_ascii=False)
        
        # Update history file
        history_file = self.workspace_dir / "learning_history.json"
        history_data = {
            'last_updated': datetime.now().isoformat(),
            'total_sessions': len(self.sessions_history) + 1,
            'sessions': [asdict(s) for s in self.sessions_history] + [asdict(session)]
        }
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, indent=2, ensure_ascii=False)
    
    def _calculate_confidence_improvement(self, learning_results: Dict[str, Any]) -> float:
        """Calculate confidence improvement from learning results"""
        confidence_scores = learning_results.get('confidence_scores', {})
        if confidence_scores:
            return max(confidence_scores.values())
        return 0.0
    
    def _print_session_summary(self, session: LearningSession):
        """Print a summary of the learning session"""
        print(f"\\n📋 Session Summary:")
        print(f"   Phase: {session.session_type}")
        print(f"   Documents: {session.documents_processed}")
        print(f"   Patterns: {session.patterns_learned}")
        print(f"   Confidence: {session.confidence_improvement:.3f}")
        print(f"   Duration: {session.duration_seconds:.2f}s")
        print(f"\\n💡 Top Recommendations:")
        for i, rec in enumerate(session.recommendations[:3], 1):
            print(f"   {i}. {rec}")


def main():
    """Demo iterative learning"""
    learner = IterativeLearner()
    
    print("🔄 Iterative Learning Pipeline Demo")
    print("=" * 50)
    
    # Example documents for learning
    sample_docs = [
        "data/raw/power_system_failure_1.json",
        "data/raw/power_system_failure_2.json",
        "data/raw/power_system_failure_3.json",
    ]
    
    # Start learning cycle
    print("🚀 Starting learning cycle...")
    session = learner.start_learning_cycle(sample_docs)
    
    print(f"\\n✅ Learning session completed: {session.session_id}")


if __name__ == "__main__":
    main()