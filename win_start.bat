@echo off

cd /d %~dp0

echo Starting Ortho4XP
call .\venv\Scripts\activate

python Ortho4XP.py
