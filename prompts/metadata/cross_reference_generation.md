# 🔗 PROMPT - Generación de Cross-Referencias Inteligentes

## 🎯 Objetivo Estratégico

Generar cross-referencias automáticas entre documentos del sistema eléctrico chileno para habilitar análisis cross-domain y correlacional avanzado mediante IA.

## 🧠 **Marco Conceptual de Referencias**

### **Tipos de Relaciones Inteligentes**

#### 1. **Relaciones Temporales** ⏰
- **SAME_ENTITY_DIFFERENT_TIME**: Misma entidad en diferentes períodos
- **SEQUENTIAL_REPORTS**: Reportes consecutivos del mismo tipo
- **COMPARATIVE_ANALYSIS**: Comparación histórica de rendimiento

#### 2. **Relaciones Operacionales** ⚡
- **PROGRAMADO_VS_REAL**: Comparación programación vs ejecución real
- **COMPLEMENTARITY**: Plantas que operan de manera complementaria
- **GRID_DEPENDENCY**: Plantas que comparten infraestructura

#### 3. **Relaciones Empresariales** 🏢
- **SAME_COMPANY_PORTFOLIO**: Plantas de la misma empresa
- **CORPORATE_GROUP**: Plantas del mismo grupo corporativo
- **JOINT_VENTURES**: Proyectos con participación compartida

#### 4. **Relaciones Geográficas** 🗺️
- **REGIONAL_CLUSTER**: Plantas en la misma región administrativa
- **PHYSICAL_PROXIMITY**: Plantas geográficamente cercanas
- **TRANSMISSION_CORRIDOR**: Plantas en el mismo corredor de transmisión

#### 5. **Relaciones Regulatorias** ⚖️
- **COMPLIANCE_MONITORING**: Documentos de seguimiento regulatorio
- **REGULATORY_IMPACT**: Documentos afectados por la misma normativa
- **AUDIT_TRAIL**: Documentos que forman una cadena de auditoría

## 📊 **Reglas de Detección Automática**

### **Algoritmo de Matching**

```python
# Pseudocódigo para detección de referencias
def detect_cross_references(document_a, document_b):
    references = []

    # 1. Temporal Matching
    if same_entity_different_dates(document_a, document_b):
        references.append({
            "type": "TEMPORAL_EVOLUTION",
            "confidence": calculate_entity_similarity(),
            "business_value": "trend_analysis"
        })

    # 2. Entity Matching
    common_entities = find_common_entities(document_a, document_b)
    for entity in common_entities:
        references.append({
            "type": "SHARED_ENTITY",
            "entity": entity,
            "confidence": entity.confidence_score,
            "business_value": "entity_portfolio_analysis"
        })

    # 3. Geographic Proximity
    if geographic_proximity(document_a.locations, document_b.locations):
        references.append({
            "type": "GEOGRAPHIC_CLUSTER",
            "confidence": distance_confidence_score(),
            "business_value": "regional_analysis"
        })

    return references
```

### **Reglas Específicas por Tipo de Documento**

#### **ANEXO 1 (Programación) ↔ ANEXO 2 (Real)**
```json
{
  "relacion_type": "PROGRAMADO_VS_REAL",
  "matching_criteria": {
    "mismo_periodo": "fecha_operacion",
    "misma_planta": "nombre_normalizado",
    "misma_empresa": "empresa_propietaria"
  },
  "business_value": {
    "analysis_type": "desviacion_operacional",
    "kpis": ["factor_cumplimiento", "precision_forecast"],
    "decision_support": "optimizacion_programacion"
  },
  "confidence_factors": {
    "exact_plant_match": 0.95,
    "date_alignment": 0.90,
    "capacity_consistency": 0.85
  }
}
```

#### **INFORME DIARIO ↔ ANEXOS**
```json
{
  "relacion_type": "DAILY_TO_MONTHLY_AGGREGATION",
  "matching_criteria": {
    "period_inclusion": "fecha_dentro_del_periodo",
    "operational_consistency": "coherencia_operacional"
  },
  "business_value": {
    "analysis_type": "agregacion_temporal",
    "validation": "consistency_check",
    "decision_support": "monthly_reconciliation"
  }
}
```

## 🔍 **Detección de Entidades Comunes**

### **Normalización de Nombres**
```python
def normalize_entity_name(raw_name):
    # Plantas eléctricas
    if "planta solar" in raw_name.lower():
        return normalize_solar_plant_name(raw_name)

    # Empresas
    company_mappings = {
        "Enel Chile": "enel_chile_sa",
        "Colbún": "colbun_sa",
        "AES Gener": "aes_gener_sa"
    }

    # Ubicaciones
    region_mappings = {
        "RM": "region_metropolitana",
        "Antofagasta": "region_antofagasta"
    }

    return normalized_name
```

### **Scoring de Similaridad**
```python
def calculate_similarity_score(entity_a, entity_b):
    scores = {
        "exact_match": 1.0,
        "normalized_match": 0.95,
        "fuzzy_match_high": 0.85,
        "fuzzy_match_medium": 0.70,
        "context_match": 0.60
    }

    return determine_match_type(entity_a, entity_b)
```

## 🎯 **Cross-Referencias por Dominio**

