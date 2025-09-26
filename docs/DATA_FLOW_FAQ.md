# 🤔 Guía de Procesamiento de Documentos - Preguntas y Respuestas

## 🎯 ¿Para qué sirve esta guía?

Si tienes un documento PDF (contrato, reporte, manual, etc.) y quieres **extraer información estructurada** para consultarla con IA, esta guía te explica exactamente cómo hacerlo paso a paso.

**Resultado final**: Tu documento PDF → Base de datos → Consultas inteligentes con IA

---

## 🚀 **ANTES DE EMPEZAR**

### ❓ ¿Qué necesito tener listo?

**1. ¿Tengo acceso a Claude Code?**
- Sí → Perfecto, puedes hacer todo con Claude Code
- No → Necesitarás instalar las herramientas automáticas

**2. ¿Qué tipo de documento tengo?**
- **Financiero**: Estados de resultados, balances, reportes
- **Legal**: Contratos, acuerdos, políticas
- **Técnico**: Manuales, especificaciones, procedimientos
- **Operacional**: Reportes de KPIs, análisis de rendimiento

**3. ¿Cómo es mi documento?**
- **Simple**: 1-20 páginas, estructura clara → 2-3 horas
- **Medio**: 20-100 páginas, varias secciones → 3-4 horas
- **Complejo**: 100+ páginas, estructura irregular → 4-6 horas

### ❓ ¿Cómo verifico que todo está funcionando?

```bash
# Verificar estructura básica del proyecto
ls domains/
ls ai_platform/
ls shared_platform/

# Si no existen, estás en el directorio equivocado
```

---

## 📥 **PASO 1: ¿CÓMO OBTENGO EL DOCUMENTO?**

### ❓ ¿Tengo el PDF en mi computadora?

**Sí, ya lo tengo:**
```bash
# Crear carpetas y copiar documento
mkdir -p domains/mi_dominio/data/source_documents/
cp "/ruta/a/mi/documento.pdf" domains/mi_dominio/data/source_documents/
```

**No, está online:**
```bash
# Descarga simple
wget "https://sitio.com/documento.pdf" -O mi_documento.pdf
```

### ❓ ¿Cómo organizo las carpetas?

**Para un documento nuevo:**
```bash
# Ejemplo: procesando un contrato de servicios
mkdir -p domains/legal/chapters/contrato_servicios/
mkdir -p domains/legal/chapters/contrato_servicios/docs/
mkdir -p domains/legal/chapters/contrato_servicios/processors/
mkdir -p domains/legal/chapters/contrato_servicios/outputs/
mkdir -p domains/legal/shared/
```

**¿Cuándo crear nuevo dominio vs nueva carpeta?**
- **Nuevo dominio**: Área completamente diferente (legal → financiero)
- **Nueva carpeta**: Mismo dominio, diferente documento (contrato_servicios → contrato_compraventa)

---

## 🔍 **PASO 2: ¿CÓMO ANALIZO LA ESTRUCTURA?**

### ❓ ¿Mi documento tiene capítulos o es simple?

**Con Claude Code (Recomendado):**
```
Analiza este documento PDF:

1. ¿Qué tipo de documento es? (financiero, legal, técnico, etc.)
2. ¿Tiene capítulos/secciones claras o es unitario?
3. ¿Qué información valiosa contiene?
4. ¿Qué tan complejo será procesar?

Responde en formato JSON con esta estructura.
```

**Con herramientas automáticas (si existen):**
```bash
python ai_platform/analyzers/document_structure_analyzer.py \
  --document "domains/mi_dominio/data/source_documents/documento.pdf" \
  --output "analysis_result.json"
```

### ❓ ¿Cómo divido el documento en secciones?

**Si tiene capítulos/secciones claras:**
- Claude Code puede identificar automáticamente dónde empiezan y terminan
- O usar: `python ai_platform/processors/chapter_divider.py`

