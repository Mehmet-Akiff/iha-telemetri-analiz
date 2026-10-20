#define MyAppName "İHA Telemetri Analiz İstasyonu v1.6.0"
#define MyAppVersion "1.6.0"
#define MyAppPublisher "AAES İleri Mühendislik / Drohytech - Mehmet Akif Ürey"
#define MyAppIcon "assets\telemetry_icon.ico"

[Setup]
AppId={{8E9A71B2-4F3C-4B6A-9D21-7C8E5F1A2B3D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\IHA_Telemetri_Analiz_v1.6.0
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=dist_signed
OutputBaseFilename=IHA_Telemetri_Analiz_Setup_v1.6.0
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
Source: "dist_signed\IHA_Telemetri_Analiz_v1.6.0\*"; DestDir: "{app}"; Excludes: "__pycache__,*.pyc"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\runtime\pythonw.exe"; Parameters: """{app}\boot.pyw"""; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppIcon}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\runtime\pythonw.exe"; Parameters: """{app}\boot.pyw"""; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppIcon}"; Tasks: desktopicon
Name: "{app}\{#MyAppName}"; Filename: "{app}\runtime\pythonw.exe"; Parameters: """{app}\boot.pyw"""; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppIcon}"

[Run]
Filename: "{app}\runtime\pythonw.exe"; Parameters: """{app}\boot.pyw"""; WorkingDir: "{app}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
