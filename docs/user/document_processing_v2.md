# Document Processing V2 - Structured Technical Documents

## 🎯 OBJETIVO
Algoritmos especializados para procesar documentos técnicos con estructura específica:
- Informes de fallas eléctricas (CEN Chile)
- ANEXOS numerados con títulos descriptivos
- Secciones individuales (INFORME DIARIO + fecha)
- Contenido tabular y técnico

## 📁 ESTRUCTURA

### `/extractors/`
- **`pdf_extractor_v2.py`**: Extractor principal con algoritmos robustos
- **`title_page_extractor.py`**: Especializado en páginas de títulos 
- **`table_extractor.py`**: Para contenido tabular y técnico

### `/analyzers/`
- **`document_structure_analyzer.py`**: Detecta patrones de estructura
- **`title_pattern_analyzer.py`**: Identifica títulos y secciones
- **`content_quality_analyzer.py`**: Evalúa calidad de extracción

### `/processors/`
- **`structured_chunker.py`**: Chunking inteligente por estructura
- **`theme_classifier.py`**: Clasificación temática automática
- **`database_integrator.py`**: Integración con SQLite

### `/utils/`
- **`pdf_diagnostics.py`**: Herramientas de diagnóstico
- **`text_cleaning.py`**: Limpieza y normalización
- **`pattern_library.py`**: Biblioteca de patrones regex

### `/config/`
- **`processing_config.yaml`**: Configuración de parámetros
- **`patterns.yaml`**: Patrones específicos por tipo de documento

### `/tests/`
- Scripts de prueba para cada componente

## 🔧 ENFOQUE V2

1. **Análisis previo del PDF**: Identificar páginas problemáticas
2. **Extracción adaptativa**: Diferentes algoritmos según el tipo de página
3. **Validación en tiempo real**: Detectar placeholders durante extracción
4. **Reintento con múltiples métodos**: Si un método falla, probar otros
5. **Estructura jerárquica**: Mantener relaciones entre secciones

## 🚀 VENTAJAS SOBRE V1

- ✅ **Elimina placeholders**: Extracción real del texto
- ✅ **Estructura específica**: Algoritmos diseñados para este tipo de documentos  
- ✅ **Validación continua**: Detecta errores durante el procesamiento
- ✅ **Modular y escalable**: Fácil agregar nuevos tipos de documentos
- ✅ **Recuperación completa**: Acceso al 100% del contenido