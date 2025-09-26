#!/usr/bin/env python3
"""
Cross-Reference Engine - Automatic document linking
Creates relationships between documents across domains
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any

class CrossReferenceEngine:
    """Automatically create cross-references between documents"""

    def __init__(self):
        self.rules_dir = Path(__file__).parent
        self.cross_reference_rules = self._load_cross_reference_rules()

    def _load_cross_reference_rules(self) -> Dict:
        """Load cross-reference rules configuration"""
        return {
            "temporal_rules": {
                "same_date": {
                    "description": "Link documents from the same date",
                    "relationship": "SAME_DATE",
                    "confidence": 1.0,
                    "enabled": True
                },
                "consecutive_days": {
                    "description": "Link daily reports from consecutive days",
                    "relationship": "FOLLOWS",
                    "confidence": 0.9,
                    "enabled": True
                }
            },

            "entity_rules": {
                "same_power_plant": {
                    "description": "Link documents mentioning the same power plant",
                    "relationship": "REFERENCES",
                    "confidence": 0.85,
                    "enabled": True
                },
                "same_company": {
                    "description": "Link documents from the same company",
                    "relationship": "REFERENCES",
                    "confidence": 0.8,
                    "enabled": True
                }
            },

            "domain_rules": {
                "operaciones_to_mercados": [
                    {
                        "condition": "solar_generation_mentioned",
                        "target_type": "solar_price_data",
                        "relationship": "IMPACTS",
                        "confidence": 0.8,
                        "context": "Solar generation affects midday prices"
                    },
                    {
                        "condition": "system_incident",
                        "target_type": "market_disruption",
                        "relationship": "CAUSES",
                        "confidence": 0.9,
                        "context": "System incidents disrupt market operations"
                    }
                ],
                "operaciones_to_legal": [
                    {
                        "condition": "safety_incident",
                        "target_type": "safety_regulation",
                        "relationship": "MUST_COMPLY_WITH",
                        "confidence": 0.95,
                        "context": "Safety incidents trigger regulatory compliance"
                    },
                    {
                        "condition": "equipment_failure",
                        "target_type": "technical_standard",
                        "relationship": "VIOLATES",
                        "confidence": 0.8,
                        "context": "Equipment failures may violate standards"
                    }
                ],
                "mercados_to_planificacion": [
                    {
                        "condition": "high_demand_forecast",
                        "target_type": "capacity_expansion",
                        "relationship": "TRIGGERS",
                        "confidence": 0.85,
                        "context": "High demand forecasts trigger expansion planning"
                    }
                ]
            }
        }

    def generate_cross_references(self, document: Dict, all_documents: List[Dict] = None) -> List[Dict]:
        """Generate cross-references for a document"""
        cross_references = []

        if all_documents:
            # Temporal cross-references
            cross_references.extend(self._apply_temporal_rules(document, all_documents))

            # Entity-based cross-references
            cross_references.extend(self._apply_entity_rules(document, all_documents))

            # Domain-specific cross-references
            cross_references.extend(self._apply_domain_rules(document, all_documents))

        return cross_references

    def _apply_temporal_rules(self, document: Dict, all_documents: List[Dict]) -> List[Dict]:
        """Apply temporal linking rules"""
        cross_refs = []
        doc_date = self._extract_date(document)

        if not doc_date:
            return cross_refs

        for other_doc in all_documents:
            if other_doc.get("@id") == document.get("@id"):
                continue

            other_date = self._extract_date(other_doc)
            if not other_date:
                continue

            # Same date rule
            if doc_date == other_date and other_doc.get("universal_metadata", {}).get("domain") != document.get("universal_metadata", {}).get("domain"):
                cross_refs.append({
                    "target_document_id": other_doc.get("@id"),
                    "target_domain": other_doc.get("universal_metadata", {}).get("domain"),
                    "relationship_type": "SAME_DATE",
                    "confidence": 1.0,
                    "context": f"Documents from same date: {doc_date}"
                })

            # Consecutive days rule (for daily reports)
            elif abs((doc_date - other_date).days) == 1:
                if self._is_daily_report(document) and self._is_daily_report(other_doc):
                    relationship = "FOLLOWS" if doc_date > other_date else "PRECEDES"
                    cross_refs.append({
                        "target_document_id": other_doc.get("@id"),
                        "target_domain": other_doc.get("universal_metadata", {}).get("domain"),
                        "relationship_type": relationship,
                        "confidence": 0.9,
                        "context": f"Consecutive daily reports"
                    })

        return cross_refs

    def _apply_entity_rules(self, document: Dict, all_documents: List[Dict]) -> List[Dict]:
        """Apply entity-based linking rules"""
        cross_refs = []
        doc_entities = self._extract_entity_names(document)

        for other_doc in all_documents:
            if other_doc.get("@id") == document.get("@id"):
                continue

            other_entities = self._extract_entity_names(other_doc)

            # Find common entities
            common_plants = set(doc_entities.get("power_plants", [])) & set(other_entities.get("power_plants", []))
            common_companies = set(doc_entities.get("companies", [])) & set(other_entities.get("companies", []))

            # Same power plant rule
            if common_plants:
                cross_refs.append({
                    "target_document_id": other_doc.get("@id"),
                    "target_domain": other_doc.get("universal_metadata", {}).get("domain"),
                    "relationship_type": "REFERENCES",
                    "confidence": 0.85,
                    "context": f"Both mention power plants: {', '.join(list(common_plants)[:3])}"
                })

            # Same company rule
            elif common_companies:
                cross_refs.append({
                    "target_document_id": other_doc.get("@id"),
                    "target_domain": other_doc.get("universal_metadata", {}).get("domain"),
                    "relationship_type": "REFERENCES",
                    "confidence": 0.8,
                    "context": f"Both mention companies: {', '.join(list(common_companies)[:3])}"
                })

        return cross_refs

    def _apply_domain_rules(self, document: Dict, all_documents: List[Dict]) -> List[Dict]:
        """Apply domain-specific cross-reference rules"""
        cross_refs = []
        doc_domain = document.get("universal_metadata", {}).get("domain")
        doc_content = self._get_document_content(document)

        # Get applicable rules for this domain
        domain_rules_key = f"{doc_domain}_to_*"
        for rule_key, rules in self.cross_reference_rules.get("domain_rules", {}).items():
            if not rule_key.startswith(doc_domain):
                continue

            target_domain = rule_key.split("_to_")[1]

            for rule in rules:
                if self._check_rule_condition(rule["condition"], doc_content):
                    # Find matching documents in target domain
                    matching_docs = self._find_matching_documents(
                        rule["target_type"],
                        target_domain,
                        all_documents
                    )

                    for target_doc in matching_docs:
                        cross_refs.append({
                            "target_document_id": target_doc.get("@id"),
                            "target_domain": target_domain,
                            "relationship_type": rule["relationship"],
                            "confidence": rule["confidence"],
                            "context": rule["context"]
                        })

        return cross_refs

    def _extract_date(self, document: Dict) -> datetime:
        """Extract date from document"""
        date_str = document.get("universal_metadata", {}).get("creation_date")
        if date_str:
            try:
                return datetime.fromisoformat(date_str)
            except:
                pass
        return None

    def _extract_entity_names(self, document: Dict) -> Dict[str, List[str]]:
        """Extract entity names from document"""
        entities = document.get("entities", {})
        result = {}

        for entity_type, entity_list in entities.items():
            if isinstance(entity_list, list):
                result[entity_type] = [entity.get("name", "") for entity in entity_list if entity.get("name")]

        return result

    def _get_document_content(self, document: Dict) -> str:
        """Get text content from document for rule checking"""
        # Extract searchable content from various fields
        content_parts = []

        # From title and metadata
        metadata = document.get("universal_metadata", {})
        content_parts.append(metadata.get("title", ""))

        # From semantic tags
        tags = document.get("semantic_tags", [])
        content_parts.extend(tags)

        # From entities
        entities = document.get("entities", {})
        for entity_list in entities.values():
            if isinstance(entity_list, list):
                for entity in entity_list:
                    content_parts.append(entity.get("name", ""))

        return " ".join(content_parts).lower()

    def _check_rule_condition(self, condition: str, content: str) -> bool:
        """Check if rule condition is met"""
        condition_map = {
            "solar_generation_mentioned": ["solar", "fotovoltaica", "pv"],
            "system_incident": ["incidente", "falla", "interrupción", "emergencia"],
            "safety_incident": ["seguridad", "accidente", "peligro", "riesgo"],
            "equipment_failure": ["falla", "avería", "defecto", "mal funcionamiento"],
            "high_demand_forecast": ["alta demanda", "peak", "máximo", "pronóstico alto"]
        }

        keywords = condition_map.get(condition, [])
        return any(keyword in content for keyword in keywords)

    def _find_matching_documents(self, target_type: str, target_domain: str, all_documents: List[Dict]) -> List[Dict]:
        """Find documents matching target type in target domain"""
        matching_docs = []

        for doc in all_documents:
            if doc.get("universal_metadata", {}).get("domain") != target_domain:
                continue

            doc_content = self._get_document_content(doc)

            # Simple matching based on target type
            type_keywords = {
                "solar_price_data": ["solar", "precio", "tarifa"],
                "market_disruption": ["mercado", "interrupción", "volatilidad"],
                "safety_regulation": ["seguridad", "regulación", "norma"],
                "technical_standard": ["estándar", "técnico", "especificación"],
                "capacity_expansion": ["expansión", "capacidad", "crecimiento"]
            }

            keywords = type_keywords.get(target_type, [])
            if any(keyword in doc_content for keyword in keywords):
                matching_docs.append(doc)

        return matching_docs[:5]  # Limit to 5 matches

    def _is_daily_report(self, document: Dict) -> bool:
        """Check if document is a daily report"""
        doc_type = document.get("universal_metadata", {}).get("document_type", "").lower()
        title = document.get("universal_metadata", {}).get("title", "").lower()

        return any(keyword in doc_type or keyword in title
                  for keyword in ["diario", "daily", "informe_diario"])

# Example usage
if __name__ == "__main__":
    engine = CrossReferenceEngine()

    # Test with sample documents
    sample_doc = {
        "@id": "cen:operaciones:anexo_01:2025-02-15",
        "universal_metadata": {
            "title": "ANEXO 1 - Generación Solar",
            "domain": "operaciones",
            "creation_date": "2025-02-15"
        },
        "entities": {
            "power_plants": [{"name": "Solar Atacama"}]
        },
        "semantic_tags": ["solar", "generación"]
    }

    other_docs = [
        {
            "@id": "cen:mercados:precio_solar:2025-02-15",
            "universal_metadata": {
                "title": "Precios Solar Febrero",
                "domain": "mercados",
                "creation_date": "2025-02-15"
            },
            "semantic_tags": ["solar", "precio"]
        }
    ]

    cross_refs = engine.generate_cross_references(sample_doc, other_docs)
    print(json.dumps(cross_refs, indent=2, ensure_ascii=False))