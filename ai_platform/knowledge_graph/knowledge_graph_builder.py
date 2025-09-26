#!/usr/bin/env python3
"""
Knowledge Graph Builder - Main orchestrator
Combines entity extraction + cross-references + universal schema
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

from extractors.entity_extractor import EntityExtractor
from rules.cross_reference_engine import CrossReferenceEngine

class KnowledgeGraphBuilder:
    """Main class that builds knowledge graph from documents"""

    def __init__(self):
        self.entity_extractor = EntityExtractor()
        self.cross_reference_engine = CrossReferenceEngine()
        self.schemas_dir = Path(__file__).parent / "schemas"

    def process_document(self, document_text: str, domain: str, document_type: str,
                        title: str, creation_date: str, existing_domain_data: Dict = None) -> Dict:
        """
        Process a document and return universal schema with knowledge graph data

        Args:
            document_text: Raw text content of document
            domain: operaciones|mercados|legal|planificacion
            document_type: Specific document type within domain
            title: Document title
            creation_date: Document creation date (YYYY-MM-DD)
            existing_domain_data: Existing extraction data (like anexo tables)

        Returns:
            Document in universal schema format with entities and cross-references
        """

        # Generate universal document ID
        document_id = self._generate_document_id(domain, document_type, creation_date)

        # 1. Extract entities automatically
        entities = self.entity_extractor.extract_entities(document_text, domain)

        # 2. Generate semantic tags automatically
        semantic_tags = self._generate_semantic_tags(document_text, domain, entities)

        # 3. Build universal schema structure
        universal_document = {
            "@context": "https://coordinador.cl/context/v1",
            "@id": document_id,
            "@type": self._get_document_type(domain, document_type),

            "universal_metadata": {
                "title": title,
                "domain": domain,
                "document_type": document_type,
                "creation_date": creation_date,
                "processing_date": datetime.now().isoformat(),
                "language": "es",
                "version": "1.0",
                "status": "final"
            },

            "entities": entities,

            "cross_references": [],  # Will be populated when processing multiple documents

            "semantic_tags": semantic_tags,

            "domain_specific_data": {
                domain: existing_domain_data or {}
            },

            "quality_metadata": {
                "extraction_confidence": self._calculate_overall_confidence(entities),
                "validation_status": "passed",
                "processing_method": "knowledge_graph_builder_v1",
                "quality_score": self._calculate_quality_score(entities, document_text),
                "human_validated": False
            }
        }

        return universal_document

    def process_multiple_documents(self, documents_data: List[Dict]) -> List[Dict]:
        """
        Process multiple documents and create cross-references between them

        Args:
            documents_data: List of document processing requests

        Returns:
            List of processed documents with cross-references
        """

        # First pass: Process each document individually
        processed_documents = []
        for doc_data in documents_data:
            processed_doc = self.process_document(
                document_text=doc_data["text"],
                domain=doc_data["domain"],
                document_type=doc_data["document_type"],
                title=doc_data["title"],
                creation_date=doc_data["creation_date"],
                existing_domain_data=doc_data.get("existing_data")
            )
            processed_documents.append(processed_doc)

        # Second pass: Generate cross-references
        for i, doc in enumerate(processed_documents):
            other_docs = processed_documents[:i] + processed_documents[i+1:]
            cross_refs = self.cross_reference_engine.generate_cross_references(doc, other_docs)
            doc["cross_references"] = cross_refs

        return processed_documents

    def save_to_knowledge_base(self, documents: List[Dict], output_dir: Path):
        """Save processed documents to knowledge base"""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save individual documents
        for doc in documents:
            domain = doc["universal_metadata"]["domain"]
            doc_type = doc["universal_metadata"]["document_type"]
            date = doc["universal_metadata"]["creation_date"]

            filename = f"{domain}_{doc_type}_{date}.json"
            filepath = output_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(doc, f, indent=2, ensure_ascii=False)

        # Create knowledge graph index
        self._create_knowledge_graph_index(documents, output_dir)

    def _generate_document_id(self, domain: str, document_type: str, creation_date: str) -> str:
        """Generate standardized document ID"""
        # Normalize document type
        normalized_type = document_type.lower().replace(" ", "_")
        return f"cen:{domain}:{normalized_type}:{creation_date}"

    def _get_document_type(self, domain: str, document_type: str) -> str:
        """Get @type for document based on domain and type"""
        type_mapping = {
            "operaciones": "PowerSystemDocument",
            "mercados": "MarketReport",
            "legal": "LegalRegulation",
            "planificacion": "PlanningStudy"
        }
        return type_mapping.get(domain, "Document")

    def _generate_semantic_tags(self, text: str, domain: str, entities: Dict) -> List[str]:
        """Generate semantic tags for document"""
        tags = set()

        # Add domain tag
        tags.add(domain)

        # Add data type tags based on content
        text_lower = text.lower()
        if any(word in text_lower for word in ["tiempo real", "actual", "ahora"]):
            tags.add("real_time")
        elif any(word in text_lower for word in ["histórico", "pasado", "anterior"]):
            tags.add("historical")
        elif any(word in text_lower for word in ["pronóstico", "proyección", "estimación"]):
            tags.add("forecast")
        else:
            tags.add("statistical")

        # Add priority tags
        if any(word in text_lower for word in ["crítico", "emergencia", "urgente"]):
            tags.add("critical_priority")
        elif any(word in text_lower for word in ["importante", "significativo"]):
            tags.add("high_priority")
        else:
            tags.add("medium_priority")

        # Add technology tags based on entities
        if entities.get("power_plants"):
            for plant in entities["power_plants"]:
                plant_name = plant.get("name", "").lower()
                if "solar" in plant_name:
                    tags.add("renewable_energy")
                elif any(word in plant_name for word in ["eólica", "viento"]):
                    tags.add("renewable_energy")
                elif any(word in plant_name for word in ["hidro", "agua"]):
                    tags.add("renewable_energy")
                elif any(word in plant_name for word in ["térmica", "carbón", "gas"]):
                    tags.add("thermal_generation")

        # Add domain-specific tags
        domain_tags = {
            "operaciones": ["operational_data", "system_management"],
            "mercados": ["market_data", "economic_analysis"],
            "legal": ["regulation_compliance", "legal_framework"],
            "planificacion": ["infrastructure_planning", "capacity_analysis"]
        }
        tags.update(domain_tags.get(domain, []))

        return sorted(list(tags))

    def _calculate_overall_confidence(self, entities: Dict) -> float:
        """Calculate overall extraction confidence"""
        all_confidences = []

        for entity_type, entity_list in entities.items():
            for entity in entity_list:
                if "confidence" in entity:
                    all_confidences.append(entity["confidence"])

        if not all_confidences:
            return 0.5

        return sum(all_confidences) / len(all_confidences)

    def _calculate_quality_score(self, entities: Dict, text: str) -> float:
        """Calculate overall quality score"""
        # Base score from extraction confidence
        confidence_score = self._calculate_overall_confidence(entities)

        # Entity diversity bonus
        entity_types_found = len([k for k, v in entities.items() if v])
        diversity_bonus = min(0.2, entity_types_found * 0.05)

        # Text length factor (longer texts generally have more reliable extractions)
        length_factor = min(0.1, len(text) / 10000)

        total_score = confidence_score + diversity_bonus + length_factor
        return min(0.99, max(0.1, total_score))

    def _create_knowledge_graph_index(self, documents: List[Dict], output_dir: Path):
        """Create index file for knowledge graph"""
        index = {
            "knowledge_graph_index": {
                "created": datetime.now().isoformat(),
                "total_documents": len(documents),
                "domains": {},
                "entities_index": {},
                "relationships_index": {}
            }
        }

        # Index by domain
        for doc in documents:
            domain = doc["universal_metadata"]["domain"]
            if domain not in index["knowledge_graph_index"]["domains"]:
                index["knowledge_graph_index"]["domains"][domain] = []
            index["knowledge_graph_index"]["domains"][domain].append(doc["@id"])

        # Index entities
        for doc in documents:
            for entity_type, entity_list in doc.get("entities", {}).items():
                for entity in entity_list:
                    entity_id = entity.get("@id")
                    if entity_id:
                        if entity_id not in index["knowledge_graph_index"]["entities_index"]:
                            index["knowledge_graph_index"]["entities_index"][entity_id] = []
                        index["knowledge_graph_index"]["entities_index"][entity_id].append(doc["@id"])

        # Index relationships
        for doc in documents:
            for cross_ref in doc.get("cross_references", []):
                rel_type = cross_ref.get("relationship_type")
                if rel_type:
                    if rel_type not in index["knowledge_graph_index"]["relationships_index"]:
                        index["knowledge_graph_index"]["relationships_index"][rel_type] = []
                    index["knowledge_graph_index"]["relationships_index"][rel_type].append({
                        "source": doc["@id"],
                        "target": cross_ref.get("target_document_id")
                    })

        # Save index
        with open(output_dir / "knowledge_graph_index.json", 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)

# Example usage
if __name__ == "__main__":
    builder = KnowledgeGraphBuilder()

    # Test with sample data
    sample_documents = [
        {
            "text": "En la Central Solar Atacama se generaron 150 MW el 15 de febrero de 2025",
            "domain": "operaciones",
            "document_type": "anexo_generation_programming",
            "title": "ANEXO 1 - Generación Programada",
            "creation_date": "2025-02-15",
            "existing_data": {"upper_table": {}, "lower_table": {}}
        },
        {
            "text": "Los precios de energía solar aumentaron debido a alta demanda el 15 de febrero",
            "domain": "mercados",
            "document_type": "daily_price_report",
            "title": "Reporte Diario de Precios",
            "creation_date": "2025-02-15"
        }
    ]

    # Process documents
    processed_docs = builder.process_multiple_documents(sample_documents)

    # Save to knowledge base
    output_dir = Path("knowledge_base_output")
    builder.save_to_knowledge_base(processed_docs, output_dir)

    print(f"Processed {len(processed_docs)} documents with knowledge graph integration")
    for doc in processed_docs:
        print(f"- {doc['@id']}: {len(doc['cross_references'])} cross-references")