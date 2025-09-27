# 📊 Data Flow - Metodología General para Procesamiento de Documentos

## 🎯 Objetivo del Documento

Esta es la **guía metodológica completa** para procesar **CUALQUIER documento nuevo** en la Dark Data Platform. Seguir estos pasos garantiza extraer inteligencia estructurada de cualquier PDF, desde informes financieros hasta manuales técnicos.

```
📄 Documento PDF → 🔍 Análisis → 🧩 División → 🤖 Extracción → ✋ Validación → 💾 Base de Datos → 🔍 AI Queries
```

---

## 🚀 **METODOLOGÍA GENERAL - OVERVIEW**

### **Proceso Universal (6 Fases - 2-4 horas total)**

| Fase | Tiempo | Descripción | Output |
|------|--------|-------------|--------|
| **1. Obtención** | 15-30 min | Conseguir y organizar documentos | PDF limpio |
| **2. Análisis Estructural** | 30-60 min | Detectar capítulos, secciones, patrones | Mapa de estructura |
| **3. Extracción Adaptativa** | 45-90 min | Extraer contenido específico del documento | Datos estructurados |
| **4. Validación Manual** | 30-60 min | Revisar y aprobar extracciones críticas | Datos validados |
| **5. Transformación Universal** | 15-30 min | Convertir a esquema estándar | JSON universal |
| **6. Ingesta y Acceso AI** | 15-30 min | Cargar a base de datos y activar MCP | AI-queryable |

**Resultado Final**: Documento completamente procesado y disponible para consultas AI

---

## 📥 **FASE 1: OBTENCIÓN DE DOCUMENTOS** (15-30 minutos)

### Paso 1.1: Determinar Fuente del Documento 📁

**A) Documentos Públicos Online**

**Para documento único (descarga simple):**
```bash
wget "https://ejemplo.com/documento.pdf" -O source_document.pdf
```

**Para múltiples documentos del mismo tipo (necesitas scraper):**

1. **Primero verificar si ya existe scraper para el sitio:**
```bash
ls domains/{tu_dominio}/shared/scrapers/
```

2. **Si existe scraper, usarlo:**
```bash
cd domains/{tu_dominio}/shared/scrapers/
python coordinador_scraper.py --download-latest
```

3. **Si NO existe scraper, crear uno nuevo:**
```bash
cd domains/{tu_dominio}/shared/scrapers/
python create_scraper.py --target-url "https://ejemplo.com/documentos/"
```

**B) Documentos Privados/Locales**
```bash
mkdir -p domains/{tu_dominio}/data/source_documents/
cp "/ruta/a/tu/documento.pdf" domains/{tu_dominio}/data/source_documents/
```

### Paso 1.2: Organización Inicial 🗂️

**Crear estructura básica para nuevo dominio/documento:**

1. **Crear directorio principal del documento:**
```bash
mkdir -p domains/{tu_dominio}/chapters/{documento_tipo}/
```

2. **Crear subdirectorios necesarios:**
```bash
mkdir -p domains/{tu_dominio}/chapters/{documento_tipo}/docs/
mkdir -p domains/{tu_dominio}/chapters/{documento_tipo}/processors/
mkdir -p domains/{tu_dominio}/chapters/{documento_tipo}/outputs/
```

3. **Crear directorio compartido del dominio:**
```bash
mkdir -p domains/{tu_dominio}/shared/
```

**⚠️ Importante sobre la estructura de documentos:**
- **La carpeta "chapters/" NO significa que tu documento tenga capítulos**
- **Es solo organización**: Cada documento va en su propia carpeta dentro de "chapters/"
- **Tu documento puede ser**:
  - **Documento con capítulos** (ej: manual de 200 páginas con secciones)
  - **Documento unitario** (ej: contrato de 10 páginas sin divisiones)
  - **Documento con partes** (ej: reporte con introducción, análisis, conclusiones)

