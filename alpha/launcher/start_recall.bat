@echo off
REM start_recall.bat - launch Recall without finding it in the Start menu.
REM
REM Tester double-clicks this if the desktop shortcut is missing or if
REM Recall has stopped running. The path is the per-user install root
REM the alpha installer writes to.

set "RECALL=%LOCALAPPDATA%\Programs\Recall\Recall.exe"

if not exist "%RECALL%" (
  echo Recall is not installed yet.
  echo Run install.ps1 in this folder first.
  pause
  exit /b 1
)

start "" "%RECALL%"
exit /b 0
