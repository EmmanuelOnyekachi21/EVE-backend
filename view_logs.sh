#!/bin/bash
# Helper script to view ingestion logs

LOGS_DIR="logs"

echo "==================================="
echo "EVE Backend - Log Viewer"
echo "==================================="
echo ""

# Check if logs directory exists
if [ ! -d "$LOGS_DIR" ]; then
    echo "❌ Logs directory not found. Run the ingestion command first."
    exit 1
fi

# Function to display menu
show_menu() {
    echo "Available log files:"
    echo "1) ingestion.log (Detailed ingestion logs)"
    echo "2) general.log (General application logs)"
    echo "3) errors.log (Error logs only)"
    echo "4) View all logs (tail -f all files)"
    echo "5) Clear all logs"
    echo "6) Exit"
    echo ""
}

# Function to tail a log file
tail_log() {
    local file=$1
    if [ -f "$LOGS_DIR/$file" ]; then
        echo "📄 Viewing $file (Press Ctrl+C to stop)"
        echo "-----------------------------------"
        tail -f "$LOGS_DIR/$file"
    else
        echo "❌ $file not found. Run the ingestion command first."
    fi
}

# Function to view a log file with less
view_log() {
    local file=$1
    if [ -f "$LOGS_DIR/$file" ]; then
        echo "📄 Viewing $file (Press 'q' to quit)"
        echo "-----------------------------------"
        less "$LOGS_DIR/$file"
    else
        echo "❌ $file not found. Run the ingestion command first."
    fi
}

# Main loop
while true; do
    show_menu
    read -p "Select an option (1-6): " choice
    
    case $choice in
        1)
            view_log "ingestion.log"
            ;;
        2)
            view_log "general.log"
            ;;
        3)
            view_log "errors.log"
            ;;
        4)
            echo "📄 Tailing all logs (Press Ctrl+C to stop)"
            echo "-----------------------------------"
            tail -f logs/*.log 2>/dev/null || echo "No log files found"
            ;;
        5)
            read -p "⚠️  Are you sure you want to clear all logs? (y/n): " confirm
            if [ "$confirm" = "y" ]; then
                rm -f logs/*.log
                echo "✅ All logs cleared"
            else
                echo "❌ Cancelled"
            fi
            ;;
        6)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid option. Please select 1-6."
            ;;
    esac
    echo ""
done
