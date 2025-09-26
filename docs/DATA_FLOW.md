# 📊 Data Flow - Proceso Universal End-to-End

## 🎯 Visión General del Proceso

Este documento describe el proceso completo y genérico que debe seguir una persona para extraer, procesar y obtener información inteligente de **cualquier tipo de documento**, con o sin capítulos.

```
📄 Documentos → 🔍 Análisis IA → 🤖 Extracción + Prompts → ✋ Validación → 💾 Base de Datos → 🔍 Consultas IA
```

---

## 🚀 **FASE 1: OBTENCIÓN DE DOCUMENTOS** (15-45 minutos)

### Paso 1.1: Adquisición de Documentos 📁

**Fuentes posibles**:
- 🌐 **Web scraping automático**: Para sitios web con documentos regulares
- 📧 **Email/descargas manuales**: Para documentos recibidos por email
- 💾 **Archivos locales**: Para documentos ya disponibles localmente
- 🗂️ **Sistemas corporativos**: Para documentos de sistemas internos

```bash
# Opción A: Web scraping (si disponible)
cd domains/[dominio]/shared/scrapers/[fuente]
python scraper_automatico.py

# Opción B: Colocación manual
mkdir -p domains/[dominio]/data/source_documents
# Copiar documentos manualmente a esta carpeta
```

### Paso 1.2: Organización de Documentos (5-10 minutos) 📂

**Tarea humana**: Clasificar y organizar documentos por tipo

```bash
# Verificar documentos obtenidos
ls -la domains/[dominio]/data/source_documents/

# Organizar por tipo si es necesario
mkdir -p domains/[dominio]/data/source_documents/reportes_financieros
mkdir -p domains/[dominio]/data/source_documents/documentos_legales
mkdir -p domains/[dominio]/data/source_documents/manuales_tecnicos

# Renombrar para consistencia
mv "Reporte Q3 2025.pdf" "reporte_financiero_2025_Q3.pdf"
```

---

## 🤖 **FASE 2: ANÁLISIS Y PROCESAMIENTO CON IA** (2-8 horas de desarrollo iterativo)

### Paso 2.1: Análisis Inicial Automático 🔍

**⚠️ Prompt como Herramienta de Apoyo**: El prompt es una **guía para desarrollo**, no una solución automática

**Prompt Estratégico #1 - Herramienta de Apoyo para Análisis**
```markdown
# PROMPT GUÍA - USAR PARA GENERAR CÓDIGO INICIAL
# REQUIERE ITERACIÓN Y PERSONALIZACIÓN ESPECÍFICA

Analiza este documento y genera código Python que determine:

1. **Tipo de documento**: Reporte, manual, contrato, análisis, etc.
2. **Estructura**: ¿Tiene capítulos/secciones? ¿Es documento único?
3. **Contenido principal**: Tipos de datos, tablas, información clave
4. **Entidades**: Personas, empresas, ubicaciones, fechas importantes
5. **Organización**: ¿Cómo está organizada la información?

**Si tiene capítulos/secciones**:
- Genera código para detectar divisiones automáticamente
- Identifica patrones específicos de títulos/secciones

**Si es documento unitario**:
- Genera código para análisis de contenido secuencial
- Detecta patrones de datos repetitivos específicos

Genera código Python con clases específicas, no solo JSON de respuesta.
```

**Desarrollo Real Requerido** (2-4 horas de iteración):
```bash
# 1. Usar prompt para generar código base
# 2. ITERAR 3-5 veces personalizando para documento específico

# Archivos a generar/calibrar:
cd domains/{dominio}/chapters/{documento}/processors/

# A) document_analyzer.py (OBLIGATORIO)
python generate_analyzer.py --prompt-file "prompts/analysis/universal_document_analysis.md"
# → Personalizar para detectar estructura específica del documento
# → Iterar hasta 85%+ precisión en detección

# B) chapter_divider.py (SI APLICA - si tiene capítulos)
python generate_divider.py --based-on analyzer_results.json
# → Desarrollar divisor específico para patrones encontrados
# → Calibrar títulos/secciones específicas del documento

# C) content_classifier.py (OBLIGATORIO)
python generate_classifier.py --document-type detected_type
# → Clasificador específico para tipo de contenido encontrado
# → Personalizar para estructura específica
```