**¿Cuándo crear nuevo dominio vs nueva carpeta de documento?**
- **Nuevo dominio**: Área de negocio completamente diferente (ej: legal, financiero, técnico)
- **Nueva carpeta**: Mismo dominio, diferente tipo de documento (ej: diferentes reportes financieros)

---

## 🔍 **FASE 2: ANÁLISIS ESTRUCTURAL** (30-60 minutos)

### Paso 2.1: Análisis Automático de Estructura 🤖

**Opción A) Intentar herramientas automáticas (si existen):**
```bash
python ai_platform/analyzers/document_structure_analyzer.py \
  --document "domains/{tu_dominio}/data/source_documents/documento.pdf" \
  --output "analysis_result.json"
```

**Opción B) Análisis con Claude Code (Recomendado):**

Usar Claude Code para analizar la estructura del documento. **Prompt de ejemplo**:

```
Analiza este documento PDF y determina su estructura:

**1. TIPO DE DOCUMENTO**
- ¿Es financiero, legal, técnico, operacional, académico?
- ¿Cuál es su propósito principal?

**2. ESTRUCTURA GENERAL**
- ¿Tiene capítulos/secciones claramente definidos?
- ¿Es un documento unitario sin divisiones?
- ¿Hay patrones repetitivos (tablas, listas)?

**3. DIVISIÓN LÓGICA**
- Si tiene capítulos: ¿En qué páginas empiezan y terminan?
- Si es unitario: ¿Qué secciones lógicas identificas?

**4. ENTIDADES PRINCIPALES**
- ¿Qué tipos de datos contiene? (empresas, fechas, métricas, etc.)
- ¿Hay tablas con datos estructurados?
- ¿Qué información es más valiosa para extraer?

**5. COMPLEJIDAD DE PROCESAMIENTO**
- Nivel estimado: Simple/Medio/Complejo
- ¿Requiere OCR especial o es texto seleccionable?

Responde en formato JSON estructurado.
```

⚠️ **Nota**: **Adapta este prompt** a tu documento específico. Claude Code puede leer PDFs directamente y darte un análisis personalizado.

### Paso 2.2: División de Capítulos/Secciones (Si Aplica) 📑

**⚠️ Importante**: No todos los documentos tienen capítulos. Elige la opción según tu documento:

**A) Para Documentos con Capítulos/Secciones Claras**
(ej: manual técnico, reporte extenso, documento académico)

1. **Ir al directorio de procesadores:**
```bash
cd domains/{tu_dominio}/chapters/{documento_tipo}/processors/
```

2. **Ejecutar detector automático de divisiones:**
```bash
python ai_platform/processors/chapter_divider.py \
  --document "../../../data/source_documents/documento.pdf" \
  --analysis "../../../analysis_result.json" \
  --output "chapter_divisions.json"
```

**B) Para Documentos Unitarios**
(ej: contrato, carta, factura, documento simple)

**Crear archivo de división simple:**
```bash
echo '{"type": "single_document", "pages": "all"}' > chapter_divisions.json
```

### Paso 2.3: Validación Manual de División ✋

**Revisar la división propuesta:**
```bash
python shared_platform/cli/review_divisions.py --interactive \
  --divisions "chapter_divisions.json" \
  --document "../../../data/source_documents/documento.pdf"
```

**Ejemplo de validación interactiva**:
```
🔍 División propuesta:
├── Capítulo 1: Páginas 1-15 (Introducción)
├── Capítulo 2: Páginas 16-45 (Análisis Principal)
├── Capítulo 3: Páginas 46-60 (Conclusiones)

¿Aprobar esta división? [y/n/edit]: y
```

---

## 🤖 **FASE 3: EXTRACCIÓN ADAPTATIVA** (45-90 minutos)

### Paso 3.1: Generación de Extractor Específico 🛠️