**Si es documento simple:**
```bash
echo '{"type": "single_document", "pages": "all"}' > chapter_divisions.json
```

---

## 🤖 **PASO 3: ¿CÓMO EXTRAIGO LOS DATOS?**

### ❓ ¿Cómo creo un extractor para mi documento?

**Con Claude Code (Recomendado):**
```
Crea un extractor Python para este documento:

CONTEXTO:
- Tipo: [contrato de servicios / reporte financiero / manual técnico]
- Estructura: [simple / con capítulos]

EXTRAER:
- Para contratos: partes, obligaciones, fechas, montos
- Para reportes: métricas, empresas, períodos, KPIs
- Para manuales: procedimientos, especificaciones, equipos

CREAR: archivo extractor_documento.py
```

**Con herramientas automáticas:**
```bash
python ai_platform/processors/adaptive_document_processor.py \
  --document "documento.pdf" \
  --analysis "analysis_result.json" \
  --output-processor "mi_extractor.py"
```

### ❓ ¿Cómo sé si mi extractor funciona bien?

**Primera revisión técnica:**
1. **Ejecutar extractor:**
```bash
python mi_extractor.py --input "../../../data/source_documents/documento.pdf"
```

2. **¿Extrajo algo coherente?**
- Sí → Continuar
- No → Refinar código del extractor

3. **Repetir hasta lograr >85% confianza**

### ❓ ¿Cómo genero metadatos y tags?

**Con Claude Code:**
```
Analiza los datos extraídos y genera:

TAGS PARA:
- Conceptos clave del documento
- Fechas y períodos relevantes
- Ubicaciones geográficas mencionadas
- Organizaciones y personas
- Tipo y propósito del documento

CREAR: archivo metadata.json con tags categorizados
```

---

## ✋ **PASO 4: ¿CÓMO VALIDO QUE TODO ESTÁ CORRECTO?**

### ❓ ¿Cómo reviso cada dato extraído?

**Validación de contenido (diferente a la revisión técnica):**

**Con Claude Code:**
```
Revisa estos datos extraídos uno por uno:

Para cada extracción:
1. ¿Es correcta la información?
2. ¿Falta algún dato importante?
3. ¿Hay errores de interpretación?

Dime qué correcciones necesito hacer.
```

**Con herramientas automáticas:**
```bash
python shared_platform/cli/validation_interface.py --interactive
```

### ❓ ¿Cómo genero referencias cruzadas?

**Si tengo otros documentos procesados:**

**Con Claude Code:**
```
Busca relaciones entre este documento y la base de datos:

BUSCAR:
- Mismas empresas/personas en otros documentos
- Mismo período temporal
- Ubicaciones relacionadas
- Temas similares

CREAR: archivo cross_references.json
```

---

## 💾 **PASO 5: ¿CÓMO CONVIERTO AL FORMATO UNIVERSAL?**

### ❓ ¿Por qué necesito un formato universal?

**Problema**: Cada documento extrae datos diferentes
- Contrato: partes, fechas, obligaciones
- Reporte: métricas, empresas, períodos
- Manual: procedimientos, equipos, especificaciones

**Solución**: Formato universal que la IA puede consultar consistentemente

### ❓ ¿Cómo hago la transformación?

**Con Claude Code (Recomendado):**
```
Transforma mis datos al esquema universal:

ESQUEMA OBJETIVO:
{
  "document_metadata": {...},
  "extracted_entities": {
    "organizations": [...],
    "people": [...],
    "dates": [...],
    "metrics": [...],
    "domain_specific": {...}
  },
  "semantic_tags": {...},
  "cross_references": [...]
}

MAPEAR:
- Mis entidades específicas → categorías universales
- Datos únicos de mi dominio → campo "domain_specific"
- Conservar toda la información original

CREAR: archivo universal_schema.json
```

---

## 🗄️ **PASO 6: ¿CÓMO CARGO LOS DATOS A LA BASE DE DATOS?**

