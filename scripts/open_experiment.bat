@echo off
setlocal

set "CONFIG=%~1"
if "%CONFIG%"=="" set "CONFIG=experiments\example.yaml"

call "%~dp0run_experiment.cmd" "%CONFIG%" -OpenOnly
set "EXIT_CODE=%ERRORLEVEL%"

endlocal & exit /b %EXIT_CODE%