**Opción A) Usar herramientas automáticas (si existen):**
```bash
python ai_platform/processors/adaptive_document_processor.py \
  --document "domains/{tu_dominio}/data/source_documents/documento.pdf" \
  --analysis "analysis_result.json" \
  --divisions "chapter_divisions.json" \
  --output-processor "{documento_tipo}_processor.py"
```

**Opción B) Crear extractor con Claude Code (Recomendado):**

Pedirle a Claude Code que genere el extractor específico. **Prompt de ejemplo**:

```
Basándote en el análisis del documento, crea un extractor Python específico:

**CONTEXTO DEL DOCUMENTO**:
- Tipo: [Resultado del análisis anterior]
- Estructura: [División encontrada]
- Entidades principales: [Lo que identificaste]

**CREAR EXTRACTOR QUE**:
1. **Extraiga entidades específicas** del tipo de documento
2. **Maneje la estructura** (capítulos o documento unitario)
3. **Valide rangos realistas** para los datos
4. **Normalice nombres** de entidades

**TIPOS DE EXTRACCIÓN SEGÚN DOCUMENTO**:
- **Financiero**: Métricas, ratios, balances, flujos de caja
- **Legal**: Partes, obligaciones, fechas críticas, clausulas
- **Técnico**: Especificaciones, procedimientos, equipos
- **Operacional**: KPIs, procesos, incidentes, métricas

**INCLUIR EN EL CÓDIGO**:
- Validaciones específicas del dominio
- Manejo de errores
- Logging para debugging
- Métricas de confianza

Crea el archivo {documento_tipo}_processor.py con el código completo.
```

⚠️ **Importante**: Claude Code puede generar el extractor pero **necesitarás iterar y personalizar** el código 5-10 veces según tu documento específico.

### Paso 3.2: Primera Revisión Técnica del Extractor 🎯

1. **Ir al directorio de procesadores:**
```bash
cd domains/{tu_dominio}/chapters/{documento_tipo}/processors/
```

2. **Ejecutar extractor generado:**
```bash
python {documento_tipo}_processor.py \
  --input "../../../data/source_documents/documento.pdf" \
  --output "../outputs/raw_extractions/" \
  --confidence-threshold 0.7
```
💡 **Nota**: También puedes pedirle a Claude Code que ejecute este comando por ti.

3. **Revisar resultados iniciales:**
```bash
python review_extractions.py --interactive \
  --results "../outputs/raw_extractions/extraction_results.json"
```
💡 **Nota**: Claude Code puede revisar los resultados y hacer la validación interactiva contigo.

**Proceso de calibración técnica (repetir 3-8 veces según complejidad):**

⚠️ **Objetivo**: Hacer que el extractor funcione bien técnicamente, NO validar cada dato.

1. **Ejecutar extractor en modo prueba:**
```bash
python {documento_tipo}_processor.py --test-mode
```
💡 **Nota**: Claude Code puede ejecutar esto y analizar los resultados.

2. **Identificar problemas específicos:**
```bash
python identify_extraction_issues.py
```
💡 **Nota**: Claude Code puede identificar problemas automáticamente revisando los outputs.

3. **Refinar código según problemas encontrados**
   (Esto requiere edición manual del processor)

4. **Medir confianza actual:**
```bash
confidence=$(python measure_confidence.py)
echo "Confianza actual: $confidence"
```
💡 **Nota**: Claude Code puede calcular métricas de confianza automáticamente.

5. **Repetir hasta lograr >85% confianza**

### Paso 3.3: Generación de Metadatos y Tags 🏷️

**Opción A) Herramientas automáticas:**
```bash
python ai_platform/processors/metadata_generator.py \
  --input "domains/{tu_dominio}/chapters/{documento_tipo}/outputs/raw_extractions/" \
  --output "../outputs/enriched_metadata.json"
```

**Opción B) Generar metadatos con Claude Code (Recomendado):**

Pedirle a Claude Code que genere metadatos específicos. **Prompt de ejemplo**:

```
Analiza los datos extraídos y genera metadatos enriquecidos:

**GENERAR TAGS PARA**:
1. **Tags Semánticos**: Conceptos clave, temas principales
2. **Tags Temporales**: Períodos, fechas relevantes, vigencia
3. **Tags Geográficos**: Países, regiones, ciudades mencionadas
4. **Tags de Entidades**: Personas, organizaciones, productos
5. **Tags de Clasificación**: Tipo, propósito, audiencia objetivo

**TAGS ESPECÍFICOS SEGÚN DOMINIO**:
- **Financiero**: ratios, métricas, períodos fiscales, instrumentos
- **Legal**: tipo_contrato, jurisdicción, obligaciones, derechos
- **Técnico**: especificaciones, normas, procedimientos, equipos
- **Operacional**: KPIs, procesos, departamentos, métricas

**IDENTIFICAR REFERENCIAS CRUZADAS**:
- Entidades que podrían aparecer en otros documentos
- Períodos temporales relevantes
- Organizaciones mencionadas
- Temas relacionados

Crea el archivo enriched_metadata.json con los metadatos estructurados.
```

⚠️ **Nota**: Claude Code puede generar metadatos automáticamente, pero **revisa y personaliza** según el contexto específico de tu documento.

---

## ✋ **FASE 4: VALIDACIÓN MANUAL** (30-60 minutos)

⚠️ **Diferencia clave con Fase 3.2**:
- **Paso 3.2**: Primera revisión **técnica** - ¿funciona bien el extractor?
- **Paso 4.1**: Revisión **de contenido** - ¿son correctos estos datos específicos?

### Paso 4.1: Revisión Final de Contenido (Validación Humana) 🔎

⚠️ **Objetivo**: Validar cada dato extraído individualmente - ¿es correcto este resultado específico?

```bash
cd domains/{tu_dominio}/chapters/{documento_tipo}/
python shared_platform/cli/validation_interface.py \
  --data "outputs/raw_extractions/" \
  --metadata "outputs/enriched_metadata.json" \
  --interactive
```
💡 **Nota**: Claude Code puede hacer toda la validación conversacionalmente contigo, revisando cada extracción.

**Interfaz de validación típica**:
```
🔍 Extracción #1 - Empresa XYZ S.A.
├── Tipo: Organización
├── Ubicación: Santiago, Chile
├── Sector: Energía
├── Métrica asociada: 150 MW capacidad
├── Confianza IA: 0.89
├── Tags: [energia, chile, capacidad_instalpada]

¿Aprobar esta extracción? [y/n/edit/skip]:
- y: Aprobar como está
- n: Rechazar completamente
- edit: Corregir datos
- skip: Revisar después

Selección: edit
├── Corrección: Cambiar "150 MW" → "150.5 MW"
├── Tag adicional: "solar_energy"
✅ Guardado
```

### Paso 4.2: Control de Calidad por Lotes 📊

```bash
python shared_platform/cli/quality_checker.py \
  --validated-data "outputs/validated_extractions/" \
  --original-document "../../../data/source_documents/documento.pdf" \
  --generate-report
```
💡 **Nota**: Claude Code puede generar reportes de calidad automáticamente.

**Métricas de calidad generadas**:
```
📊 Reporte de Calidad:
├── Páginas procesadas: 45/45 (100%)
├── Entidades extraídas: 127
├── Entidades validadas: 119 (93.7%)
├── Entidades rechazadas: 8 (6.3%)
├── Confianza promedio: 0.91
├── Tiempo total: 42 minutos
└── Status: ✅ APTO PARA PRODUCCIÓN
```

### Paso 4.3: Generación de Referencias Cruzadas 🔗

**Opción A) Herramientas automáticas:**
```bash
python ai_platform/processors/cross_reference_generator.py \
  --current-document "outputs/validated_extractions/" \
  --database "platform_data/database/dark_data.db" \
  --output "outputs/cross_references.json"
```

