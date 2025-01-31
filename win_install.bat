@echo off

cd /d %~dp0

python --version | findstr "3.12" >nul
if %errorlevel% neq 0 (
    echo Python 3.12 is not installed! 
    echo Download and install Python3.12 from: https://www.python.org/downloads/windows/ ! 
    echo Customize installation, check the following options:
    echo "Add python.exe to PATH", "pip", "tcl/tk and IDLE", "Add Python to environment variables", "Install Python 3.12 for all users"
    pause
    exit /b 1)
        
echo Python 3.12 is installed. Setting up Ortho4XP.

python -m venv venv

call .\venv\Scripts\activate

echo Installing GDAL from: https://github.com/cgohlke/geospatial-wheels/releases/tag/v2025.1.20

pip install https://github.com/cgohlke/geospatial-wheels/releases/download/v2025.1.20/GDAL-3.10.1-cp312-cp312-win_amd64.whl

echo Installing requirements
pip install -r requirements.txt

echo: 
pip list
echo:
echo Use win_start.bat to run Ortho4XP
echo:

call deactivate
pause