### ❓ ¿Cómo configuro la base de datos?

**Primera vez:**
```bash
make setup-db  # Crea la base de datos SQLite
```

**Cargar mis datos:**
```bash
python shared_platform/database_tools/ingest_data.py \
  --input "domains/mi_dominio/chapters/mi_documento/outputs/universal_json/"
```

**Con Claude Code:**
```
Carga estos datos universales a la base de datos dark_data.db
```

### ❓ ¿Cómo activo el acceso AI?

**Activar servidores MCP:**
```bash
make run-mcp  # Servidor principal para consultas AI
```

**Con Claude Code:**
- Ya tienes acceso directo, no necesitas activar nada adicional

---

## 🎯 **¿CÓMO SÉ QUE TODO FUNCIONÓ?**

### ❓ ¿Cómo pruebo que puedo consultar mis datos?

**Consultas de prueba:**
```
# Con Claude Code puedes preguntar directamente:
"¿Cuántas entidades extraje de mi documento?"
"Lista las organizaciones principales mencionadas"
"Muestra un resumen de los datos extraídos"
"¿Qué referencias cruzadas encontraste?"
```

**Con herramientas de prueba:**
```bash
python shared_platform/cli/test_ai_queries.py --domain "mi_dominio"
```

### ❓ ¿Cómo proceso mi segundo documento?

**Si es del mismo tipo:**
- Usar el mismo extractor
- Proceso mucho más rápido (30-45 min)

**Si es tipo diferente:**
- Repetir todo el proceso
- Pero ya conoces los pasos (2-3 horas)

---

## 🚨 **¿QUÉ HAGO CUANDO ALGO SALE MAL?**

### ❓ ¿Claude Code no puede leer mi PDF?

**Posibles soluciones:**
1. **PDF protegido**: Remover protección primero
2. **PDF escaneado**: Necesita OCR, usar herramientas automáticas
3. **PDF corrupto**: Regenerar el PDF desde fuente original

### ❓ ¿Las extracciones salen terribles?

**Diagnóstico:**
1. **¿El análisis inicial fue correcto?** → Rehacer análisis
2. **¿El extractor está mal diseñado?** → Refinar código 5-10 veces
3. **¿El documento es muy complejo?** → Dividir en partes más pequeñas

### ❓ ¿No tengo las herramientas automáticas?

**Solución simple:**
- Usar **solo Claude Code** para todo
- Es más conversacional y flexible
- No necesitas instalar nada adicional

### ❓ ¿Cómo sé si mis datos son de buena calidad?

**Señales de éxito:**
- ✅ Extractor logra >85% confianza
- ✅ Validación manual encuentra pocos errores
- ✅ Datos transformados se ven completos
- ✅ Consultas AI devuelven información coherente

**Señales de problemas:**
- ❌ Muchos datos extraídos incorrectamente
- ❌ Información importante faltante
- ❌ Tags y metadatos irrelevantes
- ❌ Referencias cruzadas sin sentido

---

## 🎯 **EJEMPLOS PRÁCTICOS POR TIPO DE DOCUMENTO**

### 📋 **Ejemplo: Contrato de Servicios (45-75 min)**

**1. Análisis con Claude Code:**
```
"Analiza este contrato: ¿qué partes están involucradas, qué servicios se prestan, cuáles son las fechas importantes y los montos?"
```

**2. Extracción esperada:**
- Partes: Cliente, Proveedor
- Servicios: Descripción detallada
- Fechas: Inicio, fin, hitos
- Montos: Valor total, formas de pago
- Obligaciones: De cada parte

**3. Validación:**
- ¿Son correctos los nombres de las empresas?
- ¿Las fechas están bien interpretadas?
- ¿Los montos incluyen moneda correcta?

### 📈 **Ejemplo: Reporte Financiero (60-90 min)**

