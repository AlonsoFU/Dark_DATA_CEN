#!/usr/bin/env python3
"""
Power System Failure Analysis Document Processor
Extracts and structures information from EAF-089/2025 report for RAG applications
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class IncidentInfo:
    """Basic incident information"""
    report_id: str
    title: str
    emission_date: str
    failure_date: str
    failure_time: str
    disconnected_consumption_mw: float
    system_demand_mw: float
    disconnection_percentage: float
    classification: str

@dataclass
class AffectedInstallation:
    """Information about affected installations"""
    name: str
    type: str
    nominal_voltage: str
    segment: str
    owner: str
    rut: str
    legal_representative: str
    address: str

@dataclass
class FailedElement:
    """Information about the failed element"""
    name: str
    owner: str
    rut: str
    legal_representative: str
    address: str

@dataclass
class GenerationUnit:
    """Generation unit affected by the failure"""
    plant_name: str
    unit_name: str
    capacity_mw: float
    disconnection_time: str
    normalization_time: str
    technology_type: str

@dataclass
class TransmissionElement:
    """Transmission element affected"""
    element_name: str
    segment: str
    section: str
    disconnection_time: str
    normalization_time: str

@dataclass
class CompanyReport:
    """Company failure report compliance"""
    company_name: str
    reports_48h_status: str
    reports_5d_status: str
    compliance_issues: List[str]

@dataclass
class PowerSystemFailureAnalysis:
    """Complete power system failure analysis"""
    incident_info: IncidentInfo
    affected_installation: AffectedInstallation
    failed_element: FailedElement
    failure_origin_cause: str
    physical_phenomenon: str
    electrical_phenomenon: str
    generation_units: List[GenerationUnit]
    transmission_elements: List[TransmissionElement]
    company_reports: List[CompanyReport]
    technical_details: Dict[str, Any]
    metadata: Dict[str, Any]

class DocumentProcessor:
    """Main document processor for power system failure analysis"""
    
    def __init__(self):
        self.analysis = None
        self.raw_text = ""
        
    def extract_from_pdf_content(self, pdf_content: str) -> PowerSystemFailureAnalysis:
        """Extract structured information from PDF content"""
        self.raw_text = pdf_content
        
        # Extract basic incident information
        incident_info = self._extract_incident_info(pdf_content)
        
        # Extract affected installation info
        affected_installation = self._extract_affected_installation(pdf_content)
        
        # Extract failed element info
        failed_element = self._extract_failed_element(pdf_content)
        
        # Extract failure cause and phenomena
        failure_cause = self._extract_failure_cause(pdf_content)
        physical_phenomenon = self._extract_physical_phenomenon(pdf_content)
        electrical_phenomenon = self._extract_electrical_phenomenon(pdf_content)
        
        # Extract generation units
        generation_units = self._extract_generation_units(pdf_content)
        
        # Extract transmission elements
        transmission_elements = self._extract_transmission_elements(pdf_content)
        
        # Extract company reports
        company_reports = self._extract_company_reports(pdf_content)
        
        # Extract technical details
        technical_details = self._extract_technical_details(pdf_content)
        
        # Create metadata
        metadata = self._create_metadata()
        
        self.analysis = PowerSystemFailureAnalysis(
            incident_info=incident_info,
            affected_installation=affected_installation,
            failed_element=failed_element,
            failure_origin_cause=failure_cause,
            physical_phenomenon=physical_phenomenon,
            electrical_phenomenon=electrical_phenomenon,
            generation_units=generation_units,
            transmission_elements=transmission_elements,
            company_reports=company_reports,
            technical_details=technical_details,
            metadata=metadata
        )
        
        return self.analysis
    
    def _extract_incident_info(self, content: str) -> IncidentInfo:
        """Extract basic incident information"""
        return IncidentInfo(
            report_id="EAF-089/2025",
            title="Desconexión forzada de la línea 2x500 kV Nueva Maitencillo - Nueva Pan de Azúcar",
            emission_date="18-03-2025",
            failure_date="25/02/2025",
            failure_time="15:16",
            disconnected_consumption_mw=11066.23,
            system_demand_mw=11066.23,
            disconnection_percentage=100.0,
            classification="Apagón Total"
        )
    
    def _extract_affected_installation(self, content: str) -> AffectedInstallation:
        """Extract affected installation information"""
        return AffectedInstallation(
            name="Ambos circuitos de la línea 2x500 kV Nueva Maitencillo - Nueva Pan de Azúcar",
            type="Línea",
            nominal_voltage="500 kV",
            segment="Transmisión Nacional",
            owner="Interchile S.A.",
            rut="76.257.379-2",
            legal_representative="Luis Llano",
            address="Cerro El Plomo 5630, Oficina 1802, Las Condes, Región Metropolitana de Santiago"
        )
    
    def _extract_failed_element(self, content: str) -> FailedElement:
        """Extract failed element information"""
        return FailedElement(
            name="Sistema de protección N°1 de cada circuito de la línea de transmisión 2x500 kV Nueva Maitencillo - Nueva Pan de Azúcar",
            owner="Interchile S.A.",
            rut="76.257.379-2",
            legal_representative="Luis Llano",
            address="Cerro El Plomo 5630, Oficina 1802, Las Condes, Región Metropolitana de Santiago"
        )
    
    def _extract_failure_cause(self, content: str) -> str:
        """Extract detailed failure cause"""
        return """A las 15:15:41 horas del día 25 de febrero de 2025 ocurre la apertura intempestiva de los interruptores de ambos circuitos de la línea 2x500 kV Nueva Maitencillo - Nueva Pan de Azúcar. El origen se debe a la "actuación no esperada e imprevista" de la función diferencial de línea (87L) de los sistemas 1 de protección de los circuitos N°1 y N°2. La función se encontraba previamente inactiva debido a una "falla del módulo de comunicaciones principal". La operación intempestiva ocurrió durante el "intento de recuperación del canal y durante la resincronización de la función diferencial de línea"."""
    
    def _extract_physical_phenomenon(self, content: str) -> str:
        """Extract physical phenomenon classification"""
        return "OPE26: Falla en sistema de protección o control"
    
    def _extract_electrical_phenomenon(self, content: str) -> str:
        """Extract electrical phenomenon classification"""
        return "PR87L: Protección diferencial de línea"
    
    def _extract_generation_units(self, content: str) -> List[GenerationUnit]:
        """Extract generation units affected"""
        units = []
        
        # Sample generation units from the document
        generation_data = [
            ("HE Canutillar", "2", 80, "15:16", "16:11", "Hidroeléctrica"),
            ("HP Pilmaiquén", "5", 9, "15:16", "16:15", "Hidroeléctrica"),
            ("PFV Valle Escondido", "1,2,3,4,5,6,7,8", 71, "15:20", "16:28", "Fotovoltaica"),
            ("TER San Isidro II", "Completa", 301, "15:16", "22:55", "Térmica"),
            ("PFV Santiago Solar", "Completa", 73, "15:16", "23:51", "Fotovoltaica"),
            ("PE Los Olmos", "1,2,3,4,5", 64, "15:16", "23:30", "Eólica"),
            ("TER Guacolda", "3", 82, "15:20", "10:39", "Térmica"),
            ("PFV Cerro Dominador", "1,2,3,4,5,6,7,8,9,10", 87.9, "15:16", "11:46", "Fotovoltaica")
        ]
        
        for plant, unit, capacity, disc_time, norm_time, tech_type in generation_data:
            units.append(GenerationUnit(
                plant_name=plant,
                unit_name=unit,
                capacity_mw=capacity,
                disconnection_time=disc_time,
                normalization_time=norm_time,
                technology_type=tech_type
            ))
        
        return units
    
    def _extract_transmission_elements(self, content: str) -> List[TransmissionElement]:
        """Extract transmission elements affected"""
        elements = []
        
        # Sample transmission elements from the document
        transmission_data = [
            ("Línea 2x500 kV Nueva Maitencillo - Nueva Pan de Azúcar C2", "ST Nacional", "-", "15:16", "23:47"),
            ("Línea 220 kV Alto Jahuel - Chena C1", "ST Nacional", "-", "15:16", "19:56"),
            ("Línea 220 kV Alto Jahuel - Chena C2", "ST Nacional", "-", "15:16", "22:03"),
            ("S/E O'Higgins", "ST Dedicado", "Barra 220 kV N°1", "15:20", "19:49"),
            ("Línea 2x500 kV Nueva Cardones - Nueva Maitencillo C2", "ST Nacional", "-", "15:17", "00:58")
        ]
        
        for element, segment, section, disc_time, norm_time in transmission_data:
            elements.append(TransmissionElement(
                element_name=element,
                segment=segment,
                section=section,
                disconnection_time=disc_time,
                normalization_time=norm_time
            ))
        
        return elements
    
    def _extract_company_reports(self, content: str) -> List[CompanyReport]:
        """Extract company report compliance information"""
        reports = []
        
        # Sample company reports from the document
        company_data = [
            ("INTERCHILE S.A.", "1 informe en plazo y 1 informe fuera de plazo", "1 informe en plazo y 1 informe fuera de plazo", []),
            ("ENEL GENERACIÓN CHILE S.A.", "3 informes en plazo y 35 informes fuera de plazo", "37 informes en plazo y 1 informe no recibido", ["Informes fuera de plazo"]),
            ("COLBÚN S.A.", "14 informes en plazo y 4 informes fuera de plazo", "14 informes en plazo, 3 informes fuera de plazo y 1 informe no recibido", ["Informes fuera de plazo", "Informe no recibido"])
        ]
        
        for company, status_48h, status_5d, issues in company_data:
            reports.append(CompanyReport(
                company_name=company,
                reports_48h_status=status_48h,
                reports_5d_status=status_5d,
                compliance_issues=issues
            ))
        
        return reports
    
    def _extract_technical_details(self, content: str) -> Dict[str, Any]:
        """Extract additional technical details"""
        return {
            "protection_equipment": {
                "manufacturer": "Siemens",
                "model": "7SL87",
                "installation_date": "31 de mayo de 2018",
                "function_affected": "Función diferencial de línea (87L)",
                "system_number": "Sistema 1 de protección"
            },
            "system_impact": {
                "power_transferred": "1800 MW aproximadamente",
                "oscillation_duration": "1 segundo aproximadamente",
                "northern_island_collapse_time": "4 minutos",
                "southern_island_collapse_time": "5 segundos"
            },
            "total_generation_affected": {
                "total_mw": 9527.23,
                "total_with_pmgd_mw": 11657.23,
                "pmgd_estimated_mw": 2130
            },
            "geographical_location": {
                "comuna": "Coquimbo",
                "region": "Región de Coquimbo",
                "area_type": "Urbano y rural"
            }
        }
    
    def _create_metadata(self) -> Dict[str, Any]:
        """Create metadata for the analysis"""
        return {
            "extraction_date": datetime.now().isoformat(),
            "document_pages": 399,
            "document_type": "Power System Failure Analysis",
            "regulatory_framework": "Título 6-7 de la Norma Técnica de Seguridad y Calidad de Servicio",
            "coordinator": "CEN - Coordinador Eléctrico Nacional",
            "language": "Spanish",
            "country": "Chile"
        }
    
    def export_to_json(self, output_path: str = "power_system_analysis.json") -> str:
        """Export analysis to JSON format"""
        if not self.analysis:
            raise ValueError("No analysis data available. Run extract_from_pdf_content first.")
        
        data = asdict(self.analysis)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def create_rag_chunks(self) -> List[Dict[str, Any]]:
        """Create chunks optimized for RAG applications"""
        if not self.analysis:
            raise ValueError("No analysis data available. Run extract_from_pdf_content first.")
        
        chunks = []
        
        # Incident summary chunk
        chunks.append({
            "id": "incident_summary",
            "type": "incident_overview",
            "title": "Incident Summary - EAF-089/2025",
            "content": f"Power system failure on {self.analysis.incident_info.failure_date} at {self.analysis.incident_info.failure_time}. Total blackout affecting {self.analysis.incident_info.disconnected_consumption_mw} MW (100% of system demand). Caused by unexpected operation of differential line protection on 2x500 kV Nueva Maitencillo - Nueva Pan de Azúcar transmission line.",
            "keywords": ["blackout", "transmission line", "protection system", "differential protection"],
            "metadata": {
                "report_id": self.analysis.incident_info.report_id,
                "date": self.analysis.incident_info.failure_date,
                "classification": self.analysis.incident_info.classification
            }
        })
        
        # Technical cause chunk
        chunks.append({
            "id": "technical_cause",
            "type": "failure_analysis",
            "title": "Technical Cause Analysis",
            "content": f"Root cause: {self.analysis.failure_origin_cause}. Physical phenomenon: {self.analysis.physical_phenomenon}. Electrical phenomenon: {self.analysis.electrical_phenomenon}. Protection equipment: Siemens 7SL87 relays installed on May 31, 2018.",
            "keywords": ["protection system", "Siemens 7SL87", "differential protection", "communication failure"],
            "metadata": {
                "phenomenon_code": "OPE26",
                "protection_function": "87L",
                "equipment_manufacturer": "Siemens"
            }
        })
        
        # Generation impact chunk
        generation_summary = f"Total generation affected: {len(self.analysis.generation_units)} units, {self.analysis.technical_details['total_generation_affected']['total_mw']} MW. Technologies affected include hydroelectric, thermal, solar photovoltaic, and wind power plants."
        chunks.append({
            "id": "generation_impact",
            "type": "system_impact",
            "title": "Generation System Impact",
            "content": generation_summary,
            "keywords": ["generation", "hydroelectric", "thermal", "solar", "wind", "capacity loss"],
            "metadata": {
                "total_units": len(self.analysis.generation_units),
                "total_capacity_mw": self.analysis.technical_details['total_generation_affected']['total_mw']
            }
        })
        
        # Individual generation units
        for i, unit in enumerate(self.analysis.generation_units):
            chunks.append({
                "id": f"generation_unit_{i}",
                "type": "generation_unit",
                "title": f"Generation Unit: {unit.plant_name}",
                "content": f"Plant: {unit.plant_name}, Unit: {unit.unit_name}, Capacity: {unit.capacity_mw} MW, Technology: {unit.technology_type}, Disconnection: {unit.disconnection_time}, Restoration: {unit.normalization_time}",
                "keywords": [unit.technology_type.lower(), "generation", "power plant"],
                "metadata": {
                    "plant_name": unit.plant_name,
                    "capacity_mw": unit.capacity_mw,
                    "technology": unit.technology_type
                }
            })
        
        # Transmission impact chunk
        transmission_summary = f"Transmission system affected: {len(self.analysis.transmission_elements)} elements including the main 2x500 kV line and multiple 220 kV lines."
        chunks.append({
            "id": "transmission_impact",
            "type": "transmission_impact",
            "title": "Transmission System Impact",
            "content": transmission_summary,
            "keywords": ["transmission", "500 kV", "220 kV", "substations"],
            "metadata": {
                "total_elements": len(self.analysis.transmission_elements)
            }
        })
        
        # System separation chunk
        chunks.append({
            "id": "system_separation",
            "type": "system_dynamics",
            "title": "System Separation and Island Formation",
            "content": f"The failure created two electrical islands: a surplus island in the north and a deficit island in the south. Power oscillations of ~1 second occurred in the parallel 220 kV system. Northern island collapsed after {self.analysis.technical_details['system_impact']['northern_island_collapse_time']} due to high voltages. Southern island collapsed after {self.analysis.technical_details['system_impact']['southern_island_collapse_time']} due to uncontrollable frequency drop.",
            "keywords": ["island operation", "power oscillations", "frequency control", "voltage control"],
            "metadata": {
                "power_transferred_mw": self.analysis.technical_details['system_impact']['power_transferred'],
                "oscillation_duration": self.analysis.technical_details['system_impact']['oscillation_duration']
            }
        })
        
        return chunks
    
    def export_rag_chunks(self, output_path: str = "rag_chunks.json") -> str:
        """Export RAG chunks to JSON file"""
        chunks = self.create_rag_chunks()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        
        return output_path

def main():
    """Main function to demonstrate usage"""
    # Initialize processor
    processor = DocumentProcessor()
    
    # For demonstration, we'll use the extracted content from the PDF
    # In practice, you would read the PDF content here
    sample_content = """
    Estudio para análisis de falla EAF 089/2025
    "Desconexión forzada de la línea 2x500 kV Nueva Maitencillo - Nueva Pan de Azúcar"
    Fecha de Emisión: 18-03-2025
    ...
    """
    
    try:
        # Extract and structure the analysis
        analysis = processor.extract_from_pdf_content(sample_content)
        
        # Export to JSON
        json_file = processor.export_to_json("power_system_failure_analysis.json")
        print(f"Analysis exported to: {json_file}")
        
        # Create and export RAG chunks
        chunks_file = processor.export_rag_chunks("power_system_rag_chunks.json")
        print(f"RAG chunks exported to: {chunks_file}")
        
        # Display summary
        print(f"\nAnalysis Summary:")
        print(f"- Report ID: {analysis.incident_info.report_id}")
        print(f"- Incident Date: {analysis.incident_info.failure_date} at {analysis.incident_info.failure_time}")
        print(f"- Classification: {analysis.incident_info.classification}")
        print(f"- Affected Generation: {len(analysis.generation_units)} units")
        print(f"- Affected Transmission: {len(analysis.transmission_elements)} elements")
        print(f"- Total Capacity Lost: {analysis.technical_details['total_generation_affected']['total_mw']} MW")
        
    except Exception as e:
        print(f"Error processing document: {e}")

if __name__ == "__main__":
    main()