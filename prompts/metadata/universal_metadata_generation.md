# 🏷️ PROMPT - Generación Universal de Metadatos

## 🎯 Objetivo

Generar metadatos completos, tags semánticos y clasificaciones automáticas para cualquier tipo de documento, optimizando para búsqueda IA y análisis cross-domain, independientemente del dominio o industria.

## 📊 Datos de Entrada

**Input**: Documento JSON extraído de cualquier tipo de documento
**Context**: Universal - adaptable a cualquier dominio o industria
**Output**: Metadatos estructurados con tags, clasificaciones y referencias universales

## 🏷️ **Sistema de Clasificación Universal**

### **1. Tags por Dominio/Industria**
Clasificar automáticamente según el contenido detectado:

```
Financiero: "finanzas", "balance", "ingresos", "rentabilidad", "inversión"
Legal: "contrato", "clausulas", "obligaciones", "derecho", "cumplimiento"
Técnico: "especificaciones", "procedimientos", "normas", "calidad", "ingeniería"
Operacional: "procesos", "rendimiento", "métricas", "eficiencia", "resultados"
Recursos Humanos: "personal", "capacitación", "evaluación", "organización"
Marketing: "mercadeo", "ventas", "clientes", "campañas", "branding"
Investigación: "análisis", "estudio", "metodología", "resultados", "conclusiones"
```

### **2. Tags Geográficos Universales**
Analizar ubicaciones mencionadas y generar jerarquía:

```
Nivel 1 - Continente: "america", "europa", "asia", "africa", "oceania"
Nivel 2 - País: "chile", "argentina", "españa", "estados_unidos", etc.
Nivel 3 - Región/Estado: "metropolitana", "valparaiso", "madrid", "california"
Nivel 4 - Ciudad: "santiago", "barcelona", "nueva_york", "londres"
Nivel 5 - Área específica: "providencia", "las_condes", "centro_historico"

Ejemplo: ["america", "chile", "region_metropolitana", "santiago", "providencia"]
```

### **3. Tags Temporales Universales**
Clasificar por período temporal y frecuencia:

```
Período: "2025", "2024", "q3_2025", "septiembre_2025"
Frecuencia: "diario", "semanal", "mensual", "trimestral", "anual"
Tipo temporal: "histórico", "actual", "proyección", "forecast"
Estacionalidad: "primavera", "verano", "otoño", "invierno" (hemisferio adaptativo)

Ejemplo: ["2025", "q3_2025", "septiembre", "actual", "otoño"]
```

### **4. Tags por Tipo de Organización**
Identificar y clasificar entidades organizacionales:

```
Tipo: "empresa_privada", "organismo_publico", "ong", "institución_educativa"
Tamaño: "startup", "pyme", "gran_empresa", "multinacional"
Sector: "tecnología", "servicios", "manufactura", "energia", "salud"
Origen: "nacional", "internacional", "regional", "global"

Ejemplo: ["empresa_privada", "gran_empresa", "tecnología", "internacional"]
```

### **5. Tags por Tipo de Documento**
Clasificar según propósito y formato:

```
Propósito: "reporte", "contrato", "manual", "análisis", "propuesta"
Audiencia: "ejecutiva", "técnica", "legal", "operativa", "académica"
Confidencialidad: "publica", "interna", "confidencial", "restringida"
Formato: "formal", "informal", "técnico", "divulgativo"

Example: ["reporte", "ejecutiva", "interna", "formal"]
```

## 📋 **Metadatos Estructurados Universales**

### **Clasificación Automática por Contenido**
```json
{
  "clasificacion_automatica": {
    "dominio_principal": "financiero | legal | técnico | operacional | rrhh | marketing | investigación",
    "subdominios": ["contabilidad", "auditoría", "análisis_financiero"],

    "tipo_documento": {
      "categoria": "reporte | contrato | manual | análisis | propuesta | informe",
      "subcategoria": "estado_financiero | contrato_servicios | manual_usuario",
      "formato": "formal | informal | técnico | ejecutivo"
    },

    "complejidad": {
      "nivel": "básica | intermedia | avanzada | experta",
      "especialización": "alta | media | baja",
      "audiencia_tecnica": true
    },

    "confidencialidad": {
      "nivel": "publica | interna | confidencial | secreta",
      "restricciones": ["solo_directivos", "personal_autorizado"],
      "fecha_clasificacion": "2025-09-25"
    }
  }
}
```

### **Entidades Normalizadas**
```json
{
  "entidades_normalizadas": {
    "personas": [
      {
        "nombre_completo": "Juan Carlos Pérez González",
        "nombre_normalizado": "juan_carlos_perez_gonzalez",
        "rol": "director_general",
        "organization": "empresa_abc_sa",
        "confidence": 0.94,
        "contexto": "firma_contrato"
      }
    ],

    "organizaciones": [
      {
        "nombre_oficial": "Empresa ABC Sociedad Anónima",
        "nombre_normalizado": "empresa_abc_sa",
        "tipo": "empresa_privada",
        "industria": "tecnología",
        "pais": "chile",
        "confidence": 0.97
      }
    ],

    "ubicaciones": [
      {
        "direccion_completa": "Avenida Providencia 1234, Santiago",
        "ubicacion_normalizada": "av_providencia_1234_santiago",
        "ciudad": "santiago",
        "region": "region_metropolitana",
        "pais": "chile",
        "coordinates": "-33.4489, -70.6693",
        "confidence": 0.91
      }
    ],

    "fechas_criticas": [
      {
        "fecha": "2025-12-31",
        "tipo": "vencimiento",
        "descripcion": "Plazo final entrega proyecto",
        "importancia": "crítica",
        "confidence": 0.96
      }
    ]
  }
}
```

