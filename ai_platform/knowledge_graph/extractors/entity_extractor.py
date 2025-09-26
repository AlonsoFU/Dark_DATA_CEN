#!/usr/bin/env python3
"""
Entity Extractor - Automatic AI-powered entity recognition
Extracts power plants, companies, locations from documents
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Any

class EntityExtractor:
    """Automatically extract entities from document text"""

    def __init__(self):
        self.schemas_dir = Path(__file__).parent.parent / "schemas"
        self.vocabularies = self._load_vocabularies()

    def _load_vocabularies(self) -> Dict:
        """Load domain vocabularies for entity recognition"""
        vocab_file = self.schemas_dir / "domain_vocabularies.json"
        if vocab_file.exists():
            with open(vocab_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def extract_entities(self, document_text: str, domain: str) -> Dict[str, List[Dict]]:
        """Extract all entities from document text"""
        entities = {
            "power_plants": self._extract_power_plants(document_text),
            "companies": self._extract_companies(document_text),
            "locations": self._extract_locations(document_text),
            "regulations": self._extract_regulations(document_text),
            "equipment": self._extract_equipment(document_text)
        }

        # Add confidence scores and normalize IDs
        for entity_type, entity_list in entities.items():
            for entity in entity_list:
                entity["@id"] = self._generate_entity_id(entity["name"], entity_type)
                entity["@type"] = self._get_entity_type(entity["name"], entity_type)
                if "confidence" not in entity:
                    entity["confidence"] = self._calculate_confidence(entity["name"], document_text)

        return entities

    def _extract_power_plants(self, text: str) -> List[Dict]:
        """Extract power plant names from text"""
        plants = []

        # Common Chilean power plant patterns
        plant_patterns = [
            r'(?:Planta|Central|Parque)\s+(?:Solar|Eólica|Hidroeléctrica|Térmica)?\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+\d*)',
            r'([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)\s+(?:Solar|Eólica|Hidroeléctrica|Térmica)',
            r'(?:Solar|Eólica|Hidroeléctrica|Térmica)\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)',
            r'([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)\s+\d+\s*MW',
        ]

        for pattern in plant_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                plant_name = match.group(1).strip()
                if len(plant_name) > 3 and plant_name not in [p["name"] for p in plants]:
                    plants.append({
                        "name": plant_name,
                        "raw_context": match.group(0),
                        "position": match.start()
                    })

        return plants

    def _extract_companies(self, text: str) -> List[Dict]:
        """Extract company names from text"""
        companies = []

        # Chilean company patterns
        company_patterns = [
            r'([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)\s+(?:S\.A\.|Ltda\.|SpA)',
            r'(?:Empresa|Compañía|Generadora)\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)',
            r'([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)\s+(?:Energía|Eléctrica|Power)',
        ]

        for pattern in company_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                company_name = match.group(1).strip()
                if len(company_name) > 3 and company_name not in [c["name"] for c in companies]:
                    companies.append({
                        "name": company_name,
                        "raw_context": match.group(0),
                        "position": match.start()
                    })

        return companies

    def _extract_locations(self, text: str) -> List[Dict]:
        """Extract location names from text"""
        locations = []

        # Chilean location patterns
        location_patterns = [
            r'Región\s+(?:de\s+)?([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)',
            r'Provincia\s+(?:de\s+)?([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)',
            r'Comuna\s+(?:de\s+)?([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)',
            r'([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)\s+\d+\s*kV',  # Substations
        ]

        for pattern in location_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                location_name = match.group(1).strip()
                if len(location_name) > 3 and location_name not in [l["name"] for l in locations]:
                    locations.append({
                        "name": location_name,
                        "raw_context": match.group(0),
                        "position": match.start()
                    })

        return locations

    def _extract_regulations(self, text: str) -> List[Dict]:
        """Extract regulation references from text"""
        regulations = []

        # Chilean regulation patterns
        regulation_patterns = [
            r'(?:Ley|Decreto|Resolución|Norma)\s+(?:N°\s*)?(\d+[\-/]\d+)',
            r'(?:Ley|Decreto)\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)',
            r'NT\s+SyCS\s+([\d\.]+)',  # Technical standards
            r'Procedimiento\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ\s]+)',
        ]

        for pattern in regulation_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                reg_name = match.group(1).strip()
                if len(reg_name) > 2 and reg_name not in [r["name"] for r in regulations]:
                    regulations.append({
                        "name": reg_name,
                        "raw_context": match.group(0),
                        "position": match.start()
                    })

        return regulations

    def _extract_equipment(self, text: str) -> List[Dict]:
        """Extract equipment mentions from text"""
        equipment = []

        # Equipment patterns
        equipment_patterns = [
            r'(?:Transformador|Interruptor|Seccionador)\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ0-9\s\-]+)',
            r'([A-ZÁÉÍÓÚÑ][a-záéíóúñ0-9\s\-]+)\s+(?:kV|MVA|MW)',
            r'Línea\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñ0-9\s\-]+)',
        ]

        for pattern in equipment_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                equipment_name = match.group(1).strip()
                if len(equipment_name) > 3 and equipment_name not in [e["name"] for e in equipment]:
                    equipment.append({
                        "name": equipment_name,
                        "raw_context": match.group(0),
                        "position": match.start()
                    })

        return equipment

    def _generate_entity_id(self, name: str, entity_type: str) -> str:
        """Generate standardized entity ID"""
        # Normalize name for ID
        normalized = re.sub(r'[^a-zA-Z0-9\s]', '', name.lower())
        normalized = re.sub(r'\s+', '_', normalized.strip())

        # Map entity types to ID prefixes
        type_mapping = {
            "power_plants": "plant",
            "companies": "company",
            "locations": "location",
            "regulations": "regulation",
            "equipment": "equipment"
        }

        prefix = type_mapping.get(entity_type, "entity")
        return f"cen:{prefix}:{normalized}"

    def _get_entity_type(self, name: str, category: str) -> str:
        """Determine specific entity type from vocabularies"""
        # Simple heuristics - could be enhanced with AI classification
        if category == "power_plants":
            if any(word in name.lower() for word in ["solar"]):
                return "SolarPowerPlant"
            elif any(word in name.lower() for word in ["eólica", "viento"]):
                return "WindPowerPlant"
            elif any(word in name.lower() for word in ["hidro", "agua"]):
                return "HydroPowerPlant"
            elif any(word in name.lower() for word in ["térmica", "carbón", "gas"]):
                return "ThermalPowerPlant"
            else:
                return "PowerPlant"
        elif category == "companies":
            return "PowerCompany"
        elif category == "locations":
            if "región" in name.lower():
                return "Region"
            elif "provincia" in name.lower():
                return "Province"
            elif "comuna" in name.lower():
                return "Commune"
            else:
                return "Location"
        elif category == "regulations":
            return "LegalRegulation"
        elif category == "equipment":
            return "Equipment"

        return "Entity"

    def _calculate_confidence(self, entity_name: str, full_text: str) -> float:
        """Calculate confidence score for entity extraction"""
        # Simple confidence based on context and repetition
        occurrences = full_text.lower().count(entity_name.lower())
        base_confidence = min(0.5 + (occurrences * 0.1), 0.95)

        # Boost confidence for well-formed names
        if len(entity_name.split()) > 1:  # Multi-word names more likely correct
            base_confidence += 0.1

        # Penalize very short names
        if len(entity_name) < 4:
            base_confidence -= 0.2

        return max(0.1, min(0.99, base_confidence))

# Example usage
if __name__ == "__main__":
    extractor = EntityExtractor()

    # Test with sample text
    sample_text = """
    En el día 15 de febrero de 2025, la Central Solar Atacama generó 150 MW,
    mientras que la Empresa Energías Renovables S.A. reportó operación normal
    en la Región de Antofagasta. El Transformador T1 de la Subestación Quillota 220 kV
    cumple con la Norma NT SyCS 5.1.2.
    """

    entities = extractor.extract_entities(sample_text, "operaciones")
    print(json.dumps(entities, indent=2, ensure_ascii=False))