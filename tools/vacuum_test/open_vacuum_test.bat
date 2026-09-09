@echo off
setlocal
rem Opens the editor only; does not start the workflow.
"%~dp0..\..\.bonsai\Bonsai.exe" "%~dp0bonsai_flow_control_demo.bonsai"
set "EXIT_CODE=%ERRORLEVEL%"
if not "%EXIT_CODE%"=="0" pause
endlocal & exit /b %EXIT_CODE%
