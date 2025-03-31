@echo off
echo Starting ADE Model Training Manager...
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
)

REM Start the Flask application in the background
start /B python src/web/app.py

REM Wait for the server to start
timeout /t 3 /nobreak

REM Open the browser
start http://localhost:5000

echo Model Training Manager is running at http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

REM Keep the window open
pause 