**Resultado Esperado tras Iteración**:
```
domains/{dominio}/chapters/{documento}/processors/
├── document_analyzer.py          # ✅ Analiza estructura específica
├── chapter_divider.py            # ✅ Si aplica: divide capítulos automáticamente
├── content_classifier.py         # ✅ Clasifica contenido específico
└── patterns/
    ├── title_patterns.json       # ✅ Patrones de títulos calibrados
    ├── structure_rules.json      # ✅ Reglas de estructura específicas
    └── content_types.json        # ✅ Tipos de contenido identificados
```

### Paso 2.2: Extracción Adaptativa de Datos 📊

**⚠️ Prompt como Herramienta de Apoyo**: Requiere 8-20 horas de desarrollo específico e iterativo

**Prompt Estratégico #2 - Herramienta para Generar Extractores**
```markdown
# PROMPT GUÍA - GENERAR CÓDIGO DE EXTRACCIÓN ESPECÍFICO
# REQUIERE 8-15 ITERACIONES DE PERSONALIZACIÓN

Genera código Python de extracción específica para este documento:

**Contexto**: [Usar resultado de análisis previo]
**Objetivo**: Crear clase extractor específica, no extracción genérica

**Generar código Python que**:
1. **Extraiga entidades específicas del tipo de documento**
2. **Valide rangos específicos** (ej: fechas válidas, montos realistas)
3. **Normalice entidades** (ej: nombres de empresas consistentes)
4. **Maneje casos específicos** del tipo de documento

**Para documentos con capítulos**: Generar método de procesamiento por secciones
**Para documentos unitarios**: Generar método de procesamiento secuencial
**Incluir**: Validaciones específicas del dominio y tipo de documento
```

**Desarrollo Real Requerido** (8-20 horas de iteración intensiva):
```bash
cd domains/{dominio}/chapters/{documento}/processors/

# A) Extractor principal (8-20 horas de iteración)
python generate_extractor.py --prompt-file "prompts/extraction/generic_document_extraction.md"
# → Personalizar ESPECÍFICAMENTE para el documento
# → Iterar 8-15 veces hasta lograr 85-95%+ confianza

# B) content_extractor.py (OBLIGATORIO - desarrollo específico)
# → Extraer contenido específico del tipo de documento
# → Personalizar validaciones de rangos y formatos
# → NO automatizable con prompts

# C) section_processor.py (SI APLICA - para documentos con capítulos)
# → Procesamiento específico por tipo de sección encontrada
# → Requiere lógica específica por cada tipo de capítulo

# D) entity_extractor.py (OBLIGATORIO - altamente específico)
# → Extraer entidades específicas del dominio
# → Diccionarios de normalización específicos
# → Validaciones de coherencia específicas del documento
```

**Proceso Iterativo Típico**:
```bash
# Ciclo de desarrollo (repetir 8-15 veces):
for iteration in {1..15}; do
    echo "Iteración $iteration:"

    # 1. Probar extractor actual
    python {documento}_processor.py --test-sample sample_$iteration.pdf

    # 2. Revisar manualmente resultados
    python review_results.py --interactive

    # 3. Identificar fallos específicos
    # 4. Refinar código específico (NO prompt)
    # 5. Calibrar validaciones específicas

    # 6. Validar confianza
    confidence=$(python measure_confidence.py --results last_extraction.json)
    echo "Confianza actual: $confidence"

    if [ "$confidence" -gt "0.85" ]; then
        echo "✅ Extractor calibrado exitosamente"
        break
    fi
done
```

**Resultado Esperado tras Iteración Intensiva**:
```
domains/{dominio}/chapters/{documento}/processors/
├── {documento}_processor.py      # ✅ Procesador principal calibrado 85-95%+
├── content_extractor.py          # ✅ Extractor de contenido específico
├── section_processor.py          # ✅ Si aplica: procesador por secciones
├── entity_extractor.py           # ✅ Extractor de entidades específicas
├── validation_rules.py           # ✅ Reglas de validación específicas
└── patterns/
    ├── entity_patterns.json      # ✅ Patrones de entidades calibrados
    ├── data_validation.json      # ✅ Rangos válidos específicos
    └── extraction_rules.json     # ✅ Reglas de extracción específicas
```

