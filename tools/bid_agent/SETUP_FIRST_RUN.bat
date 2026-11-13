@echo off
echo.
echo  BID AGENT - FIRST TIME SETUP
echo  ============================
echo.
echo  Installing required Python packages...
echo.

pip install --upgrade anthropic PyPDF2 python-docx openpyxl

echo.
IF NOT EXIST "%~dp0company_profile.json" (
    copy "%~dp0company_profile.example.json" "%~dp0company_profile.json" >nul
    echo  Created company_profile.json from the example.
    echo  Open it and enter your own company and PM details before the first run.
    echo.
)

echo  Done. You can now run the agent by:
echo.
echo  1. Dragging a job folder onto run_bid_agent.bat
echo  2. OR: python bid_agent.py "C:\Path\To\JobFolder"
echo.
echo  Make sure ANTHROPIC_API_KEY is set in your environment variables.
echo  To set it now (only needed once per machine):
echo  Note: setx stores the key in plain text in your Windows user environment.
echo  Open a new command window after setting it.
echo.
SET /P APIKEY="  Paste your Anthropic API key (or press Enter to skip): "

IF NOT "%APIKEY%"=="" (
    setx ANTHROPIC_API_KEY "%APIKEY%"
    echo.
    echo  API key saved to environment variables.
)

echo.
pause
