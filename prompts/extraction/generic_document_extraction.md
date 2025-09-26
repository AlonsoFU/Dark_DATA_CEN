# 📊 PROMPT - Extracción Universal de Documentos

## 🎯 Objetivo

Extraer información estructurada de cualquier tipo de documento, adaptándose automáticamente al contenido y estructura encontrados, independientemente de si tiene capítulos o es un documento unitario.

## 📋 Instrucciones de Extracción Universal

### **Fase 1: Contextualización Automática**

Basándote en el análisis previo del documento, adapta tu estrategia de extracción:

- **Si el documento tiene secciones/capítulos**: Procesa sección por sección
- **Si es un documento continuo**: Procesa el documento completo identificando bloques de información

### **Fase 2: Extracción Adaptativa**

#### **Entidades Universales (Extraer siempre)**

1. **👥 Personas**
   - Nombres completos mencionados
   - Roles o cargos asociados
   - Información de contacto si está disponible
   - Context de aparición (firma, mención, responsabilidad)

2. **🏢 Organizaciones**
   - Nombres de empresas, instituciones, organizaciones
   - Tipo de entidad (empresa, gobierno, ONG, etc.)
   - Información de contacto o ubicación
   - Relaciones entre organizaciones

3. **📍 Ubicaciones**
   - Direcciones específicas
   - Ciudades, regiones, países
   - Coordenadas geográficas si están presentes
   - Contexto geográfico relevante

4. **📅 Información Temporal**
   - Fechas específicas (formato ISO preferido)
   - Períodos (mensual, trimestral, anual)
   - Plazos y vencimientos
   - Rangos temporales

5. **💰 Datos Cuantitativos**
   - Valores monetarios (con moneda)
   - Porcentajes y ratios
   - Métricas y KPIs
   - Cantidades y medidas (con unidades)

#### **Extracción Específica por Tipo de Documento**

**Adapta automáticamente según el tipo detectado**:

##### **📈 Si es Documento Financiero**
- Balance: activos, pasivos, patrimonio
- P&L: ingresos, gastos, utilidades
- Ratios financieros: liquidez, rentabilidad, endeudamiento
- Comparativos temporales: año anterior, trimestre anterior
- Proyecciones: estimaciones futuras, presupuestos

##### **📋 Si es Documento Legal/Contractual**
- Partes del contrato: nombres, roles, representación
- Obligaciones: qué debe hacer cada parte
- Derechos: qué puede exigir cada parte
- Condiciones: requisitos, términos específicos
- Plazos: vencimientos, duraciones, fechas críticas

##### **🔧 Si es Documento Técnico**
- Especificaciones: parámetros técnicos, tolerancias
- Procedimientos: pasos secuenciales, instrucciones
- Requisitos: condiciones necesarias, estándares
- Referencias: normas aplicables, documentos relacionados
- Valores técnicos: medidas, capacidades, límites

##### **📊 Si es Informe Operacional**
- Métricas de rendimiento: KPIs, indicadores
- Resultados: logros, desviaciones, cumplimientos
- Comparativos: períodos anteriores, objetivos vs reales
- Análisis de causas: explicaciones de variaciones
- Recomendaciones: acciones sugeridas

## 📊 **Formato de Salida JSON Universal**

