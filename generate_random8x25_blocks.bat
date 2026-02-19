@echo off
setlocal EnableDelayedExpansion

REM ===== PARAMETERS =====
set numBlocks=25
set filename=test_cmd_random_blocks_1to8.csv

REM delete old file if exists
if exist "%filename%" del "%filename%"

echo Generating random blocks...

for /L %%b in (1,1,%numBlocks%) do (
    
    REM create list 1..8
    set nums=1 2 3 4 5 6 7 8
    
    REM shuffle 8 times (Fisher–Yates style)
    for /L %%i in (8,-1,1) do (
        set /a r=!random! %% %%i
        
        REM get r-th number from list
        set count=0
        for %%n in (!nums!) do (
            if !count! EQU !r! set picked=%%n
            set /a count+=1
        )
        
        REM write picked number to file
        echo !picked!>>"%filename%"
        
        REM remove picked number from list
        set newlist=
        for %%n in (!nums!) do (
            if NOT "%%n"=="!picked!" set newlist=!newlist! %%n
        )
        set nums=!newlist!
    )
)

echo.
echo Done! File created:
echo %filename%
echo.
pause
