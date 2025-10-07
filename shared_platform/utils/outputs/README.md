# Outputs - Extracción de Contenido PDF

Este directorio contiene las extracciones de contenido del documento **EAF-089-2025.pdf** (399 páginas).

## 📁 Estructura de Carpetas

```
outputs/
├── capitulo_01/          # Capítulo 1: Descripción de la perturbación (páginas 1-11)
├── capitulo_02/          # Capítulo 2: Equipamiento afectado (páginas 12-90)
├── indices/              # Índices generales del documento
└── pdfs_enhanced/        # PDFs con visualización de bloques de contenido
```

---

## 📄 Capítulo 1 - Descripción Pormenorizada de la Perturbación

**Páginas:** 1-11 (11 páginas)

### Archivos Disponibles

| Archivo | Descripción | Contenido |
|---------|-------------|-----------|
| `cap1_titulos_FINAL.txt` | ✅ **ÚLTIMA VERSIÓN** | 14 títulos detectados (incluye título del documento) |
| `cap1_parrafos_FINAL.txt` | ✅ **ÚLTIMA VERSIÓN** | 20 párrafos narrativos (formato 100 chars/línea) |
| `cap1_figuras.txt` | ✅ **ÚLTIMA VERSIÓN** | 0 figuras (capítulo administrativo) |
| `cap1_listas.txt` | ✅ **ÚLTIMA VERSIÓN** | 2 listas detectadas |

### Características de la Extracción

**Títulos (14 total):**
- 1 título de documento (nivel 0): "Desconexión forzada..."
- 1 capítulo principal (nivel 1): "1. Descripción pormenorizada..."
- 8 subsecciones (nivel 2): a., b., c., e., f., g., h., i.
- 4 subsecciones jerárquicas (nivel 3): d.1, d.2, d.3, d.4

**Párrafos (20 total):**
- ✅ Excluye todos los 14 títulos detectados
- ✅ Excluye contenido de tablas (fechas, códigos, nombres de empresas)
- ✅ Respeta saltos de línea (gap > 3px = nuevo párrafo)
- ✅ Incluye campos de formulario válidos (sección d.3 Reiteración)
- ✅ Formato legible con word wrap a 100 caracteres

**Distribución por sección:**
- d.1 Origen y causa: 6 párrafos
- d.2 Fenómeno Físico: 1 párrafo
- d.3 Reiteración: 3 párrafos (campos de formulario)
- d.4 Fenómeno eléctrico: 1 párrafo
- e. Detalles de la instalación: 3 párrafos
- f. Tipo de zona: 1 párrafo
- g. Proposición del propietario: 1 párrafo
- i. Cumplimiento normativo: 4 párrafos

---

## 📄 Capítulo 2 - Descripción del Equipamiento Afectado

**Páginas:** 12-90 (79 páginas)

### Archivos Disponibles

| Archivo | Descripción | Contenido |
|---------|-------------|-----------|
| `cap2_titulos_FINAL.txt` | ✅ **ÚLTIMA VERSIÓN** | 4 títulos detectados |
| `cap2_parrafos_FINAL.txt` | ⚠️ **CONTENIDO TABULAR** | 3,490 "párrafos" (en realidad filas de tabla) |

### Características de la Extracción

**Títulos (4 total):**
- 1 capítulo principal: "2. Descripción del equipamiento afectado..."
- 3 subsecciones: a. Sistema de Generación, b. Sistema de Transmisión, c. Consumos

**⚠️ Nota Importante:**
El Capítulo 2 es principalmente **tabular** (listados de equipamiento afectado). Los 3,490 "párrafos" extraídos son en realidad **filas de tabla** con:
- Central
- Unidad
- Pérdida de Generación (MW)
- Hora inicial / Hora final

**Recomendación:** Este capítulo requiere un **extractor de tablas especializado**, no un extractor de párrafos narrativos.

---

## 📑 Índices Generales

**Ubicación:** `indices/`

| Archivo | Descripción | Tamaño |
|---------|-------------|--------|
| `INDICE_EAF-089-2025.md` | Índice completo del documento | 90 KB |
| `INDICE_FINAL.md` | Índice resumido | 3 KB |

---

## 🎨 PDFs Enhanced (Visualización de Contenido)

**Ubicación:** `pdfs_enhanced/`

PDFs con bloques de contenido clasificados por color:
- 🔵 **Azul** - Texto narrativo
- 🟢 **Verde** - Tablas
- 🟣 **Magenta** - Fórmulas
- 🟠 **Naranja** - Imágenes
- 🟪 **Púrpura** - Metadatos

**Archivos (8 PDFs, ~110 MB total):**
- `EAF-089-2025_pages_1_to_50_ENHANCED.pdf` (13 MB)
- `EAF-089-2025_pages_51_to_100_ENHANCED.pdf` (13 MB)
- `EAF-089-2025_pages_101_to_150_ENHANCED.pdf` (13 MB)
- `EAF-089-2025_pages_151_to_200_ENHANCED.pdf` (16 MB)
- `EAF-089-2025_pages_201_to_250_ENHANCED.pdf` (16 MB)
- `EAF-089-2025_pages_251_to_300_ENHANCED.pdf` (14 MB)
- `EAF-089-2025_pages_301_to_350_ENHANCED.pdf` (14 MB)
- `EAF-089-2025_pages_351_to_399_ENHANCED.pdf` (14 MB)

---

## 🛠️ Códigos de Extracción

Los extractores están disponibles en: **`codigos_extractores/`**

### Extractores Principales

