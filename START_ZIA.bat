@echo off
cd /d "%~dp0"
echo Starting DSA King Cleaning System...
where py >nul 2>nul
if %errorlevel%==0 (set "PYTHON=py -3") else (set "PYTHON=python")
%PYTHON% -c "import flask,requests,dotenv" >nul 2>nul
if errorlevel 1 (
 echo First-time setup: installing Python packages. Internet required.
 %PYTHON% -m pip install -r requirements.txt
 if errorlevel 1 (echo Installation failed. Install Python 3 and retry.&pause&exit /b 1)
)
%PYTHON% app.py
if errorlevel 1 pause
