# 🔍 PROMPT - Análisis Universal de Documentos

## 🎯 Objetivo

Analizar cualquier tipo de documento para determinar su estructura, contenido y la mejor estrategia de extracción de datos, independientemente de si tiene capítulos o es un documento unitario.

## 📋 Instrucciones de Análisis

### **Análisis Inicial**

Examina este documento y proporciona un análisis estructurado que responda:

#### **1. Identificación del Documento**
- **Tipo de documento**: Reporte financiero, contrato legal, manual técnico, análisis académico, informe operacional, etc.
- **Propósito**: ¿Para qué fue creado este documento?
- **Audiencia objetivo**: ¿A quién está dirigido?
- **Nivel de formalidad**: Formal/oficial, informal, técnico, ejecutivo

#### **2. Estructura del Documento**
- **¿Tiene capítulos/secciones definidas?**: Sí/No
- **Si SÍ tiene secciones**:
  - Lista todos los capítulos/secciones principales
  - Describe el tipo de contenido en cada sección
  - Identifica si hay subsecciones importantes
  - Determina si las secciones son independientes o secuenciales

- **Si NO tiene secciones formales**:
  - Describe la organización general del contenido
  - Identifica patrones de información repetitivos
  - Detecta si hay bloques de contenido distinguibles

#### **3. Análisis de Contenido**
- **Tipos de datos presentes**:
  - Tablas numéricas
  - Listas de elementos
  - Texto narrativo
  - Datos temporales (fechas, períodos)
  - Métricas y KPIs
  - Referencias a otras entidades

- **Entidades principales identificadas**:
  - Personas mencionadas
  - Organizaciones/empresas
  - Ubicaciones geográficas
  - Fechas y períodos importantes
  - Conceptos técnicos clave
  - Métricas o valores numéricos importantes

#### **4. Complejidad y Estrategia de Extracción**
- **Nivel de complejidad**: Baja, Media, Alta
- **Estrategia recomendada**:
  - Procesamiento completo del documento
  - Procesamiento por secciones
  - Procesamiento con OCR especializado
  - Procesamiento con análisis de tablas

- **Desafíos potenciales**:
  - Calidad de imagen/escaneo
  - Tablas complejas
  - Texto en columnas múltiples
  - Gráficos con datos relevantes

## 📊 **Formato de Respuesta JSON**

```json
{
  "document_analysis": {
    "identification": {
      "document_type": "reporte_financiero | contrato_legal | manual_tecnico | informe_operacional | etc",
      "purpose": "Descripción del propósito del documento",
      "target_audience": "ejecutivos | técnicos | legal | operacional | etc",
      "formality_level": "formal | informal | técnico | ejecutivo",
      "language": "español | inglés | etc",
      "estimated_pages": 0
    },

    "structure": {
      "has_chapters": true,  // o false
      "structure_type": "sectioned | continuous | mixed",

      "sections": [  // Solo si has_chapters es true
        {
          "section_name": "Capítulo 1: Resumen Ejecutivo",
          "content_type": "resumen | datos_tabulares | narrativo | técnico",
          "pages": "1-3",
          "key_information": "Descripción del contenido principal"
        }
      ],

      "content_organization": "Descripción de cómo está organizado el contenido",  // Si has_chapters es false
      "repeating_patterns": ["patrón1", "patrón2"]  // Patrones identificados
    },

    "content_analysis": {
      "data_types": {
        "tables": true,
        "numerical_data": true,
        "temporal_data": true,
        "narrative_text": true,
        "lists": true,
        "references": true
      },

      "key_entities": {
        "people": ["Juan Pérez", "María González"],
        "organizations": ["Empresa ABC S.A.", "Instituto XYZ"],
        "locations": ["Santiago", "Región Metropolitana"],
        "dates": ["2025-09-01", "Q3 2025"],
        "technical_concepts": ["ROI", "EBITDA", "Factor de carga"],
        "metrics": ["15.5%", "$1.2M", "85 MW"]
      },

      "content_density": "alta | media | baja",
      "information_quality": "excelente | buena | regular | pobre"
    },

    "extraction_strategy": {
      "complexity_level": "baja | media | alta",
      "recommended_approach": "complete_document | section_by_section | specialized_ocr | table_focused",

      "processing_recommendations": [
        "Procesamiento por secciones recomendado",
        "Usar OCR especializado para tablas",
        "Priorizar extracción de métricas financieras"
      ],

      "potential_challenges": [
        "Calidad de escaneo variable",
        "Tablas con formato complejo",
        "Referencias cruzadas múltiples"
      ],

      "estimated_processing_time": "30-90 minutos",
      "confidence_expectation": "alto | medio | bajo"
    },

    "business_value": {
      "information_value": "crítico | alto | medio | bajo",
      "automation_potential": "alto | medio | bajo",
      "analysis_opportunities": [
        "Análisis de tendencias temporales",
        "Comparación con documentos similares",
        "Extracción de KPIs clave"
      ]
    }
  }
}
```

## 🔧 **Instrucciones Específicas por Tipo**

### **Para Documentos Financieros**
- Identificar: Balance, P&L, Cash Flow, métricas financieras
- Buscar: Períodos fiscales, comparativos año anterior, proyecciones
- Extraer: Números clave, ratios, tendencias

### **Para Documentos Legales**
- Identificar: Cláusulas, obligaciones, derechos, plazos
- Buscar: Fechas de vencimiento, partes involucradas, términos clave
- Extraer: Obligaciones específicas, condiciones, referencias legales

### **Para Documentos Técnicos**
- Identificar: Especificaciones, procedimientos, requisitos
- Buscar: Parámetros técnicos, tolerancias, estándares
- Extraer: Valores técnicos, procedimientos paso a paso, referencias

### **Para Informes Operacionales**
- Identificar: Métricas de rendimiento, indicadores, resultados
- Buscar: Comparaciones periódicas, tendencias, desviaciones
- Extraer: KPIs, variaciones, análisis de causas

## ⚠️ **Consideraciones Importantes**

### **Validaciones Automáticas**
- ✅ Verificar coherencia en fechas identificadas
- ✅ Confirmar consistencia en entidades mencionadas
- ✅ Validar formato de números y métricas
- ✅ Checkear referencias cruzadas dentro del documento

### **Banderas de Alerta**
- 🚨 Calidad de imagen muy pobre (confianza < 0.6)
- 🚨 Documento con múltiples idiomas mezclados
- 🚨 Estructura inconsistente o anómala
- 🚨 Datos aparentemente incorrectos o incoherentes

---

**🎯 Este prompt de análisis universal está diseñado para funcionar con cualquier tipo de documento y proporciona la base para una extracción de datos efectiva y adaptada al contenido específico.**