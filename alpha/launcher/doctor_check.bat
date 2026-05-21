@echo off
REM doctor_check.bat - run "recall doctor" and keep the window open.
REM
REM A tester runs this at end-of-week-one and screenshots the result
REM into FEEDBACK.md. The bundled Recall ships with doctor built in -
REM no Python required.

set "RECALL=%LOCALAPPDATA%\Programs\Recall\Recall.exe"

if not exist "%RECALL%" (
  echo Recall is not installed yet.
  echo Run install.ps1 in this folder first.
  pause
  exit /b 1
)

echo Running diagnostics. This takes one or two seconds.
echo.
"%RECALL%" doctor
echo.
echo --- end of report ---
echo Screenshot this window into the FEEDBACK.md you return.
pause
exit /b 0
