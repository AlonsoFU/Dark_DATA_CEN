# 🧹 Configuración del Repositorio

## Reducir tamaño para GitHub

Este documento explica cómo mantener un repositorio liviano excluyendo archivos de entrada y salida pesados.

## 📋 Pasos para limpiar el repositorio

### 1. Ejecutar script de limpieza
```bash
# Limpiar archivos grandes del historial de git
./cleanup_git.sh
```

### 2. Aplicar cambios
```bash
# Agregar los cambios del .gitignore
git add .gitignore
git add */.gitkeep
git add SETUP_REPOSITORY.md

# Confirmar cambios
git commit -m "Actualizar .gitignore y remover archivos grandes

- Excluir PDFs originales (entrada de datos)
- Excluir extracciones JSON (salida de datos)
- Excluir bases de datos SQLite
- Mantener estructura con .gitkeep
- Reducir tamaño del repositorio para GitHub"

# Subir cambios
git push
```

## 📂 Estructura mantenida

### ✅ Se mantiene en git:
- **Código fuente**: `.py`, scripts, configuraciones
- **Documentación**: `README.md`, `CLAUDE.md`, docs
- **Configuración**: `pyproject.toml`, `Makefile`, requirements
- **Esquemas**: JSON pequeños de configuración
- **Templates**: HTML, patrones, perfiles

### ❌ Se excluye de git:
- **PDFs originales**: Documentos fuente pesados
- **Extracciones JSON**: Resultados de procesamiento
- **Bases de datos**: SQLite generadas
- **Cache**: Archivos temporales
- **Logs**: Archivos de registro

## 🗂️ Directorios con .gitkeep

Los siguientes directorios mantienen su estructura con archivos `.gitkeep`:

```
domains/operaciones/anexos_eaf/data/source_documents/
platform_data/database/
domains/operaciones/anexos_eaf/chapters/anexo_01/data/extractions/
```

## 🚀 Configuración inicial para desarrolladores

Después de clonar el repositorio:

```bash
# 1. Instalar dependencias
make install-dev

# 2. Crear estructura de datos (si no existe)
mkdir -p domains/operaciones/anexos_eaf/data/source_documents
mkdir -p platform_data/database

# 3. Colocar documentos PDF en:
# domains/operaciones/anexos_eaf/data/source_documents/

# 4. Crear base de datos
make setup-db

# 5. Procesar documentos
# (seguir instrucciones en README.md)
```

## 📊 Beneficios

- **Repositorio liviano**: Solo código fuente y configuración
- **Clones rápidos**: Sin archivos pesados de datos
- **Colaboración eficiente**: Solo cambios de código relevantes
- **Estructura preservada**: Directorios importantes mantenidos

## ⚠️ Importante

- Los PDFs y datos grandes deben colocarse localmente
- Las extracciones se generan localmente
- Cada desarrollador mantiene sus propios datos de trabajo
- El repositorio solo contiene el código para procesarlos