# INVENTARIO DE SCRIPTS - Proyecto Dark Data CEN

## 📋 SCRIPTS PRINCIPALES (MANTENER)

### Core Processing
- `document_structure_analyzer.py` - Análisis inicial de estructura
- `large_document_processor.py` - Procesador principal V1
- `truly_adaptive_processor.py` - Procesador mejorado 
- `integrate_chunks_to_db.py` - Integración a SQLite
- `enhanced_annex_processor.py` - Detección de anexos
- `specific_annex_detector.py` - Detección específica de títulos

### Database & Viewing
- `simple_viewer.py` - Visor básico original
- `dashboard.py` - Dashboard web
- `view_processed_data.py` - Visor de datos procesados
- `database_viewer.py` - Visor de base de datos

### MCP Integration
- `mcp_server.py` - Servidor MCP principal
- `mcp_server_enhanced.py` - Servidor MCP mejorado  
- `linux_mcp_client.py` - Cliente MCP para Linux
- `claude_mcp_bridge_semantic.py` - Bridge semántico

### Analysis & Search
- `analyze_title_patterns.py` - Análisis de patrones de títulos
- `find_all_document_titles.py` - Búsqueda de todos los títulos
- `search_all_content_types.py` - Análisis de tipos de contenido

## 🔍 SCRIPTS DE BÚSQUEDA ESPECÍFICA (MANTENER ALGUNOS)

### Búsquedas de Anexos
- `search_anexos_3_4.py` - Búsqueda específica anexos 3 y 4
- `find_complete_annex_titles.py` - Títulos completos de anexos

### Búsquedas de INFORME DIARIO  
- `find_informe_diario_titles.py` - Búsqueda INFORME DIARIO
- `search_page_135.py` - Búsqueda específica página 135
- `search_around_page_135.py` - Búsqueda alrededor página 135

## ⚠️ SCRIPTS TEMPORALES/DUPLICADOS (ELIMINAR)

### Scripts de Prueba Temporal
- `quick_test.py` - Prueba rápida temporal
- `test_new_tools_direct.py` - Test de herramientas
- `demo_new_tools.py` - Demo temporal
- `show_simple_examples.py` - Ejemplos simples
- `show_chunk_examples.py` - Ejemplos de chunks

### Scripts de Búsqueda Muy Específica (ya cumplieron su función)
- `search_page_164.py` - Página específica
- `search_page_191.py` - Página específica  
- `direct_content_164.py` - Contenido directo
- `sql_direct_164.py` - SQL directo
- `direct_sql_page_191.py` - SQL página específica
- `show_chunk_161.py` - Chunk específico

### Scripts de Fix/Reparación Temporal
- `fix_anexo_2_title.py` - Fix específico anexo 2
- `fix_real_annexes.py` - Fix anexos
- `add_anexo_4.py` - Agregar anexo 4
- `manually_add_anexo_5.py` - Agregar anexo 5 manualmente
- `force_create_missing_annexes.py` - Crear anexos faltantes
- `check_anexo_2.py` - Verificar anexo 2
- `check_anexo_4_complete.py` - Verificar anexo 4
- `check_anexos_structure.py` - Verificar estructura anexos

### Scripts de Análisis Redundantes
- `real_content_analysis.py` - Análisis de contenido (redundante)
- `investigate_content_processing.py` - Investigación procesamiento
- `structure_validation.py` - Validación estructura (redundante)
- `count_all_titles.py` - Conteo títulos (funcionalidad ya en otros)
- `get_anexo_3_title.py` - Get anexo específico
- `find_anexo_5_pattern.py` - Patrón anexo específico

### Scripts de Mostrar/Display Redundantes  
- `show_my_chunks.py` - Mostrar chunks (redundante con viewer)
- `show_chunk_structure.py` - Estructura chunks (redundante)
- `show_results.py` - Mostrar resultados (redundante)

### Scripts de Búsqueda Redundantes
- `search_anexo_2_title.py` - Búsqueda específica anexo 2
- `search_all_anexo_patterns.py` - Patrones anexos (redundante)
- `find_all_anexos_in_index.py` - Anexos en índice
- `find_formal_titles.py` - Títulos formales (redundante)
- `find_single_page_titles.py` - Títulos página individual
- `find_title_pages_algorithm.py` - Algoritmo páginas título

## 📁 ORGANIZACIÓN PROPUESTA

### Crear carpetas:
```
scripts/
├── core/              # Scripts principales  
├── analysis/          # Análisis y búsquedas útiles
├── mcp/              # Integración MCP
├── viewers/          # Visualizadores
└── archive/          # Scripts históricos (no eliminar, archivar)
```

## ⚡ ACCIÓN RECOMENDADA

1. **MOVER scripts principales a carpetas organizadas**
2. **ARCHIVAR scripts temporales** (no eliminar por si acaso)
3. **ELIMINAR duplicados evidentes** 
4. **MANTENER solo 15-20 scripts activos** en el directorio principal

¿Proceder con la limpieza?