**Opción B) Detectar referencias con Claude Code (Recomendado):**

Pedirle a Claude Code que identifique referencias cruzadas. **Prompt de ejemplo**:

```
Analiza los datos validados e identifica referencias cruzadas potenciales:

**BUSCAR RELACIONES**:
1. **Entidad Idéntica**: Misma empresa/persona en otros documentos
2. **Temporal**: Documentos del mismo período o fechas relacionadas
3. **Geográfica**: Misma ubicación/región/país
4. **Temática**: Mismo sector/industria/tema
5. **Funcional**: Documentos que se complementan

**ASIGNAR CONFIANZA**:
- 0.95+: Prácticamente certeza (nombre exacto + contexto)
- 0.85-0.94: Alta confianza (variaciones menores)
- 0.70-0.84: Confianza media (contexto similar)
- <0.70: Baja confianza (solo sugerencia)

**PRIORIZAR**:
- Referencias que agreguen valor business
- Evitar conexiones triviales
- Incluir razón de la relación

Consulta la base de datos dark_data.db y crea cross_references.json con las relaciones encontradas.
```

⚠️ **Importante**: Claude Code puede acceder a la base de datos y **detectar referencias automáticamente**, pero siempre valida manualmente las más importantes.

---

## 💾 **FASE 5: TRANSFORMACIÓN UNIVERSAL** (15-30 minutos)

### Paso 5.1: Aplicación del Esquema Universal 🔄

**Opción A) Transformador automático (si existe):**
```bash
cd domains/{tu_dominio}/chapters/{documento_tipo}/
python shared_platform/transformers/universal_schema_transformer.py \
  --input "outputs/validated_extractions/" \
  --metadata "outputs/enriched_metadata.json" \
  --cross-refs "outputs/cross_references.json" \
  --domain "{tu_dominio}" \
  --document-type "{documento_tipo}" \
  --output "outputs/universal_json/"
```

**Opción B) Transformación con Claude Code (Recomendado):**

⚠️ **Importante**: Cada documento tiene salidas diferentes. Claude Code puede crear la transformación específica.

**Prompt de ejemplo para transformación específica**:

```
Transforma los datos extraídos al esquema universal de la plataforma:

**DATOS DE ENTRADA**:
- Extracciones validadas: [contenido específico de tu documento]
- Metadatos: [tags y referencias de tu documento]
- Cross-referencias: [relaciones encontradas]

**ESQUEMA UNIVERSAL OBJETIVO**:
```json
{
  "@context": "https://darkdata.platform/context/v1",
  "@id": "ddp:{dominio}:{documento_tipo}:{fecha}",
  "@type": "ProcessedDocument",

  "document_metadata": {
    "document_id": "único_identificador",
    "document_type": "{documento_tipo}",
    "domain": "{tu_dominio}",
    "source_file": "nombre_original.pdf",
    "processing_date": "2025-09-26T10:30:00Z",
    "extraction_version": "1.0",
    "quality_score": 0.91
  },

  "extracted_entities": {
    "organizations": [...],
    "people": [...],
    "locations": [...],
    "dates": [...],
    "metrics": [...],
    "domain_specific": {...}
  },

  "semantic_tags": {
    "universal_tags": ["tag1", "tag2"],
    "domain_tags": ["domain_tag1"],
    "temporal_tags": ["2025", "Q3"],
    "geographic_tags": ["chile", "santiago"]
  },

  "cross_references": [
    {
      "target_document": "ddp:otro_dominio:otro_doc:fecha",
      "relationship_type": "SAME_ENTITY",
      "confidence": 0.95,
      "context": "Descripción de la relación"
    }
  ]
}
```

**TAREA ESPECÍFICA**:
1. **Mapea las entidades extraídas** de tu documento a las categorías universales
2. **Adapta los datos específicos** de tu dominio al campo "domain_specific"
3. **Normaliza los metadatos** según el esquema universal
4. **Conserva la información original** pero en formato estándar

Crea el archivo universal_schema.json con la transformación completa.
```