### Paso 2.3: Generación Automática de Metadatos 🏷️

**⚠️ Prompt como Herramienta de Apoyo**: Requiere 4-8 horas de desarrollo y calibración específica

**Prompt Estratégico #3 - Herramienta para Metadatos Específicos**
```markdown
# PROMPT GUÍA - GENERAR CÓDIGO DE METADATOS ESPECÍFICOS
# REQUIERE PERSONALIZACIÓN PARA DOMINIO/INDUSTRIA ESPECÍFICA

Genera código Python para metadatos específicos de este documento:

**Generar código Python que**:
1. **Tags semánticos específicos**: Del dominio/industria específica
2. **Clasificación automática**: Basada en contenido específico detectado
3. **Entidades normalizadas**: Con diccionarios específicos del dominio
4. **Cross-referencias**: Reglas específicas entre tipos de documentos

**Específico por dominio**:
- **Financiero**: Tags de métricas, periodos fiscales, ratios específicos
- **Legal**: Tags de tipos de contrato, obligaciones, jurisdicciones
- **Técnico**: Tags de especificaciones, normas, procedimientos
- **Operacional**: Tags de KPIs, procesos, métricas de rendimiento
```

**Desarrollo Real Requerido** (4-8 horas de calibración específica):
```bash
cd domains/{dominio}/chapters/{documento}/processors/

# A) metadata_generator.py (OBLIGATORIO - específico por dominio)
python generate_metadata_code.py --prompt-file "prompts/metadata/universal_metadata_generation.md"
# → Personalizar tags específicos del dominio/industria
# → Calibrar diccionarios de normalización específicos
# → NO automatizable completamente con prompts

# B) tag_classifier.py (DESARROLLO ESPECÍFICO)
# → Clasificador de tags específicos para el tipo de documento
# → Requiere conocimiento del dominio específico
# → Diccionarios de sinónimos específicos

# C) entity_normalizer.py (ALTAMENTE ESPECÍFICO)
# → Normalizador de nombres de empresas/organizaciones
# → Específico por país/región/industria
# → Requiere bases de datos específicas del dominio

# D) cross_reference_generator.py (LÓGICA ESPECÍFICA)
# → Generador de referencias cruzadas específicas
# → Reglas específicas entre tipos de documentos del dominio
# → NO generalizable con prompts únicamente
```

**Calibración Específica Requerida**:
```python
# Ejemplo de desarrollo específico NO automatizable
class DomainSpecificMetadataGenerator:
    def __init__(self, domain_type):
        # Diccionarios específicos del dominio
        if domain_type == "financial_chile":
            self.company_normalizer = {
                "Banco de Chile": ["BancoChile", "BCH", "Banco Chile S.A."],
                "Banco Santander": ["Santander", "BSA", "Santander Chile"]
            }
            self.tag_patterns = {
                "ratios_financieros": ["ROI", "ROE", "EBITDA", "margen"],
                "periodos": ["trimestre", "Q1", "Q2", "Q3", "Q4", "anual"]
            }
        elif domain_type == "legal_spain":
            self.legal_terms = {
                "contratos": ["arrendamiento", "servicios", "compraventa"],
                "jurisdicciones": ["madrid", "barcelona", "valencia"]
            }
        # ... desarrollo específico por dominio
```

**Resultado Esperado tras Calibración**:
```
domains/{dominio}/chapters/{documento}/processors/
├── metadata_generator.py         # ✅ Generador específico calibrado
├── tag_classifier.py             # ✅ Clasificador específico del dominio
├── entity_normalizer.py          # ✅ Normalizador específico región/industria
├── cross_reference_generator.py  # ✅ Generador referencias específicas
└── metadata_config/
    ├── domain_tags.json          # ✅ Tags específicos del dominio
    ├── normalization_dict.json   # ✅ Diccionario normalización específico
    ├── entity_aliases.json       # ✅ Aliases específicos región/industria
    └── cross_ref_rules.json      # ✅ Reglas referencias específicas
```
3. **Clasificación geográfica**: países, regiones, ciudades mencionadas
4. **Clasificación temporal**: fechas, períodos, rangos temporales
5. **Clasificación funcional**: tipo de documento, propósito, audiencia

