#!/usr/bin/env python3
"""
AI Training Data Pipeline
Prepares documents for machine learning with optimal data structures
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class TrainingExample:
    """Structured training example for AI models"""
    id: str
    document_type: str
    source_document: str
    text: str
    labels: Dict[str, Any]  # Classification, entities, etc.
    metadata: Dict[str, Any]
    created_at: str


@dataclass  
class DocumentEmbedding:
    """Vector embedding representation of document chunks"""
    chunk_id: str
    document_id: str
    text: str
    embedding: List[float]
    chunk_type: str  # 'header', 'content', 'table', etc.
    semantic_tags: List[str]


class AITrainingPipeline:
    """Pipeline for preparing AI training data from documents"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            project_root = Path(__file__).parent.parent.parent
            self.data_dir = project_root / "data"
        else:
            self.data_dir = Path(data_dir)
            
        self.training_db = self._init_training_database()
    
    def _init_training_database(self) -> str:
        """Initialize training data database"""
        db_path = self.data_dir / "training_data" / "training.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS training_examples (
                id TEXT PRIMARY KEY,
                document_type TEXT,
                source_document TEXT,
                text TEXT,
                labels JSON,
                metadata JSON,
                created_at TEXT
            );
            
            CREATE TABLE IF NOT EXISTS document_embeddings (
                chunk_id TEXT PRIMARY KEY,
                document_id TEXT,
                text TEXT,
                embedding BLOB,  -- Serialized numpy array
                chunk_type TEXT,
                semantic_tags JSON,
                created_at TEXT
            );
            
            CREATE TABLE IF NOT EXISTS entity_annotations (
                id TEXT PRIMARY KEY,
                document_id TEXT,
                text_span TEXT,
                start_pos INTEGER,
                end_pos INTEGER,
                entity_type TEXT,
                confidence REAL,
                created_at TEXT
            );
            
            CREATE TABLE IF NOT EXISTS relationship_annotations (
                id TEXT PRIMARY KEY,
                document_id TEXT,
                subject_entity TEXT,
                relationship_type TEXT, 
                object_entity TEXT,
                confidence REAL,
                context TEXT,
                created_at TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_doc_type ON training_examples(document_type);
            CREATE INDEX IF NOT EXISTS idx_entity_type ON entity_annotations(entity_type);
        """)
        conn.close()
        
        return str(db_path)
    
    def process_document_for_training(
        self, 
        document_path: str,
        document_type: str,
        annotations: Optional[Dict] = None
    ) -> List[TrainingExample]:
        """
        Process a document into training examples
        
        Args:
            document_path: Path to processed document JSON
            document_type: Type of document
            annotations: Human annotations if available
            
        Returns:
            List of training examples
        """
        with open(document_path, 'r', encoding='utf-8') as f:
            doc_data = json.load(f)
        
        training_examples = []
        
        # Extract different types of training data
        
        # 1. Classification examples
        if 'classification' in doc_data:
            example = TrainingExample(
                id=f"{Path(document_path).stem}_classification",
                document_type=document_type,
                source_document=document_path,
                text=doc_data.get('full_text', ''),
                labels={
                    'classification': doc_data['classification'],
                    'task_type': 'document_classification'
                },
                metadata={
                    'pages': doc_data.get('page_count', 0),
                    'has_tables': doc_data.get('has_tables', False)
                },
                created_at=datetime.now().isoformat()
            )
            training_examples.append(example)
        
        # 2. Entity extraction examples
        if 'entities' in doc_data:
            for entity_data in doc_data['entities']:
                example = TrainingExample(
                    id=f"{Path(document_path).stem}_entity_{len(training_examples)}",
                    document_type=document_type,
                    source_document=document_path,
                    text=entity_data.get('context', ''),
                    labels={
                        'entities': entity_data['entities'],
                        'task_type': 'named_entity_recognition'
                    },
                    metadata={
                        'section': entity_data.get('section', 'unknown')
                    },
                    created_at=datetime.now().isoformat()
                )
                training_examples.append(example)
        
        # 3. Summarization examples
        if 'sections' in doc_data:
            for section in doc_data['sections']:
                if 'summary' in section:
                    example = TrainingExample(
                        id=f"{Path(document_path).stem}_summary_{section['id']}",
                        document_type=document_type,
                        source_document=document_path,
                        text=section['content'],
                        labels={
                            'summary': section['summary'],
                            'task_type': 'summarization'
                        },
                        metadata={
                            'section_type': section.get('type', 'content'),
                            'length_ratio': len(section['summary']) / len(section['content'])
                        },
                        created_at=datetime.now().isoformat()
                    )
                    training_examples.append(example)
        
        # Save to database
        self._save_training_examples(training_examples)
        
        return training_examples
    
    def _save_training_examples(self, examples: List[TrainingExample]):
        """Save training examples to database"""
        conn = sqlite3.connect(self.training_db)
        
        for example in examples:
            conn.execute("""
                INSERT OR REPLACE INTO training_examples 
                (id, document_type, source_document, text, labels, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                example.id,
                example.document_type, 
                example.source_document,
                example.text,
                json.dumps(example.labels),
                json.dumps(example.metadata),
                example.created_at
            ))
        
        conn.commit()
        conn.close()
    
    def create_training_dataset(
        self, 
        task_type: str,
        document_types: Optional[List[str]] = None,
        train_split: float = 0.7,
        val_split: float = 0.15
    ) -> Dict[str, List[TrainingExample]]:
        """
        Create training/validation/test splits for a specific task
        
        Args:
            task_type: Type of ML task ('classification', 'ner', 'summarization')
            document_types: Filter by document types
            train_split: Training set proportion
            val_split: Validation set proportion
            
        Returns:
            Dictionary with 'train', 'val', 'test' splits
        """
        conn = sqlite3.connect(self.training_db)
        
        # Build query
        query = """
            SELECT * FROM training_examples 
            WHERE JSON_EXTRACT(labels, '$.task_type') = ?
        """
        params = [task_type]
        
        if document_types:
            placeholders = ','.join(['?'] * len(document_types))
            query += f" AND document_type IN ({placeholders})"
            params.extend(document_types)
        
        query += " ORDER BY RANDOM()"  # Random shuffle
        
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to TrainingExample objects
        examples = []
        for row in rows:
            example = TrainingExample(
                id=row[0],
                document_type=row[1],
                source_document=row[2], 
                text=row[3],
                labels=json.loads(row[4]),
                metadata=json.loads(row[5]),
                created_at=row[6]
            )
            examples.append(example)
        
        # Create splits
        total = len(examples)
        train_end = int(total * train_split)
        val_end = train_end + int(total * val_split)
        
        return {
            'train': examples[:train_end],
            'val': examples[train_end:val_end],
            'test': examples[val_end:]
        }
    
    def export_for_huggingface(
        self, 
        task_type: str,
        output_dir: str,
        document_types: Optional[List[str]] = None
    ):
        """Export training data in HuggingFace datasets format"""
        splits = self.create_training_dataset(task_type, document_types)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for split_name, examples in splits.items():
            # Convert to HuggingFace format
            hf_data = []
            for example in examples:
                if task_type == 'document_classification':
                    hf_data.append({
                        'text': example.text,
                        'label': example.labels['classification'],
                        'id': example.id
                    })
                elif task_type == 'named_entity_recognition':
                    # Convert to IOB format
                    tokens, labels = self._convert_to_iob(
                        example.text, 
                        example.labels['entities']
                    )
                    hf_data.append({
                        'tokens': tokens,
                        'ner_tags': labels,
                        'id': example.id
                    })
                elif task_type == 'summarization':
                    hf_data.append({
                        'document': example.text,
                        'summary': example.labels['summary'],
                        'id': example.id
                    })
            
            # Save JSON
            with open(output_path / f"{split_name}.json", 'w', encoding='utf-8') as f:
                json.dump(hf_data, f, indent=2, ensure_ascii=False)
    
    def _convert_to_iob(self, text: str, entities: List[Dict]) -> tuple:
        """Convert entity annotations to IOB format"""
        # This would implement proper IOB tagging
        # Simplified implementation
        tokens = text.split()
        labels = ['O'] * len(tokens)  # Default to Outside
        
        # This needs proper implementation based on entity positions
        return tokens, labels
    
    def get_training_statistics(self) -> Dict[str, Any]:
        """Get statistics about training data"""
        conn = sqlite3.connect(self.training_db)
        
        stats = {}
        
        # Document type distribution
        cursor = conn.execute("""
            SELECT document_type, COUNT(*) as count
            FROM training_examples
            GROUP BY document_type
        """)
        stats['document_types'] = dict(cursor.fetchall())
        
        # Task type distribution  
        cursor = conn.execute("""
            SELECT JSON_EXTRACT(labels, '$.task_type') as task_type, COUNT(*) as count
            FROM training_examples  
            GROUP BY JSON_EXTRACT(labels, '$.task_type')
        """)
        stats['task_types'] = dict(cursor.fetchall())
        
        # Total examples
        cursor = conn.execute("SELECT COUNT(*) FROM training_examples")
        stats['total_examples'] = cursor.fetchone()[0]
        
        conn.close()
        return stats


def main():
    """Demo usage of AI training pipeline"""
    pipeline = AITrainingPipeline()
    
    print("🤖 AI Training Pipeline Demo")
    print("=" * 40)
    
    # Show current statistics
    stats = pipeline.get_training_statistics() 
    print(f"📊 Training Statistics:")
    print(f"   Total Examples: {stats['total_examples']}")
    print(f"   Document Types: {stats.get('document_types', {})}")
    print(f"   Task Types: {stats.get('task_types', {})}")


if __name__ == "__main__":
    main()