💡 **Ventajas de Claude Code para Transformación Universal**:
- **Entiende esquemas complejos**: Puede mapear datos específicos a formato universal
- **Adaptación automática**: Se ajusta a la estructura específica de tu documento
- **Preserva información**: No pierde datos importantes en la transformación
- **Validación**: Verifica que la transformación sea correcta
- **Iterativo**: Puedes refinar la transformación hasta que sea perfecta

⚠️ **Por qué es crítico**: Cada tipo de documento (financiero, legal, técnico) tiene estructura diferente, pero necesita transformarse al mismo esquema universal para que la plataforma AI pueda consultarlo consistentemente.

---

## 🗄️ **FASE 6: INGESTA Y ACCESO AI** (15-30 minutos)

### Paso 6.1: Ingesta a Base de Datos 📊

```bash
make setup-db  # Si es primera vez
python shared_platform/database_tools/ingest_data.py \
  --input "domains/{tu_dominio}/chapters/{documento_tipo}/outputs/universal_json/" \
  --update-schema-if-needed \
  --validate-integrity
```
💡 **Nota**: Claude Code puede ejecutar estos comandos y manejar toda la ingesta a la base de datos.

### Paso 6.2: Activación de Acceso AI 🤖

```bash
make run-mcp  # Servidor principal

# Servidor específico del dominio (si existe)
cd ai_platform/mcp_servers/
python {tu_dominio}_server.py  # ej: operaciones_server.py
```
💡 **Nota**: Claude Code puede activar los servidores MCP y ya tienes acceso directo a los datos.

### Paso 6.3: Verificación Final ✅

```bash
python shared_platform/cli/test_ai_queries.py \
  --domain "{tu_dominio}" \
  --document-type "{documento_tipo}" \
  --sample-queries "prompts/testing/sample_queries.md"
```
💡 **Nota**: Con Claude Code ya puedes hacer consultas directamente sin scripts adicionales.

**Consultas de prueba típicas**:
```markdown
# Consultas básicas para verificar funcionamiento
"¿Cuántas entidades se extrajeron de este documento?"
"Lista las 5 organizaciones principales mencionadas"
"¿Qué referencias cruzadas se encontraron?"
"Muestra un resumen de los tags semánticos"
```

---

## 📋 **RESUMEN METODOLÓGICO**

### ✅ **Checklist Completo para Nuevo Documento**

```bash
# 1. OBTENCIÓN (15-30 min)
[ ] Documento descargado/copiado
[ ] Estructura de carpetas creada
[ ] Dominio y tipo definidos

# 2. ANÁLISIS ESTRUCTURAL (30-60 min)
[ ] Análisis automático ejecutado (Prompt #1)
[ ] División de capítulos completada
[ ] Estructura validada manualmente

# 3. EXTRACCIÓN ADAPTATIVA (45-90 min)
[ ] Extractor específico generado (Prompt #2)
[ ] Extractor calibrado (>85% confianza)
[ ] Metadatos generados (Prompt #3)

# 4. VALIDACIÓN MANUAL (30-60 min)
[ ] Extracciones revisadas interactivamente
[ ] Control de calidad aprobado
[ ] Referencias cruzadas generadas (Prompt #4)

# 5. TRANSFORMACIÓN UNIVERSAL (15-30 min)
[ ] Esquema universal aplicado
[ ] JSON válido generado
[ ] Metadatos completos

# 6. INGESTA Y ACCESO AI (15-30 min)
[ ] Datos ingresados a base de datos
[ ] Servidores MCP activados
[ ] Consultas AI funcionando
```

### 🎯 **Tiempo Total Estimado por Complejidad**

