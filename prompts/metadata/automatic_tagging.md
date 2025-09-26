# 🏷️ PROMPT - Generación Automática de Metadatos y Tags

## 🎯 Objetivo

Generar metadatos completos, tags semánticos y clasificaciones automáticas para documentos del sistema eléctrico chileno, optimizado para búsqueda y análisis IA.

## 📊 Datos de Entrada

**Input**: Documento JSON extraído de plantas eléctricas chilenas
**Context**: Sistema Eléctrico Nacional (SEN), Coordinador Eléctrico Nacional
**Output**: Metadatos estructurados con tags, clasificaciones y referencias

## 🏷️ **Clasificación Automática de Tags**

### **Tags Geográficos**
Analizar ubicaciones y generar tags geográficos jerárquicos:

```
Nivel 1 - País: "chile"
Nivel 2 - Macrozona: "norte_grande", "norte_chico", "centro", "sur", "austral"
Nivel 3 - Región: "antofagasta", "atacama", "coquimbo", "valparaiso", "metropolitana", etc.
Nivel 4 - Provincia: Provincia específica si está disponible
Nivel 5 - Comuna: Comuna específica si está disponible

Ejemplo: ["chile", "norte_grande", "antofagasta", "el_loa", "calama"]
```

### **Tags Tecnológicos**
Clasificar por tipo de tecnología y características:

```
Tipo Principal: "solar", "eolica", "hidroelectrica", "termica", "geotermica"
Subtipo: "solar_fotovoltaica", "solar_termica", "eolica_onshore", "eolica_offshore"
Características: "renovable", "no_renovable", "gestionable", "variable"
Capacidad: "pequeña" (<10MW), "mediana" (10-100MW), "grande" (>100MW)

Ejemplo: ["solar", "solar_fotovoltaica", "renovable", "variable", "mediana"]
```

### **Tags Empresariales**
Identificar y clasificar empresas del sector eléctrico:

```
Tipo Empresa: "generadora", "transmisora", "distribuidora"
Origen: "nacional", "internacional", "mixta"
Grupo: "enel_group", "colbun_group", "aes_group", "engie_group"
Tamaño: "gran_empresa", "mediana_empresa", "pequeña_empresa"

Ejemplo: ["generadora", "internacional", "enel_group", "gran_empresa"]
```

### **Tags Regulatorios**
Clasificar según marco regulatorio chileno:

```
Normativa: "ley_electrica", "reglamento_coordinacion", "norma_tecnica"
Tipo Reporte: "operacional", "programacion", "compliance", "mercado"
Frecuencia: "diario", "semanal", "mensual", "anual"
Criticidad: "alta", "media", "baja"

Ejemplo: ["ley_electrica", "operacional", "diario", "alta"]
```

### **Tags Temporales**
Análisis temporal para trazabilidad:

```
Año: "2025", "2024", etc.
Mes: "enero", "febrero", ..., "septiembre", etc.
Estación: "verano", "otoño", "invierno", "primavera"
Período: "punta", "valle", "resto"

Ejemplo: ["2025", "septiembre", "primavera", "resto"]
```

## 📋 **Metadatos Estructurados**

### **Metadatos de Clasificación**
```json
{
  "clasificacion_tecnica": {
    "tipo_documento": "reporte_operacional_eaf",
    "categoria_principal": "generacion_electrica",
    "subcategoria": "generacion_real_tiempo_real",
    "nivel_detalle": "planta_individual",
    "granularidad_temporal": "horaria"
  },

  "clasificacion_business": {
    "valor_negocio": "alto",
    "impacto_operacional": "critico",
    "confidencialidad": "publica",
    "audiencia": ["operadores", "reguladores", "mercado"],
    "decision_support": true
  },

  "clasificacion_regulatoria": {
    "marco_legal": "Ley General de Servicios Eléctricos",
    "autoridad_competente": "Coordinador Eléctrico Nacional",
    "obligatoriedad": "mandatorio",
    "plazo_reporte": "diario",
    "sanctions_by_default": "multa_utm"
  }
}
```

