# Recall — single-command dev bootstrap (Windows / PowerShell).
#
# Creates the venv if missing, installs dependencies, runs the smoke
# test, then launches the desktop app. Idempotent — re-run any time.
#
#   ./scripts/dev.ps1            # full path: venv + deps + smoke + launch
#   ./scripts/dev.ps1 -SkipSmoke # skip the 5-second smoke test
#   ./scripts/dev.ps1 -Demo      # launch in --demo mode (no indexing)
#   ./scripts/dev.ps1 -DebugBoot # launch with --debug boot diagnostics

[CmdletBinding()]
param(
    [switch]$SkipSmoke,
    [switch]$Demo,
    [switch]$DebugBoot
)

$ErrorActionPreference = "Stop"

# The script lives at infra/scripts/, two levels deep from the
# repo root. The Python desktop tree currently sits at the root;
# the pseudo-monorepo migration plan in apps/desktop/README.md
# will move it under apps/desktop/ in a future cycle.
$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $Root

Write-Host ""
Write-Host "Recall dev bootstrap — $Root" -ForegroundColor Cyan
Write-Host ""

# 1. Python version check
$pythonMin = [Version]"3.10"
try {
    $pyVer = (python --version 2>&1).ToString().Split(" ")[1]
    $pyVerObj = [Version]($pyVer -replace "[^\d.]", "")
    if ($pyVerObj -lt $pythonMin) {
        Write-Host "Python $pyVer detected; 3.10+ required." -ForegroundColor Red
        exit 1
    }
    Write-Host "  python $pyVer" -ForegroundColor Gray
} catch {
    Write-Host "python not found on PATH. Install Python 3.10+." -ForegroundColor Red
    exit 1
}

# 2. Create venv if missing
$venv = Join-Path $Root ".venv"
if (-not (Test-Path $venv)) {
    Write-Host "  creating venv at .venv …" -ForegroundColor Gray
    python -m venv $venv
}

# 3. Activate venv
$activate = Join-Path $venv "Scripts\Activate.ps1"
if (-not (Test-Path $activate)) {
    Write-Host "  venv activation script missing at $activate." -ForegroundColor Red
    exit 1
}
. $activate

# 4. Install deps (only if requirements has changed since last install)
$reqHashFile = Join-Path $venv ".reqhash"
$reqPath = Join-Path $Root "requirements.txt"
$currentHash = (Get-FileHash $reqPath).Hash
$installNeeded = $true
if (Test-Path $reqHashFile) {
    if ((Get-Content $reqHashFile) -eq $currentHash) {
        $installNeeded = $false
    }
}
if ($installNeeded) {
    Write-Host "  installing dependencies …" -ForegroundColor Gray
    pip install --quiet --upgrade pip
    pip install --quiet -r $reqPath
    Set-Content $reqHashFile $currentHash
} else {
    Write-Host "  dependencies up to date" -ForegroundColor Gray
}

# 5. Smoke test
if (-not $SkipSmoke) {
    Write-Host "  running smoke test …" -ForegroundColor Gray
    python _smoke_api.py | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "smoke test failed. Re-run with: python _smoke_api.py" -ForegroundColor Red
        exit $LASTEXITCODE
    }
    Write-Host "  smoke test ok" -ForegroundColor Gray
}

# 6. Launch
Write-Host ""
Write-Host "starting Recall …" -ForegroundColor Cyan
Write-Host ""

$launchArgs = @()
if ($Demo)      { $launchArgs += "--demo" }
if ($DebugBoot) { $launchArgs += "--debug" }

python recall.py @launchArgs
