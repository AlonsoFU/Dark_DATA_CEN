# 🏗️ PROYECTO DARK DATA CEN - ESTRUCTURA PROFESIONAL

## 📁 NUEVA ORGANIZACIÓN

```
Proyecto Dark Data CEN/
├── src/                              # 📦 CÓDIGO FUENTE PRINCIPAL
│   ├── analyzers/                    # 🔍 Análisis de estructura y patrones
│   │   ├── document_structure_analyzer.py    # Análisis inicial de documentos
│   │   └── specific_annex_detector.py        # Detección específica de anexos
│   │
│   ├── processors/                   # ⚙️ Procesamiento de documentos
│   │   ├── large_document_processor.py       # Procesador principal V1
│   │   ├── truly_adaptive_processor.py       # Procesador mejorado
│   │   ├── enhanced_annex_processor.py       # Procesamiento de anexos
│   │   ├── adaptive_document_processor.py    # Procesador adaptativo
│   │   └── document_processor.py             # Procesador base
│   │
│   ├── database/                     # 🗄️ Operaciones de base de datos
│   │   ├── integrate_chunks_to_db.py         # Integración a SQLite
│   │   ├── database_viewer.py               # Visor de base de datos
│   │   └── view_processed_data.py           # Visualización de datos
│   │
│   ├── utils/                        # 🛠️ Utilidades y herramientas
│   │   ├── simple_viewer.py                 # Visor básico original
│   │   ├── dashboard.py                     # Dashboard web
│   │   ├── web_viewer.py                    # Visor web
│   │   └── claude_chunk_interface.py        # Interface para Claude
│   │
│   └── extractors/                   # 📄 Extractores de PDF (V2)
│       └── pdf_extractor_v2.py              # Extractor avanzado
│
├── mcp/                              # 🔌 INTEGRACIÓN MCP
│   ├── servers/                      # Servidores MCP
│   │   ├── mcp_server.py                    # Servidor principal
│   │   └── mcp_server_enhanced.py           # Servidor mejorado
│   │
│   ├── clients/                      # Clientes MCP
│   │   └── linux_mcp_client.py              # Cliente Linux
│   │
│   ├── bridges/                      # Puentes MCP
│   │   ├── claude_mcp_bridge_semantic.py    # Bridge semántico
│   │   └── claude_mcp_bridge.py             # Bridge básico
│   │
│   └── mcp_demo.py                   # Demo MCP
│
├── scripts/                          # 📋 SCRIPTS EJECUTABLES
│   ├── analysis/                     # Scripts de análisis
│   │   ├── analyze_title_patterns.py        # Análisis de patrones
│   │   ├── find_all_document_titles.py      # Búsqueda de títulos
│   │   ├── search_all_content_types.py      # Análisis de contenido
│   │   └── analysis_queries.py              # Consultas de análisis
│   │
│   ├── processing/                   # Scripts de procesamiento
│   │   └── ingest_data.py                   # Ingesta de datos
│   │
│   └── maintenance/                  # Scripts de mantenimiento
│       └── (pendiente)
│
├── config/                           # ⚙️ CONFIGURACIONES
│   └── processing_config.yaml               # Configuración V2
│
├── archive/                          # 📦 SCRIPTS HISTÓRICOS
│   ├── search_page_*.py              # Búsquedas específicas de páginas
│   ├── fix_*.py                      # Scripts de reparación temporal
│   ├── show_*.py                     # Scripts de visualización
│   ├── test_*.py                     # Scripts de prueba
│   └── [50+ scripts archivados]     # Scripts temporales cumplieron función
│
├── document_processing_v2/           # 🚀 SISTEMA V2 (EN DESARROLLO)
│   └── [estructura V2 completa]
│
└── docs/                            # 📚 DOCUMENTACIÓN
    ├── PROJECT_STRUCTURE.md         # Este archivo
    ├── SCRIPT_INVENTORY.md          # Inventario de scripts
    └── LARGE_DOCUMENT_GUIDE.md      # Guía original
```

## 🎯 SCRIPTS ACTIVOS PRINCIPALES

### Core Processing (src/)
- **`src/processors/truly_adaptive_processor.py`** - Procesador principal actual
- **`src/database/integrate_chunks_to_db.py`** - Integración SQLite
- **`src/analyzers/specific_annex_detector.py`** - Detección de anexos

### MCP Integration (mcp/)
- **`mcp/servers/mcp_server_enhanced.py`** - Servidor MCP principal
- **`mcp/clients/linux_mcp_client.py`** - Cliente para Linux

### Analysis Tools (scripts/analysis/)
- **`scripts/analysis/analyze_title_patterns.py`** - Análisis de patrones
- **`scripts/analysis/find_all_document_titles.py`** - Búsqueda de títulos

### Viewers (src/utils/)
- **`src/utils/simple_viewer.py`** - Visor básico
- **`src/utils/dashboard.py`** - Dashboard web

## 📊 ESTADÍSTICAS DE LIMPIEZA

- **Antes**: 65+ scripts en directorio raíz (caos total)
- **Después**: ~15 scripts organizados profesionalmente
- **Archivados**: 50+ scripts temporales (sin eliminar, por si acaso)
- **Estructura**: 8 carpetas organizadas temáticamente

## 🚀 PRÓXIMOS PASOS

1. ✅ **Estructura creada** - Organización profesional completa
2. ⏳ **Actualizar imports** - Ajustar referencias entre archivos
3. ⏳ **Documentar APIs** - Crear documentación técnica
4. ⏳ **Tests unitarios** - Crear suite de pruebas
5. ⏳ **CI/CD Pipeline** - Automatización de despliegue

## 💡 BENEFICIOS OBTENIDOS

- **✅ Mantenibilidad**: Código organizado y fácil de encontrar
- **✅ Escalabilidad**: Fácil agregar nuevas funcionalidades
- **✅ Colaboración**: Estructura estándar de la industria
- **✅ Modularidad**: Separación clara de responsabilidades
- **✅ Historial preservado**: Scripts archivados, no eliminados