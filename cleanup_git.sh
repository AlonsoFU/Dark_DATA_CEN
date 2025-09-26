#!/bin/bash
# Script para limpiar archivos grandes del repositorio git

echo "🧹 Limpiando archivos grandes del repositorio git..."

# Remover archivos PDF de la historia de git
echo "📄 Removiendo PDFs..."
git rm --cached -r . 2>/dev/null || true
git rm --cached "*.pdf" 2>/dev/null || true
git rm --cached "*.PDF" 2>/dev/null || true

# Remover extracciones JSON grandes
echo "📊 Removiendo extracciones JSON grandes..."
git rm --cached -r "data/documents/anexos_EAF/extractions/" 2>/dev/null || true
git rm --cached -r "domains/operaciones/data/documents/" 2>/dev/null || true
git rm --cached -r "domains/operaciones/anexos_eaf/chapters/*/data/extractions/" 2>/dev/null || true

# Remover bases de datos
echo "🗄️ Removiendo bases de datos..."
git rm --cached "*.db" 2>/dev/null || true
git rm --cached "*.sqlite" 2>/dev/null || true
git rm --cached "*.sqlite3" 2>/dev/null || true
git rm --cached "platform_data/database/*" 2>/dev/null || true

# Remover archivos de scraping grandes
echo "🌐 Removiendo archivos de scraping..."
git rm --cached -r "shared_platform/scrapers/coordinador_cl/extractions/" 2>/dev/null || true

# Remover archivos temporales y cache
echo "🗑️ Removiendo archivos temporales..."
git rm --cached -r "logs/" 2>/dev/null || true
git rm --cached -r "cache/" 2>/dev/null || true
git rm --cached -r "tmp/" 2>/dev/null || true
git rm --cached -r "archive/" 2>/dev/null || true
git rm --cached -r "processed_docs/" 2>/dev/null || true

echo "✅ Limpieza completada!"
echo "📝 Ahora ejecuta:"
echo "   git add .gitignore"
echo "   git commit -m 'Actualizar .gitignore y remover archivos grandes'"
echo "   git push"