**Entidades universales a identificar**:
- **Personas**: Nombres de individuos mencionados
- **Organizaciones**: Empresas, instituciones, entidades gubernamentales
- **Ubicaciones**: Direcciones, ciudades, regiones, países
- **Fechas**: Fechas específicas, períodos, plazos
- **Conceptos clave**: Términos técnicos, métricas importantes

**Clasificación automática por industria/dominio**:
- Si es financiero: balance, ingresos, gastos, activos
- Si es legal: contratos, clausulas, obligaciones, derechos
- Si es técnico: especificaciones, procedimientos, equipos
- Si es operacional: procesos, resultados, métricas

**Cross-referencias potenciales**:
- Mismas entidades en otros documentos
- Mismo período temporal
- Mismas organizaciones involucradas
```

**Ejecutar**:
```bash
python ai_platform/processors/metadata_generator.py \
  --input "extracted_data.json" \
  --prompt-file "prompts/metadata/universal_metadata_generation.md"
```

---

## ✋ **FASE 3: VALIDACIÓN Y ENRIQUECIMIENTO MANUAL** (30-60 minutos)

### Paso 3.1: Revisión Interactiva de Extracciones 🔎

**Herramienta de validación humana**:
```bash
python shared_platform/cli/validation_interface.py --chapter "anexo_02" --interactive
```

**Proceso de validación**:
1. **Revisar cada extracción**: ✅ Aprobar o ❌ Rechazar
2. **Verificar nombres**: ¿"Planta Solar Atacama" es correcto?
3. **Validar capacidades**: ¿100 MW es realista para esta planta?
4. **Confirmar ubicaciones**: ¿Las coordenadas corresponden?

**Ejemplo de interfaz interactiva**:
```
🔍 Extracción #47 - Planta Solar Quilapilún
├── Empresa: Enel Chile S.A.
├── Capacidad: 110 MW
├── Tecnología: Solar Fotovoltaica
├── Ubicación: Región Metropolitana
├── Confianza IA: 0.89

¿Aprobar esta extracción? [y/n/edit]:
```

### Paso 3.2: Enriquecimiento Manual de Datos 📝

**Agregar información adicional**:
```bash
# Editor interactivo para agregar datos
python shared_platform/cli/data_enrichment.py --entity "planta_solar_quilapilun"
```

**Información que puedes agregar manualmente**:
- **Context business**: Importancia estratégica de la planta
- **Observaciones técnicas**: Particularidades operacionales
- **Links externos**: Sitio web de la empresa, noticias relevantes
- **Tags personalizados**: Etiquetas específicas de tu análisis
- **Notas de calidad**: Comentarios sobre la confiabilidad de los datos

**Ejemplo de enriquecimiento**:
```json
{
  "manual_annotations": {
    "business_priority": "high",
    "strategic_notes": "Planta clave para suministro RM",
    "data_quality": "validated_2025_09_25",
    "custom_tags": ["nueva_tecnologia", "alto_rendimiento"],
    "external_links": ["https://enel.cl/proyectos/quilapilun"],
    "analyst_notes": "Rendimiento 15% superior al promedio regional"
  }
}
```

### Paso 3.3: Validación de Cross-Referencias 🔗

**Prompt Estratégico #4 - Cross-Referencias**
```markdown
# PROMPT PARA CROSS-REFERENCIAS AUTOMÁTICAS
Genera cross-referencias inteligentes para esta planta solar:

**Reglas de referencia**:
1. **Temporal**: Misma planta en reportes de diferentes meses
2. **Empresarial**: Otras plantas de la misma empresa
3. **Geográfica**: Plantas en la misma región
4. **Técnica**: Plantas con similar capacidad y tecnología
5. **Operacional**: Plantas que operan en el mismo horario solar

**Tipos de relación**:
- MISMA_ENTIDAD: Misma planta en otro documento
- MISMA_EMPRESA: Otra planta de la misma empresa
- PROXIMIDAD_GEOGRAFICA: Plantas cercanas geográficamente
- COMPLEMENTARIEDAD_TECNICA: Plantas que se complementan operacionalmente

