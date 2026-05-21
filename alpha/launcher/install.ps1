# install.ps1 - the alpha-001 one-click install path.
#
# Right-click -> "Run with PowerShell" (or double-click after a
# PowerShell association). No terminal knowledge required.
#
# What this script does:
#   1. Finds Recall-Setup.exe next to itself (no download needed).
#   2. Runs the installer silently with the right task flags so
#      the desktop icon AND the autostart shortcut are both
#      created (the wizard would have asked; silent mode needs
#      /TASKS= explicitly - see docs/release/INSTALL_METRICS.md).
#   3. Writes the install log next to the script so a tester
#      can email it back if anything went wrong.
#   4. Prints one calm GREEN or RED line, nothing more.
#
# No telemetry, no network calls, nothing leaves this folder.

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$installer = Join-Path $here "Recall-Setup.exe"
$log = Join-Path $here "install.log"

function Say($color, $line) {
    Write-Host $line -ForegroundColor $color
}

if (-not (Test-Path $installer)) {
    Say Red "Recall-Setup.exe not found next to install.ps1."
    Say Red "Did you copy both files into the same folder?"
    Read-Host "Press Enter to close"
    exit 1
}

Say Cyan "Installing Recall (~30-60 seconds, no admin needed)..."
$sw = [System.Diagnostics.Stopwatch]::StartNew()
$args = @(
    "/VERYSILENT",
    "/SUPPRESSMSGBOXES",
    "/NORESTART",
    "/TASKS=desktopicon,startuplaunch",
    "/LOG=$log"
)
$proc = Start-Process -FilePath $installer -ArgumentList $args -PassThru -Wait
$sw.Stop()

$dest = Join-Path $env:LOCALAPPDATA "Programs\Recall\Recall.exe"

if ($proc.ExitCode -eq 0 -and (Test-Path $dest)) {
    Say Green ("Recall installed in {0:N1}s." -f $sw.Elapsed.TotalSeconds)
    Say Green "Open it from the desktop shortcut, or press Ctrl + Space anywhere."
    Say DarkGray "Log: $log"
} else {
    Say Red "Install failed (exit $($proc.ExitCode))."
    Say Red "See $log and send the file to your alpha contact."
}

Read-Host "Press Enter to close"
