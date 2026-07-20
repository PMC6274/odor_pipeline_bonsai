@echo off
setlocal

set "PYTHON_EXE=D:\software\miniconda\python.exe"
set "SCRIPT_DIR=%~dp0"

"%PYTHON_EXE%" "%SCRIPT_DIR%stim_list_gui.py"

endlocal
