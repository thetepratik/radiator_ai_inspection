@echo off
echo =========================================
echo Starting Radiator AI Inspection System
echo =========================================

cd /d "%~dp0"

REM Fix PATH issue just in case C:\Windows\System32 is missing
set PATH=%PATH%;C:\Windows\System32;C:\Windows\System32\WindowsPowerShell\v1.0;C:\Windows\System32\Wbem

set VENV_PATH=..\EDI2\radiator_ai_inspection\venv

IF NOT EXIST "%VENV_PATH%\Scripts\activate.bat" (
    echo Error: Could not find the existing venv at %VENV_PATH%
    echo Please ensure the EDI2 folder exists and contains the venv.
    pause
    exit /b 1
)

echo Activating existing virtual environment from EDI2 folder...
call "%VENV_PATH%\Scripts\activate.bat"

echo Starting FastAPI Backend Server on port 8000...
REM Using /k instead of /c so the window stays open if it crashes!
start "Radiator Backend API" cmd /k "call %VENV_PATH%\Scripts\activate.bat && python api\server.py"

echo Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak >nul

echo Starting Streamlit UI...
start "Radiator Frontend UI" cmd /k "call %VENV_PATH%\Scripts\activate.bat && streamlit run ui\streamlit_app.py"

echo.
echo System has been started in separate windows!
echo Backend API is running on http://localhost:8000
echo Frontend UI is running on http://localhost:8501
echo.
echo Please look at the "Radiator Backend API" black window. If there is an error there, copy it and paste it here!
pause
