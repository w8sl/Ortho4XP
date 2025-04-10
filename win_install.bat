@echo off

:: Change directory to the main Ortho4XP folder
cd /d %~dp0

:: Check if Python is installed
python --version | findstr "3." >nul
if %errorlevel% neq 0 (
    echo Python is not installed! 
    echo Download and install Python from: https://www.python.org/downloads/windows/ ! 
    echo Customize installation, check the following options:
    echo "Add python.exe to PATH", "pip", "tcl/tk and IDLE", "Add Python to environment variables", "Install Python 3.* for all users"
    pause
    exit /b 1)
        
echo Python is installed. Setting up Python venv

:: Set up Python virtual environment
python -m venv venv

call .\venv\Scripts\activate

echo Installing requirements

:: Install requirements
echo Installing requirements
pip install -r requirements.txt

setlocal

:: Get Python version
for /f "tokens=*" %%i in ('python -c "import sys; print(sys.version)"') do set "PYVER=%%i"

if "%PYVER:~0,4%" == "3.13" (
    echo Python version is 3.13.*
    
) else if "%PYVER:~0,4%" == "3.12" (    
    echo Python version is 3.12.*    
    
) else if "%PYVER:~0,4%" == "3.11" (
    echo Python version is 3.11.*
    
) else if "%PYVER:~0,4%" == "3.10" (
    echo Python version is 3.10.*
     
) else (
    echo Python version is not 3.13.*, 3.12.*, 3.11.*, or 3.10.*
    echo aborting!
    pause
    exit /b 1)
)

endlocal

echo Ready!
echo: 
pip list
echo:
echo Use win_start.bat to run Ortho4XP
echo:

call deactivate
pause
