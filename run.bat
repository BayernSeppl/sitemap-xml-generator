@echo off
REM Sitemap XML Generator Start Script (Windows)

echo.
echo ====================================================
echo   Sitemap XML Generator
echo ====================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python ist nicht installiert oder nicht im PATH.
    echo Bitte Python von https://www.python.org/ herunterladen und installieren.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Erstelle virtuelle Umgebung...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installiere Abhängigkeiten...
pip install -q -r requirements.txt

REM Start Flask app
echo.
echo ====================================================
echo   Server startet...
echo   Öffne: http://localhost:5001
echo   Drücke Ctrl+C zum Beenden
echo ====================================================
echo.

python app.py

pause