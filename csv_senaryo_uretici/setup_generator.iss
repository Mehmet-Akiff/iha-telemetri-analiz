#define MyAppName "İHA Telemetri CSV Senaryo Üretici v1.6.0"
#define MyAppVersion "1.6.0"
#define MyAppPublisher "AAES İleri Mühendislik / Drohytech - Mehmet Akif Ürey"
#define MyAppIcon "assets\generator_icon.ico"

[Setup]
AppId={{4C2F91A8-7E5D-4A1B-8C62-3D9F0E2B4A5C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\CSV_Senaryo_Uretici_v1.6.0
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=..\dist_signed
OutputBaseFilename=CSV_Senaryo_Uretici_Setup_v1.6.0
SetupIconFile={#MyAppIcon}
Compression=lzma2/fast
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppIcon}
UninstallDisplayName={#MyAppName}

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
Source: "..\..\iha-csv-senaryo-uretici\dist_signed\CSV_Senaryo_Uretici_v1.6.0\*"; DestDir: "{app}"; Excludes: "__pycache__,*.pyc"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\runtime\pythonw.exe"; Parameters: """{app}\boot.pyw"""; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppIcon}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\runtime\pythonw.exe"; Parameters: """{app}\boot.pyw"""; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppIcon}"; Tasks: desktopicon
Name: "{app}\{#MyAppName}"; Filename: "{app}\runtime\pythonw.exe"; Parameters: """{app}\boot.pyw"""; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppIcon}"

[Run]
Filename: "{app}\runtime\pythonw.exe"; Parameters: """{app}\boot.pyw"""; WorkingDir: "{app}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
