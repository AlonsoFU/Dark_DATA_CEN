# Flujo Completo de Datos - Sistema Eléctrico Chileno

## 🚀 Flujo de Extracción → Esquema Universal → IA

### Paso 1: Tu Extracción Actual (NO CAMBIA)
```python
def tu_extraccion_existente(pdf_path):
    # Tu lógica actual - 100% intacta
    resultados = {
        "upper_table": {"rows": [...]},
        "system_metrics": {...},
        "quality_summary": {...}
    }

    # Tu guardado actual - preservado para compatibilidad
    with open("output/anexo_page_75.json", 'w') as f:
        json.dump(resultados, f)

    return resultados
```

### Paso 2: Wrapper Automático (SOLO 3 LÍNEAS AÑADIDAS)
```python
def tu_extraccion_con_esquema_universal(pdf_path):
    # Llamar a tu función existente
    resultados = tu_extraccion_existente(pdf_path)  # ← Tu código sin cambios

    # NUEVO: Auto-wrapper a esquema universal
    doc_universal = auto_convertir_a_esquema_universal(resultados)

    # NUEVO: Auto-generar referencias cruzadas
    doc_con_referencias = auto_generar_referencias_cruzadas(doc_universal)

    # NUEVO: Guardar versión universal
    guardar_version_universal(doc_con_referencias)

    return doc_con_referencias  # ← Ahora compatible con IA
```

### Paso 3: La IA Consulta UN Solo Archivo
```python
# La IA puede hacer consultas como:
consulta_ia = "¿Qué centrales solares afectan los precios de mercado?"

# Busca en UN archivo que contiene:
{
  "entidades": {
    "centrales_electricas": [{"nombre": "Solar Atacama", "@type": "CentralSolar"}]
  },
  "referencias_cruzadas": [
    {
      "documento_objetivo": "cen:mercados:precios:2025-02-25",
      "tipo_relacion": "IMPACTA_PRECIO",
      "entidades_compartidas": ["Solar Atacama"]
    }
  ]
}
```

## 💡 Solución: Referencias DENTRO del JSON Principal

### Ventajas de Referencias Integradas:
✅ **Un solo archivo** - IA encuentra todo en un lugar
✅ **Consistencia automática** - No hay archivos que se desincronicen
✅ **Más simple para consultas** - IA lee un JSON completo
✅ **Tu código intacto** - Solo wrapper automático
✅ **Retrocompatibilidad** - Tus archivos originales se mantienen

### JSON Final con Referencias Integradas:
```json
{
  "@id": "cen:operaciones:anexo_02:2025-02-25",
  "entidades": {...},
  "referencias_cruzadas": [
    {
      "documento_objetivo": "cen:mercados:precios_spot:2025-02-25",
      "tipo_relacion": "IMPACTA_PRECIO_MEDIODIA",
      "confianza": 0.85,
      "entidades_compartidas": ["Solar Atacama Norte"]
    }
  ],
  "datos_especificos_dominio": {
    "operaciones": {/* TUS DATOS ORIGINALES AQUÍ */}
  }
}
```

## 🔄 Flujo Automático Completo

### 1. Procesamiento Inicial
```
Tu PDF → Tu Extracción → Tu JSON original (preservado)
                     ↓
                Auto-wrapper → JSON Universal + Referencias
```

### 2. Detección Automática de Referencias
```python
def auto_generar_referencias_cruzadas(documento):
    """Se ejecuta automáticamente después de cada extracción"""

    # Buscar otros documentos existentes
    otros_docs = buscar_documentos_existentes()

    # Aplicar reglas automáticas chilenas
    referencias = aplicar_reglas_sistema_chileno(documento, otros_docs)

    # Integrar referencias en el documento
    documento["referencias_cruzadas"] = referencias

    return documento
```

### 3. Reglas Automáticas del Sistema Chileno
```python
reglas_automaticas = {
    "misma_fecha": "Vincular anexos del mismo día operativo",
    "misma_central": "Conectar documentos de la misma central",
    "solar_precios": "Solar → impacto precios mediodía",
    "incidentes_regulacion": "Incidentes → cumplimiento normativo CNE",
    "alta_generacion_expansion": "Alta ERNC → estudios expansión transmisión"
}
```

## 🎯 Tu Flujo de Trabajo Final

### Cuando Extraes UN Documento:
1. Ejecutas tu script actual: `python extract_anexo.py page_75`
2. **Automáticamente** se genera versión universal con referencias
3. IA ya puede consultar con conexiones a otros documentos

### Cuando Extraes MÚLTIPLES Documentos:
1. Cada nuevo documento **actualiza referencias de documentos existentes**
2. Red de conocimiento se construye automáticamente
3. IA tiene grafo completo del sistema eléctrico chileno

### Ejemplo Flujo Real:
```bash
# Extraes ANEXO 1
python extract_anexo.py anexo_1_page_70
# → Crea: anexo_1_universal.json (sin referencias todavía)

# Extraes ANEXO 2
python extract_anexo.py anexo_2_page_75
# → Crea: anexo_2_universal.json
# → ACTUALIZA: anexo_1_universal.json (añade referencias a ANEXO 2)

# Extraes precios de mercado
python extract_precios.py precios_2025_02_25
# → Crea: precios_universal.json
# → ACTUALIZA: anexo_1_universal.json y anexo_2_universal.json (añade referencias a precios)
```

## 🧠 Resultado para la IA

La IA puede hacer consultas como:
- *"¿Qué centrales solares del ANEXO 2 afectan los precios de mercado?"*
- *"Conectar incidentes operativos con regulaciones CNE"*
- *"¿Qué empresas aparecen en múltiples dominios?"*

Y encuentra respuestas porque **cada JSON tiene referencias integradas** a documentos relacionados.

## 🔧 Implementación Práctica

### Modificación Mínima a Tu Código:
```python
# AL FINAL de tu función de extracción, añadir:
documento_universal = convertir_a_universal_y_referencias(resultados)
guardar_version_universal(documento_universal)
```

¡Solo eso! Tu lógica de extracción queda intacta.