@echo off
setlocal

echo Unblocking project files under:
echo %~dp0..
echo.

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -Command "Get-ChildItem -LiteralPath '%~dp0..' -Recurse -File ^| Unblock-File"
if errorlevel 1 (
    echo.
    echo ERROR: Windows could not unblock all project files.
    echo Try right-clicking the downloaded ZIP, select Properties, check Unblock,
    echo and extract it again. A company Group Policy may also prevent this action.
    pause
    exit /b 1
)

echo Project files were unblocked successfully.
echo You can now use start_experiment.bat from the project root.
pause

endlocal
