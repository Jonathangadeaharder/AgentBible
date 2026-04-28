@echo off
setlocal EnableDelayedExpansion

echo ====================================
echo   TheBible Deployment Script
echo ====================================
echo.

REM Ask if all languages should be included
set "INCLUDE_ALL=Y"
set /p "INCLUDE_ALL=Include all languages? (Y/N) [Y]: "
if "!INCLUDE_ALL!"=="" set "INCLUDE_ALL=Y"

REM Convert to uppercase for consistency
for %%L in (A B C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    set "INCLUDE_ALL=!INCLUDE_ALL:%%L=%%L!"
)
set "INCLUDE_ALL=!INCLUDE_ALL: =!"

REM If yes to all, set all to Y, otherwise ask individually
if /i "!INCLUDE_ALL!"=="Y" (
    set "INCLUDE_CSHARP=Y"
    set "INCLUDE_CPP=Y"
    set "INCLUDE_PYTHON=Y"
    set "INCLUDE_REACT=Y"
    echo.
    echo [All languages selected]
) else (
    echo.
    REM Ask for individual languages with defaults
    set "INCLUDE_CSHARP=Y"
    set /p "INCLUDE_CSHARP=Include C# guidelines? (Y/N) [Y]: "
    if "!INCLUDE_CSHARP!"=="" set "INCLUDE_CSHARP=Y"
    
    set "INCLUDE_CPP=Y"
    set /p "INCLUDE_CPP=Include C++ guidelines? (Y/N) [Y]: "
    if "!INCLUDE_CPP!"=="" set "INCLUDE_CPP=Y"
    
    set "INCLUDE_PYTHON=Y"
    set /p "INCLUDE_PYTHON=Include Python guidelines? (Y/N) [Y]: "
    if "!INCLUDE_PYTHON!"=="" set "INCLUDE_PYTHON=Y"
    
    set "INCLUDE_REACT=Y"
    set /p "INCLUDE_REACT=Include React guidelines? (Y/N) [Y]: "
    if "!INCLUDE_REACT!"=="" set "INCLUDE_REACT=Y"
)

REM Normalize inputs to uppercase (case insensitive)
call :UpperCase INCLUDE_CSHARP
call :UpperCase INCLUDE_CPP
call :UpperCase INCLUDE_PYTHON
call :UpperCase INCLUDE_REACT

echo.
echo Selected languages:
if /i "!INCLUDE_CSHARP!"=="Y" echo - C#
if /i "!INCLUDE_CPP!"=="Y" echo - C++
if /i "!INCLUDE_PYTHON!"=="Y" echo - Python
if /i "!INCLUDE_REACT!"=="Y" echo - React
echo.

REM Convert language selections to Python arguments
set "PY_ARGS="
if "!INCLUDE_CSHARP!"=="Y" set "PY_ARGS=!PY_ARGS! csharp"
if "!INCLUDE_CPP!"=="Y" set "PY_ARGS=!PY_ARGS! cpp"
if "!INCLUDE_PYTHON!"=="Y" set "PY_ARGS=!PY_ARGS! python"
if "!INCLUDE_REACT!"=="Y" set "PY_ARGS=!PY_ARGS! react"

echo ====================================
echo   Phase 1: Deploy to GitHub Copilot
echo ====================================
echo.

python deploy_to_copilot.py!PY_ARGS!
if !ERRORLEVEL! NEQ 0 (
    echo [ERROR] Failed to deploy to Copilot
    goto :EOF
)

echo.
echo ====================================
echo   Phase 2: Deploy to Windsurf
echo ====================================
echo.

python deploy_to_windsurf.py!PY_ARGS!
if !ERRORLEVEL! NEQ 0 (
    echo [ERROR] Failed to deploy to Windsurf
    goto :EOF
)

echo.
echo ====================================
echo   Phase 3: Creating AGENTS.MD
echo ====================================
echo.

REM Create reference document using PowerShell
powershell -ExecutionPolicy Bypass -File "combine-agents.ps1" "!INCLUDE_CSHARP!" "!INCLUDE_CPP!" "!INCLUDE_PYTHON!" "!INCLUDE_REACT!"

if !ERRORLEVEL! EQU 0 (
    echo [OK] AGENTS.MD created successfully
) else (
    echo [ERROR] Failed to create AGENTS.MD
)

echo.
echo ====================================
echo   Deployment Complete!
echo ====================================
echo.
pause
goto :eof

REM Function to convert variable to uppercase
:UpperCase
setlocal EnableDelayedExpansion
set "str=!%~1!"
set "str=!str:a=A!"
set "str=!str:b=B!"
set "str=!str:c=C!"
set "str=!str:d=D!"
set "str=!str:e=E!"
set "str=!str:f=F!"
set "str=!str:g=G!"
set "str=!str:h=H!"
set "str=!str:i=I!"
set "str=!str:j=J!"
set "str=!str:k=K!"
set "str=!str:l=L!"
set "str=!str:m=M!"
set "str=!str:n=N!"
set "str=!str:o=O!"
set "str=!str:p=P!"
set "str=!str:q=Q!"
set "str=!str:r=R!"
set "str=!str:s=S!"
set "str=!str:t=T!"
set "str=!str:u=U!"
set "str=!str:v=V!"
set "str=!str:w=W!"
set "str=!str:x=X!"
set "str=!str:y=Y!"
set "str=!str:z=Z!"
endlocal & set "%~1=%str%"
goto :eof