## 🔗 **Sistema de Cross-Referencias Universales**

### **Reglas de Referencia Adaptativas**
```json
{
  "reglas_cross_referencia": {
    "por_entidades": {
      "misma_persona": "Mismo individuo en documentos diferentes",
      "misma_organizacion": "Misma empresa/institución referenciada",
      "misma_ubicacion": "Misma dirección o región geográfica"
    },

    "por_tiempo": {
      "mismo_periodo": "Documentos del mismo período temporal",
      "secuencial": "Documentos de períodos consecutivos",
      "comparativo": "Documentos para análisis de tendencias"
    },

    "por_dominio": {
      "mismo_proyecto": "Documentos relacionados al mismo proyecto",
      "misma_linea_negocio": "Documentos de la misma área de negocio",
      "regulatorio": "Documentos bajo la misma normativa"
    },

    "por_tipo": {
      "mismo_tipo_documento": "Documentos del mismo tipo y propósito",
      "complementarios": "Documentos que se complementan",
      "dependientes": "Documentos con dependencias"
    }
  }
}
```

### **Generación Automática de Referencias**
```python
# Pseudocódigo para generación de referencias universales
def generate_universal_cross_references(current_document, document_database):
    references = []

    # Referencia por entidades comunes
    common_entities = find_common_entities(current_document, document_database)
    for entity in common_entities:
        references.append({
            "tipo_relacion": "SHARED_ENTITY",
            "entidad_comun": entity.normalized_name,
            "confidence": entity.confidence_score,
            "business_value": determine_business_value(entity)
        })

    # Referencia temporal
    temporal_docs = find_temporal_related(current_document, document_database)
    for doc in temporal_docs:
        references.append({
            "tipo_relacion": "TEMPORAL_SEQUENCE",
            "periodo_comun": doc.period,
            "confidence": calculate_temporal_confidence(doc),
            "analysis_type": "trend_analysis"
        })

    # Referencia por dominio
    domain_docs = find_domain_related(current_document, document_database)
    for doc in domain_docs:
        references.append({
            "tipo_relacion": "DOMAIN_RELATED",
            "dominio": doc.domain,
            "confidence": calculate_domain_similarity(doc),
            "analysis_type": "domain_analysis"
        })

    return references
```

## 📊 **Output Final - Metadatos Universales**

```json
{
  "@context": "https://darkdata.platform/metadata/v1",
  "@id": "metadata:universal:documento_id:2025_09_25",
  "@type": "DocumentMetadataUniversal",

  "tags_semanticos": [
    // Tags por dominio
    "financiero", "reporte_trimestral", "estado_resultados",

    // Tags geográficos
    "america", "chile", "region_metropolitana", "santiago",

    // Tags temporales
    "2025", "q3_2025", "septiembre", "actual",

    // Tags organizacionales
    "empresa_privada", "gran_empresa", "tecnología",

    // Tags de documento
    "reporte", "ejecutiva", "interna", "formal"
  ],

  "clasificacion_universal": {
    "dominio_principal": "financiero",
    "subdominios": ["contabilidad", "análisis_financiero"],
    "tipo_documento": "estado_financiero",
    "nivel_complejidad": "intermedia",
    "audiencia_objetivo": "ejecutiva",
    "confidencialidad": "interna"
  },

  "entidades_identificadas": {
    "total_personas": 5,
    "total_organizaciones": 12,
    "total_ubicaciones": 3,
    "total_fechas_criticas": 8,
    "total_metricas": 25
  },

  "referencias_cruzadas_potenciales": [
    {
      "documento_objetivo": "universal:reporte_q2_2025",
      "tipo_relacion": "TEMPORAL_COMPARISON",
      "confidence": 0.92,
      "business_value": "trend_analysis_quarterly",
      "analysis_type": "temporal_evolution"
    },
    {
      "documento_objetivo": "universal:auditoria_2025",
      "tipo_relacion": "REGULATORY_COMPLIANCE",
      "confidence": 0.87,
      "business_value": "compliance_verification",
      "analysis_type": "audit_trail"
    }
  ],

  "quality_metrics": {
    "completitud_metadatos": 0.94,
    "confidence_promedio": 0.89,
    "consistency_score": 0.91,
    "normalization_success": 0.96
  },

  "processing_info": {
    "extraction_method": "universal_adaptive",
    "processing_date": "2025-09-25T14:30:00Z",
    "model_version": "universal_v1.0",
    "total_processing_time_seconds": 45
  }
}
```

## 🎯 **Adaptaciones por Industria/Dominio**

### **Detección Automática de Contexto**
```markdown
SI documento contiene ["balance", "ingresos", "EBITDA", "ROI"]:
  → Aplicar metadatos financieros adicionales
  → Tags: "finanzas", "contabilidad", "métricas_financieras"

SI documento contiene ["contrato", "cláusula", "obligación", "derecho"]:
  → Aplicar metadatos legales adicionales
  → Tags: "legal", "contractual", "cumplimiento"

SI documento contiene ["especificación", "procedimiento", "norma", "técnico"]:
  → Aplicar metadatos técnicos adicionales
  → Tags: "técnico", "ingeniería", "procedimientos"

SI documento contiene ["rendimiento", "KPI", "eficiencia", "proceso"]:
  → Aplicar metadatos operacionales adicionales
  → Tags: "operacional", "métricas", "rendimiento"
```

---

**🚀 Este sistema de metadatos universales se adapta automáticamente a cualquier tipo de documento, proporcionando clasificación inteligente y cross-referencias que permiten análisis avanzado independientemente del dominio o industria.**