**1. Análisis con Claude Code:**
```
"Analiza este estado de resultados: ¿qué métricas contiene, de qué período, qué comparativos hay?"
```

**2. Extracción esperada:**
- Métricas: Ingresos, gastos, utilidades, ratios
- Período: Trimestre, año fiscal
- Comparativos: Año anterior, presupuesto
- Empresa: Nombre, sector

**3. Validación:**
- ¿Los números están en la moneda correcta?
- ¿Los períodos corresponden?
- ¿Los cálculos son coherentes?

### 🔧 **Ejemplo: Manual Técnico (75-120 min)**

**1. Análisis con Claude Code:**
```
"Analiza este manual: ¿qué procedimientos describe, qué equipos involucra, qué especificaciones técnicas contiene?"
```

**2. Extracción esperada:**
- Procedimientos: Pasos detallados
- Equipos: Modelos, especificaciones
- Normas: Estándares aplicables
- Seguridad: Precauciones, riesgos

**3. Validación:**
- ¿Los procedimientos están completos?
- ¿Las especificaciones son precisas?
- ¿Las normas están correctamente referenciadas?

---

## ✅ **CHECKLIST FINAL: ¿LO HICE BIEN?**

### 📋 **Verificación por Fase**

**FASE 1 - Obtención:**
- [ ] Documento PDF copiado en la carpeta correcta
- [ ] Estructura de directorios creada
- [ ] Tipo de dominio definido correctamente

**FASE 2 - Análisis:**
- [ ] Tipo de documento identificado
- [ ] Estructura (simple/capítulos) determinada
- [ ] División de secciones realizada (si aplica)

**FASE 3 - Extracción:**
- [ ] Extractor específico creado y calibrado
- [ ] Confianza técnica >85% lograda
- [ ] Metadatos y tags generados

**FASE 4 - Validación:**
- [ ] Cada extracción revisada individualmente
- [ ] Datos incorrectos corregidos o eliminados
- [ ] Referencias cruzadas identificadas

**FASE 5 - Transformación:**
- [ ] Datos transformados a esquema universal
- [ ] Información original preservada
- [ ] Formato JSON válido generado

**FASE 6 - Ingesta:**
- [ ] Datos cargados a base de datos SQLite
- [ ] Servidores MCP activados (si aplica)
- [ ] Consultas AI funcionando correctamente

### 🎯 **¿Cómo sé que está todo listo?**

**Prueba final:**
```
"Basándote en los datos que procesé, responde:
1. ¿Cuántas entidades principales extraje?
2. ¿Cuáles son los conceptos más importantes del documento?
3. ¿Qué relaciones encontraste con otros documentos?
4. Haz un resumen ejecutivo de la información extraída"
```

**Si Claude Code puede responder esto coherentemente → ¡Éxito! 🎉**

---

## 🚀 **¿QUÉ SIGUE DESPUÉS?**

### 📈 **Para tu segundo documento:**
- **Mismo tipo**: Reutilizar extractor (30-45 min)
- **Tipo diferente**: Proceso completo pero ya conoces los pasos

### 🔍 **Consultas avanzadas que puedes hacer:**
```
"Compara los datos de mis documentos financieros del último trimestre"
"Encuentra todas las empresas mencionadas en mis contratos"
"¿Qué procedimientos técnicos aparecen en múltiples manuales?"
"Analiza las tendencias temporales en mis datos"
```

### 🎯 **Expansión de la plataforma:**
- Agregar más tipos de documento
- Crear extractores reutilizables
- Desarrollar dashboards personalizados
- Integrar con otras fuentes de datos

---

**🌟 ¡Felicidades! Ya tienes tu documento PDF convertido en inteligencia consultable con IA.**

> **Tiempo total**: 2-6 horas dependiendo de la complejidad
> **Resultado**: De PDF estático → Base de conocimiento AI-queryable
> **Beneficio**: Análisis inteligente, búsquedas precisas, insights automáticos