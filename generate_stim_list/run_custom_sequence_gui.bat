@echo off
setlocal

set "PYTHON_EXE=D:\software\miniconda\python.exe"
set "SCRIPT_DIR=%~dp0"

"%PYTHON_EXE%" "%SCRIPT_DIR%custom_sequence_gui.py"

endlocal
