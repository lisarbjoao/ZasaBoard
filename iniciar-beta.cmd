@echo off
setlocal
cd /d "%~dp0"
set "BETA_RUNTIME=%~dp0.venv"
if not exist "%BETA_RUNTIME%\Scripts\python.exe" set "BETA_RUNTIME=%~dp0..\Idleboard\.venv"
if not exist "%BETA_RUNTIME%\Scripts\python.exe" (
 echo Ambiente Python ausente. Consulte o README.
 pause
 exit /b 1
)
set "IDLEBOARD_EDICAO=uso"
set "IDLEBOARD_ABRIR_CANDIDATO="
set "IDLEBOARD_DADOS=%~dp0data\beta-fonte\profiles"
set "TCL_LIBRARY=%BETA_RUNTIME%\tcl\tcl8.6"
set "TK_LIBRARY=%BETA_RUNTIME%\tcl\tk8.6"
if /i "%~1"=="--verificar" (
 "%BETA_RUNTIME%\Scripts\python.exe" -c "import tkinter, customtkinter, tkwry; print('Runtime da beta pronto.')"
 exit /b
)
"%BETA_RUNTIME%\Scripts\python.exe" "%~dp0app\main.py"
if errorlevel 1 pause
endlocal
