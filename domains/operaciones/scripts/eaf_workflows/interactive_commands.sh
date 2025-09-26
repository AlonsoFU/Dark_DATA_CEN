#!/bin/bash
# Interactive Anexos Processing Commands
# Quick shortcuts for the interactive processor

DOCUMENT_PATH="data/documents/anexos_EAF/raw/Anexos-EAF-089-2025.pdf"
SAMPLE_PATH="data/documents/anexos_EAF/samples/Anexos-EAF-089-2025_reduc.pdf"

echo "🚀 Interactive Anexos Processing Commands"
echo "========================================"
echo ""

# Function to show available commands
show_commands() {
    echo "Available commands:"
    echo ""
    echo "📍 DISCOVERY PHASE:"
    echo "  discover-sample    - Discover chapters in sample doc (pages 1-10)"
    echo "  discover-full      - Discover chapters in full doc (pages 1-20)"
    echo "  discover-range     - Discover specific page range"
    echo ""
    echo "✅ VALIDATION PHASE:"  
    echo "  validate-sample    - Validate chapters in sample doc"
    echo "  validate-full      - Validate chapters in full doc"
    echo "  validate-range     - Validate specific page range"
    echo ""
    echo "🔍 EXTRACTION PHASE:"
    echo "  extract-sample     - Extract data from sample doc chapters"
    echo "  extract-full       - Extract data from full doc chapters"
    echo ""
    echo "🛠️  UTILITY:"
    echo "  show-page <num>    - Show preview of specific page"
    echo "  debug-text <pages> - Show raw text from page range"
    echo "  session-status     - Show current session status"
    echo ""
    echo "Example usage:"
    echo "  ./interactive_commands.sh discover-sample"
    echo "  ./interactive_commands.sh show-page 15"
    echo "  ./interactive_commands.sh debug-text 10-15"
}

# Parse command
case "$1" in
    "discover-sample")
        echo "🔍 Discovering chapters in sample document (pages 1-10)..."
        python scripts/smart_interactive_processor.py "$SAMPLE_PATH" --mode discover --start-page 1 --pages 10
        ;;
        
    "discover-full")
        echo "🔍 Discovering chapters in full document (pages 1-20)..."
        python scripts/smart_interactive_processor.py "$DOCUMENT_PATH" --mode discover --start-page 1 --pages 20
        ;;
        
    "discover-range")
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo "Usage: $0 discover-range <start_page> <num_pages>"
            echo "Example: $0 discover-range 50 10"
            exit 1
        fi
        echo "🔍 Discovering chapters in range (pages $2-$(($2+$3-1)))..."
        python scripts/smart_interactive_processor.py "$DOCUMENT_PATH" --mode discover --start-page "$2" --pages "$3"
        ;;
        
    "validate-sample")
        echo "✅ Validating chapters in sample document..."
        python scripts/smart_interactive_processor.py "$SAMPLE_PATH" --mode validate --start-page 1 --pages 20
        ;;
        
    "validate-full") 
        echo "✅ Validating chapters in full document..."
        python scripts/smart_interactive_processor.py "$DOCUMENT_PATH" --mode validate --start-page 1 --pages 50
        ;;
        
    "validate-range")
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo "Usage: $0 validate-range <start_page> <num_pages>"
            exit 1
        fi
        echo "✅ Validating range (pages $2-$(($2+$3-1)))..."
        python scripts/smart_interactive_processor.py "$DOCUMENT_PATH" --mode validate --start-page "$2" --pages "$3"
        ;;
        
    "extract-sample")
        echo "🔍 Extracting data from sample document chapters..."
        python scripts/smart_interactive_processor.py "$SAMPLE_PATH" --mode extract
        ;;
        
    "extract-full")
        echo "🔍 Extracting data from full document chapters..."
        python scripts/smart_interactive_processor.py "$DOCUMENT_PATH" --mode extract
        ;;
        
    "show-page")
        if [ -z "$2" ]; then
            echo "Usage: $0 show-page <page_number>"
            exit 1
        fi
        echo "📖 Showing page $2 preview..."
        python scripts/debug_document_content.py "$DOCUMENT_PATH" --pages "$2"
        ;;
        
    "debug-text")
        if [ -z "$2" ]; then
            echo "Usage: $0 debug-text <page_range>"
            echo "Example: $0 debug-text 10-15"
            exit 1
        fi
        echo "📝 Showing raw text from pages $2..."
        python scripts/debug_document_content.py "$DOCUMENT_PATH" --pages "$2" --max-chars 2000
        ;;
        
    "session-status")
        echo "📊 Session Status:"
        echo "Latest sessions:"
        ls -lt data/documents/anexos_EAF/development/ | head -5
        ;;
        
    "help"|""|*)
        show_commands
        ;;
esac