**Nivel de confianza**: 0-1 para cada referencia sugerida
```

---

## 💾 **FASE 4: CONSOLIDACIÓN Y ALMACENAMIENTO** (15-30 minutos)

### Paso 4.1: Generación de JSON Universal 📄

**Aplicar esquema universal chileno**:
```bash
python domains/operaciones/shared/utilities/extractor_universal_integrado.py --input "validated_extractions/" --output "universal_format/"
```

**Resultado - Esquema JSON-LD Universal**:
```json
{
  "@context": "https://coordinador.cl/context/v1",
  "@id": "cen:operaciones:anexo_02:2025-09-25",
  "@type": "DocumentoSistemaElectricoChile",

  "metadatos_universales": {
    "titulo": "ANEXO 2 - Generación Real",
    "dominio": "operaciones",
    "regulador": "Coordinador Eléctrico Nacional",
    "sistema_electrico": "SEN"
  },

  "entidades": {
    "centrales_electricas": [
      {
        "@id": "cen:central:planta_solar_quilapilun",
        "@type": "CentralSolarChile",
        "nombre": "Planta Solar Quilapilún",
        "empresa": "Enel Chile S.A.",
        "capacidad_mw": 110,
        "confianza": 0.92
      }
    ]
  },

  "referencias_cruzadas": [
    {
      "documento_objetivo": "cen:operaciones:anexo_01:2025-09-25",
      "tipo_relacion": "MISMA_CENTRAL_PROGRAMACION",
      "confianza": 0.95,
      "contexto": "Misma planta en programación operacional"
    }
  ],

  "datos_especificos_dominio": {
    "operaciones": {
      // Datos originales extraídos preservados
    }
  }
}
```

### Paso 4.2: Ingesta a Base de Datos 🗄️

```bash
# Crear/actualizar base de datos
make setup-db

# Ingestar datos procesados
make ingest-data

# Verificar ingesta exitosa
python shared_platform/database_tools/verify_ingestion.py --stats
```

**Resultado esperado**:
```
✅ Base de datos actualizada:
├── [N] entidades principales ingresadas
├── [M] cross-referencias generadas automáticamente
├── [X] organizaciones identificadas y normalizadas
└── 100% datos con validación humana
```

---

## 🔍 **FASE 5: ACCESO Y CONSULTAS IA** (Tiempo real)

### Paso 5.1: Activar Servidores MCP 🤖

```bash
# Servidor principal
make run-mcp

# Servidores especializados por dominio
cd ai_platform/mcp_servers
python operaciones_server.py      # Análisis operacional
python mercados_server.py         # Análisis de mercados/business
python legal_server.py            # Análisis legal/compliance
python cross_domain_server.py     # Análisis cross-domain
```

### Paso 5.2: Consultas IA Inteligentes 💡

**Ejemplos de consultas universales por tipo de documento**:

```markdown
# Consultas sobre documentos financieros
"¿Cuáles son las 10 empresas con mayor crecimiento de ingresos y cómo se comparan con sus presupuestos?"

# Consultas sobre documentos legales/contractuales
"Muestra todos los contratos que vencen en los próximos 6 meses y sus obligaciones pendientes"

# Consultas sobre documentos operacionales
"¿Qué procesos tienen mayor desviación respecto a KPIs establecidos y cuáles son las causas identificadas?"

