@echo off

cd /d %~dp0

REM Get the absolute path of the osgeo directory
for /f "delims=" %%i in ('cd') do set "abs_path=%%i\venv\Lib\site-packages\osgeo"

REM Add the osgeo directory to the PATH
set "PATH=%PATH%;%abs_path%"

REM Activate Python venv
cmd /k ".\venv\Scripts\activate"


