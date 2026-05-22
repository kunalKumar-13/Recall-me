; Recall — Windows installer (Inno Setup script)
; ------------------------------------------------------------------
; Builds Recall-Setup.exe from the PyInstaller bundle in dist\Recall\.
; Compile with:  iscc infra\packaging\windows\recall.iss
; (build.ps1 runs PyInstaller then this, in one step.)
;
; The grandmother test: the user double-clicks Recall-Setup.exe,
; clicks Next twice, and Recall is installed, shortcutted, and
; running. No terminal, no Python, no docs.

#define AppName        "Recall"
#define AppVersion      "0.1.0"
#define AppPublisher    "Recall"
#define AppExeName      "Recall.exe"
#define AppId           "{{A7E3F1C2-9D4B-4E6A-8F12-RECALL000001}}"

[Setup]
AppId={#AppId}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
; Per-user install — no admin prompt. This is the whole point of
; "zero friction": a normal double-click installs without UAC.
PrivilegesRequired=lowest
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
DisableDirPage=auto
OutputDir=..\..\..\dist\installer
; Phase 5J - lite variant. The previous Recall-Setup.exe (Phase 5F
; full build, 260.8 MB, SHA-256 7AFA5349...75FD975) remains the
; historical full artifact whose hash is recorded in
; docs/trust/INSTALL_PROOF_WINDOWS.md.
OutputBaseFilename=Recall-Setup-lite
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
; Icons / branding — Phase 5F uses the existing app icon so the
; installer can build today; branded wizard BMPs are a "Later"
; polish item and the Inno Setup default banner is used until then.
SetupIconFile=..\..\..\app\assets\icon.ico
; WizardImageFile / WizardSmallImageFile intentionally omitted; add
; branded BMPs at infra/packaging/assets/ when ready.
; Silent repair: `Recall-Setup.exe /SILENT` reinstalls in place over
; a broken install without prompting — the "silent repair path".
UninstallDisplayIcon={app}\{#AppExeName}
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; \
  GroupDescription: "Shortcuts:"
; Launch-on-login is OPT-IN and checked by default — a continuity
; tool that isn't running captures nothing. The app's own Settings
; can toggle this later (app/core/autostart.py owns the Run key).
Name: "startuplaunch"; Description: "Start Recall when I sign in"; \
  GroupDescription: "Startup:"

[Files]
; The entire PyInstaller one-folder bundle.
Source: "..\..\..\dist\Recall\*"; DestDir: "{app}"; \
  Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{userdesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; \
  Tasks: desktopicon
; Launch-on-login: a Startup-folder shortcut. The app's Settings
; can also manage this via the registry Run key; the installer
; only seeds the initial choice.
Name: "{userstartup}\{#AppName}"; Filename: "{app}\{#AppExeName}"; \
  Tasks: startuplaunch

[Run]
; First run — launch Recall straight after install so the user
; lands in onboarding, not at an empty desktop. First-run config
; (~/.recall/) is created by the app itself, not the installer.
Filename: "{app}\{#AppExeName}"; Description: "Start Recall now"; \
  Flags: nowait postinstall skipifsilent

[Registry]
; Register the `recall://` URL scheme so the browser extension's
; "Open Recall" button (and any future `recall://open?...` deep link)
; resolves to this installed Recall.exe. Per-user only - HKCU.
; The `uninsdeletekey` flag removes the entire `recall` subtree on
; uninstall so the URL handler does not outlive the install.
Root: HKCU; Subkey: "Software\Classes\recall"; \
  ValueType: string; ValueName: ""; \
  ValueData: "URL:Recall protocol"; \
  Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\recall"; \
  ValueType: string; ValueName: "URL Protocol"; ValueData: ""
Root: HKCU; Subkey: "Software\Classes\recall\DefaultIcon"; \
  ValueType: string; ValueName: ""; \
  ValueData: "{app}\{#AppExeName},0"
Root: HKCU; Subkey: "Software\Classes\recall\shell\open\command"; \
  ValueType: string; ValueName: ""; \
  ValueData: """{app}\{#AppExeName}"" ""%1"""

[UninstallDelete]
; Leave ~/.recall/ alone on uninstall — the user's memory is theirs.
; A full wipe is the documented manual step (apps/docs/uninstall.mdx).
Type: filesandordirs; Name: "{app}\__pycache__"
