@echo off
setlocal

rem Change this path when moving the project to another computer.
set "PYTHON_EXE=F:\miniconda3\python.exe"
set "SCRIPT_DIR=%~dp0"

if not exist "%PYTHON_EXE%" (
    echo Python was not found at: %PYTHON_EXE%
    echo Edit PYTHON_EXE in this batch file to point to Python with Tkinter installed.
    pause
    exit /b 1
)

"%PYTHON_EXE%" "%SCRIPT_DIR%mix_stim_list_gui.py"
set "EXIT_CODE=%ERRORLEVEL%"
if not "%EXIT_CODE%"=="0" pause

endlocal & exit /b %EXIT_CODE%