# Consultas cross-domain (múltiples tipos)
"Correlaciona el rendimiento financiero con los indicadores operacionales durante el último trimestre"
```

### Paso 5.3: Dashboard Web Interactivo 📊

```bash
make run-web
# → http://localhost:5000
```

**Funcionalidades del dashboard**:
- **Vista de entidades**: Visualización interactiva de todas las entidades extraídas
- **Análisis temporal**: Gráficos de tendencias y evolución de datos en el tiempo
- **Comparativas**: Entre organizaciones, regiones, métricas, períodos
- **Búsqueda**: Por nombre, entidad, métricas, ubicación, fechas
- **Exportación**: CSV, JSON, reportes PDF personalizables

---

## 🎯 **PROMPTS ESTRATÉGICOS - Herramientas de Desarrollo IA**

### ⚠️ **IMPORTANTE: Los Prompts son Herramientas de Apoyo**

Los prompts **NO** son soluciones automáticas. Son **plantillas de instrucciones** para:
- **Guiar el desarrollo** de código específico para cada documento
- **Acelerar la iteración** de procesadores personalizados
- **Estandarizar el enfoque** de extracción y validación

**Proceso real de desarrollo**:
1. **Usar prompt como guía** → Generar código inicial con IA
2. **Iterar y personalizar** → Adaptar código al documento específico
3. **Validar y calibrar** → Lograr 85-95%+ confianza en extracciones
4. **Generar componentes** → Crear divisores, validadores, normalizadores

### 📁 Estructura Completa de Componentes por Fase

```
domains/{dominio}/chapters/{documento}/
├── processors/
│   ├── {documento}_processor.py              # Procesador principal
│   ├── chapter_divider.py                    # Si aplica: División automática de capítulos
│   ├── content_extractor.py                 # Extractor de contenido específico
│   ├── data_validator.py                    # Validador de datos extraídos
│   ├── entity_normalizer.py                 # Normalizador de entidades
│   └── quality_checker.py                   # Control de calidad específico
├── patterns/
│   ├── title_patterns.json                  # Patrones de títulos/secciones
│   ├── entity_patterns.json                 # Patrones de entidades específicas
│   └── validation_rules.json                # Reglas de validación específicas
└── data/
    ├── extractions/                          # Resultados finales validados
    ├── samples/                              # Muestras para desarrollo
    └── validation_logs/                      # Logs de control de calidad
```

### 🔧 **Uso de Prompts por Etapa de Desarrollo**

#### **ETAPA 1: Análisis Inicial (Prompt: analysis/universal_document_analysis.md)**
```bash
# Usar prompt para generar analizador inicial
python ai_platform/analyzers/document_structure_analyzer.py \
  --prompt-file "prompts/analysis/universal_document_analysis.md" \
  --document "sample_document.pdf"

# Resultado: Código base para chapter_divider.py (si aplica)
# Iteración manual: Personalizar patrones de detección específicos
```

#### **ETAPA 2: Extracción Específica (Prompt: extraction/generic_document_extraction.md)**
```bash
# Usar prompt como base para generar extractor
# IMPORTANTE: El código generado requiere 5-10 iteraciones mínimo

# Desarrollo iterativo típico:
for iteration in range(10):
    # 1. Generar código con IA usando prompt
    # 2. Probar en documentos reales
    # 3. Identificar fallos específicos
    # 4. Refinar prompt y regenerar código
    # 5. Validar manualmente hasta lograr 85-95%+ confianza

# Resultado final: {documento}_processor.py calibrado específicamente
```

#### **ETAPA 3: Componentes de Validación (Iteración manual intensiva)**
```python
# data_validator.py - Desarrollado específicamente por documento
class DocumentSpecificValidator:
    def __init__(self):
        # Rangos específicos del tipo de documento
        self.valid_ranges = {
            "financial": {"revenue": (0, 1e12), "margin": (0, 1)},
            "legal": {"contract_duration_months": (1, 240)},
            "technical": {"temperature_celsius": (-50, 200)}
        }

    def validate_extraction(self, data):
        # Validaciones específicas que requieren conocimiento del dominio
        # NO generables automáticamente con prompts
        pass

# quality_checker.py - Control de calidad específico
class QualityController:
    def check_completeness(self, extracted_data, source_document):
        # Verificaciones específicas del documento
        # Requiere calibración manual iterativa
        pass
```

#### **ETAPA 4: Normalización de Entidades (Específico por dominio)**
```python
# entity_normalizer.py - Altamente específico
class EntityNormalizer:
    def __init__(self):
        # Diccionarios específicos del dominio/región
        self.company_aliases = {
            "financial_chile": {"Banco de Chile": ["BancoChile", "BCH", "Banco Chile"]},
            "energy_spain": {"Iberdrola S.A.": ["Iberdrola", "IBE", "Iberdrola España"]}
        }

    def normalize_companies(self, raw_entities):
        # Lógica específica que requiere conocimiento del dominio
        # NO automatizable con prompts genéricos
        pass