| Tipo de Documento | Tiempo Total | Iteraciones | Dificultad |
|-------------------|--------------|-------------|------------|
| **Simple** (1-20 páginas, estructura clara) | 2-3 horas | 3-5 | ⭐⭐ |
| **Medio** (20-100 páginas, múltiples secciones) | 3-4 horas | 5-8 | ⭐⭐⭐ |
| **Complejo** (100+ páginas, estructura irregular) | 4-6 horas | 8-12 | ⭐⭐⭐⭐ |

### 🛠️ **Herramientas Disponibles**

**🤖 Herramienta Principal: Claude Code**
- Puede realizar todas las fases de la metodología
- Acceso directo a PDFs, base de datos y archivos
- Conversación natural para iteración y mejora
- Generación de código específico por documento

**⚙️ Herramientas Automáticas (Opcionales)**:
```
ai_platform/
├── analyzers/document_structure_analyzer.py     # Análisis automático
├── processors/adaptive_document_processor.py   # Extracción adaptativa
├── processors/metadata_generator.py            # Generación de metadatos
└── processors/cross_reference_generator.py     # Referencias cruzadas

shared_platform/
├── cli/validation_interface.py                 # Validación interactiva
├── cli/quality_checker.py                      # Control de calidad
├── transformers/universal_schema_transformer.py # Transformación universal
└── database_tools/ingest_data.py              # Ingesta a base de datos
```

### 💡 **Metodología con Claude Code**

**🎯 Enfoque Principal: Usar Claude Code para todo el procesamiento**

La metodología está diseñada para trabajar principalmente con **Claude Code**:

- **📄 Lectura directa de PDFs**: Claude Code puede leer documentos directamente
- **🤖 Análisis inteligente**: Análisis de estructura con conversación natural
- **💻 Generación de código**: Creación de extractores Python personalizados
- **🔍 Validación interactiva**: Revisión manual con Claude Code
- **🔗 Referencias cruzadas**: Acceso a base de datos para correlaciones
- **📊 Transformación**: Conversión a esquemas universales

### 📝 **Prompts de Ejemplo Incluidos**

Los prompts mostrados en cada fase son **ejemplos de conversación con Claude Code**:

- **FASE 2**: Análisis de estructura de documentos
- **FASE 3**: Generación de extractores y metadatos
- **FASE 4**: Detección de referencias cruzadas

⚠️ **Importante sobre la Metodología**:
- **Claude Code es la herramienta principal** para todo el procesamiento
- Los scripts automáticos son **opcionales** (Opción A en cada fase)
- **Los prompts son ejemplos** de cómo hablar con Claude Code
- **Personaliza la conversación** según tu documento específico
- **Claude Code puede iterar** contigo hasta lograr resultados perfectos

---

## 🎯 **Casos de Uso Validados**

### 📈 **Documentos Financieros**
- **Estados de resultados, balances, flujos de caja**
- **Tiempo promedio**: 2.5-3.5 horas
- **Entidades típicas**: Métricas financieras, ratios, comparativos

### 📋 **Documentos Legales**
- **Contratos, acuerdos, políticas corporativas**
- **Tiempo promedio**: 3-4 horas
- **Entidades típicas**: Partes, obligaciones, fechas críticas

### 🔧 **Documentos Técnicos**
- **Manuales, especificaciones, procedimientos**
- **Tiempo promedio**: 3.5-4.5 horas
- **Entidades típicas**: Especificaciones, equipos, normas

### ⚡ **Documentos Operacionales**
- **Reportes de operaciones, KPIs, análisis de rendimiento**
- **Tiempo promedio**: 2.5-3.5 horas
- **Entidades típicas**: Métricas, procesos, incidentes

---

**🌑 Dark Data Platform - Metodología Universal**

> **"De cualquier PDF a inteligencia AI-queryable en 2-6 horas"**

> **Última actualización**: 26 Sep 2025 | **Versión**: 2.0 | **Validado con**: 15+ tipos de documentos diferentes