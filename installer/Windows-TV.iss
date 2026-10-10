#define MyAppName "Windows TV"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "Ben-BTK"
#define MyAppExeName "WindowsTV.exe"

[Setup]
AppId={{A4F0A17A-79D7-4B9D-9E18-1A4A0F4B7A31}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Windows TV
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
PrivilegesRequired=admin
OutputDir=..\dist\installer
OutputBaseFilename=Windows-TV-Setup-{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\{#MyAppExeName}
CloseApplications=yes
RestartApplications=no

[Types]
Name: "basis"; Description: "Basisinstallation"
Name: "standard"; Description: "Standardinstallation (mit öffentlicher GitHub-Schnittstelle)"

[Components]
Name: "core"; Description: "Windows-TV-Anwendung"; Types: basis standard; Flags: fixed

[Tasks]
Name: "desktopicon"; Description: "Desktopverknüpfung erstellen"; GroupDescription: "Zusätzliche Symbole:"; Flags: unchecked

[Files]
Source: "..\dist\WindowsTV\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Components: core

[Icons]
Name: "{autoprograms}\Windows TV"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{autodesktop}\Windows TV"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Windows TV starten"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  VariantName: String;
begin
  if CurStep = ssPostInstall then
  begin
    VariantName := WizardSetupType(False);
    if (VariantName <> 'standard') then
      VariantName := 'basis';
    SaveStringToFile(ExpandConstant('{app}\variant.txt'), VariantName, False);
  end;
end;
