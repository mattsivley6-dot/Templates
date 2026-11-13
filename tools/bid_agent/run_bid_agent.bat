@echo off
REM ============================================================
REM  BID COORDINATION AGENT
REM  Drag a job folder onto this file to run.
REM  Or double-click and type the path when prompted.
REM ============================================================

echo.
echo  BID COORDINATION AGENT
echo  ======================
echo.

REM If a folder was dragged onto this bat file, use it
SET FOLDER=%~1

IF "%FOLDER%"=="" (
    echo  No folder dragged. Enter the job folder path below.
    echo  Example: C:\Jobs\Sample-Elementary
    echo.
    SET /P FOLDER="  Folder path: "
)

IF "%FOLDER%"=="" (
    echo  ERROR: No folder provided.
    pause
    exit /b 1
)

echo.
SET /P PROJECT="  Project name (optional, press Enter to skip): "

echo.
echo  Reading folder and sending to the Anthropic API...
echo  A full run can take several minutes. Do not close this window.
echo.

IF "%PROJECT%"=="" (
    python "%~dp0bid_agent.py" "%FOLDER%"
) ELSE (
    python "%~dp0bid_agent.py" "%FOLDER%" --project "%PROJECT%"
)

echo.
pause
