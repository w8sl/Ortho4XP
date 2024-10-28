@echo off

cd /d %~dp0

python --version | findstr "3.11" >nul
if %errorlevel% neq 0 (
    echo Python 3.11 is not installed! 
    echo Download and install Python3.11 from: https://www.python.org/downloads/windows/ ! 
    echo Customize installation, check the following options:
    echo "Add python.exe to PATH", "pip", "tcl/tk and IDLE", "Add Python to environment variables", "Install Python 3.11 for all users"
    pause
    exit /b 1)
        
echo Python 3.11 is installed. Setting up Ortho4XP.

python -m venv venv

call .\venv\Scripts\activate

echo Installing GDAL from: https://github.com/cgohlke/geospatial-wheels/releases/tag/v2024.9.22

pip install https://github.com/cgohlke/geospatial-wheels/releases/download/v2024.9.22/GDAL-3.9.2-cp311-cp311-win_amd64.whl

echo Installing requirements
pip install -r requirements.txt

echo: 
pip list
echo:
echo Use win_start.bat to run Ortho4XP
echo:

call deactivate
pause