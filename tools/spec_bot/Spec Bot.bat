@echo off
setlocal enableextensions
title Spec Bot

REM Folder this .bat lives in (ends with a backslash).
set "SPEC_BOT=%~dp0"

cls
echo.
echo ============================================================
echo   Spec Bot
echo ============================================================
echo.
echo This reads a project manual PDF, compares it against your
echo past bids, and produces an Excel checklist that
echo highlights what to read vs. what is boilerplate.
echo.

REM ---------- Step 1: get the spec PDF ----------
REM If user dragged a PDF onto the .bat icon, %1 has the path.
if "%~1"=="" (
    echo Step 1 of 2  ^|  Spec PDF
    echo ------------------------
    echo Drag the project manual PDF onto this window, or paste
    echo its full path below. Then press Enter.
    echo.
    set /p "PDF_PATH=PDF path: "
) else (
    set "PDF_PATH=%~1"
    echo PDF: %PDF_PATH%
)

REM Strip any surrounding quotes that drag-and-drop sometimes adds.
set PDF_PATH=%PDF_PATH:"=%

if not exist "%PDF_PATH%" (
    echo.
    echo !! ERROR: Could not find that file.
    echo    %PDF_PATH%
    echo.
    echo Press any key to close.
    pause >nul
    exit /b 1
)

REM ---------- Step 2: get the bid name ----------
echo.
echo Step 2 of 2  ^|  Bid name
echo ------------------------
echo Type a short name for this bid. Example: Sample Elementary
echo (Used to name your Excel output. No special characters needed.)
echo.
set /p "BID_NAME=Bid name: "

if "%BID_NAME%"=="" (
    echo.
    echo !! ERROR: A bid name is required.
    echo.
    pause >nul
    exit /b 1
)

REM ---------- Run the pipeline ----------
echo.
echo ============================================================
echo Working...  (this typically takes 30-60 seconds)
echo ============================================================
python "%SPEC_BOT%run_bot.py" "%PDF_PATH%" "%BID_NAME%"

if errorlevel 1 (
    echo.
    echo Something went wrong. Read the messages above for the cause.
    echo.
    pause >nul
    exit /b 1
)

echo.
echo ============================================================
echo Done. Your Excel checklist should now be open.
echo ============================================================
echo.
echo You can close this window.
echo.
pause >nul
endlocal
