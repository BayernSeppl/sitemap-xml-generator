#!/bin/bash
# Sitemap XML Generator Start Script (Mac/Linux)

echo ""
echo "===================================================="
echo "  Sitemap XML Generator"
echo "===================================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 ist nicht installiert."
    echo "Bitte Python3 installieren: sudo apt-get install python3 python3-pip"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Erstelle virtuelle Umgebung..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installiere Abhängigkeiten..."
pip install -q -r requirements.txt

# Start Flask app
echo ""
echo "===================================================="
echo "  Server startet..."
echo "  Öffne: http://localhost:5001"
echo "  Drücke Ctrl+C zum Beenden"
echo "===================================================="
echo ""

python3 app.py