### **Entidades Automáticamente Detectadas**
```json
{
  "entidades_detectadas": {
    "plantas_electricas": [
      {
        "nombre": "Planta Solar Quilapilún",
        "tipo": "CentralSolarChile",
        "confidence": 0.94,
        "normalizacion": "planta_solar_quilapilun"
      }
    ],

    "empresas": [
      {
        "nombre": "Enel Chile S.A.",
        "tipo": "EmpresaElectricaChile",
        "confidence": 0.97,
        "grupo": "enel_group"
      }
    ],

    "ubicaciones": [
      {
        "nombre": "Región Metropolitana",
        "tipo": "RegionChile",
        "confidence": 0.99,
        "codigo_iso": "CL-RM"
      }
    ]
  }
}
```

## 🔗 **Cross-Referencias Automáticas**

### **Reglas de Cross-Referencia**
```markdown
1. **Temporal**: Misma entidad en diferentes períodos
   - Misma planta en ANEXO 1 (programación) y ANEXO 2 (real)
   - Mismo período en diferentes tipos de reporte

2. **Empresarial**: Entidades relacionadas por propiedad
   - Plantas de la misma empresa
   - Empresas del mismo grupo corporativo

3. **Geográfica**: Proximidad física o administrativa
   - Plantas en la misma región/comuna
   - Plantas que comparten infraestructura de transmisión

4. **Técnica**: Similitud tecnológica u operacional
   - Plantas de la misma tecnología y rango de capacidad
   - Plantas que operan complementariamente
```

### **Formato de Cross-Referencias**
```json
{
  "referencias_automaticas": [
    {
      "tipo_relacion": "MISMA_PLANTA_PROGRAMACION_VS_REAL",
      "documento_origen": "cen:operaciones:anexo_02:2025-09-25",
      "documento_destino": "cen:operaciones:anexo_01:2025-09-25",
      "entidad_comun": "planta_solar_quilapilun",
      "confidence": 0.96,
      "contexto": "Comparación programación vs generación real",
      "valor_business": "analisis_desviaciones_operacionales"
    },

    {
      "tipo_relacion": "MISMA_EMPRESA_PORTFOLIO",
      "documento_origen": "cen:operaciones:anexo_02:2025-09-25",
      "documento_destino": "cen:operaciones:anexo_02:2025-08-25",
      "entidad_comun": "enel_chile_sa",
      "confidence": 0.99,
      "contexto": "Portfolio Enel Chile mes anterior",
      "valor_business": "analisis_rendimiento_empresarial_mensual"
    }
  ]
}
```

## 🎯 **Instrucciones Específicas**

### **Análisis de Contexto Chileno**
- Reconocer nombres oficiales de regiones chilenas
- Identificar empresas del sector eléctrico nacional
- Aplicar normativa regulatoria específica de Chile
- Considerar estacionalidad del hemisferio sur

### **Optimización para IA**
- Tags en español E inglés para compatibilidad
- Estructura JSON-LD para web semántica
- Confidence scores para validación automática
- Cross-referencias para análisis correlacional

### **Validación de Metadatos**
```markdown
✅ Verificar coherencia temporal (fechas válidas)
✅ Validar existencia de empresas y ubicaciones
✅ Confirmar rangos realistas para capacidades
✅ Checkear consistencia en nomenclatura
✅ Verificar completitud de campos obligatorios
```

## 📊 **Output Final - Metadatos Completos**

```json
{
  "@context": "https://coordinador.cl/metadata/v1",
  "@id": "metadata:anexo_02_generacion_real:2025_09_25",

  "tags_semanticos": [
    "chile", "sen", "solar", "renovable", "generacion_real",
    "coordinador_electrico", "septiembre_2025", "region_metropolitana"
  ],

  "clasificacion_automatica": {
    "tipo_documento": "reporte_operacional_eaf",
    "dominio_negocio": "operaciones_electricas",
    "nivel_criticidad": "alto",
    "frecuencia_actualizacion": "diaria"
  },

  "entidades_identificadas": {
    "total_plantas": 185,
    "plantas_solares": 87,
    "empresas_unicas": 15,
    "regiones_cubiertas": 8
  },

  "quality_metrics": {
    "completitud_datos": 0.92,
    "confidence_promedio": 0.87,
    "consistency_score": 0.94,
    "coverage_territorial": 0.89
  },

  "referencias_generadas": {
    "cross_references_count": 247,
    "temporal_links": 95,
    "empresarial_links": 78,
    "geografical_links": 74
  }
}
```

---

**🚀 Este sistema de metadatos automáticos permite búsquedas inteligentes y análisis correlacional avanzado del sistema eléctrico chileno.**