| Código | Descripción | Uso |
|--------|-------------|-----|
| `detailed_heading_detector.py` | Detecta títulos con numeración | Identifica estructura del documento |
| `paragraph_extractor.py` | Extrae párrafos narrativos | Filtra tablas, títulos y listas |
| `figure_extractor.py` | Detecta figuras y captions | Asocia imágenes con sus títulos |
| `list_detector.py` | Detecta listas numeradas/viñetas | Distingue listas de títulos |
| **`create_enhanced_pdf.py`** | ⭐ **Crea PDFs con boxes coloreados** | Clasifica contenido por tipo |
| **`batch_create_enhanced_pdfs.py`** | Procesa PDFs en lotes | Genera múltiples PDFs enhanced |
| `content_classifier.py` | Clasificador universal de contenido | Motor de detección de tipos |

### Características de los Extractores

**`detailed_heading_detector.py`:**
- Detecta títulos con numeración (1., a., d.1, etc.)
- Detecta título de documento (texto entre comillas en página 1)
- Filtra contenido de tablas
- Soporta jerarquías complejas (hasta nivel 4)

**`paragraph_extractor.py`:**
- ✅ Excluye títulos detectados previamente
- ✅ Filtra tablas por keywords exclusivas
- ✅ Filtra campos de formulario opcionales
- ✅ Respeta saltos de línea (gap > 3px)
- ✅ Permite menciones técnicas (kV, S/E, MW)
- ✅ Word wrap a 100 caracteres por línea
- ⚠️ No distingue bien contenido tabular extenso (Cap 2)

**`figure_extractor.py`:**
- Extrae imágenes del PDF
- Detecta captions con patrones: "Figura X:", "Gráfico X:", etc.
- Asocia captions con imágenes cercanas

**`list_detector.py`:**
- Detecta listas con viñetas (•, -, *)
- Detecta listas numeradas (1., 2., a), b))
- Agrupa ítems consecutivos en listas completas

**⭐ `create_enhanced_pdf.py`:**
- Clasifica contenido del PDF por tipo
- Dibuja boxes coloreados alrededor de cada bloque
- **Colores:**
  - 🔵 Azul = Texto narrativo
  - 🟢 Verde = Tablas
  - 🟣 Magenta = Fórmulas
  - 🟠 Naranja = Imágenes
  - 🟪 Púrpura = Metadatos
- Muestra etiquetas con tipo y confianza
- Usa `content_classifier.py` como motor de detección

**`batch_create_enhanced_pdfs.py`:**
- Procesa PDFs grandes en lotes (ej: cada 50 páginas)
- Genera múltiples archivos enhanced
- Uso: `python batch_create_enhanced_pdfs.py <pdf> <batch_size> <output_dir>`
- Ejemplo: `python batch_create_enhanced_pdfs.py documento.pdf 50 outputs/`

**`content_classifier.py`:**
- Motor universal de clasificación de contenido
- Detecta: texto, tablas, fórmulas, imágenes, metadatos
- Análisis de densidad de texto, alineación, patrones
- Retorna tipo + nivel de confianza para cada bloque

---

## 📊 Estadísticas Generales

### Documento Completo
- **Total páginas:** 399
- **Capítulos procesados:** 2 / 11
- **Archivos generados:** 20

### Por Capítulo

| Capítulo | Páginas | Títulos | Párrafos | Figuras | Listas |
|----------|---------|---------|----------|---------|--------|
| Cap 1    | 11      | 14      | 20       | 0       | 2      |
| Cap 2    | 79      | 4       | 3,490*   | -       | -      |

\* Cap 2: mayormente contenido tabular, no párrafos narrativos

---

## 🔄 Versiones y Actualizaciones

**Última actualización:** 7 de octubre de 2025

### Changelog

**v1.0 (2025-10-07)**
- ✅ Capítulo 1 completamente procesado
- ✅ Capítulo 2 procesado (requiere extractor de tablas)
- ✅ Word wrap a 100 caracteres para mejor legibilidad
- ✅ Estructura organizada por capítulos
- ✅ PDFs enhanced generados (8 archivos)

### Archivos con Versión FINAL

Archivos marcados con `_FINAL.txt` son las **últimas versiones estables**:
- ✅ `cap1_titulos_FINAL.txt` - Versión definitiva
- ✅ `cap1_parrafos_FINAL.txt` - Versión definitiva
- ✅ `cap1_figuras.txt` - Versión definitiva
- ✅ `cap1_listas.txt` - Versión definitiva
- ✅ `cap2_titulos_FINAL.txt` - Versión definitiva
- ⚠️ `cap2_parrafos_FINAL.txt` - Contenido tabular (requiere procesamiento especializado)

---

## 📝 Notas Técnicas

### Filtros Aplicados en Extracción de Párrafos

1. **Títulos:** Excluidos mediante `detailed_heading_detector.py`
2. **Tablas:** Filtradas por keywords exclusivas ("informes en plazo", "no recibido por el CEN")
3. **Nombres de empresas sueltos:** Filtrados si terminan en S.A./SPA/Ltda (<=6 palabras)
4. **Listas de subestaciones:** Filtradas si tienen 5+ referencias "S/E"
5. **Campos clave:valor múltiples:** Filtrados si tienen 2+ pares en formato formulario

### Limitaciones Conocidas

- **Capítulo 2:** El extractor de párrafos no es adecuado para contenido tabular extenso
- **Figuras:** No detectadas en capítulos administrativos (normal)
- **Listas:** Puede confundir títulos estructurales con listas en algunos casos

---

## 🚀 Próximos Pasos

- [ ] Crear extractor de tablas especializado para Capítulo 2
- [ ] Procesar Capítulos 3-11
- [ ] Generar extracciones en formato JSON estructurado
- [ ] Integrar con sistema de base de datos

---

**Generado por:** Claude Code
**Proyecto:** Dark Data Platform - Proyecto CEN
**Documento fuente:** EAF-089-2025.pdf (Estudio para análisis de falla)