```

### 📋 **Prompts Disponibles (Herramientas de Apoyo)**

```
prompts/
├── analysis/
│   └── universal_document_analysis.md          # Guía para analyzers/
├── extraction/
│   └── generic_document_extraction.md          # Base para processors/
├── metadata/
│   ├── universal_metadata_generation.md        # Apoyo para metadatos
│   └── cross_reference_generation.md          # Guía para referencias
├── validation/
│   ├── quality_check.md                        # Base para quality_checker.py
│   └── consistency_validation.md               # Base para data_validator.py
└── README.md                                   # Manual completo de iteración
```

### ⏱️ **Tiempo Real de Desarrollo por Componente**

| Componente | Prompt Base | Iteraciones | Tiempo Total |
|------------|-------------|-------------|--------------|
| `document_analyzer.py` | `analysis/universal_*` | 3-5 | 2-4 horas |
| `chapter_divider.py` | Manual | 5-8 | 4-8 horas |
| `{doc}_processor.py` | `extraction/generic_*` | 8-15 | 8-20 horas |
| `data_validator.py` | `validation/quality_*` | 5-10 | 6-12 horas |
| `entity_normalizer.py` | Manual | 10-20 | 10-25 horas |
| `quality_checker.py` | `validation/consistency_*` | 8-12 | 8-15 horas |

### ✅ **Proceso de Calibración hasta 85-95%+ Confianza**

```bash
# Flujo iterativo típico para un nuevo tipo de documento
cd domains/{dominio}/chapters/{documento}/processors

# 1. Análisis inicial (2-4 horas)
python document_analyzer.py --samples ../data/samples/ --iterations 5

# 2. División de capítulos si aplica (4-8 horas)
python chapter_divider.py --calibrate --manual-validation

# 3. Extracción específica (8-20 horas de iteración)
for i in {1..15}; do
    python {documento}_processor.py --test-sample $i
    # Revisar manualmente, identificar problemas
    # Refinar código, repetir hasta 85-95%+ confianza
done

# 4. Validación robusta (6-12 horas)
python data_validator.py --strict-mode --manual-review

# 5. Normalización (10-25 horas - más intensivo)
python entity_normalizer.py --build-dictionary --validate-all

# 6. Control de calidad final (8-15 horas)
python quality_checker.py --full-validation --confidence-threshold 0.85
```

---

## ⚡ **Proceso Rápido - Resumen Ejecutivo Universal**

### **Para CUALQUIER documento nuevo (Primera vez - 2-3 horas)**:
```bash
# 1. Obtener/organizar documentos (15-30 min)
mkdir -p domains/[dominio]/data/source_documents
# Colocar documentos en carpeta

# 2. Análisis automático (15-30 min)
python ai_platform/analyzers/document_structure_analyzer.py \
  --pdf "path/to/document.pdf" \
  --prompt-file "prompts/analysis/universal_document_analysis.md"

# 3. Extracción adaptativa (45-90 min)
python ai_platform/processors/adaptive_document_processor.py \
  --document "path/to/document.pdf" \
  --analysis "analysis_result.json" \
  --prompt-file "prompts/extraction/generic_document_extraction.md"

# 4. Generación de metadatos (15-30 min)
python ai_platform/processors/metadata_generator.py \
  --input "extracted_data.json" \
  --prompt-file "prompts/metadata/universal_metadata_generation.md"

# 5. Validación interactiva (30-60 min)
python shared_platform/cli/universal_validation_interface.py --interactive

# 6. Consolidación final (15 min)
make ingest-data

# 7. Acceso IA inmediato
make run-mcp
```

### **Para documentos del mismo tipo (Proceso establecido - 30-45 minutos)**:
```bash
# Reutilizar procesadores calibrados
python ai_platform/processors/adaptive_document_processor.py \
  --document "path/to/new/document.pdf" \
  --reuse-profile "previous_document_profile.json" \
  --auto-validate
