#!/usr/bin/env python3
"""
Intelligent Rule Discovery - AI discovers business rules from data
Analyzes existing documents to find cross-domain patterns automatically
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

class IntelligentRuleDiscovery:
    """AI-powered discovery of business rules from existing data"""

    def __init__(self):
        self.discovered_rules = []
        self.pattern_confidence_threshold = 0.7
        self.minimum_evidence_count = 3

    def analyze_documents_for_patterns(self, documents: List[Dict]) -> List[Dict]:
        """
        Analyze existing documents to discover cross-domain business rules

        Args:
            documents: List of processed documents with entities and cross-references

        Returns:
            List of discovered business rules with confidence scores
        """

        # Group documents by domain
        domain_groups = self._group_by_domain(documents)

        # Discover temporal patterns
        temporal_rules = self._discover_temporal_patterns(documents)

        # Discover entity-based patterns
        entity_rules = self._discover_entity_patterns(documents)

        # Discover content-based patterns
        content_rules = self._discover_content_patterns(documents)

        # Discover cross-domain correlations
        cross_domain_rules = self._discover_cross_domain_patterns(domain_groups)

        all_rules = temporal_rules + entity_rules + content_rules + cross_domain_rules

        # Filter and rank rules
        validated_rules = self._validate_and_rank_rules(all_rules, documents)

        return validated_rules

    def _group_by_domain(self, documents: List[Dict]) -> Dict[str, List[Dict]]:
        """Group documents by domain for analysis"""
        groups = defaultdict(list)
        for doc in documents:
            domain = doc.get("universal_metadata", {}).get("domain")
            if domain:
                groups[domain].append(doc)
        return dict(groups)

    def _discover_temporal_patterns(self, documents: List[Dict]) -> List[Dict]:
        """Discover time-based business rules"""
        rules = []

        # Pattern: Same-day events across domains
        same_day_events = defaultdict(list)
        for doc in documents:
            date = doc.get("universal_metadata", {}).get("creation_date")
            domain = doc.get("universal_metadata", {}).get("domain")
            if date and domain:
                same_day_events[date].append((domain, doc))

        # Analyze same-day co-occurrences
        for date, domain_docs in same_day_events.items():
            if len(domain_docs) >= 2:
                domains = [domain for domain, _ in domain_docs]
                domain_pairs = [(domains[i], domains[j]) for i in range(len(domains))
                               for j in range(i+1, len(domains))]

                for domain1, domain2 in domain_pairs:
                    # Check for meaningful correlations
                    doc1 = next(doc for d, doc in domain_docs if d == domain1)
                    doc2 = next(doc for d, doc in domain_docs if d == domain2)

                    correlation = self._analyze_document_correlation(doc1, doc2)
                    if correlation["confidence"] > self.pattern_confidence_threshold:
                        rules.append({
                            "rule_type": "temporal_correlation",
                            "pattern": f"{domain1}_same_day_affects_{domain2}",
                            "description": f"Events in {domain1} on same day correlate with {domain2}",
                            "confidence": correlation["confidence"],
                            "evidence_count": 1,
                            "example": {
                                "source": doc1.get("@id"),
                                "target": doc2.get("@id"),
                                "correlation_details": correlation["details"]
                            }
                        })

        return rules

    def _discover_entity_patterns(self, documents: List[Dict]) -> List[Dict]:
        """Discover entity-based business rules"""
        rules = []

        # Track entity mentions across domains
        entity_mentions = defaultdict(lambda: defaultdict(list))

        for doc in documents:
            domain = doc.get("universal_metadata", {}).get("domain")
            entities = doc.get("entities", {})

            for entity_type, entity_list in entities.items():
                for entity in entity_list:
                    entity_id = entity.get("@id")
                    if entity_id:
                        entity_mentions[entity_id][domain].append(doc)

        # Find entities mentioned across multiple domains
        for entity_id, domain_docs in entity_mentions.items():
            if len(domain_docs) >= 2:
                domains = list(domain_docs.keys())
                for i, domain1 in enumerate(domains):
                    for domain2 in domains[i+1:]:
                        docs1 = domain_docs[domain1]
                        docs2 = domain_docs[domain2]

                        # Analyze how entity impacts across domains
                        impact_analysis = self._analyze_cross_domain_entity_impact(
                            entity_id, docs1, docs2, domain1, domain2
                        )

                        if impact_analysis["confidence"] > self.pattern_confidence_threshold:
                            rules.append({
                                "rule_type": "entity_cross_domain",
                                "pattern": f"{entity_id}_impacts_{domain1}_to_{domain2}",
                                "description": f"Entity {entity_id} has cross-domain impact from {domain1} to {domain2}",
                                "confidence": impact_analysis["confidence"],
                                "evidence_count": len(docs1) + len(docs2),
                                "entity_details": {
                                    "entity_id": entity_id,
                                    "source_domain": domain1,
                                    "target_domain": domain2,
                                    "impact_type": impact_analysis["impact_type"]
                                }
                            })

        return rules

    def _discover_content_patterns(self, documents: List[Dict]) -> List[Dict]:
        """Discover content-based business rules using semantic analysis"""
        rules = []

        # Analyze semantic tag co-occurrences
        tag_cooccurrences = defaultdict(lambda: defaultdict(int))
        domain_tag_patterns = defaultdict(lambda: defaultdict(int))

        for doc in documents:
            domain = doc.get("universal_metadata", {}).get("domain")
            tags = doc.get("semantic_tags", [])

            # Track tag patterns within domain
            for tag in tags:
                domain_tag_patterns[domain][tag] += 1

            # Track tag co-occurrences
            for i, tag1 in enumerate(tags):
                for tag2 in tags[i+1:]:
                    tag_cooccurrences[tag1][tag2] += 1
                    tag_cooccurrences[tag2][tag1] += 1

        # Find strong tag correlations
        for tag1, related_tags in tag_cooccurrences.items():
            for tag2, count in related_tags.items():
                if count >= self.minimum_evidence_count:
                    confidence = min(0.95, count / 10)  # Scale confidence

                    if confidence > self.pattern_confidence_threshold:
                        rules.append({
                            "rule_type": "semantic_correlation",
                            "pattern": f"{tag1}_correlates_with_{tag2}",
                            "description": f"Documents with '{tag1}' often also have '{tag2}'",
                            "confidence": confidence,
                            "evidence_count": count,
                            "semantic_details": {
                                "primary_tag": tag1,
                                "correlated_tag": tag2,
                                "cooccurrence_frequency": count
                            }
                        })

        return rules

    def _discover_cross_domain_patterns(self, domain_groups: Dict[str, List[Dict]]) -> List[Dict]:
        """Discover patterns that span multiple domains"""
        rules = []

        # Analyze existing cross-references to find patterns
        cross_ref_patterns = defaultdict(lambda: defaultdict(int))

        for domain, docs in domain_groups.items():
            for doc in docs:
                for cross_ref in doc.get("cross_references", []):
                    target_domain = cross_ref.get("target_domain")
                    relationship_type = cross_ref.get("relationship_type")

                    if target_domain and relationship_type:
                        pattern_key = f"{domain}_to_{target_domain}"
                        cross_ref_patterns[pattern_key][relationship_type] += 1

        # Find frequent cross-domain patterns
        for pattern_key, relationships in cross_ref_patterns.items():
            for relationship_type, count in relationships.items():
                if count >= self.minimum_evidence_count:
                    source_domain, target_domain = pattern_key.split("_to_")
                    confidence = min(0.95, count / 8)  # Scale confidence

                    if confidence > self.pattern_confidence_threshold:
                        rules.append({
                            "rule_type": "cross_domain_relationship",
                            "pattern": pattern_key + "_" + relationship_type,
                            "description": f"{source_domain} documents frequently {relationship_type} {target_domain} documents",
                            "confidence": confidence,
                            "evidence_count": count,
                            "relationship_details": {
                                "source_domain": source_domain,
                                "target_domain": target_domain,
                                "relationship_type": relationship_type,
                                "frequency": count
                            }
                        })

        return rules

    def _analyze_document_correlation(self, doc1: Dict, doc2: Dict) -> Dict:
        """Analyze correlation between two documents"""
        correlation_score = 0.0
        details = []

        # Check entity overlap
        entities1 = self._get_all_entity_names(doc1)
        entities2 = self._get_all_entity_names(doc2)
        entity_overlap = len(entities1 & entities2)

        if entity_overlap > 0:
            correlation_score += 0.3
            details.append(f"Shared {entity_overlap} entities")

        # Check semantic tag overlap
        tags1 = set(doc1.get("semantic_tags", []))
        tags2 = set(doc2.get("semantic_tags", []))
        tag_overlap = len(tags1 & tags2)

        if tag_overlap > 0:
            correlation_score += 0.2 * tag_overlap
            details.append(f"Shared {tag_overlap} semantic tags")

        # Check content keywords
        title1 = doc1.get("universal_metadata", {}).get("title", "").lower()
        title2 = doc2.get("universal_metadata", {}).get("title", "").lower()

        keyword_overlap = self._calculate_keyword_overlap(title1, title2)
        correlation_score += keyword_overlap * 0.3

        if keyword_overlap > 0:
            details.append(f"Keyword similarity: {keyword_overlap:.2f}")

        return {
            "confidence": min(0.95, correlation_score),
            "details": details
        }

    def _analyze_cross_domain_entity_impact(self, entity_id: str, docs1: List[Dict],
                                          docs2: List[Dict], domain1: str, domain2: str) -> Dict:
        """Analyze how an entity impacts across domains"""

        # Simple heuristic: if entity appears in both domains frequently,
        # there's likely a business relationship

        total_mentions = len(docs1) + len(docs2)
        confidence = min(0.90, total_mentions / 10)

        # Determine impact type based on domains
        impact_types = {
            ("operaciones", "mercados"): "OPERATIONAL_MARKET_IMPACT",
            ("operaciones", "legal"): "OPERATIONAL_COMPLIANCE",
            ("mercados", "legal"): "MARKET_REGULATION",
            ("operaciones", "planificacion"): "OPERATIONAL_PLANNING",
            ("mercados", "planificacion"): "MARKET_PLANNING",
            ("legal", "planificacion"): "REGULATORY_PLANNING"
        }

        impact_type = impact_types.get((domain1, domain2), "GENERAL_CROSS_REFERENCE")

        return {
            "confidence": confidence,
            "impact_type": impact_type
        }

    def _get_all_entity_names(self, doc: Dict) -> set:
        """Get all entity names from a document"""
        entity_names = set()
        entities = doc.get("entities", {})

        for entity_list in entities.values():
            for entity in entity_list:
                name = entity.get("name")
                if name:
                    entity_names.add(name.lower())

        return entity_names

    def _calculate_keyword_overlap(self, text1: str, text2: str) -> float:
        """Calculate keyword overlap between two texts"""
        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0.0

        overlap = len(words1 & words2)
        total_unique = len(words1 | words2)

        return overlap / total_unique if total_unique > 0 else 0.0

    def _validate_and_rank_rules(self, rules: List[Dict], documents: List[Dict]) -> List[Dict]:
        """Validate and rank discovered rules"""

        # Filter rules by confidence and evidence
        validated_rules = [
            rule for rule in rules
            if (rule["confidence"] >= self.pattern_confidence_threshold and
                rule["evidence_count"] >= self.minimum_evidence_count)
        ]

        # Add validation score
        for rule in validated_rules:
            rule["validation_score"] = self._calculate_validation_score(rule, documents)

        # Sort by validation score
        validated_rules.sort(key=lambda r: r["validation_score"], reverse=True)

        return validated_rules

    def _calculate_validation_score(self, rule: Dict, documents: List[Dict]) -> float:
        """Calculate validation score for a rule"""
        base_score = rule["confidence"]
        evidence_bonus = min(0.2, rule["evidence_count"] / 20)

        # Bonus for cross-domain rules (more valuable)
        if "cross_domain" in rule["rule_type"]:
            base_score += 0.1

        return min(0.99, base_score + evidence_bonus)

# Example usage
if __name__ == "__main__":
    discovery = IntelligentRuleDiscovery()

    # Sample documents for testing
    sample_docs = [
        {
            "@id": "cen:operaciones:anexo_01:2025-02-15",
            "universal_metadata": {"domain": "operaciones", "creation_date": "2025-02-15"},
            "entities": {"power_plants": [{"@id": "cen:plant:solar_atacama", "name": "Solar Atacama"}]},
            "semantic_tags": ["solar", "renewable_energy", "real_time"],
            "cross_references": [{"target_domain": "mercados", "relationship_type": "IMPACTS"}]
        },
        {
            "@id": "cen:mercados:price_report:2025-02-15",
            "universal_metadata": {"domain": "mercados", "creation_date": "2025-02-15"},
            "entities": {"power_plants": [{"@id": "cen:plant:solar_atacama", "name": "Solar Atacama"}]},
            "semantic_tags": ["solar", "price_impact", "real_time"],
            "cross_references": []
        }
    ]

    discovered_rules = discovery.analyze_documents_for_patterns(sample_docs)

    print(f"Discovered {len(discovered_rules)} business rules:")
    for rule in discovered_rules:
        print(f"- {rule['pattern']}: {rule['confidence']:.2f} confidence")
        print(f"  {rule['description']}")