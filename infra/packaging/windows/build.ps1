# Recall — Windows build pipeline
# ------------------------------------------------------------------
# One command, two stages:
#   1. PyInstaller  → dist\Recall\Recall.exe   (the app bundle)
#   2. Inno Setup   → dist\installer\Recall-Setup.exe   (the installer)
#
#   pwsh infra\packaging\windows\build.ps1
#
# Prerequisites (one-time, on the build machine):
#   • Python deps:  pip install -r requirements.txt pyinstaller
#   • Inno Setup 6: https://jrsoftware.org/isdl.php  (provides `iscc`)
#
# This produces an UNSIGNED installer. Code-signing (an EV cert +
# signtool) is a separate release step — see RELEASE.md.

$ErrorActionPreference = "Stop"

# Repo root is three levels up from this script.
$root = Resolve-Path "$PSScriptRoot\..\..\.."
Set-Location $root
Write-Host "Recall build — root: $root" -ForegroundColor Cyan

# --- stage 1: PyInstaller -----------------------------------------
Write-Host "`n[1/2] PyInstaller bundle..." -ForegroundColor Cyan
if (Test-Path "dist\Recall") { Remove-Item -Recurse -Force "dist\Recall" }
pyinstaller --noconfirm recall.spec
if (-not (Test-Path "dist\Recall\Recall.exe")) {
    throw "PyInstaller did not produce dist\Recall\Recall.exe"
}
Write-Host "  bundle ready: dist\Recall\Recall.exe" -ForegroundColor Green

# --- stage 2: Inno Setup ------------------------------------------
Write-Host "`n[2/2] Inno Setup installer..." -ForegroundColor Cyan
$iscc = Get-Command iscc -ErrorAction SilentlyContinue
if ($iscc) { $iscc = $iscc.Source }
if (-not $iscc) {
    # winget installs Inno Setup per-user under %LOCALAPPDATA%\Programs;
    # the classic installer puts it in Program Files (x86). Check both.
    $guesses = @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "${env:ProgramFiles}\Inno Setup 6\ISCC.exe",
        "${env:LOCALAPPDATA}\Programs\Inno Setup 6\ISCC.exe"
    )
    foreach ($g in $guesses) {
        if (Test-Path $g) { $iscc = $g; break }
    }
    if (-not $iscc) {
        throw "Inno Setup (iscc) not found. Install Inno Setup 6 (winget install JRSoftware.InnoSetup)."
    }
}
Write-Host "  iscc: $iscc" -ForegroundColor DarkGray
& $iscc "infra\packaging\windows\recall.iss"
$out = "dist\installer\Recall-Setup.exe"
if (-not (Test-Path $out)) { throw "Installer not produced: $out" }

Write-Host "`nDone. Release artifact:" -ForegroundColor Green
Write-Host "  $root\$out" -ForegroundColor Green
Write-Host "Next: code-sign it (RELEASE.md) before publishing." -ForegroundColor Yellow