```json
{
  "extraction_metadata": {
    "document_type": "tipo_detectado",
    "extraction_date": "2025-09-25T14:30:00Z",
    "processing_method": "universal_adaptive",
    "confidence_threshold": 0.75,
    "total_entities_extracted": 0,
    "processing_time_minutes": 0
  },

  "document_info": {
    "title": "Título del documento si está disponible",
    "author": "Autor si identificado",
    "creation_date": "Fecha de creación si disponible",
    "pages_processed": "total",
    "language": "español | inglés | etc"
  },

  "universal_entities": {
    "people": [
      {
        "name": "Juan Pérez González",
        "role": "Director General",
        "organization": "Empresa ABC S.A.",
        "contact_info": "juan.perez@abc.com",
        "context": "Firmante del contrato",
        "confidence": 0.95
      }
    ],

    "organizations": [
      {
        "name": "Empresa ABC S.A.",
        "type": "empresa_privada",
        "industry": "tecnología",
        "location": "Santiago, Chile",
        "contact_info": "www.abc.com",
        "context": "Parte contratante principal",
        "confidence": 0.92
      }
    ],

    "locations": [
      {
        "address": "Av. Providencia 1234, Santiago",
        "city": "Santiago",
        "region": "Región Metropolitana",
        "country": "Chile",
        "coordinates": "-33.4489, -70.6693",
        "context": "Domicilio legal",
        "confidence": 0.88
      }
    ],

    "dates": [
      {
        "date": "2025-12-31",
        "type": "vencimiento",
        "description": "Fecha límite de entrega",
        "context": "Plazo contractual",
        "confidence": 0.96
      }
    ],

    "quantities": [
      {
        "value": 1500000,
        "unit": "CLP",
        "type": "monto_contractual",
        "description": "Valor total del contrato",
        "context": "Cláusula de pago",
        "confidence": 0.94
      }
    ]
  },

  "domain_specific_data": {
    // Contenido específico según el tipo de documento detectado
    // Se llena automáticamente basado en el tipo

    "financial_data": {  // Solo si es documento financiero
      "revenue": 2500000,
      "expenses": 1800000,
      "profit_margin": 0.28,
      "fiscal_period": "Q3 2025"
    },

    "legal_data": {  // Solo si es documento legal
      "contract_parties": ["Empresa ABC", "Cliente XYZ"],
      "contract_duration": "24 meses",
      "payment_terms": "30 días",
      "termination_clauses": ["incumplimiento", "caso fortuito"]
    },

    "technical_data": {  // Solo si es documento técnico
      "specifications": {
        "capacity": "100 MW",
        "voltage": "220 kV",
        "frequency": "50 Hz"
      },
      "requirements": ["ISO 9001", "Norma IEC 61850"],
      "tolerances": "±5%"
    },

    "operational_data": {  // Solo si es informe operacional
      "kpis": {
        "efficiency": 0.87,
        "availability": 0.95,
        "performance_vs_target": 1.12
      },
      "period": "Septiembre 2025",
      "comparatives": {
        "vs_previous_month": 0.03,
        "vs_same_month_last_year": 0.08
      }
    }
  },

  "relationships": [
    {
      "entity_1": "Juan Pérez González",
      "relationship_type": "works_for",
      "entity_2": "Empresa ABC S.A.",
      "confidence": 0.91
    }
  ],

  "key_insights": [
    {
      "insight": "Contrato de alto valor con plazo extendido",
      "importance": "high",
      "supporting_data": ["monto: 1.5M CLP", "duración: 24 meses"]
    }
  ],

  "quality_metrics": {
    "extraction_completeness": 0.89,
    "data_consistency": 0.92,
    "confidence_average": 0.87,
    "validation_flags": []
  }
}
```

## 🔧 **Validaciones Automáticas**

### **Consistencia de Datos**
- ✅ Fechas en formato válido y coherente
- ✅ Montos con moneda especificada
- ✅ Porcentajes en rango realista (0-100% típicamente)
- ✅ Nombres de personas con formato apropiado
- ✅ Direcciones con estructura geográfica válida

### **Coherencia Contextual**
- ✅ Entidades mencionadas múltiples veces tienen información consistente
- ✅ Fechas siguen secuencia lógica temporal
- ✅ Montos están en rangos esperados para el tipo de documento
- ✅ Referencias cruzadas dentro del documento son válidas

### **Quality Flags**
```json
{
  "quality_flags": [
    {
      "type": "warning",
      "message": "Fecha futura detectada, verificar contexto",
      "entity": "2026-15-32",
      "confidence_impact": -0.1
    },
    {
      "type": "info",
      "message": "Múltiples formatos de moneda detectados",
      "entities": ["USD", "CLP", "EUR"]
    }
  ]
}
```

## 🎯 **Instrucciones de Adaptación Automática**

### **Detección de Patrones**
1. **Si detectas tablas**: Extrae estructura tabular completa
2. **Si detectas listas**: Procesa como elementos relacionados
3. **Si detectas firmas**: Identifica personas y roles asociados
4. **Si detectas logotipos/sellos**: Identifica organizaciones

### **Manejo de Incertidumbre**
- **Alta confianza (>0.85)**: Extraer directamente
- **Media confianza (0.60-0.85)**: Extraer con flag de revisión
- **Baja confianza (<0.60)**: Marcar para validación manual

### **Escalabilidad y Flexibilidad**
- Adaptar campos JSON según contenido encontrado
- Agregar nuevos tipos de entidades si se detectan
- Expandir secciones domain_specific_data según el documento
- Mantener estructura base pero permitir extensiones

---

**🚀 Este prompt de extracción universal se adapta automáticamente a cualquier tipo de documento, proporcionando extracción estructurada y consistente sin requerir prompts específicos por tipo de documento.**