### **Dominio Operaciones** ⚡
```json
{
  "cross_references": [
    {
      "source": "anexo_01_generacion_programada",
      "target": "anexo_02_generacion_real",
      "relation": "PROGRAMMED_VS_ACTUAL",
      "entities": ["planta_solar_quilapilun"],
      "confidence": 0.94,
      "business_insight": "Planta con 15% desviación negativa respecto programación",
      "action_required": "revisar_factores_meteorologicos"
    }
  ]
}
```

### **Dominio Mercados** 💰
```json
{
  "cross_references": [
    {
      "source": "operaciones_generacion_real",
      "target": "mercados_precios_spot",
      "relation": "GENERATION_PRICE_CORRELATION",
      "correlation_strength": 0.78,
      "business_insight": "Alta generación solar correlaciona con precios bajos en horario solar",
      "market_impact": "price_suppression_effect"
    }
  ]
}
```

### **Dominio Legal/Compliance** ⚖️
```json
{
  "cross_references": [
    {
      "source": "operaciones_generacion_real",
      "target": "compliance_ernc_requirements",
      "relation": "RENEWABLE_COMPLIANCE_CHECK",
      "compliance_status": "cumple",
      "regulatory_requirement": "20_percent_renewable_quota",
      "compliance_margin": "3.4_percent_above_minimum"
    }
  ]
}
```

## 🚀 **Algoritmo de Generación Automática**

### **Paso 1: Preparación de Datos**
```markdown
1. Normalizar todas las entidades (plantas, empresas, ubicaciones)
2. Extraer metadatos temporales (fechas, períodos)
3. Geocodificar ubicaciones cuando sea posible
4. Standardizar capacidades y unidades
```

### **Paso 2: Matching Matrix**
```python
# Crear matriz de similaridad entre documentos
similarity_matrix = calculate_pairwise_similarity(all_documents)

# Filtrar por threshold mínimo
potential_references = filter_by_confidence(similarity_matrix, min_threshold=0.7)

# Rankear por valor business
ranked_references = rank_by_business_value(potential_references)
```

### **Paso 3: Validación Automática**
```markdown
✅ Verificar consistencia temporal (no referencias imposibles)
✅ Validar coherencia de capacidades y ubicaciones
✅ Confirmar existencia de entidades referenciadas
✅ Checkear loops o referencias circulares
✅ Verificar threshold de confianza mínimo
```

## 📊 **Output Structure - Referencias Generadas**

```json
{
  "@context": "https://coordinador.cl/cross-references/v1",
  "@id": "cross_ref:operaciones_complete:2025_09",

  "generation_metadata": {
    "generation_date": "2025-09-25T14:30:00Z",
    "documents_processed": 12,
    "total_references_generated": 247,
    "confidence_threshold": 0.7,
    "processing_time_seconds": 45
  },

  "cross_references_by_type": {
    "temporal_relations": {
      "count": 89,
      "average_confidence": 0.87,
      "business_value": "trend_analysis"
    },

    "operational_relations": {
      "count": 74,
      "average_confidence": 0.82,
      "business_value": "performance_optimization"
    },

    "empresarial_relations": {
      "count": 52,
      "average_confidence": 0.91,
      "business_value": "portfolio_analysis"
    },

    "geographic_relations": {
      "count": 32,
      "average_confidence": 0.79,
      "business_value": "regional_planning"
    }
  },

  "high_value_references": [
    {
      "reference_id": "ref_001",
      "type": "PROGRAMMED_VS_ACTUAL_SYSTEMATIC_DEVIATION",
      "confidence": 0.96,
      "business_priority": "critical",
      "entities_involved": ["planta_solar_atacama", "planta_solar_quilapilun"],
      "insight": "Systematic 20% under-performance in Metropolitan Region solar plants",
      "recommended_action": "investigate_weather_data_accuracy",
      "estimated_impact": "15M_CLP_monthly_optimization_potential"
    }
  ],

  "quality_metrics": {
    "precision": 0.89,
    "recall": 0.84,
    "f1_score": 0.865,
    "false_positive_rate": 0.08,
    "business_value_score": 0.92
  }
}
```

## 🔮 **Casos de Uso Business**

### **Análisis de Performance Empresarial**
```sql
-- Query ejemplo habilitada por cross-referencias
SELECT
  empresa,
  AVG(factor_cumplimiento_programacion) as performance_promedio,
  COUNT(referencias_cruzadas) as nivel_integracion_datos
FROM plantas_con_referencias
WHERE periodo = '2025-09'
GROUP BY empresa
ORDER BY performance_promedio DESC;
```

### **Detección de Anomalías Sistémicas**
```python
# Análisis correlacional habilitado por referencias
def detect_systematic_issues():
    references = load_cross_references(type="PROGRAMMED_VS_ACTUAL")

    systematic_deviations = []
    for ref in references:
        if ref.confidence > 0.85 and ref.deviation_pattern == "consistent_underperformance":
            systematic_deviations.append(ref)

    return analyze_root_causes(systematic_deviations)
```

---

**🎯 Este sistema de cross-referencias permite análisis inteligente multi-dimensional del sistema eléctrico chileno, habilitando insights business que serían imposibles de detectar manualmente.**