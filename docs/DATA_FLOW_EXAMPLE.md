# 📊 Data Flow Example - Complete Walkthrough

## 🎯 Real-World Example: Processing ANEXO FALLAS Documents

This document shows a complete example of processing a new document type from start to finish, focusing on achieving maximum precision.

---

## 📄 Scenario: New Document Type Arrives

**You receive**: `anexo_fallas_enero_2025.pdf` - First incident report document you've ever seen.

**Goal**: Extract data with maximum precision and make it AI-queryable with validated rules.

---

## 🎯 High-Precision Approach (New Document Type)

### Step 1: Identify Document Type
```bash
# New PDF arrives
incoming_document.pdf → "anexo_fallas_enero_2025.pdf"

# You determine: This is a new type = "anexo_fallas"
```

### Step 2: Precision-First Processor Creation
```bash
# Create processor with full human validation for maximum precision
$ python scripts/tools/manage_rules.py create anexo_fallas \
  --sample-doc anexo_fallas_enero_2025.pdf \
  --validation full

🤖 AI Analysis Complete for: anexo_fallas
==========================================

AI Generated Suggestions:
📋 Cross-Reference Rules:
1. Critical Incidents → Legal (REQUIERE_REPORTE_LEGAL) - 95% confidence
   Reasoning: "Critical incidents require legal compliance reporting"

2. Equipment Failures → Markets (IMPACTA_GENERACION) - 80% confidence
   Reasoning: "Equipment failures affect generation and market prices"

🏷️ Semantic Tags:
• incidentes_operacionales
• equipos_afectados
• seguridad_sistema
• eventos_criticos

🔍 Human Validation Required (Maximum Precision):
===============================================

Rule 1: Critical Incidents → Legal
- Condition: "When incident severity is 'CRÍTICO'"
- Target: Legal domain
- Relation: REQUIERE_REPORTE_LEGAL
- Approve this rule? [Y/n]: Y ✅
- Adjust confidence? Current: 0.95 [Enter/new value]: 0.98 ✅

Rule 2: Equipment Failures → Markets
- Condition: "When 'potencia_afectada' > 50 MW"
- Target: Markets domain
- Relation: IMPACTA_GENERACION
- Approve this rule? [Y/n]: Y ✅
- Refine condition? [Y/n]: Y
  New condition: "When 'potencia_afectada' > 25 MW" ✅

Additional rule suggestions? [Y/n]: Y

🆕 Add custom business rules:
Rule name: Environmental Impact
Description: Major incidents affecting environmental systems
Condition: When environmental_impact = true
Target domain: legal
Relation: REQUIERE_EVALUACION_AMBIENTAL
Confidence: 0.95
✅ Custom rule added

Rule name: Cascading Failures
Description: Incidents that cause multiple system failures
Condition: When cascading_failure = true
Target domain: operaciones
Relation: REQUIERE_ANALISIS_SISTEMICO
Confidence: 0.90
✅ Custom rule added

Semantic tags validation:
• incidentes_operacionales ✅ Keep
• equipos_afectados ✅ Keep
• seguridad_sistema ✅ Keep
• eventos_criticos ✅ Keep
• impacto_ambiental 🆕 Added for environmental incidents
• fallas_cascada 🆕 Added for system-wide impacts
• alta_tension 🆕 Added for >220kV incidents

✅ Processor created with high-precision validated rules!
📁 Location: domains/operaciones/scripts/extract_anexo_fallas.py
⏱️ Total time: 20 minutes
🎯 Precision: Maximum (human-validated + custom business rules)
```
```bash
# Create processor with full human validation
$ python scripts/tools/manage_rules.py create anexo_fallas \
  --sample-doc anexo_fallas_enero_2025.pdf \
  --validation full

🤖 AI Analysis Complete for: anexo_fallas
==========================================

AI Generated Suggestions:
📋 Cross-Reference Rules:
1. Critical Incidents → Legal (REQUIERE_REPORTE_LEGAL) - 95% confidence
   Reasoning: "Critical incidents require legal compliance reporting"

2. Equipment Failures → Markets (IMPACTA_GENERACION) - 80% confidence
   Reasoning: "Equipment failures affect generation and market prices"

🏷️ Semantic Tags:
• incidentes_operacionales
• equipos_afectados
• seguridad_sistema
• eventos_criticos

🔍 Human Validation Required:
=============================

Rule 1: Critical Incidents → Legal
- Condition: "When incident severity is 'CRÍTICO'"
- Target: Legal domain
- Relation: REQUIERE_REPORTE_LEGAL
- Approve this rule? [Y/n]: Y ✅

Rule 2: Equipment Failures → Markets
- Condition: "When 'potencia_afectada' > 50 MW"
- Target: Markets domain
- Relation: IMPACTA_GENERACION
- Approve this rule? [Y/n]: Y ✅

Additional rule suggestions? [Y/n]: Y

🆕 Add custom rule:
Rule name: High Voltage Incidents
Condition: When voltage > 220 kV
Target domain: legal
Relation: REQUIERE_INVESTIGACION
Confidence: 0.90
✅ Custom rule added

Semantic tags validation:
• incidentes_operacionales ✅ Keep
• equipos_afectados ✅ Keep
• seguridad_sistema ✅ Keep
• eventos_criticos ✅ Keep
• alta_tension 🆕 Added

✅ Processor created with validated rules!
📁 Location: domains/operaciones/scripts/extract_anexo_fallas.py
⏱️ Total time: 18 minutes
```

### Step 3: High-Precision Processing
The generated processor now includes your custom rules:

```python
# Generated extract_anexo_fallas.py now includes:

def generar_referencias_anexo_fallas(datos):
    referencias = []

    # Validated rule 1
    if is_critical_incident(datos):
        referencias.append({
            "tipo_relacion": "REQUIERE_REPORTE_LEGAL",
            "dominio_objetivo": "legal",
            "confianza": 0.95
        })

    # Validated rule 2
    if affects_generation_over_50mw(datos):
        referencias.append({
            "tipo_relacion": "IMPACTA_GENERACION",
            "dominio_objetivo": "mercados",
            "confianza": 0.80
        })

    # Your custom rule
    if high_voltage_incident(datos):
        referencias.append({
            "tipo_relacion": "REQUIERE_INVESTIGACION",
            "dominio_objetivo": "legal",
            "confianza": 0.90
        })

    return referencias
```

---

## 🔄 Ongoing Usage - Both Approaches

### Processing More Documents (Same Type)
```bash
# February document arrives
$ python domains/operaciones/scripts/extract_anexo_fallas.py anexo_fallas_febrero_2025.pdf
✅ Processed in 30 seconds (uses same rules)

# March document arrives
$ python domains/operaciones/scripts/extract_anexo_fallas.py anexo_fallas_marzo_2025.pdf
✅ Processed in 30 seconds (uses same rules)

# Batch processing
$ for file in anexos_fallas_2025_*.pdf; do
    python domains/operaciones/scripts/extract_anexo_fallas.py "$file"
  done
✅ 50 documents processed in 25 minutes
```

### Refining Rules Later (Quick Approach Users)
```bash
# If you started with quick approach, you can refine later
$ python scripts/tools/manage_rules.py edit anexo_fallas

📋 ANEXO FALLAS - Rule Manager (AI-Generated Rules)
==================================================
⚠️  Rules were created with AI suggestions (not validated)

Current Cross-Reference Rules:
1. 🤖 Critical Incidents → Legal - Approve? [Y/n]: Y ✅ Now validated
2. 🤖 Equipment Failures → Markets - Approve? [Y/n]: Y ✅ Now validated

Add new rule? [Y/n]: Y
🆕 Added: High Voltage → Investigation Required

✅ Rules refined and processor regenerated!
```

---

## 📊 Results Comparison

### JSON Output Structure (Both Approaches)
```json
{
  "@context": "https://schema.org/context/v1",
  "@id": "doc:operaciones:anexo_fallas:2025-01-15",
  "@type": "DocumentoEstructurado",

  "metadatos_universales": {
    "titulo": "ANEXO - Reporte de Fallas Enero 2025",
    "dominio": "operaciones",
    "tipo_documento": "anexo_fallas",
    "fecha_creacion": "2025-01-15"
  },

  "entidades": {
    "entidades_principales": [
      {
        "@id": "ent:equipo:transformador_220kv_norte",
        "@type": "EquipoElectrico",
        "nombre": "Transformador 220kV Norte",
        "confianza": 0.9
      }
    ],
    "organizaciones": [
      {
        "@id": "ent:empresa:enel_chile",
        "@type": "EmpresaElectricaChile",
        "nombre": "Enel Chile",
        "confianza": 0.85
      }
    ]
  },

  "referencias_cruzadas": [
    {
      "documento_objetivo": "doc:legal:compliance_report:2025-01-15",
      "dominio_objetivo": "legal",
      "tipo_relacion": "REQUIERE_REPORTE_LEGAL",
      "confianza": 0.95,
      "contexto": "Incidente crítico requiere reporte de cumplimiento",
      "automatico": true
    }
  ],

  "etiquetas_semanticas": [
    "chile", "sen", "operaciones",
    "incidentes_operacionales",
    "equipos_afectados",
    "seguridad_sistema"
  ],

  "datos_especificos_dominio": {
    "operaciones": {
      "incidentes_reportados": {
        "rows": [
          {
            "fecha_incidente": "2025-01-15",
            "equipo_afectado": "Transformador 220kV Norte",
            "severidad": "CRÍTICO",
            "potencia_afectada": "150 MW",
            "empresa_responsable": "Enel Chile",
            "accion_correctiva": "Reemplazo programado"
          }
        ]
      }
    }
  },

  "metadatos_calidad": {
    "confianza_extraccion": 0.85,
    "metodo_procesamiento": "extraccion_automatizada"
  }
}
```

### AI Query Examples (Both Approaches Work)
```bash
# Queries that now work:
"What critical incidents occurred in January 2025?"
"Which equipment failures affected more than 100MW?"
"Show me all incidents that require legal reporting"
"What companies had the most equipment failures?"
"Compare incident frequency between January and February"
```

---

## ⚖️ Document Type Processing Comparison

| Situation | Setup Time | Accuracy | Processing Speed | Best For |
|-----------|------------|----------|------------------|----------|
| **New Document Type** | 20 minutes | Maximum (validated) | 30 sec/future docs | First-time precision setup |
| **Known Document Type** | 0 seconds | Consistent | 30 sec/doc | All subsequent processing |

---

## 🎯 Precision-First Workflow

### **For New Document Types:**
1. ✅ **Invest time upfront** - 20 minutes validation
2. ✅ **Custom business rules** - Add domain-specific logic
3. ✅ **Refined conditions** - Adjust thresholds for your needs
4. ✅ **Maximum precision** - Human-validated from start

### **Benefits of This Approach:**
- ✅ **Highest accuracy** from first document
- ✅ **Custom business logic** embedded
- ✅ **Production-ready** immediately
- ✅ **Consistent results** for all future documents
- ✅ **Domain expertise** captured in rules

### **Long-term ROI:**
- **20 minutes investment** → **Infinite precision processing**
- **Custom rules once** → **Applied to hundreds of documents**
- **Validated accuracy** → **Reliable AI insights**
- **Business logic** → **Competitive advantage**

**Result**: Maximum precision system that scales infinitely with consistent quality.