```

### **Ejemplos por Tipo de Documento**

#### **📈 Documento Financiero (ej: Estado de Resultados)**
```bash
# Tiempo estimado: 60-90 minutos
python ai_platform/processors/adaptive_document_processor.py \
  --document "estado_resultados_q3_2025.pdf" \
  --domain-hint "financiero" \
  --extract-focus "métricas_financieras,comparativos_temporales"
```

**Resultado esperado**: Ingresos, gastos, ratios financieros, comparativos año anterior

#### **📋 Contrato Legal (ej: Contrato de Servicios)**
```bash
# Tiempo estimado: 45-75 minutos
python ai_platform/processors/adaptive_document_processor.py \
  --document "contrato_servicios_2025.pdf" \
  --domain-hint "legal" \
  --extract-focus "partes_contrato,obligaciones,fechas_criticas"
```

**Resultado esperado**: Partes involucradas, obligaciones, plazos, condiciones

#### **🔧 Manual Técnico (ej: Manual de Operación)**
```bash
# Tiempo estimado: 75-120 minutos
python ai_platform/processors/adaptive_document_processor.py \
  --document "manual_operacion_equipo.pdf" \
  --domain-hint "técnico" \
  --extract-focus "procedimientos,especificaciones,requisitos_seguridad"
```

**Resultado esperado**: Procedimientos paso a paso, especificaciones técnicas, normas

---

## 🏆 **Beneficios del Proceso Universal**

### ✅ **Adaptabilidad Total**
- **Funciona con CUALQUIER tipo de documento**: Financieros, legales, técnicos, operacionales
- **Auto-detección de estructura**: Con capítulos o documentos unitarios
- **Procesadores adaptativos**: Se ajustan automáticamente al contenido

### ✅ **Automatización Inteligente**
- **85-90%+ automatizado** con validación humana estratégica
- **Prompts universales** que se adaptan al contenido detectado
- **Reutilización automática** de perfiles para documentos similares

### ✅ **Calidad y Consistencia**
- **Validación interactiva** en puntos críticos identificados automáticamente
- **Cross-referencias universales** entre cualquier tipo de documento
- **Metadatos estructurados** para búsqueda y análisis avanzado

### ✅ **Escalabilidad Enterprise**
- **Documentos nuevos del mismo tipo**: 30-45 minutos (reutilización automática)
- **Tipos completamente nuevos**: 2-3 horas (primera vez, luego reutilizable)
- **Consultas IA cross-domain**: Tiempo real sobre todos los tipos de datos

### ✅ **Valor Business Universal**
- **ROI inmediato**: De documento a insights business en 2-3 horas máximo
- **Análisis correlacional**: Entre documentos de diferentes dominios
- **Decisiones data-driven**: Basadas en información estructurada y cross-referenciada
- **Knowledge building**: Construcción automática de base de conocimiento empresarial

### ✅ **Casos de Uso Empresariales**

#### **Due Diligence Automatizado**
```markdown
Escenario: Adquisición empresarial
Documentos: Estados financieros + contratos + auditorías + documentos legales
Resultado: Análisis integral automático con red de cross-referencias
Tiempo: 8-12 horas vs 2-3 semanas manual
```

#### **Compliance Automático**
```markdown
Escenario: Auditoría regulatoria
Documentos: Políticas + procedimientos + reportes + contratos
Resultado: Verificación automática de cumplimiento normativo
Tiempo: 4-6 horas vs 1-2 semanas manual
```

#### **Research & Analysis**
```markdown
Escenario: Investigación de mercado
Documentos: Estudios + reportes + análisis + documentos públicos
Resultado: Síntesis inteligente con insights cross-document
Tiempo: 6-8 horas vs 3-4 semanas manual
```

---

## 📚 **Documentación Relacionada**

- [`DATA_FLOW_EXAMPLE.md`](DATA_FLOW_EXAMPLE.md) - Ejemplo práctico paso a paso
- [`prompts/README.md`](../prompts/README.md) - Biblioteca completa de prompts
- [`CLAUDE.md`](../CLAUDE.md) - Guía técnica para desarrolladores
- [`SETUP_REPOSITORY.md`](../SETUP_REPOSITORY.md) - Configuración inicial del proyecto

---

**🚀 ¡Tu inteligencia del sistema eléctrico chileno está lista en 2-3 horas!**